---
okf_version: "0.2"
type: Concept
title: "接受规则：严格大于、三结果类与搜索的单调形状"
description: "accept_rule.py 用无 target 严格大于、饱和缺口与两阶段 Pareto 决定合并：它塑造单调爬坡，也把测量契约的漏洞原样放大"
tags: [HWE Bench, 接受规则, accept_rule, Pareto, 搜索形状]
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

## 是什么：三结果类与第四种运行态

方法学把每个 N×K 槽位的结局分成三类（F-082，BENCH_METHODOLOGY.md L68-L82）：

- **improvement**：fitness **严格超过**轮前冠军，合并入活动分支成为新冠军，每轮至多一个；
- **regression**：lint/formal/cosim/fpga 各门全过，但 fitness ≤ 冠军，worktree 丢弃；
- **broken**：某一道门失败，按错误类细分（formal_failed/cosim_failed/sandbox_violation/schema_error 等，v1 实例谱见 F-102）。

log.jsonl 里还存在第四种**运行态** `placement_failed`：3 个 nextpnr 种子中成功布局的不足 2 个（`MIN_SUCCESSFUL_SEEDS = 2`），单幸存者中位数不予承认（F-071）。它不是「想法被验证为差」，而是「这一轮没测成」，v1 共 4 例且全是 structural 类（F-103）。

## 怎么实现：accept_rule.py 的三种模式

[accept_rule.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/accept_rule.py#L69-L108) 只有 109 行、纯函数无 I/O（F-015），按传入 target 分三种模式：

1. **无 target（标准配置）**：`(np or 0) > (op or 0)`——严格大于（[L84-L86](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/accept_rule.py#L84-L86)）。平局不换主干：fitness 相等的候选即使门全过也丢弃，主干指针不会因噪声横跳。
2. **单 target**：饱和缺口（`_deficit`，[L12-L41](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/accept_rule.py#L12-L41)）在达标前负责爬坡；两轴都越过目标后回落到「只改进被约束轴」。
3. **双 target（两阶段 Pareto）**：phase-1 比缺口分数；双方都达标（score=0）后进入 phase-2 的严格 Pareto 支配——两轴都不差且至少一轴严格更好才接受（[L56-L66](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/accept_rule.py#L56-L66)）。

方法学注明标准 NeurIPS 配置两个 target flag 都不传，规则退化为 "higher CoreMark wins"（F-082）。

## 为什么：规则塑造搜索的单调形状

接受规则是对搜索空间的塑形器，而不只是记账：

- **单调爬坡**：主干冠军序列只允许严格上升，fitness 曲线天然是阶梯函数（progress.png 的黑色 step-line 即由此画成，F-016），读者可以从日志无歧义重放「当前最强」在每一轮是谁。
- **防漂移**：平局不合并 + ff-only 快进合并（[03-worktree-sandbox](/concepts/03-worktree-sandbox.md)）保证主干历史等于胜场历史，一次回退式合并都不可能混进冠军序列。
- **错误教学也被拦截**：门全过但分数变差的候选被丢弃，agent 不会从「错误动作得到奖励」——这是作者论点 "the artifact that survived ... was the verifier" 的机制基础（F-005）。

## 真实拦截样本：−73.25% 与它的同伴

v1 运行的 73 个假设给出了规则价值的直接证据（均为作者报告的日志实测，F-104/F-105）：

| 槽位 | 想法 | fitness | delta | formal/cosim |
|---|---|---|---|---|
| r24s2 | Registered Lookahead JALR Target Predictor | 154.53 | **−73.25%** | 均 True |
| r9s1 | Store-Slot-Aware Fetch Skid Queue | 166.23 | −58.19% | 均 True |
| r5s0 | Explicit MEM Byte-Lane Steering | 166.75 | −48.61% | 均 True |

r24s2 发生在峰值 577 iter/s 已经锁定之后：各门全部通过、实现完全合法，只是分数崩塌，被「与基线（现任冠军）比较」闸拦下；若被接受，一个回合就抵消此前全部胜场（F-104）。另有 4 个 placement_failed 全是存储结构尝试（Two-Entry Retiring Store Buffer、Two-Entry Pending Store Slot、Same-Cycle Store Slot Refill、Replay-Fed Memory Plus ADDI Pair Issue，F-103）。完整失败样本集见 [/examples/02-failure-gallery.md](/examples/02-failure-gallery.md)，51 条 regression 的分类账见 [11-v1-evolution](/concepts/11-v1-evolution.md)。

## 演进：V2 从严格 0 改成 4.6% 噪声门限

严格大于在 V1 是正确选择，但 V2 测出布局噪声后修正了它：接受阈值改为 **4.6% margin，set from measured placement noise**（作者报告，F-124，[v2.html L359](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L359)）。即 V1 的「任何提升都接受」（"Any improvement accepted"）在噪声量级约 4.6% 的测量系统里会把噪声当成胜场；V2 要求候选超过 margin 才算 improvement。规则随测量契约的校准而校准，而不是一成不变。

## 边界：接受规则的质量上界是测量契约

接受规则只能对「它收到的分数」诚实，不能修复分数本身。两类问题明确落在它的边界之外：

- **测量假象它照单全收**：作者 2026-09-26 日记记录的 fitness 契约缺口（作者报告，F-079）——core_bench 把 imem/dmem Ready tie 成 1'b1，「只在 ready 为低时作用」的停顿专用逻辑被常量折叠出时序网表：周期收益计入、面积与时序成本为零。实例是 **V1 排行榜 Opus rep 的 r9s1（695.16，commit ed49aaf）**，4096 项 I-side replay store 与 r7s0 网表等价（LUT4 3078 vs 3080、Fmax 222.1 vs 219.2 MHz）：门全过、分数真提升，但提升是测量口径的产物。注意它与本束 v1 历史运行的 r9s1（−58.19%，F-105）只是槽位标号相同、属于不同运行。接受规则无法分辨「真快」与「夹具看不见的逻辑」，修复只能改测量夹具（V2 已把停顿生成器纳入被计时电路，F-124）。
- **形式规格错误它也不判**：V2 披露 vendored formal 把有符号 DIV/REM 按 unsigned 算、以及两个最终设计给 formal 的代码与综合/仿真异版（F-123）——这些是规格与指纹层面的缺口，接受规则只消费 formal 门的布尔结果。

## 相关概念

- [一轮编排：N 槽锦标赛、四个角色与门的短路顺序](/concepts/02-round-orchestration.md)
- [FPGA 门：3-seed 中位数、fitness 公式与反常量折叠夹具](/concepts/07-fpga-fitness.md)
- [CoreMark 评测口径：canonical 2K、IPC 量纲与 holdout 五程序](/concepts/08-coremark-measurement.md)
- [v1 进化史：9 个真胜场、63 次拒绝与 −73% 警戒线](/concepts/11-v1-evolution.md)
