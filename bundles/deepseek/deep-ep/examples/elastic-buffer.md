---
type: example
scope: deep-ep
name: ElasticBuffer 配置与使用
version: "2.1.0"
source: deep_ep/buffers/elastic.py
description: ElasticBuffer 的各种配置方式、缓冲区大小计算、SM/QP 自动调优、混合模式控制，以及 Engram/PP/AGRS 等高级功能的使用示例
---

# ElasticBuffer 配置与使用示例

本示例展示 ElasticBuffer 的各种配置选项和高级功能，包括缓冲区大小计算、自动资源调优、FP8 通信、Engram 远程 KV 获取、PP 通信、AGRS 等。

## 1. 缓冲区大小计算

### 方式一：自动计算（推荐）

构造时传入 MoE 参数，ElasticBuffer 自动计算所需缓冲区大小：

```python
import torch
import torch.distributed as dist
import deep_ep

dist.init_process_group('nccl')
rank = dist.get_rank()
torch.cuda.set_device(rank)

buffer = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    # 不传 num_bytes，由以下 MoE 参数自动计算
    num_max_tokens_per_rank=2048,  # 每 rank 最大 token 数
    hidden=4096,                   # Hidden 维度
    num_topk=8,                    # Top-k 专家数
    use_fp8_dispatch=False,        # 是否 FP8 通信
    allow_hybrid_mode=True,        # 启用混合模式（自动 NVLink+RDMA）
)
print(f"Buffer size: {buffer.num_bytes / 1024**2:.1f} MB")
```

### 方式二：预计算推荐大小

使用静态方法 `get_buffer_size_hint()` 预计算，适用于需要先检查显存或自定义大小的场景：

```python
buffer_size = deep_ep.ElasticBuffer.get_buffer_size_hint(
    group=dist.group.WORLD,
    num_max_tokens_per_rank=2048,
    hidden=4096,
    num_topk=8,
    use_fp8_dispatch=False,
    allow_hybrid_mode=True,
    allow_multiple_reduction=True,
)
# 返回值已 2MB 对齐
buffer = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_bytes=buffer_size,
)
```

### 方式三：手动指定

直接传入 `num_bytes`（必须 2MB 对齐）：

```python
buffer = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_bytes=512 * 1024 * 1024,  # 512 MB
)
```

## 2. FP8 Dispatch 示例

使用 FP8 精度减少通信带宽：

```python
# 创建支持 FP8 的缓冲区
buffer = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_max_tokens_per_rank=2048,
    hidden=4096,
    num_topk=8,
    use_fp8_dispatch=True,  # FP8 模式
)

# BF16 输入
x = torch.randn(1024, 4096, device='cuda', dtype=torch.bfloat16)
topk_idx = torch.randint(0, 64, (1024, 8), device='cuda',
                          dtype=deep_ep.topk_idx_t)

# 方法 A：传入 BF16 数据，Buffer 内部自动量化为 FP8
recv_x, recv_topk_idx, recv_weights, handle, event = buffer.dispatch(
    x=x,
    topk_idx=topk_idx,
    num_experts=64,
)
# recv_x 是 (fp8_tensor, scales) 元组
# recv_x[0] 为 FP8 数据，recv_x[1] 为缩放因子

# 方法 B：手动量化后传入
from deep_ep.utils.math import per_token_cast_to_fp8, per_token_cast_back
x_fp8, x_scales = per_token_cast_to_fp8(x)
recv_x, _, _, handle, event = buffer.dispatch(
    x=(x_fp8, x_scales),  # FP8 元组
    topk_idx=topk_idx,
    num_experts=64,
)
# 反量化回 BF16 进行计算
recv_x_bf16 = per_token_cast_back(recv_x[0], recv_x[1])
```

## 3. 确定性路由

启用确定性模式保证相同输入产生相同输出顺序：

```python
buffer = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_max_tokens_per_rank=2048,
    hidden=4096,
    num_topk=8,
    deterministic=True,  # 启用确定性路由
)

# Dispatch 返回后自动注册排序回调
recv_x, _, _, handle, event = buffer.dispatch(
    x=x, topk_idx=topk_idx, num_experts=64,
)
# event.current_stream_wait() 时自动执行 deterministic_sort
with event:
    # recv_x 已按源 token 索引排序，顺序确定
    output = expert_model(recv_x)
```

## 4. 缓存 Dispatch（推理加速）

当路由模式固定时，复用 EPHandle 跳过布局重计算：

