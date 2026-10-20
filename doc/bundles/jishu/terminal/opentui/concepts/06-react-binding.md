---
type: Concept
title: React binding 与 reconciler
description: 使用 @opentui/react 把 React tree 接入已有 CliRenderer，并区分 React root 清理和 renderer 销毁。
source: "OpenTUI React source and official React binding documentation"
tags: [opentui, react, jsx, reconciler]
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

# React binding 与 reconciler

`@opentui/react` 将 React 的声明式更新接入 OpenTUI renderable host。应用仍需从 `@opentui/core` 创建 renderer，再通过 React binding 的 `createRoot(renderer)` 建立 root。React 负责 component tree 与 hooks；renderer 负责终端 session 和其余 OpenTUI 生命周期。

## 最小连接模型

```tsx
import { createCliRenderer } from "@opentui/core"
import { createRoot } from "@opentui/react"

function App() {
  return <text>Hello from React</text>
}

const renderer = await createCliRenderer()
createRoot(renderer).render(<App />)
```

这段入口形式来自官方 React binding 指南。项目还必须设置 OpenTUI React JSX runtime（例如配置 `jsxImportSource`），并使用官方文档对应的 TypeScript/Bun 编译路径；仅复制 TSX 文件并不包含构建配置。[React bindings](https://opentui.com/docs/bindings/react/) · [entrypoint reference](https://opentui.com/docs/reference/package-entrypoints/)

## 组件与 hooks

React 包提供 OpenTUI JSX elements、hooks 和扩展组件 API。通用 keyboard/focus 语义仍由 Core interaction contract 决定；React hooks 是访问 renderer 与终端事件的框架层封装，并不改变 Core 的焦点或终端能力模型。遇到键盘事件处理顺序、Tab traversal 或 terminal-window focus，应回到 [输入、焦点和 Keymap](/concepts/04-input-focus-and-keymap.md) 核对。

自定义 renderable 可通过 React binding 提供的扩展方式纳入 JSX catalogue。类型声明、组件注册 API 与 package subpath 会随版本变化，使用前应查阅当前版本的官方 React 文档和 [entrypoint 清单](/references/package-surface.md)。

## Root 与 renderer 的关闭

`createRoot(renderer)` 返回带 `render(node)` 和 `unmount()` 的 root。`root.unmount()` 移除 React tree、运行 React effect cleanup，但 renderer 仍处于活动状态。调用 `renderer.destroy()` 会释放 renderer 并触发它关联的 React root cleanup。创建 renderer 的应用负责确保 `destroy()` 覆盖所有关闭路径。[生命周期与清理](https://opentui.com/docs/bindings/react/#lifecycle-and-cleanup) · [reconciler source](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/react/src/reconciler/renderer.ts#L29-L56)

```tsx
const renderer = await createCliRenderer()
const root = createRoot(renderer)

try {
  root.render(<App />)
  // 等待应用退出信号。
} finally {
  root.unmount()
  renderer.destroy()
}
```

上面的关闭次序显式让 React cleanup 先于 renderer shutdown。实际程序还需包含应用自己的退出信号和异步资源清理；可运行的端到端版本见 [React entrypoint 示例](/examples/03-react-entrypoint.md)。

## 何时选择 React binding

已有 React component 组织习惯、需要 React hooks 和生态整合时，React binding 可减少 UI 模型切换。若目的是先理解 OpenTUI 本身，建议从 Core renderer 与 renderable tree 起步；这样能区分 Core 契约和 React reconciler 行为。

## 相关概念

- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
- [Solid binding](/concepts/07-solid-binding.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
- [React entrypoint 示例](/examples/03-react-entrypoint.md)
