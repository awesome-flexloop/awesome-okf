---
okf_version: "0.2"
type: Concept
title: "量化器：QACT/QST、行尺度 Sa/da 与 q8 公式"
description: "openTPU 把量化做成执行单元：QACT/QST 是两条 opcode，行尺度 Sa 与 4 个 da 驻在 ACT RAM，q8 公式与两次舍入乘法逐位受契约约束"
tags: [openTPU, 量化, QACT, QST, ACT RAM, int8, ISA]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T16:40:00+08:00"
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

## 量化为什么是执行单元

在很多推理栈里，量化是部署前的一次性离线变换：脚本把权重换算成整数，运行时硬件只做整数乘加。openTPU 不是这样——量化器（quantizer）是与 DMA、MXU、VPU 并列的执行单元，QACT（0x21）与 QST（0x22）是 17 条指令中的两条 opcode（[isa.py L10-L17](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L10-L17)）。激活在「被使用的地方、被使用的时刻」量化：TMEM 里的 fp32 行进 QACT 变成 ACT RAM 中的 int8 行加尺度记录，随即被 MM 读走；QST 则把量化结果连同尺度直接写进 DRAM 字节（KV cache 就是这样产生的）。

这样设计有两个直接后果。其一，尺度不是旁路元数据，而是机器状态的一部分：它占据 ACT RAM 的存储、是 MM epilogue 的移位与乘法输入（见 [06-mm-and-mxu.md](/concepts/06-mm-and-mxu.md)）。其二，RMSNorm 这类「先缩放再量化」的前处理可以折叠进量化器本身，省掉一整遍向量遍历（见下文 CSCALE/RSCALE）。量化的每一步舍入都写在 [docs/isa.md L135-L150](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L135-L150) 的契约里，fp32.py、isasim.py 与 RTL 必须写出同样的位。

## ACT RAM 的尺度布局回顾

机器模型里 ACT RAM 是一块只服务矩阵乘的私有存储（[isa.md L20-L23](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L20-L23)）：每行、每个 K 块（D 个元素，生产板卡 D=128）存放一个 fp32 行尺度 `Sa[r][k]` 和 4 个 8-bit 子块偏移 `da[r][k][b]`。4 对应常量 `NSUB = 4`（[quant.py L267](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L267)）：每个 D 块切成 4 个 D/4 子块，子块 b 的实际尺度是 `Sa * 2^-da`。ACT RAM 只由 QACT 写、只由 MM 读，软件没有第三条访问路径。

一条 QACT 写的若干块必须共享同一个 `Sa`——MM 每输出行只读 `Sa[j][ab]` 一次；模拟器在不一致时直接报错（[isa.md L225-L226](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L225-L226)）。

## 行量化公式：amax、S、inv 与 d_g

把一行 `x[0..n)` 量化（QACT 的组是 D/4 子块，QST 的组是整个 D 块；ROW 模式下所有 `d = 0`），契约给出的公式是：

```text
amax = max |x| over the row            （按冲洗后的位，与 RMAX 同源）
S    = amax == 0 ? 0 : amax * f32(1/127)        # 行尺度
inv  = amax == 0 ? 0 : 127 * recip(amax)
a_g  = max |x| over group g
d_g  = (a_g == 0 or ROW) ? 0
                     : min(31, e(amax) - e(a_g) - (f(a_g) > f(amax) ? 1 : 0))
q[i] = q8(x[i] * (inv * f32(2^d_g)))            # 组 g 内；两次舍入乘法
```

含义逐层看：行尺度 `S = amax/127`；`inv` 用的是硬件自己的近似 `recip` 而不是数学倒数；`d_g` 是满足 `a_g * 2^d ≤ amax` 的最大 `d`（上限 31），所以组 g 以 `S * 2^-d_g` 为尺度，落在它自身 `a_g/127` 的两倍以内——幅度小的组自动获得更细的量化台阶。注意 `q[i]` 是**两次舍入乘法**：先算 `inv * 2^d_g`（一次 fp32 舍入），再乘 `x[i]`（再舍入一次），然后才进 `q8`。`q8` 本身是 half-to-even 取整、饱和到 [-127, 127]、NaN 给 0（NaN 来自「0 乘无穷 inv」的情形）。

