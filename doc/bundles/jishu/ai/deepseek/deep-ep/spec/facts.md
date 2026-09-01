# DeepEP 源码事实提取

> R-Phase: 从源码中提取的客观事实，编号 F-001 起。每条事实仅记录代码中存在的内容，不做推断。

## 1. 模块入口与版本

- **F-001**: 包入口文件为 `deep_ep/__init__.py`，版本号为 `__version__ = '2.1.0'`。
- **F-002**: 模块导入时自动执行两个初始化函数：`check_nccl_so()` 和 `init_jit()`。
- **F-003**: `check_nccl_so()` 函数通过读取 `/proc/self/maps` 检查运行时加载的 NCCL 库是否与链接的 NCCL 库二进制一致，若发现重复或版本不匹配则 assert 失败。可通过环境变量 `EP_SUPPRESS_NCCL_CHECK=1` 跳过检查。
- **F-004**: `find_cuda_home()` 函数使用 `@functools.lru_cache()` 装饰，按顺序查找 `CUDA_HOME`、`CUDA_PATH` 环境变量，再通过 `which nvcc` 推断，最后回退到 `/usr/local/cuda`。
- **F-005**: `init_jit()` 调用 C 扩展 `_C.init_jit(library_root_path, find_cuda_home(), find_nccl_root())`，传入库根路径、CUDA 路径和 NCCL 路径。
- **F-006**: 包公开导出的 Python API 包括：`Buffer`（来自 `buffers.legacy`）、`ElasticBuffer`、`EPHandle`（来自 `buffers.elastic`）、`EventOverlap`、`EventHandle`（来自 `utils.event`）、`get_physical_domain_size`、`get_logical_domain_size`（来自 `utils.envs`）、`Config`、`topk_idx_t`（来自 C 扩展 `_C`）。

## 2. 顶层数据类型

- **F-007**: `topk_idx_t` 是从 C 扩展导出的 PyTorch dtype，默认使用 64 位整数（`EP_NUM_TOPK_IDX_BITS` 默认为 64，定义在 `deep_ep/include/deep_ep/common/compiled.cuh:55`），对应 Python 端的 `torch.int64`。
- **F-008**: `Config` 是从 C 扩展导出的配置结构体，定义在 `csrc/legacy/config.hpp:24-51`，包含五个整数字段：`num_sms`、`num_max_nvl_chunked_send_tokens`、`num_max_nvl_chunked_recv_tokens`、`num_max_rdma_chunked_send_tokens`、`num_max_rdma_chunked_recv_tokens`。
- **F-009**: `Config` 构造函数要求 `num_max_nvl_chunked_send_tokens < num_max_nvl_chunked_recv_tokens` 且 `num_max_rdma_chunked_send_tokens <= num_max_rdma_chunked_recv_tokens / 2`，构造时会将 `num_max_rdma_chunked_recv_tokens` 向上对齐到 `num_max_rdma_chunked_send_tokens` 的整数倍。

## 3. EPHandle 类（弹性通信句柄）

- **F-010**: `EPHandle` 类定义在 `deep_ep/buffers/elastic.py:25-193`，由 `ElasticBuffer.dispatch()` 返回，被 `ElasticBuffer.combine()` 消费以逆转化 token 路由。
- **F-011**: `EPHandle.__init__` 接收参数：`do_expand: bool`、`num_experts: int`、`expert_alignment: int`、`num_max_tokens_per_rank: int`、`num_sms: int`、`topk_idx: torch.Tensor`、`num_recv_tokens: int`、`num_expanded_tokens: int`、`num_recv_tokens_per_expert_list: list`、`psum_num_recv_tokens_per_scaleup_rank: torch.Tensor`、`psum_num_recv_tokens_per_expert: torch.Tensor`、`num_unaligned_recv_tokens_per_expert: torch.Tensor`、`recv_src_metadata: torch.Tensor`、`dst_buffer_slot_idx: torch.Tensor`、`token_metadata_at_forward: Optional[torch.Tensor]`、`channel_linked_list: Optional[torch.Tensor]`。
- **F-012**: `EPHandle` 实例属性包括：`do_expand`、`num_experts`、`expert_alignment`、`num_max_tokens_per_rank`、`num_sms`、`topk_idx`、`psum_num_recv_tokens_per_scaleup_rank`、`psum_num_recv_tokens_per_expert`、`num_unaligned_recv_tokens_per_expert`、`num_recv_tokens_per_expert_list`、`recv_src_metadata`、`dst_buffer_slot_idx`、`token_metadata_at_forward`、`channel_linked_list`、`num_recv_tokens`、`num_expanded_tokens`、`cached_recv_src_metadata_before_sort`（初始为 `None`）。
- **F-013**: `EPHandle.deterministic_sort(do_cpu_sync, is_cached_dispatch, recv_x, recv_sf, recv_topk_idx, recv_topk_weights, channel_linked_list)` 方法对接收的 token 进行排序以保证确定性 dispatch 输出。非 expand 模式排序 `recv_x`、`recv_sf`、`recv_topk_weights`、`recv_topk_idx`、`recv_src_metadata`；expand 模式仅排序 `recv_x`、`recv_sf`、`recv_topk_weights`，并更新 `recv_src_metadata[:, 2:]` 的槽位指针。

## 4. ElasticBuffer 类（V2 弹性通信缓冲区）

### 4.1 构造与销毁

