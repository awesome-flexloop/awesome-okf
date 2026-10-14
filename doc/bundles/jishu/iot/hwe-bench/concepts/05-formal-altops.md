---
okf_version: "0.2"
type: Concept
title: "riscv-formal 分层：ALTOPS 替身、检查数三口径与空过分类"
description: "循环内 formal 用 ALTOPS 替身只证旁路/路由不证真乘除；make -k、PREUNSAT 计数与 53/95+/~105 三口径的分层声明"
tags: [HWE Bench, riscv-formal, ALTOPS, 形式验证, BMC, bitwuzla]
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

## 是什么：循环内跑的是一套分层声明的形式验证

formal 门由 [formal/checks.cfg](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/checks.cfg#L1-L45) 配置，头部三行定下求解范围：`isa rv32im`、`nret 2`、`solver bitwuzla`（F-047）。检查由 run_all.sh 调 genchecks.py 对 RTL+wrapper 实时生成，约 45 个 I 基/M-ext 指令检查，再加 reg/pc_fwd/pc_bwd/causal/unique/cover/ill/liveness 等跨指令性质（F-054）。

BMC 深度表是有意配成短深度的（[checks.cfg L6-L22](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/checks.cfg#L6-L22)，F-048）：`insn 20`，reg/pc_fwd/pc_bwd/causal 为 BMC 10 + k-induction 20，unique 1/10/20，cover 1/20，ill 20，liveness 1/10/20；注释明说目标是暴露任意符号指令流**约 20 个周期内**的 bug。预注册方法学也确认循环内 formal 固定用 ALTOPS 快速模式（F-080）。

## ALTOPS：M 扩展的 XOR-of-add/sub 替身

`[defines]` 里同时打开 `RISCV_FORMAL_ALIGNED_MEM` 与 `RISCV_FORMAL_ALTOPS`（F-049、F-050）。ALTOPS 把 mul/div/rem 替换成 XOR-of-add/sub 的简单替身公式，让 bitwuzla 在 20 步 BMC 预算内解完；cfg 注释逐字声明它证明什么、不证明什么（[checks.cfg L26-L45](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/checks.cfg#L26-L45)）。关键在于 DUT 与 spec **共用同一替身**：错误的真实乘法器一样能过，所以真算术不能由这一层背书（F-050）。

| 性质 | ALTOPS 循环内 formal | 兜底手段 |
|---|---|---|
| M-ext 旁路与操作数路由（rs1/rs2→单元→rd） | ✓ 替身可证 | — |
| mul/div 的停顿/前递纪律 | ✓ | — |
| I 基算术与 trap 纪律 | ✓（替身只替换 M-ext） | cosim 与 ill 检查 |
| 真实 MUL/DIV/REM 位精确结果 | ✗ 双方共用替身 | test_alu.py（每 M-ext op 30+ 向量）、cosim 逐字段对拍、`make formal-deep`（每项数小时，周期外运行） |

兜底三件同样写在 cfg 注释里（F-050）；真算术由 cocotb `test_alu.py` 加 formal-deep 强制也是 CLAUDE.md 不变量 5b（[CLAUDE.md L16](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/CLAUDE.md#L16)）。

## 三份 cfg 与 ALIGNED_MEM

- [checks.cfg](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/checks.cfg#L24-L25)（67 行）：nret=2，ALIGNED_MEM + ALTOPS，循环内默认（F-049）。
- checks_si.cfg（40 行）：nret=1 的单发射版，同样开 ALTOPS（亲验 [L29](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/checks_si.cfg#L29)）。
- checks-deep.cfg（66 行）：nret=1、**无 ALTOPS**，`[defines]` 只有 ALIGNED_MEM（亲验 [L24-L25](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/checks-deep.cfg#L24-L25)），即 formal-deep 慢模式（F-049、F-050）。

ALIGNED_MEM 是 RVFI 的访存打包约定：地址字对齐、字节偏移编码进移位后的字节使能；cosim 对拍时也要做同一归一化（F-060），见 [06-cosim-iss](/concepts/06-cosim-iss.md)。

## run_all.sh：为什么必须 `make -j -k`

[run_all.sh](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/run_all.sh#L165-L200)（220 行）用 `make -j -k` 跑全部检查。`-k` 表示单检查失败后继续：NRET=2 下个别 `_ch1` 检查在单发射核上会 PREUNSAT 报错，没有 `-k` make 在首个错误就停，注释称「95+ checks never run」，只产出一份误导性的未建目录失败清单（F-051）。

计数规则分三档（F-052、F-053）：

1. 日志含 `DONE (PASS` 计 PASS；
2. 检查名以 `_ch1` 结尾且日志为 `Status: PREUNSAT`（rc=16）也计 PASS——valid_1 被 tie 0 时 ch1 BMC 假设不可满足，属性在空集上真空成立，是合法通过；双发射假设使假设可满足，此分支不再命中；
3. PASS+FAIL=0 时强制 FAIL 并记 `no_checks_generated`，防 genchecks 崩溃只产出一个空过任务。

## formal.py：53 口径、50 门槛与失败再分类

评测侧 [tools/eval/formal.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/formal.py#L1-L62)（246 行）再加两层闸门：

- docstring 给出基线口径：约 45 个 insn 检查加跨指令性质，**「53 total against the V0 baseline」**（F-054）。
- `EXPECTED_MIN_CHECKS = 50`（可由 `FORMAL_MIN_CHECKS` 覆盖）：V0 基线产 53，留 1-2 个余量给 cfg 合法微调，但拒绝只生成 1-2 个任务的半截 genchecks——旧规则 `passed>0 and failed==0` 会把崩溃后的单一真空通过误判为成功（F-055）。
- no_checks 再分类：输出若含 SBY DONE / engine status / make Error 任一模式，说明检查确实跑过、只是结果在 tally 前被清掉或中断，改判 `make_failed_during_execution` 而非 `no_checks_generated`（F-056）。

## 检查数三口径：引用必须带标签

formal 检查数在仓库里同时存在三个数（F-057，勘误 K-4 裁决）：

| 口径 | 数值 | 计数对象 |
|---|---|---|
| formal.py docstring | 53 | V0 基线生成的检查全集，也是闸值 50 的依据 |
| run_all.sh 注释 | 95+ | NRET=2 下 `make -k` 实际调度项 |
| README | ~105 checks at NRET=2 | NRET=2 含 ch1 与 PREUNSAT 项的对外说法（[README L198-L199](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/README.md#L198-L199)） |

K-4 裁决三者计数对象不同、同时为真，正文引用必须带口径标签，不得混用为「formal 有 N 条检查」（F-057）。

## 边界：V2 自曝的三门形式验证缺口

formal 通过不是布尔事实，V2 结果页明确披露三个正确性缺口、且均不改分（F-123）：① 取指地址越界长期无门，补写有界 formal 后 44 个设计过 36，其中 1 个 Opus 设计复位后第 9 周期在错误预测路径上从负地址取指（最终结果仍对），7 个大设计超时；② vendored formal 规格把**有符号 DIV/REM 按 unsigned** 计算，导致全算术检查对每个正确除法器都失败；③ 两个最终设计送 formal 的某块代码与综合/仿真版**异版**，换成综合版后「both pass all 53 checks」。它们正是「证明矩阵必须显式声明」与「formal 所消费源码应纳入指纹」的真实例证。

## 相关概念

- [RVFI NRET=2 契约：双通道退休顺序与不可焊死规则](/concepts/04-rvfi-nret-contract.md)
- [cosim 对拍：Verilator C++ 仿真器与 Python RV32IM ISS](/concepts/06-cosim-iss.md)
- [V2 演进与 E3 holdout](/concepts/15-v2-holdout.md)
