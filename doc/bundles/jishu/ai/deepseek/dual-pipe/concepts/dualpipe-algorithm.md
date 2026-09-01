---
type: concept
scope: dual-pipe
name: DualPipe 算法调度
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/dualpipe/dualpipe.py
prerequisites:
  - /deepseek/dual-pipe/concepts/overview
description: 深入解析 DualPipe.step() 的 8 步调度算法，包括 chunk 流转、通信模式和零气泡优化
---

# DualPipe 算法调度

## 前置条件

DualPipe 的调度有以下约束（源码 F-043, F-044）：

1. `num_ranks` 必须为偶数
2. `num_chunks` 必须为正偶数且 ≥ 2×num_ranks
3. 每个 rank 持有两个 module：`self.module[0]` 和 `self.module[1]`
4. 必须先调用 `set_p2p_tensor_shapes()` 和 `set_p2p_tensor_dtype()` 配置通信

## 八步调度流程

DualPipe.step() 的主循环分为 8 个步骤。以 num_ranks=4（4个GPU）为例，每个 GPU 执行对应步骤：

### Step 1: nF0（warmup 前向 phase 0）

- 接收来自前一个 rank 的 phase 0 前向输入
- 执行 phase 0 前向计算
- 发送 phase 0 前向输出到下一个 rank

```
每个GPU: [recv_f0] → [compute_f0] → [send_f0]
```

### Step 2: nF0F1（warmup 双向前向）

- 同时接收两个方向的前向输入
- 同时执行两个方向的前向计算
- 同时发送两个方向的前向输出

```
每个GPU: [recv_f0 + recv_f1] → [compute_f0 + compute_f1] → [send_f0 + send_f1]
```

### Step 3: nB1W1F1（warmup 反向+前向重叠）

- 接收 phase 1 反向梯度和 phase 1 前向输入
- 执行 phase 1 反向计算（含权重梯度）+ phase 1 前向计算
- 发送 phase 1 前向输出和反向梯度

这一步是第一个计算重叠点：一个方向的反向与另一个方向的前向同时进行。

### Step 4: nF0B1F1B0（主循环，稳态阶段）

这是最核心的步骤，执行 num_chunks - 2×num_ranks 次（即填充完流水线后循环）：

- 接收：phase 0 前向 + phase 1 反向 + phase 1 前向 + phase 0 反向
- 计算：phase 0 前向 + phase 1 反向 + phase 1 前向 + phase 0 反向
- 发送：phase 0 前向 + phase 1 反向 + phase 1 前向 + phase 0 反向

**四个操作完全重叠**：前向0、前向1、反向0、反向1同时在不同的 CUDA stream 上执行，通信与计算重叠。

### Step 5: nB1F1B0（cooldown 反向+前向）

- 接收：phase 1 反向 + phase 1 前向 + phase 0 反向
- 计算：phase 1 反向 + phase 1 前向 + phase 0 反向
- 发送：phase 1 反向 + phase 1 前向 + phase 0 反向

### Step 6: nB1B0（cooldown 双向反向）

- 接收：phase 1 反向 + phase 0 反向
- 计算：phase 1 反向 + phase 0 反向
- 发送：phase 1 反向 + phase 0 反向

### Step 7: nWB0（收尾权重+反向）

- 执行权重梯度计算（W阶段，来自 WeightGradStore）
- 接收 phase 0 反向梯度
- 执行 phase 0 反向计算
- 发送 phase 0 反向梯度

### Step 8: nW（最终权重更新）

- 执行最后一批权重梯度计算

## 微批次流转

以 num_ranks=4, num_chunks=8 为例，phase 0 的 chunk 流转：

```
时间步 →  1  2  3  4  5  6  7  8
GPU0(s0): F0 F1       B1 B0    W
GPU1(s1):    F0 F1    B1 B0 W
GPU2(s2):       F0 F1 B1 B0 W
GPU3(s3):          F0 B1    W
```

（简化视图，实际是双向的）

## Phase 翻转机制

在后半部分 rank（`is_in_second_half = True`），phase 会被翻转：`phase ^= self.is_in_second_half`。这意味着：
- GPU0（first half）处理 phase 0 前向时，GPU3（second half）实际上在处理 phase 1
- 这种翻转确保了对称的双向调度

## 中间 Rank 的特殊处理

中间两个 rank（`is_middle_rank = True`，即 rank = num_ranks//2-1 和 rank = num_ranks//2）在 step 4（主循环）中额外执行权重梯度计算（`_weight_chunk()`），使得 W 阶段也能与其他计算重叠。

## 通信批量执行

所有 P2P 通信操作通过 `comm_ops` 列表累积，最后由 `_commit_and_wait_comm()` 调用 `dist.batch_isend_irecv()` 批量执行。这确保所有 isend/irecv 操作同时启动，由 NCCL/NVLink 硬件并行处理。

详见 P2P 通信模式。