- **F-014**: `ElasticBuffer` 类定义在 `deep_ep/buffers/elastic.py:195-1107`，支持高吞吐 EP all-to-all（dispatch/combine）、Engram（远程 KV 缓存获取）、流水线并行 send/recv（PP）、all-gather reduce-scatter（AGRS）。
- **F-015**: `ElasticBuffer.__init__` 参数包括：`group: dist.ProcessGroup`、`num_bytes: Optional[int]`、`num_cpu_bytes: int = 0`、`num_max_tokens_per_rank: int = 0`、`hidden: int = 0`、`num_topk: int = 0`、`use_fp8_dispatch: bool = False`、`deterministic: bool = False`、`allow_hybrid_mode: bool = True`、`allow_multiple_reduction: bool = True`、`prefer_overlap_with_compute: bool = True`、`sl_idx: int = 3`、`num_allocated_qps: int = 0`、`num_cpu_timeout_secs: int = 300`、`num_gpu_timeout_secs: int = 100`、`explicitly_destroy: bool = False`。
- **F-016**: 构造时若 `num_bytes` 为 `None`，通过 `_C.calculate_elastic_buffer_size()` 根据 MoE 参数自动计算缓冲区大小。
- **F-017**: 构造时调用 `check_nvlink_connections(group)` 检查 NVLink 连接。
- **F-018**: 构造时通过 `get_nccl_comm_handle(group, force_new_comm=num_cpu_bytes > 0)` 获取 NCCL 通信句柄。
- **F-019**: 当 `num_cpu_bytes > 0` 时，构造函数设置环境变量 `NCCL_WIN_STRIDE` 以扩展 NCCL VA 空间，并通过 `_C.create_cpu_handle(num_cpu_bytes)` 创建 CPU 句柄，再通过 `dist.all_gather_object` 在所有 rank 间交换。
- **F-020**: 构造函数末尾执行 `torch.cuda.synchronize()` → `group.barrier()` → `torch.cuda.synchronize()` 确保初始化对所有 peer 可见。
- **F-021**: `ElasticBuffer.destroy()` 方法要求 `explicitly_destroy=True`，调用 `self.runtime.destroy()` 释放 C++ 资源并将 `self.runtime` 和 `self.nccl_comm_handle` 置为 `None`。

### 4.2 静态工具方法

- **F-022**: `ElasticBuffer.get_buffer_size_hint(group, num_max_tokens_per_rank, hidden, num_topk=0, use_fp8_dispatch=False, allow_hybrid_mode=True, allow_multiple_reduction=True) -> int`：静态方法，返回推荐的缓冲区大小（字节，2MB 对齐），不构造缓冲区。
- **F-023**: `ElasticBuffer.get_engram_storage_size_hint(num_entries, hidden, num_max_tokens_per_rank, dtype=torch.bfloat16) -> Tuple[int, int]`：静态方法，返回 Engram 存储所需的 `(num_gpu_bytes, num_cpu_bytes)`，均 2MB 对齐。每个 entry 大小按 `hidden * dtype.itemsize` 对齐到 32 字节。
- **F-024**: `ElasticBuffer.get_pp_buffer_size_hint(num_max_tensor_bytes, num_max_inflight_tensors) -> int`：静态方法，返回 PP send/recv 所需缓冲区大小（2MB 对齐），计算公式为 `align(num_max_tensor_bytes * num_max_inflight_tensors * 2 * 2, 2MB)`。
- **F-025**: `ElasticBuffer.get_agrs_num_max_session_bytes(group, shapes, dtype) -> int`：静态方法，计算单次 AGRS session 所需总字节数，每个 shape 按 `group.size() * prod(shape) * dtype.itemsize` 对齐到 32 字节后求和。
- **F-026**: `ElasticBuffer.get_agrs_buffer_size_hint(group, num_max_session_bytes) -> int`：静态方法，返回 AGRS 缓冲区推荐大小（2MB 对齐）。

### 4.3 核心通信方法

- **F-027**: `ElasticBuffer.barrier(use_comm_stream=True, with_cpu_sync=False, sequential=True) -> None`：执行 GPU 级 barrier。`use_comm_stream` 控制是否使用通信流；`with_cpu_sync` 控制是否在 barrier 前后调用 `cudaDeviceSynchronize`；`sequential` 控制 scaleout 和 scaleup barrier 是否顺序执行。
- **F-028**: `ElasticBuffer.capture() -> EventHandle`：静态方法，在当前流上捕获 CUDA 事件。
- **F-029**: `ElasticBuffer.get_comm_stream() -> torch.Stream`：返回通信流。
- **F-030**: `ElasticBuffer.get_physical_domain_size() -> Tuple[int, int]`：返回 `(num_rdma_ranks, num_nvlink_ranks)`。
- **F-031**: `ElasticBuffer.get_logical_domain_size() -> Tuple[int, int]`：返回 `(num_scaleout_ranks, num_scaleup_ranks)`。

### 4.4 Dispatch 方法

- **F-032**: `ElasticBuffer.dispatch(x, topk_idx=None, topk_weights=None, cumulative_local_expert_recv_stats=None, num_experts=None, num_max_tokens_per_rank=None, expert_alignment=None, num_sms=0, num_qps=0, previous_event=None, previous_event_before_epilogue=None, async_with_compute_stream=False, allocate_on_comm_stream=False, handle=None, do_handle_copy=True, do_cpu_sync=None, do_expand=False, do_zero_padding=False, use_tma_aligned_col_major_sf=False)` 返回五元组：`(recv_x, recv_topk_idx, recv_topk_weights, handle: EPHandle, event: EventOverlap)`。
- **F-033**: dispatch 的输入 `x` 可以是 `torch.Tensor`（BF16，形状 `[num_tokens, hidden]`）或 `(torch.Tensor, torch.Tensor)` 元组（FP8 模式：第一个为 FP8 数据 `[num_tokens, hidden]`，第二个为缩放因子）。
- **F-034**: `topk_idx` 形状为 `[num_tokens, num_topk]`，类型为 `deep_ep.topk_idx_t`，值为专家索引，`-1` 表示无选择。当 `handle` 提供时 `topk_idx` 必须为 `None`。
- **F-035**: `topk_weights` 形状为 `[num_tokens, num_topk]`，类型为 `torch.float`。当 `handle` 提供时可选传入（用于反向传播缓存 expand）。
- **F-036**: `num_sms=0` 时自动通过 `get_theoretical_num_sms()` 计算；`num_qps=0` 时自动通过 `get_theoretical_num_qps(num_sms)` 计算。
- **F-037**: 当 `handle` 提供（缓存模式）时，`do_cpu_sync` 必须为 `False`（或 `None` 自动设为 `False`），且复用 handle 中的 `topk_idx`、`num_max_tokens_per_rank`、`num_experts`、`expert_alignment`。
- **F-038**: `expert_alignment` 默认为 1；`do_cpu_sync` 在无缓存 handle 时默认为 `True`。
- **F-039**: 当 `self.deterministic=True` 时，dispatch 返回前会注册或直接执行 `handle.deterministic_sort()` 进行确定性排序。
- **F-040**: 返回的 `recv_x` 与输入类型一致（Tensor 或 (Tensor, Tensor) 元组）；`recv_topk_weights` 在输入无 `topk_weights` 时为 `None`。

