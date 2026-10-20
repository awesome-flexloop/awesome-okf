---
type: Example
title: Core 最小终端程序
description: 用 createCliRenderer 和 TextRenderable 创建终端输出，并通过退出键与 Ctrl+C 关闭 renderer。
tags: [opentui, core, quickstart]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: opentui-docs
    resource: /references/official-documentation.md
    title: 官方 Quickstart
  - id: opentui-source
    resource: /references/source-code-snapshot.md
    title: 固定源码快照
---

# Core 最小终端程序

这个最小示例从 Core 创建终端 renderer，在根节点挂载一个文本 renderable，并监听 `q` 退出。示例遵循官方 Quickstart 的 Bun/TypeScript 运行方式；renderer 创建方负责在退出时调用 `destroy()`。

## 前置条件

在项目中安装 `@opentui/core`，并使用 OpenTUI 官方文档支持的 Bun、Node 与平台组合。以下文件使用 TypeScript 顶层 `await`，保存为 `index.ts` 后可通过 `bun index.ts` 运行。

## 完整示例

```typescript
import { TextRenderable, createCliRenderer } from "@opentui/core"

const renderer = await createCliRenderer({
  exitOnCtrlC: true,
})

renderer.root.add(
  new TextRenderable(renderer, {
    content: "Hello, OpenTUI! Press q to quit.",
  }),
)

renderer.keyInput.on("keypress", (key) => {
  if (key.name === "q") {
    renderer.destroy()
  }
})
```

`createCliRenderer()` 返回一个异步创建的 `CliRenderer`。`renderer.root.add(...)` 把 renderable 放进根树；键盘事件通过 `renderer.keyInput` 分发。按 `q` 会显式销毁 renderer，`exitOnCtrlC: true` 则启用 Ctrl+C 关闭路径。

## 验证边界

此示例覆盖 Core API 的最小挂载和正常关闭路径。它不声明所有异常退出信号都已处理；真实 CLI 若有额外资源，应把它们纳入应用自己的关闭流程。`renderer.destroy()` 的生命周期语义见[生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)。

## 相关概念

- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
- [输入、焦点和 Keymap](/concepts/04-input-focus-and-keymap.md)
