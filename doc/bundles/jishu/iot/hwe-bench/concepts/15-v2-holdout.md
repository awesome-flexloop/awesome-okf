---
okf_version: "0.2"
type: Concept
title: "V2 演进：6×6 几何均值、holdout 主榜与三门正确性缺口"
description: "V2 因开源 timer 漏计路径而重建记分：6 系统×6 runs、五隐藏程序几何均值、预注册 1.32x 主对比、三门正确性缺口与 V1/V2 不可比"
tags: [HWE Bench, V2, holdout, 几何均值, 正确性缺口]
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

## V2 为什么存在：一次测量装置的整体更换

V2 不是 V1 的扩样，而是**记分装置重建后的新基准**：V1 使用的开源 nextpnr timer 被发现漏掉整类电路路径——一个 32 位除法器开源 timer 报 123 MHz，厂商工具只给 6.9 MHz（F-124）。V2 因此把计时换成 Gowin 厂商工具、让停顿生成器进入被计时电路、改用 agent 永远看不到的 5 个隐藏程序排名（[v2.html L31-L45](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L31-L45)，F-117）。

## 设计：6 系统 × 6 runs 与预注册主对比

V2 hero：6 个 agent 系统（模型 + 其厂商命令行 agent 构成的整体）各跑 **6 runs = 36 个 scored runs**，每 run 仍是 **15 轮 × 3 尝试**，从同一颗起始核出发（F-117）。统计从 V1 的「报最佳 run」改为 **6 runs 几何均值 + 预注册检验**（F-124）。

预注册的唯一主对比是 Opus 5.5 vs GPT-6.1 Sol：**ratio 1.320，95% CI [1.183, 1.473]，p = 0.0005**（F-117、F-119）。三层结果：Opus 5.5 与 Sonnet 5.5（Claude Code）、GPT-6.1 Sol 与 GPT-6 Astra（Codex CLI）、GPT-5.5 与 GPT-6 Luna（Codex CLI）（F-117）。

## 主表四列怎么读（数字均为作者报告）

V2 主表列 held-out iter/s、CoreMark iter/s、Fmax、LUT4（[v2.html L154-L217](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L154-L217)，F-118）：

| 系统 | held-out iter/s | CoreMark | Fmax MHz | LUT4 |
|---|---|---|---|---|
| Opus 5.5 | 7,024 | 280 | 107.8 | 3,161 |
| Sonnet 5.5 | 6,418 | 259 | 103.8 | 4,232 |
| GPT-6.1 Sol | 5,320 | 215 | 90.7 | 4,716 |
| GPT-6 Astra | 5,014 | 201 | 83.6 | 5,546 |
| GPT-5.5 | 3,595 | 143 | 63.9 | 2,948 |
| GPT-6 Luna | 3,538 | 137 | 64.6 | 2,934 |
| VexRiscv MaxPerf（human） | 6,216 | — | 87.8 | — |
| textbook edit | 2,645 | 103.7 | 46.6 | 2,541 |
| V0（每 run 起点） | 309 | 12.1 | 5.4 | 12,312 |

排名分是**五隐藏程序**的几何均值；CoreMark 退为优化信号（agent 场内可见），不再用于排名（F-124）。holdout 的机械口径承接 E3：五内核为 dhrystone、aha-mont64、crc32、matmult-int、edn，复用与 fitness 同一 50M cycle 上限与同一停顿模型（F-084）；geomean 只对 validated 核做 mean-of-logs（纯 Python 无 numpy），无核 validated 时为 0.0，五核全过才有 all_validated（F-085）。五核的 V0 期望值（cycles、reps、iter_s 与 geomean 7212.33…）冻结在 bench/holdout/v0_expected.json，为作者报告的留存基线参照（F-086）。

## Holm 12 对与 20% 分辨力

预注册对比之外，V2 对 12 个附加对做 Holm 校正：**9 对分离，3 对不分离——不分离的恰好是各层内部对**（Opus/Sonnet、Sol/Astra、5.5/Luna）（F-119）。作者给出的功效刻度是：**6 runs 能分辨约 20% 的差距，分辨不了层内 6-10%**（[v2.html L223-L228](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L223-L228)，F-119）。因此同层两系统的名次差不应被读作能力差。

## 三个对照：textbook、random、lessons 消融

