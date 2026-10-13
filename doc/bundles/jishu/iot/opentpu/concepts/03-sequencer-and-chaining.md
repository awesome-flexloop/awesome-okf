---
okf_version: "0.2"
type: Concept
title: "sequencer：顺序派发、WIN=16 足迹窗口与 HALT CHAIN 常驻程序"
description: "otpu_seq 按程序序派发并记录内存足迹依赖：WIN=16 是顺序窗口而非乱序；R15 起分配参数寄存器；HALT CHAIN 支撑常驻 decode"
tags: [openTPU, sequencer, 记分板, WIN, HALT CHAIN, 常驻程序, 寄存器分配]
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

## sequencer 在 RTL 中的位置

RTL 顶层分四块（[rtl/top/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/top)）：`otpu_top.sv` 实例化多个 slice；`otpu_slice.sv` 内含 seq+dma+mxu+vpu+存储；`otpu_coll.sv` 实现 GATHER/BAR 集合单元；`otpu_pkg.sv` 放参数包。派发逻辑全部集中在唯一的 seq 文件 [otpu_seq.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/seq/otpu_seq.sv)。

文件头注释把机制说得很直白：NOP、LI、ADDI、LOOP 在 sequencer 本地执行；其他指令解析完寄存器相对字段后，**按程序序（in program order）**连同其内存足迹一起派进一个有 WIN 个槽位的窗口（[otpu_seq.sv L1-L12](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/seq/otpu_seq.sv#L1-L12)）。

## WIN=16：顺序的足迹窗口，不是乱序发射窗

生产 target 的 `[uarch] WIN = 16`（[ypcb-00338.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/ypcb-00338.toml)；RTL 参数默认值同样是 16，四个 target 一致）。窗口内每个槽位记录三组信息（[otpu_seq.sv L243-L246](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/seq/otpu_seq.sv#L243-L246)）：

```systemverilog
logic [NUNITS-1:0] soh [WIN];   // 该槽归属哪个执行单元（one-hot）
logic [WIN-1:0]  sdep [WIN];    // sdep[i][j]：槽 i 等待槽 j（TMEM/DRAM/ACT 依赖）
logic [WIN-1:0]  sdepd [WIN];   // sdep 中只涉及 DRAM 的部分（供 MXU 流启动）
```

派发时，新指令把自己与所有在飞指令在 TMEM/DRAM/ACT RAM 区间上的 RAW/WAR/WAW 冲突登记进 `sdep`。派发规则有两条关键限定（[otpu_seq.sv L5-L12](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/seq/otpu_seq.sv#L5-L12)）：

1. 每个周期，每个空闲单元启动其**依赖已全部完成的最老**一条指令；一条与老指令冲突的指令永远不会先于老指令就绪，所以年轻的独立工作提前开始总是安全的；
2. **每个单元按启动顺序完成**。

因此单元之间可以自由重叠、互相填泡，但结果与严格顺序执行完全一致——这正是 [isa.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L25-L26)「每条指令全部写可见后下一条才开始」契约在微架构上的兑现方式。WIN=16 是**顺序窗口**：它只跟踪依赖、不重排指令，不能读作「16 项乱序发射」。

MXU 有两点特殊（[otpu_seq.sv L14-L17](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/seq/otpu_seq.sv#L14-L17)）：它严格按序启动指令，且分两阶段——DRAM 依赖一清就可以开始从 DRAM **流**（ustart，深度预取），等全部依赖清空才真正**消费**流（urel）。`sdepd` 单独切出 DRAM 依赖正是服务于此，使预取能与静态操作数的生产过程重叠。机器模型里说的「MXU 内部预取」到这里就落到了具体信号上。

## 参数寄存器：从 R15 往下长，release 归还

run 启动时 R8-R15 装主机参数 ARG0-ARG7（见 [01-machine-model](/concepts/01-machine-model.md)）。编译器的分配规则在 [compiler.py L111-L114](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L111-L114)：

```python
def arg_reg(k: int) -> int:
    """The register of a program's k-th run-time argument (Builder.run_args): from R15 down,
    as address registers are taken from R1 up."""
    return 15 - k
```

第 k 个不同的运行时量 `(var, c)` 占 R15-k，地址寄存器则从 R1 向上增长，两边在 16 个寄存器里相向分配。内核用完某个运行时值后调用 `ol.release(var)`（`Builder.release_arg`）归还其寄存器；编译器只在不搬运就会不够用时才复用/搬运寄存器，因此本来就放得下的程序指令位完全不变。RLD 则在运行时形成闭环：设备算出的 token 行地址等经 RLD 进寄存器，sequencer 用一个翻转的保持信号（rl_wait）暂停取指直到值回来（[otpu_seq.sv L18-L24](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/seq/otpu_seq.sv#L18-L24)）。

## HALT CHAIN：换程序但不结束 run

普通 HALT 等窗口排空后停片。带 flag bit0（CHAIN）的 HALT 则在排空窗口、所有 store 落地之后继续（[isa.md L488-L496](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L488-L496)）：

1. 从 DRAM **字节地址 R[ra]**（chunk 对齐，至多 IMEM 容量）载入 **R[rb] 条**指令到 IMEM；
2. 启动新程序：**R0-R7=0，R8-R15 装入主机新写的参数**；
3. **TMEM、ACT RAM、DRAM 内容全部保持**；
4. 板卡上 RUN 保持置位、CYCLES 继续计数、ICOUNT 把各段指令数累加，主机看到的仍是**一次 run**；重载只是程序加载器对新程序的一次 DRAM 读。

RTL 侧，HALT CHAIN 把 R[ra]（程序地址）与 R[rb]（指令数）随 halt 报告（ch_addr/ch_n），由 slice 完成重载与重启（[otpu_seq.sv L22-L24](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/seq/otpu_seq.sv#L22-L24)）。

## 常驻 decode 程序：主机每 token 只加零点儿毫秒

HALT CHAIN 让 decode 可以是一份**一次编译、常驻卡上**的程序：decode 按 attention bucket 推进，一个 bucket 的程序 CHAIN 到下一个 bucket 的程序。以 LFM2/Qwen3 的常驻 decode 为例（[README L120-L125](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L120-L125)，作者报告）：程序从寄存器读 position，自找 embedding/RoPE 行，**logits 在卡仍在运行时流式回传**；主机每 token 只增加 **0.17-0.30 ms**（omarchy；opentpu 主机为 0.45-1.3 ms）。

主机开销能压到这么低，靠的是三件事的合流：参数经 R8-R15 传入而不必重发程序、CHAIN 换段不产生 run 间往返、WAITW/mailbox 协议让主机只在专家缺失等少数时刻介入（见 [13-host-stack-serve-moe](/concepts/13-host-stack-serve-moe.md)）。

## 演进注记：WIN=32 → WIN=16

09-23 的 as-built 设计稿（docs/superpowers/specs/2026-09-23-opentpu-design.md）写的是「每周期一条指令进入 **WIN=32** 槽窗口」；生产 target 体系落地后统一为 **WIN=16**（同一文档中的 S=2/MCOLS=8 也已被生产点 S=1/MCOLS=4 取代）。读旧设计稿遇到 WIN=32 应理解为同一机制的早期尺寸选型：无论 16 还是 32，窗口都是顺序足迹记分板，不改变 ISA 可见语义。

## 相关概念

- [指令系统：17 条指令、8×32-bit 字编码与寄存器约定](/concepts/02-instruction-set.md)
- [主机软件栈：chat/serve、卡上批量与 MoE 专家流 offload](/concepts/13-host-stack-serve-moe.md)
- [机器模型：slice、三层存储与顺序完成语义](/concepts/01-machine-model.md)
- [openTPU 事实登记表 F-001~F-123](/references/facts.md)
