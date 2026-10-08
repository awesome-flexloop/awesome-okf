---
type: reference
scope: deep-ep
name: Buffer (Legacy) API
version: "2.1.0"
source: deep_ep/buffers/legacy.py, csrc/legacy/
description: V1 遗留 Buffer 类 API 参考，包括三模式（intranode/internode/low-latency）dispatch/combine 及低延迟专用接口
---

# Buffer (Legacy) API 参考

`Buffer` 是 DeepEP V1 的通信缓冲区类，基于 NVSHMEM 构建，支持三种通信模式：节点内高吞吐（NVLink）、节点间高吞吐（RDMA+NVLink）、低延迟（IBGDA）。新代码推荐使用 ElasticBuffer。

## 构造函数

```python
Buffer(
    group: Optional[dist.ProcessGroup],
    num_nvl_bytes: int = 0,
    num_rdma_bytes: int = 0,
    low_latency_mode: bool = False,
    num_qps_per_rank: int = 24,
    allow_nvlink_for_low_latency_mode: bool = True,
    allow_mnnvl: bool = False,
    explicitly_destroy: bool = False,
    enable_shrink: bool = False,
    comm: Optional["mpi4py.MPI.Comm"] = None,
)
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `group` | `Optional[dist.ProcessGroup]` | 必填 | PyTorch 分布式进程组（与 `comm` 二选一） |
| `num_nvl_bytes` | `int` | `0` | NVLink 节点内通信缓冲区大小（字节） |
| `num_rdma_bytes` | `int` | `0` | RDMA 节点间通信缓冲区大小（字节） |
| `low_latency_mode` | `bool` | `False` | 是否启用低延迟模式（IBGDA） |
| `num_qps_per_rank` | `int` | `24` | 每 rank RDMA QP 数量；低延迟模式下须等于本地专家数 |
| `allow_nvlink_for_low_latency_mode` | `bool` | `True` | 低延迟模式是否允许 NVLink 流量 |
| `allow_mnnvl` | `bool` | `False` | 是否允许多节点 NVLink（MNNVL） |
| `explicitly_destroy` | `bool` | `False` | 是否需要显式调用 `destroy()` 释放资源 |
| `enable_shrink` | `bool` | `False` | 是否启用收缩模式（支持动态屏蔽 rank） |
| `comm` | `Optional[mpi4py.MPI.Comm]` | `None` | MPI 通信器（与 `group` 二选一） |

**初始化流程：**
1. 检查 NVLink 连接（`check_nvlink_connections`）
2. 创建 C++ 运行时（`_C.Buffer(...)`）
3. 同步 device IDs（all_gather_object）
4. 同步 IPC 句柄（all_gather_object）
5. 多 RDMA rank 或低延迟模式时：设置 NVSHMEM 环境变量，同步 NVSHMEM unique IDs
6. 调用 `runtime.sync(device_ids, ipc_handles, root_unique_id)` 完成初始化

**低延迟模式环境变量设置：**
- `NVSHMEM_DISABLE_P2P`：根据 `allow_nvlink_for_low_latency_mode` 设置
- `NVSHMEM_IB_ENABLE_IBGDA=1`：启用 IBGDA
- `NVSHMEM_IBGDA_NUM_RC_PER_PE=num_qps_per_rank`：每 peer RC 数量
- `NVSHMEM_QP_DEPTH`：QP 深度，默认 1024
- `NVSHMEM_MAX_TEAMS=7`：最大 team 数
- `NVSHMEM_DISABLE_NVLS=1`：禁用 NVLink SHARP
- `NVSHMEM_CUMEM_GRANULARITY=2^29`：CUDA 内存粒度（512MB）

### 类属性与方法

| 成员 | 类型 | 说明 |
|------|------|------|
| `num_sms` | `int`（类变量，默认20） | 高吞吐内核使用的 SM 数，必须为偶数 |
| `set_num_sms(new_num_sms)` | 静态方法 | 设置 SM 数（必须为偶数） |
| `is_sm90_compiled()` | 静态方法 | 返回是否编译了 SM90（FP8/TMA）特性 |
| `destroy()` | 实例方法 | 销毁 C++ 运行时（要求 `explicitly_destroy=True`） |

---

## 静态工具方法

### get_low_latency_rdma_size_hint()

```python
@staticmethod
Buffer.get_low_latency_rdma_size_hint(
    num_max_dispatch_tokens_per_rank: int,
    hidden: int,
    num_ranks: int,
    num_experts: int,
) -> int
```

返回低延迟 RDMA 缓冲区最小推荐大小（字节），按 BF16 计算。

### get_dispatch_config()

```python
@staticmethod
Buffer.get_dispatch_config(num_ranks: int) -> Config
```

返回推荐的 dispatch `Config`，支持 rank 数：2/4/8/16/24/32/48/64/96/128/144/160。

### get_combine_config()

```python
@staticmethod
Buffer.get_combine_config(num_ranks: int) -> Config
```

返回推荐的 combine `Config`，支持同样的 rank 数。

### capture()

```python
@staticmethod
Buffer.capture() -> EventOverlap
```

在当前流上捕获 CUDA 事件，返回 `EventOverlap` 包装器。

---

## 通信流与缓冲区访问

### get_comm_stream()

```python
buffer.get_comm_stream() -> torch.Stream
```

返回通信流。

### get_local_buffer_tensor()

```python
buffer.get_local_buffer_tensor(
    dtype: torch.dtype,
    size: Optional[int] = None,
    offset: int = 0,
    use_rdma_buffer: bool = False,
) -> torch.Tensor
```

获取原始缓冲区作为 PyTorch 张量（支持切片）。`use_rdma_buffer=True` 使用 RDMA 段，否则使用 NVLink 段。

---

## 高吞吐 Dispatch

### get_dispatch_layout()

```python
buffer.get_dispatch_layout(
    topk_idx: torch.Tensor,
    num_experts: int,
    previous_event: Optional[EventOverlap] = None,
    async_finish: bool = False,
    allocate_on_comm_stream: bool = False,
) -> Tuple[torch.Tensor, Optional[torch.Tensor], torch.Tensor, torch.Tensor, EventOverlap]
```

计算 dispatch 布局（不执行实际数据传输）。

**返回值**：`(num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, event)`

| 返回值 | 形状 | 类型 | 说明 |
|--------|------|------|------|
| `num_tokens_per_rank` | `[num_ranks]` | int | 每个 rank 接收的 token 数 |
| `num_tokens_per_rdma_rank` | `[num_rdma_ranks]` 或 None | int | 每个 RDMA rank 接收的 token 数（节点内为 None） |
| `num_tokens_per_expert` | `[num_experts]` | int | 每个专家接收的 token 数 |
| `is_token_in_rank` | `[num_tokens, num_ranks]` | bool | 每个 token 是否发送到对应 rank |
| `event` | - | EventOverlap | 事件句柄 |

### dispatch()

```python
buffer.dispatch(
    x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
    handle: Optional = None,
    num_tokens_per_rank: Optional[torch.Tensor] = None,
    num_tokens_per_rdma_rank: Optional[torch.Tensor] = None,
    is_token_in_rank: Optional[torch.Tensor] = None,
    num_tokens_per_expert: Optional[torch.Tensor] = None,
    topk_idx: Optional[torch.Tensor] = None,
    topk_weights: Optional[torch.Tensor] = None,
    expert_alignment: int = 1,
    num_worst_tokens: int = 0,
    config: Optional[Config] = None,
    previous_event: Optional[EventOverlap] = None,
    async_finish: bool = False,
    allocate_on_comm_stream: bool = False,
) -> Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
          Optional[torch.Tensor], Optional[torch.Tensor],
          List[int], Any, EventOverlap]
