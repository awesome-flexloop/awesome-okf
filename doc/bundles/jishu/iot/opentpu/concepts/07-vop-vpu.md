---
okf_version: "0.2"
type: Concept
title: "VOP 向量指令：20 个功能码、四种广播与归约/OUTER/ARGMAX"
description: "VOP 一条指令操作 TMEM 瓦片：四种 B 广播模式、20 个已定义功能码（码 7 跳用）、逐元素算子与 EXP2SUB 融合、P=64 归约、ARGMAX 出 token id、OUTER 线性循环状态更新"
tags: [openTPU, VOP, VPU, 向量指令, 归约, softmax]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T16:20:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-13T18:10:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: opentpu-facts
    resource: /references/facts.md
    title: "openTPU 事实登记表 F-001~F-123"
  - id: opentpu-pinned
    resource: "https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e"
    title: "openTPU 固定提交 ffe997e"
---

VOP（opcode `0x30`）是 VPU 对外的唯一指令：它对 TMEM 中的 `[rows, cols]` fp32 瓦片做逐元素运算、行规约或线性循环状态更新，功能由一个 8 位 `func` 字段选择。契约在 [isa.md VOP 节](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L298-L349)，编码构造器是 [isa.py vop()](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L431-L441)，模拟器实现在 [isasim.py `_vop`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L595-L659)。

## 字段与 B 的四种广播模式

`dst=R[ra]+w1`、`a=R[rb]+w2`、`b=R[rc]+w3` 都是 TMEM 字地址；`rows=w4[15:0]`、`cols=w4[31:16]`；`drs/ars/brs` 分别是 dst/A/B 的行跨度（drs、ars 打包在 w5，brs 在 w6 低 16 位）；`func=w6[23:16]`、`bmode=w6[25:24]`；`imm = R[rd]+w7`。A 永远是完整瓦片 `A(r,c) = T[a + r*ars + c]`；B 按 bmode 有四种形状（[isa.md L300-L309](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L300-L309)）：

| bmode | 名称 | `B(r,c)` |
|---|---|---|
| 0 | B_FULL | `T[b + r*brs + c]`（完整瓦片） |
| 1 | B_ROW | `T[b + r*brs]`（每行一个标量；`brs=0` 时整片一个 TMEM 标量） |
| 2 | B_COL | `T[b + c]`（每列一个向量） |
| 3 | B_SCALAR | `imm`（w7 的 fp32 位立即数） |

逐元素功能写 `T[dst + r*drs + c] = f(A, B)`；规约功能从 c=0 顺序折叠，每行写一个 `T[dst + r*drs]`。

## 20 个功能码全表（码 7 跳用）

功能码占槽位 0-20 共 21 个位置，但**码 7 跳用**，已定义的是 **20 个**（[isa.py L39-L46](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L38-L51)）：

| 码 | 名称 | 结果 |
|---|---|---|
| 0-5 | ADD / SUB / RSUB / MUL / MAX / MIN | 对应二元逐元素运算（RSUB=B-A） |
| 6 | OUTER | `A*Dv(c) + B(r)*Cv(c)`，原位更新（见下） |
| 8 | COPY | `A` |
| 9-11 | EXP2 / RECIP / RSQRT | 三个近似函数（[下篇](/concepts/05-elementary-functions.md)） |
| 12-13 | ABS / FILL | `abs(A)`；FILL 写 `B`（不读 A） |
| 14 | EXP2SUB | `exp2(A - B)`，融合 softmax 步 |
| 15 | LOG2 | `log2(A)` |
| 16 | RSUM | `isum_64(A(r,0..cols-1))` |
| 17 | RMAX | 行内全序最大（任意求值顺序同位） |
| 18 | RSSQ | `isum_64(A*A)`（RMSNorm 用，等价 B=A 的 RDOT） |
| 19 | RDOT | `isum_64(A(r,c)*B(r,c))`，B 可任取 bmode |
| 20 | ARGMAX | 每行写 `(RMAX, i2f(首个最大列 + base))` 对 |

RSSQ/RDOT 里每个乘积先舍入，再进部分和。注意 BINARY 集合还包含 FILL 与 EXP2SUB——它们都按 bmode 读 B。

**EXP2SUB** 把 softmax 的「减行最大、再取指数」两步焊死成一条指令：模拟器就是 `F.exp2(F.sub(A, B))`（[isasim.py L656](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L650-L656)）。配合 MM 的 RMAX flag，softmax 的行最大值和指数步都不需要单独的向量遍历。

## 归约：isum_64 的 P=64 部分和

RSUM/RSSQ/RDOT 共享上篇所述的 `isum_64` 规约形状：64 路交错部分和（左到右、+0 填充且参与加法）再过折叠树，因此每个乘积先舍入、加法顺序完全钉死，Python 与 RTL 必须同位。fp32.py 里三者就是 `interleaved_sum(A, 64)` 与 `rdot(A,B) = interleaved_sum(mul(a,b), 64)`（[fp32.py L215-L217](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L215-L222)）。RMAX 走全序比较的 `chain_max`，与折叠顺序无关。

## ARGMAX：为什么输出直接是 token id

