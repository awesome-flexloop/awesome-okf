---
type: spec
title: "DualPipe 架构洞察（I阶段产出）"
---

# DualPipe 架构洞察（I阶段产出）

> 基于事实清单 facts.md 分析，提炼架构设计要点

## I-1: 双向流水线核心机制

DualPipe 的核心创新是让每个 GPU 同时持有两个 pipeline stage（rank 和 pp_size-1-rank），形成"双向"流水线：
- Phase 0 从第一个 stage 向最后一个 stage 前向传播
- Phase 1 从最后一个 stage 向第一个 stage 前向传播
- 两个方向共享同一组 GPU，实现计算-通信完全重叠

这与传统 1F1B 流水线（单方向，有大量流水线气泡）不同。DualPipe 的调度序列 8 步中，前向计算、反向计算和通信在大部分步骤中完全重叠。

## I-2: rank_mapping 支持非连续 rank

`DualPipe.__init__` 接受 `rank_mapping: Optional[List[int]]` 参数，将进程组 rank 映射到 PP rank。这允许用户自定义 rank 到 stage 的映射关系，适用于拓扑感知的部署（如将相邻 stage 放在 NVLink 连接的 GPU 对上）。默认映射是 `list(range(num_ranks))`（恒等映射）。

`rank_inverse_mapping` 字典用于反查：给定 PP rank 找到对应的进程组 rank，用于 `_recv_forward`/`_send_forward` 等通信操作。

## I-3: overlapped_forward_backward 自定义重叠接口

模块可以通过实现类方法 `overlapped_forward_backward(phase0, phase1, input0, inputs1)` 来自定义前向和反向的重叠策略。当两个 module 类型相同且该方法存在时，DualPipe 调用该方法而非默认的分离式前向+反向。

示例代码展示了 `PipelineStage.overlapped_forward_backward` 的实现：先做前向计算，保存输入，再立即执行反向传播，中间不释放中间激活值，实现计算时间上的完全重叠。

## I-4: WeightGradStore 零气泡优化

`WeightGradStore` 类实现了权重梯度计算的延迟执行：
- 在反向传播中，权重梯度的计算函数被放入 `WeightGradStore.cache` 列表
- 当 `enable_zb=True` 时（零气泡模式），这些函数不会立即执行
- 而是通过 `WeightGradStore.flush()` 移到 `funcs_queue` 队列
- 在 `_weight_chunk()` 中被批量执行，与通信重叠

这使得权重梯度计算（W 阶段）可以与前向/反向通信并行，进一步减少流水线气泡。

## I-5: DualPipe vs DualPipeV 差异

| 特征 | DualPipe | DualPipeV |
|------|----------|-----------|
| GPU 需求 | 偶数个 GPU（2*pp_size） | pp_size 个 GPU |
| Stage 分配 | 每个 GPU 持有 stage(rank) 和 stage(pp_size-1-rank) | 每个 GPU 持有 stage(rank) 和 stage(2*pp_size-1-rank) |
| Phase 连接 | 第一/最后 rank 各持一个方向端点 | 最后 rank 处 phase 0 输出→phase 1 输入（V型连接） |
| Loss 位置 | 第一 rank（phase=1）或最后 rank（phase=0） | 仅第一 rank（phase=1） |
| num_chunks 约束 | 必须为偶数且 ≥ 2*pp_size | 只需 ≥ 2*pp_size |
| 适用场景 | 对称双向调度 | V型调度，节省 GPU 数量 |

## I-6: 通信模式

通信模块 `comm.py` 使用全局变量存储 P2P tensor 的 shape 和 dtype：
1. 用户必须先调用 `set_p2p_tensor_shapes()` 和 `set_p2p_tensor_dtype()` 配置
2. `append_irecv()` 按照预设 shapes 创建接收 tensor，加入 P2POp 列表
3. `append_isend()` 将输出 tensor 加入发送操作列表
4. `_commit_and_wait_comm()` 使用 `dist.batch_isend_irecv()` 批量执行所有 P2P 操作
5. 通信完成后 `to_free` 列表中的临时 tensor 被释放

使用 `batch_isend_irecv` 而非逐条 send/recv 可以让通信硬件并行处理所有 P2P 操作。

## I-7: chunk 调度流程（8步循环）

step() 方法的主循环分为 8 个步骤，按 num_chunks 次循环执行：

1. **nF0**: 接收 phase0 前向 → 计算前向0 → 发送前向0
2. **nF0F1**: 接收前向0+前向1 → 计算前向0+前向1 → 发送前向0+前向1
3. **nB1W1F1**: 接收前向1+反向1 → 计算反向1（含W）+前向1 → 发送反向1+前向1
4. **nF0B1F1B0** (主循环): 接收前向0+前向1+反向1+反向0 → 计算前向0+反向1+前向1+反向0 → 发送前向0+反向1+前向1+反向0
5. **nB1F1B0**: 接收前向1+反向1+反向0 → 计算反向1+前向1+反向0 → 发送反向1+前向1+反向0
6. **nB1B0**: 接收反向1+反向0 → 计算反向1+反向0 → 发送反向1+反向0
7. **nWB0**: 计算W（权重梯度）+ 接收反向0 → 计算反向0 → 发送反向0
8. **nW**: 计算W

每个 GPU 根据自身位置（first/last/middle/second_half）跳过不属于自己的操作，形成双向流水线。
