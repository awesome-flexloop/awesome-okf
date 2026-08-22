---
type: reference
scope: dual-pipe
name: DualPipe 内部模块结构
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/dualpipe/dualpipe.py, dualpipe/comm.py, dualpipe/utils.py
description: DualPipe 内部方法签名与通信工具函数参考
---

# DualPipe 内部模块参考

## dualpipe.py 内部方法

以下方法为 `DualPipe` 类的内部实现方法，通常不需要直接调用，但理解其行为有助于调试和自定义。

### 状态管理

| 方法 | 签名 | 说明 |
|------|------|------|
| `_reset_states` | `() -> None` | 重置所有内部状态，在 `step()` 开始时调用 |

### 计算方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `_forward_compute_chunk` | `(phase: int) -> None` | 执行指定 phase 的一个 micro-batch 前向计算 |
| `_backward_compute_chunk` | `(phase: int, enable_zb: bool = False) -> None` | 执行指定 phase 的一个 micro-batch 反向计算 |
| `_forward_backward_compute_chunk` | `(phase0: int, phase1: int) -> None` | 重叠执行 phase0 前向和 phase1 反向 |
| `_weight_chunk` | `() -> None` | 执行一批延迟的权重梯度计算 |
| `_free_tensors` | `() -> None` | 释放临时 tensor 内存 |

### 通信方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `_recv_forward` | `(phase: int) -> None` | 从相邻 rank 接收前向激活 |
| `_send_forward` | `(phase: int) -> None` | 向相邻 rank 发送前向激活 |
| `_recv_backward` | `(phase: int) -> None` | 接收反向梯度 |
| `_send_backward` | `(phase: int) -> None` | 发送反向梯度 |
| `_commit_and_wait_comm` | `() -> None` | 批量提交所有 P2P 通信操作并等待完成 |

### Chunk 级方法（接收-计算-发送一体）

| 方法 | 签名 | 说明 |
|------|------|------|
| `_forward_chunk` | `(phase: int, recv: bool = True, send: bool = True) -> None` | 接收-计算-发送一个前向 chunk |
| `_backward_chunk` | `(phase: int, enable_zb: bool = False, recv: bool = True, send: bool = True) -> None` | 接收-计算-发送一个反向 chunk |
| `_forward_backward_chunk` | `(phase0: int, phase1: int, recv0: bool = True) -> None` | 重叠执行前后向 chunk |

---

## comm.py 通信模块

### 全局状态

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `TENSOR_SHAPES` | `List[Tuple[int]]` | `None` | P2P 通信 tensor 形状列表 |
| `TENSOR_DTYPE` | `torch.dtype` | `None` | P2P 通信 tensor 数据类型 |

### 内部函数

| 函数 | 签名 | 说明 |
|------|------|------|
| `build_from_tensor_shapes` | `() -> List[torch.Tensor]` | 根据全局 TENSOR_SHAPES 和 TENSOR_DTYPE 创建 CUDA tensor 列表（requires_grad=True） |
| `append_irecv` | `(ops: List, src: int, group: dist.ProcessGroup) -> List[Tensor]` | 向 ops 添加 irecv 操作，返回接收 tensor 列表 |
| `append_isend` | `(ops: List, tensors: List[Tensor], dst: int, group: dist.ProcessGroup) -> None` | 向 ops 添加 isend 操作 |

**注意**：`append_irecv` 和 `append_isend` 使用 `dist.distributed_c10d.get_global_rank(group, local_rank)` 获取全局 rank，确保在子进程组中正确寻址。

---

## utils.py 工具模块

| 函数/类 | 签名 | 说明 |
|---------|------|------|
| `WeightGradStore` | class | 权重梯度延迟存储类（详见 [api.md](/deepseek/dual-pipe/references/api.md)） |
| `run_backward` | `(tensors, grad_tensors) -> None` | 调用 `Variable._execution_engine.run_backward()` 执行反向传播 |
| `chunk_tensor` | `(x: Tensor, chunks: int, dim: int) -> List[Tensor]` | 将 tensor 沿 dim 切分为 chunks 份 |
| `cat_tensor` | `(x: List[Tensor], dim: int) -> Tensor` | 将 tensor 列表沿 dim 拼接 |
| `scatter` | `(inputs: Tuple[Tensor, ...], chunks: int, dim: int) -> List[Tuple[Tensor, ...]]` | 将输入 tuple 切分为 micro-batch 列表 |
| `gather` | `(micro_outputs: List, dim: int) -> Union[Tensor, Tuple]` | 将 micro-batch 输出拼接回完整输出 |
