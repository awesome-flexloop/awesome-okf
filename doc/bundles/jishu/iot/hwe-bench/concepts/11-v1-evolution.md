---
okf_version: "0.2"
type: Concept
title: "v1 进化史：9 个真胜场、63 次拒绝与 −73% 警戒线"
description: "log.jsonl 74 行机械复算：73 假设 9 胜 51 回归 9 broken 4 placement；同一想法两度、K-2 计数勘误与 9h51m 时间线"
tags: [HWE Bench, v1, 进化史, log.jsonl, 机械复算]
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

## 是什么：log.jsonl 是一本可机械复算的账本

v1 运行的全部历史不在叙述文章里，而在 [cores/v1/experiments/log.jsonl](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L1-L74)：**74 行、603,222 字节 = 73 个真假设 + L1 一行基线哨兵**（F-097，字节/行数本地镜像亲验一致）。每行是一条按失败深度异构的账本：结果字段名为 `outcome`、变化字段名为 `delta_pct`；全表并集 26 个字段，跑完全门的行 25 个、L1 哨兵 22 个、broken/placement 行 10-14 个（F-097）；id 带 rNsM 轮槽后缀（正则见 F-024），与 git 提交可互相关联。L1 哨兵即 "Baseline retest (no implementation change)"，id hyp-20260427-001、outcome=improvement、fitness 301.04、fmax 135.21、lut4 9880、ff 1858、ipc_coremark 2e-06（F-098）；其 seeds 数组 [121.29, 135.21, 136.07] 的中位数正是 135.21，直观展示 Fmax 取 3 种子中位数的规则。

## 九连胜时间线（日志实测，作者报告）

73 个假设中只有 9 个真实架构胜场。下表 fitness/delta 取自 F-100，fmax 为 pinned 日志各行三种子中位数值（本地 Python 解析亲验）：

