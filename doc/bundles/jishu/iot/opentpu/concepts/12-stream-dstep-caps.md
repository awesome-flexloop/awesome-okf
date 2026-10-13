---
okf_version: "0.2"
type: Concept
title: "STREAM/DSTEP 状态引擎、WAITW 轮询与 CAPS 能力位"
description: "DSTEP 与 STREAM 让 fp32 循环状态留在 DRAM 完成一步更新；WAITW 是卡等主机的轮询 fence；CAPS 寄存器公告每张位流支持哪些能力。"
tags: [openTPU, DSTEP, STREAM, WAITW, CAPS, stream-engine]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T17:00:00+08:00"
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

## 这三条机制解决什么问题

线性循环模型（Gated DeltaNet、Mamba2/SSD、GLA、RWKV 这一族）的核心是一个 fp32 状态矩阵 `St[rows, cols]`，每个 token 对它做一次「点积—门控—外积累加—再点积」的更新。用普通向量指令（VOP）做这件事，状态必须整块搬进 TMEM 再搬回 DRAM；而状态往往比 TMEM 大。**DSTEP（0x12）与 STREAM（0x13）让状态留在 DRAM，由 DMA 把行流式送过一条计算数据通路再原位写回，状态全程不进 TMEM。**

配套的两块基础设施是：**WAITW（0x07）**——卡上程序等待主机往 DRAM 写一个字的轮询指令，MoE 专家流用它做 fence；**CAPS 能力位**——每张位流启动时公告「我实现了哪些可选能力」，编译器和主机据此选择指令序列。本教程为静态源码阅读，未运行这些测试、未构建位流。

## DSTEP：一个 Gated DeltaNet head step

DSTEP 的语义在 [docs/isa.md L352-L384](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L352-L384) 与 [isa.py L195-L203](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L195-L203)。DMA 把行主序的转置状态（行是 value 维）逐行流过数据通路：

```text
kv = RDOT(St, k)              # 每行一次 isum_64 点积，与 VOP 同一个归约器
d  = MUL(SUB(v, MUL(kv, e)), beta)
St = OUTER(St, e, d, k)       # add(mul(St, e), mul(d(r), k(c)))，DRAM 中原位
o  = RDOT(St, q)              # 输出写 TMEM
```

关键点不是公式本身，而是契约：**DSTEP 与它所替代的 VOP 序列 `RDOT, MUL, SUB, MUL, OUTER(DSCALAR), RDOT` 逐位一致**，每次运算的舍入都同名同义（FTZ、两次舍入积加一次舍入加、`isum_64` 的 P=64 部分和折叠树）。这条等价性由测试 `tests/test_vops.py::test_dstep_is_the_vop_sequence` 钉住。形状约束为 rows 1..256、cols ∈ {64, 128, 192, 256}；flag bit0（ZERO）表示位置 0 的状态取 +0、不读旧状态。

板上 DSTEP 跑在 stream engine 上：DMA 搬状态，VPU 的 slot-0 部分和循环与折叠树做点积 A，尾部单元（[otpu_se_tail.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_se_tail.sv)）完成其余部分；每周期 8 个状态字。文档给出的作者报告估算：128×128 的 head 约 2048 周期数据通路加约 200 周期填充/排空，对应 1024 个 port-B chunk（各 64 KiB 读、64 KiB 写）。DSTEP 占用引擎期间 VOP 等待；只有 8-lane（W=8）构建含 DSTEP。

## STREAM：描述符编程的泛化

STREAM（0x13）把 DSTEP 这一固定形态泛化为「对一个流的每一行执行一遍四阶段程序」（[docs/stream.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/stream.md)、[isa.py L244-L329](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L244-L329)）：

