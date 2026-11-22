---
type: "Wiki Tutorial"
title: "09 · Cordis 实现：从 Table 2 到 Algorithm 10"
description: "三层架构、ctx.effect 单一原语、三个符号槽、Algorithm 1–10、HMR 三阶段与 Koishi 证据等级"
tags: [spatiotemporal-composability, cordis, implementation, hmr, tutorial]
sources:
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 §5、Table 2、Algorithm 1–10
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
---

# 09 · Cordis 实现：从 Table 2 到 Algorithm 10

> 一句话：Cordis 把论文的单一原语 `ctx.effect`、三个符号槽与惯性状态机落到 TypeScript，并用 HMR 三阶段把「配置即唯一真相源」变成可观察行为。

## 1. 三层架构（F-058）

§5 把实现分为 **core library / component loader / 应用框架（Koishi）** 三层。Table 2 给出理论符号与运行时名称的对应，完整表见 [理论符号 ↔ Cordis API 映射全表](../references/theory-api-mapping.md)，此处只摘最关键的：

| 理论 | 实现 |
|---|---|
| `Γ∞` | `ctx`，一等公民上下文 |
| `𝔈Γ`、`ℑΓ` | `Effect` 回调，返回或产出 inverse |
| `effectΓ(e)` | `ctx.effect(callback)` |
| `Σ` | `ctx[@@store]` |
| `ω` / `target(γ,n)` | `fiber.committed` / `fiber.target` |
| `inertia` | `fiber.inertia` |

## 2. 单一原语与「不校验」

§5.1.1（F-059）：**所有上下文变更经 `ctx.effect`**，它同时接受 `𝔈Γ` 与 `ℑΓ`，是 `effectiter_Γ` 的实现。运行时**不校验 witness**：逆真能回退、键上操作可交换，均为组件作者义务。

Algorithm 1 的 `execute`（F-060）在每次迭代前检查 guard，把产出的逆以**前置方式 LIFO 累积**；`ctx.effect` 的 `armed` 标志使 `dispose` 至多触发一次。这正是 [04](04-revertible-effects.md) 的 `trackΓ` 与 [07](07-dynamic-composition-calculus.md) 的 `L-Iter` 在代码里的形状。

## 3. 三个符号槽与通知（F-061）

`@@store` / `@@isolate` / `@@intercept` 承载 `Σ`、`Σ_iso`、`Σ_inter`；`ctx.get` 走两层解析（F-039、F-040）。Algorithm 3 的 `notify` 只对「键在 `fiber.inject` **且** realm 相同」的 fiber 调用 `refresh`——这是 [05](05-reactive-coeffects.md) notify 三分类的筛选条件，也是隔离域不会误通知的保证点。

## 4. 实例化、惯性与访问检查

- **Algorithm 4**（F-062）：`ctx.use` 的实例化被实现为**父 fiber 的一个被追踪效应**，其逆把子 fiber 的 target 置 `⊥` 并触发 unload。把「装载子插件」本身也做成可逆效应，是整套模型能自洽的关键一环。
- **Algorithm 5**（F-062）：`refresh` / `reload` / `unload` 互相递归实现惯性。三处 ordering 落点：Line 10 先标 `UNLOADING`、Line 14 提交 committed view、Line 25 等待依赖者进入 `INACTIVE` 后才执行 `dispose`。对应 Theorem 70（F-053）。
- **Algorithm 6**（F-063）：Proxy 沿 fiber 链向上解析属性；「声明但未提交」抛 `INACTIVE_ACCESS`，到根仍未声明抛 `UNDECLARED_ACCESS`。

## 5. HMR 三阶段（F-064）

**Definition 81** 定义 entry 六字段 `id / url / isolate / intercept / config / disabled`。§5.2.1 按**字段差异**分派最小扰动操作：`isolate` 重指派 realm、`intercept` 原地更新且不触发 reload。

§5.2.2 把热更新分三阶段，Algorithm 7–10 分别对应：

| 阶段 | 算法 | 作用 |
|---|---|---|
| 模块分类 | 7 `patch_isolation`、8 `classify` | accepted / declined 不动点分类 |
| 陈旧条目检测 | 9 `detect` | 按依赖树检测陈旧 entry |
| 事务化重载 | 10 `reload` | 缓存失效 + 备份 + 失败回滚 |

论文强调这一过程**无需开发者标注 acceptance boundary**——边界由依赖声明与可逆效应自动确定。

## 6. 证据等级：Koishi 案例该怎么读

§5.3（F-065）：Koishi 有**四年开发史**与 **4000+ 社区插件**，服务端与 Web 控制台是两个独立 Cordis 应用；脚注 4 说明 Koishi 当前用 **Cordis v3**，论文呈现 **v4**，核心组合模型两版共享。

> ⚠️ **不要把这当作「已验证有效」的证据**。论文 Threats to validity 明确写明：这是**单生态、单宿主语言、观察性**证据，**不是对照实验**。本包据此把 [回程同源](../references/pattern-return-ticket-with-effect.md) 标为 `maturity: L1`、`validation_count: 1`，不宣称跨项目已复现。同时论文把「自我演化 Agent Harness」列为 §8 的**未来验证方向**（F-072），不是已完成的实证。

## 7. 与既有包的分工

本包讲的是**论文里描述的算法**，不是仓库源码。要看 `packages/core/src/fiber.ts` 的真实类型定义、`@Inject` 装饰器与 `disposable` 形态，请转 [cordis/concepts/effects-coeffects.md](../../cordis/concepts/effects-coeffects.md)；API 与文件行号索引见 [cordis/references/cordis-sources.md](../../cordis/references/cordis-sources.md)。可运行示例也在兄弟包，本包不提供。

> 本篇事实依据：F-058 – F-065、F-072。下一篇：[10 · 边界与相关工作](10-boundaries-and-related-work.md)。
