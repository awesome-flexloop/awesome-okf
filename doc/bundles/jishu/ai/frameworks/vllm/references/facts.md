---
type: Reference
title: "事实清单 F-001~F-155（vLLM v0.32）"
description: "vLLM 知识包编号事实清单——155 条事实全部采自本地源码检出 v0.32.1rc0-283（2026-10-22）或 vllm.ai 官网/文档站，每条标注来源路径；推导性结论单独标记
tags: [vllm, facts, fact-list, evidence, source-cited]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /source-map.md
    title: 本地源码检出登记（vllm-project/vllm @ 7d53359）
  - id: website
    url: https://vllm.ai/
    title: vLLM 官网与文档站
---

# 事实清单 F-001~F-155

采集口径：**本地源码（第一手）+ 官网/文档站（第一手）**；每条事实给出来源（源码相对路径或文档 URL）。标注「推导」的为基于事实的工程结论，非原文陈述。时点敏感数字（Star 数、兼容表）均注明抓取日期 2026-10-22。

## 一、项目身份与版本（F-001~F-009）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-001 | 官方定位：vLLM 是 "A high-throughput and memory-efficient inference and serving engine for LLMs"（高吞吐、省显存的 LLM 推理与服务平台） | 官网首页 hero；README.md |
| F-002 | 本地源码检出版本 `v0.32.1rc0-283-g7d5335936c`（commit `7d53359`，2026-10-22 07:26 UTC）；本包源码路径类事实的统一信源 | 本地 git describe |
| F-003 | 官网文档站 stable 版本为 0.32.0；版本号对外引用以官网 stable 为口径 | docs.vllm.ai/en/latest（2026-10-22 抓取） |
| F-004 | 许可证 Apache-2.0 | 仓库根 `LICENSE` |
| F-005 | 出身 UC Berkeley Sky Computing Lab，现为 PyTorch Foundation 旗下项目 | 官网 Community/Governance 页 |
| F-006 | GitHub Star 95K+、贡献者 3.8K+（2026-10 官网时点；动态数字，引用须带日期） | 官网首页（2026-10-22 抓取） |
| F-007 | 核心论文《Efficient Memory Management for LLM Serving with PagedAttention》，SOSP 2023，arXiv 2309.06180 | 论文页 |
| F-008 | Python 版本要求：官网安装页 3.10+（3.12+ 推荐）；本地 `docs/getting_started/quickstart.md` 为 3.11–3.14 | docs/getting_started/quickstart.md |
| F-009 | 源码树规模：`vllm/` 2881 个 Python 文件、`tests/` 2196、`examples/` 159、`docs/` 245 篇 Markdown、`csrc/` 263 个 CUDA/C++ 文件 | 本地 find 统计（2026-10-22） |

## 二、V1 架构与进程模型（F-010~F-019）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-010 | V1 进程模型：API Server + Engine Core（每 DP rank 1 个）+ GPU Worker（每 GPU 1 个）+ DP Coordinator（DP>1 时）；进程间经 ZMQ 消息队列连接 | docs/design/arch_overview.md；`vllm/v1/engine/core.py` |
| F-011 | 进程计数公式：**Total = A + DP + N（+1 if DP>1）**，A=API server 数、DP=data parallel size、N=DP×PP×TP=GPU 总数；官方算例：单节点 TP4 = 1 API + 0 + 4 worker；DP2×TP4 = 1 API + 2 core + 8 worker + 1 coordinator | docs/design/arch_overview.md |
| F-012 | 通信拓扑：每个 API server 经 ZMQ 连接所有 engine core（多对多），任一 API server 可把请求路由到任一 engine core；API server 内媒体加载线程数由 `VLLM_MEDIA_LOADING_THREAD_COUNT` 控制（默认 8） | docs/design/arch_overview.md |
| F-013 | 配置体系：`EngineArgs`（`vllm/engine/arg_utils.py`，约 3266 行 dataclass）接收全部引擎参数，归并生成 `VllmConfig`，在 Engine→Executor→Worker→ModelRunner→Model 全链路传递；KV 容量可由 `--kv-cache-memory-bytes` 按字节指定；CUDA graph 捕获尺寸由 `--cudagraph-capture-sizes`/`--max-cudagraph-capture-size` 控制 | `vllm/engine/arg_utils.py`；docs/design/arch_overview.md |
| F-014 | V1 模型统一构造签名强制 keyword-only 参数；`prefix` 参数用于按 state-dict 名字差异化初始化（非均匀量化、vision/language 子模型）；仓库外老模型用 shim 类适配 | `vllm/model_executor/models/interfaces.py` 及 docs/design |
| F-015 | 初始化时即按 TP 切分与量化权重：405B 模型（约 810GB 权重）在 16×H100 上每卡只需加载约 50GB 分片，避免「全量加载再切分」的翻倍显存 | docs/design/arch_overview.md |
| F-016 | V0 引擎已完全废弃（RFC #18571）；v0.32 起 V1 是唯一引擎 | docs/usage/v1_guide.md；RFC #18571 |
| F-017 | V1 重写目标四点：简单模块易修改、近零 CPU 开销、优化统一、零配置默认开启；2025-01 发布 alpha，2026 年已成唯一引擎 | docs/usage/v1_guide.md |
| F-018 | V1 统一调度器把 prefill 与 decode 视为同一件事：用 `{request_id: num_tokens}` 字典动态分配每步 token 预算，无硬性阶段分离（V0 一次 step 只能处理一种） | docs/usage/v1_guide.md；`vllm/v1/core/sched/scheduler.py` |
| F-019 | V1 默认开启：chunked prefill（`enable_chunked_prefill` 默认 True，V0 按模型条件启用）、prefix caching、CUDA graphs；V1 CUDA graph 占显存比 V0 多；logprobs 默认原始 raw（`--logprobs-mode` 可调）；prompt logprobs + 前缀缓存不缓存、重算全量 prefill | `vllm/config/scheduler.py:134`；docs/usage/v1_guide.md |

