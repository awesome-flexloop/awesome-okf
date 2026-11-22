---
type: "Wiki Tutorial"
title: "10 · 边界、限制与相关工作"
description: "内外边界判据与 acquisition/emission、capability 限制、依赖环与名义链接，以及和四类相关工作的对比"
tags: [spatiotemporal-composability, boundaries, related-work, limitations, tutorial]
sources:
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 §6–§8
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
---

# 10 · 边界、限制与相关工作

> 一句话：这套模型有清晰的系统边界，越界的东西不回滚；它也不是通用可逆计算，而是「运行期组件装卸」这一窄问题的结构性方案。

## 1. 内外边界判据（§6.1，F-066）

论文给了一条可操作的判据，而不是凭直觉区分：

> 位置在系统**能独占修改且能恢复原状**时属「内」，否则属「外」。

外部操作按 `idΓ` 处理，并分两阶段：

| 阶段 | 例子 | 可逆性 |
|---|---|---|
| `acquisition` | `open` / `malloc` / `fork`：在系统内**安装一条记录** | 可逆 |
| `emission` | `write` / `send`：把数据推过边界 | **不可逆** |

这解释了为什么 [08](08-metatheory.md) 的 recovery exactness 只到观测等价：撤回的是「记录」，不是「已经发出去的字节」。设计系统时应尽早把不可逆动作推迟到边界之外，或显式接受它不可回滚。

## 2. 安全模型与它的终点（§6.3，F-067）

依赖声明构成 **capability-based 访问控制**：`inject` 是能力请求，context proxy 是能力中介，confinement（F-050）限定可写位置。但论文明确：**不可信代码的沙箱需要语言之外的执行边界**。也就是说这套机制解决的是「能力是否被正确分发」，不是「恶意代码能否逃逸运行时」。

## 3. 三条实打实的限制

| 限制 | 内容 | 出处 |
|---|---|---|
| 依赖环 | `≺` 有环使相关组件**永久 inactive**，但可从声明**静态预测**；把双向交互分解为细粒度集成组件时，其数量最坏随 n **二次增长** | F-068 |
| 名义链接 | 形式模型只提供按 key 的名义链接，缺版本 / 结构链接 ⇒ 接口漂移与键碰撞；应对为键命名空间、peer dependencies（Cordis 当前采用）、结构兼容性，属缓解非保证 | F-069 |
| 不校验见证 | 逆是否有效、键上操作是否可交换，运行时均不检查 | F-059 |

再加上 Theorem 80 **只谈状态不谈过程期间 emissions**（F-056），以及 Cordis **无 FRP 式 glitch freedom**、只保证单次 transition 不跨两个 resolution（F-072），共同构成这套方法的适用边界。

## 4. 相关工作对比（§7）

| 对比对象 | 论文指出的差异 | 出处 |
|---|---|---|
| dagger / inverse arrows（Heunen 等） | 论文要求的是**单侧逆**、**运行时追踪**，且不要求整个计算可逆 | F-070 |
| COP（context-oriented programming） | COP 的 layer 既不追踪也不回退副作用，激活**不由依赖满足度驱动** | F-071 |
| AOP | coeffect 是组件**显式声明**的横切点，而非 oblivious 的 pointcut | F-071 |
| FRP | glitch freedom 在 Cordis **无对应物**；Cordis 只保证单次 transition 的 resolution 一致性 | F-072 |

§7.3 的 **Interposed reclamation**（Nooks 在内核与可加载扩展边界插入 object tracker、shadow drivers 从另一侧记录请求与配置）是同一思路的近亲：都靠**运行时保存回收记录**而非扩展作者手写清理。差别在记录由平台按资源类型固定，而 Cordis 让组件自带每个原子效应的逆。该迁移分析见 [回程同源](../references/pattern-return-ticket-with-effect.md)。

## 5. 未来方向（§8，F-072）

论文把**自我演化 Agent Harness** 列为未来验证方向。这一句被二手解读频繁放大成「已在 DeepSeek Harness 上验证」——按论文原文，它是**动机举例与未来工作**，不是已完成的实证。

同样要注意：本包与 [deepseek-harness](../../deepseek-harness/index.md) 是「理论」与「产品落地」两条线，互不作为对方的验证证据；论文自身对 Koishi 案例的 Threats to validity 声明见 [09](09-implementation-cordis.md)。

## 6. 适用性自检

在把这套模型迁到别的系统前，逐条问：

- 共享位置能否 reify 成**带类型的键**，且系统能独占修改？（§6.1、F-034、F-050）
- 副作用能否在产生处**就地交出逆**？跨边界的 emission 占比多大？（F-024、F-066）
- 依赖拓扑是否**无环**、迭代器步数是否**有界**？（Theorem 73 前提，F-054）
- 键上操作是否**可交换**？有序链一类的键怎么办？（F-043）
- 团队能否接受「运行时不校验见证」这一纪律成本？（F-059）

任一问答不上来，就不该直接套用 [回程同源](../references/pattern-return-ticket-with-effect.md) 的检验标准。

> 本篇事实依据：F-050、F-056、F-059、F-066 – F-072。下一篇：[11 · 学习路径](11-learning-path.md)。
