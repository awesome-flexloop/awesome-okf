---
type: concept
scope: dual-pipe
name: P2P 通信模式
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/dualpipe/comm.py, dualpipe/dualpipe.py
prerequisites:
  - /deepseek/dual-pipe/concepts/overview
  - /pydata/pytorch/distributed/p2p-communication
description: 解释 DualPipe 的 P2P 通信机制，包括全局 tensor shape 配置、批量通信和内存管理
---

# P2P 通信模式

## 通信配置前置步骤

在使用 DualPipe 之前，必须先配置 P2P 通信 tensor 的形状和类型：

```python
from dualpipe import set_p2p_tensor_shapes, set_p2p_tensor_dtype

# 设置通信 tensor 的形状列表
set_p2p_tensor_shapes([(hidden_size,), (hidden_size,), ...])

# 设置通信 tensor 的数据类型
set_p2p_tensor_dtype(torch.bfloat16)
```

这两个函数设置全局变量 `TENSOR_SHAPES` 和 `TENSOR_DTYPE`，后续的 `append_irecv` 使用这些信息预分配接收缓冲区。

## 通信流程

DualPipe 的每次 P2P 通信遵循以下模式：

### 1. 累积通信操作

```python
def _recv_forward(self, phase: int):
    # 根据 phase 判断通信的 peer rank
    if phase == 0:
        src = self.prev_rank if not self.is_in_second_half else self.next_rank
    else:
        src = self.next_rank if not self.is_in_second_half else self.prev_rank
    
    # 创建接收 tensor 并添加 irecv 操作
    inputs = append_irecv(self.comm_ops, self.rank_inverse_mapping[src], self.group)
    self.input_chunks[phase].append(tuple(inputs))
```

`append_irecv` 内部做了：
1. 调用 `build_from_tensor_shapes()` 根据预设 shapes/dtype 在 CUDA 上创建 tensor
2. 创建 `dist.P2POp(dist.irecv, tensor, global_rank)` 操作
3. 将操作追加到 ops 列表
4. 返回创建的 tensor 列表

### 2. 批量提交

所有 isend/irecv 操作累积到 `self.comm_ops` 列表后，`_commit_and_wait_comm()` 一次性提交：

```python
def _commit_and_wait_comm(self):
    reqs = dist.batch_isend_irecv(self.comm_ops)
    for req in reqs:
        req.wait()
    # 释放临时 tensor
    for tensor in self.to_free:
        tensor.data = torch.Tensor()  # 释放 CUDA 内存
    self.comm_ops = []
    self.to_free = []
```

### 3. 内存释放

通信完成后，`to_free` 列表中的 tensor 被显式释放（通过将 `.data` 设置为空 Tensor），避免在 micro-batch 间累积显存占用。

## Peer Rank 计算

DualPipe 的双向通信需要根据 phase 和当前 rank 位置动态计算通信对象：

| 操作 | phase=0（前半rank） | phase=1（前半rank） | phase=0（后半rank） | phase=1（后半rank） |
|------|---------------------|---------------------|---------------------|---------------------|
| 接收前向 | prev_rank | next_rank | next_rank | prev_rank |
| 发送前向 | next_rank | prev_rank | prev_rank | next_rank |
| 接收反向 | next_rank | prev_rank | prev_rank | next_rank |
| 发送反向 | prev_rank | next_rank | next_rank | prev_rank |

这是因为后半部分 rank 的 phase 被翻转（`phase ^= self.is_in_second_half`），通信方向也相应翻转。

## rank_mapping 支持

当使用自定义 `rank_mapping` 时，实际通信通过 `rank_inverse_mapping` 字典查找全局 rank：

```python
self.rank_inverse_mapping = {v: k for k, v in enumerate(rank_mapping)}
```

`append_irecv`/`append_isend` 使用 `get_global_rank(group, rank_inverse_mapping[peer])` 获取全局 rank，支持在非连续 rank 组成的子进程组中正确通信。

## 通信与计算重叠

关键设计：通信操作的提交（isend/irecv）发生在计算之前，而等待（wait）发生在计算之后：

```python
# 先提交接收
self._recv_forward(0)
# 提交发送
self._send_forward(0)
# 执行计算（此时通信在后台进行）
self._forward_compute_chunk(0)
# 等待通信完成
self._commit_and_wait_comm()
```

这确保 GPU 计算核函数和 NCCL 通信核函数在不同的 CUDA stream 上并行执行，实现计算-通信重叠。
