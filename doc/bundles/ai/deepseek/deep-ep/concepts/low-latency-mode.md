---
type: concept
scope: deep-ep
name: 低延迟模式
version: "2.1.0"
source: deep_ep/buffers/legacy.py, csrc/legacy/
description: V1 Buffer 的低延迟模式（Low-Latency Mode），基于 IBGDA 实现推理场景的超低延迟 dispatch/combine，包括零拷贝优化和 rank 屏蔽机制
---

# 低延迟模式

低延迟模式（Low-Latency Mode）是 V1 `Buffer` 专为 MoE 推理场景设计的通信模式，基于 NVIDIA IBGDA（InfiniBand GPU Direct Async）技术实现 GPU 直接发起 RDMA 通信，完全绕过 CPU 参与，最小化通信延迟。

## 为什么需要低延迟模式

训练场景的高吞吐模式和推理场景的低延迟模式有本质区别：

| 维度 | 高吞吐模式（训练） | 低延迟模式（推理） |
|------|-------------------|-------------------|
| **目标** | 最大化带宽利用率 | 最小化单次通信延迟 |
| **Batch size** | 大（数千 token） | 小（数十至数百 token） |
| **通信粒度** | 大块数据传输 | 小块数据频繁传输 |
| **内核设计** | 分块（chunked）传输，流水线化 | 预分配固定槽位，直接写入 |
| **CPU 参与** | 参与布局计算和同步 | 完全绕过（GPU-initiated RDMA） |
| **IBGDA** | 不使用 | 使用（GPU Direct Async） |

在自回归推理中，每步生成的 token 数很少（batch size 通常为 1-64），但需要快速完成 dispatch/combine 以生成下一个 token。此时高吞吐模式的分块流水线开销反而成为瓶颈，低延迟模式通过预分配固定大小的缓冲区槽位，让 GPU 直接通过 IBGDA 读写对端 GPU 内存，实现微秒级通信延迟。

## 启用低延迟模式

```python
from deep_ep import Buffer

buf = Buffer(
    group=group,
    num_nvl_bytes=0,                        # 低延迟模式使用 RDMA 缓冲区
    num_rdma_bytes=rdma_buffer_size,        # 通过 get_low_latency_rdma_size_hint 计算
    low_latency_mode=True,                  # 启用低延迟模式
    num_qps_per_rank=num_local_experts,     # QP 数必须等于本地专家数
    allow_nvlink_for_low_latency_mode=True, # 允许 NVLink 流量
)
```

### 缓冲区大小计算

使用静态方法计算 RDMA 缓冲区大小：

```python
rdma_size = Buffer.get_low_latency_rdma_size_hint(
    num_max_dispatch_tokens_per_rank=max_tokens,
    hidden=hidden_dim,
    num_ranks=world_size,
    num_experts=num_experts,
)
```

计算公式基于 BF16 数据类型，返回最小推荐大小。

### NVSHMEM 环境变量

低延迟模式初始化时自动设置以下 NVSHMEM 环境变量：

| 环境变量 | 值 | 说明 |
|----------|-----|------|
| `NVSHMEM_IB_ENABLE_IBGDA` | `1` | 启用 IBGDA（GPU Direct Async） |
| `NVSHMEM_IBGDA_NUM_RC_PER_PE` | `num_qps_per_rank` | 每 peer 的 RC QP 数量 |
| `NVSHMEM_QP_DEPTH` | `1024`（默认） | QP 深度，必须大于在途 WR 数以跳过 WQ 槽位检查 |
| `NVSHMEM_DISABLE_P2P` | `0`/`1` | 根据 `allow_nvlink_for_low_latency_mode` 设置 |
| `NVSHMEM_MAX_TEAMS` | `7` | 最大 team 数（减少 GPU 内存占用） |
| `NVSHMEM_DISABLE_NVLS` | `1` | 禁用 NVLink SHARP |
| `NVSHMEM_CUMEM_GRANULARITY` | `2^29`（512MB） | CUDA 内存分配粒度 |

