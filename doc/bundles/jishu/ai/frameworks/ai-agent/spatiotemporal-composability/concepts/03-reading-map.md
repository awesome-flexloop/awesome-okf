---
type: "Wiki Tutorial"
title: "03 · 阅读地图与符号约定"
description: "本包 12 篇与论文章节的对应表、形式符号速查、F 编号与信源的使用方式"
tags: [spatiotemporal-composability, reading-guide, notation, tutorial]
sources:
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 §3–§7
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
---

# 03 · 阅读地图与符号约定

> 一句话：这一篇不含任何推导，只把「论文哪一节 → 本包哪一篇 → 用哪些符号」固定下来，供后续按需跳读。

## 1. 章节对应表

| 本包 | 主题 | 论文位置 | 形式化密度 |
|---|---|---|---|
| [00](00-overview.md) | 总览与直觉 | §1、§3、§8 | 无 |
| [01](01-two-composabilities.md) | 两个可组合性与反例 | §1.1–§1.2 | 无 |
| [02](02-from-types-to-runtime.md) | 谱系与 reify 立场 | §1.3、§2、§3 开篇 | 低 |
| 03（本篇） | 阅读地图 | — | 无 |
| [04](04-revertible-effects.md) | 可逆效应 | §3.1 | 高：Def 1–17 |
| [05](05-reactive-coeffects.md) | 响应式协同效应 | §3.2、§3.4.2 | 高：Def 19–27、Thm 45/47 |
| [06](06-context-paradigm.md) | 统一上下文与观测等价 | §3.3、§3.4.1 | 高：Def 28、42 |
| [07](07-dynamic-composition-calculus.md) | 动态组合演算 | §4.1–§4.2 | 高：Def 48–55、九规则 |
| [08](08-metatheory.md) | 元理论与扩展 | §4.3–§4.4 | 最高：Thm 64–80 |
| [09](09-implementation-cordis.md) | Cordis 实现 | §5 | 中：Table 2、Alg 1–10 |
| [10](10-boundaries-and-related-work.md) | 边界、限制与相关工作 | §6、§7 | 低 |
| [11](11-learning-path.md) | 学习路径与误读清单 | — | 无 |

前四篇不出现推导式，是刻意安排：V 阶段「新人视角」审查指出符号首见即劝退，故把全部形式符号延后到第 04 篇之后（见 [对抗审查记录](../references/verification.md)）。

## 2. 符号速查

| 记号 | 读法 | 直觉 |
|---|---|---|
| `Γ` / `γ` | 上下文类型 / 某个具体上下文状态 | 系统当前「全部可触及状态」 |
| `∂Γ` | 效应上下文 | 状态 + 逆的累积器（Def 2） |
| `𝔈Γ` / `𝔈*Γ` | 效应函数 / 见证版效应函数 | 返回「新状态 + 逆」的函数（Def 8） |
| `ℑΓ` | 效应迭代器 | 可分步产出多个效应的递归结构（Def 17） |
| `Σ` | 协同效应上下文 | 键 → 值的有限偏函数（Def 19） |
| `Γ∞` | 统一上下文 | 递归地把 effect 与 coeffect 装进同一个东西（Def 28） |
| `≃S` | 观测等价 | 没有任何操作序列能区分两者（§3.3.2） |
| `d` / `p` / `e` | 依赖规范 / 供给键集 / 效应迭代器 | 组件三元组（Def 48） |
| `ω` | committed view | 一次激活期间固定的依赖解析 |
| `φ` / `g` | 逆的累积器 | 卸载时逆序应用的东西 |

一个容易混的点：`g` 在不同段落既表示单个逆函数、也表示累积后的 accumulator；读原文时以「是否带下标 / 是否出现在 fiber 七元组里」区分。

## 3. 等式该怎么读

§3.1 给出的所有等式按 `≃S` 读取，而非逐字相等（F-042）。原因：多个组件的效应在同一上下文里交织，物理状态未必逐字节相同，但只要**任何后续操作序列都观察不出差别**，就认为恢复成立。Theorem 68 的 recovery exactness 正是在这个意义上说的（F-052）。

这条约定同时划定了保证的边界：论文不承诺物理状态复原，也不覆盖已经越界的 emission（F-066）。

## 4. F 编号与信源怎么用

- 正文里的 `F-xxx` 全部指向 [论文事实台账](../references/facts.md)，每条带 PDF 页码；[paper-source.md](../references/paper-source.md) 是按章节重排的第二份登记，两份编号集合机械比对一致（F-001…F-072，无重复无跳号）。
- 需要看原文时，权威信源只有 arXiv abs 与 v1 PDF，登记在 [信源登记与版本声明](../references/sources.md)；Pith、BestHub 等只用于交叉核验转述口径，不作事实依据。
- 想从符号直接跳到工程 API，用 [理论符号 ↔ Cordis API 映射全表](../references/theory-api-mapping.md)。

## 5. 两条阅读纪律

1. **每条定理先看前提再看结论**。Theorem 73 要求 `≺` 无环、迭代器步数有界、名字集有限；Theorem 80 要求组件 total on its provision 且排除失败 fiber（F-054、F-055、F-056、F-057）。只记结论就是虚假升级。
2. **区分小节名与定理名**。§4.3 的 Preservation / Temporal Composability / Spatial Composability / Progress / Confluence 是**五个小节**，具体结果是 Theorem 64、68、Corollary 69、70、71、73、80 等编号条目（勘误 E-03）。

> 下一篇开始进入形式化：[04 · 可逆效应](04-revertible-effects.md)。若只想了解工程落地，可直接跳到 [09 · Cordis 实现](09-implementation-cordis.md)。
