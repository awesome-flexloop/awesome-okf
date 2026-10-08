---
type: bundle
scope: deep-ep
name: DeepEP
version: "2.1.0"
okf_version: "0.2"
source: external/libs/ai/deepseek-ai/DeepEP/
description: DeepEP 是 DeepSeek 开发的高性能 MoE 专家并行通信库，支持 NVLink/RDMA 高吞吐 dispatch/combine、IBGDA 低延迟推理、Engram 远程 KV 缓存、PP send/recv、AGRS 等通信模式
tags:
  - expert-parallelism
  - moe
  - distributed-training
  - all-to-all
  - nvshmem
  - nccl
  - jit-compilation
  - low-latency
  - deepseek
prerequisites:
  - /pydata/pytorch/distributed/basics
  - /deepseek/deep-gemm
---

# DeepEP

DeepEP（DeepSeek Expert Parallelism）是 DeepSeek 开发的高性能专家并行通信库，专为大规模 MoE（Mixture of Experts）模型的训练和推理设计。它提供高效的 all-to-all 通信原语，解决 MoE 模型中 token 分发到专家（dispatch）和专家输出聚合回源（combine）这两个核心通信问题。

## 核心特性

- **V2 ElasticBuffer**：基于 NCCL 对称内存的统一通信缓冲区，自动混合 NVLink/RDMA 分层通信，支持自适应 SM/QP 资源调优
- **高吞吐 Dispatch/Combine**：JIT 编译的专用通信内核，支持 BF16/FP8 精度、确定性路由、缓存 dispatch、expand 模式
- **低延迟推理模式**：基于 IBGDA（GPU Direct Async）的超低延迟 dispatch/combine，支持零拷贝优化和动态 rank 屏蔽
- **Engram 远程 KV 缓存**：通过 RDMA 从远程 CPU 内存获取 KV 条目，支持 DeepSeek-V4/R1 条件内存
- **流水线并行支持**：内置 PP send/recv 原语，与 [DualPipe](../dual-pipe/index.md) 双向流水线无缝配合
- **All-Gather Reduce-Scatter**：支持 AGRS 集合通信原语，用于序列并行等场景
- **JIT 编译内核**：运行时根据模型参数和硬件拓扑生成最优 CUDA 内核，CRTP 启动器框架
- **计算-通信重叠**：独立通信流 + EventOverlap 事件系统，精细控制计算与通信的重叠

## 快速导航

### [核心概念](concepts/index.md)

| 概念 | 说明 |
|------|------|
| 架构概述 | DeepEP 定位、两代缓冲区设计、通信拓扑抽象、在 DeepSeek 训练栈中的位置 |
| Dispatch/Combine 流程 | Token 分发和聚合的数据流动模型、EPHandle 路由元数据、高级模式 |
| MoE 专家并行 | EP 并行策略基础、top-k 路由、EP 与 TP/PP/DP 组合、负载均衡 |
| Elastic vs Legacy | V2 ElasticBuffer 与 V1 Buffer 的架构差异、API 对比、迁移指南 |
| 低延迟模式 | V1 IBGDA 低延迟推理路径、零拷贝优化、rank 屏蔽机制 |
| JIT 编译系统 | 运行时 CUDA 内核编译原理、CRTP 启动器框架、内核缓存机制 |

### [API 参考](references/index.md)

| 参考文档 | 说明 |
|----------|------|
| 公开 API | 包导出一览、数据类型（Config/topk_idx_t）、初始化行为、工具函数 |
| ElasticBuffer API | V2 弹性缓冲区完整 API：构造、dispatch/combine、Engram、PP、AGRS |
| Buffer (Legacy) API | V1 遗留缓冲区 API：三模式 dispatch/combine、低延迟专用接口 |
| JIT 编译系统 | 编译器、内核缓存、CRTP 启动器框架、环境变量 |
| 事件系统 | EventOverlap/EventHandle：计算-通信重叠、流同步、钩子机制 |

### [示例](examples/index.md)

| 示例 | 说明 |
|------|------|
| 基础 MoE 通信 | ElasticBuffer 进行 dispatch → 专家计算 → combine 的完整流程 |
| ElasticBuffer 配置与使用 | 缓冲区大小计算、FP8、缓存 dispatch、Engram、PP、AGRS 等高级功能 |
| 计算-通信重叠 | EventOverlap 各种使用模式：with 语句、钩子、链式等待、异步模式 |

## 安装

