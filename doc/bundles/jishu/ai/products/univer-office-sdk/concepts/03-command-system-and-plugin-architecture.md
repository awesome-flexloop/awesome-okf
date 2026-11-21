---
okf_version: "0.2"
type: Concept
title: "命令系统与插件架构：撤销为什么不会乱"
description: "Command/Mutation/Operation 三类动作、跨特性变更的撤销合成、changesets 与 OT、插件分层与 interceptor 扩展点"
tags: [univer, command-pattern, mutation, undo-redo, ot, plugin-architecture]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-20T10:15:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/7WCDC4R7mxqFRHMP0Zf9hA
  - id: official-readme
    url: https://github.com/dream-num/univer/blob/dev/README.md
---

# 命令系统与插件架构：撤销为什么不会乱

> 概念层（Why / Architecture）。博文用「在开着筛选的区域插入一行」这个例子讲清了 Univer 最难被替代的部分——本文把它还原为可迁移的架构原则。

## 问题本质：难的不是功能，是功能之间的牵连

单个功能（插一行、改筛选范围）都好写。麻烦在于一次业务动作会**同时影响多个特性的状态**：在筛选区域内插入一行，表格内容变了，筛选范围也得跟着变；用户按撤销，两样必须一起回退（F-032/F-033）。

如果每个插件各自记一条撤销记录，用户就得按两次撤销，且中间态可能不一致。Univer 的解法是：**由 Command 统一编排，各特性只贡献变更与逆变更，合成一条历史记录**（F-034/F-068）。

## 三类动作（官方逐字定义）

| 动作 | 职责 | 是否进快照 |
|------|------|-----------|
| **Command** | 编排一次业务操作及其所需变更；可收集各插件交上来的改动 | 本身不进 |
| **Mutation** | 真正改内容的变更，参数可序列化，是快照与协同的基本单位 | ✅ 进 |
| **Operation** | 只改临时状态（滚动位置、打开了哪个面板等） | ❌ 不进 |

（F-035~F-037、F-068）

这条分界很关键：**只有 Mutation 才会被持久化、被协同、被撤销**。UI 状态用 Operation，内容变更用 Mutation，业务编排用 Command——三者混用会导致快照污染或撤销失效。

## 撤销合成与协同

- **撤销合成**：特性实现提供 forward mutations 与对应 inverse mutations，Command 通过 `IUndoRedoService` 记录；当一个动作影响多个特性时，把它们的变更和撤销数据合并为**单条** undo/redo 记录（F-068）。
- **协同**：把 mutations 打包成 **changesets**，对并发变更做 **OT（operational transformation）**，管理已确认 revision 与 snapshot；历史可由一个 snapshot 加后续 changesets 重建（F-038/F-068）。

> 注意：博文说"实时协同也建在 Mutation 之上"是对的，但**协同能力本身属于 Server SDK 商业扩展**（F-062）。开源仓库提供的是命令/Mutation 这套可组合的机制，不是开箱即用的多人协同服务。

## 插件分层与扩展点

官方 README 的结构（F-039/F-068）：

```
Core / 渲染引擎 / 公式引擎        ← 引擎层
        ↓
Sheets、Docs 产品插件             ← 内容类型层
        ↓
筛选、数据验证等功能插件          ← 特性层（逻辑 Controller 与 UI Controller 各拆）
```

- 每个插件可含 **Controllers**（逻辑 Controller 协调内容变更，UI Controller 接菜单/快捷键/交互）与 **Services**（如面板状态）；
- UI 基础由 `@univerjs/design`（组件与样式）、`@univerjs/ui`（菜单/快捷键/面板/组件注册）、`@univerjs/icons` 提供；
- **Interceptors 与 reference-range handlers** 是特性协作的正式扩展点，插件在此贡献检查或关联 mutations，优先级决定顺序（F-068）；
- 官方提供 [filter implementation walkthrough](https://docs.univer.ai/blog/anatomy)，博文"照着筛选插件把结构抄一遍"的建议由此而来（F-040）。

引擎层也是共享的：单元格内富文本复用了 Docs 的布局与渲染能力，自定义特性可直接基于公式引擎与 Canvas 渲染引擎构建，不必另起一套内容栈（F-068）。

## 可迁移的架构原则

1. **把"一次用户意图"作为事务边界**，而非把"一次数据写入"作为边界——撤销记录的粒度应等于用户感知的动作粒度。
2. **区分可持久化变更与临时状态**，否则快照会被 UI 状态污染、协同会同步不该同步的东西。
3. **让特性通过扩展点贡献变更，由编排者统一合成**，避免特性之间互相硬编码依赖；新增特性时无需修改既有特性的撤销逻辑。
4. **测试策略随之分层**：模型与服务独立测、依赖经 DI 替换、对"组合动作 + 撤销"补回归用例（官方 filter controller 测试即此思路，F-068）。

## 阅读下一篇

- [04 · AI agent 治理与生态](04-agent-governance-and-ecosystem.md)——同一套命令系统如何变成 agent 的权限闸门
- [05 · 选型与可迁移模式](05-selection-and-transferable-patterns.md)
