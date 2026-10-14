---
okf_version: "0.2"
type: Concept
title: "FPGA 门：3-seed 中位数、fitness 公式与反常量折叠夹具"
description: "Tang Nano 20K 上 yosys+nextpnr 三种子取中位 Fmax 乘 CoreMark IPC；LFSR/XOR 反折叠夹具与 tie-ready 契约缺口"
tags: [HWE Bench, FPGA, nextpnr, fitness, CoreMark, 反作弊, Gowin]
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

## 是什么：fitness 在真实器件上合成得出

FPGA 门是七门中最后、也最慢的一门：每个候选综合布局布线到 Gowin **GW2A-LV18QN88C8/I7**（Tang Nano 20K 开发板），用真实时序 Fmax 乘 CoreMark 效率得 fitness（F-067）。脚本三件为 synth.tcl（44 行，synth_gowin）、nextpnr_run.sh（31 行，器件名在亲验 [L20](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/fpga/scripts/nextpnr_run.sh#L20)）与 4 行 CST 约束（F-067）。评测器是 [tools/eval/fpga.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L30-L56)（311 行），core_bench 顶层夹具在 `fpga/core_bench.sv`（150 行）。

夹具随 nret 路由：核声明 nret=1 时改用 93 行的 core_bench_si.sv（亲验 [fpga.py L25-L28](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L25-L28)），与 formal wrapper、cosim 宏共用同一个 core.yaml 字段（F-046）。门内顺序是先求 3-seed Fmax 中位数、再跑 CoreMark 求 iter/cycle；CoreMark 未完成（CRC 不符、超时、OOB）直接返回 `bench_failed`，不产 fitness（亲验 [fpga.py L262-L272](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L262-L272)）。

## 3-seed 中位数与 placement_failed

`SEEDS = [1, 2, 3]`：每候选跑 3 个 nextpnr 种子，Fmax 取三者中位数；README 原话是 **「One seed is a coin flip; three is comparable across rounds.」**（**作者报告**，[fpga.py L30](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L30)、[README L202-L204](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/README.md#L202-L204)，F-068）。

选中位数而不是最佳值，是因为单种子 Fmax 是掷硬币：取 max 等于奖励运气、放大布局噪声，中位数才使跨轮分数可比（F-068、F-073）。`MIN_SUCCESSFUL_SEEDS = 2`：3 个种子至少 2 个布局成功才给分，单幸存者的中位数不被承认，直接判 `placement_failed`（F-071）；nextpnr 非零退出（[nextpnr_run.sh L8](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/fpga/scripts/nextpnr_run.sh#L8) 开 `set -eo pipefail`，防 tee 掩盖非零退出）或解析不到 Fmax 也算失败，防止半成品运行打印的频率行计分（亲验 [fpga.py L89-L92](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L89-L92)）。v1 运行的 4 个 placement_failed 全部是 structural 类存储结构尝试（F-103），见 [11-v1-evolution](/concepts/11-v1-evolution.md)。

## CoreMark 自校：五 CRC 常量与固定 flags

评测器不信核上打印的结论，自行复核 UART 输出中的五个 canonical 2K 配置 CRC（F-069）：seedcrc `0xe9f5`、crclist `0xe714`、crcmatrix `0x1fd7`、crcstate `0x8e3a`、crcfinal `0xfcaf`，注释称与 VexRiscv 预编译 coremark_rv32im.bin 核对一致（[fpga.py L33-L44](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L33-L44)）。仿真 flags 固定 `--bench --istall --dstall`，即与 VexRiscv iStall/dStall 同口径的约 22% 反压（F-070、F-059）。计时只认 MMIO start/stop 括号内周期，warm-up 与 printf 时间排除在外（F-062）。

之所以要自校，是因为 CoreMark **即使结果错误也会打印「Correct operation validated.」**——它检查自己的 CRC 后照常输出该字面量（F-078，[README L205-L207](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/README.md#L205-L207)）。评测器还从 core_portme.h 正则读 ITERATIONS 而不自带副本，读不到就报错，保证换算 iter/cycle 用的迭代次数与 ELF 实际编译值不脱节（亲验 [fpga.py L58-L66](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L58-L66)）。

## Fmax 取值与 fitness 公式

- Fmax 取 nextpnr 输出中**最后一条** 「Max frequency」：中间估计可能悲观（布线前）或乐观（布局前），最终布线后值才权威（F-072，[fpga.py L82-L87](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L82-L87)）。
- 公式在 [fpga.py L262-L296](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L262-L296)：`fmax_median = statistics.median(all_fmax)`，`fitness = fmax_median * iter_per_cycle * 1_000_000`（CoreMark iter/sec）；返回值 fmax/ipc/fitness 分别 round 2/6/2 位（F-073，公式在亲验 L274）。
- 勘误 K-5 留痕：BENCH_METHODOLOGY.md L59 把公式位置引为 `fpga.py:247`，实测 L246-L247 是 seed_results/successful 行，公式在 L274——以代码常量为准，不替上游静默改文档（F-074）。

## 解析失败大声报错：假失败优于假通过

LUT4/DFF 从 nextpnr 日志正则解析；解析失败**永不替 0**（F-075，[fpga.py L277-L291](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/fpga.py#L277-L291)）。理由是非对称的：设了 LUT 目标时 0 LUT4 是最佳面积分，日志格式漂移若静默替 0，每个假设都会「获胜」——那是假通过；大声报 `fpga_report_unparsed` 只是假失败。这种「假失败优于假通过」的故障方向设计呼应 [洞察 I-6](/references/insights.md)，系统分析见 [16-harness-reliability](/concepts/16-harness-reliability.md)。

## core_bench.sv 的反常量折叠三件

综合夹具不是可部署 SoC，而是专门防综合器优化掉被测对象（F-076、F-077）：

1. **直驱 core，不接零初始化 BRAM 的 SoC**：否则 Yosys 从全零指令推出「永远退休非法指令 0」，常量折叠剪掉约 99% 逻辑，Fmax 与真实关键路径无关（[core_bench.sv L1-L18](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/fpga/core_bench.sv#L1-L18)）。
2. **32 位 Fibonacci LFSR 驱动 io_imemData**：复位种子 `32'h1`，taps 为 `[31]^[21]^[1]^[0]`，任意非零种子满周期，迫使 decoder/ALU/比较器/前递 mux 全部留在网表里（亲验 [L29-L34](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/fpga/core_bench.sv#L29-L34)）；dmem 保留 8 KiB 字节使能 BRAM，使读路径映射贴近部署形态。
3. **全部 CPU 输出 XOR-reduce 到单个 LED 位**：否则死输出消除会把 RVFI fan-out 与大部分流水寄存器当不可见逻辑剪掉（亲验 [L134-L148](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/fpga/core_bench.sv#L134-L148)）。

## 边界（重点）：tie-ready 的 fitness 契约缺口

同一夹具仍有一处作者实测并公开记录的缺口（**作者报告**日记，F-079）：core_bench 把 `io_imemReady`/`io_dmemReady` tie 成 `1'b1`（亲验 [L83-L89](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/fpga/core_bench.sv#L83-L89)），因为器件上是 1 周期 BRAM；但周期数来自带 22% 反压的 Verilator 仿真。于是**「只在 ready 为低时作用」的停顿逻辑被常量折叠出时序网表**：周期收益照计，面积与时序成本为零。

实例是 Opus run 的 r9s1（已接受，fitness 695.16，commit ed49aaf）：一个 4096 项 I-side replay store 与 r7s0 网表等价——LUT4 3078 vs 3080、Fmax 222.1 vs 219.2 MHz（**作者报告**）。它不违反任何规则：只改了 rtl/ 与测试、全门通过；这是**每个模型都可利用的 fitness 契约缺口**，接受规则挡不住测量装置自身的漏洞（F-079）。

值得注意的是发现方式：它不是被某道门拦下的，而是作者比对两次接受设计的网表等价性时从日记里挖出的，且作者明说任何分数中多少比例来自该缺口「unmeasured」（F-079）。这说明防作弊措施只能挡住已知攻击面，夹具自身的口径矛盾需要独立审计；接受规则的质量上界由测量契约决定（[洞察 I-2](/references/insights.md)），见 [09-accept-rule-outcomes](/concepts/09-accept-rule-outcomes.md)。

后续修复方向也有据可查：V2 的七项变更之一正是把停顿生成器纳入被计时电路，使周期收益与面积时序成本落在同一网表（F-124）；V1/V2 数字因此被官方明示不可比。

## 相关概念

- [cosim 对拍：Verilator C++ 仿真器与 Python RV32IM ISS](/concepts/06-cosim-iss.md)
- [CoreMark 评测口径](/concepts/08-coremark-measurement.md)
- [接受规则与三结果类](/concepts/09-accept-rule-outcomes.md)
- [harness 可靠性工程](/concepts/16-harness-reliability.md)
