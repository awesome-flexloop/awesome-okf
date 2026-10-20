---
type: Concept
title: Solid binding 与响应式 render
description: 通过 @opentui/solid 的 render API 将 Solid JSX 接入 OpenTUI，并理解 signals、effects 与 renderer 生命周期边界。
source: "OpenTUI Solid source and official Solid binding documentation"
tags: [opentui, solid, jsx, signals]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: source-code
    resource: /references/source-code-snapshot.md
    title: 固定源码快照
  - id: official-docs
    resource: /references/official-documentation.md
    title: 官方文档
---

# Solid binding 与响应式 render

`@opentui/solid` 提供 Solid renderer/reconciler，将 Solid JSX 组件挂到 OpenTUI host。官方入门形式是从包中导入 `render`，再传入一个返回 JSX 的函数。Solid 的 signals 和 effects 维持响应式更新；JSX 最终仍由 OpenTUI renderable/native scene 与终端帧流程承载。

## render API

```tsx
import { render } from "@opentui/solid"

const App = () => <text>Hello, Solid!</text>

await render(App)
```

这个 API 及其示例由官方 Solid 指南给出。Solid 项目还需把 JSX transform 指向 `@opentui/solid` 并采用该包要求的 universal preset/config；Bun plugin 和 preload 是不同入口，不能当作同一个 import 使用。[Solid bindings](https://opentui.com/docs/bindings/solid/) · [package entrypoints](https://opentui.com/docs/reference/package-entrypoints/)

## 响应式更新

Solid hooks 源码使用 Solid 的 `createSignal`、`createEffect` 等原语，OpenTUI reconciler 则创建 renderer adapter 并将更新落实到 host 节点。这样一来，组件的响应式依赖和终端渲染对象变更处于相连但不同的层次：signals 决定何时更新，OpenTUI host 负责把组件结果映射到 renderable tree。

不要把 Solid DOM renderer 的假设直接套用到终端 host。终端焦点、键盘事件、mouse handling、layout 与 renderer cleanup 仍需遵守 OpenTUI 自己的 Core 契约。

## Renderer ownership 与 teardown

官方文档的 `render()` 会等待初始 mount，但这不代表应用外部资源和终端 renderer 已自动关闭。文档区分传入现有 renderer 与由 render config 创建 renderer 等情形，也要求应用在 shutdown 时调用 `renderer.destroy()`。精确的 render options 和返回约定须按所用版本的 [Solid lifecycle guide](https://opentui.com/docs/bindings/solid/) 核实。

要把 Solid cleanup 放入完整应用退出流程，需同时考虑组件 cleanup 与 renderer 所有权；示例见 [Solid entrypoint](/examples/04-solid-entrypoint.md)。示例明确初始化和销毁，不用一个未经核实的返回值来推导 dispose API。

## 与 React 的区别

React 通过 `createRoot(renderer).render(node)` 显式挂接已有 renderer；Solid 以 `render(node)` 为主要入口，并有自己的 JSX transform、响应式模型和测试 API。两者共享 OpenTUI Core/native rendering 与 terminal interaction，不代表其初始化、root teardown 或 package subpath 相同。[React binding](/concepts/06-react-binding.md)

## 相关概念

- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
- [React binding](/concepts/06-react-binding.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
- [Solid entrypoint 示例](/examples/04-solid-entrypoint.md)