```python
# 首次 dispatch：计算布局
recv_x, _, _, handle, event = buffer.dispatch(
    x=x1, topk_idx=topk_idx1, num_experts=64,
)
with event:
    out1 = expert_model(recv_x)
combined1, _, ev1 = buffer.combine(out1, handle)
ev1.current_stream_wait()

# 后续 dispatch：复用 handle（topk_idx 必须为 None）
# 适用于推理中固定 batch size 的 decode 阶段
for _ in range(num_decode_steps):
    recv_x, _, _, handle2, event = buffer.dispatch(
        x=x_step,
        handle=handle,  # 复用之前的 handle
        num_experts=64,
    )
    with event:
        out = expert_model(recv_x)
    combined, _, ev = buffer.combine(out, handle2)
    ev.current_stream_wait()
```

注意：缓存模式下 token 数和路由模式必须与首次 dispatch 一致。

## 5. Expand 模式

Expand 模式为每个 top-k 槽位分配独立空间，便于逐专家独立处理：

```python
recv_x, _, recv_weights, handle, event = buffer.dispatch(
    x=x,
    topk_idx=topk_idx,
    num_experts=64,
    do_expand=True,  # 启用 expand 模式
    expert_alignment=128,
)
# recv_x 按专家分组，每组有 padding（expert_alignment 对齐）
# handle.num_unaligned_recv_tokens_per_expert 记录每个专家未对齐的实际 token 数
# handle.num_expanded_tokens 为展开后总 token 数

with event:
    # 专家计算（按专家分组处理）
    expert_outputs = []
    offset = 0
    for i in range(num_local_experts):
        # 计算该专家的实际 token 数
        aligned_start = offset
        n = handle.num_unaligned_recv_tokens_per_expert[i].item()
        if n > 0:
            expert_tokens = recv_x[aligned_start:aligned_start + n]
            expert_outputs.append(local_experts[i](expert_tokens))
        # 跳过对齐 padding
        psum = handle.psum_num_recv_tokens_per_expert[i].item()
        offset = psum  # 下一个专家的对齐偏移

    expert_output = torch.cat(expert_outputs, dim=0)

# Combine：expand 模式下 topk_weights 为一维
combined, _, ev = buffer.combine(
    expert_output, handle,
    topk_weights=recv_weights,  # 一维 [num_expanded_tokens]
)
```

## 6. SM/QP 资源配置

### 自动计算（推荐）

```python
# 默认自动计算最优 SM/QP 数量
recv_x, _, _, handle, event = buffer.dispatch(x, topk_idx=topk_idx, ...)
# num_sms=0, num_qps=0 表示自动计算
```

### 手动指定 SM 数

```python
# 指定 SM 数（必须为偶数，至少 4）
recv_x, _, _, handle, event = buffer.dispatch(
    x, topk_idx=topk_idx,
    num_sms=16,  # 使用 16 个 SM
    num_qps=8,   # 指定 QP 数
)
```

### 使用带宽模型估算

```python
# 静态方法：根据带宽建模估算最优 SM 数
num_sms = deep_ep.ElasticBuffer.get_theoretical_num_sms(
    num_experts=64,
    num_topk=8,
    rdma_gbs=50,       # RDMA 带宽 GB/s
    nvlink_gbs=450,    # NVLink 带宽 GB/s
    sm_read_gbs=200,
    sm_write_gbs=50,
)
print(f"Recommended SM count: {num_sms}")
```

### 控制计算-通信重叠权衡

```python
# 优先与计算重叠：使用更少 SM，留出 SM 给计算
buffer_overlap = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_max_tokens_per_rank=2048,
    hidden=4096,
    num_topk=8,
    prefer_overlap_with_compute=True,  # 默认 True
)

# 最大化通信带宽：使用更多 SM
buffer_bandwidth = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_max_tokens_per_rank=2048,
    hidden=4096,
    num_topk=8,
    prefer_overlap_with_compute=False,  # 最大化通信带宽
)
```

## 7. Engram 远程 KV 缓存

Engram 允许将 KV 缓存存储在 CPU 内存中，通过 RDMA 按需拉取：