## 低延迟 Dispatch

```python
recv_x, recv_count, handle, event, hook = buf.low_latency_dispatch(
    x,                          # 输入 token: [num_tokens, hidden] (BF16) 或 (fp8, scales) 元组
    topk_idx,                   # 专家索引: [num_tokens, num_topk]
    num_max_dispatch_tokens_per_rank=max_tokens,
    num_experts=num_experts,
    use_fp8=True,               # 是否使用 FP8（推荐）
    return_recv_hook=False,     # 是否返回接收等待钩子
    async_finish=False,         # 是否异步完成
)
```

### 接收张量布局

低延迟 dispatch 的接收张量具有特殊的预分配布局：

**FP8 模式**：返回 `(fp8_data, scales)` 元组
- `fp8_data`：`[num_local_experts, num_max_dispatch_tokens_per_rank * num_ranks, hidden]`
- `scales`：对应的缩放因子张量

**BF16 模式**：返回单张量
- `recv_x`：`[num_local_experts, num_max_dispatch_tokens_per_rank * num_ranks, hidden]`

关键区别于高吞吐模式：
- 接收张量是**预分配的固定大小**（`num_max_dispatch_tokens_per_rank * num_ranks` 槽位）
- 第一维是本地专家索引，每个专家有固定的槽位空间
- 每个 rank 的槽位从偏移 `rank * num_max_dispatch_tokens_per_rank` 开始
- 实际接收的 token 数由 `recv_count` 指示

### recv_count

`recv_count` 形状 `[num_local_experts]`（int32），表示每个本地专家实际接收的 token 数。这是访问有效数据的关键：

```python
for expert_idx in range(num_local_experts):
    n = recv_count[expert_idx].item()
    if n > 0:
        expert_tokens = recv_x[expert_idx, :n]  # 该专家实际接收的 token
        expert_output = experts[expert_idx](expert_tokens)
```

### 返回值说明

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `recv_x` | Tensor 或 (Tensor, Tensor) | 接收的 token 数据（固定大小槽位） |
| `recv_count` | Tensor `[num_local_experts]` | 每个专家实际接收 token 数 |
| `handle` | 不透明对象 | combine 所需的句柄 |
| `event` | EventOverlap | 事件句柄 |
| `hook` | Callable（可选） | 接收等待钩子（`return_recv_hook=True` 时） |

## 低延迟 Combine

```python
combined_x, event, hook = buf.low_latency_combine(
    x,                          # 专家输出: 与 recv_x 相同布局
    topk_idx,                   # Top-k 索引: [num_tokens, num_topk]
    topk_weights,               # Top-k 权重: [num_tokens, num_topk]
    handle,                     # dispatch 返回的句柄
    zero_copy=False,            # 是否零拷贝优化
    return_recv_hook=False,     # 是否返回接收钩子
    out=None,                   # 预分配输出张量（可选）
)
```

### 零拷贝优化（Zero-Copy）

`zero_copy=True` 时，combine 直接写入 RDMA 缓冲区中预分配的槽位，避免一次额外的数据拷贝：

```python
# 获取下一个 combine 的 RDMA 缓冲区指针
combine_buffer = buf.get_next_low_latency_combine_buffer(handle)
# 在专家计算时直接写入 combine_buffer
# 然后调用 zero-copy combine
combined_x, event, _ = buf.low_latency_combine(
    combine_buffer, topk_idx, topk_weights, handle, zero_copy=True
)
```

`get_next_low_latency_combine_buffer()` 返回 BF16 张量，形状 `[num_local_experts, num_ranks * num_max_dispatch_tokens_per_rank, hidden]`，指向 RDMA 缓冲区中用于 combine 的槽位。

### 缓冲区清理

在高吞吐量模式和低延迟模式之间切换时，需要清理低延迟缓冲区：