## 三、引擎内部：AsyncLLM 与调度数据结构（F-020~F-029）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-020 | V1 默认开启特性清单（chunked prefill / prefix caching / CUDA graphs）与 V0 的差异对照见 v1_guide | docs/usage/v1_guide.md |
| F-021 | `AsyncLLM`（`vllm/v1/engine/async_llm.py`）实现 `EngineClient` 接口，是 API server 与 EngineCore 之间的客户端；`EngineCore`（`vllm/v1/engine/core.py`）是引擎核心进程逻辑 | `vllm/v1/engine/async_llm.py`、`core.py` |
| F-022 | 每个 DP rank 对应一个 EngineCore 进程（`EngineCoreProc(dp_rank)`），内部持有本地 `EngineCore` 实例 | `vllm/v1/engine/core.py` |
| F-023 | detokenize 在 API server 侧由 `_run_output_handler` 完成（增量 detokenize），EngineCore 只回传 token 级输出 | `vllm/v1/engine/async_llm.py` |
| F-024 | `RequestOutputCollector`（`vllm/v1/engine/output_processor.py`）按请求收集输出，支持流式 `put`/`get`；`StreamingInputOutputCollector` 处理流式输入 | `vllm/v1/engine/output_processor.py` |
| F-025 | Scheduler 主入口 `schedule()` 返回 `SchedulerOutput`；请求状态转换由 `update_from_output` 在每步后更新 | `vllm/v1/core/sched/scheduler.py` |
| F-026 | Scheduler 维护四类队列：`waiting`（等待）、`kv_holding_waiting`（持块等待）、`deferred_waiting`（延迟）、`running`（运行中） | `vllm/v1/core/sched/scheduler.py:224-232` |
| F-027 | 每步令牌预算：`token_budget = max_num_scheduled_tokens`，`input_budget = max_num_batched_tokens`；running 请求按序消耗预算 | `vllm/v1/core/sched/scheduler.py:642-715` |
| F-028 | 支持抢占：`_preempt_request` 在 KV 不足时抢占运行中请求（重算路径），`reset_preempted_req_ids` 记录上步被抢占请求 | `vllm/v1/core/sched/scheduler.py:1658` |
| F-029 | `max_num_running_reqs = scheduler_config.max_num_seqs`，即运行队列上限等于 max_num_seqs | `vllm/v1/core/sched/scheduler.py:130` |