Python 侧的逐位模型是 [fp32.py 的 quantize_mx L297-L316](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L297-L316)，偏移计算在 `mx_offset`（[fp32.py L289-L294](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L289-L294)），完全按指数域 `e` 与尾数位 `f` 实现，不调用数学对数。

## QACT：字段与四个 flag

QACT 把 TMEM 行量化进 ACT RAM，构造器签名是 `qact(src, rows, ab, kb, srs, row=False, cscale=None, rscale=None, dup=False, ...)`（[isa.py L409-L420](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L409-L420)）：`src` 是 TMEM 源、`rows ≤ ACT_ROWS`、`ab` 是起始块号、`kb` 是每行块数、`srs` 是源行步长。语义见 [isa.md L269-L281](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L269-L281)，四个 flag 各有明确用途：

- **ROW（bit0）**：所有子块 `d = 0`，整行只用 `Sa` 一个尺度；
- **CSCALE（bit1）**：量化前每个元素先乘逐列尺度 `x = x * T[w4 + c]`；
- **RSCALE（bit2）**：再乘逐行因子 `T[w5 + r]`。两者同时置位时 `x = (x * r) * c`，恰好是 RMSNorm 的 `x * r * gamma`——一次向量遍历被折叠进量化器，不再产生中间 tile；
- **DUP（bit3）**：要求 `2*rows ≤ MCOLS`，把行 r 在同样的周期里复制到 ACT 行 r+rows，这是 MM PAIR 的操作数布局，详见 [10-pair-rsc.md](/concepts/10-pair-rsc.md)。

ol 侧的入口是 `ol.quantize(x, rscale=..., cscale=...)`，编译器还会把「无名临时量上的列乘」peephole 成 CSCALE（[language.py L79-L90](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L79-L90)）。

## QST：量化进 DRAM 字节

QST 把 TMEM 行量化后写入 DRAM（字节地址），构造器 `qst(src, dst, sdst, rows, kb, srs, drs, es, row=False, half=False, ...)`（[isa.py L423-L428](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L423-L428)），语义在 [isa.md L283-L297](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L283-L297)。它是全机唯一写字节的指令（DRAM 通常只接受 4 字节对齐的字访问）。两种尺度输出要分清：

- **ROW 模式**：每行只写一个 fp32 尺度字 `S` 到 `sdst + r*4`——这正是 MM RSC 需要的 K cache 尺度行（每 token 一个尺度）；
- **非 ROW 模式**：写完整 int8 scale 行：先一个字 `S`，然后每块一个 `d_k` 字节，按 4 字节补零，行长 `4 + 4*ceil(KB/4)`，可直接被 MM 当作 WF=0 的权重 scale 行读回。

板卡上 DRAM 以 64 字节为一个 beat：QST 只写了 beat 的一部分时，`otpu_native_dram` 会把整个 beat 读出、合并、整 beat 写回；scoreboard 把该 beat 的每个字都计作 QST 所写，且 QST 运行期间主机不得写同一 beat 的其他字节。**HALF（bit1，仅 ROW）**只写每行前半元素但尺度仍按整行算——服务 V^T 追加中「头宽只有填充行一半」的情形（LFM2 的头 64/128：写 64 个真行而非 128 个字节跨步行，无人读取的零填充就不必落盘）。

## Python 侧对应 API

主机端的镜像量化器与硬件同公式：[fp32.quantize_mx](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py#L297-L316) 返回 `(q, S, d)`；[quant.py 的 fake_act L672-L723](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L672-L723) 按 QACT/QST 的方式把激活反量化成 float64 并携带 `da`（`MXAct` 类型），连「距舍入平局 2^-31 以内」的边界都改调 fp32 模型处理，避免 float64 噪声扰动精确平局。validate 的 golden 正是用这套镜像在「设备量化点」每 128 个值做一次激活 round。本篇为静态源码阅读结论：未运行测试、未构建位流、未使用 FPGA。

## 相关概念

- [MM 指令与四列脉动 MXU](/concepts/06-mm-and-mxu.md)
- [权重格式族：int8/int4/FP4/NVFP4](/concepts/09-weight-formats.md)
- [PAIR 列复用、RSC K-cache 与 DUP](/concepts/10-pair-rsc.md)
