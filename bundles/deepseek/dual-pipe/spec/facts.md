# DualPipe 事实清单（R阶段产出）

> 源码路径：`external/libs/ai/deepseek-ai/DualPipe/`
> 版本：1.0.0
> 采集时间：2026-08-23

F-001: `dualpipe/__init__.py` 定义 `__version__ = "1.0.0"`
F-002: `dualpipe/__init__.py` 从 `dualpipe.dualpipe` 导入 `DualPipe` 类
F-003: `dualpipe/__init__.py` 从 `dualpipe.dualpipev` 导入 `DualPipeV` 类
F-004: `dualpipe/__init__.py` 从 `dualpipe.comm` 导入 `set_p2p_tensor_shapes` 和 `set_p2p_tensor_dtype` 函数
F-005: `dualpipe/__init__.py` 从 `dualpipe.utils` 导入 `WeightGradStore` 类
F-006: `dualpipe/__init__.py` 的 `__all__` 列表包含 `["DualPipe", "DualPipeV", "WeightGradStore", "set_p2p_tensor_shapes", "set_p2p_tensor_dtype"]`

F-007: `dualpipe/dualpipe.py` 定义 `DualPipe` 类，继承自 `torch.nn.Module`
F-008: `DualPipe.__init__` 接受参数 `modules: Tuple[nn.Module, nn.Module]`, `batch_dim: int = 0`, `process_group: Optional[dist.ProcessGroup] = None`, `rank_mapping: Optional[List[int]] = None`
F-009: `DualPipe.__init__` 中 `self.module = nn.ModuleList(modules)`，存储两个模块
F-010: `DualPipe.__init__` 中 `self.overlapped_forward_backward` 通过检测 `type(modules[0]) == type(modules[1]) and hasattr(type(modules[0]), "overlapped_forward_backward")` 判断是否支持前后向重叠
F-011: `DualPipe.__init__` 中 `self.group` 使用传入的 `process_group` 或默认进程组 `dist.distributed_c10d._get_default_group()`
F-012: `DualPipe.__init__` 中 `self.num_ranks = self.group.size()`
F-013: `DualPipe.__init__` 支持 `rank_mapping` 参数，将进程组 rank 映射到 PP rank；默认为 `list(range(self.num_ranks))`
F-014: `DualPipe.__init__` 中计算 `rank_inverse_mapping`，用于从 PP rank 反查进程组 rank
F-015: `DualPipe.__init__` 中设置 `self.rank`, `self.first_rank`, `self.prev_rank`, `self.next_rank`, `self.last_rank`
F-016: `DualPipe.__init__` 中设置 `self.is_first_rank`, `self.is_last_rank`, `self.is_in_second_half`（rank >= num_ranks//2）, `self.is_middle_rank`（rank == num_ranks//2 - 1 或 rank == num_ranks//2）
F-017: `DualPipe._reset_states` 方法清空 `WeightGradStore`，初始化 `input_chunks`, `output_chunks`, `input_grad_chunks`, `output_grad_chunks` 为 `([], [])` 二元组
F-018: `DualPipe._reset_states` 中初始化 `current_f_chunk_id`, `current_b_chunk_id`, `current_send_f_chunk_id`, `current_send_b_chunk_id`, `current_recv_f_chunk_id`, `current_recv_b_chunk_id` 为 `[0, 0]`
F-019: `DualPipe._reset_states` 中初始化 `comm_ops: List[dist.P2POp] = []`, `to_free: List[torch.Tensor] = []`
F-020: `DualPipe._forward_compute_chunk(self, phase: int)` 方法：执行 phase 方向的前向计算
F-021: `DualPipe._forward_compute_chunk` 中 `phase ^= self.is_in_second_half`，后半部分 rank 的 phase 翻转
F-022: `DualPipe._forward_compute_chunk` 中 `is_last_stage = (self.is_first_rank and phase == 1) or (self.is_last_rank and phase == 0)`
F-023: `DualPipe._forward_compute_chunk` 中调用 `self.module[phase](*inputs)` 执行前向
F-024: `DualPipe._forward_compute_chunk` 中如果是最后阶段且有 criterion，则计算 loss 加入 `self.loss_chunks`
F-025: `DualPipe._backward_compute_chunk(self, phase: int, enable_zb: bool = False)` 方法：执行 phase 方向的反向计算
F-026: `DualPipe._backward_compute_chunk` 中 `WeightGradStore.enabled = enable_zb` 控制零气泡权重梯度存储
F-027: `DualPipe._backward_compute_chunk` 中最后阶段调用 `loss.backward()`，非最后阶段调用 `run_backward(outputs, output_grads)`
F-028: `DualPipe._backward_compute_chunk` 中如果 `enable_zb=True`，调用 `WeightGradStore.flush()`
F-029: `DualPipe._forward_backward_compute_chunk(self, phase0: int, phase1: int)` 方法：重叠执行 phase0 前向和 phase1 反向
F-030: `DualPipe._forward_backward_compute_chunk` 中如果模块支持 `overlapped_forward_backward`，调用 `type(module0).overlapped_forward_backward(...)` 实现计算重叠
F-031: `DualPipe._forward_chunk(self, phase: int, recv: bool = True, send: bool = True)` 方法：接收-计算-发送一个前向 micro-batch
F-032: `DualPipe._backward_chunk(self, phase: int, enable_zb: bool = False, recv: bool = True, send: bool = True)` 方法：接收-计算-发送一个反向 micro-batch
F-033: `DualPipe._forward_backward_chunk(self, phase0: int, phase1: int, recv0: bool = True)` 方法：重叠执行前后向 chunk
F-034: `DualPipe._weight_chunk(self)` 方法：从 `WeightGradStore.funcs_queue` 中弹出并执行权重梯度计算函数
F-035: `DualPipe._free_tensors(self)` 方法：释放 `self.to_free` 列表中的 tensor 内存（设置 `tensor.data = torch.Tensor()`）
F-036: `DualPipe._recv_forward(self, phase: int)` 方法：从 prev_rank 或 next_rank 接收前向 tensor，加入 `self.input_chunks[phase]`
F-037: `DualPipe._send_forward(self, phase: int)` 方法：将 `self.output_chunks[phase][chunk_id]` 发送给 next_rank 或 prev_rank
F-038: `DualPipe._recv_backward(self, phase: int)` 方法：接收反向梯度 tensor，加入 `self.output_grad_chunks[phase]`
F-039: `DualPipe._send_backward(self, phase: int)` 方法：将 `self.input_grad_chunks[phase][chunk_id]` 发送
F-040: `DualPipe._commit_and_wait_comm(self)` 方法：调用 `dist.batch_isend_irecv(self.comm_ops)` 批量提交通信，等待所有请求完成，然后释放 tensor
F-041: `DualPipe.step(self, *inputs, num_chunks: int = 0, criterion=None, labels=[], return_outputs: bool = False)` 方法：执行一个训练或推理步
F-042: `DualPipe.step` 返回 `Tuple[Optional[torch.Tensor], Optional[Union[torch.Tensor, Tuple[torch.Tensor]]]]`：(loss, outputs)
F-043: `DualPipe.step` 要求 `num_chunks > 0 and num_chunks % 2 == 0 and num_chunks >= num_ranks * 2`
F-044: `DualPipe.step` 要求 `num_ranks % 2 == 0`
F-045: `DualPipe.step` 中 `self.forward_only = not torch.is_grad_enabled()`
F-046: `DualPipe.step` 的调度分为 8 个步骤：nF0 → nF0F1 → nB1W1F1 → nF0B1F1B0（主循环）→ nB1F1B0 → nB1B0 → nWB0 → nW
F-047: `DualPipe.step` 中 inputs 通过 `scatter(inputs, half_num_chunks, self.batch_dim)` 切分为 micro-batch
F-048: `DualPipe.step` 中第一 rank 接收 phase 0 输入、phase 1 labels；最后 rank 相反