- **REDUCE A**：`A = isum_64(S[r] * opA)`，opA 可以是列槽、行自身或常量，也可以取行最大值；
- **SCALAR**：每行至多 15 条短标量程序，操作 r0..r7、A、行标量 X[r]、常量 K0..K3、+0、+1；
- **MAP U**：`Y = S*G + D*B`（或 PASS/只乘/只加），即 OUTER 的原位更新；
- **MAP/REDUCE Q**：`O[r] = isum_64(Y * Q)`，或把标量寄存器直接作为行输出。

标量算子共 **11 种**（码 0-10）：`SC_ADD/SUB/MUL/MAX/MIN/MOV/RSQRT/RECIP/EXP2/LOG2/EXP2SUB`，复合函数复用 VPU 的两条长 lane，与 [fp32 数值契约](/concepts/04-fp32-contract.md)是同一套固定序列。

程序不编码进指令字，而放在 TMEM 里的**描述符**中。`StreamDesc.words()` 生成「5 个固定字 + 每个标量 op 一个字」，常量定义在 isa.py：

```python
STREAM_SLOTS = 4        # 4 个列槽，槽 i 位于 vec + i*cols
STREAM_MAX_OPS = 15     # 每行至多 15 条标量 op
STREAM_DESC_FIXED = 5   # 标量 op 之前的固定描述符字
STREAM_DESC_AREA = 64   # 编译器把描述符放在 TMEM 顶部 64 字驻留区
```

描述符字是 **float-safe** 的：`_fsafe()` 把 24-bit 载荷编码进指数域为 0x80 的正常 fp32（落在 [2, 4)），符号位携带载荷最高位，于是 VOP FILL 能把它原样精确写进 TMEM，不经过任何舍入。`gdn_desc(rows, cols)` 返回的描述符恰好就是 DSTEP——DSTEP 是 STREAM 取 Gated DeltaNet 描述符、`ks = gs` 的特例。ol 侧入口为 `ol.state_step / ol.deltanet_step / ol.has_dstep / ol.has_stream`，覆盖 Gated DeltaNet、DeltaNet、KDA、GLA、RetNet、Mamba2、mLSTM、RWKV-7 等模式。

## stream_hw_cfg：硬件子集裁决与 VOP 回退

ISA 模拟器运行 STREAM 的全部描述符空间，但 v1 硬件只实现一个子集。一份描述符能不能上板，由 [`stream_hw_cfg()`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L358-L378) 裁决：流必须在 DRAM（不能 SRC_T/DST_T/NODST）、rows ≤ 256、cols 为 64 的倍数且 ≤ 256、U 阶段必须是 `S*G + D*B` 形态、标量程序必须匹配四种状态步之一（`D_DELTA/D_DELTA1/D_SCALE/D_DOT`，门控为常量/列/1）。返回 `None` 时编译器（`ol.state_step`）**按同舍入语义改发一串 VOP**——程序不需要为不同位流维护两套。板子支持该子集由 CAPS bit26 公告；无 DSTEP/STREAM 引擎的位流把这两条当非法指令，run 以 ERROR 停止（修复前 DMA 会永远等一个不存在的引擎）。

## WAITW：等待主机写的字

WAITW 是「卡等主机」的唯一原语（[docs/isa.md L432-L486](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L432-L486)）。DMA 反复读 `v = M32[R[ra] + w1]`，直到 `cmp(v & w4, R[rc] + w3)` 成立，再把 v 的原始位写进 `T[R[rb] + w2]`：

- flags[1:0] 选比较：**0 EQ / 1 NE / 2 GE**；GE 是把 `(v & w4) - ref` 当有符号 32-bit 整数判 ≥0，因此计数器和正 fp32（正值的位序与数值序一致）可直接比较；
- `w5` 为两次读取间的周期数（首次立即读），`w6` 为超时周期（0 表示不超时）；
- 这个字不经过 VPU（避免被当非规格数冲洗），RLD 的 RAW 模式再把整 32 位地址取进寄存器；
- 超时时序器与各单元被按住复位，STATUS 显示 **HALTED + ERROR + WAIT_TO（bit8）**，TMEM/DRAM/ICOUNT 保持；首个 WAITW 位流（be824d5）只有 HALTED 与 ERROR。