## 四、KV 缓存与 PagedAttention（F-030~F-039）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-030 | PagedAttention 把 KV cache 切成固定大小 block 按需分配，来源论文 SOSP 2023（arXiv 2309.06180） | 论文；docs/design/paged_attention.md |
| F-031 | `KVCacheBlock` 一个 block 存固定数量 token 的 KV，**默认 16 token/block**（非 MLA 标准 transformer 层的显存公式见 docs） | `vllm/v1/core/block_pool.py`；docs/features/automatic_prefix_caching |
| F-032 | `BlockPool`/`free_block_queue` 管理可用 block（双向链表池）；decode 时注意力内核按块表索引拼接历史 KV，block 物理不连续、逻辑连续 | `vllm/v1/core/block_pool.py`；docs/design/paged_attention.md |
| F-033 | prefix caching 默认开启；命中按块前缀匹配；`/reset_prefix_cache` 可清空（开发端点） | docs/features/automatic_prefix_caching.md；`vllm/entrypoints/openai/api_server.py` |
| F-034 | continuous batching：所有序列 flatten 拼成一条 super sequence，靠 position 索引与 attention mask 隔离，免 right-padding；prefill/decode 请求混编同行 | docs/usage/v1_guide.md；docs/design/arch_overview.md |
| F-035 | block 大小默认 16，可调；不同注意力结构有不同 KV spec | `vllm/config/cache.py` |
| F-036 | 前缀缓存命中基于块内容哈希的前缀匹配 | `vllm/v1/core/kv_cache_manager.py` |
| F-037 | KV spec 分组管理：`register_all_kvcache_specs(vllm_config)` 按层注册 spec，`KVCacheSpecRegistry.get_manager_class` 选择管理器，`single_type_kv_cache_manager.py` 分管各类型 | `vllm/v1/core/single_type_kv_cache_manager.py:2645`；`vllm/v1/kv_cache_spec_registry.py` |
| F-038 | 多模态 encoder cache：视觉编码器输出缓存，`/reset_encoder_cache` 为其管理端点（开发模式） | `vllm/v1/core/encoder_cache_manager.py`；api_server.py |
| F-039 | KV spec 类型：`FullAttentionSpec`、`MLAAttentionSpec`、`RSWASpec`（滑窗）、`MambaSpec`（状态空间）、`HiddenStateCacheSpec`；聚合容器 `UniformTypeKVCacheSpecs` | `vllm/v1/kv_cache_interface.py` |

## 五、调度（F-040~F-049）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-040 | `--scheduling-policy` 二选一：`fcfs`（先来先服务）与 `priority`（优先级） | `vllm/config/scheduler.py` |
| F-041 | engine step 内部恒为三段：Schedule → Execute → Update；`GPUModelRunner` 每步做五件事（输入批处理/准备 attention metadata/前向/采样/输出组装）；stop 细节：`stop_token_ids` 会出现在输出里，stop strings 不会（截断到首次出现处） | `vllm/v1/engine/core.py`；`vllm/v1/worker/gpu_model_runner.py` |
| F-042 | `allocate_slots`（`vllm/v1/core/kv_cache_manager.py`）为调度请求分配 KV block 槽位 | `vllm/v1/core/kv_cache_manager.py:371` |
| F-043 | Prefill 请求对整个 prompt 做一次前向，compute-bound，最后位置采样新 token；Decode 请求只算最新 token，memory-bandwidth-bound | docs/design/arch_overview.md |
| F-044 | `SchedulerOutput` 字段：`scheduled_new_reqs`（首次调度）、`scheduled_cached_reqs`（已缓存请求的 diff）、`num_scheduled_tokens`（req_id→token 数）、`total_num_scheduled_tokens`、`scheduled_spec_decode_tokens` | `vllm/v1/core/sched/output.py:232` |
| F-045 | 令牌预算分配：running 中 decode 请求优先消耗预算，剩余给新 prefill；超预算的长 prefill 截断为 chunk | `vllm/v1/core/sched/scheduler.py:715-767` |
| F-046 | chunked prefill：限制每步新 token 数（`long_prefill_token_threshold`），超长 prompt 分步算，保护其他请求 TTFT；V1 默认开启 | `vllm/config/scheduler.py:79,134` |
| F-047 | 默认值：`max_num_seqs` = 128（`DEFAULT_MAX_NUM_SEQS`）、`max_num_batched_tokens` = 2048（`DEFAULT_MAX_NUM_BATCHED_TOKENS`） | `vllm/config/scheduler.py:41-62` |
| F-048 | `long_prefill_token_threshold` 默认 0（即不按阈值截断）；`long_prefill_token_threshold_adaptive` 默认 False | `vllm/config/scheduler.py:79-86` |
| F-049 | `watermark` 默认 0.0（关闭）；设为 >0 时为接纳 waiting/被抢占请求保留的空闲 block 比例 | `vllm/config/scheduler.py:196` |

## 六、执行层：Worker 与 Executor（F-050~F-055）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-050 | 惯例「一个进程控制一个加速器设备」：TP=2×PP=2 即 4 个 worker；worker 由 `rank`（全局）与 `local_rank`（设备分配）标识 | docs/design/arch_overview.md；`vllm/v1/worker/gpu_worker.py` |
| F-051 | `--enforce-eager` 默认 False（即默认启用 CUDA graph） | `vllm/engine/arg_utils.py` |
| F-052 | CUDA graph 两种模式（piecewise/full）；`--enforce-eager` 关闭图捕获；V1 图捕获比 V0 占更多显存 | docs/design/arch_overview.md；`vllm/config/compilation.py` |
| F-053 | Worker 初始化三步：Init device（分配设备、验证显存、建分布式组、实例化 model_runner 与 CPU 侧 InputBatch）→ Load model（实例化架构、TP 切分加载、`model.eval()`、可选 compile）→ Initialize KV cache（取每层 KV spec、profiling 前向 + 显存快照估算 block 数、分配绑定、捕获 CUDA graph） | `vllm/v1/worker/gpu_worker.py` |
| F-054 | `Executor`（`vllm/v1/executor/abstract.py`）是对引擎暴露的统一执行接口——「在一个设备或多个设备上执行模型」；`UniProcExecutor` 单进程单 GPU 直接调用 worker | `vllm/v1/executor/abstract.py`、`uniproc_executor.py` |
| F-055 | `MultiprocExecutor` 单机多卡：每 rank spawn 守护进程，共享内存消息队列 `rpc_broadcast_mq`/`worker_response_mq` 广播任务、回收结果；`execute_model` 调用方式对引擎透明（单卡直接调用、多卡经队列间接） | `vllm/v1/executor/multiproc_executor.py` |

