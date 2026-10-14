---
okf_version: "0.2"
type: Concept
title: "cosim 对拍：Verilator C++ 仿真器与 Python RV32IM ISS"
description: "285 行 C++ DUT 仿真器、318 行 Python ISS 与 112 行对拍器：全 RVFI trace 逐字段 diff、22% 随机反压与两段短路"
tags: [HWE Bench, cosim, Verilator, ISS, RVFI, CoreMark]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T16:20:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-14T19:30:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: hwe-facts
    resource: /references/facts.md
    title: "HWE Bench 事实登记表 F-001~F-126"
  - id: hwe-pinned
    resource: "https://github.com/FeSens/auto-arch-tournament/tree/4a137bb1378834ca3664a1c971684777eb5f364a"
    title: "HWE Bench 固定提交 4a137bb"
---

## 是什么：同一条指令流的两个实现必须吐出同一条退休流

cosim 门在 formal 之后回答另一个问题：符号 BMC 不证真实乘除与长程序行为，那就让 DUT 跑真实 ELF，与一个独立解释器逐条对拍退休记录。ALTOPS 替身下「错误乘法器也能过 formal」的缺口，在这一层由真实指令流的逐字段 diff 兜住（F-050、F-001）。

契约三件套都在 `test/cosim/`，同属 don't-touch 清单，agent 改不到（F-022、F-058）：