**保序是它的全部意义。**主机先 h2c DMA 数据、再写 flag；卡先见 flag、再发年轻的 LD/MM。XDMA 与核在 `otpu_mem_ch` 和 LiteDRAM 交汇，这个顺序必须由硬件维持。生产位流曾缺少 port-A flush（直到 g2fix 0885d436）：WAITW 之后第一次 scale 读或新一次 run 的读，可能命中 DRAM 适配器为 MXU 读 run 保留的最后一拍旧数据——35B 模型连续 embed run 因此失败；修复让 WAITW 挂起时像 run 开始和程序载入一样冲掉 port A 的保留 beat。

这个顺序不是口头约定，而有专门的资格测试 [tools/qual/waitw.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/qual/waitw.py)（配合 `host/checks.py` 的 `waitw_host/waitw_tag/waitw_timeout`）：每轮主机先写旧数据和一个比较必失败的 flag，启卡确认它在等，再写新数据、最后写 flag；卡上 WAITW 之后的 LD 必须读到新数据（1..32768 字、任意字偏移，覆盖 EQ/NE/GE 与 masked EQ，轮询间隔 0/64/1000 周期，两个通道都放 flag）；另有「永不成立必须超时 ERROR、下一个 run 正常 HALT」与「flag 落在 1-4 MiB DMA 最后一拍」的 tag 轮次。模拟器中 `Machine.host` 钩子在所有可运行 slice 都进入等待时调用，模拟主机守护进程服务。

## CAPS：位流能力位体系

主机不能假设一张位流有什么——CAPS 寄存器（驱动定义见 [host/regs.py L40-L66](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/host/regs.py#L40-L66)）把可选特性公告出来：

| 位 | 能力 |
|---|---|
| bit6 | DSTEP（DMA 的 Gated DeltaNet head step） |
| bit25 | 运行参数 ARG0..ARG7（控制寄存器 0x60 起 8 个字，即每次 run 起点的 R8..R15） |
| bit26 | STREAM 引擎（运行 `stream_hw_cfg` 接受的子集；DSTEP 也跑在其上） |
| bit27 | LiteDRAM 主机校准通道（`otpu-memcal`/`memcal.ensure`；生产镜像启动时由核内小 CPU 约 12 秒自校准两通道） |
| bit31 | RTL WAITW（DMA 等主机写的字） |

同表还包括 bit4 四位权重、bit5 PAIR 列复用、bit7 CHASH 通道交织、bit24 ACT_ROWS、bit29 MX 数值（新旧数值互不兼容，配合 CFG_HASH 让主机拒绝错配位流）、bit30 卡上 decode 循环；完整位表在 docs/observability.md 的寄存器表。主机启动时经 `device_config` 读 CAPS 与 CFG_* 配置寄存器（切片数、TMEM/IMEM、ACT、DRAM、微结构、platform_id、架构哈希），模拟器侧则由 `Config.DSTEP/STREAM` 与 `board_config()` 的环境覆盖表达同一件事——同一套程序源码，靠能力位在「全 VOP 的旧位流」与「含状态引擎的新位流」之间自动落地。

## 相关概念

- [VOP 向量指令：20 个功能码、四种广播与归约/OUTER/ARGMAX](/concepts/07-vop-vpu.md)
- [主机软件栈：chat/serve、卡上批量与 MoE 专家流 offload](/concepts/13-host-stack-serve-moe.md)
- [指令系统：17 条指令、8×32-bit 字编码与寄存器约定](/concepts/02-instruction-set.md)
- [sequencer：顺序派发、WIN=16 足迹窗口与 HALT CHAIN 常驻程序](/concepts/03-sequencer-and-chaining.md)
- [openTPU 事实登记表 F-001~F-123](/references/facts.md)
