---
type: Example
title: React renderer entrypoint
description: 将 React root 挂接到已有 CliRenderer，并在有限演示周期结束时分别清理 React tree 与 renderer。
tags: [opentui, react, lifecycle]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: opentui-docs
    resource: /references/official-documentation.md
    title: 官方 React binding 与生命周期文档
  - id: opentui-source
    resource: /references/source-code-snapshot.md
    title: 固定源码快照
---

# React renderer entrypoint

React binding 接收一个已经创建的 `CliRenderer`，再由 `createRoot(renderer)` 返回的 root 挂载 JSX tree。React root 与 renderer 是两个生命周期对象：`root.unmount()` 清理 React tree；创建 renderer 的应用仍负责 `renderer.destroy()`。

## 前置条件

安装 `@opentui/core`、`@opentui/react` 与兼容版本的 React，并按官方指南配置 TypeScript JSX transform，例如 `jsxImportSource: "@opentui/react"`。此示例保存为 `index.tsx`，使用 Bun 执行。

## 完整示例

```tsx
import { createCliRenderer } from "@opentui/core"
import { createRoot } from "@opentui/react"

function App() {
  return <text>Hello from React</text>
}

const renderer = await createCliRenderer({ exitOnCtrlC: false })
const root = createRoot(renderer)

try {
  root.render(<App />)
  // 用短暂演示周期使示例可运行且确定地结束。
  await new Promise<void>((resolve) => setTimeout(resolve, 750))
} finally {
  root.unmount()
  renderer.destroy()
}
```

## 生命周期解读

1. 应用创建 renderer，并将其交给 React `createRoot`。
2. `root.render(...)` 把 React component tree 提交给 OpenTUI host。
3. `root.unmount()` 运行 React tree 的 cleanup，但不会销毁 renderer。
4. `renderer.destroy()` 释放终端与 renderer 资源；renderer 销毁本身也会触发关联 React root 的 cleanup。

示例使用 750 毫秒的演示周期，避免引入未在示例中定义的应用退出协调器。长期运行的 CLI 应将 renderer 销毁接入自身信号和失败处理；`exitOnCtrlC: false` 仅用于让此短示例的关闭顺序显式可见。

## 相关概念

- [React binding 与 reconciler](/concepts/06-react-binding.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