- [main.cpp](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L1-L59)（285 行）：Verilator C++ 仿真器。按 ELF program header 把可加载段灌进 imem/dmem（各 1 MiB），默认最多跑 50M 周期，每周期驱动核、处理总线反压/OOB/MMIO，并按 RVFI 通道吐出 JSON 退休流；写 0x10000000 的字符进 UART 捕获缓冲（F-058，亲验 L24-L29、L84-L95）。
- [reference.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/reference.py#L2-L24)（318 行）：纯 Python RV32IM ISS，内置九类陷阱纪律（保留 R 型、非法 funct3、JALR funct3≠0、非 EBREAK 的 SYSTEM、未知 opcode、misaligned 访存与跳转等）；trap 时 rvfi_trap=1、rd/mem 归零、npc=pc+4（F-058，亲验 L9-L22）。
- [run_cosim.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/run_cosim.py#L41-L100)（112 行）：驱动两侧、解析 JSON、逐字段 diff，输出 `{passed, divergence_at, insn, pc, field, expected, got}` 形态的失配报告（F-058、F-060，亲验 L36-L39）。

## 怎么实现：15 字段直比 + ALIGNED_MEM 归一

对拍器先对 **15 个直接相等字段**逐条比对：order/pc/npc/insn、rd 地址与值、rs1/rs2 地址与值、trap/halt/intr/mode/ixl（[run_cosim.py L48-L53](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/run_cosim.py#L48-L53)，亲验）。

trap/halt/intr/mode/ixl 也在直比之列是有意的：对拍器注释说明，这样核未来若开始误报 trap 或特权模式，分歧会立刻暴露，而不是藏在曾经忽略的字段里；ISS 侧固定报 mode=3（M 态）、ixl=1（RV32）（亲验 [run_cosim.py L44-L47](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/run_cosim.py#L44-L47)、[reference.py L133](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/reference.py#L133)）。

访存字段按 `RISCV_FORMAL_ALIGNED_MEM` 约定归一（亲验 [L56-L64](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/run_cosim.py#L56-L64)）：ISS 报原始字节地址与未移位宽度掩码（1/3/15），对拍器左移到字对齐位置后再比；掩码双方必须一致（这是「有没有访存」的唯一依据），地址只在掩码非零时比较，rdata/wdata 只比实际使能的字节（F-060）。退休条数不等或一侧没到 EBREAK 同样判失败。

main.cpp 侧严格按 NRET 契约排空：先 emit ch0 再 emit ch1，nret=1 构建时 `#if NRET >= 2` 整段不存在，JSON 流与双发前基线字节一致（亲验 [main.cpp L225-L250](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L225-L250)）；构建由 build.sh 的 `-DNRET` 宏区分单/双发（F-060）。

驱动侧两侧是对称的有限执行：ISS 由对拍器 `load_elf` 后逐条 `step()`，上限 1000 万条退休指令，遇不支持编码返回 `reference_invalid_or_unsupported_instruction`；DUT 侧按 50M cycle 上限跑 Verilator，完成条件是 rc=0、trace 非空且最后一条 insn 为 EBREAK（`0x00100073`）（亲验 [run_cosim.py L6-L34](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/run_cosim.py#L6-L34)）。任一侧先终止、两侧条数不等、或 harness 自身抛异常（JSON/超时/OS 错误）都各自给出独立失败分类，不混为同一字段（亲验 [run_cosim.py L89-L110](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/run_cosim.py#L89-L110)）。

## 为什么带 22% 停顿：诚实微架构数

main.cpp 注释自称「xorshift7 LFSR」（32 位状态、移位 13/17/5，低 7 位做判定，种子 0xDEADBEEF）生成总线反压：`(state & 0x7F) < 100` 即约 78% 接受、**约 22% 停顿**，imem 与 dmem 各一份，注释明确对标 VexRiscv 回归模型的 iStall/dStall（[main.cpp L48-L59](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L48-L59)，F-059）。这不是加噪声：零等待幻想总线上 V0 跑到「2.87 CM/MHz」，带停顿只有「2.21」——后者才是与 VexRiscv 公布的 2.30（iStall+dStall 口径）可比的诚实微架构数（**作者报告**，[fpga.py L45-L52](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L45-L52)，F-059）。fitness 评测固定传 `--bench --istall --dstall` 三个 flag（F-070）。

反压默认关闭：不传 flag 时 ready 恒为 1，普通 selftest 对拍不被无关停顿拖慢；只有 CoreMark fitness 路径显式打开两个 stall flag（亲验 [main.cpp L115-L120](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L115-L120)）。这也埋下后面 FPGA 一节要讲的测量口径缺口：仿真中的停顿网表与综合时的零等待夹具不是同一对象。

## 访存边界与 MMIO 计时括号

- 访存限定 `[0x0, 0x100000)`（1 MiB，`MEM_SIZE = 1u << 20` 与 sticky 标志见 [main.cpp L24-L27](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L24-L27)）加 UART/markers 窗口 `[0x10000000, 0x10000200)`（契约口径来自 [CLAUDE.md L17](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/CLAUDE.md#L17) 不变量 #6，F-062）：越界仿真器置 sticky `oob`，最终记录 `"oob":true`，eval 判失败，返回码 3；没跑到 EBREAK（撞 50M cycle 上限）返回码 2（亲验 [main.cpp L135-L141](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L135-L141)、[L267-L283](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L267-L283)）。
- CoreMark 经 0x10000000 UART 输出 banner；`start_time/stop_time` 写 `0x10000100/0x10000104`，仿真器只记录这对 MMIO 括号内周期，排除初始化与打印 CRC 的时间（F-062，亲验 [L32-L37](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L32-L37)、[L156-L161](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L156-L161)）。这对括号与 FPGA 门共用同一口径，见 [07-fpga-fitness](/concepts/07-fpga-fitness.md)。

OOB 检查是从真实漏洞补出来的：越界访存过去静默回绕（sim 与 reference 以同样方式别名到 `dmem[addr & 0xFFFFC]`），有效地址 bug 在对拍中完全不可见；现在 imem 越界、dmem 读 UART（该窗口只写）、非窗口写越界分别置 sticky 标志，UART 读返回 0 且两侧语义一致（亲验 [main.cpp L121-L141](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L121-L141)）。对拍器把 rc=3 翻译成带 `[oob_access detected during simulation]` 的失败（亲验 [run_cosim.py L13-L20](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/run_cosim.py#L13-L20)）。

还有一处时序细节与停顿模型直接相关：dmem 写必须在时钟上升沿**之前**处理。若在 posedge 后采样，dmem_ready 从 0 跳 1 那个周期被接受的 STORE 会随 EX/MEM 推进而丢失；带反压后这是必发竞态（亲验 [main.cpp L145-L155](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L145-L155)）。

## 两段短路与 canonical 2K 程序

[cosim.py L140-L171](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/cosim.py#L140-L171) 把 ELF 分两类短路（F-061）：① 除 coremark.elf 外的小 ELF（selftest 等）并行跑**全 trace 对拍**，任一失败立即返回；② coremark.elf 单独跑 CRC 校验门，仿真 timeout 600s（亲验 [cosim.py L80](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/cosim.py#L80)；小 ELF 120s）。`--bench` 模式下仿真器抑制逐条退休输出、只打印最后一条记录加完成标志 JSON（`ebreak`/`maxcycles_hit`/`oob`/`bench_bracketed`/`uart`），消费方必须先确认 `ebreak:true` 才信周期数（亲验 [main.cpp L252-L276](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/test/cosim/main.cpp#L252-L276)）。CoreMark 程序来自 `bench/programs/`：COREMARK_SIZE=2000、-O3、ITERATIONS=10 的 EEMBC canonical 2K 配置，配裸机 crt0.S（9 行）、link.ld（11 行）与 selftest.S（157 行），与 VexRiscv 等公开数同口径（F-063、F-064）；评测细节见 [08-coremark-measurement](/concepts/08-coremark-measurement.md)。

## 战绩与边界

v1 运行 9 个 broken 中 **5 个死于 cosim**：4 个 selftest.elf（r1s0/r3s0/r18s1/r22s1）+ 1 个 coremark.elf（r19s1）（F-065）。

selftest.elf 由 157 行手写 selftest.S 汇出，是全 trace 对拍的主负载——它小、确定、覆盖常规指令路径，适合在分钟级失败里给出精确分歧点；r1s0 那版「把 DIV/REM 移出单周期 ALU 路径」就倒在 selftest 对拍，两小时后改写为多周期 Cold DIV/REM 才成为 +15.7% 突破胜场（F-064、F-101）。失败群像见 [示例 02 失败样本集](/examples/02-failure-gallery.md)。

边界也写在代码里：ISS 是仓库随附的 318 行自研最小模型，docstring 明说「Mirrors the DUT's trap discipline」且改动需用户显式批准——它与 RTL 共享同一套 trap 假设，不是第三方独立黄金模型（F-058）；xorshift 只随机化 ready 反压时序，不随机化指令流（指令流来自固定 ELF，可用 `--seed` 换反压序列），因此它覆盖停顿交互、不覆盖随机指令序列。退休通道本身的焊死/顺序问题在进 cosim 前先由毫秒级 rvfi_lint 挡（F-066），见 [04-rvfi-nret-contract](/concepts/04-rvfi-nret-contract.md)；两层各管一段，不互相替代。

## 相关概念

- [riscv-formal 分层：ALTOPS 替身、检查数三口径与空过分类](/concepts/05-formal-altops.md)
- [FPGA 门：3-seed 中位数、fitness 公式与反常量折叠夹具](/concepts/07-fpga-fitness.md)
- [CoreMark 评测口径](/concepts/08-coremark-measurement.md)