```

执行高吞吐 dispatch（all-to-all 发送 token 到专家所在 GPU）。

**返回值**：`(recv_x, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, handle, event)`

- 多 RDMA rank（节点间）时内部调用 `internode_dispatch`
- 纯 NVLink（节点内）时内部调用 `intranode_dispatch`
- 缓存模式（`handle` 非 None）：`topk_idx` 和 `topk_weights` 必须为 None

### combine()

```python
buffer.combine(
    x: torch.Tensor,
    handle: Any,
    topk_weights: Optional[torch.Tensor] = None,
    bias: Optional[torch.Tensor] = None,
    config: Optional[Config] = None,
    previous_event: Optional[EventOverlap] = None,
    async_finish: bool = False,
    allocate_on_comm_stream: bool = False,
) -> Tuple[torch.Tensor, Optional[torch.Tensor], EventOverlap]
```

执行高吞吐 combine（聚合专家输出回源 GPU）。

**返回值**：`(recv_x, recv_topk_weights, event)`

- 多 RDMA rank 时内部调用 `internode_combine`
- 纯 NVLink 时内部调用 `intranode_combine`

---

## 低延迟模式专用 API

### clean_low_latency_buffer()

```python
buffer.clean_low_latency_buffer(
    num_max_dispatch_tokens_per_rank: int,
    hidden: int,
    num_experts: int,
) -> None
```

清理低延迟缓冲区的零初始化部分。在正常 dispatch/combine 后执行低延迟内核前必须调用。

### low_latency_dispatch()

```python
buffer.low_latency_dispatch(
    x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
    topk_idx: torch.Tensor,
    num_max_dispatch_tokens_per_rank: int,
    num_experts: int,
    cumulative_local_expert_recv_stats: Optional[torch.Tensor] = None,
    dispatch_wait_recv_cost_stats: Optional[torch.Tensor] = None,
    use_fp8: bool = True,
    round_scale: bool = False,
    use_ue8m0: bool = False,
    async_finish: bool = False,
    return_recv_hook: bool = False,
) -> Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
          torch.Tensor, Any, EventOverlap, Optional[Callable]]