```python
# 计算 Engram 所需缓冲区大小
num_kv_entries = 131072  # KV 缓存条目数
hidden = 512             # KV hidden 维度
num_max_fetch_tokens = 64
gpu_bytes, cpu_bytes = deep_ep.ElasticBuffer.get_engram_storage_size_hint(
    num_entries=num_kv_entries,
    hidden=hidden,
    num_max_tokens_per_rank=num_max_fetch_tokens,
    dtype=torch.bfloat16,
)

# 创建含 CPU 缓冲区的 ElasticBuffer
total_bytes = gpu_bytes + mOE_buffer_bytes  # GPU 缓冲区 + Engram GPU 接收区
buffer = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_bytes=total_bytes,
    num_cpu_bytes=cpu_bytes,  # CPU 缓冲区用于 Engram 存储
    allow_hybrid_mode=True,
)

# 写入 KV 缓存到 CPU 段
kv_storage = torch.randn(num_kv_entries, hidden, device='cuda',
                          dtype=torch.bfloat16)
buffer.engram_write(kv_storage)

# 通过 RDMA 获取远程 KV
fetch_indices = torch.randint(0, num_kv_entries, (32, 4), device='cuda',
                               dtype=torch.int32)  # 32 tokens, 4 entries each
wait_fn = buffer.engram_fetch(fetch_indices)
# wait_fn 是可调用对象，阻塞等待 RDMA 完成
fetched_data, fetched_sf = wait_fn()
# fetched_data: [32*4, hidden]
```

## 8. 流水线并行（PP）Send/Recv

与 [DualPipe](/deepseek/dual-pipe) 配合使用，实现 EP+PP 混合并行：

```python
# 计算 PP 缓冲区大小
max_tensor_bytes = 2 * 4096 * 2  # BF16: micro_bsz * hidden * 2 bytes
pp_buffer_size = deep_ep.ElasticBuffer.get_pp_buffer_size_hint(
    num_max_tensor_bytes=max_tensor_bytes,
    num_max_inflight_tensors=2,
)

# 创建含 PP 空间的 ElasticBuffer
buffer = deep_ep.ElasticBuffer(
    group=pp_group,
    num_bytes=ep_buffer_size + pp_buffer_size,
    # ... 其他 EP 参数
)

# 配置 PP
buffer.pp_set_config(
    num_max_tensor_bytes=max_tensor_bytes,
    num_max_inflight_tensors=2,
)

# PP Send/Recv
send_tensor = torch.randn(micro_bsz, hidden, device='cuda', dtype=torch.bfloat16)
recv_tensor = torch.empty_like(send_tensor)

# 发送给下一个 rank
buffer.pp_send(send_tensor, dst_rank_idx=buffer.next_rank_idx)
# 从上一个 rank 接收
buffer.pp_recv(recv_tensor, src_rank_idx=buffer.prev_rank_idx)
```

## 9. All-Gather Reduce-Scatter（AGRS）

用于序列并行等场景：

```python
# 计算 AGRS 缓冲区大小
session_bytes = deep_ep.ElasticBuffer.get_agrs_num_max_session_bytes(
    group=dist.group.WORLD,
    shapes=(4096, 4096),  # 本地张量形状
    dtype=torch.bfloat16,
)
agrs_size = deep_ep.ElasticBuffer.get_agrs_buffer_size_hint(
    group=dist.group.WORLD,
    num_max_session_bytes=session_bytes,
)

# 创建含 AGRS 空间的缓冲区后，使用上下文管理器
with buffer.agrs_new_session():
    buffer.agrs_set_config(
        num_max_session_bytes=session_bytes,
        num_max_all_gathers_per_session=4,
    )
    # 获取就地张量
    local_tensor = buffer.agrs_get_inplace_tensor(
        shapes=(4096, 4096), dtype=torch.bfloat16,
    )
    local_tensor.copy_(my_data)

    # All-gather
    gathered, wait_handle = buffer.all_gather(local_tensor)
    wait_handle()  # 等待数据到达
    # gathered 形状 [num_ranks, 4096, 4096]
```

## 10. 资源释放

```python
# 方式一：依赖析构函数自动释放（默认）
# del buffer 后 Python GC 触发析构

# 方式二：显式销毁（推荐，避免析构时挂起）
buffer = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_bytes=buffer_size,
    explicitly_destroy=True,  # 要求显式销毁
)
# ... 使用 buffer ...
buffer.destroy()  # 显式释放 C++ 资源
```

## 相关参考

- [ElasticBuffer API](/deepseek/deep-ep/references/buffer-elastic)
- [基础 MoE 示例](basic-moe.md)
- [计算-通信重叠示例](event-overlap.md)
- [架构概述](/deepseek/deep-ep/concepts/overview)
- [Dispatch/Combine 流程](/deepseek/deep-ep/concepts/dispatch-combine)
