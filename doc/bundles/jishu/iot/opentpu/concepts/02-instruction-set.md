---
okf_version: "0.2"
type: Concept
title: "指令系统：17 条指令、8×32-bit 字编码与寄存器约定"
description: "17 条 opcode 全表与分组、8×32-bit 编码与 w0 位段、LOOP/RLD/BAR/GATHER 语义，及编码表 16 行与 STREAM 专节"
tags: [openTPU, ISA, 指令编码, opcode, RLD, 寄存器约定]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T16:00:00+08:00"
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

## 17 条指令：按功能点的五组

openTPU ISA v1 一共 **17 条指令**，opcode 常量在 [isa.py L8-L17](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L8-L17)，语义表在 [isa.md L160-L177](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L160-L177)。按 opcode 区段分成五组：

| 组 | opcode | 指令（17） |
|---|---|---|
| 控制（8） | 0x00-0x07 | NOP、HALT、LI、ADDI、LOOP、BAR、RLD、WAITW |
| 访存/状态（4） | 0x10-0x13 | LD、ST、DSTEP、STREAM |
| 矩阵/量化（3） | 0x20-0x22 | MM、QACT、QST |
| 向量（1） | 0x30 | VOP（20 个功能码，见 [07-vop-vpu](/concepts/07-vop-vpu.md)） |
| 集合（1） | 0x40 | GATHER |

```python
NOP, HALT, LI, ADDI, LOOP, BAR, RLD, WAITW = 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07
LD, ST, DSTEP, STREAM = 0x10, 0x11, 0x12, 0x13
MM, QACT, QST = 0x20, 0x21, 0x22
VOP = 0x30
GATHER = 0x40
```

这段定义逐字摘自 [isa.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L8-L12)。注意指令数是 **17**，不是 16：VOP 一条指令内部再用功能码区分 20 个向量操作，而 DSTEP/STREAM 是两条独立 opcode。

### 为什么 docs 编码表只有 16 行

[isa.md 的编码表](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L160-L177)逐行列出 16 条：0x00-0x07 八条、0x10-0x12 三条（LD/ST/DSTEP）、0x20-0x22 三条、VOP、GATHER。**0x13 STREAM 不在表里**，它在文档后面的独立专节 "STREAM"（[isa.md L386-L414](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L386-L414)）中定义，因为它带有一个 float-safe 的 TMEM 描述符，字段与定长立即数模型差别较大。所以「16 表格行 + STREAM 独立专节 = 17 opcode」，两种数法都对，指的是同一套 ISA。

## 8×32-bit 字编码与 w0 位段

每条指令固定 **8 个 32-bit 字 `w0..w7`**。w0 打包操作码、四个寄存器字段和 flags，w1-w7 是各指令自定义的立即数（[isa.md L154-L158](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L154-L158)）：

```text
w0 = opcode[7:0] | ra[11:8] | rb[15:12] | rc[19:16] | rd[23:20] | flags[31:24]
```

寄存器字段只放寄存器编号；地址一律是「寄存器 + 立即数」即 `R[x] + w`。而**计数、形状、步长永远是立即数**，与寄存器字段里装了什么无关——例如 LD/ST 的字数 n、QACT 的 w2/w3、GATHER 的 w3。这样编码只有 256 bit、没有变长扩展，解码逻辑一周期可读。

寄存器越界在 Python 侧是硬错误。`Instr.encode()` 编码前检查（[isa.py L77-L83](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L77-L83)）：

```python
_check(all(0 <= r < 16 for r in (self.ra, self.rb, self.rc, self.rd)),
       f"{OPNAMES.get(self.op, self.op)}: a register field outside R0..R15")
```

`_check` 抛 `ValueError` 而不是 `assert`，注释解释了原因：`python -O` 下 assert 会被删掉，导致坏字段被静默截断进指令字（[isa.py L99-L103](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L99-L103)）。

## 控制类八条怎么协作

