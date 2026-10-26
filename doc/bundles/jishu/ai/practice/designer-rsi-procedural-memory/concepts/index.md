---
type: category
title: "Designer-RSI 概念教程"
description: "按问题、记忆、检索、演化、门控、评测、结果、边界八层组织学习路径。"
status: stable
stale_after: 2027-03-31
generated: { by: "reference_agent", at: 2026-10-26T11:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-26T11:00:00+08:00 }
sources:
  - id: blog
    resource: "https://mp.weixin.qq.com/s/XsUBelItpT4LnC_ETSv_Vw"
  - id: paper
    resource: "https://arxiv.org/abs/2609.22086"
  - id: article-facts
    resource: "../references/article-source.md"
---

# 概念教程

| 想了解 | 阅读 |
|---|---|
| 全文地图、五个机制与关键数字 | [速览：冻结模型之外的程序记忆](00-overview.md) |
| 程序记忆是什么，SKILL.md 怎么写，76 个冷启动技能从哪来 | [程序记忆与技能库](01-procedural-memory.md) |
| 139 个技能如何只暴露 2–4 个候选，全文怎样按需加载 | [两阶段检索与渐进披露](02-retrieval-and-injection.md) |
| Widening 与 Deepening 各自怎么触发、怎么修、为什么必须耦合 | [双轴演化](03-evolution-widening-deepening.md) |
| 为什么“平均分变高”不能上线，门控到底怎么判 | [匹配回放门控](04-replay-gate.md) |
| 设计质量如何拆成三根轴，四个指标怎么分开读 | [Graphic-Eval](05-graphic-eval.md) |
| 五轮实验、消融、回退与不能外推的结论 | [结果与读法](06-results.md) |
| 六条边界、适用性判据与落地检查表 | [边界与落地](07-limits-and-adoption.md) |

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-procedural-memory
02-retrieval-and-injection
03-evolution-widening-deepening
04-replay-gate
05-graphic-eval
06-results
07-limits-and-adoption
```
