---
type: Reference
title: "核验报告：AI 一人公司与单点产品"
description: "对原文收入、增长、下载量和收购声明进行来源距离判断、交叉核验与勘误登记。"
tags: [核验, P0, AI商业化, 事实边界]
generated: { by: "reference_agent/web-search", at: "2026-09-20T00:00:00Z" }
verified: [{ by: "process:seven-concepts-v", at: "2026-09-20T00:00:00Z" }]
status: flagged
stale_after: "2026-12-31"
sources:
  - id: blog
    resource: "https://mp.weixin.qq.com/s/NgiuQ1DfKyiaqhYOWRz_CA"
  - id: revenuecat-coconote
    resource: "https://www-docs.revenuecat.com/blog/growth/brett-zack-coconote-sub-club-podcast-2026/"
  - id: coconote-subclub
    resource: "https://subclub.com/episode/bootstrapped-to-67m-arr-and-an-exit-to-quizlet-in-2-years-brett-bauman-zack-hargett-coconote"
  - id: myfitnesspal-calai
    resource: "https://www.globenewswire.com/news-release/2026/03/02/3247439/0/en/MyFitnessPal-Acquires-Cal-AI-Expanding-on-its-Position-as-the-Leading-Player-in-Digital-Nutrition-Tracking.html"
  - id: photoai-case
    resource: "https://www.indiehackers.com/post/photo-ai-by-pieter-levels-complete-deep-dive-case-study-0-to-182k-mrr-in-18-months-3a9a2b1579"
---

# 核验结论

## 状态

本 bundle 为 `flagged`。原因是文章主论据依赖多个未经原文脚注支持的收入与增长数字；部分数字有二手材料支持，但没有统一的审计口径。

## P0 勘误四清单

| 清单 | 核验对象 | 结论 |
|---|---|---|
| 日期/版本 | 原文发布日期、Cal AI 收购宣布日期 | 原文发布日为 2026-09-18；Cal AI 收购公开宣布日可由 MyFitnessPal/媒体材料指向 2026-03-02。✅ |
| 成效数字溯源 | Photo AI 10.5 万美元月收入、Coconote 670 万美元年收入、Cal AI 3000 万美元年收入 | Photo AI 与 Coconote 有二手材料，Cal AI 有收购报道转述；均非本文原始脚注或审计报表。⚠️ |
| 口径对照 | “月入/利润/年收入/ARR/下载量” | 原文将收入、利润、ARR、下载量并置，未说明统计时点与口径，不能直接横向比较。⚠️ |
| 引文逐字 | 原文没有引号式官方引文 | 无需勘误，但不得把作者判断改写成官方结论。✅ |

## 逐项核验

1. **Photo AI**：Indie Hackers 等二手案例报告过超过 10 万美元月经常性收入，并描述为 Pieter Levels 的单人产品；不同时间点出现 10.5 万、13.2 万至 13.8 万美元等数字。因此正文只写“公开二手案例在不同时间点报告过超过 10 万美元月收入”，不复述为固定当前值。
2. **Coconote**：RevenueCat 文章明确支持四个月达到 100 万美元 ARR，并转述其后达到 670 万美元 ARR、被 Quizlet 收购。由于来源是平台文章/播客摘要，不等于审计；正文保留“公开增长叙述”标签。
3. **Cal AI**：MyFitnessPal 收购相关报道支持超过 1500 万下载和超过 3000 万美元年收入的公司口径，交易条款未披露。正文不把“七人团队”作为已独立核验的组织规模事实。
4. **10 人验证法**：没有外部证据，归为作者建议，不得写成转化率定律。

## V 对抗审查摘要

- 事实溯源视角：所有数字均回指 F 编号，未把作者算术示例升级为市场数据。
- 结构视角：商业分析类不设 `examples/`，根索引声明“非操作教程”。
- 读者视角：给出可迁移检查框架，但明确不承诺收入结果。
- 时效视角：收入、下载量、收购状态设置 `stale_after: 2026-12-31`，到期后应复核。