### 4.5 Combine 方法

- **F-041**: `ElasticBuffer.combine(x, handle: EPHandle, topk_weights=None, bias=None, num_sms=0, num_qps=0, previous_event=None, previous_event_before_epilogue=None, async_with_compute_stream=False, allocate_on_comm_stream=False)` 返回三元组：`(combined_x, combined_topk_weights, event: EventOverlap)`。
- **F-042**: combine 输入 `x` 形状为 `[num_tokens, hidden]`，类型为 `torch.bfloat16`。
- **F-043**: combine 的 `topk_weights` 在非 expand 模式下形状为 `[num_tokens, num_topk]`，在 expand 模式下为一维 `[num_tokens]`。
- **F-044**: combine 的 `bias` 参数可以是单个 `torch.Tensor` 或两个 Tensor 的元组 `(bias_0, bias_1)`，形状为 `[num_combined_tokens, hidden]`，类型为 BF16，作为最终输出的偏置。
- **F-045**: combine 的 `num_sms=0` 时复用 dispatch handle 中保存的 `handle.num_sms`。

### 4.6 SM/QP 估算方法

- **F-046**: `ElasticBuffer.get_theoretical_num_sms(num_experts, num_topk, num_scaleout_topk=0, rdma_gbs=0, nvlink_gbs=0, sm_read_gbs=200, sm_write_gbs=50) -> int`：基于带宽建模估算最优 SM 数量，使用 `@weak_lru(maxsize=None)` 缓存。返回值为偶数，至少为 4，不超过设备 SM 数；当 `prefer_overlap_with_compute=True` 时倾向使用更少 SM。
- **F-047**: `ElasticBuffer.get_theoretical_num_qps(num_sms) -> int`：基于 SM 数和模式估算 RDMA QP 数量。直接模式：`min(num_sms, 9)`；混合模式：`num_sms * 16 + 1`。最终不超过 `self.num_allocated_qps`。

### 4.7 Engram（远程 KV 缓存）

- **F-048**: `ElasticBuffer.engram_write(storage: torch.Tensor, sf: Optional[torch.Tensor] = None) -> None`：将 Engram 存储数据写入缓冲区 CPU 段。写入前后各执行一次 barrier 确保可见性。`storage` 形状 `[num_entries, hidden]`，类型为 BF16 或 FP8；`sf` 形状 `[num_total_entries, num_sf_packs]`（FP8 模式必需）。
- **F-049**: `ElasticBuffer.engram_fetch(indices: torch.Tensor, num_qps=0, use_tma_aligned_col_major_sf=False) -> Callable`：通过 RDMA 从远程 rank 获取 Engram 条目，返回一个可调用对象，调用时阻塞等待 RDMA 完成并返回 `(data: Tensor, sf: Optional[Tensor])`。`indices` 形状 `[num_tokens, num_entries_per_token]`，类型为 `torch.int`。返回的 `data` 形状 `[num_tokens * num_entries_per_token, hidden]`。

### 4.8 流水线并行（PP）

- **F-050**: `ElasticBuffer.pp_set_config(num_max_tensor_bytes: int, num_max_inflight_tensors: int)`：配置 PP send/recv 参数，包含 barrier 刷新之前操作。设置 `prev_rank_idx` 和 `next_rank_idx` 为环形通信中的前一个和后一个 rank。
- **F-051**: `ElasticBuffer.pp_send(t: torch.Tensor, dst_rank_idx: int, num_sms=0) -> None`：向 PP 环中相邻 rank 发送张量。`dst_rank_idx` 必须是 `prev_rank_idx` 或 `next_rank_idx`。
- **F-052**: `ElasticBuffer.pp_recv(t: torch.Tensor, src_rank_idx: int, num_sms=0) -> None`：从 PP 环中相邻 rank 接收张量到 `t`。`src_rank_idx` 必须是 `prev_rank_idx` 或 `next_rank_idx`。

### 4.9 All-Gather Reduce-Scatter（AGRS）

- **F-053**: `ElasticBuffer.create_agrs_session() -> None`：开始新的 AGRS session。
- **F-054**: `ElasticBuffer.destroy_agrs_session() -> None`：结束当前 AGRS session，等待计算流，向所有 peer 发信号。
- **F-055**: `ElasticBuffer.agrs_new_session(enabled=True)`：上下文管理器，封装 `create_agrs_session`/`destroy_agrs_session`；`enabled=False` 时为空操作。
- **F-056**: `ElasticBuffer.agrs_set_config(num_max_session_bytes: int, num_max_all_gathers_per_session: int) -> None`：配置 AGRS session 参数，包含 barrier 刷新。
- **F-057**: `ElasticBuffer.agrs_get_inplace_tensor(shapes, dtype)`：在 AGRS session 内从缓冲区获取本 rank 槽位的就地张量，返回单个 Tensor 或 Tensor 元组（批处理模式）。
- **F-058**: `ElasticBuffer.all_gather(t)`：在 AGRS session 内执行 all-gather。单张量输入返回 `(gathered, handle)`，`gathered` 多一个前导维度 `num_ranks`；序列输入返回 `(*gathered_tensors, handle)`。`handle` 是等待数据到达的可调用对象。

## 5. Buffer 类（V1 遗留缓冲区）

### 5.1 构造与配置