## 七、编译、注意力与采样（F-056~F-059）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-056 | `--compilation-config` 控制编译等级（`vllm/config/compilation.py`）：piecewise/full compile、编译缓存（避免重启重编译）、图级变换；官方文档 `docs/design/torch_compile.md` 专篇 | `vllm/config/compilation.py`；docs/design/torch_compile.md |
| F-057 | `GPUModelRunner`（`vllm/v1/worker/gpu_model_runner.py`）约 7200 行，是每步执行的核心 | 本地 wc -l |
| F-058 | 注意力后端位于 `vllm/v1/attention/backends/`（FlashAttention/FlashInfer/Triton 等）；paged_attention.md 自述为历史文档，现实现见 `csrc/` 与 backends | docs/design/paged_attention.md |
| F-059 | 采样器位于 `vllm/v1/sample/`（`sampler.py` 与 logits processors），由 model runner 持有 | `vllm/v1/sample/` |

## 八、入口、配置与在线服务（F-060~F-079）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-060 | 离线入口：`from vllm import LLM, SamplingParams`，`llm.generate(prompts, params)` 一次提交一批、同步返回 `RequestOutput` 列表 | `vllm/entrypoints/llm.py`；docs/getting_started/quickstart.md |
| F-061 | CLI 参数由 `EngineArgs` 字段自动生成（`vllm --help` 与 `vllm serve --help` 同源）；Python 侧 `LLM(model=..., tensor_parallel_size=...)` 与 CLI 同源 | `vllm/engine/arg_utils.py` |
| F-062 | chat 模板：chat 端点要求模型 tokenizer 配置带 Jinja2 模板；`llm.chat()`/`/v1/chat/completions` 内部按模板拼装 | docs/serving/online_serving/openai_compatible_server.md |
| F-063 | Anthropic 兼容：`/v1/messages`、`/v1/messages/count_tokens`；源码 `vllm/entrypoints/anthropic/` | docs/serving/online_serving/ |
| F-064 | 在线入口：`vllm serve <model>` 默认监听 `http://localhost:8000`；`--api-key` 启用 Bearer 鉴权 | docs/serving/online_serving/openai_compatible_server.md |
| F-065 | 无 chat 模板的模型聊天请求直接报错，补救 `--chat-template ./path.jinja`（文件或内联）；多模态 content 格式自动探测（`string`/`openai` 列表），不符时 `--chat-template-content-format` 覆盖 | docs/serving/online_serving/openai_compatible_server.md |
| F-066 | 运维端点：`/health`、`/v1/models`、`/version`、`/load`、`/tokenize`、`/detokenize`、`/tokenizer_info`、`/start_profile`、`/stop_profile` | `vllm/entrypoints/openai/api_server.py` |
| F-067 | LoRA 动态加载/卸载：`/v1/load_lora_adapter`、`/v1/unload_lora_adapter`（仅限本地开发） | `vllm/entrypoints/openai/api_server.py` |
| F-068 | `VLLM_SERVER_DEV_MODE=1` 开启开发端点（生产禁用）：`/reset_prefix_cache`、`/reset_mm_cache`、`/reset_encoder_cache`、`/init_weight_transfer_engine`、`/update_weights`、`/sleep`、`/wake_up`、`/collective_rpc`；`/server_info` 返回生效配置 | `vllm/entrypoints/openai/api_server.py` |
| F-069 | vLLM 自定义端点族：`/v1/embeddings`、`/v1/score`、`/v1/classification`、`/v1/decisions`、`/v1/audio/transcriptions`、`/v1/audio/translations` | `vllm/entrypoints/openai/api_server.py` |
| F-070 | 参数优先级链：命令行 > 环境变量（`VLLM_*`，如 `VLLM_API_KEY`）> 模型自带 `generation_config.json` > 默认值；`generation_config="vllm"` 切断模型配置 | `vllm/config/model.py`；docs/getting_started/quickstart.md |
| F-071 | `--served-model-name` 可指定对外暴露的模型名（可多个） | `vllm/engine/arg_utils.py` |
| F-072 | Responses API：`/v1/responses`（含 `/{id}`、`/{id}/cancel`） | `vllm/entrypoints/openai/` |
| F-073 | 音频端点：`/v1/audio/transcriptions`、`/v1/audio/translations`（ASR 模型） | `vllm/entrypoints/openai/` |
| F-074 | `/v1/decisions`：谓词/选择/评分三类 typed 问题 | `vllm/entrypoints/openai/` |
| F-075 | 工具调用：chat completions 传 `tools=[...]`，`parallel_tool_calls` 控制并行工具调用；`/v1/completions` 不支持 `suffix` 参数 | docs/serving/online_serving/openai_compatible_server.md |
| F-076 | 批量变体：`/v1/chat/completions/batch` | `vllm/entrypoints/openai/` |
| F-077 | 流式：`stream=True` 走 SSE，逐 chunk 收 `choices[0].delta.content` | docs/serving/online_serving/ |
| F-078 | chat completions 的 `user` 参数被忽略 | docs/serving/online_serving/openai_compatible_server.md |
| F-079 | `/metrics` 提供 Prometheus 指标 | `vllm/v1/metrics/prometheus.py` |

