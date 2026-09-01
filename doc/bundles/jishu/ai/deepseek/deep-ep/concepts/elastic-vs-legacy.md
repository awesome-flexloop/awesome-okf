---
type: concept
scope: deep-ep
name: ElasticBuffer vs Buffer (Legacy)
version: "2.1.0"
source: deep_ep/buffers/elastic.py, deep_ep/buffers/legacy.py
description: V2 ElasticBuffer 与 V1 Buffer 的架构差异、API 对比、性能特性对比，以及迁移指南
---

# ElasticBuffer vs Buffer (Legacy)

DeepEP 包含两代通信缓冲区实现：V2 `ElasticBuffer`（推荐）和 V1 `Buffer`（Legacy/遗留）。理解两者的差异有助于为具体场景选择正确的 API，并理解 DeepEP 的架构演进方向。

## 架构根本差异

| 维度 | V1 Buffer | V2 ElasticBuffer |
|------|-----------|-----------------|
| **底层通信库** | NVSHMEM | NCCL 对称内存 |
| **内存后端** | NVSHMEM 对称内存（仅 GPU） | NCCL Symmetric Memory（GPU + CPU） |
| **模式选择** | 用户手动选择三模式 | 自动混合模式（hybrid mode） |
| **缓冲区分段** | `num_nvl_bytes` + `num_rdma_bytes` 分别管理 | 统一 `num_bytes`（含 GPU + CPU） |
| **SM 配置** | 类变量全局配置（默认 20，必须偶数） | 基于带宽建模自动计算，支持按调用指定 |
| **路由句柄** | 隐式状态 / 不透明 handle | 结构化 `EPHandle`，可检查可缓存 |
| **初始化同步** | device IDs + IPC handles + NVSHMEM UIDs | NCCL comm + 对称内存映射 |
| **低延迟模式** | 原生 IBGDA 支持 | 暂未直接暴露（在 V1 中使用） |

## 为什么需要 ElasticBuffer

V1 Buffer 的三个核心痛点驱动了 V2 的重新设计：

### 1. NVSHMEM 与 NCCL 的生态冲突

V1 基于 NVSHMEM 构建，但 PyTorch 分布式训练生态以 NCCL 为核心。NVSHMEM 和 NCCL 共存时可能出现：
- NCCL 通信器与 NVSHMEM team 的资源竞争
- 重复的 NCCL 库加载问题（DeepEP 通过 `check_nccl_so()` 检测）
- GPU 内存中两份通信库的开销

V2 迁移到 NCCL 对称内存后，可以直接复用 PyTorch 已有的 NCCL 通信器（`EP_REUSE_NCCL_COMM=1`，默认开启），消除了多通信库共存的复杂度。

### 2. 三模式 API 分裂

V1 要求用户理解 intranode/internode/low-latency 三种模式，分别调用不同的内部函数（`intranode_dispatch`/`internode_dispatch`/`low_latency_dispatch`），且三种模式的缓冲区配置和内核行为差异很大。

V2 的混合模式自动处理节点内/节点间通信分层，用户只需调用统一的 `dispatch()`/`combine()` API，无需关心底层是 NVLink 还是 RDMA。

### 3. 固定资源配置 vs 自适应调优

V1 的 SM 数量通过 `Buffer.num_sms = 20` 全局固定，用户需要手动调优。这在不同模型大小、不同硬件配置下很难达到最优。

V2 的 `get_theoretical_num_sms()` 基于带宽建模自动计算：
- 输入参数：专家数、top-k、scaleout top-k、RDMA 带宽、NVLink 带宽、SM 读写带宽
- 输出：最优 SM 数（偶数，≥4，≤设备 SM 数）
- `prefer_overlap_with_compute=True` 时倾向使用更少 SM，将 SM 留给计算

## API 对比

### 构造函数对比

```python
# V1: 需要分别指定 NVLink 和 RDMA 缓冲区大小
buf_v1 = Buffer(
    group=group,
    num_nvl_bytes=nvl_bytes,     # NVLink 段大小
    num_rdma_bytes=rdma_bytes,   # RDMA 段大小
    low_latency_mode=False,      # 是否低延迟模式
    num_qps_per_rank=24,         # QP 数量
)

# V2: 统一缓冲区大小，或按 MoE 参数自动计算
buf_v2 = ElasticBuffer(
    group=group,
    num_bytes=total_bytes,       # 统一大小（含 CPU 段）
    num_cpu_bytes=0,             # CPU 段（Engram 用）
    # 或自动计算：
    # num_max_tokens_per_rank=..., hidden=..., num_topk=...
    allow_hybrid_mode=True,      # 自动分层通信
    prefer_overlap_with_compute=True,  # 自适应 SM
)
```

V2 提供静态方法计算推荐缓冲区大小，无需构造实例：
- `ElasticBuffer.get_buffer_size_hint()`：MoE dispatch/combine 缓冲区
- `ElasticBuffer.get_engram_storage_size_hint()`：Engram 存储
- `ElasticBuffer.get_pp_buffer_size_hint()`：PP send/recv
- `ElasticBuffer.get_agrs_buffer_size_hint()`：AGRS

### Dispatch 对比

