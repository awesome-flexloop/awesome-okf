---
type: "Wiki Tutorial"
title: "08 · 元理论：七条结果与各自的前提"
description: "Preservation、Recovery exactness、Ordering、Progress、Confluence 等结果的编号、前提与保证边界"
tags: [spatiotemporal-composability, metatheory, theorems, formal-methods]
sources:
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 §4.3–§4.4（Theorem 64–80）
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
---

# 08 · 元理论：七条结果与各自的前提

> 一句话：这一篇的每条结论都附带「前提」与「不保证什么」。只记结论不记前提，就是把作者的条件命题读成了无条件承诺。

> ⚠️ 命名层级：§4.3 的 Preservation / Temporal Composability / Spatial Composability / Progress / Confluence 是**五个小节名**；下面是带编号的**具体结果**。二手解读把两者混成「五个元定理」并另列「Terminal Recovery」为 loader 依赖，属勘误 [E-03](../references/verification.md)。

## 1. Preservation（§4.3.1）

**Definition 63**（F-051）给出注册表良构四条件：父指针落在注册表内、供给两两互斥、committed view 在声明键上全函数、被解析到的提供者已安装。

**Theorem 64**（F-051）：九条规则保持良构性。

| 项 | 内容 |
|---|---|
| 前提 | 初始状态良构；规则按 §4.2 的前提触发 |
| 保证 | 任意步数后注册表仍满足四条件 |
| 不保证 | 组件交出的逆真的能回退（F-059）；配置本身语义正确 |

## 2. Temporal Composability（§4.3.2）

**Theorem 68 · Recovery exactness**（F-052）：施加某 fiber 的 accumulator 后，各表与「该 fiber 从未开始」时其他步骤留下的表 `≃K`-等价。

**Corollary 69 · Terminal recovery**（F-052）：episode 关闭后 `σ_n = ∅`，满足 `O-Remove` 的前提。

| 项 | 内容 |
|---|---|
| 前提 | 每个见证有效；回退按逆序；状态按 `≃K` 比较 |
| 保证 | 剩余组件在观测等价意义下无法分辨该组件是否曾加载 |
| 不保证 | 物理状态复原；已越界的 emission 撤回（F-066） |

## 3. Spatial Composability（§4.3.3）

**Theorem 70 · Ordering**（F-053）：`L-Begin` 仅在依赖已提供时发生；提供者撤回晚于依赖者停用；绑定在依赖者 episode 内稳定。

**Theorem 71 · Resolution coherence**（F-053）：一次 transition 的所有迭代针对同一 resolution `ω`。

| 项 | 内容 |
|---|---|
| 前提 | `L-Unload` 的 guard `¬relied_n(γ)` 成立；迭代不跨 transition |
| 保证 | 不会出现「读到半个新解析」或「依赖者还活着但提供者已回退」 |
| 不保证 | 跨多次 transition 的整体无毛刺——FRP 的 glitch freedom 在此**无对应物**（F-072） |

## 4. Progress（§4.3.4）

**Definition 72**（F-054）：优先关系 `n ≺ m ≔ p_n ∩ d_m ≠ ∅`（n 供给 m 所需）。

**Theorem 73 · Progress**（F-054）：在给定前提下无死锁，且步数上界 `S(n) ≤ (K+3)(V(n)+1)`。

| 项 | 内容 |
|---|---|
| 前提 | **`≺` 无环**；**`len(e_n) ≤ K`**（迭代器步数一致有界）；**名字集有限** |
| 保证 | 系统不会停在既非静止也不可继续的状态 |
| 不保证 | 有依赖环时仍能激活——§6.5 明确依赖环使相关组件**永久 inactive**（F-068）；也不保证无界异步迭代 |

这三条前提是本包最容易被「教程化」抹掉的地方。特别是 `≺` 无环：论文没有提供自动打破环的机制，只说明环可从声明**静态预测**。

## 5. Confluence（§4.3.5）

**Definition 74**（F-055）：support set `A` 只读 `τ, π, d, p`。**Definition 76**：组件 total on its provision，即激活完成须安装 `p` 的全部键。

**Theorem 80 · Confluence**（F-056）：生命周期关系合流；规范形是从 `γ₀` 按 `⊲` 线性序各取一个 episode 的「一次性静态装配」。

| 项 | 内容 |
|---|---|
| 前提 | 组件 total on its provision；**排除失败 fiber**（§4.4 Failure，F-057）；静止态可达 |
| 保证 | 任意插拔调度最终收敛到**同一个状态**，因此配置可作唯一真相源，无需带顺序的迁移脚本 |
| 不保证 | **过程期间产生的 emissions**——§4.3.5 明确该结论只谈状态，不谈过程；也不保证失败组件参与收敛 |

「只谈状态不谈 emissions」是本定理最重要的限定：两条不同调度可以产生不同的外部消息序列，即便最终状态一致。把 Confluence 读成「怎么插拔都完全等价」是虚假升级。

## 6. 四个扩展（§4.4，F-057）

| 扩展 | 做法 | 对元理论的影响 |
|---|---|---|
| 异步惯性 | 只取 `L-Divert` 的 landing 分支 | 保持前述结构 |
| 失败 | 错误写入 fiber，target 置 `⊥` | **Confluence 排除失败 fiber** |
| 隔离 | 键集放大为 `K × R` | 与 `Σ_iso` 一致（F-039） |
| 配置修订 | retire → deactivate → remove → reinsert 的复合 | 由 Confluence 保证不必写迁移脚本 |

## 7. 一句话总结保证强度

框架保证的是**结构与时机**：良构性、回退顺序、解析一致性、状态收敛。它不保证**内容正确**（逆是否有效、键是否可交换，F-059）、**外部效应**（emission 不可撤回，F-066），也不保证**有环 / 失败 / 无界迭代**场景仍可进展。

> 本篇事实依据：F-051 – F-057、F-059、F-066、F-068、F-072。下一篇：[09 · Cordis 实现](09-implementation-cordis.md)。
