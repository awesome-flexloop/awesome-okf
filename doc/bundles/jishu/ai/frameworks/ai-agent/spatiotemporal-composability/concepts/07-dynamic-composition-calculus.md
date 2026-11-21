---
type: "Wiki Tutorial"
title: "07 · 动态组合演算：九条规则"
description: "组件三元组、fiber 七元组与四状态、九条编排/生命周期规则、target view、guard 与 confinement"
tags: [spatiotemporal-composability, calculus, lifecycle, formal-methods, tutorial]
sources:
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 §4.1–§4.2（Definition 48–55、Figure 1）
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
---

# 07 · 动态组合演算：九条规则

> 一句话：把「组件、注册表、生命周期」写成一组状态转移规则，才谈得上证明插拔顺序无关；这一篇是元理论 [08](08-metatheory.md) 的对象语言。

## 1. 静态结构

**Definition 48**（F-044）：组件是三元组 `(d, p, e)` —— 依赖规范、供给键集、配置绑定后的见证效应迭代器。约束很硬：**`p` 之外不得安装绑定**。组件不能偷偷往上下文里塞自己没声明的东西。

**Definition 49**（F-045）：fiber 是七元组 `⟨d, p, e, π, σ, τ, θ⟩`，其中生命周期状态

```
Θ ::= Inactive | Reloading(i, g, ω) | Active(g, ω) | Unloading(g, ω)
```

四种状态都携带逆累积器 `g`；`Active` 与 `Unloading` 还携带已提交的依赖解析 `ω`。

**Definition 50**（F-046）：状态携带注册表 `Fγ : 𝔑 ⇀ 𝔉Γ`，其父指针 `π` 构成以 `root` 为根的树——这就是 [06](06-context-paradigm.md) 里 `Γ∞` 递归上下文树在演算中的投影。

## 2. 九条规则（不是五个原语）

§4.2 明确「**nine rules generating two relations**」（F-047）。两类关系分别是**编排**（orchestration，改注册表）与**生命周期**（lifecycle，改 fiber 状态）：

| 类 | 规则 | 作用 |
|---|---|---|
| 编排 | `O-Insert` | 插入新组件 |
| 编排 | `O-Retire` | 标记退役 |
| 编排 | `O-Remove` | 从注册表移除 |
| 生命周期 | `L-Begin` | 依赖满足，开始激活 |
| 生命周期 | `L-Iter` | 迭代器推进一步 |
| 生命周期 | `L-Finish` | 激活完成 |
| 生命周期 | `L-Divert` | 迭代边界处条件失败，转入卸载 |
| 生命周期 | `L-Leave` | 记录停用决定 |
| 生命周期 | `L-Unload` | 应用累积器，完成回退 |

**Figure 1 只画了八条**：`O-Retire` 在四个状态上均为自环，画出来不增加信息，故省略（F-047）。

> ⚠️ 口径提醒：二手解读写成「演算定义五个原语操作 insert / retire / remove / load / unload」，把生命周期**状态名**误当规则名，且数量不对。本包按九条列出，见勘误 [E-02](../references/verification.md)。

## 3. 三个关键设计

**target view 记录名字而非值**（Definition 53，F-048）：声明键映射到**提供者名字**的映射，并定义静止判据 `quiet(γ)`。§4.2.2 给出理由：记录提供者身份，才能检出「换了一个提供等价值的新 fiber」这种变化——若只记值，值相同就会误判为无需动作。

**`L-Leave` 不立即行动，`L-Unload` 独占回退**（F-049）：`L-Leave` 只登记停用决定；`L-Unload` 是**唯一**应用 accumulator 的规则，其前提 `¬relied_n(γ)` 称为 guard。这个拆分是异步拆卸能成立的关键：先让所有依赖方走完自己的卸载，再回退提供者。Cordis 的 `unload` 在 Algorithm 5 Line 25 等待依赖者进入 `INACTIVE` 后才执行 `dispose`（F-062）。

**confinement**（Definition 55，F-050）：效应函数只能写**自身表**与其**声明键在提供方表中的值**，不得读写其他表、控制字段或未被任何键绑定的位置。这是把 [05](05-reactive-coeffects.md) 的 capability 直觉变成可证约束的一步，也是 §6.3 依赖声明构成 capability-based 访问控制的形式基础（F-067）。

## 4. 读规则时的两个习惯

1. **分清「改注册表」与「改状态」**：`O-*` 与 `L-*` 是两种关系，Figure 1 的箭头跨这两类；把它们混成一组「操作」就数不清为什么是九条。
2. **每次 transition 盯住 `ω`**：Theorem 71（Resolution coherence）证明一次 transition 的所有迭代针对**同一 resolution**（F-053）。这直接对应 §7.4 里 Cordis 与 FRP 的差异——Cordis 只保证单次 transition 不跨两个 resolution，不提供 glitch freedom（F-072）。

## 5. 与实现的最短连线

| 演算 | Cordis | 依据 |
|---|---|---|
| `d` / `p` / `e` | `fiber.inject` / `provide` / `fiber.apply` | F-058 |
| `ω` | `fiber.committed` | F-058 |
| `target(γ,n)` | `fiber.target`（由 `refresh` 重算） | F-048、F-058 |
| `L-Leave` | `refresh` 标 `UNLOADING`（Algorithm 5 Line 10） | F-062 |
| 四状态 | `fiber.state`；`LOADING` ↔ `Reloading`，`FAILED` 承载错误 | F-045 |

完整对照见 [理论符号 ↔ Cordis API 映射全表](../references/theory-api-mapping.md)，源码级讲解见 [cordis/concepts/fiber-lifecycle.md](../../cordis/concepts/fiber-lifecycle.md)。

> 本篇事实依据：F-044 – F-050、F-053、F-058、F-062、F-067、F-072。下一篇：[08 · 元理论](08-metatheory.md)——每条定理都会单列前提与「不保证什么」。
