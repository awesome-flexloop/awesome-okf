---
okf_version: "0.2"
type: Concept
title: "V1 基准方法学：预注册 15×3、成本门限与参照核政策"
description: "HWE Bench V1 把自主研究循环变成跨模型基准：预注册固定配置、三结果类与配对统计、$200/rep 成本门限、参照核 citation_only 政策"
tags: [HWE Bench, 基准方法学, 预注册, 参照核, 统计口径]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T17:00:00+08:00"
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

## 它是什么：把自治循环冻结成一张实验台

BENCH_METHODOLOGY.md（251 行）是 HWE Bench V1 的预注册方法学：它规定「同一颗冻结夹具核、同一套门、同一组旋钮」下，让不同 LLM 系统各自跑完整场自治锦标赛，再用统一统计口径比较（F-080）。与「让模型写一段代码、跑一次测试」的基准不同，它测的是长程持续进步——默认每 rep 要经历 N=15 轮、每轮 K=3 个并行假设槽，共 45 个「假设-实现-全门评测」周期（F-081）。

方法学的冻结对象是**配置**而非结果：xhigh reasoning effort、成本上限、超时、formal 模式在开跑前写死，但不预设任何模型应当得到什么分数（F-080）。

## 预注册固定配置表

方法学 L33-L51 给出整张固定配置表（[BENCH_METHODOLOGY.md L33-L51](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/BENCH_METHODOLOGY.md#L33-L51)）：

| 参数 | 预注册值 | 代码出处 |
|---|---|---|
| 每模型 rep 数 J | 3 | runner CLI `--reps` 默认 3（F-020） |
| 轮数 N | 15 | runner CLI `--n` 默认 15（F-020） |
| 每轮槽数 K | 3 | runner CLI `--k` 默认 3（F-020） |
| reasoning effort | xhigh | `_runtime.py`（codex/opencode 拼装） |
| rep 墙钟超时 | 无（0=不封顶） | `DEFAULT_REP_TIMEOUT_SEC = 0`（F-019） |
| 每 rep 成本上限 | $200 硬上限 | `DEFAULT_MAX_COST_USD = 200.0`（F-019） |
| 实现代理超时 | 30 min | `CLAUDE_TIMEOUT_SEC = 600*3` = 1800s（F-029） |
| 假设代理超时 | 20 min | hypothesis 角色 1200s（F-028） |
| 循环内 formal | ALTOPS 快速模式；真 M 扩展算术走 `make formal-deep` | checks.cfg（F-050） |
| nextpnr 种子 | [1, 2, 3]，至少 2 个成功才计分 | fpga.py SEEDS / MIN_SUCCESSFUL_SEEDS |

规模口径因此是确定的：**15×3 = 45 个候选/rep**，加上每 rep 开头 1 次基线复测，per-rep 明细共 46 个 iter（F-081、F-112）。

## 三结果类与统计口径

每个候选槽只落入三类之一（F-082，[BENCH_METHODOLOGY.md L68-L82](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/BENCH_METHODOLOGY.md#L68-L82)）：

- `improvement`——fitness 严格超过轮前任冠军，快进合并为新冠军，每轮至多一个；
- `regression`——所有门通过但 fitness ≤ 冠军，worktree 丢弃；
- `broken`——某道门失败，按错误类再细分（formal_failed、cosim_failed、hypothesis_gen_failed 等）。

聚合与比较口径写在 L142-L153（F-083）：跨 rep 的 fitness 报 **mean ± std**，std 是纯 Python 实现的**总体标准差 pstdev**（无 scipy 依赖，report.py L143-L145）；模型与 static 对照按共享 rep 编号配对，做**双侧 Wilcoxon 符号秩检验**（正态近似加连续性修正、按惯例剔除零差），**n<5 时 p 报「—」**——零分布太稀疏，给不出有意义的 p 值，但表仍给出 n_pairs、mean/median Δ、W 与 treatment_wins 供判断效应量。

同一节埋着一条量纲勘误（K-5 相关）：log.jsonl 原始字段 `ipc_coremark` 存的是 iter/cycle 绝对值（基线哨兵实测 2e-06），乘 1e6 才是对外的 2.2264 CoreMark/MHz（F-083）。IPC 量纲的完整换算见 [08-coremark-measurement](/concepts/08-coremark-measurement.md)。

## 成本与时间门限

成本是硬代码门限而非建议：runner.py 的 `DEFAULT_MAX_COST_USD = 200.0` 是每 rep 的成本天花板（[runner.py L68-L71](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/bench/runner.py#L68-L71)，F-019）；rep 墙钟不设默认上限（`DEFAULT_REP_TIMEOUT_SEC = 0`），注释解释原 9h 上限会误杀 premium 模型上合法的 4-5h 长跑（F-019）。时间尺度（作者报告）：xhigh premium 模型每 rep 约 4-5h wall，11 个模型 × 3 rep 加对照串行约 **130-170h**（[BENCH_METHODOLOGY.md L234-L235](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/BENCH_METHODOLOGY.md#L234-L235)，F-091）。这一时间尺度也是可靠性工程（无人值守必然遇故障）的出发点，见 [16-harness-reliability](/concepts/16-harness-reliability.md)。

## 参照核政策：synth-only 同流数与 citation_only

bench/reference-cores.md 把参照核分两类处理（F-088、F-089）：

- **同 Gowin 流 synth-only**：PicoRV32（87c89a，ISC，0.516 CM/MHz）、Ibex（eede2fb，Apache-2.0，small 配置 0.904；上游另有 2.47/3.13 两档）、NEORV32（a0c202，BSD，VHDL，需 ghdl 插件，0.9523）（[reference-cores.md L5-L8](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/reference-cores.md#L5-L8)，F-088）。
- **VexRiscv（680756，MIT）标为 `citation_only`**：上游只有 Scala 源、无预生成 Verilog。作者同流测得 **3402 LUT4（CPU 核）/ 3957（含 bench wrapper）**、同流 P&R Fmax **128.58 MHz**（VexRiscvBench_report.json），但计分**只使用上游公布数**：2.30（full no-cache）与 2.57（MaxPerf@144 MHz），后者折合约 **370 iter/s** 人类参照线；同流数仅用于面积（[reference-cores.md L15](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/reference-cores.md#L15)，F-089）。站点图上的 370 线由 build.py 的 `VEXRISCV_REF`（fitness 370.0、lut4 3402）绘制（F-017）。

政策的含义是：自己流片口径只和自己流片口径比；缺 Verilog 的核不临时生成一份再跑分，避免「生成配置差异」被误记成性能差异。

## 文档漂移组：复现者必须以代码常量为准（K-3、K-5）

方法学与代码之间存在一组已登记的文档漂移，复现时不应照文档字面跑：

- **K-3（N/K 三套口径）**：BENCH 预注册 N=15/K=3，但同文示例命令两处写 `--n 10`（L218/L225）；Makefile 的 `N ?= 10`/`K ?= 1` 是交互式 `make loop` 的旋钮，不是基准配置。裁决：基准口径以预注册 **15/3=45** 为准，示例 `--n 10` 是文档笔误（F-013、F-081）。
- **K-5（三处 help/注释漂移）**：runner CLI 的 `--max-cost` help 文本误写 "(default $30)"，实际常量是 $200（[runner.py L1139-L1145](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/bench/runner.py#L1139-L1145)，F-020）；BENCH L59 把 fitness 公式引为 `fpga.py:247`，公式实际在 L274（F-074）；implement.py L11 同行注释写 "10 min watchdog"，实际 600*3=1800s=30 min（F-029）。

四处均按勘误留痕、不替上游静默修改；**复现实验一律以代码常量为准**。

## 边界与口径

- 预注册只锁配置，不锁结果；但 V1 实际执行并未跑满 J=3：多数模型只有 1-2 个完成 rep（榜首 Opus 为 n=1），导致配对检验 n_pairs 仅 1-2、p 值全部为「—」，统计功效不足以支撑细粒度排名（F-107、F-111）。排行榜应如何在这一约束下阅读，见 [14-v1-leaderboard](/concepts/14-v1-leaderboard.md)。
- 方法学的 fitness 口径（开源 nextpnr timer、CoreMark 单程序、报最佳 run）在 V2 被七项变更整体替换，V1/V2 数字不可直接比较（K-1），V2 的重建见 [15-v2-holdout](/concepts/15-v2-holdout.md)。
- 本文全部时间与费用预估均为「作者报告」，配置表为固定提交 4a137bb 的静态取证。

## 相关概念

- [V1 排行榜：16 模型、失败模式谱与两个对照的崩溃](/concepts/14-v1-leaderboard.md)
- [FPGA 门：3-seed 中位数、fitness 公式与反常量折叠夹具](/concepts/07-fpga-fitness.md)
- [CoreMark 评测口径：canonical 2K、IPC 量纲与 holdout 五程序](/concepts/08-coremark-measurement.md)
- [HWE Bench 事实登记表 F-001~F-126](/references/facts.md)
