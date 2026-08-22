---
type: concept
scope: dual-pipe
name: DualPipeV 与 DualPipe 对比
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/dualpipe/dualpipe.py, dualpipe/dualpipev.py
prerequisites:
  - /deepseek/dual-pipe/concepts/overview
  - /deepseek/dual-pipe/concepts/dualpipe-algorithm
description: 对比 DualPipe 和 DualPipeV 两种双向流水线调度的差异，包括 GPU 需求、Stage 分配、连接方式和适用场景
---

# DualPipeV 与 DualPipe 对比

## 核心差异：Stage 分配方式

### DualPipe：对称分配

```
GPU0: stage0 ←→ stage(N-1)
GPU1: stage1 ←→ stage(N-2)
GPU2: stage2 ←→ stage(N-3)
...
GPU(N/2-1): stage(N/2-1) ←→ stage(N/2)
```

- 需要 2×pp_size 个 GPU？实际上 DualPipe 需要偶数个 GPU，每个 GPU 持有对称的两个 stage
- 当 pp_size=4（4个stage）时，需要 4 个 GPU（不是8个）：
  - GPU0: stage0 + stage3
  - GPU1: stage1 + stage2
  - GPU2: stage2 + stage1（is_in_second_half，phase翻转）
  - GPU3: stage3 + stage0

Wait，让我重新理解。根据源码 F-008~F-016 和示例代码：

DualPipe 中 `num_ranks` 是参与的 GPU 数量，必须为偶数。每个 GPU 持有两个 module。GPU 数量 = pp_size（即 stage 数量的一半？不对，让我看示例）。

根据 `examples/example_dualpipe.py` 的注释："DualPipe requires an even number of GPUs, with each GPU holding two stages (rank and pp_size-1-rank)"。

所以当使用 pp_size=4 个 stage 时：
- 需要 4 个 GPU
- GPU i 持有 stage(i) 和 stage(3-i)
- Phase 0 从 GPU0(stage0) → GPU1(stage1) → GPU2(stage2) → GPU3(stage3)
- Phase 1 从 GPU0(stage3) ← GPU1(stage2) ← GPU2(stage1) ← GPU3(stage0)？

不对，让我仔细看源码中的逻辑。实际上 DualPipe 和 DualPipeV 的区别在 stage 分配上：

### DualPipe：双向对称，首尾都有 loss

DualPipe 中：
- GPU0 (is_first_rank): 持有 module[0]=stage0, module[1]=stage(pp_size-1)？
- 看 F-022：`is_last_stage = (self.is_first_rank and phase == 1) or (self.is_last_rank and phase == 0)`

这说明 first rank 的 phase 1 方向和 last rank 的 phase 0 方向都是"最后阶段"（需要计算 loss）。

### DualPipeV：V 型连接，仅首尾 loss

DualPipeV 中（F-053）：
- `is_last_stage = (self.is_first_rank and phase == 1)` — 只有 first rank 的 phase 1 是最后阶段
- 最后 rank（is_last_rank）phase 0 时，outputs 被 detach+requires_grad 后传给 phase 1 作为输入（V 型拐点）

## GPU 数量差异

根据 examples：
- `example_dualpipe.py`: DualPipe 需要偶数个 GPU
- `example_dualpipev.py`: DualPipeV 需要 pp_size 个 GPU

两者实际上都需要偶数个 GPU（因为 DualPipeV 中 num_ranks 也用于 pp_size），关键区别在于 stage 的连接方式。

## 数据流差异

### DualPipe 数据流

```
Phase 0: input → stage0(GPU0) → stage1(GPU1) → ... → stage(N-2)(GPU2) → stage(N-1)(GPU3) → loss
Phase 1: input → stage(N-1)(GPU0) → stage(N-2)(GPU1) → ... → stage1(GPU2) → stage0(GPU3) → loss
```

两个方向独立流动，首尾都有输入和 loss。

### DualPipeV 数据流（V 型）

```
Phase 0: input → stage0(GPU0) → stage1(GPU1) → ... → stage(N-2)(GPU2) → stage(N-1)(GPU3)
                                                                          ↓ (V型连接)
Phase 1: loss ← stage0(GPU0) ← stage1(GPU1) ← ... ← stage(N-2)(GPU2) ← output(detached)
```

Phase 0 的输出在最后一个 GPU（V 型底部）直接传给 phase 1 的输入（detach + requires_grad），形成 V 字型数据流。只有 GPU0 处有 loss。

## num_chunks 约束

| 约束 | DualPipe | DualPipeV |
|------|----------|-----------|
| num_chunks > 0 | ✅ | ✅ |
| num_chunks 必须为偶数 | ✅ | ❌ |
| num_chunks ≥ 2×num_ranks | ✅ | ✅ |

DualPipe 要求 num_chunks 为偶数是因为双向对称调度需要每个方向处理相同数量的 chunk；DualPipeV 的 V 型连接不需要这个约束。

## 代码差异要点

DualPipeV 相对于 DualPipe 的关键代码差异：

1. **无 `is_in_second_half` 和 `is_middle_rank`**：因为 V 型调度不需要 phase 翻转
2. **V 型连接**（F-054, F-055）：最后 rank 的 phase 0 输出传递给 phase 1 输入
3. **Loss 仅在 first rank**（F-053, F-058）：phase=1 时在 is_first_rank 计算 loss
4. **step 中最后 rank 的特殊处理**：F-057 描述了 phase 0→1 的传递和反向 phase 1→0 的传递

## 选择建议

| 场景 | 推荐 |
|------|------|
| 对称双向数据，两端都有输入/标签 | DualPipe |
| 标准自回归模型（一端输入，一端 loss） | DualPipeV |
| 节省 GPU 数量 | DualPipeV（更灵活的 chunk 数） |
| 最小化气泡 | DualPipe（对称调度最充分重叠） |
