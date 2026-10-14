---
okf_version: "0.2"
type: Example
title: "示例：拆解一个 983.2 的 rep：46 iters、9 接受与 $123.62"
description: "把 V1 榜首 Opus 的单个 983.2 rep 拆成口径、接受率、broken 构成、成本遥测与 n=1 统计边界五个镜头"
tags: [HWE Bench, 示例, V1 排行榜, 成本遥测, n=1]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T17:40:00+08:00"
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

本示例拆解 V1 排行榜首行 `claude-opus-5_5_xhigh` 的**唯一一个完成 rep**（rep1）：终态 fitness 983.2、Δ248%、46 次迭代、9 个候选接受、563.3 分钟、API 等价费用 $123.62（全部作者报告，F-107/F-112）。一个汇总数字会同时回答好几件不同的事——搜索结果、每槽产出率、钱、统计显著性——本示例先校准计数口径，再用四个独立镜头拆解它，并标出 n=1 的边界。

这是静态走读：数字逐字摘自固定提交 `4a137bb1378834ca3664a1c971684777eb5f364a` 的 LEADERBOARD、bench 模型目录 README 与研究日记，未复跑任何 rep；本文不产生新测量。

## 口径：46 iters = 45 个候选 + 1 次 baseline retest

预注册规模为 N=15 轮 × K=3 槽 = 45 个候选/rep，另加每 rep 开头一次基线 retest，故 per-rep 明细每行都是 46 iters（F-080/F-081/F-112）。起点 282.8 是**冻结基准夹具核** bench-fixture-v1 的 retest 口径（基线 282.82，F-095），不要与 v1 历史开发运行的 L1 哨兵 301.04（fmax 135.21、lut4 9880，F-098）混用：前者是所有 bench 配置共同的起跑线，后者是 2026-04-28 那次 73 假设开发运行的一次性记录。两个基线的区别见 [/concepts/10-baseline-cpu.md](/concepts/10-baseline-cpu.md)。

## 主榜行与 per-rep 行（逐字摘引）

下面两行分别摘自 [bench/LEADERBOARD.md L15](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L15)（主榜）与 [L183](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L183)（per-rep 明细），列标题对应原文 L13 与 L181：

```text/markdown
| `claude-opus-5_5_xhigh` | 1/1 | 983.2 (n=1) | 983.2 | 3128 | 302.2 | 3.25 | 10.0 | 13.0 | 23.0 | 42.0 | 22% | $0.00 | 735 |
| `claude-opus-5_5_xhigh` | 1 | done | 46 | 10 | 13 | 23 | 282.8 → 983.2 | 248% | 983.2 | 3128 | 302.2 | 3.25 | 563.3 |
```

