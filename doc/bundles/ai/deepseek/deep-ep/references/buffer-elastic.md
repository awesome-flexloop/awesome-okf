---
type: reference
scope: deep-ep
name: ElasticBuffer API
version: "2.1.0"
source: deep_ep/buffers/elastic.py, csrc/elastic/buffer.hpp
description: ElasticBuffer（V2 弹性通信缓冲区）完整 API 参考，包括构造、dispatch/combine、Engram、PP、AGRS 等方法
---

# ElasticBuffer API 参考

`ElasticBuffer` 是 DeepEP V2 的核心通信缓冲区类，基于 NCCL 对称内存实现，支持 MoE dispatch/combine、Engram 远程 KV 获取、流水线并行 send/recv、all-gather reduce-scatter 等通信模式。

## 构造函数

```python
ElasticBuffer(
    group: dist.ProcessGroup,
    num_bytes: Optional[int] = None,
    num_cpu_bytes: int = 0,
    num_max_tokens_per_rank: int = 0,
    hidden: int = 0,
    num_topk: int = 0,
    use_fp8_dispatch: bool = False,
    deterministic: bool = False,
    allow_hybrid_mode: bool = True,
    allow_multiple_reduction: bool = True,
    prefer_overlap_with_compute: bool = True,
    sl_idx: int = 3,
    num_allocated_qps: int = 0,
    num_cpu_timeout_secs: int = 300,
    num_gpu_timeout_secs: int = 100,
    explicitly_destroy: bool = False,
)
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `group` | `dist.ProcessGroup` | 必填 | PyTorch 分布式进程组 |
| `num_bytes` | `Optional[int]` | `None` | 缓冲区总字节数（GPU+CPU，2MB对齐）；为 None 时根据 MoE 参数自动计算 |
| `num_cpu_bytes` | `int` | `0` | CPU 缓冲区字节数（用于 Engram 存储，2MB对齐） |
| `num_max_tokens_per_rank` | `int` | `0` | 每 rank 最大 token 数（用于自动计算缓冲区大小） |
| `hidden` | `int` | `0` | Token 隐藏维度（用于自动计算缓冲区大小） |
| `num_topk` | `int` | `0` | Top-k 专家数（用于自动计算缓冲区大小） |
| `use_fp8_dispatch` | `bool` | `False` | 是否启用 FP8 dispatch（BF16 输入自动量化） |
| `deterministic` | `bool` | `False` | 是否使用确定性路由算法 |
| `allow_hybrid_mode` | `bool` | `True` | 是否启用混合模式（RDMA+NVLink 分层） |
| `allow_multiple_reduction` | `bool` | `True` | combine 是否允许多次规约（减少传输量但可能影响精度） |
| `prefer_overlap_with_compute` | `bool` | `True` | 是否优先与计算重叠（倾向使用更少 SM） |
| `sl_idx` | `int` | `3` | RDMA Service Level 索引（可被 `EP_OVERRIDE_RDMA_SL` 覆盖） |
| `num_allocated_qps` | `int` | `0` | RDMA QP 数量（0 为自动分配） |
| `num_cpu_timeout_secs` | `int` | `300` | CPU 侧超时秒数 |
| `num_gpu_timeout_secs` | `int` | `100` | GPU 侧超时秒数 |
| `explicitly_destroy` | `bool` | `False` | 是否需要显式调用 `destroy()` 释放资源 |

**注意事项：**
- `num_bytes=None` 时，必须提供 `num_max_tokens_per_rank`、`hidden`、`num_topk` 以自动计算大小
- `num_cpu_bytes > 0` 时 `num_bytes` 必须显式提供，构造函数会自动扩展 NCCL VA 空间
- 构造末尾执行 `cuda.synchronize() → barrier() → cuda.synchronize()` 确保初始化对所有 peer 可见

### destroy()

```python
buffer.destroy() -> None
```

显式销毁 C++ 运行时并释放资源。要求构造时设置 `explicitly_destroy=True`。

---

## 静态工具方法

### get_buffer_size_hint()

```python
@staticmethod
ElasticBuffer.get_buffer_size_hint(
    group: dist.ProcessGroup,
    num_max_tokens_per_rank: int,
    hidden: int,
    num_topk: int = 0,
    use_fp8_dispatch: bool = False,
    allow_hybrid_mode: bool = True,
    allow_multiple_reduction: bool = True,
) -> int
```

返回推荐的缓冲区大小（字节，2MB对齐），不构造缓冲区实例。

### get_engram_storage_size_hint()

```python
@staticmethod
ElasticBuffer.get_engram_storage_size_hint(
    num_entries: int,
    hidden: int,
    num_max_tokens_per_rank: int,
    dtype: torch.dtype = torch.bfloat16,
) -> Tuple[int, int]
```

返回 Engram 存储所需的 `(num_gpu_bytes, num_cpu_bytes)`，均2MB对齐。每个 entry 按 `hidden * dtype.itemsize` 对齐到32字节。

### get_pp_buffer_size_hint()

```python
@staticmethod
ElasticBuffer.get_pp_buffer_size_hint(
    num_max_tensor_bytes: int,
    num_max_inflight_tensors: int,
) -> int
```

返回 PP send/recv 所需缓冲区大小（2MB对齐）。计算公式：`align(num_max_tensor_bytes * num_max_inflight_tensors * 2 * 2, 2MB)`。

### get_agrs_num_max_session_bytes()

```python
@staticmethod
ElasticBuffer.get_agrs_num_max_session_bytes(
    group: dist.ProcessGroup,
    shapes: Union[Tuple[int,...], Sequence[Tuple[int,...]]],
    dtype: torch.dtype,
) -> int
```

计算单次 AGRS session 所需总字节数。每个 shape 按 `group.size() * prod(shape) * dtype.itemsize` 对齐到32字节后求和。

### get_agrs_buffer_size_hint()

```python
@staticmethod
ElasticBuffer.get_agrs_buffer_size_hint(
    group: dist.ProcessGroup,
    num_max_session_bytes: int,
) -> int
```

返回 AGRS 缓冲区推荐大小（2MB对齐）。

### capture()

```python
@staticmethod
ElasticBuffer.capture() -> EventHandle
```

在当前流上捕获 CUDA 事件。

---

## 核心通信方法

### barrier()

```python
buffer.barrier(
    use_comm_stream: bool = True,
    with_cpu_sync: bool = False,
    sequential: bool = True,
) -> None
```

执行 GPU 级 barrier。
- `use_comm_stream=True`：在通信流上执行
- `with_cpu_sync=True`：barrier 前后调用 `cudaDeviceSynchronize`
- `sequential=True`：scaleout 和 scaleup barrier 顺序执行

### get_comm_stream()

```python
buffer.get_comm_stream() -> torch.Stream
```

返回独立的通信流（高优先级 CUDA 流）。

### get_physical_domain_size()

```python
buffer.get_physical_domain_size() -> Tuple[int, int]
# 返回 (num_rdma_ranks, num_nvlink_ranks)
```

### get_logical_domain_size()

```python
buffer.get_logical_domain_size() -> Tuple[int, int]
# 返回 (num_scaleout_ranks, num_scaleup_ranks)
```

### get_theoretical_num_sms()

```python
@staticmethod
ElasticBuffer.get_theoretical_num_sms(
    num_experts: int,
    num_topk: int,
    num_scaleout_topk: int = 0,
    rdma_gbs: float = 0,
    nvlink_gbs: float = 0,
    sm_read_gbs: float = 200,
    sm_write_gbs: float = 50,
) -> int
```

基于带宽建模估算最优 SM 数量。返回值为偶数，至少为4，不超过设备 SM 数。结果通过 `weak_lru` 缓存。当 `prefer_overlap_with_compute=True` 时倾向使用更少 SM。

---

## Dispatch 方法

```python
buffer.dispatch(
    x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
    topk_idx: Optional[torch.Tensor] = None,
    topk_weights: Optional[torch.Tensor] = None,
    cumulative_local_expert_recv_stats: Optional[torch.Tensor] = None,
    num_experts: Optional[int] = None,
    num_max_tokens_per_rank: Optional[int] = None,
    expert_alignment: Optional[int] = None,
    num_sms: int = 0,
    num_qps: int = 0,
    previous_event: Optional[EventHandle] = None,
    previous_event_before_epilogue: Optional[EventHandle] = None,
    async_with_compute_stream: bool = False,
    allocate_on_comm_stream: bool = False,
    handle: Optional[EPHandle] = None,
    do_handle_copy: bool = True,
    do_cpu_sync: Optional[bool] = None,
    do_expand: bool = False,
    do_zero_padding: bool = False,
    use_tma_aligned_col_major_sf: bool = False,
) -> Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
          Optional[torch.Tensor], Optional[torch.Tensor],
          EPHandle, EventOverlap]
