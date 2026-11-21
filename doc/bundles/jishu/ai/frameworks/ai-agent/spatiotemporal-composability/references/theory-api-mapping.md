---
type: Reference
title: "理论符号 ↔ Cordis API 映射全表"
description: "论文 Table 2 与 Algorithm 1–10 的中文对照索引，供读者从形式化定义跳到工程实现"
tags: [spatiotemporal-composability, cordis, api, mapping, algorithm]
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
sources:
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 §5、Table 2
---

# 理论符号 ↔ Cordis API 映射全表

> 本表是论文 Table 2（F-058）的中文整理，符号列保留论文记法，实现列使用 §5 引入的运行时名称。源码级 API 与行号请转 [cordis/references/cordis-sources.md](../../cordis/references/cordis-sources.md)。

## 1. 上下文与效应

| 理论符号 | 含义 | Cordis 实现 |
|---|---|---|
| `Γ∞` | 统一上下文类型 | `ctx`，一等公民上下文 |
| `γ ∈ Γ` | 上下文树与系统触及的全部状态 | context tree + 运行时状态 |
| `𝔈Γ`、`ℑΓ` | 效应函数 / 效应迭代器 | `Effect` 回调，返回或产出 inverse |
| `effectΓ(e)` | 把效应提升到效应上下文 | `ctx.effect(callback)` |
| `Σ`、`Σ_iso`、`Σ_inter` | 协同效应上下文及其隔离 / 拦截变体 | `ctx[@@store]`、`ctx[@@isolate]`、`ctx[@@intercept]` |
| `get(k)`、`set(k,v)` | 依赖读写 | `ctx.get(key)`、`ctx.set(key, value)` |
| `isolate(k,r)` | 隔离域指派 | `ctx.isolate(key, realm)` |
| `intercept(k,ν)` | 元数据合并 | `ctx.intercept(key, metadata)` |
| derived realization | 派生上下文、恒等逆 | `fiber.ctx`，子上下文，dispose 时整体丢弃 |

## 2. 组件、Fiber 与生命周期

| 理论符号 | 含义 | Cordis 实现 |
|---|---|---|
| `⟨d,p,e,π,σ,τ,θ⟩` | fiber 七元组 | `fiber` |
| `dom(Fγ)` | 注册表名字域 | 经 `ctx.registry` 枚举 |
| `n : 𝔑` | fiber 名字 | `fiber.uid` |
| `d : 𝔇Γ` | 依赖规范 | `fiber.inject` |
| `p : 𝔓Γ` | 供给键集 | 组件的 `provide` |
| `e : ℑ_{d∪p}Γ` | 配置绑定后的效应迭代器 | `fiber.apply` |
| `π` | 父 fiber | `fiber.parent.fiber.uid` |
| `θ` | 四状态生命周期 | `fiber.state`；`LOADING` 对应 `Reloading`，`FAILED` 承载错误 outcome |
| `g`（accumulator） | 逆的累积器 | `fiber.dispose` |
| `ω`（committed view） | 已提交的依赖解析 | `fiber.committed` |
| `provider_k(γ)` | 键的提供者 | `Impl`，其 provider fiber 处于 `ACTIVE` |
| `target(γ,n)` | 目标视图 | `fiber.target`，由 `refresh` 重算；`⊥` 对应 `INACTIVE` |
| `inertia` | 在途异步迁移 | `fiber.inertia` |

## 3. 演算规则 ↔ 运行时动作

| 规则 | Cordis 中的对应动作 |
|---|---|
| `O-Insert`、`O-Retire` | `ctx.use` 与其回调返回的逆（Algorithm 4） |
| `O-Remove` | fiber 从 runtime 中移除，`uid` 清空 |
| `L-Begin` / `L-Iter` / `L-Finish` | `execute` 的迭代循环（Algorithm 1） |
| `L-Divert` | 迭代边界处 guard 失败；或 `reload` 链式转入 `unload` |
| `L-Leave` | `refresh` 把 fiber 标为 `UNLOADING`（Algorithm 5 Line 10） |
| `L-Unload` | `unload` 及其惯性链接（Algorithm 5） |
| `L-Unload` 的 guard | `unload` 等待被通知的依赖者进入 `INACTIVE`（Line 25） |
| `failure`（§4.4） | 错误记录在 fiber 上，target 置 `⊥` |

## 4. 算法索引（Algorithm 1–10）

| 编号 | 位置 | 作用 |
|---|---|---|
| Algorithm 1 | §5.1.1 | `execute` / `effect`：guard 检查、LIFO 累积逆、`armed` 一次性触发 |
| Algorithm 2 | §5.1.2 | `get` / `set`：两层解析与 `notify` 成对调用 |
| Algorithm 3 | §5.1.2 | `notify`：按 `inject` 与 realm 匹配筛选受影响 fiber |
| Algorithm 4 | §5.1.3 | `use`：把实例化实现为父 fiber 的被追踪效应 |
| Algorithm 5 | §5.1.3 | `refresh` / `reload` / `unload`：惯性状态机与三处 ordering 落点 |
| Algorithm 6 | §5.1.4 | `resolve`：Proxy 沿 fiber 链解析属性并做访问检查 |
| Algorithm 7 | §5.2.1 | `patch_isolation`：用 delimiter 判定绑定归属并重指派 realm |
| Algorithm 8 | §5.2.2 | `classify`：accepted / declined 不动点分类 |
| Algorithm 9 | §5.2.2 | `detect`：按依赖树检测陈旧 entry |
| Algorithm 10 | §5.2.2 | `reload`：缓存失效 + 备份 + 失败回滚的事务化重载 |

> 上表为**论文给出的伪代码索引**，不是可运行代码。本包不提供部署实测；可运行示例见兄弟包 [cordis/examples/](../../cordis/examples/create-basic-plugin.md)。
