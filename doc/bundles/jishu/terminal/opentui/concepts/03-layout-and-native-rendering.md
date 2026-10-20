---
type: Concept
title: Layout、native scene 与终端帧渲染
description: 沿 renderable tree、Yoga layout、cell painting、frame encoding 和 output delivery 追踪 OpenTUI 的渲染路径。
source: "OpenTUI native source and official native rendering documentation"
tags: [opentui, native, zig, yoga, rendering]
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

# Layout、native scene 与终端帧渲染

OpenTUI 把应用对象树转换为终端 cell 的过程跨越 TypeScript Core 与 Zig native scene。阅读渲染机制时，建议把“描述界面”“计算布局”“绘制 cell”“交付输出”分开；这些阶段有不同的状态、执行边界和可观察结果。

## 从 renderable 到 native scene

Core `Renderable` 暴露 parent-child 结构与属性；native `Scene` 保存绘制节点、parent relation 及与 Yoga 节点关联的布局信息。scene 的插入、重排、移除路径会更新 Yoga child relation。[Core tree](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/Renderable.ts#L1657-L1781) · [native scene](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/native/src/scene.zig#L232-L241)

这不是两个互不相关的 UI 树。TypeScript 层承载可供应用操控的 renderables；native scene 参与 layout、geometry、clipping、paint order 和 cell painting。对具体属性或节点变更，应从调用 API 沿对应的 native bridge 继续读，而不是仅凭同名字段推断 native 行为。

## Yoga layout 与 terminal cells

Yoga 为 scene 中的节点计算位置和尺寸。官方 native overview 以“一节点对应一个 Yoga node”解释布局路径；布局结果再提供屏幕位置、裁剪边界等绘制输入。native 绘制工作面向 cell 网格，而不是像素画布。Unicode 文本宽度也必须按 terminal cell 规则处理，不能简单用 UTF-8 字节数代替显示宽度。[Native rendering](https://opentui.com/docs/native/overview/) · [Frames and output](https://opentui.com/docs/native/frames/)

## 一帧的阶段

可将核心路径概括为：

1. 宿主驱动应用与 renderer 的工作。
2. Native Scene 处理布局准备和 frame state。
3. 结合 Yoga 结果、paint 属性、顺序和 clipping 绘制 cell。
4. 将变更编码成终端输出数据。
5. 通过当前宿主的输出路径交付数据。

官方文档明确将 paint、frame submit/commit 和 output delivery 分开讨论。即使某阶段成功，也不能据此断言终端设备最终已显示该 frame。native frame 流程还包含同步的 layout、allocation、排序、paint-list preparation、painting 和 encoding 工作；不要笼统描述成全部在后台 worker 中异步完成。[Frames and output](https://opentui.com/docs/native/frames/)

## Host 与 native 的边界

OpenTUI 使用宿主 event loop 进行调度与终端输入。native library 不负责启动应用事件循环或 rendering worker；宿主提供 I/O 与时间推进，native 层处理 scene/layout/paint 等工作。自定义宿主、worker 输出或非标准 writable stream，需要结合 output tickets 和 host I/O 文档确定缓冲与确认语义。[Host I/O and time](https://opentui.com/docs/native/host-io-time/) · [Native rendering](https://opentui.com/docs/native/overview/)

## 何时深入 Zig 实现

普通应用开发可以先停留在 Core renderables 和官方 layout APIs；只有需要调试测量函数、裁剪、绘制顺序或输出传输时，才沿 `packages/native/src/scene.zig`、`renderer.zig`、session/context ABI 深入。保持事实粒度：公开契约来自官方 API 和 Core 类型，内部实现描述须固定到对应源码 commit。

## 相关概念

- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
- [输入、焦点和 Keymap](/concepts/04-input-focus-and-keymap.md)
- [Native frames 示例](/examples/05-native-rendering-boundaries.md)
- [源码快照登记](/references/source-code-snapshot.md)