- **F-059**: `Buffer` 类定义在 `deep_ep/buffers/legacy.py:14-713`，支持高吞吐节点内 all-to-all（NVLink）、高吞吐节点间 all-to-all（RDMA+NVLink）、低延迟 all-to-all（RDMA/IBGDA）。
- **F-060**: `Buffer.__init__` 参数包括：`group: Optional[dist.ProcessGroup]`、`num_nvl_bytes: int = 0`、`num_rdma_bytes: int = 0`、`low_latency_mode: bool = False`、`num_qps_per_rank: int = 24`、`allow_nvlink_for_low_latency_mode: bool = True`、`allow_mnnvl: bool = False`、`explicitly_destroy: bool = False`、`enable_shrink: bool = False`、`comm: Optional[mpi4py.MPI.Comm] = None`。
- **F-061**: `Buffer.num_sms` 是类变量，默认值为 20，可通过 `Buffer.set_num_sms(new_num_sms)` 修改（要求偶数）。
- **F-062**: 构造时同步 device IDs（通过 `runtime.get_local_device_id()` + `all_gather_object`）、IPC 句柄（`runtime.get_local_ipc_handle()`）、NVSHMEM unique IDs（仅在多 RDMA rank 或低延迟模式时）。
- **F-063**: 低延迟模式初始化时设置环境变量：`NVSHMEM_DISABLE_P2P`、`NVSHMEM_IB_ENABLE_IBGDA=1`、`NVSHMEM_IBGDA_NUM_RC_PER_PE=num_qps_per_rank`、`NVSHMEM_QP_DEPTH`（默认 1024）、`NVSHMEM_MAX_TEAMS=7`、`NVSHMEM_DISABLE_NVLS=1`、`NVSHMEM_CUMEM_GRANULARITY=2^29`。
- **F-064**: `Buffer.destroy()` 要求 `explicitly_destroy=True`，调用 `self.runtime.destroy()`。
- **F-065**: `Buffer.is_sm90_compiled() -> bool`：静态方法，返回是否编译了 SM90（FP8/TMA）特性。
- **F-066**: `Buffer.get_low_latency_rdma_size_hint(num_max_dispatch_tokens_per_rank, hidden, num_ranks, num_experts) -> int`：静态方法，返回低延迟 RDMA 缓冲区最小推荐大小。
- **F-067**: `Buffer.get_dispatch_config(num_ranks: int) -> Config`：静态方法，返回推荐的 dispatch Config，支持 rank 数 2/4/8/16/24/32/48/64/96/128/144/160。
- **F-068**: `Buffer.get_combine_config(num_ranks: int) -> Config`：静态方法，返回推荐的 combine Config，支持同样的 rank 数。

### 5.2 核心通信方法

- **F-069**: `Buffer.get_comm_stream() -> torch.Stream`：返回通信流。
- **F-070**: `Buffer.get_local_buffer_tensor(dtype, size=None, offset=0, use_rdma_buffer=False) -> torch.Tensor`：获取原始缓冲区（支持切片）作为 PyTorch 张量。
- **F-071**: `Buffer.capture() -> EventOverlap`：静态方法，在当前流上捕获 CUDA 事件。

### 5.3 Dispatch 布局与执行

- **F-072**: `Buffer.get_dispatch_layout(topk_idx, num_experts, previous_event=None, async_finish=False, allocate_on_comm_stream=False)` 返回五元组：`(num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, event)`。
- **F-073**: `get_dispatch_layout` 的 `num_tokens_per_rank` 形状 `[num_ranks]`（int），`num_tokens_per_rdma_rank` 形状 `[num_rdma_ranks]`（int，节点内为 None），`num_tokens_per_expert` 形状 `[num_experts]`（int），`is_token_in_rank` 形状 `[num_tokens, num_ranks]`（bool）。
- **F-074**: `Buffer.dispatch(x, handle=None, num_tokens_per_rank=None, num_tokens_per_rdma_rank=None, is_token_in_rank=None, num_tokens_per_expert=None, topk_idx=None, topk_weights=None, expert_alignment=1, num_worst_tokens=0, config=None, previous_event=None, async_finish=False, allocate_on_comm_stream=False)` 返回六元组：`(recv_x, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, handle, event)`。
- **F-075**: 当存在多个 RDMA rank（节点间）时，`dispatch` 内部调用 `internode_dispatch`；否则调用 `intranode_dispatch`。
- **F-076**: dispatch 的缓存模式（`handle` 非 None）要求 `topk_idx` 和 `topk_weights` 均为 None。
- **F-077**: `Buffer.combine(x, handle, topk_weights=None, bias=None, config=None, previous_event=None, async_finish=False, allocate_on_comm_stream=False)` 返回三元组：`(recv_x, recv_topk_weights, event)`。
- **F-078**: 当存在多个 RDMA rank 时，`combine` 内部调用 `internode_combine`；否则调用 `intranode_combine`。

### 5.4 低延迟模式