读法（作者报告）：终态/最佳同为 983.2（日志原值 983.24，+247.7%，日记记为 round 14 达峰）；LUT4 3128、Fmax 中位数 302.2 MHz、CoreMark IPC 3.25；wall 563.3 分钟（33,800 s，2026-09-26T03:22:40Z→12:46:01Z）。两个计数细节：表里的 `acc=10` 含基线 retest 哨兵，候选口径是 **9 接受**——模型目录 README 逐字说明 "The legacy `accepted: 10` counter includes the baseline, so it is one higher than candidate improvements"（[README L59](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/claude-opus-5_5_xhigh/README.md#L59)）；`Iters→best 42` 是日志条目序号而非锦标赛轮次（同段说明，F-107/F-112）。

## 23 个 broken：22 个连假设都没写出来

23 个 broken 的构成见排行榜失败模式小节（[L59-L64](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L59-L64)）：

```text/markdown
| Class | Count |
|---|---|
| `hypothesis_gen_failed` | 22 |
| `formal_failed` | 1 |
```

也就是说，榜首模型有 22 个槽（占 45 个候选的 49%）卡在假设代理的 20 分钟上限，连预期的 YAML 都没写到预分配路径（口径见排行榜 L57；日记记录 round 2/6/8/15 三个槽全灭，[diary 2026-09-26 L37-L40](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/research/diary/2026-09-26.md#L37-L40)）。唯一真形式反例是 r13s2 的 load-dependent 分支投机：BMC 53 个检查挂了 7 个（[README L41](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/claude-opus-5_5_xhigh/README.md#L41)）。主榜 pass-rate 22% = 10/46（含 retest；候选口径 9/45 = 20%）。**+248% 增益与 22% 接受率同时成立**：高均值来自 9 个被接受的大跳（含 R7 +25.6%、R10 +23.7%），高破碎率说明每槽的假设产出极不稳定，二者不矛盾。

## 9 个接受长什么样：胜场链的形状

248% 不是均匀爬出来的。9 个候选接受的轮次与逐轮增益（作者报告，摘自 [L231-L239](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L231-L239) 的 Winning hypotheses 小节；数字逐字，长标题为控制宽度按原文截断，完整标题见原文）：

```text/markdown
- R1  Split EX into single-cycle integer ALU plus iterative DIV/REM unit — 359.0 (+26.9%)
- R3  Stall-only I-fetch replay store with registered next-PC lookahead — 438.5 (+22.1%)
- R5  Pre-decoded one-hot ALU controls registered in ID/EX — 512.1 (+11.6%)
- R7  LUT-RAM register file + ID/EX control/data split + registered div b!=0 — 643.4 (+25.6%)
- R9  stall-only D-side store buffer + load cache, 4096-entry I-side replay store — 695.2 (+8.0%)
- R10 Take the divider off every critical path (div_unit.sv only, cycle-neutral) — 859.8 (+23.7%)
- R12 BHT in distributed LUT-RAM + split 2x32 rvfi_order counter (draft) — 894.4 (+4.0%)
- R14 Late branch unit (v2 form): verify load-dependent BRANCHes in MEM — 983.2 (+9.9%)
```

（上列省略 R4 +4.7% 一行；LUT4/Fmax 列见原文。）三点读法：① 九个胜场里两个大跳（R7、R10）与除法器/寄存器堆时序相关，R1 第一条就是冷除法器——与 v1 运行 r6s0 的故事同构（见 [/examples/00-cold-div-reincarnation.md](/examples/00-cold-div-reincarnation.md)，F-120 还指出这是大多数 agent 的第一手）；② 接受轮次跳过 R2/R6/R8/R15，恰是三槽全 broken 的轮次，增益与破碎率在时间上交错；③ R3/R9 的 stall-only 结构在作者审计中被标为 fitness 契约缺口（计时网表把 ready 常量化导致停顿逻辑被折叠出去），分数带 caveat（F-079，[/concepts/16-harness-reliability.md](/concepts/16-harness-reliability.md)）。

## 成本与遥测：$123.62 是估价，$0.00 不是零支出

费用字段必须成对读（[bench/claude-opus-5_5_xhigh/README.md L23-L24](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/claude-opus-5_5_xhigh/README.md#L23-L24)，逐字摘引）：

> "dollar billing is not available under OAuth. `total_cost_usd: 0.0` is not measured zero spend. `api_equivalent_cost_usd` (123.62 USD) is Claude Code's own list-price estimate, not a bill."

即主榜 `$0.00` 是 OAuth 订阅登录下无计费数据，不是实测零花费；$123.62 是 Claude Code 自己按牌价估的 API 等价成本（遥测重建口径见 F-126）。token 遥测为 **522,817,399 in / 1,904,689 out**，因 harness 归档了 implementer 与 scribe 全部会话，入 token 覆盖全部代理；出 token 是下界——超时被杀的会话只留流式快照（[diary L45](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/research/diary/2026-09-26.md#L45)）。节奏口径：735 s/iter（主榜行）≈ 563.3 min × 60 / 46；该 rep 未触每 rep $200 硬上限（F-019）。

## n=1：没有 std，也没有 p

主榜给的是 `983.2 (n=1)` 而非 ± 值——report.py 对单 rep 行刻意打印 "(n=1)" 而不是 "± 0.0"（[diary L56](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/research/diary/2026-09-26.md#L56)）。配对 Wilcoxon 表中该行 n_pairs=1，p 值为 "—"（全表 p 列无一例外，n<5 不报有意义 p，[L40](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/LEADERBOARD.md#L40)，F-111）：

```text/markdown
| `claude-opus-5_5_xhigh` | 1 | 1/1 | +700.42 | +700.42 | — | — |
```

作者自己在 README 与日记中两次声明：这是 "a fact about this run, not evidence that this configuration is better than another"（[README L9](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/bench/claude-opus-5_5_xhigh/README.md#L9)）。因此 983.2 是记录本上的最高分事实，不是排名结论；与 3-rep 模型的均值不可直接比名次。另需注意该 rep 的得分在 V2 更换厂商 timer、holdout 五程序后与 V2 数字严禁互比（K-1，见 [/concepts/15-v2-holdout.md](/concepts/15-v2-holdout.md)）。

## 这是 bench rep，不是 v1 进化史

容易混淆的两条实验线：v1 的 73 假设运行是**开发运行**——单一连续搜索，9h51m，301.04→577.76，9 个真胜场，产物是 v1 冠军核（F-003/F-106，见 [/concepts/11-v1-evolution.md](/concepts/11-v1-evolution.md)）；本示例的 rep 是**基准运行**——从冻结夹具核出发、N=15/K=3 预注册、成本门限与同种子复现条件全部锁死（F-080，见 [/concepts/13-v1-bench-methodology.md](/concepts/13-v1-bench-methodology.md)）。两者都出现了「冷除法器」开头，但那是趋同演化，不是同一次运行。

## 教训：算力、费用、接受率是三件独立的事

- **结果镜头**：983.2、+248%、302.2 MHz 描述搜索到了什么（作者报告）。
- **效率镜头**：22% pass-rate、735 s/iter、22 次假设超时描述每槽产出的稳定性——榜首模型也有近半槽位空转。
- **成本镜头**：$123.62 是牌价估价、$0.00 是计费缺失、5.23 亿入 token 是资源消耗；三个数回答三个问题，引用时必须带口径标签。
- **统计镜头**：n=1 只支持事实陈述，不支持模型间比较；要排名得看跨 rep 分布与 V2 的 6-runs 几何均值（F-117）。

## 相关概念与示例

- [/concepts/13-v1-bench-methodology.md](/concepts/13-v1-bench-methodology.md)：15×3 预注册、$200 成本门限与 per-rep 口径
- [/concepts/14-v1-leaderboard.md](/concepts/14-v1-leaderboard.md)：16 模型主榜、失败模式谱与两个对照
- [/concepts/11-v1-evolution.md](/concepts/11-v1-evolution.md)：别与开发运行的 9 胜场进化史混用
- [/concepts/15-v2-holdout.md](/concepts/15-v2-holdout.md)：n=1 之后，6-runs 与 V1/V2 不可比裁决
- [/concepts/16-harness-reliability.md](/concepts/16-harness-reliability.md)：telemetry 重建、OAuth 口径与故障方向
- [/examples/00-cold-div-reincarnation.md](/examples/00-cold-div-reincarnation.md)：胜场链 R1 冷除法器的开发运行版本——同一想法如何在 cosim 失败两小时后重生为 +15.7%
- [/examples/02-failure-gallery.md](/examples/02-failure-gallery.md)：22% pass-rate 的另一面——v1 与 bench 的真实失败按拦截点分组陈列，含 135 次零接受对照
- [/examples/index.md](/examples/index.md)：HWE Bench 束示例索引与三篇的阅读路径