- **LI/ADDI**：`R[rd] = w1`、`R[rd] = R[ra] + w1`，寄存器侧仅有的整数运算；地址靠它们在循环外初始化。
- **LOOP**：函数式硬件循环。body 是随后 `w1` 条指令，执行 `R[ra] + w2` 次，计数为 0 则跳过；**嵌套深度 4**（RTL 里就是 4 级循环栈）。约束：内层 body 不能与外层 body 在同一条指令上结束（[isa.md L166](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L166)）。
- **BAR**：等待所有 slice 都到达同一条 BAR，是跨片栅栏（[isa.md L167](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L167)）。
- **HALT**：停止本 slice；flag bit0 为 CHAIN 时不是结束而是**换程序继续跑**——排空窗口、落盘 store、从 DRAM 载入新程序，主机视角仍是一次 run。这是常驻 decode 程序的机制基础，细节集中在 [03-sequencer-and-chaining](/concepts/03-sequencer-and-chaining.md)。
- **WAITW（0x07）**：让 DMA 轮询主机写入 DRAM 的一个字，掩码比较（EQ/NE/GE）成立后取走，支持间隔与超时，超时以 HALTED+ERROR+WAIT_TO（bit8）停下。MoE 专家流用它做 fence 与槽位标签，语义较长，见 [12-stream-dstep-caps](/concepts/12-stream-dstep-caps.md)。

## RLD：设备算出的值回到寄存器的唯一通道

`RLD` 做 `R[rd] = f2i(T[R[ra]+w1])`，是设备计算结果到达**地址、循环计数、条件判断**的唯一途径（[isa.md L416-L430](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L416-L430)）。两个 flag：bit0 RAW 直接取 32 位原始位（不经 fp32→整数转换）；bit1 MUL 再乘 `R[rb]+w2` 取低 32 位——例如把 token id 乘上 2.4 GB embedding 表的行字节跨距 9344，整数地址由此产生。

`f2i` 向零截断，边界行为在 [isa.py L167-L178](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L167-L178) 写死：

- `|x| < 1`（含 ±0 与被冲洗的非规格数）→ 0；
- `|x| ≥ 2^31`、±inf、NaN → `0x80000000`；
- **不超过 24 个有效位的整数精确转换**（fp32 的整数精确表示范围）。

RLD 在记分板上被当作一条单元指令派发，值未回来前暂停取指，年轻指令才能安全使用该寄存器。

## 访存、状态与集合指令

- **LD/ST**：DRAM↔TMEM 的字搬运，字数与双方偏移都是立即数；字地址必须 4 字节对齐。
- **DSTEP（0x12）/STREAM（0x13）**：由 DMA/stream engine 对**留在 DRAM 内的 fp32 状态**做递推步（如 Gated DeltaNet 的 head step），状态不进 TMEM；DSTEP 是 STREAM 取固定描述符 `isa.gdn_desc` 的特例，语义与 VOP 序列 RDOT,MUL,SUB,MUL,OUTER,RDOT 逐位一致。能力位与回退规则见 [12-stream-dstep-caps](/concepts/12-stream-dstep-caps.md)。
- **GATHER（0x40）**：all-gather。所有 slice 必须以**相同的 dst、rows、cols、drs、seg** 执行；每片把自己的分片写入**所有片**的 TMEM，源区间与目的区间不得重叠（[isa.md L498-L505](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L498-L505)）。
- **MM/QACT/QST** 三条承载矩阵乘与量化，字段众多（WF 权重格式、PAIR、RSC、CSCALE 等），分别在 [06-mm-and-mxu](/concepts/06-mm-and-mxu.md) 与 [08-quantization-unit](/concepts/08-quantization-unit.md) 展开。

## 相关概念

- [sequencer：顺序派发、WIN=16 足迹窗口与 HALT CHAIN 常驻程序](/concepts/03-sequencer-and-chaining.md)
- [MM 指令与四列脉动 MXU：48-bit 精确累加、epilogue 与 replay](/concepts/06-mm-and-mxu.md)
- [VOP 向量指令：20 个功能码、四种广播与归约/OUTER/ARGMAX](/concepts/07-vop-vpu.md)
- [STREAM/DSTEP 状态引擎、WAITW 轮询与 CAPS 能力位](/concepts/12-stream-dstep-caps.md)
- [openTPU 事实登记表 F-001~F-123](/references/facts.md)