## 九、模型支持（F-080~F-089）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-080 | 模型注册表 `vllm/model_executor/models/registry.py` 按任务类型分字典登记，`@_ModelRegistry.register_model` 装饰器把 `architectures` 映射到实现类 | `vllm/model_executor/models/registry.py` |
| F-081 | 注册表架构计数（2026-10-22）：文本生成 121、多模态 124、投机解码 65、embedding 33、reward 3，合计 346 | 本地统计 registry.py |
| F-082 | 官网口径 "200+ model architectures"（docs/models/supported_models.md），与注册表计数统计对象/时点不同 | docs/models/supported_models.md |
| F-083 | `--model-impl` 默认 `auto`：注册表命中走 vLLM 原生实现，未命中回退 Transformers modeling backend（`vllm/model_executor/models/transformers/`） | `vllm/config/model.py`；docs/models/supported_models.md |
| F-084 | 官方口径：Transformers backend 性能与专用 vLLM 实现一致；代价是首次加载稍慢、部分融合算子不可用 | docs/models/supported_models.md |
| F-085 | 自定义模型路径一：在 `vllm/model_executor/models/` 新增实现类并装饰注册 | docs/models/supported_models.md |
| F-086 | 自定义模型路径二：HuggingFace 模型遵循自定义模型规范（`vllm_config` 传参、weights 加载约定）即可跑，无需改 vLLM 代码 | docs/models/supported_models.md |
| F-087 | 架构匹配按 HF config 的 `architectures` 列表顺序匹配注册表键 | `vllm/model_executor/models/registry.py` |
| F-088 | 任务类型由 `LLM(task=...)` 指定（generate/embed/classify/score 等），对应不同注册表与服务端点 | `vllm/entrypoints/llm.py` |
| F-089 | 外挂模型可经插件机制注册，避免 fork vLLM | docs/contributing/ |

## 十、量化配置入口与 KV 量化（F-090~F-095）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-090 | `--kv-cache-dtype` 支持 `fp8`/`fp8_e4m3`/`fp8_e5m2`，KV 以 FP8 存储显存约减半，精度损失依模型而异 | docs/features/quantization/quantized_kvcache.md |
| F-091 | `--quantization` 缺省时从模型 config 的 `quantization_config` 读取；`--linear-backend` 选择线性层内核后端 | `vllm/engine/arg_utils.py` |
| F-092 | `fbgemm_fp8.py` 与 `fp8.py` 为两套 FP8 实现（fbgemm 核 vs 通用核） | `vllm/model_executor/layers/quantization/` |
| F-093 | `mxfp4.py` 支持 OCP MXFP4/MXFP8 格式 | `vllm/model_executor/layers/quantization/mxfp4.py` |
| F-094 | `modelopt.py`/`modelopt_block_quant.py` 承接 NVIDIA Model Optimizer（NVFP4）量化 | `vllm/model_executor/layers/quantization/modelopt.py` |
| F-095 | KV cache 量化实现位于 `vllm/model_executor/layers/quantization/kv_cache.py`，与 `--kv-cache-dtype` 联动 | `vllm/model_executor/layers/quantization/kv_cache.py` |

