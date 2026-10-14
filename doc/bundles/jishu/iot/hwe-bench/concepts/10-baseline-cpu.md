---
okf_version: "0.2"
type: Concept
title: "baseline CPU 走读：5 级按序 RV32IM 种子核与 bench 冻结夹具"
description: "baseline 是 13 个 .sv 构成的通用 RV32IM 种子核；bench 夹具与它 12 文件哈希一致、只 core.sv 不同；三套口径数字不可混用"
tags: [HWE Bench, baseline, RV32IM, 流水线, bench fixture]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T16:40:00+08:00"
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

## 是什么：baseline 的定位是「通用种子」

baseline 不是某个最优实现，而是所有 fork 的起跑点。它的 core.yaml 自述为 "the universal seed for new cores"（[baseline/core.yaml L1-L4](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/baseline/core.yaml#L1-L4)）：**5 级按序 RV32IM、硬件 M 扩展、操作数前递与冒险检测；无分支预测、无 cache**（F-092）。「简单且诚实」是刻意选择——agent 的任何改动都要在这个朴素基线上证明自己，而不是在一团祖传复杂结构上做归因不清的调整。

## 怎么构成：13 个 .sv（本地镜像亲验文件名）

固定提交的 cores/baseline/rtl/ 下恰有 13 个 .sv（F-092，文件名本地镜像亲验），与 5 级流水一一对应：

| 文件 | 角色 |
|---|---|
| core.sv | 核顶层，I/O 契约（clock/reset、imem/dmem、NRET=2 RVFI）所在 |
| core_pkg.sv | 包定义（12 个 module 之外的第 13 件） |
| if_stage.sv / id_stage.sv / ex_stage.sv / mem_stage.sv / wb_stage.sv | 取指/译码/执行/访存/写回五级 |
| decoder.sv | 指令译码 |
| reg_file.sv | 寄存器堆 |
| imm_gen.sv | 立即数生成 |
| alu.sv | 算术逻辑单元（含 M 扩展操作路径） |
| forward_unit.sv | 操作数前递 |
| hazard_unit.sv | 冒险检测与停顿 |

agent 唯一可写面就是这些文件加 test/test_*.py，core.sv 的 I/O 契约是顶层不变量（F-021）。

## bench 夹具核：冻结的基准，只 core.sv 不同

bench 是另一个核目录，名字叫 **bench-fixture-v1**，core.yaml 显式声明 `nret: 1`（[bench/core.yaml L1-L4](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/bench/core.yaml#L1-L4)）：排行榜的每次克隆都从这个 orphan 夹具分支出发，且只操作这个目录（F-093）。本束用本地镜像对两目录 13 个 .sv 逐一做 SHA-256 比对，亲验结论与 F-093 一致：**12 个文件哈希完全相同，仅 core.sv 不同**（夹具版 core.sv 是 nret=1 的整宽连接，formal 侧对应 wrapper_si.sv，见 F-046）。

为什么要冻结夹具：基准跑分要回答「15 轮后比起跑线强了多少」，起跑线 RTL 必须在所有 rep、所有模型间逐位一致且不可被 agent 顺手修改。夹具由 orphan 提交+tag 成对重建、克隆时剥离成果（F-116），可靠性细节见 [16-harness-reliability](/concepts/16-harness-reliability.md)。

## v1 冠军核：16 个 .sv 与三个新增件

v1 是 73 假设运行活下来的冠军核，rtl/ 有 16 个 .sv（F-094）。相对 baseline 的 13 件，新增三件（文件名与职责本地镜像亲验）：

- [div_unit.sv L1-L16](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/rtl/div_unit.sv#L1-L16)：迭代式 DIV/DIVU/REM/REMU 单元，EX 级仅对这四条指令启动并冒泡 EX/MEM 直到 done，把冷除法移出单周期 ALU 结果路径——即 +15.7% 的 Cold DIV/REM 胜场的落点（F-101）；
- [store_slot.sv L1-L6](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/rtl/store_slot.sv#L1-L6)：单条目 pending-store 退休槽，只在 dmemReady 为低的合法对齐 store 到达 MEM 时分配，指令入队当拍照常经 MEM/WB 退休，槽位事后排空物理写；
- [00_core_pkg_first.sv L1-L9](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/rtl/00_core_pkg_first.sv#L1-L9)：不是微架构件，而是文件序兼容垫片——手工 lint 的裸 `rtl/*.sv` glob 在该文件系统上把 core.sv 排在 core_pkg.sv 前，它负责把包定义提前 include；正常有序构建命中宏守卫后它是 no-op。

v1 core.yaml 自述特性为 store-slot、hazard/forward、banked I-fetch replay predictor（F-094），九次胜场的完整时间线见 [11-v1-evolution](/concepts/11-v1-evolution.md)。

## 三套口径数字：务必对号入座（重点）

同一份 RTL 在固定提交里挂着三组不同身份的数字，引用时必须分清（均为作者报告）：

| 口径 | fmax MHz | LUT4 | FF | iter/s | CM/MHz | 身份与日期 |
|---|---|---|---|---|---|---|
| v1 log L1 历史基线哨兵 | 135.21 | 9880 | 1858 | 301.04 | ipc 字段 2e-06 | log.jsonl 74 行账本的 L1 哨兵（F-097），2026-04-28 运行开跑前的一次性测量（F-098） |
| baseline/core.yaml current | 127.03 | 9563 | 1866 | 282.82 | 2.2264 | 2026-07-16 retest，source baseline-retest，修正 2026-04-29 的陈旧一次性测量（F-095） |
| v1/core.yaml current | 198.69 | 5944 | 2235 | 577.76 | 2.9078 | source hyp-20260428-054-r20s2，2026-04-28（F-096） |

要点有三：

1. **V1 排行榜的对照基线 282.8 用的是第二行**：两个无 LLM 对照 fitness 均为 282.8±0.0，即夹具基线 282.82（F-110）；它不是 v1 历史运行出发时的 301.04。
2. v1 运行自身的「+92%」叙事以 301.04 为历史锚点（F-003/F-098），属于当时口径，不能拿 retest 后的 282.82 去重算作者结论。
3. 两份 core.yaml 的 **targets 字段是 `make loop` 的健身目标而非实测**：baseline 写 135/10000/300/2.2，v1 写 90/3000/400/4.5（F-095/F-096）；引用性能只能用 current 与日志实测。

## 边界与参照

baseline 的数字只有放进参照系才有意义：同 Gowin 流 synth-only 的 PicoRV32（0.516 CM/MHz）、Ibex（small 0.904）、NEORV32（0.9523）提供开源锚点，VexRiscv 以公布数 2.30/2.57 计分、同流仅用于面积（F-088/F-089），政策细节见 [13-v1-bench-methodology](/concepts/13-v1-bench-methodology.md)。本束所有数字为固定提交静态取证与作者报告，未在本地重跑综合。

## 相关概念

- [v1 进化史：9 个真胜场、63 次拒绝与 −73% 警戒线](/concepts/11-v1-evolution.md)
- [CoreMark 评测口径：canonical 2K、IPC 量纲与 holdout 五程序](/concepts/08-coremark-measurement.md)
- [V1 基准方法学：预注册 15×3、成本门限与参照核政策](/concepts/13-v1-bench-methodology.md)
