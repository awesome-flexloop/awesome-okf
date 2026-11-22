---
type: "Wiki Tutorial"
title: "11 · 学习路径与常见误读清单"
description: "三档阅读路线、跨包阅读顺序、八条常见误读及自检题"
tags: [spatiotemporal-composability, learning-path, faq, tutorial]
sources:
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 全文
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
---

# 11 · 学习路径与常见误读清单

> 一句话：按目标选一档路线读完，再用末尾八条误读清单自查——这篇教程最容易出错的地方不是看不懂符号，而是把条件命题读成无条件承诺。

## 1. 三档路线

| 路线 | 适合 | 篇序 | 拿到什么 |
|---|---|---|---|
| **A · 20 分钟直觉档** | 只想判断「这跟我做的插件系统有没有关系」 | [00](00-overview.md) → [01](01-two-composabilities.md) → [02](02-from-types-to-runtime.md) → [10](10-boundaries-and-related-work.md) → [回程同源](../references/pattern-return-ticket-with-effect.md) | 问题定义、适用判据、可迁移模式 |
| **B · 工程档** | 要读 Cordis / Koishi 源码，或实现类似机制 | A + [03](03-reading-map.md) → [05](05-reactive-coeffects.md) → [07](07-dynamic-composition-calculus.md) → [09](09-implementation-cordis.md) → [API 映射表](../references/theory-api-mapping.md) | 键表、九规则、Algorithm 1–10 的对应关系 |
| **C · 完整档** | 要复现证明或评估方法学强度 | 按 00 → 11 顺序全读，重点 [04](04-revertible-effects.md)、[06](06-context-paradigm.md)、[08](08-metatheory.md) | 全部定义编号、定理前提与保证边界 |

三档都建议先读 [03 · 阅读地图](03-reading-map.md) 的符号速查表，避免在第 04 篇被记号卡住。

## 2. 跨包顺序

```
本包（论文精读）
  → [cordis](../../cordis/index.md)（框架源码机制）
  → [deepseek-harness](../../deepseek-harness/index.md)（Agent 框架落地）
```

理由：本包提供「为什么这样设计」，`cordis/` 提供「代码里长什么样」，`deepseek-harness/` 提供「用起来是什么体验」。反过来读容易把源码里的具体类名误当成理论必然。

若只想查重或核对版本，可读既有 [背景理论章节](../../cordis/references/background-paper.md)——注意它记录的是**早期草稿**（2026-08-13、约 88 页），与本包的 arXiv v1 口径构成版本差异 E-04，不是错误。

## 3. 八条常见误读

| # | 误读 | 更正 | 依据 |
|---|---|---|---|
| 1 | 「框架保证卸载一定干净」 | 运行时**不校验见证**；逆是否有效是组件作者义务 | F-059 |
| 2 | 「恢复 = 什么都没发生过」 | 只到观测等价 `≃S`；已越界的 emission 不可撤回 | F-042、F-066 |
| 3 | 「Confluence 说明怎么插拔都完全等价」 | 只谈**最终状态**，不谈过程期间的 emissions；且排除失败 fiber | F-056、F-057 |
| 4 | 「Progress 保证一定不会卡住」 | 前提是 `≺` 无环、迭代器步数有界、名字集有限；有环则相关组件永久 inactive | F-054、F-068 |
| 5 | 「87% 的热门扩展有问题」 | 原文是前 100 个中 **87 个**含可执行代码、**7 个**声明非内置扩展依赖，日期 2026-06-09 | F-013 – F-015、E-01 |
| 6 | 「演算有五个原语」 | 是**九条规则**；Figure 1 画八条因 `O-Retire` 为自环 | F-047、E-02 |
| 7 | 「五个元定理：Preservation / …」 | 那是**五个小节名**；结果是 Theorem 64、68、69、70、71、73、80 等 | E-03 |
| 8 | 「已在 DeepSeek Harness / 自我演化 Agent 上验证」 | 论文把自我演化 Agent Harness 列为 §8 **未来方向**；Koishi 证据是单生态、单语言、观察性，**非对照实验** | F-065、F-072 |

## 4. 自检题

1. 一次效应的类型为什么是 `Γ → Γ × (Γ → Γ)` 而不是 `Γ → Γ`？逆为什么必须就地生成？（[04](04-revertible-effects.md)）
2. `set(k,v)` 为什么本身是一次效应？（[05](05-reactive-coeffects.md)）
3. 迭代器独立性的**两个**条件分别是什么？只满足「变换两两交换」够不够？（[06](06-context-paradigm.md)）
4. `L-Leave` 与 `L-Unload` 为什么必须拆开？guard 在等谁？（[07](07-dynamic-composition-calculus.md)）
5. target view 为什么记录**提供者名字**而不是值？（F-048）
6. Theorem 73 的三条前提、Theorem 80 排除的情形各是什么？（[08](08-metatheory.md)）
7. acquisition 与 emission 的分界在哪，为什么它决定了恢复强度？（[10](10-boundaries-and-related-work.md)）

## 5. 复核与维护

本包依据 **arXiv:2608.25512v1**（2026-08-26）。论文为活跃修订中的预印本，全包 `stale_after: 2027-02-28`，到期复核动作：检查 arXiv 是否发布 v2+、比对 §3/§4 定义与定理编号是否变化、更新受影响的 F 编号条目。核验与勘误全表见 [P0 核验报告与对抗审查记录](../references/verification.md)，事实原文页码见 [论文事实台账](../references/facts.md)。

> 读完还想动手：先按 [回程同源](../references/pattern-return-ticket-with-effect.md) 的检验标准评估自己系统，再决定是否迁移；该模式 `maturity: L1`，未经跨项目复现。
