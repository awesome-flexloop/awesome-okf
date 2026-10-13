---
okf_version: "0.2"
type: Concept
title: "PAIR 列复用、RSC K-cache 与 DUP：4-bit 满速技巧"
description: "4-bit 权重默认每周期只流一块、列一半闲置；PAIR 把奇 K 块映射到 M..2M-1 列，QACT DUP 复制行，RSC 让 K cache 尺度行只剩 Sw"
tags: [openTPU, PAIR, RSC, DUP, 4-bit, MXU, KV-cache]
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

## 4-bit 的列闲置问题

MXU 从 DRAM 读入的最小单位是 D 字节一个 chunk（生产板卡 D=128，即 128 字节）。对 int8，一个 chunk 正好是一个 K 块（128 个元素），每块流一个周期、阵列列全部用上。对 4-bit 格式（int4/FP4/NVFP4），两元素塞一字节，同一个 chunk 装的是**两个** K 块（块 2c 与 2c+1），而 MM 默认每周期只消耗一个块——于是一半阵列列在另一个周期空闲，4-bit MM 的峰值速率只有 int8 的一半。问题不是算力不够，而是喂不饱。

[docs/quant.md L15-L22](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/quant.md#L15-L22) 把两档说得很直白：默认两块两周期（MAC 宽度与 int8 相同）；列复用开启后一块一周期，每行 256 MAC/周期、128 颗 DSP 不变，速率翻倍。

## PAIR：奇 K 块映射到闲置列

MM flag bit6 `PAIR` 解决这个问题，语义在 [isa.md L257-L267](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L257-L267)，构造器约束在 [isa.py L394-L395](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L394-L395)。当操作数至多 MCOLS/2 行时，让闲置的列 M..2M-1 取奇块：

- 输出行 j 的**偶块**来自 ACT 行 j，**奇块**来自 ACT 行 j+M；
- 累加循环里体现为一行：`r = PAIR and k odd ? j + M : j`；
- 一个 chunk 的两块（2c、2c+1）在同一周期进入阵列，满速；
- 结果是**同一个整数**——PAIR 不改变输出的任何一位，它只改数据在列上的空间映射。

三条硬约束（isa.py 里直接 `_check`）：仅 4-bit 权重可用（`PAIR needs 4-bit weights`）；`2*M ≤ MCOLS`；`k0` 必须为偶数（`PAIR needs an even k0`）。后两条的原因在尺度读取上：一个 chunk 两块的尺度字是一起读的（WF1/2 为 8 字节，WF3 为 16 字节），所以 `ssa/srs` 要 8/16 字节对齐、入口块成对；KB 为奇数时最后一个 chunk 的第二块尺度字照读但丢弃。ACC、RMAX、ASCALE 语义不变，仍只写 M 行结果。

## QACT DUP：同周期复制操作数行

列 j+M 需要一份与行 j 完全相同的激活，这份复制由 QACT flag bit3 `DUP` 在量化时顺手完成（[isa.md L279-L281](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L279-L281)）：置位后（同样要求 `2*rows ≤ MCOLS`），行 r+rows 在**相同的周期**收到与行 r 相同的字节与尺度记录，不额外来一遍量化。这就是「PAIR 的操作数布局」。

编译器把这对 flag 一起决定，源码只有一行条件（[compiler.py L1422-L1424](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L1422-L1424)）：

```python
# 回放行（最多 ACT_ROWS 行）改为重流块：PAIR 不会更快
pair = self.cfg.PAIR and 2 * x.rows <= self.cfg.MCOLS
```

即目标配置开了 PAIR、且操作数行数不超过 MCOLS/2 时才用；QACT 发 `dup=pair`，MM 发 PAIR。大规模 MM（M>MCOLS/2）靠的是 MXU 对每 MCOLS 行组 replay 流数据（结果对 MCOLS/ACT_ROWS 透明），不走 PAIR。

## RSC：只有 Sw[n] 的 K cache 尺度行

第二个技巧是 MM flag bit7 `RSC`（[isa.py L250](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L250)、[isa.py L396](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L396)）。置位后 scale 行只有一个 fp32 字 `Sw[n]`，所有 `dw = 0、m = 1`——每 token 一个尺度，所以叫 K cache：`ol.kv_append` 追加 K 行时，对「一个头恰好一个 D 块」的 K 用 QST ROW 写 fp32 尺度（d=D 时 `rsc=True`），之后 attention 的 MM 以 RSC 读回（[language.py L355-L369](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L355-L369)、[compiler.py L390-L394](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L390-L394)）；更宽的 K 则写普通 int8 scale 行、当 int8 权重读。互斥约束只有一条：**RSC 不能与 NVFP4（WF=3）同用**（`MM: RSC does not take NVFP4`）。

## 生产 MCOLS=4 时这些技巧的实际意义

生产 target（ypcb-00338）是 MCOLS=4、ACT_ROWS=16，因此 PAIR 的适用面是 `M ≤ 2` 的 MM：单 token decode（M=1）与卡上小批量（M=2）正好命中，这正是 decode 带宽受限时 4-bit 提速 40-45% 能在卡上兑现的微结构前提；而 prefill 按 tile 成行（最多 ACT_ROWS=16 行），M>2 时编译器显式放弃 PAIR、改用 replay，语义不变只是不吃列复用红利。代价也有账：docs/quant.md 报告列复用在 xc7k480t 上的 Vivado 综合成本为 +4.6K LUT、+1.2K FF、+2 BRAM、不增 DSP（半速率 4-bit MXU 本身又比 int8 多约 2.2K LUT，作者综合报告）。配合 RSC，K cache 每 token 仅多一个 4 字节尺度字而非一整条块尺度行——两个技巧一省算力闲置、一省尺度流量，都是为「decode 每 token 流式读全部权重」这一口径服务的。本篇为静态源码阅读：未运行测试、未构建位流、未使用 FPGA。

## 相关概念

- [MM 指令与四列脉动 MXU](/concepts/06-mm-and-mxu.md)
- [量化器：QACT/QST、行尺度 Sa/da 与 q8 公式](/concepts/08-quantization-unit.md)
- [权重格式族：int8/int4/FP4/NVFP4](/concepts/09-weight-formats.md)
- [ol 内核语言与编译器](/concepts/11-ol-language-compiler.md)
