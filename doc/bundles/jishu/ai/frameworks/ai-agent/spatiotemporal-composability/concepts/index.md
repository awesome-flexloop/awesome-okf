---
type: group
title: "概念教程（Concepts）"
description: "《A Programming Paradigm for Spatiotemporal Composability》12 篇原子化中文教程，从直觉到形式化再到边界"
---

# 概念教程（Concepts）

本目录按「直觉 → 问题 → 立场 → 地图 → 三层形式化 → 元理论 → 实现 → 边界 → 路径」组织，建议顺序阅读。前四篇不引入推导式；第 04 篇起才出现形式符号。

## 阅读路径

| 顺序 | 文档 | 回答的问题 |
|---|---|---|
| 00 | [总览](00-overview.md) | 论文在解决什么；本包与 cordis / deepseek-harness 如何分工 |
| 01 | [两个可组合性](01-two-composabilities.md) | 时间/空间可组合性的定义，VSCode 为何做不到 |
| 02 | [从静态类型到运行时](02-from-types-to-runtime.md) | effect / coeffect 谱系；为什么是 reify 而非类型标注 |
| 03 | [阅读地图与符号约定](03-reading-map.md) | 章节对应、符号速查、等式读法 |
| 04 | [可逆效应](04-revertible-effects.md) | `Γ → Γ × (Γ → Γ)`、track/recover、见证版与迭代器 |
| 05 | [响应式协同效应](05-reactive-coeffects.md) | `Σ`、notify 三分类、隔离与拦截、交换性义务 |
| 06 | [上下文范式](06-context-paradigm.md) | `Γ∞`、观测等价 `≃S`、迭代器独立性两条件 |
| 07 | [动态组合演算](07-dynamic-composition-calculus.md) | 组件/fiber 结构、九条规则、target view 与 guard |
| 08 | [元理论](08-metatheory.md) | 七条结果的编号、前提与「不保证什么」 |
| 09 | [Cordis 实现](09-implementation-cordis.md) | Table 2、Algorithm 1–10、HMR 三阶段与证据等级 |
| 10 | [边界与相关工作](10-boundaries-and-related-work.md) | 内外边界、三条限制、与 dagger/COP/AOP/FRP 对比 |
| 11 | [学习路径与常见误读](11-learning-path.md) | 三档路线、八条误读、自检题与复核机制 |

> 全部概念页字符数均落在 500–5000 的原子化区间内；事实以 `F-xxx` 回指 [论文事实台账](../references/facts.md)。

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-two-composabilities
02-from-types-to-runtime
03-reading-map
04-revertible-effects
05-reactive-coeffects
06-context-paradigm
07-dynamic-composition-calculus
08-metatheory
09-implementation-cordis
10-boundaries-and-related-work
11-learning-path
```
