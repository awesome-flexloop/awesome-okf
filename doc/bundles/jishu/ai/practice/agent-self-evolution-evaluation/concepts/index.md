---
type: category
title: "LIFT 概念教程"
description: "按测量对象、评测协议、排行榜解读和结论边界组织 LIFT 学习路径。"
status: stable
stale_after: 2026-12-31
generated: { by: "reference_agent", at: 2026-10-10T12:06:17+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-10T12:06:17+08:00 }
sources:
  - id: repo
    resource: "https://github.com/FeiZhuNiU-INFJA/LIFT"
  - id: paper
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/paper-neurips.md"
---

# 概念教程

| 想了解 | 阅读 |
|---|---|
| LIFT 所说的“加载影响”具体测量什么 | [LIFT 衡量的是什么](00-lift-measures-loaded-impact.md) |
| Warmup、Holdout、Base、Loaded 如何配对 | [配对 Holdout 协议](01-paired-holdout-protocol.md) |
| delta、置信区间和榜单日期如何解释 | [排行榜数字如何解读](02-reading-leaderboard.md) |
| 结论能外推到哪里，如何迁移评测设计 | [有效范围与迁移边界](03-limitations-and-transfer.md) |

```{toctree}
:hidden:
:maxdepth: 2

00-lift-measures-loaded-impact
01-paired-holdout-protocol
02-reading-leaderboard
03-limitations-and-transfer
```