```

执行低延迟 dispatch。

**返回值**：`(recv_x, recv_count, handle, event, hook)`

| 返回值 | 说明 |
|--------|------|
| `recv_x` | FP8 模式：`(fp8_data, scales)` 元组；BF16 模式：单 tensor。形状 `[num_local_experts, num_max_dispatch_tokens_per_rank * num_ranks, hidden]` |
| `recv_count` | `[num_local_experts]`（int），每个专家实际接收 token 数 |
| `handle` | combine 所需的通信句柄 |
| `event` | EventOverlap 事件 |
| `hook` | `return_recv_hook=True` 时返回的接收等待钩子 |

### low_latency_combine()

```python
buffer.low_latency_combine(
    x: torch.Tensor,
    topk_idx: torch.Tensor,
    topk_weights: torch.Tensor,
    handle: Any,
    use_logfmt: bool = False,
    zero_copy: bool = False,
    async_finish: bool = False,
    return_recv_hook: bool = False,
    out: Optional[torch.Tensor] = None,
    combine_wait_recv_cost_stats: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, EventOverlap, Optional[Callable]]
```

执行低延迟 combine。

**返回值**：`(combined_x, event, hook)`

- `zero_copy=True` 时直接写入 RDMA 缓冲区，减少一次拷贝
- `out` 参数可提供预分配输出张量

### get_next_low_latency_combine_buffer()

```python
buffer.get_next_low_latency_combine_buffer(handle: Any) -> torch.Tensor
```

获取下一个低延迟 combine 的原始 RDMA 缓冲区张量（BF16），形状 `[num_local_experts, num_ranks * num_max_dispatch_tokens_per_rank, hidden]`，用于零拷贝优化。

### 低延迟 Rank 屏蔽

```python
buffer.low_latency_update_mask_buffer(rank_to_mask: int, mask: bool = False) -> None
buffer.low_latency_query_mask_buffer(mask_status: torch.Tensor) -> None
buffer.low_latency_clean_mask_buffer() -> None
```

动态屏蔽/取消屏蔽/查询/清理 rank 屏蔽状态。`mask=True` 屏蔽指定 rank，`mask_status` 形状 `[num_ranks]`（int，1 表示屏蔽）。

---

## 相关参考

- ElasticBuffer API — V2 推荐使用的弹性缓冲区
- Elastic vs Legacy 对比
- 低延迟模式
- 事件系统