## 十一、量化方法（F-096~F-109）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-096 | vLLM 消费外部工具（llm-compressor、AutoAWQ、GPTQModel、NVIDIA Model Optimizer、AMD Quark、TorchAO、Intel INC）产出的量化权重，运行时提供对应 kernel | docs/features/quantization/README.md |
| F-097 | 量化硬件兼容表（2026-10 时点）：Volta=SM 7.0、Turing=7.5、Ampere=8.0/8.6、Ada=8.9、Hopper=9.0；*Turing 不支持 Marlin MXFP4；Intel Gaudi 量化已迁至 vllm-gaudi | docs/features/quantization/README.md |
| F-098 | 官方 quickstart 的 FP8 案例在 Hopper 上运行（neuralmagic FP8 权重） | docs/getting_started/quickstart.md |
| F-099 | INT4（W4A16）家族（GPTQ/AWQ）跨代兼容最广，Volta 起 NVIDIA 全系 | docs/features/quantization/README.md |
| F-100 | GGUF 保持 llama.cpp 生态兼容，NVIDIA 全系 + AMD GPU 可用 | docs/features/quantization/README.md |
| F-101 | MoE 量化：线性层与专家层可分别配置；`FusedMoE` 走 `FusedMoEMethodBase` 子类（如 `Fp8MoEMethod`），未量化专家用 `UnquantizedFusedMoEMethod` 跳过 | docs/features/quantization/README.md；`vllm/model_executor/layers/fused_moe/` |
| F-102 | llm-compressor 格式同时携带权重量化与忽略层清单 | docs/features/quantization/llm_compressor/README.md |
| F-103 | 树外量化插件：`@register_quantization_config` 装饰器注册，实现 `QuantizationConfig.get_quant_method`（对 `FusedMoE` 返回 `FusedMoEMethodBase` 子类） | docs/features/quantization/README.md |
| F-104 | 量化插件经 `vllm/plugins/` 机制被发现；硬件厂商（AMD Quark、Intel INC、NVIDIA ModelOpt）以此模式集成 | docs/features/quantization/README.md |
| F-105 | Marlin 是 GPTQ/AWQ/FP8/FP4 的统一高性能内核后端（Turing 起） | `vllm/model_executor/layers/quantization/utils/` |
| F-106 | 在线量化：`quantization/online/` 目录支持运行时量化（online quantization） | `vllm/model_executor/layers/quantization/online/` |
| F-107 | Humming 后端承接 NVFP4 W4A16 线性层（llm-compressor 场景） | docs/features/quantization/README.md |
| F-108 | 社区/厂商后端：`quark`（AMD）、`torchao.py`（TorchAO）、`inc`（Intel Neural Compressor）、`turboquant` | `vllm/model_executor/layers/quantization/` |
| F-109 | `compressed_tensors/` 实现 llm-compressor 统一压缩格式容器 | `vllm/model_executor/layers/quantization/compressed_tensors/` |

## 十二、投机解码（F-111~F-125，含 F-151/F-154/F-155）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-111 | 投机解码：用小模型/廉价方法先猜若干 token，目标模型一次前向批量验证，猜中部分免去串行解码 | docs/features/speculative_decoding/README.md |
| F-114 | `--speculative-config` 公共键：`method`、`model`、`draft_tensor_parallel_size`、`max_model_len`、`parallel_drafting`（仅 EAGLE/draft-model）、`draft_sample_method`（greedy/probabilistic）、`use_heterogeneous_vocab`（仅 draft_model） | docs/features/speculative_decoding/README.md |
| F-116 | 接受率采集：`vllm/v1/spec_decode/metrics.py` 与 docs/features/speculative_decoding/acceptance_metrics.md | `vllm/v1/spec_decode/metrics.py` |
| F-117 | 经验法则（推导）：接受率 < 40% 时应减小 `num_speculative_tokens` 或更换方法——投机深度超过模型可预测性后吞吐反降 | 推导（基于 F-116 口径） |
| F-118 | 可用 `vllm-project/speculators` 库训练 EAGLE/draft 草稿模型并无缝接入 | docs/features/speculative_decoding/speculators.md |
| F-119 | 投机 token 参与调度预算：`SchedulerOutput.scheduled_spec_decode_tokens` 传递每请求投机 token | `vllm/v1/core/sched/output.py:248` |
| F-124 | EAGLE 实现 `vllm/v1/spec_decode/eagle.py`；`extract_hidden_states.py` 从目标模型提取隐藏状态训练草稿头 | `vllm/v1/spec_decode/` |
| F-125 | n-gram/suffix 方法零模型成本：`ngram_proposer.py`/`ngram_proposer_gpu.py`/`suffix_decoding.py` | `vllm/v1/spec_decode/` |
| F-151 | 模型类 proposer 共享 `llm_base_proposer.py` 基类；`metadata.py` 管逐请求元数据 | `vllm/v1/spec_decode/` |
| F-154 | Gemma 4 assistant checkpoint 必须走 `method: mtp`，误配 draft_model 会触发启动告警 | docs/features/speculative_decoding/README.md |
| F-155 | 选型口径：模型类方法（EAGLE/MTP/draft）延迟收益最大；n-gram/suffix 零模型成本，适合峰值流量不增负载场景 | docs/features/speculative_decoding/README.md |

