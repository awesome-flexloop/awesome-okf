---
type: Example
title: Solid renderer entrypoint
description: 将 Solid render 挂载到应用创建的 CliRenderer，并用 renderer.destroy 触发 Solid root cleanup。
tags: [opentui, solid, lifecycle]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: opentui-docs
    resource: /references/official-documentation.md
    title: 官方 Solid binding 与生命周期文档
  - id: opentui-source
    resource: /references/source-code-snapshot.md
    title: 固定源码快照
---

# Solid renderer entrypoint

Solid binding 使用 `render(node, rendererOrConfig?)` 挂载组件。应用可以自行创建 `CliRenderer` 并将它传给 `render`；此时 renderer 所有权仍属于创建它的应用，销毁 renderer 会触发 Solid root disposal。

## 前置条件

安装 `@opentui/core`、`@opentui/solid` 与文档要求的 `solid-js` 版本。配置 Solid JSX transform，将 `jsxImportSource` 设为 `@opentui/solid`；使用 Bun 时还需按官方 setup 配置 `@opentui/solid/preload`。示例文件保存为 `index.tsx`。

## 完整示例

```tsx
import { createCliRenderer } from "@opentui/core"
import { render } from "@opentui/solid"

const App = () => <text>Hello from Solid</text>

const renderer = await createCliRenderer({ exitOnCtrlC: false })

try {
  await render(App, renderer)
  // 用短暂演示周期使示例可运行且确定地结束。
  await new Promise<void>((resolve) => setTimeout(resolve, 750))
} finally {
  renderer.destroy()
}
```

## 生命周期解读

`render(App, renderer)` 挂载 Solid tree，但不会返回 disposer。示例让应用继续持有 renderer，并在 `finally` 中调用 `renderer.destroy()`；renderer 销毁时，Solid binding 会 dispose 对应 root 并运行 `onCleanup` 回调。

示例使用短暂演示周期，而不是假设 `render()` 会返回清理函数。长期运行程序需将 `destroy()` 接入应用自己的关闭协调流程。若把配置对象传给 `render` 以让 binding 创建 renderer，所有权和访问方式不同，应依照对应版本的 Solid 生命周期文档处理。

## 相关概念

- [Solid binding 与响应式 render](/concepts/07-solid-binding.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