- **F-079**: `Buffer.clean_low_latency_buffer(num_max_dispatch_tokens_per_rank, hidden, num_experts) -> None`：清理低延迟缓冲区的零初始化部分。在正常 dispatch/combine 后执行低延迟内核前必须调用。
- **F-080**: `Buffer.low_latency_dispatch(x, topk_idx, num_max_dispatch_tokens_per_rank, num_experts, cumulative_local_expert_recv_stats=None, dispatch_wait_recv_cost_stats=None, use_fp8=True, round_scale=False, use_ue8m0=False, async_finish=False, return_recv_hook=False)` 返回五元组：`(recv_x, recv_count, handle, event, hook)`。
- **F-081**: 低延迟 dispatch 的 `recv_x` 在 FP8 模式下为 `(Tensor, Tensor)` 元组，形状 `[num_local_experts, num_max_dispatch_tokens_per_rank * num_ranks, hidden]`（FP8 数据）和对应的缩放因子；BF16 模式下单张量形状 `[num_local_experts, num_max_dispatch_tokens_per_rank * num_ranks, hidden]`。
- **F-082**: 低延迟 dispatch 的 `recv_count` 形状 `[num_local_experts]`（int），表示每个专家接收的 token 数。
- **F-083**: `Buffer.low_latency_combine(x, topk_idx, topk_weights, handle, use_logfmt=False, zero_copy=False, async_finish=False, return_recv_hook=False, out=None, combine_wait_recv_cost_stats=None)` 返回三元组：`(combined_x, event, hook)`。
- **F-084**: `Buffer.low_latency_update_mask_buffer(rank_to_mask: int, mask: bool = False)`：屏蔽/取消屏蔽某个 rank（mask=True 屏蔽，False 取消）。
- **F-085**: `Buffer.low_latency_query_mask_buffer(mask_status: torch.Tensor)`：查询所有 rank 的屏蔽状态，`mask_status` 形状 `[num_ranks]`（int），1 表示屏蔽。
- **F-086**: `Buffer.low_latency_clean_mask_buffer()`：清理屏蔽缓冲区。
- **F-087**: `Buffer.get_next_low_latency_combine_buffer(handle) -> torch.Tensor`：获取下一个低延迟 combine 的原始 RDMA 缓冲区张量（BF16），形状 `[num_local_experts, num_ranks * num_max_dispatch_tokens_per_rank, hidden]`，用于零拷贝优化。

## 6. 事件系统

- **F-088**: `EventHandle` 类从 C 扩展 `_C` 导入，封装 CUDA 事件句柄。
- **F-089**: `EventOverlap` 类定义在 `deep_ep/utils/event.py:8-96`，包装 CUDA 事件以支持计算通信重叠。
- **F-090**: `EventOverlap.__init__(event=None, extra_tensors=None)`：接收可选的 `EventHandle` 和额外张量元组。
- **F-091**: `EventOverlap.current_stream_wait(release_handle=False)`：让当前流 `torch.cuda.current_stream()` 等待事件完成；若注册了 `hook_after_wait` 回调则在等待后执行；`release_handle=True` 时等待后释放事件引用。
- **F-092**: `EventOverlap.register_hook_after_wait(hook_after_wait: Callable)`：注册在 `current_stream_wait()` 后执行的回调，同一实例只能注册一个。
- **F-093**: `EventOverlap` 支持 Python `with` 语法（上下文管理器），进入时返回 `self`，退出时自动调用 `current_stream_wait()`。
- **F-094**: `EventOverlap.__call__(release_handle=False) -> EventOverlap`：配置上下文管理器的 `release_handle` 行为，返回 `self`。

## 7. NCCL 通信管理

- **F-095**: `NCCLCommHandle` 类定义在 `deep_ep/utils/comm.py:11-37`，包装原始 NCCL 通信器，管理生命周期。
- **F-096**: `NCCLCommHandle.__init__(nccl_comm: int, managed: bool)`：`nccl_comm` 为原始 NCCL 通信器整数指针；`managed=True` 表示由 DeepEP 创建，析构时需调用 `_C.destroy_nccl_comm` 销毁。
- **F-097**: `NCCLCommHandle.get() -> int`：返回原始 NCCL 通信器。
- **F-098**: `get_nccl_comm_handle(group: dist.ProcessGroup, force_new_comm: bool = False) -> NCCLCommHandle`：获取或创建 NCCL 通信器句柄，结果缓存。优先复用 PyTorch 后端的 `_comm_ptr`（受环境变量 `EP_REUSE_NCCL_COMM` 控制，默认 1）；`force_new_comm=True` 时总是创建新的 DeepEP 管理的通信器。
- **F-099**: `destroy_all_managed_nccl_comm() -> None`：销毁所有缓存的 NCCL 通信器句柄并清空缓存。

## 8. 环境与配置工具

- **F-100**: `deep_ep/utils/envs.py` 定义了以下模块级函数：
- **F-101**: `init_seed(global_seed: int) -> None`：初始化随机种子，local_seed = global_seed + rank。
- **F-102**: `get_local_seed() -> int` / `get_global_seed() -> int`：返回本地/全局随机种子。
- **F-103**: `dist_print(s='', once_in_node=False) -> None`：从所有 rank（或每节点 rank 0）打印消息，后跟 barrier。
- **F-104**: `init_dist(local_rank, num_local_ranks, seed=0) -> Tuple[int, int, dist.ProcessGroup]`：初始化 NCCL 分布式环境，设置 BF16 默认 dtype 和 CUDA 设备，返回 `(rank, world_size, group)`。
- **F-105**: `get_physical_domain_size(group: ProcessGroup) -> Tuple[int, int]`：返回 `(num_rdma_ranks, num_nvlink_ranks)`。
- **F-106**: `get_logical_domain_size(group: ProcessGroup, allow_hybrid_mode=True) -> Tuple[int, int]`：返回 `(num_scaleout_ranks, num_scaleup_ranks)`。
- **F-107**: `check_nvlink_connections(group: ProcessGroup) -> None`：检查 GPU 间 NVLink 连接。PCIe GPU 只支持 EP2（rank 数 ≤ 2），使用 pynvml 检查 P2P NVLink 状态。
- **F-108**: `check_torch_deterministic() -> None`：断言不同时启用 `torch.are_deterministic_algorithms_enabled()` 和 `torch.utils.deterministic.fill_uninitialized_memory`，否则 `torch.empty()` 的初始化内核可能与通信流重叠导致错误。
- **F-109**: `get_nvlink_gbs(factor=0.9) -> float`：通过 `nvidia-smi nvlink -s` 获取总 NVLink 带宽（GB/s），使用 `@functools.lru_cache()` 缓存，返回值乘以效率因子。
- **F-110**: `check_fast_rdma_atomic_support(nic_name='mlx5_0') -> bool`：通过 `ibstat` 检查 NIC 是否支持快速 RDMA 原子操作（MT4131 或更新），可通过环境变量 `EP_NIC_NAME` 配置 NIC 名。
- **F-111**: `get_rdma_gbs(nic_name='mlx5_0') -> float`：通过 `ibstat` 获取 RDMA 带宽（GB/s），缓存。

