---
type: Concept
title: "配置体系：EngineArgs 与 VllmConfig"
description: "vLLM 的单一配置对象 VllmConfig、EngineArgs 数据类（约 3000 行）的分组地图、常用参数按用途速查（模型/显存/调度/并行/编译/量化/LoRA/多模态）与环境变量覆盖"
tags: [vllm, configuration, engine-args, vllm-config, parameters, 核心模块]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-argutils
    resource: /references/facts.md
    title: vllm/engine/arg_utils.py + vllm/config/（本地检出）
---

# 配置体系：EngineArgs 与 VllmConfig

vLLM 的全部旋钮收敛为**一个配置对象**：`EngineArgs`（`vllm/engine/arg_utils.py`，约 3266 行的 dataclass）接收命令行/API 参数，归并生成 `VllmConfig`，后者作为「引擎级全局状态」在 Engine→Executor→Worker→ModelRunner→Model 全链路传递（F-013）。CLI 参数由 `EngineArgs` 字段自动生成（`vllm --help` 与 `vllm serve --help` 同源），Python 侧 `LLM(model=..., tensor_parallel_size=...)` 亦同（F-061）。

## 参数分组地图

`EngineArgs` 字段按关注点分组引用各 Config 类（`vllm/config/`，37 个配置文件，F-002）：

| 分组 | 代表参数 | 说明 |
|------|---------|------|
| 模型与加载 | `model`、`tokenizer`、`dtype`、`revision`、`load_format`、`hf_overrides`、`trust_remote_code` | 模型身份与权重加载（F-013） |
| 显存与缓存 | `gpu_memory_utilization`（默认 0.9）、`kv_cache_memory_bytes`、`kv_cache_dtype`、`block_size`、`num_gpu_blocks_override`、`enable_prefix_caching`、`cpu_offload_gb` | KV 容量与块策略（F-013、F-053） |
| 调度 | `max_num_seqs`、`max_num_batched_tokens`、`long_prefill_token_threshold`、`enable_chunked_prefill`、`scheduling_policy`、`watermark` | 批大小与 prefill/decode 预算（F-013） |
| 并行 | `tensor_parallel_size`、`pipeline_parallel_size`、`data_parallel_size`、`prefill/decode_context_parallel_size`、`enable_expert_parallel`、`nnodes`、`node_rank` | 五种并行度与多机（F-110） |
| 执行与编译 | `enforce_eager`、`cudagraph_capture_sizes`、`max_cudagraph_capture_size`、`compilation_config` | CUDA graph 与 torch.compile（F-052） |
| 量化 | `quantization`、`quantization_config`、`kv_cache_dtype`、`linear_backend` | 权重量化与内核后端（F-090、F-091） |
| 多模态 | `limit_mm_per_prompt`、`mm_processor_cache_gb`、`language_model_only`、`allowed_local_media_path` | 多模态输入限制与缓存（F-013） |
| LoRA | `enable_lora`、`max_loras`、`max_lora_rank`、`lora_dtype` | 多适配器服务（F-142） |
| 采样/输出 | `max_logprobs`、`logprobs_mode`、`generation_config` | logprobs 语义与生成配置（F-019、F-070） |
| 结构化输出 | `structured_outputs_config` | xgrammar/guidance 后端（F-143） |

> 参数以本地检出 `EngineArgs` 为准；完整清单由 `vllm serve --help` 或生成的 engine arguments reference（`docs/configuration/engine_args.md`）给出（F-002）。

## 常用参数速查（按意图）

**「想改吞吐/延迟」**

- `--max-num-seqs`：并发序列上限，调大提高吞吐、增加排队与显存压力；
- `--max-num-batched-tokens`：每步 token 预算，直接决定 chunked prefill 粒度与 step 时长；
- `--gpu-memory-utilization`：KV 池占总显存比例，0.9 为默认；OOM 时下调；
- `--enable-chunked-prefill` / `--long-prefill-token-threshold`：长 prompt 场景保护 TTFT（F-019）。

**「想省显存」**

- 权重量化：`--quantization fp8`（或 gptq/awq/gguf 等，见 [10 量化](10-quantization.md)）；
- KV 量化：`--kv-cache-dtype fp8`（F-090）；
- 卸载：`--cpu-offload-gb N`（F-140）。

**「想多卡」**

- `--tensor-parallel-size N`：单机多卡切分权重（F-110）；
- `--data-parallel-size N`：多副本提高总吞吐，API server 自动扩展（F-112）；
- 多机：`--nnodes`/`--node-rank` + `--master-addr`/`--master-port`（F-112）。

**「想追新/调试」**

- `--enforce-eager`：关 CUDA graph，便于 debug（F-052）；
- `VLLM_SERVER_DEV_MODE=1`：开开发端点（sleep/wake、weight transfer、reset cache，F-068）；
- `--logprobs-mode`：raw/processed 四种 logprobs 口径（F-019）。

## 三层覆盖优先级

同一参数可来自：命令行 > 环境变量（`VLLM_*`，如 `VLLM_API_KEY`、`VLLM_USE_MODELSCOPE`）> 模型自带配置（`generation_config.json`）> 默认值（F-070、F-013）。理解这条链能解释「为什么改了参数没生效」——模型仓库的 `generation_config.json` 会在采样参数上覆盖 vLLM 默认，`--generation-config vllm` 可切断（F-070）。

## 配置的自检与导出

`/server_info` 端点返回运行中服务的完整生效配置（开发模式端点，F-068）；`vllm collect-env` 收集环境信息用于 issue 报告（F-153）。

## 延伸阅读

- [01 快速开始](01-quickstart.md)：最小参数集实例
- [examples/04 基准测试](../examples/04-benchmarking.md)：以 SLO 为目标的参数调优闭环
- [12 分布式推理与扩展](12-distributed.md)：并行参数的组网细节
