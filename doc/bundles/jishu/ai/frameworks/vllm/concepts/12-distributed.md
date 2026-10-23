---
type: Concept
title: "分布式推理与扩展：TP/PP/DP/EP/CP"
description: "vLLM 并行体系——tensor/pipeline/data/expert/context 五维并行与 parallel_state 的 GroupCoordinator 组、单机多卡 uniproc/multiproc 执行器、Ray 执行器与多节点部署、--tensor-parallel-size 等参数与 EP 对 MoE 的意义"
tags: [vllm, distributed, tensor-parallel, pipeline-parallel, data-parallel, expert-parallel, context-parallel, ray, multi-node]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-parallel
    resource: /references/source-map.md
    title: vllm/distributed/parallel_state.py 与 vllm/v1/executor/（本地检出）
  - id: website-dist
    url: https://docs.vllm.ai/en/latest/serving/distributed_serving/
    title: Distributed Inference and Serving（官网文档）
---

# 分布式推理与扩展：TP/PP/DP/EP/CP

当模型或请求量超出单卡，vLLM 提供五个正交的并行维度。它们不是互斥选项，而是**可组合的切分方式**——理解组合规则比记住单个参数更重要。

## 五个并行维度

| 维度 | 参数 | 切分对象 | 典型场景 |
|------|------|---------|---------|
| Tensor Parallel | `--tensor-parallel-size` | 层内权重矩阵 | 最常用，单层放不下时 |
| Pipeline Parallel | `--pipeline-parallel-size` | 层间（按层分段） | 超大模型跨节点 |
| Data Parallel | `--data-parallel-size` | 请求（副本） | 提吞吐，每副本一份模型 |
| Expert Parallel | `--enable-expert-parallel` | MoE 专家 | MoE 模型专家分布到多卡 |
| Context Parallel | `--context-parallel-size`（CP 组） | 长序列上下文 | 超长上下文（100K+） |

源码侧由 `vllm/distributed/parallel_state.py` 统一管理：每种并行对应一个 `GroupCoordinator`（`get_tp_group`/`get_pp_group`/`get_dp_group`/`get_ep_group`/`get_pcp_group` 等），集合通信经 `all_reduce`/`all_gather`/`reduce_scatter` 原语下发（F-126）。ETP（expert tensor parallel）是 TP 在专家层的变体，由 `get_etp_group` 管理（F-127）。

**组合规则**：`world_size = TP × PP × DP`（EP 在 TP 维度内切分专家，不占额外卡）；V1 引擎为**每个 DP rank 起一个 EngineCore 进程**（见 [03 架构总览](03-architecture.md) 的进程模型，F-010）。

## 执行器（Executor）选型

并行落到执行层由 Executor 抽象（`vllm/v1/executor/abstract.py`）承接：

| 执行器 | 文件 | 场景 |
|--------|------|------|
| UniprocExecutor | `uniproc_executor.py` | 单进程，调试/单卡 |
| MultiprocExecutor | `multiproc_executor.py` | 单机多卡（默认路径） |
| RayExecutor | `ray_executor_v2.py` | 多机多卡，Ray 集群 |

Ray 路径支持弹性与异构放置（GPU 型号混合），代价是集群运维复杂度（F-128）。

## 多节点部署

```bash
# 节点 1（主节点）
vllm serve <model> --tensor-parallel-size 8 \
  --data-parallel-size 2 --data-parallel-size-local 1 \
  --data-parallel-address 10.0.0.1 --data-parallel-rpc-port 29500

# 节点 2（从节点，同参数加 headless）
vllm serve <model> --tensor-parallel-size 8 \
  --data-parallel-size 2 --data-parallel-size-local 1 --headless \
  --data-parallel-address 10.0.0.1 --data-parallel-rpc-port 29500 \
  --data-parallel-start-rank 1
```

要点（F-129）：

- **DP 主从**：`--data-parallel-address/rpc-port` 指定 DP coordinator 入口，`--data-parallel-start-rank` 区分主从；API Server 只在主节点。
- **PP 跨节点**：`--pipeline-parallel-size` 超过单机卡数时自动进入多节点，需保证各节点同构。
- **EP 与 MoE**：`--enable-expert-parallel` 常与 TP 组合（如 TP8+EP8），专家并行对 MoE 模型的显存分布收益最大（F-130）。
- **CP 与长上下文**：上下文并行按序列切分 attention 计算，配合 chunked prefill 处理超长 prompt（F-131）。

## 硬件插件与扩展

除 NVIDIA 外，分布式执行还可落到 Ascend（vllm-ascend）、TPU（vllm-tpu）、Gaudi（vllm-gaudi）、Spyre（vllm-spyre）等**仓库外插件**，各自实现平台 Executor 与 Worker（F-122）。详见 [02 安装与硬件平台](02-installation.md)。

## 选型速查

| 约束 | 首选 | 次选 |
|------|------|------|
| 单卡放不下单层 | TP | — |
| 模型太大（TP 超单机） | TP + PP | — |
| 要更高请求吞吐 | DP | TP（若显存富余） |
| MoE 专家显存爆炸 | TP + EP | — |
| 100K+ 长上下文 | CP | 增大 `max-model-len`+chunked prefill |

## 相关阅读

- [03 架构总览](03-architecture.md)：DP Coordinator 与多 EngineCore 进程模型
- [04 调度与批处理](04-scheduling.md)：DP 下调度器的数据并行行为
- [13 进阶主题](13-advanced.md)：PD 分离是「跨节点级并行」的下一站