## 9. 数学与语义工具

- **F-112**: `deep_ep/utils/math.py` 定义：`calc_diff(x, y) -> float`（余弦相似度差异）、`safe_div(a, b) -> float`（安全除法，0/0=0）、`ceil_div(x, y) -> int`、`align(x, y) -> int`（向上对齐）。
- **F-113**: `per_token_cast_to_fp8(x: Tensor) -> Tuple[Tensor, Tensor]`：使用 `@torch.compile(dynamic=True)` 编译，将 2D 张量按 token 逐行量化为 FP8，返回 `(fp8_tensor, scales)`，hidden 维度对齐到 128。
- **F-114**: `per_token_cast_back(x_fp8: Tensor, x_scales: Tensor) -> Tensor`：使用 `@torch.compile(dynamic=True)` 编译，将 FP8 张量反量化回 BF16。
- **F-115**: `inplace_unique(x: Tensor, num_slots: int) -> None`：原地计算 2D 张量每行的唯一值（去重并按频次降序排列）。
- **F-116**: `deep_ep/utils/semantic.py` 定义 `value_or(value, default)`（None 时返回 default）和 `weak_lru(maxsize=128, typed=False)` 装饰器（使用弱引用的 LRU 缓存，避免类方法内存泄漏）。

## 10. JIT 编译系统

- **F-117**: JIT 系统位于 `csrc/jit/` 命名空间 `deep_ep::jit`。
- **F-118**: `init(library_root_path, cuda_home_path, nccl_root_path)` 函数（`csrc/jit/api.hpp:9-14`）依次调用 `Compiler::prepare_init`、`KernelRuntime::prepare_init`、`IncludeParser::prepare_init`。
- **F-119**: `DeviceRuntime` 类（`csrc/jit/device_runtime.hpp:9-63`）提供设备属性查询：`get_clock_rate()` 返回 GPU 时钟频率（Hz，从 kHz 转换）、`get_num_smem_bytes()` 返回每 block 最大动态共享内存字节数、`get_num_sms()` 返回 SM 数量、`get_arch()` 返回架构字符串（如 `"90a"`、`"100a"`）。
- **F-120**: 全局静态变量 `device_runtime`（`csrc/jit/device_runtime.hpp:65`）使用 `LazyInit<DeviceRuntime>` 懒初始化。
- **F-121**: `Compiler`/`NVCCCompiler` 类（`csrc/jit/compiler.hpp`）负责 JIT 编译 CUDA 内核，支持缓存；通过 `compiler->build(kernel_name, code)` 编译并返回 `shared_ptr<KernelRuntime>`。
- **F-122**: `KernelRuntimeCache` 类（`csrc/jit/cache.hpp:11-32`）使用 `unordered_map<string, shared_ptr<KernelRuntime>>` 缓存已编译内核，通过目录路径查找。全局静态变量 `kernel_runtime_cache` 持有缓存实例。
- **F-123**: `KernelRuntime` 类（`csrc/jit/kernel_runtime.hpp:13-83`）从编译输出目录加载 CUBIN 文件，使用 `cuobjdump -symbols` 解析唯一入口符号（排除 `vprintf`、`__instantiate_kernel`、`__internal`、`__assertfail`），通过 `load_kernel` 加载内核函数。
- **F-124**: `KernelRuntime::check_validity(dir_path)` 检查目录中 `kernel.cu` 和 `kernel.cubin` 是否同时存在。
- **F-125**: `LaunchArgs` 结构体（`csrc/jit/launch_runtime.hpp:14-27`）包含：`grid_dim: pair<int,int>`、`num_threads: int`、`smem_size: int`、`cluster_dim: int`、`cooperative: bool`、`pdl_enabled: bool`，提供两个构造函数重载。
- **F-126**: `LaunchRuntime<Derived>` 模板基类（`csrc/jit/launch_runtime.hpp:29-72`）使用 CRTP 模式，提供 `generate(args)` 和 `launch(kernel_runtime, args, stream_opt)` 静态方法。`generate` 调用 `Derived::generate_impl` 生成 CUDA C++ 代码并附加 include 哈希；`launch` 配置 grid/block 维度和共享内存后调用 `Derived::launch_impl` 启动内核。
- **F-127**: 内核句柄类型通过条件编译区分：CUDA Runtime API（CUDART_VERSION >= 12080 且定义 `EP_JIT_USE_RUNTIME_API`）使用 `cudaLibrary_t`/`cudaKernel_t`/`cudaLaunchConfig_t`；否则使用 CUDA Driver API 的 `CUmodule`/`CUfunction`/`CUlaunchConfig`（定义在 `csrc/jit/handle.hpp`）。
- **F-128**: `construct_launch_config` 函数配置内核启动参数，支持 cluster dimension、cooperative launch、programmatic dependent launch（PDL）属性。
- **F-129**: 环境变量 `EP_JIT_DEBUG`（默认 0）控制 JIT 调试输出，非零时打印生成的内核代码和启动配置。
- **F-130**: 环境变量 `EP_JIT_CACHE_DIR`、`EP_JIT_PRINT_COMPILER_COMMAND`、`EP_NUM_TOPK_IDX_BITS`、`EP_NCCL_ROOT_DIR` 为持久化环境变量，在安装时被捕获并烘焙到包中作为默认值（定义在 `setup.py:13`）。

## 11. C++ ElasticBuffer 实现细节