| 槽位 | 想法 | fmax 中位数 | fitness | delta | 行 |
|---|---|---|---|---|---|
| r1s2 | Backward-Branch Taken Predictor | 134.93 | 313.10 | +4.01% | [L4](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L4) |
| r2s2 | IF Direct-Jump Predictor | 138.22 | 324.48 | +3.63% | [L7](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L7) |
| r6s0 | Cold Multi-Cycle DIV/REM Unit | 159.92 | 375.43 | +15.7% | [L17](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L17) |
| r8s1 | One-Deep Store Retirement Slot | 168.01 | 397.55 | +5.89% | [L24](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L24) |
| r11s0 | Segmented RVFI Order Counter | 178.67 | 422.77 | +6.34% | [L32](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L32) |
| r12s2 | Registered Lookahead I-Fetch Replay | 163.61 | 472.96 | +11.87% | [L37](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L37) |
| r13s0 | Compressed Resetless Replay Tags | 174.92 | 505.65 | +6.91% | [L38](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L38) |
| r17s0 | RTL-Only Hot/Cold ALU Opcode Split | 183.12 | 529.35 | +4.69% | [L50](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L50) |
| r20s2 | Banked Registered I-Fetch Replay | 198.69 | 577.76 | +9.15% | [L61](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/cores/v1/experiments/log.jsonl#L61) |

F-100 特别注明：日志 fmax 是中位数值，与 README 取整表略有差异；README 的「10 个接受胜场」表列 Δt/iter/s/CM/MHz/Fmax/Hypothesis 而**无 LUT 列**，博客同名表额外带 LUT4 列（F-004）。引用 LUT 时须标明取自博客表（如 5,888/5,944）。

## 同一想法两度：r1s0 死，r6s0 成为突破

九连胜中最大的一跳来自一个**先死后生**的想法（F-101）：r1s0 "Move DIV/REM off the single-cycle ALU path" 在 selftest cosim 就死了（L2），从未见到 FPGA；约两小时后，同一想法改写为 r6s0 "Cold Multi-Cycle DIV/REM Unit"——想法不变、实现修复——成为 +15.7% 的突破胜场（L17），还意外让 LUT 从约 10k 降到 5888（F-101）。作者评注：agent 事先并不知道这会同时砍掉一半 LUT，"It found out by doing it and watching the synthesizer."。完整故事见 [/examples/00-cold-div-reincarnation.md](/examples/00-cold-div-reincarnation.md)，落地 RTL 即 v1 的 div_unit.sv（见 [10-baseline-cpu](/concepts/10-baseline-cpu.md)）。

## 拒绝分类学：64 个非胜场去了哪里

机械解析 73 假设的结局分布为 **improvement 9、regression 51、broken 9、placement_failed 4**（F-099），类别分布 structural 25 / micro_opt 24 / predictor 24（memory/extension 未使用，F-099）。三类拒绝各有账本：

- **51 条 regression**：门全过但分数不升。最差三条为 r24s2 −73.25%（154.53）、r9s1 −58.19%（166.23）、r5s0 −48.61%（166.75），formal_passed 与 cosim_passed 均为 True（F-104/F-105），拦截机制见 [09-accept-rule-outcomes](/concepts/09-accept-rule-outcomes.md)。
- **9 条 broken**：cosim selftest 4（L2/L8/L54/L66）、cosim coremark 1（L57 r19s1）、沙箱越权 3（L11/L26/L71，均为试图新增白名单外的 test/_helpers.py，F-044）、schema 1（L19 r6s2，fitness_delta_pct 填 1.5 违反 integer，F-102）。
- **4 条 placement_failed**：全部是 structural 类存储结构尝试（r3s1/r15s1/r16s1/r24s1，F-103）。

## K-2：到底是 10/50 还是 9/51

博客结局表写 10 accepted / 50 regression（[blog L31-L36](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/docs/auto-arch-tournament-blog-post.md#L31-L36)），机械复算为 9/51/9/4：差异来自 L1 基线哨兵 outcome=improvement——博客把哨兵计入胜场（故「10 个接受的胜场」含 0.0h 的 Baseline 行），同时回归少计 1（F-099、K-2）。裁决口径：**真实架构胜场为 9 个**；README 的 "63 were rejected" 是约数叙事（73−9=64，K-2）。引用计数以日志机械解析为准。

## 增益归因与时间线（作者报告）

作者对 +92% 的归因分解（博客口径，F-090）：370→578 iter/s = **+56% vs VexRiscv 人类线**；其中约 **13 个百分点来自架构效率**（2.91 vs 2.57 CM/MHz），其余来自 Fmax（199 vs 144 MHz）——一个更小、更简单、综合器还能给更高频率的设计（F-003/F-090）。头条数字（73 假设、9h51m、301→577 iter/s、比 VexRiscv 公布 2.30 高 +26%、LUT 少 40%）均为作者报告（F-003）。

时间线（F-106，时间戳本地解析亲验）：L1 落 2026-04-28T02:16:49Z，末个假设 L73 落 12:08:33Z，跨度约 **9h51m**；全表最后一行 L74 落 13:30:43Z（合计约 11h14m，末行为收尾记录）。

## 边界与读史方法

- 本页全部计数与表内数字的正确读法是**用 Python json 全量解析 log.jsonl 复算**，不目测、不转引博客表；博客/README 与日志冲突时按 K 系列勘误裁决（本篇即 K-2）。
- 本篇数字只描述 v1 历史运行（开源 timer、单 CoreMark、报最佳），与 V2 的 held-out 口径不可比（K-1，见 [14-v1-leaderboard](/concepts/14-v1-leaderboard.md)）。
- 运行起点的 301.04 与排行榜对照基线 282.82 是两套口径，区别见 [10-baseline-cpu](/concepts/10-baseline-cpu.md)。

## 相关概念

- [baseline CPU 走读：5 级按序 RV32IM 种子核与 bench 冻结夹具](/concepts/10-baseline-cpu.md)
- [接受规则：严格大于、三结果类与搜索的单调形状](/concepts/09-accept-rule-outcomes.md)
- [V1 排行榜：16 模型、失败模式谱与两个对照的崩溃](/concepts/14-v1-leaderboard.md)
- [一个假设的生命周期：r1s0 失败到 r6s0 Cold DIV +15.7%](/examples/00-cold-div-reincarnation.md)