```

**返回值**：`(recv_x, recv_topk_idx, recv_topk_weights, handle, event)` 五元组。

**关键参数：**

| 参数 | 说明 |
|------|------|
| `x` | 输入 tensor（BF16，`[num_tokens, hidden]`）或 FP8 元组 `(fp8_data, scales)` |
| `topk_idx` | Top-k 专家索引，`[num_tokens, num_topk]`，类型 `deep_ep.topk_idx_t`，`-1` 表示无选择 |
| `topk_weights` | Top-k 权重，`[num_tokens, num_topk]`，类型 `torch.float` |
| `num_experts` | 专家总数；提供 `handle` 时可省略 |
| `num_sms` | 使用的 SM 数，0 为自动计算 |
| `num_qps` | 使用的 QP 数，0 为自动计算 |
| `handle` | 缓存模式：复用之前的 EPHandle 跳过布局重计算 |
| `previous_event` | 前序事件，等待其完成后再开始 dispatch |
| `do_expand` | 是否使用展开模式（每个 top-k 槽位独立展开） |
| `do_cpu_sync` | 是否 CPU 同步（无缓存 handle 时默认 True） |
| `expert_alignment` | 每个专家接收 token 数的对齐值，默认 1 |
| `async_with_compute_stream` | 是否异步与计算流重叠 |
| `use_tma_aligned_col_major_sf` | FP8 缩放因子是否使用 TMA 对齐的列优先布局 |

**缓存模式**：当 `handle` 提供时，`topk_idx` 必须为 `None`，复用 handle 中的路由信息，`do_cpu_sync` 自动设为 `False`。

---

## Combine 方法

```python
buffer.combine(
    x: torch.Tensor,
    handle: EPHandle,
    topk_weights: Optional[torch.Tensor] = None,
    bias: Optional[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]] = None,
    num_sms: int = 0,
    num_qps: int = 0,
    previous_event: Optional[EventHandle] = None,
    previous_event_before_epilogue: Optional[EventHandle] = None,
    async_with_compute_stream: bool = False,
    allocate_on_comm_stream: bool = False,
) -> Tuple[torch.Tensor, Optional[torch.Tensor], EventOverlap]
```

**返回值**：`(combined_x, combined_topk_weights, event)` 三元组。

**关键参数：**

| 参数 | 说明 |
|------|------|
| `x` | 专家输出，`[num_tokens, hidden]`，BF16 |
| `handle` | dispatch 返回的 EPHandle（必须） |
| `topk_weights` | Top-k 权重；非 expand 模式 `[num_tokens, num_topk]`，expand 模式一维 `[num_tokens]` |
| `bias` | 最终输出偏置，单 tensor 或 `(bias_0, bias_1)` 元组，`[num_combined_tokens, hidden]`，BF16 |
| `num_sms` | 使用的 SM 数，0 时复用 dispatch handle 中的值 |

---

## EPHandle 类

`EPHandle` 由 `dispatch()` 返回，封装路由元数据，被 `combine()` 消费。

### 关键属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `do_expand` | `bool` | 是否使用展开模式 |
| `num_experts` | `int` | 专家总数 |
| `expert_alignment` | `int` | 专家对齐值 |
| `num_max_tokens_per_rank` | `int` | 每 rank 最大 token 数 |
| `num_sms` | `int` | dispatch 使用的 SM 数 |
| `topk_idx` | `Tensor` | Top-k 索引 `[num_tokens, num_topk]` |
| `num_recv_tokens` | `int` | 接收 token 总数 |
| `num_expanded_tokens` | `int` | 展开后 token 总数 |
| `num_recv_tokens_per_expert_list` | `list` | 每个专家接收 token 数（CPU list） |
| `psum_num_recv_tokens_per_scaleup_rank` | `Tensor` | 每个 scaleup rank 去重接收 token 数的前缀和 |
| `psum_num_recv_tokens_per_expert` | `Tensor` | 每个本地专家对齐后接收 token 数的前缀和 |
| `num_unaligned_recv_tokens_per_expert` | `Tensor` | 每个专家未对齐的实际接收 token 数 |
| `recv_src_metadata` | `Tensor` | 源 token 索引和缓冲区槽位索引 |
| `dst_buffer_slot_idx` | `Tensor` | 目标缓冲区槽位索引 |
| `channel_linked_list` | `Optional[Tensor]` | 混合模式信道链表 |

### deterministic_sort()

```python
handle.deterministic_sort(
    do_cpu_sync: bool,
    is_cached_dispatch: bool,
    recv_x: torch.Tensor,
    recv_sf: Optional[torch.Tensor],
    recv_topk_idx: torch.Tensor,
    recv_topk_weights: torch.Tensor,
    channel_linked_list: Optional[torch.Tensor],
) -> None
```

对接收 token 排序以保证确定性输出。非 expand 模式排序 `recv_x`、`recv_sf`、`recv_topk_weights`、`recv_topk_idx`、`recv_src_metadata`；expand 模式仅排序 `recv_x`、`recv_sf`、`recv_topk_weights`，并更新槽位指针。

---

## Engram（远程 KV 缓存）

### engram_write()

```python
buffer.engram_write(
    storage: torch.Tensor,
    sf: Optional[torch.Tensor] = None,
) -> None
```

将 Engram 存储数据写入 CPU 段。写入前后各执行一次 barrier。
- `storage`：`[num_entries, hidden]`，BF16 或 FP8
- `sf`：`[num_total_entries, num_sf_packs]`，FP8 缩放因子（FP8 模式必需）

### engram_fetch()

```python
buffer.engram_fetch(
    indices: torch.Tensor,
    num_qps: int = 0,
    use_tma_aligned_col_major_sf: bool = False,
) -> Callable
```

通过 RDMA 从远程 rank 获取 Engram 条目，返回可调用对象（wait 函数）。调用 wait 函数时阻塞等待 RDMA 完成并返回 `(data, sf)`。
- `indices`：`[num_tokens, num_entries_per_token]`，`torch.int`
- 返回 `data`：`[num_tokens * num_entries_per_token, hidden]`

---

## 流水线并行（PP）

### pp_set_config()

```python
buffer.pp_set_config(
    num_max_tensor_bytes: int,
    num_max_inflight_tensors: int,
) -> None
```

配置 PP send/recv 参数，自动设置 `prev_rank_idx` 和 `next_rank_idx`（环形通信）。配置前执行 barrier 刷新之前操作。

### pp_send()

```python
buffer.pp_send(
    t: torch.Tensor,
    dst_rank_idx: int,
    num_sms: int = 0,
) -> None
```

向 PP 环中相邻 rank 发送张量。`dst_rank_idx` 必须是 `prev_rank_idx` 或 `next_rank_idx`。

### pp_recv()

```python
buffer.pp_recv(
    t: torch.Tensor,
    src_rank_idx: int,
    num_sms: int = 0,
) -> None
```

从 PP 环中相邻 rank 接收张量到 `t`。`src_rank_idx` 必须是 `prev_rank_idx` 或 `next_rank_idx`。

---

## All-Gather Reduce-Scatter（AGRS）

### create_agrs_session() / destroy_agrs_session()

```python
buffer.create_agrs_session() -> None
buffer.destroy_agrs_session() -> None
```

开始/结束 AGRS session。destroy 时等待计算流并向所有 peer 发信号。

### agrs_new_session()

```python
@contextmanager
buffer.agrs_new_session(enabled: bool = True)
```

上下文管理器，封装 create/destroy。`enabled=False` 时为空操作。

### agrs_set_config()

```python
buffer.agrs_set_config(
    num_max_session_bytes: int,
    num_max_all_gathers_per_session: int,
) -> None
```

配置 AGRS session 参数，包含 barrier 刷新。

### agrs_get_inplace_tensor()

```python
buffer.agrs_get_inplace_tensor(
    shapes: Union[Tuple[int,...], Sequence[Tuple[int,...]]],
    dtype: torch.dtype,
) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]
```

在 AGRS session 内从缓冲区获取本 rank 槽位的就地张量。返回单 Tensor 或 Tensor 元组（批处理模式）。

### all_gather()

```python
buffer.all_gather(
    t: Union[torch.Tensor, Sequence[torch.Tensor]],
) -> Union[Tuple[torch.Tensor, Callable], Tuple[torch.Tensor, ..., Callable]]
```

在 AGRS session 内执行 all-gather。
- 单张量输入：返回 `(gathered, handle)`，`gathered` 多一个前导维度 `num_ranks`
- 序列输入：返回 `(*gathered_tensors, handle)`
- `handle` 是等待数据到达的可调用对象

---

## 相关参考

- [公开 API 概览](/ai/deepseek/deep-ep/references/api)
- [Buffer (Legacy) API](/ai/deepseek/deep-ep/references/buffer-legacy)
- [事件系统](/ai/deepseek/deep-ep/references/events)
- [Dispatch/Combine 概念](/ai/deepseek/deep-ep/concepts/dispatch-combine)
- [Elastic vs Legacy 对比](/ai/deepseek/deep-ep/concepts/elastic-vs-legacy)