F-049: `dualpipe/dualpipev.py` 定义 `DualPipeV` 类，继承自 `torch.nn.Module`
F-050: `DualPipeV.__init__` 接受相同参数 `modules: Tuple[nn.Module, nn.Module]`, `batch_dim: int = 0`, `process_group=None`, `rank_mapping=None`
F-051: `DualPipeV` 没有 `is_in_second_half` 和 `is_middle_rank` 属性（V型调度，rank不翻转）
F-052: `DualPipeV.step` 只要求 `num_chunks > 0 and num_chunks >= num_ranks * 2`（不要求 num_chunks 是偶数）
F-053: `DualPipeV._forward_compute_chunk` 中最后阶段判断：`is_last_stage = (self.is_first_rank and phase == 1)`（V型只有第一 rank 有 loss）
F-054: `DualPipeV._forward_compute_chunk` 中最后 rank phase 0 时，将 outputs detach+requires_grad 后加入 `self.input_chunks[1]`（V型在最后rank连接两个方向）
F-055: `DualPipeV._backward_compute_chunk` 中最后 rank phase 1 时，将 input_grads 加入 `self.output_grad_chunks[0]`
F-056: `DualPipeV.step` 的调度同样 8 步：nF0 → nF0F1 → nB1W1F1 → nF0B1F1B0 → nB1F1B0 → nB1B0 → nWB0 → nW
F-057: `DualPipeV.step` 中最后 rank 处理：forward phase 0 输出传递给 phase 1 输入，backward phase 1 梯度传递给 phase 0
F-058: `DualPipeV.step` 只在 `is_first_rank` 返回 loss 和 outputs