## 十三、分布式推理（F-110、F-112~F-113、F-115、F-126~F-135）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-110 | 五种并行度参数：`--tensor-parallel-size`、`--pipeline-parallel-size`、`--data-parallel-size`、`--enable-expert-parallel`、上下文并行（`prefill/decode_context_parallel_size`）；多机 `--nnodes`/`--node-rank` | `vllm/engine/arg_utils.py` |
| F-112 | `--data-parallel-size N` 多副本提高总吞吐，API server 自动扩展；多机经 `--nnodes`/`--node-rank` + `--master-addr`/`--master-port` | `vllm/engine/arg_utils.py` |
| F-113 | 请求生命周期：API server 接收 → EngineCore → Scheduler（schedule/execute/update 三步）→ Worker/ModelRunner 前向采样 → 输出回传 → detokenize → 响应 | docs/design/arch_overview.md；`vllm/v1/engine/core.py` |
| F-115 | Ray 系执行器（`ray_executor_v2.py`）经 Ray 管理 worker 生命周期，支持多机与弹性 EP | `vllm/v1/executor/ray_executor_v2.py` |
| F-126 | 并行组由 `vllm/distributed/parallel_state.py` 统一管理：每种并行一个 `GroupCoordinator`（`get_tp_group`/`get_pp_group`/`get_dp_group`/`get_ep_group` 等），集合通信经 `all_reduce`/`all_gather`/`reduce_scatter` 原语下发 | `vllm/distributed/parallel_state.py` |
| F-127 | ETP（expert tensor parallel）是 TP 在专家层的变体，由 `get_etp_group` 管理 | `vllm/distributed/parallel_state.py:1601` |
| F-128 | Ray 路径支持弹性与异构放置（GPU 型号混合），代价是集群运维复杂度 | docs/serving/distributed_serving/ |
| F-129 | DP 主从参数：`--data-parallel-address`/`--data-parallel-rpc-port` 指定 DP coordinator 入口，`--data-parallel-start-rank` 区分主从；API server 只在主节点 | docs/serving/distributed_serving/ |
| F-130 | EP 常与 TP 组合（如 TP8+EP8），专家并行对 MoE 模型显存分布收益最大 | docs/serving/distributed_serving/ |
| F-131 | 上下文并行按序列切分 attention 计算，配合 chunked prefill 处理超长 prompt | docs/serving/distributed_serving/ |
| F-132 | DCP/PCP 上下文并行组：`get_dcp_group`（decode context parallel）、`get_pcp_group`（prefill context parallel）；DCP 会改变 KV block 切分（`resolve_dcp_kv_block_size`） | `vllm/distributed/parallel_state.py:1627,1683`；`vllm/v1/core/kv_cache_utils.py:740` |
| F-133 | `world_size = TP × PP × DP`（EP 在 TP 维度内切分专家，不占额外卡）；V1 为每个 DP rank 起一个 EngineCore 进程 | docs/design/arch_overview.md |
| F-134 | `MultiprocExecutor` 是单机多卡默认路径 | `vllm/v1/executor/multiproc_executor.py` |
| F-135 | Ray executor 支持多机多卡与弹性放置 | `vllm/v1/executor/ray_executor_v2.py` |