ARGMAX 每行写一对：行最大值 `m`，以及 `i2f(c + base)`，`c` 是**第一个**等于 m 的列（[isa.md L336-L340](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L336-L340)）。全序里 `-0 < +0`，所以并列只发生在完全相同的位之间，首个胜出，语义与 `np.argmax` 一致。这里 `base = R[rd]+w7` 被解释为**有符号整数**而不是 fp32 位（[isa.py vop L437](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L437-L437)）：LM head 分块算词表时，每块把自己的**首词表行号**作 base 传入，列号加基址后就是全局 token id。多行时要求 `drs ≥ 2`。B 不读。

## OUTER：线性循环状态更新

功能码 6 的 OUTER 是为线性注意力族量身定的原位状态更新（[isa.md L342-L349](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L342-L349)）：

```text
T[dst + r*drs + c] = T[dst + r*drs + c] * Dv(c) + B(r) * Cv(c)
                     └── 两次舍入积 ──┘   └ 一次舍入积 ┘  └ 一次舍入加
```

适用模型族包括 Gated DeltaNet、Mamba2/SSD、GLA、RWKV 与 linear attention。语义要点：B 必须 per-row（bmode 1）；列向量 `Cv(c)=T[imm+c]`；衰减 `Dv(c)` 取 `T[a+c]`，或 flag bit0（DSCALAR）下整片用 `T[a]`，或 flag bit1（DONE）下用 1.0；`cols ≤ 256`（列向量驻在 256 字缓存里）。**重叠规则**很关键：Cv 与 Dv 在任何写之前先读完，因此允许与 dst 重叠；但 B(r) 随每个元素被读，不能被本指令更早的元素写覆盖（模拟器 `_outer` 先取 C/D 再做 hazard 检查）。

## isasim 的分派结构

[isasim.py `_vop`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L607-L659) 按功能分四条路径：OUTER 单独进 `_outer`（强制 bmode=ROW、cols≤256）；ARGMAX 单独处理（取键序 argmax、有符号 base 相加、写 (max,index) 对）；REDUCE 集合里 RSUM/RSSQ/RDOT 走进交错部分和、RMAX 走 chain_max，并做规约专用的 hazard 检查；其余逐元素算子（ADD/SUB/RSUB/MUL/MAX/MIN、COPY/EXP2/RECIP/RSQRT/ABS/FILL/EXP2SUB/LOG2）统一查 `ops` 字典调 fp32.py 同名函数，未知名抛 `SimError("VOP: bad func")`。

## VPU RTL：七文件与 slot 程序

VPU RTL 共 7 个文件（[rtl/vpu/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu)）：

| 文件 | 职责 |
|---|---|
| [otpu_vpu.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_vpu.sv#L1-L46) | VPU 顶层：每周期沿一行处理 LANES 个 fp32，lane 分裂、slot 调度、规约树、写缓冲、stream engine 接入 |
| [otpu_fp.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_fp.sv#L1-L4) | 组合逻辑位精确 fp 函数与四个复合函数固定序列 |
| otpu_fpipe.sv | 由分级函数拼成的流水算子 `otpu_fmul/fadd/fmadd/fmma` 与延迟线 |
| otpu_quant.sv | QACT/QST 量化器（行 amax、组 d_g、q8、recip 复用 mul-add slot） |
| otpu_se_comp.sv | stream engine 的复合函数微码 stage（EXP2/RECIP/RSQRT/LOG2/EXP2SUB） |
| otpu_se_tail.sv | stream engine 的 U/Q 尾段（即 DSTEP 数据路径） |
| otpu_vtree.sv | RSUM/RSSQ/RDOT 与 DSTEP 两个行点积共用的折叠树 |

[otpu_vpu.sv 头注释](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_vpu.sv#L11-L24)把复合函数列成 slot 程序：ADD/SUB/RSUB/MUL/OUTER 1 slot；EXP2/EXP2SUB 9（减法+范围缩减+7 个 Horner 步）；RECIP 6（两次 Newton+校正）；RSQRT 10（`h=x/2`+两次 Newton+校正）；LOG2 10（`t=m-1`+8 Horner+`i2f(e)`）；MAX/MIN/COPY/ABS/FILL 为 0（读后次周期写出）。普通逐元素函数每周期发射 LANES 列（生产 LANES=8），复合函数只用长 lane、每周期 CL 列（生产 VPU_CL=2）；归约独占流水。规约实现与契约同构：lane l 持有部分和 l、l+LANES、…，用「RL=64/LANES 个 chunk 前的部分和」回灌流水线加法器，行末部分和喂进 otpu_vtree 折叠树；ARGMAX 的树同时携带值与列号，(max,index) 对在行结束后四拍经 lane 0/1 写出。

## 相关概念

- [fp32 数值契约（上）：RNE+FTZ 与零/NaN 规则](/concepts/04-fp32-contract.md)
- [fp32 数值契约（下）：四个近似函数的固定序列](/concepts/05-elementary-functions.md)
- [STREAM/DSTEP 状态引擎与 WAITW](/concepts/12-stream-dstep-caps.md)
- [事实登记表 F-001~F-123](/references/facts.md)
