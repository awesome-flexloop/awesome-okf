---
type: Concept
title: Core renderer 与 renderable tree
description: 从 createCliRenderer、root 和 renderable 对象理解 OpenTUI Core 的命令行应用结构及清理责任。
source: "OpenTUI Core source and official Core documentation"
tags: [opentui, core, renderer, renderable]
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

# Core renderer 与 renderable tree

Core 是 OpenTUI 的直接编程入口。应用先创建一个 `CliRenderer`，再向它的 `root` 添加 renderables。renderer 负责把对象树连接到 terminal input、layout/render lifecycle 与输出；renderable 则表示树中的文本、容器、输入框或其它组件。

## 创建 renderer

`createCliRenderer(config)` 是异步 factory，成功后返回 `CliRenderer`。推荐通过 factory 初始化终端；应用代码持有返回的 renderer，并在正常退出和失败路径中调用 `renderer.destroy()`。[源码签名](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/renderer.ts#L847-L847) · [Quickstart](https://opentui.com/docs/getting-started/quickstart/)

下面是核心关系的简化表达；可运行入口和完整关闭结构见 [Core hello-terminal 示例](/examples/01-core-hello-terminal.md)。

```typescript
import { TextRenderable, createCliRenderer } from "@opentui/core"

const renderer = await createCliRenderer()
renderer.root.add(new TextRenderable(renderer, { content: "Hello" }))
```

`TextRenderable` 的构造函数接收 `RenderContext` 和 `TextOptions`。这里 `renderer` 实现 render context；构造内容后，调用 root 的 `add` 将实例纳入组件树。[TextRenderable source](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/renderables/Text.ts#L9-L31)

## Renderable tree

`Renderable` 保存 parent-child 关系和布局/绘制状态。父节点可用 `add(...)` 插入子节点、用 `remove(child)` 移除子节点；树结构变化会与 native scene 的节点关系同步。节点可以具有可聚焦状态，且通过生命周期逻辑维护焦点变化。[Renderable tree source](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/Renderable.ts#L240-L287) · [add/remove source](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/Renderable.ts#L1657-L1688)

常见组件从文本与容器开始，再逐步使用 `Input`、`Textarea`、`Select`、`ScrollBox`、`Code`、`Markdown` 等更高层 renderables。实际可用项应在固定版本的 [renderables export](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/renderables/index.ts) 和官方 API reference 中核对。

## Renderer 生命周期

renderer 拥有终端 session 与关联资源。`destroy()` 停止 renderer 工作并清理终端状态，调用它的责任属于创建 renderer 的应用层。不能只移除 renderable 或卸载框架 root，就认为终端 session 已关闭。详见[生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)。

对于 React，root 的 `unmount()` 只清理 React tree，renderer 仍可继续工作；renderer 销毁会触发相应 React cleanup。Solid 也基于一个 renderer 管理其 renderable 目标，关闭时仍要遵循应用 renderer 的生命周期。

## 从 Core 继续

1. 阅读 [布局与 native 渲染](/concepts/03-layout-and-native-rendering.md)，将对象树与终端 cell frame 联系起来。
2. 阅读 [输入、焦点和 Keymap](/concepts/04-input-focus-and-keymap.md)，为 renderables 接入交互。
3. 阅读 [测试](/concepts/08-testing.md)，用 test renderer 验证 frame 和用户输入。
4. 需要声明式界面时再进入 [React](/concepts/06-react-binding.md) 或 [Solid](/concepts/07-solid-binding.md)。

## 相关概念

- [包与入口](/concepts/01-packages-and-entrypoints.md)
- [布局与 native 渲染](/concepts/03-layout-and-native-rendering.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
- [Core hello-terminal 示例](/examples/01-core-hello-terminal.md)