## 十四、进阶主题（F-136~F-150、F-152~F-153）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-136 | 插件系统三类树外扩展点：`vllm/plugins/io_processors`（I/O 处理）、`lora_resolvers`（LoRA 解析）、`endpoint_plugins`（自定义端点） | `vllm/plugins/` |
| F-137 | 可观测性：`vllm/v1/metrics/` 含 Prometheus 导出（`prometheus.py`）、日志器（`loggers.py`）、缓存命中来源统计（`cache_hit_source.py`） | `vllm/v1/metrics/` |
| F-138 | 部署三路径：Docker（官方 `vllm/vllm-openai` 镜像）、K8s、Nginx；frameworks/integrations 收录 KServe、Ray Serve 等生态集成 | docs/deployment/ |
| F-139 | RL 训练接口文档族：`docs/training/rlhf.md`、`async_rl.md`、`weight_transfer/`（权重同步）、`layerwise.md`、`routed_experts.md`、`sampling_mask.md`、`prompt_token_id_logprobs.md`、`weight_checker.md`、`trl.md` | docs/training/ |
| F-140 | KV 卸载：`--cpu-offload-gb` 指定卸载到 CPU 内存的 GB 数，冷块换出按需换入；分层/外部卸载（NVMe、分级存储）经 KV connector 实现 | docs/features/kv_offloading_usage.md |
| F-141 | PD 分离文档：`docs/features/disagg_prefill.md`、`disagg_encoder.md`；KV 传输连接器文档：mooncake/nixl/moriio/ec_cpu 系列 | docs/features/ |
| F-142 | LoRA 参数：`--enable-lora`、`--max-loras`、`--max-lora-rank`、`--lora-dtype` | `vllm/engine/arg_utils.py` |
| F-143 | 结构化输出：`vllm/v1/structured_output/` 四后端（xgrammar/guidance/outlines/lm-format-enforcer），`--structured-outputs-config.backend` 默认 `auto`；请求级参数 `structured_outputs`（json/regex/choice/grammar/structural_tag）；`guided_*` 旧字段 v0.12.0 起移除 | docs/features/structured_outputs.md；`vllm/v1/structured_output/` |
| F-144 | LoRA 源码：`vllm/lora/`（`model_manager.py`/`worker_manager.py` 管理加载分发，`punica_wrapper` Punica 打包内核，`peft_helper.py` 对接 PEFT） | `vllm/lora/` |
| F-145 | docs/training 配套能力：layerwise（逐层流水）、routed_experts（MoE 路由记录）、sampling_mask、prompt_token_id_logprobs、weight_checker、trl | docs/training/ |
| F-146 | 调度质量四指标：TTFT（首 token 延迟）、ITL/TPOT（token 间延迟）、吞吐、goodput（满足 SLO 的吞吐） | docs/benchmarking/；docs/design/arch_overview.md |
| F-147 | `vllm bench` 工具族位于 `vllm/entrypoints/cli/benchmark/`：serve（在线压测）、throughput（离线吞吐）、latency（延迟）、sweep（参数扫描）、startup（启动分解）、forward、mm_processor | `vllm/entrypoints/cli/benchmark/` |
| F-148 | `vllm bench serve` 在 `VLLM_USE_RUST_BENCH` 开启时委托给 Rust 版 CLI（`rust/`），行为兼容 | `vllm/entrypoints/cli/benchmark/main.py:24-35` |
| F-149 | `vllm bench sweep` 用花括号占位符自动枚举参数组合，结果落盘对比 | docs/benchmarking/sweeps.md |
| F-150 | 官方建议生产级压测用 GuideLLM（vllm-project/guidellm）：实时进度、自动报告、更灵活的数据集与负载模式 | docs/benchmarking/cli.md |
| F-152 | benchmark 数据集：ShareGPT、ShareGPT4V/4Video、BurstGPT、Random、RandomMultiModal、RandomForReranking、Prefix Repetition、HuggingFace-VisionArena/MMVU/InstructCoder/AIMO/MTBench/HumanEval/GSM8K/ASR 系列、Spec Bench | docs/benchmarking/cli.md |
| F-153 | `vllm collect-env` 收集环境信息用于 issue 报告 | `vllm/entrypoints/cli/collect_env.py` |

## 十五、安装与硬件平台（F-120~F-123）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-120 | 安装方式一（推荐）：`uv pip install vllm --torch-backend=auto`；conda 方式需先 `conda create -n myenv python=3.12`；`vllm download-kernels` 安装预编译内核，不装则 Hopper 及以上 GPU 启动时现场编译多花数分钟；FlashInfer 预编译内核同样需要该命令 | docs/getting_started/installation/README.md |
| F-121 | 硬件平台矩阵：NVIDIA CUDA（主仓库一等公民）、AMD ROCm（ROCm 7.0、glibc≥2.35、Python 3.12）、Intel GPU/XPU（官方 Docker 镜像，v0.26.0 起）、x86/ARM/PowerPC CPU（含 IBM Z S390X）、Google TPU（`uv pip install vllm-tpu`）、Apple Silicon（vLLM-Metal，MLX 后端）；官网首页宣称 "One engine, endless possibilities. Run any model on any hardware"——统一的是 API 与引擎语义 | docs/getting_started/installation/；官网首页 |
| F-122 | 硬件策略「主仓库统一 API + 仓库外硬件插件」：Ascend（vllm-ascend）、TPU（vllm-tpu）、Gaudi（vllm-gaudi）、Spyre（vllm-spyre）、Neuron 等为仓库外独立项目，各自实现平台 Executor 与 Worker | docs/getting_started/installation/；各插件仓库 |
| F-123 | Docker：官方镜像 `vllm/vllm-openai` 系列；ROCm/XPU 提供 nightly 变体（如 `vllm/vllm-openai-xpu:nightly`） | docs/deployment/docker.md |

## 事实覆盖核对

- 概念页 00–13 与示例页 01–04 引用的全部 F 编号均在清单内定义。
- 未引用但登记的条目（F-020、F-023~F-029、F-035~F-039、F-044~F-049、F-051、F-057~F-059、F-069、F-071~F-079、F-087~F-089、F-092~F-094、F-105~F-109、F-119、F-124~F-125、F-132~F-135、F-137~F-138、F-152）为背景事实，供检索与后续扩充引用。