```python
buf.clean_low_latency_buffer(
    num_max_dispatch_tokens_per_rank=max_tokens,
    hidden=hidden_dim,
    num_experts=num_experts,
)
```

该函数将缓冲区的零初始化部分清零，必须在正常 dispatch/combine 之后、执行低延迟内核之前调用。

## Rank 屏蔽（Shrink 模式）

低延迟模式支持动态屏蔽和恢复 rank，适用于弹性推理场景（如某些 GPU 故障或降配）：

### 更新屏蔽状态

```python
buf.low_latency_update_mask_buffer(rank_to_mask=3, mask=True)   # 屏蔽 rank 3
buf.low_latency_update_mask_buffer(rank_to_mask=3, mask=False)  # 恢复 rank 3
```

- `mask=True`：屏蔽指定 rank，不再向其发送/接收数据
- `mask=False`：取消屏蔽

### 查询屏蔽状态

```python
mask_status = torch.empty(num_ranks, dtype=torch.int32, device='cuda')
buf.low_latency_query_mask_buffer(mask_status)
# mask_status[i] == 1 表示 rank i 被屏蔽
```

### 清理屏蔽

```python
buf.low_latency_clean_mask_buffer()  # 清除所有屏蔽
```

注意：rank 屏蔽需要在构造 Buffer 时设置 `enable_shrink=True`。

## 低延迟模式的性能注意事项

1. **固定槽位开销**：缓冲区按 `num_max_dispatch_tokens_per_rank * num_ranks` 预分配，`num_max_dispatch_tokens_per_rank` 设置过大会浪费显存，设置过小会导致 token 溢出
2. **IBGDA 要求**：需要支持 GPU Direct Async 的 NIC（如 ConnectX-7 或更新）和对应的驱动/Firmware
3. **NVLink 注意**：PCIe GPU 不应启用 `allow_nvlink_for_low_latency_mode`，可能因内存序问题导致错误；确保所有 GPU 间连接为 NVLink
4. **QP 数量**：`num_qps_per_rank` 必须等于本地专家数，这是因为每个专家使用独立 QP 发送数据
5. **FP8 推荐**：低延迟模式下推荐使用 FP8（`use_fp8=True`），减少带宽需求
6. **清理步骤**：不要忘记在高吞吐/低延迟切换时调用 `clean_low_latency_buffer()`

## 典型推理流程

```python
# 1. 初始化低延迟 Buffer
buf = Buffer(group, num_rdma_bytes=rdma_size, low_latency_mode=True,
             num_qps_per_rank=num_local_experts)

# 2. Prefill 阶段（可能使用高吞吐模式，或清理后用低延迟）
buf.clean_low_latency_buffer(max_tokens, hidden, num_experts)

# 3. Decode 循环（低延迟）
for step in range(max_gen_len):
    # Dispatch
    recv_x, recv_count, handle, event, _ = buf.low_latency_dispatch(
        hidden_states, topk_idx, max_tokens, num_experts, use_fp8=True)
    event.current_stream_wait()

    # 专家计算（按 recv_count 遍历有效 token）
    expert_output = torch.empty_like(recv_x)
    for i in range(num_local_experts):
        n = recv_count[i].item()
        if n > 0:
            expert_output[i, :n] = local_experts[i](recv_x[i, :n])

    # Combine（零拷贝优化）
    combined, event, _ = buf.low_latency_combine(
        expert_output, topk_idx, topk_weights, handle)
    event.current_stream_wait()

    hidden_states = combined
```

## 相关参考

- [Buffer (Legacy) API](/ai/deepseek/deep-ep/references/buffer-legacy#低延迟模式专用-api)
- [Dispatch/Combine 流程](dispatch-combine.md)
- [MoE 专家并行](moe-parallelism.md)
- [Elastic vs Legacy 对比](elastic-vs-legacy.md)