- **F-131**: C++ `ElasticBuffer` 类定义在 `csrc/elastic/buffer.hpp:19-1344`，内存布局为 `[[[Workspace] GPU buffer] CPU buffer]`。
- **F-132**: 缓冲区对齐常量 `kNumAlignmentBytes = 2097152`（2 MB），定义在 `csrc/kernels/backend/symmetric.hpp:16`。
- **F-133**: C++ ElasticBuffer 内部使用独立通信流 `comm_stream`，通过 `get_global_comm_stream()`（`csrc/elastic/utils.hpp:8-13`）从 CUDA 流池获取（高优先级）。
- **F-134**: C++ ElasticBuffer 持有 `std::shared_ptr<nccl::NCCLSymmetricMemoryContext> nccl_context` 管理对称内存。
- **F-135**: C++ ElasticBuffer 构造函数参数：`rank_idx, num_ranks, nccl_comm (int64_t), cpu_comm, num_buffer_bytes, num_cpu_buffer_bytes, allow_hybrid_mode, allow_multiple_reduction, prefer_overlap_with_compute, sl_idx, num_allocated_qps, num_cpu_timeout_secs, num_gpu_timeout_secs, explicitly_destroy`。
- **F-136**: GPU 超时通过 `num_gpu_timeout_secs * device_runtime->get_clock_rate()` 转换为 GPU 周期数。
- **F-137**: Host workspace 通过 `cudaMallocHost` 分配映射内存，大小为 `WorkspaceLayout::get_num_bytes()`，初始清零。
- **F-138**: `stream_control_prologue` 方法处理流控制：若 `allocate_on_comm_stream=True` 则切换到通信流分配张量；若有 `previous_event` 则等待前序事件；否则等待计算流。
- **F-139**: `stream_control_epilogue` 方法处理尾部流控制：若 `async_with_compute_stream=True` 则在通信流上记录 EventHandle 并处理张量流记录；否则让计算流等待通信流。
- **F-140**: `calculate_buffer_size` 静态方法（`csrc/elastic/buffer.hpp:652-686`）根据拓扑和 MoE 参数计算所需缓冲区大小，取 dispatch 和 combine 布局的最大值并对齐到 2 MB。
- **F-141**: `create_cpu_handle(num_cpu_bytes)` 静态方法调用 `HybridElasticSymmetricMemory::create_cpu_handle` 创建 CPU 内存句柄。
- **F-142**: pybind11 绑定（`csrc/elastic/buffer.hpp:1346-1380`）将 C++ ElasticBuffer 暴露为 Python 类 `_C.ElasticBuffer`，并注册模块级函数：`create_cpu_handle`、`calculate_elastic_buffer_size`、`get_elastic_buffer_alignment`、`get_local_nccl_unique_id`、`create_nccl_comm`、`destroy_nccl_comm`、`get_physical_domain_size`、`get_logical_domain_size`。

## 12. 内核启动器（Kernels）

### 12.1 Barrier 内核

- **F-143**: `BarrierRuntime` 类定义在 `csrc/kernels/elastic/barrier.hpp`，继承 `jit::LaunchRuntime<BarrierRuntime>`，启动 GPU barrier 内核。
- **F-144**: `launch_barrier(...)` 函数（`csrc/kernels/elastic/barrier.hpp`）JIT 编译并启动 barrier 内核，模板参数包括 num_scaleout_ranks、num_scaleup_ranks、num_threads、is_scaleup_nvlink、sequential。

### 12.2 Dispatch 内核

- **F-145**: `DispatchRuntime` 类定义在 `csrc/kernels/elastic/dispatch.hpp`，继承 `jit::LaunchRuntime<DispatchRuntime>`，启动 dispatch 内核。模板参数包括 num_qps、num_max_tokens_per_rank、num_hidden_bytes、num_sf_packs、num_topk、num_experts、num_threads、num_channels_per_sm、is_scaleup_nvlink、team_tag。
- **F-146**: `DispatchCopyEpilogueRuntime` 类定义在同一文件，启动 dispatch copy epilogue 内核，负责将数据从中间缓冲区拷贝到最终接收张量。
- **F-147**: `launch_dispatch(...)` 函数生成、编译并启动 dispatch 内核；`launch_dispatch_copy_epilogue(...)` 启动 copy epilogue 内核。Dispatch 内核使用 `kNumDispatchThreads = 1024` 线程。

### 12.3 Combine 内核

- **F-148**: `CombineRuntime` 类定义在 `csrc/kernels/elastic/combine.hpp`，继承 `jit::LaunchRuntime<CombineRuntime>`，启动 combine 内核（将数据推送到远程缓冲区）。
- **F-149**: `CombineReduceEpilogueRuntime` 类定义在同一文件，启动 combine reduce epilogue 内核（执行规约加法并写回结果）。
- **F-150**: `launch_combine(...)` 函数启动 combine push 内核；`launch_combine_reduce_epilogue(...)` 启动 reduce epilogue 内核。Combine 内核使用 `kNumCombineThreads = 1024` 线程。

### 12.4 Engram 内核

- **F-151**: `EngramFetchRuntime` 类定义在 `csrc/kernels/elastic/engram.hpp:15-81`，继承 `jit::LaunchRuntime<EngramFetchRuntime>`，启动 Engram 远程获取内核。模板参数包括 num_qps、num_entries_per_rank、num_hidden_bytes、num_sf_packs、num_entries_per_token、num_rdma_peers、num_ranks_per_rdma_peer、num_cpu_bytes_per_rank、num_threads、team_tag。
- **F-152**: `EngramFetchWaitRuntime` 类定义在同一文件 `:128-189`，启动 Engram fetch wait 内核等待 RDMA 完成。
- **F-153**: `launch_engram_fetch(...)` 和 `launch_engram_fetch_wait(...)` 分别启动获取和等待内核，均使用 1024 线程。

### 12.5 PP Send/Recv 内核

- **F-154**: `PPSendRuntime` 类定义在 `csrc/kernels/elastic/pp_send_recv.hpp:15-62`，继承 `jit::LaunchRuntime<PPSendRuntime>`，启动 PP send 内核。模板参数包括 grid_dim、num_ranks、num_smem_bytes、num_timeout_cycles。
- **F-155**: `PPRecvRuntime` 类定义在同一文件 `:97-146`，启动 PP recv 内核。
- **F-156**: `launch_pp_send(...)` 和 `launch_pp_recv(...)` 使用 32 线程/block，支持 PDL（programmatic dependent launch）。

