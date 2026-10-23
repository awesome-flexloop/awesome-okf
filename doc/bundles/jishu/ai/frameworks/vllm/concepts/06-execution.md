---
type: Concept
title: "执行层：Executor、Worker 与 ModelRunner"
description: "vLLM 执行栈——Executor 抽象（UniProc/Multiproc/Ray）、每 GPU 一个 Worker、ModelRunner 的三步初始化与 execute_model 五步、CUDA Graph 捕获与 replay、torch.compile 与编译缓存"
tags: [vllm, executor, worker, model-runner, cuda-graph, torch-compile, 核心模块]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: arch-overview
    resource: /references/facts.md
    title: docs/design/arch_overview.md + v1/executor、v1/worker（本地检出）
  - id: anatomy-blog
    url: https://vllm.ai/blog/2025-09-05-anatomy-of-vllm
---

# 执行层：Executor、Worker 与 ModelRunner

调度器产出「这一步算什么」，执行层负责「真正把它算出来」。源码位置：`vllm/v1/executor/`、`vllm/v1/worker/gpu_worker.py`、`vllm/v1/worker/gpu_model_runner.py`（F-002）。

## Executor：单卡到多卡的透明扩展

`Executor`（`v1/executor/abstract.py`）是对引擎暴露的统一执行接口——「在**一个设备**或**多个设备**上执行模型」（F-054）：

| 实现 | 场景 | 机制 |
|------|------|------|
| `UniProcExecutor` | 单进程单 GPU | 直接调用 worker（F-054） |
| `ExecutorWithExternalLauncher` | 外部启动器（如 Ray actor）托管 | 单进程变体（F-054） |
| `MultiprocExecutor` | 单机多卡 TP/PP | 每 rank spawn 守护进程，共享内存消息队列 `rpc_broadcast_mq` / `worker_response_mq` 广播任务、回收结果（F-055） |
| Ray 系执行器 | 多机 / 弹性 EP | 经 Ray 管理 worker 生命周期（F-115） |

对引擎透明：`execute_model` 调用方式不变，单卡是直接调用、多卡是经消息队列间接调用（F-055）。

## Worker：一 GPU 一进程

vLLM 遵循「一个进程控制一个加速器设备」的惯例：TP=2 × PP=2 就是 4 个 worker（F-050）。worker 由 `rank`（全局编排）与 `local_rank`（设备分配、本地资源访问）标识（F-050）。`Worker`（`gpu_worker.py`）职责：

1. **Init device**：分配 CUDA device、检查 dtype（bf16 等）、按 `gpu_memory_utilization` 验证显存、设置分布式组（DP/TP/PP/EP）、实例化 `model_runner`（持有 sampler、KV cache、前向 buffer 如 `input_ids`/`positions`）与 CPU 侧 `InputBatch`（block table、sampling metadata）（F-053）；
2. **Load model**：实例化模型架构（统一构造签名）、加载权重（**初始化时即按 TP 切分**）、`model.eval()`、可选 `torch.compile()`（F-053、F-015）；
3. **Initialize KV cache**：取每层 KV spec、跑 profiling 前向 + 显存快照估算 block 数、分配并绑定 KV cache 张量、准备 attention metadata、对多个 warmup batch size **捕获 CUDA graph**（F-053）。

## ModelRunner：前向的中枢

`GPUModelRunner`（`gpu_model_runner.py`，约 7200 行，F-002）每个 engine step 做五件事（F-041）：

1. **Update states**：从 `input_batch` 移除已完成请求、更新元数据；
2. **Prepare inputs**：CPU→GPU 拷 buffer、算 positions、构建 `slot_mapping`（token → KV block 内偏移）、构造 attention metadata（按后端，如 FlashAttention/FlashInfer）；
3. **Forward pass**：执行模型前向——所有序列 flatten 成一条 super sequence（F-034）；自定义 paged attention 内核按块表读 KV；
4. **Gather last-token states**：取每序列最后位置 hidden states 算 logits（含 speculative 时的多位置）；
5. **Sample**：按 `SamplingParams` 采样（greedy、temperature、top-p、top-k、logprobs 等）。

## CUDA Graph：默认的执行模式

两种模式（F-052）：

- **Eager**：标准 PyTorch 前向，每步逐 kernel launch；
- **Captured（默认）**：初始化时对多个 warmup batch size 预捕获 CUDA graph，前向时 **replay** 预录图，消掉 kernel launch 开销、改善延迟。`--enforce-eager` 可关闭。

注意 V1 的 CUDA graph 捕获比 V0 占更多显存（F-019）；捕获尺寸可用 `--cudagraph-capture-sizes` / `--max-cudagraph-capture-size` 控制（F-013）。多模态有独立的图捕获路径（`docs/design/cuda_graphs_multimodal.md`，F-002）。

## torch.compile 与内核自动生成

`--compilation-config` 控制编译等级（`vllm/config/compilation.py`）：piecewise/full compile、编译缓存（避免重启重编译）、图级变换。官方文档另有 `docs/design/torch_compile.md` 专篇（F-002、F-056）。

## 排障入口

- 启动即 OOM：先降 `--gpu-memory-utilization` 或减小 CUDA graph 捕获尺寸（F-013、F-019）；
- 启动慢：确认 `vllm download-kernels` 已执行（F-120）；
- 编译期报错：`docs/design/debug_vllm_compile.md`（F-002）。

## 延伸阅读

- [03 架构总览](03-architecture.md)：执行层在进程模型中的位置
- [05 KV 缓存与 PagedAttention](05-kv-cache.md)：slot_mapping 寻址的块管理
- [12 分布式推理与扩展](12-distributed.md)：MultiprocExecutor 之上的 TP/PP 组网
