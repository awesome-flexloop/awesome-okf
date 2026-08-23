---
type: concept
scope: deep-ep
name: DeepEP 架构概述
version: "2.1.0"
source: deep_ep/__init__.py, deep_ep/buffers/elastic.py, deep_ep/buffers/legacy.py
description: DeepEP 的定位、核心架构、两代缓冲区设计、通信拓扑抽象，以及在 DeepSeek 混合并行训练栈中的位置
---

# DeepEP 架构概述

DeepEP（DeepSeek Expert Parallelism）是 DeepSeek 开发的高性能 MoE（Mixture of Experts）专家并行通信库，专为大规模 MoE 模型训练和推理设计。它解决了 MoE 模型中 token 路由到专家、专家输出聚合回源这两个核心通信问题，并在此基础上扩展支持 Engram 远程 KV 缓存、流水线并行通信、All-Gather Reduce-Scatter 等多种通信模式。

## 核心解决的问题

MoE 模型的核心挑战在于**专家并行（Expert Parallelism, EP）**：每个 token 只激活少数几个专家（top-k），这些专家分布在不同 GPU 上。在前向传播中需要两次 all-to-all 通信：

1. **Dispatch（分发）**：将每个 token 发送到持有其 top-k 专家的 GPU
2. **Combine（聚合）**：将各专家的输出按权重聚合回 token 的源 GPU

传统 all-to-all 通信（如 NCCL 的 `all_to_all_single`）不适合 MoE 场景，因为：
- 每个 GPU 发送给不同对等端的数据量不均匀（负载不均衡）
- 需要同时支持节点内（NVLink）和节点间（RDMA）通信
- 通信延迟直接决定 MoE 层的端到端性能
- 需要与计算（GEMM）精细重叠以隐藏通信开销

DeepEP 就是为这些需求量身定制的通信库。

## 两代架构

DeepEP 包含两代缓冲区实现：

### V2 ElasticBuffer（推荐使用）

V2 `ElasticBuffer` 是当前推荐的实现，基于 NCCL 对称内存（Symmetric Memory）构建：

- **统一内存布局**：`[[[Workspace] GPU buffer] CPU buffer]` 三段式结构，GPU 和 CPU 内存在同一对称空间管理
- **混合模式（Hybrid Mode）**：自动在 scaleout（RDMA 跨节点）和 scaleup（NVLink 节点内）之间分层通信
- **自动资源调优**：基于带宽建模自动计算最优 SM/QP 数量
- **多通信模式统一**：一个 ElasticBuffer 同时支持 dispatch/combine、Engram、PP、AGRS
- **EPHandle 路由封装**：将路由元数据封装为可复用、可缓存的句柄
- **确定性路由**：支持 `deterministic=True` 保证可复现结果

### V1 Buffer（Legacy）

V1 `Buffer` 基于 NVSHMEM 构建，是早期实现：

- **三模式分离**：intranode（NVLink）、internode（RDMA+NVLink）、low-latency（IBGDA）三种模式各有独立内核
- **固定 SM 配置**：通过类变量 `Buffer.num_sms` 全局配置 SM 数量（默认 20）
- **独立缓冲区段**：NVLink 段和 RDMA 段分别分配管理
- **低延迟模式**：基于 IBGDA 的超低延迟推理路径

新代码应使用 ElasticBuffer。V1 保留用于兼容性和低延迟推理场景。

## 通信拓扑抽象

DeepEP V2 引入了物理域和逻辑域的双层抽象，以适应不同的硬件拓扑和通信策略：

### 物理域（Physical Domain）

物理域反映实际硬件互连拓扑：
- **num_rdma_ranks**：需要通过 RDMA 通信的 rank 组数（跨节点）
- **num_nvlink_ranks**：通过 NVLink 直连的 rank 数（节点内）

物理域由 NCCL 自动检测，反映 GPU 间的物理连接方式。

### 逻辑域（Logical Domain）

逻辑域是通信策略的分组抽象：
- **num_scaleout_ranks**：scaleout 维度（跨节点 RDMA 通信）
- **num_scaleup_ranks**：scaleup 维度（节点内 NVLink 通信）

每个 rank 在逻辑域中有二维坐标 `(scaleout_rank_idx, scaleup_rank_idx)`。当启用混合模式时，节点内通过 NVLink 高带宽通信，节点间通过 RDMA 通信，形成两层通信层次。