### 12.6 内核聚合头

- **F-157**: `csrc/kernels/elastic/api.hpp` 是聚合头文件，包含 `barrier.hpp`、`dispatch.hpp`、`combine.hpp`、`engram.hpp`、`pp_send_recv.hpp`。

## 13. 后端通信 API

- **F-158**: `deep_ep::nvshmem` 命名空间（`csrc/kernels/backend/api.cuh:14-31`）提供 NVSHMEM 相关函数：`get_unique_id()`、`init(root_unique_id_val, rank, num_ranks, team_split_stride)`、`alloc(size, alignment)`、`free(ptr)`、`barrier(with_cpu_sync, stream_opt)`、`finalize()`。
- **F-159**: `deep_ep::nccl` 命名空间（`csrc/kernels/backend/api.cuh:33-95`）提供 NCCL 相关函数：`get_local_unique_id()` 返回 `pybind11::bytearray`；`create_nccl_comm(root_unique_id_bytes, num_ranks, rank_idx)` 返回 `int64_t`；`destroy_nccl_comm(nccl_comm)`；`get_physical_domain_size(nccl_comm)` 返回 `tuple<int,int>`；`get_logical_domain_size(nccl_comm, allow_hybrid_mode)` 返回 `tuple<int,int>`。
- **F-160**: `NCCLSymmetricMemoryContext` 结构体（`csrc/kernels/backend/api.cuh:47-93`）持有对称内存上下文，成员包括：rank 相关字段（`rank_idx`、`num_ranks`、`num_scaleout_ranks`、`num_scaleup_ranks`、`scaleout_rank_idx`、`scaleup_rank_idx`、`num_rdma_ranks`、`num_nvl_ranks`、`rdma_rank_idx`、`nvl_rank_idx`、`is_scaleup_nvlink`）、NCCL 句柄（`comm: ncclComm_t`、`dev_comm: NoRefPtr`、`window: ncclWindow_t`、`mapped_window_ptr`、`nvl_window_ptrs`）、配置（`num_allocated_qps`）、缓冲区大小（`num_gpu_bytes`、`num_cpu_bytes`）。
- **F-161**: `NCCLSymmetricMemoryContext::get_sym_ptr(ptr, dst_rank_idx)` 返回指定 rank 上指针对应的对称内存地址。
- **F-162**: `deep_ep::cuda_driver` 命名空间（`csrc/kernels/backend/api.cuh:97-104`）提供批量写等待函数：`batched_write(stream, ptrs, value)`、`batched_wait(stream, ptrs, value)`、`batched_write_and_wait(stream, write_ptrs, wait_ptrs, value)`，用于 AGRS session 信号同步。

## 14. 对称内存分配

- **F-163**: `GPUSymmetricMemory`、`ElasticSymmetricMemory`、`HybridElasticSymmetricMemory` 类定义在 `csrc/kernels/backend/symmetric.hpp`，管理 CUDA 驱动 API 级别的对称内存分配。
- **F-164**: `DeviceContext` 结构体（`csrc/kernels/backend/symmetric.hpp:22-70`）管理 CUDA 设备属性和 NUMA 关联，创建 GPU/HOST 分配属性（使用 `CU_MEM_ALLOCATION_TYPE_PINNED`、`CU_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR`，CUDA 13+ 支持 FABRIC 句柄）。
- **F-165**: CPU 通信类型别名：`cpu_handle_t = pair<int, int>`（pid, fd），`cpu_comm_t = vector<cpu_handle_t>`。
- **F-166**: `cumem_create_with_fallback` 函数（`csrc/kernels/backend/symmetric.hpp:73-81`）尝试使用 FABRIC 句柄创建 CUDA 内存，失败时回退到非 FABRIC 模式。

## 15. Python C 扩展绑定

- **F-167**: Python C 扩展模块名为 `_C`（`TORCH_EXTENSION_NAME = _C`），定义在 `csrc/python_api.cpp:22`。
- **F-168**: 模块文档字符串为 `"DeepEP: an efficient expert-parallel communication library"`。
- **F-169**: 模块导出 `is_sm90_compiled()` 函数返回 `deep_ep::kEnableSM90Features`。
- **F-170**: 模块通过 `deep_ep::jit::register_apis(m)` 注册 JIT API（`init_jit`）；通过 `deep_ep::legacy::register_apis(m)` 注册遗留 Buffer API；通过 `deep_ep::elastic::register_apis(m)` 注册弹性 Buffer API。
- **F-171**: 模块设置 `topk_idx_t` 属性为 `c10::CppTypeToScalarType<deep_ep::topk_idx_t>::value` 对应的 PyTorch dtype。

## 16. 环境变量汇总

- **F-172**: `EP_SUPPRESS_NCCL_CHECK`：设为 1 跳过 NCCL 库一致性检查。
- **F-173**: `EP_JIT_DEBUG`：设为非零值启用 JIT 调试输出（打印生成代码和启动配置）。
- **F-174**: `EP_REUSE_NCCL_COMM`：设为 1（默认）复用 PyTorch 的 NCCL 通信器，设为 0 总是创建新通信器。
- **F-175**: `EP_NIC_NAME`：RDMA NIC 设备名，默认 `mlx5_0`。
- **F-176**: `EP_OVERRIDE_RDMA_SL`：覆盖 RDMA Service Level 索引。
- **F-177**: `EP_BUFFER_DEBUG`：设为非零值打印缓冲区调试信息。
- **F-178**: `EP_AVOID_RECORD_STREAM`：设为非零值使用 EventHandle 内部张量记录替代 `record_stream` 调用。
- **F-179**: `EP_NUM_MAX_LOCAL_RANKS`：最大本地 rank 数，默认 16，用于 CPU buffer 的 VA space 计算。
- **F-180**: `NCCL_GIN_CROSS_NIC`、`NCCL_SYM_REUSE_SYSMEM_HANDLES`、`NCCL_WIN_STRIDE`：NCCL 相关环境变量，在 ElasticBuffer 构造时根据条件设置。
