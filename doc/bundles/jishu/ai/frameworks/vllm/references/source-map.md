---
type: Reference
title: "信源登记：vLLM 源码树与官网结构"
description: "vLLM v0.32.1rc0-283 本地源码检出的目录结构、文件统计、关键文件清单，以及 vllm.ai 官网/文档站/blog 的页面结构登记，作为全部事实条目的定位索引"
tags: [vllm, source-map, source-registration, codebase-structure, docs-structure]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-repo
    resource: vllm-project/vllm
    title: 本地源码检出（git describe: v0.32.1rc0-283-g7d5335936c）
  - id: website
    url: https://vllm.ai/
    title: vLLM 官网
---

# 信源登记：vLLM 源码树与官网结构

本文件登记 vLLM 知识包的全部信源位置，供 [facts.md](facts.md) 的每条事实回溯定位。

## 本地源码检出

| 项 | 值 |
|----|-----|
| 路径 | `external/libs/ai/vllm-project/vllm`（相对 SpecWeave 工作区） |
| 版本 | `git describe` = `v0.32.1rc0-283-g7d5335936c` |
| Commit | `7d5335936c40306063a29fc4e2ccbe71b280e40c` |
| 提交时间 | 2026-10-22 07:26:05 UTC |
| 许可证 | Apache-2.0（`LICENSE`） |

### 仓库根目录

`vllm/`（主包）、`csrc/`（CUDA/C++ 内核）、`tests/`、`examples/`、`docs/`（mkdocs 站点，`mkdocs.yaml` 驱动）、`benchmarks/`、`docker/`、`requirements/`、`rust/`（含 Rust bench CLI）、`cmake/`、`tools/`、`recipes/`。

### 文件统计（2026-10-22 快照）

| 区域 | 规模 |
|------|------|
| `vllm/` Python 文件 | 2881 |
| `tests/` Python 文件 | 2196 |
| `examples/` Python 文件 | 159 |
| `docs/` Markdown | 245 |
| `csrc/` CUDA/C++ 文件 | 263 |

### 关键文件登记

| 模块 | 路径 | 作用 |
|------|------|------|
| 包入口 | `vllm/__init__.py` | 公开 API 聚合（`LLM`、`SamplingParams` 等） |
| 离线入口 | `vllm/entrypoints/llm.py` | `LLM` 类 |
| 引擎参数 | `vllm/engine/arg_utils.py` | `EngineArgs` dataclass（约 3266 行） |
| 配置对象 | `vllm/config/model.py`、`vllm/config/` | `ModelConfig`、`VllmConfig` 族 |
| V1 引擎 | `vllm/v1/engine/` | `core.py`（EngineCore）、`async_llm.py`（AsyncLLM）、`llm_engine.py` |
| 调度器 | `vllm/v1/core/sched/scheduler.py` | V1 Scheduler |
| KV 管理 | `vllm/v1/core/kv_cache_manager.py`、`block_pool.py`、`kv_cache_utils.py` | block 池与 KV spec |
| Worker | `vllm/v1/worker/gpu_worker.py`、`gpu_model_runner.py` | 设备进程与模型运行 |
| 执行器 | `vllm/v1/executor/` | uniproc/multiproc/ray 执行器 |
| 并行 | `vllm/distributed/parallel_state.py` | GroupCoordinator 与并行组 |
| 模型注册 | `vllm/model_executor/models/registry.py` | 架构注册表 |
| 量化 | `vllm/model_executor/layers/quantization/` | 各量化方法实现 |
| 投机解码 | `vllm/v1/spec_decode/` | proposer 家族 |
| 结构化输出 | `vllm/v1/structured_output/` | 四后端 |
| LoRA | `vllm/lora/` | LoRA 全链路 |
| 采样 | `vllm/v1/sample/` | Sampler 与 logits processors |
| 指标 | `vllm/v1/metrics/` | Prometheus 等 |
| CLI | `vllm/entrypoints/cli/` | serve/bench 等子命令 |
| OpenAI 服务 | `vllm/entrypoints/openai/` | API server |
| 插件 | `vllm/plugins/` | io_processors/lora_resolvers/endpoint_plugins |

## 官网与文档站结构

### 导航（vllm.ai，2026-10-22 抓取）

- 顶导航：**Docs**（→ docs.vllm.ai/en/latest/）、**Blog**（→ blog.vllm.ai，约 159 篇）、**Community**（contributing/slack/meetups/governance/sponsorship）、**Sponsors**、**Users**、**Events**、**GitHub**、**Slack**。
- 首页：hero 定位语 "A high-throughput and memory-efficient inference and serving engine for LLMs"；Universal Compatibility 宣称 "One engine, endless possibilities. Run any model on any hardware"。

### 文档站（docs.vllm.ai/en/latest/）侧栏结构

| 一级节 | 代表页面 |
|--------|---------|
| Getting Started | quickstart、installation（GPU/CPU/ROCm/TPU 等） |
| Serving | OpenAI Compatible Server、Distributed Serving、Production Stack |
| Models | Supported Models（200+ architectures）、Extensions |
| Features | Quantization、Speculative Decoding、Structured Outputs、Automatic Prefix Caching、LoRA、Tool Calling、Multimodal Inputs 等 |
| Usage | V1 Guide |
| Design | Architecture Overview、PagedAttention、torch.compile 等 |
| Benchmarking | Benchmark CLI、Parameter Sweeps |
| Deployment | Docker、K8s、Nginx、Frameworks |
| Community / Governance / Contributing | — |

### 其他信源

- 架构博客：《Inside vLLM: Anatomy of a High-Throughput LLM Inference System》（2025-09-05，blog.vllm.ai）——请求全生命周期分组件解读。
- 论文：《Efficient Memory Management for LLM Serving with PagedAttention》，SOSP 2023，arXiv 2309.06180。
- 本地 `docs/` 与官网文档同源（mkdocs 构建源），本包大量引用本地 `docs/*.md`，路径均已登记。