F-059: `dualpipe/comm.py` 定义全局变量 `TENSOR_SHAPES: List[Tuple[int]] = None`
F-060: `dualpipe/comm.py` 定义全局变量 `TENSOR_DTYPE: torch.dtype = None`
F-061: `set_p2p_tensor_shapes(shapes: List[Tuple[int]])` 设置全局 `TENSOR_SHAPES`
F-062: `set_p2p_tensor_dtype(dtype: torch.dtype)` 设置全局 `TENSOR_DTYPE`
F-063: `build_from_tensor_shapes()` 根据 `TENSOR_SHAPES` 和 `TENSOR_DTYPE` 创建 CUDA tensor 列表（requires_grad=True）
F-064: `append_irecv(ops, src, group)` 创建接收 tensor，添加 `dist.P2POp(dist.irecv, tensor, src)` 到 ops 列表，返回 tensors
F-065: `append_isend(ops, tensors, dst, group)` 添加 `dist.P2POp(dist.isend, tensor, dst)` 到 ops 列表
F-066: `append_irecv` 和 `append_isend` 都使用 `dist.distributed_c10d.get_global_rank(group, local_rank)` 获取全局 rank

F-067: `dualpipe/utils.py` 定义 `WeightGradStore` 类
F-068: `WeightGradStore.enabled: bool = False` 类属性
F-069: `WeightGradStore.cache: List[Callable] = []` 类属性
F-070: `WeightGradStore.funcs_queue = queue.Queue()` 类属性
F-071: `WeightGradStore.put(cls, func: Callable)` 方法：将函数加入 cache 列表
F-072: `WeightGradStore.flush(cls)` 方法：将 cache 列表放入 funcs_queue，清空 cache
F-073: `WeightGradStore.pop(cls)` 方法：从 funcs_queue 取出一个函数列表，依次执行
F-074: `WeightGradStore.clear(cls)` 方法：清空 cache 和 funcs_queue
F-075: `run_backward(tensors, grad_tensors)` 函数：调用 `Variable._execution_engine.run_backward()` 执行反向传播
F-076: `chunk_tensor(x, chunks, dim)` 函数：将 tensor 沿 dim 维度切分为 chunks 份
F-077: `cat_tensor(x, dim)` 函数：将 tensor 列表沿 dim 维度拼接
F-078: `scatter(inputs, chunks, dim)` 函数：将输入 tensor 元组切分为 micro-batch 列表
F-079: `gather(micro_outputs, dim)` 函数：将 micro-batch 输出拼接回完整输出

F-080: `examples/example_dualpipe.py` 定义 `LinearFunc(torch.autograd.Function)` 自定义线性层 autograd 函数
F-081: `examples/example_dualpipe.py` 中 `LinearFunc.backward` 实现：如果 `WeightGradStore.enabled`，将 `grad_weight_fn` 放入 WeightGradStore，否则立即执行
F-082: `examples/example_dualpipe.py` 定义 `PipelineStage(nn.Module)`，包含两个 MyLinear 层和 GELU 激活
F-083: `PipelineStage.overlapped_forward_backward` 类方法：自定义前后向重叠策略（前向计算后立即执行反向）
F-084: `examples/example_dualpipe.py` 中 DualPipe 需要偶数个 GPU（每个 rank 持有两个 stage：rank 和 pp_size-1-rank）
F-085: `examples/example_dualpipev.py` 类似 DualPipe 示例，但使用 DualPipeV，每个 rank 持有两个 stage（rank 和 2*pp_size-1-rank），只需要 pp_size 个 GPU