```bash
cd external/libs/ai/deepseek-ai/DeepEP
pip install -e .
```

要求：
- CUDA 12.3+（SM90/SM100 架构）
- NCCL 2.19+
- PyTorch 2.1+
- NVSHMEM（V1 Buffer 低延迟模式需要）
- Python 3.8+

## 最小使用示例

```python
import torch
import torch.distributed as dist
import deep_ep

# 初始化分布式
dist.init_process_group('nccl')
rank = dist.get_rank()
torch.cuda.set_device(rank)

# 创建 ElasticBuffer（V2 推荐）
buffer = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_max_tokens_per_rank=2048,
    hidden=4096,
    num_topk=8,
)

# 准备输入和路由
x = torch.randn(1024, 4096, device='cuda', dtype=torch.bfloat16)
topk_idx = torch.randint(0, 64, (1024, 8), device='cuda',
                          dtype=deep_ep.topk_idx_t)

# Dispatch: 分发 token 到专家所在 GPU
recv_x, _, recv_weights, handle, event = buffer.dispatch(
    x, topk_idx=topk_idx, num_experts=64,
)

# 等待通信完成后执行专家计算
with event:
    expert_output = expert_model(recv_x)

# Combine: 聚合专家输出回源 GPU
combined, _, event = buffer.combine(
    expert_output, handle, topk_weights=recv_weights,
)
event.current_stream_wait()
```

## 与其他 DeepSeek 组件的关系

DeepEP 是 DeepSeek 混合并行训练栈的通信基石：

| 组件 | 与 DeepEP 的关系 |
|------|-----------------|
| [DeepGEMM](../deep-gemm/index.md) | MoE 分组 GEMM 内核，在 dispatch 之后执行专家计算，为 DeepEP 通信提供规整的输入输出形状 |
| [LPLB](../lplb/index.md) | 专家负载均衡器，生成 top-k 路由决策（`topk_idx`）给 DeepEP dispatch |
| [DualPipe](../dual-pipe/index.md) | 双向流水线并行，ElasticBuffer 的 PP send/recv API 为 DualPipe 提供流水线通信原语 |

典型的 DeepSeek-V3 混合并行配置：8-way EP（DeepEP）+ DualPipe PP + TP，DeepEP 同时承载 EP dispatch/combine 和 PP send/recv 通信。

## 架构概览

```
┌──────────────────────────────────────────────────────────────┐
│                    用户代码（MoE 层）                          │
├──────────────────────────────────────────────────────────────┤
│              EventOverlap（计算-通信重叠控制）                  │
├──────────────┬───────────────────────────────────────────────┤
│  V1 Buffer   │           V2 ElasticBuffer                     │
│  (NVSHMEM)   │      (NCCL Symmetric Memory)                  │
│              │                                               │
│ ┌──────────┐ │ ┌──────────┬──────────┬──────────┬─────────┐ │
│ │Intranode │ │ │Dispatch/ │ Engram   │ PP       │ AGRS    │ │
│ │Internode │ │ │Combine   │(Remote   │Send/Recv │         │ │
│ │Low-Latency│ │ │(JIT)     │KV Cache) │(JIT)     │(JIT)    │ │
│ └──────────┘ │ └──────────┴──────────┴──────────┴─────────┘ │
├──────────────┴───────────────────────────────────────────────┤
│          JIT Compilation System (NVCC Runtime)               │
├──────────────────────────────────────────────────────────────┤
│    NCCL Symmetric Memory / NVSHMEM / CUDA IPC               │
└──────────────────────────────────────────────────────────────┘
```

## 环境变量

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `EP_SUPPRESS_NCCL_CHECK` | `0` | 设为 1 跳过 NCCL 库一致性检查 |
| `EP_JIT_DEBUG` | `0` | 非零值打印 JIT 生成代码和启动配置 |
| `EP_REUSE_NCCL_COMM` | `1` | 复用 PyTorch NCCL 通信器 |
| `EP_NIC_NAME` | `mlx5_0` | RDMA NIC 设备名 |
| `EP_OVERRIDE_RDMA_SL` | 无 | 覆盖 RDMA Service Level |
| `EP_BUFFER_DEBUG` | `0` | 非零值打印缓冲区调试信息 |
| `EP_AVOID_RECORD_STREAM` | `0` | 使用 EventHandle 内部张量记录替代 record_stream |
| `EP_NUM_MAX_LOCAL_RANKS` | `16` | 最大本地 rank 数（CPU buffer VA 空间计算用） |

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
```