- **textbook edit**：把 V0 单周期除法器换成 radix-2 迭代版——这正是大多数 agent 的第一手：round-1 的 35 个接受设计中 **34 个改了除法器**。过门、2,645 held-out iter/s、**8.6x V0**，且增益**全部来自时钟频率**（F-120）。它标定了「教科书式一步」的位置：每个 scored run 都超过它，系统均值为其 1.3x（Luna）至 2.7x（Opus）（F-120）。
- **random-mutation 对照（独立抽取版）**：135 次**独立抽取**、0 接受——117 次败 formal、12 次败 cosim、6 次过全门但 no-op（F-121）。这是对 V1 播种 bug 的修复版口径，区别于 V1 的「3 draws 重复 45 次」（K-6，见 [14-v1-leaderboard](/concepts/14-v1-leaderboard.md)）。
- **lessons 消融**：GPT-6.1 Sol 无 LESSONS.md 再跑 6 次，full vs no lessons = **1.02x，CI 0.91-1.14，p=0.68**；不可区分，区间排除了经验文件 >14% 的增益（F-122）。解读边界与 scribe 机制见 [12-scribe-lessons](/concepts/12-scribe-lessons.md)。

## 三门正确性缺口：披露但不改分

V2 白页明确：三门缺口在记分期间/之后浮现，**没有任何一个改变已计分数**（F-123，[v2.html L324-L341](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L324-L341)）：

1. **取指地址越界无门**：没有检查证明取指地址留在内存内。记分后补写的有界 formal（任意 64 字程序、任意内存停顿、复位后 20 周期）在 44 个设计上过 36；发现 1 个 Opus 设计在复位后 9 周期、错误预测路径上从负地址取指——**结果仍正确**；另有 7 个大设计超时、未找到反例。
2. **有符号 DIV/REM 规格错误**：vendored formal 规格把有符号 DIV/REM 按 unsigned 计算，导致全算术检查对**每个正确除法器都失败**；真算术依赖 cosim 兜底（与 ALTOPS 分层同源，见 [05-formal-altops](/concepts/05-formal-altops.md)）。
3. **formal 看到异版代码**：两个最终设计送给 formal 的某块代码与综合/仿真版不同；换成综合版后 **"both pass all 53 checks"**。

## V1→V2 七项变更

| V1 | V2 |
|---|---|
| 开源 timer（nextpnr），漏路径（32 位除法器 123 vs 6.9 MHz） | Gowin 厂商 timer 计分且对 agent 可见 |
| 停顿只在仿真、被计时电路里没有，停顿逻辑「免费」 | 同一停顿生成器既在仿真也在被计时电路 |
| 在 agent 优化的 CoreMark 上排名 | 5 个隐藏程序排名；CoreMark 保留为优化信号 |
| 任何提升都接受 | 按实测布局噪声设 **4.6% margin** |
| 2-3 runs、报最佳 | 6 runs、几何均值、预注册检验 |
| 读权限随 CLI 而异（Codex 可读任意处） | 每并发 run 一个 OS 账号、隐藏程序不可读 |
| random 播种 bug：3 draws 重复 45 次 | 135 次独立抽取 |

（F-124，[v2.html L351-L366](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L351-L366)。）4.6% margin 的接受规则含义见 [09-accept-rule-outcomes](/concepts/09-accept-rule-outcomes.md)。

## K-1：V1/V2 数字严禁同表比较

官方在白页逐字声明：首页 V1 榜数字来自开源 timer，**"are not comparable with these"**（F-125，[v2.html L369-L372](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/site/v2.html#L369-L372)）。七项变更同时改变了计时器、被计时电路、排名程序与统计法，V1 的 983 与 V2 的 7,024 是不同对象的数，不能横比、不能换算，只能各自分章呈现——这是本束引用所有 V1/V2 数字时的硬纪律。

## 边界与口径

- 主表数字为 v2.html 静态文本上的「作者报告」；V2 原始运行数据在外部分支，本束不评价也不复跑（F-118）。
- holdout 防过拟合规则承接 E3 预注册：中位数冠军须在 holdout geomean 上保持 ≥50% CoreMark 增益才可声称 "not merely workload overfitting"，且 "No re-optimization against held-out kernels, ever"（F-087）；五程序口径的程序细节见 [08-coremark-measurement](/concepts/08-coremark-measurement.md)。
- 三门缺口「不改分」是作者裁决：补检发现的取指越界结果仍正确，另两项影响的是证明覆盖而非已测行为。

## 相关概念

- [V1 排行榜：16 模型、失败模式谱与两个对照的崩溃](/concepts/14-v1-leaderboard.md)
- [CoreMark 评测口径：canonical 2K、IPC 量纲与 holdout 五程序](/concepts/08-coremark-measurement.md)
- [riscv-formal 分层：ALTOPS 替身、检查数三口径与空过分类](/concepts/05-formal-altops.md)
- [经验积累：append-only LESSONS.md、scribe 角色与 lessons 消融](/concepts/12-scribe-lessons.md)