```python
# V1: 两步操作（先计算布局，再执行 dispatch）
num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, event = \
    buf_v1.get_dispatch_layout(topk_idx, num_experts)
recv_x, recv_topk_idx, recv_topk_weights, num_recv_list, handle, event = \
    buf_v1.dispatch(x, num_tokens_per_rank=num_tokens_per_rank,
                    num_tokens_per_expert=num_tokens_per_expert,
                    topk_idx=topk_idx, topk_weights=topk_weights)

# V2: 一步操作（布局计算内嵌在 dispatch 中）
recv_x, recv_topk_idx, recv_topk_weights, handle, event = \
    buf_v2.dispatch(x, topk_idx=topk_idx, topk_weights=topk_weights,
                    num_experts=num_experts)
```

### Combine 对比

```python
# V1
combined_x, combined_weights, event = buf_v1.combine(
    expert_output, handle, topk_weights=topk_weights
)

# V2: 相同调用模式，但 handle 是结构化的 EPHandle
combined_x, combined_weights, event = buf_v2.combine(
    expert_output, handle, topk_weights=topk_weights
)
```

### 低延迟模式

V2 目前不直接暴露低延迟模式 API。对于需要超低延迟推理的场景（如 DeepSeek-V3/R1 的推理解码），仍需使用 V1 Buffer 的 `low_latency_dispatch`/`low_latency_combine`。详见 [低延迟模式](low-latency-mode.md)。

## 功能对比

| 功能 | V1 Buffer | V2 ElasticBuffer |
|------|:---------:|:----------------:|
| 节点内 NVLink dispatch/combine | ✅ | ✅ |
| 节点间 RDMA dispatch/combine | ✅ | ✅（混合模式自动） |
| 低延迟模式（IBGDA） | ✅ | ❌（使用 V1） |
| FP8 dispatch | ✅（SM90） | ✅ |
| 缓存 dispatch（handle 复用） | ✅ | ✅（EPHandle） |
| 确定性路由 | ❌ | ✅（`deterministic=True`） |
| Expand 模式 | ❌ | ✅（`do_expand=True`） |
| Engram 远程 KV 获取 | ❌ | ✅ |
| PP send/recv | ❌ | ✅ |
| All-Gather Reduce-Scatter | ❌ | ✅ |
| CPU 对称内存 | ❌ | ✅（Engram 用） |
| 自动 SM 计算 | ❌（手动设置） | ✅（带宽模型） |
| 自动 QP 计算 | ❌（手动设置） | ✅ |
| 多规约精度控制 | ❌ | ✅（`allow_multiple_reduction`） |
| 计算-通信重叠 | ✅（EventOverlap） | ✅（增强的 EventOverlap） |
| 静态缓冲区大小查询 | ✅（`get_*_size_hint`） | ✅（更丰富的 hint 方法） |
| Rank 屏蔽（shrink） | ✅ | ❌ |
| MPI 通信器支持 | ✅（`comm` 参数） | ❌ |

## 性能特性

| 特性 | V1 Buffer | V2 ElasticBuffer |
|------|-----------|-----------------|
| **带宽利用率** | 高 | 更高（混合模式 + 自适应 SM/QP） |
| **多平面网络** | 一般 | 更友好（`NCCL_GIN_CROSS_NIC` 支持） |
| **内存占用** | 双段（NVLink+RDMA） | 统一段（更紧凑） |
| **CPU 内存支持** | 无 | 支持（Engram） |
| **初始化开销** | NVSHMEM init 较重 | NCCL sym mem init 较快 |
| **可扩展性** | 到 160 ranks | 设计支持更大规模 |

## 迁移指南

### 从 V1 迁移到 V2

1. **替换构造**：将 `Buffer(group, num_nvl_bytes, num_rdma_bytes)` 替换为 `ElasticBuffer(group, num_max_tokens_per_rank=..., hidden=..., num_topk=...)`，使用自动大小计算或 `get_buffer_size_hint()` 预计算。

2. **简化 dispatch 调用**：不再需要先调用 `get_dispatch_layout()`，直接调用 `dispatch(x, topk_idx=..., num_experts=...)`。

3. **更新 handle 类型**：V2 的 handle 是 `EPHandle`，具有公开属性（`num_recv_tokens`、`num_recv_tokens_per_expert_list` 等），可以直接检查而不必依赖不透明对象。

4. **移除手动 SM 配置**：删除 `Buffer.set_num_sms()` 调用，V2 自动计算；如需控制使用 `prefer_overlap_with_compute` 参数。

5. **低延迟场景保留 V1**：推理使用低延迟模式时继续使用 V1 Buffer 的 `low_latency_dispatch`/`low_latency_combine`。

### 何时使用 V1

- **低延迟推理**：需要 IBGDA 内核的超低延迟场景
- **Rank 动态屏蔽**：需要 `enable_shrink` / `low_latency_update_mask_buffer` 的场景
- **MPI 环境**：使用 mpi4py 通信器而非 PyTorch ProcessGroup 的场景
- **已有代码兼容**：不需要 V2 新功能的稳定代码

### 何时必须使用 V2

- 需要 Engram（远程 KV 缓存）
- 需要 PP send/recv（与 [DualPipe](../../dual-pipe/index.md) 集成）
- 需要 AGRS（All-Gather Reduce-Scatter）
- 需要确定性路由（可复现训练）
- 需要 expand 模式
- 需要自动 SM/QP 调优
- 需要 CPU 对称内存

## 版本共存

V1 和 V2 可以在同一进程中导入和使用（通过 `from deep_ep import Buffer, ElasticBuffer`），但应避免在同一通信组上同时创建两种缓冲区，因为它们底层使用不同的通信库和内存区域，可能导致意外的资源冲突。

## 相关参考

- ElasticBuffer API
- Buffer (Legacy) API
- [低延迟模式](low-latency-mode.md)
- [架构概述](overview.md)