```
物理拓扑：
  Node 0: GPU0 ─NVLink─ GPU1 ─NVLink─ GPU2 ─NVLink─ GPU3
                    │                │
                   RDMA ────────── RDMA
                    │                │
  Node 1: GPU4 ─NVLink─ GPU5 ─NVLink─ GPU6 ─NVLink─ GPU7

逻辑域（混合模式）：
  scaleup_rank_idx: 0    1    2    3
  scaleout_rank_idx=0: GPU0 GPU1 GPU2 GPU3  (Node 0)
  scaleout_rank_idx=1: GPU4 GPU5 GPU6 GPU7  (Node 1)
```

## 关键设计特性

### 对称内存（Symmetric Memory）

ElasticBuffer 基于 NCCL 对称内存构建。对称内存是指所有 rank 上分配相同大小的内存区域，且每个 rank 可以通过地址偏移直接访问其他 rank 的对应内存位置。这是实现高性能 one-sided 通信（put/get）的基础。

- GPU 缓冲区对齐到 2MB（`kNumAlignmentBytes = 2097152`）
- 支持 CPU 对称内存（用于 Engram 存储）
- 通过 `get_sym_ptr(ptr, dst_rank_idx)` 获取对端 rank 的对称地址

### JIT 编译内核

DeepEP 的通信内核通过 JIT 编译系统在运行时生成最优代码。内核的模板参数（专家数、top-k、hidden 维度、SM/QP 数等）在编译时确定，实现循环展开和最优寄存器分配。详见 [JIT 编译系统概念](jit-compilation.md)。

### 独立通信流

ElasticBuffer 使用独立的高优先级 CUDA 通信流（从 CUDA 流池获取）。通信操作在通信流上执行，不阻塞计算流，通过 `EventOverlap` 事件机制实现精细的流同步和计算-通信重叠。

### SM/QP 资源管理

- **SM（Streaming Multiprocessor）**：通信内核占用的 SM 越多，带宽越高，但留给计算的越少。V2 通过带宽模型自动平衡。
- **QP（Queue Pair）**：RDMA 通信端点。混合模式需要更多 QP 实现多信道并行。V2 自动分配 17/65/129 个 QP。

## 在 DeepSeek 训练栈中的位置

DeepEP 是 DeepSeek 混合并行训练栈的通信基石：

```
┌─────────────────────────────────────────────────────────┐
│                    模型并行策略                           │
├──────────┬──────────┬──────────┬────────────────────────┤
│   TP     │   EP     │   PP     │  DP/FSDP/ZeRO          │
│ (张量并行) │ (专家并行) │ (流水线)  │ (数据并行)              │
├──────────┼──────────┼──────────┼────────────────────────┤
│ NCCL/    │ DeepEP   │ DeepEP   │ NCCL/                  │
│ DeepEP   │          │ (PP API) │ FSDP                   │
├──────────┴──────────┴──────────┴────────────────────────┤
│                    底层通信库                             │
│              NCCL / NVSHMEM / CUDA IPC                   │
└─────────────────────────────────────────────────────────┘
```

| DeepSeek 组件 | 与 DeepEP 的关系 |
|--------------|-----------------|
| [DeepGEMM](/ai/deepseek/deep-gemm) | MoE 分组 GEMM 内核，在 dispatch 之后执行专家计算，combine 之前完成 |
| [LPLB](/ai/deepseek/lplb) | 专家负载均衡器，输出 `topk_idx` 路由决策给 dispatch |
| [DualPipe](/ai/deepseek/dual-pipe) | 双向流水线并行，与 EP 组合使用，ElasticBuffer 提供 PP send/recv 原语 |

## 版本信息

- **当前版本**：2.1.0（`deep_ep.__version__`）
- **最低依赖**：CUDA（SM90/SM100）、NCCL、PyTorch
- **SM90 特性**：FP8 调度、TMA（Tensor Memory Accelerator）支持，通过 `Buffer.is_sm90_compiled()` 检测

## 后续阅读

- [Dispatch/Combine 流程](dispatch-combine.md) — 理解 token 路由和聚合的完整流程
- [MoE 专家并行](moe-parallelism.md) — 深入理解 EP 并行策略
- [Elastic vs Legacy 对比](elastic-vs-legacy.md) — 两代缓冲区的详细对比
- [低延迟模式](low-latency-mode.md) — 推理场景的超低延迟通信
- [JIT 编译系统](jit-compilation.md) — 运行时内核编译机制
