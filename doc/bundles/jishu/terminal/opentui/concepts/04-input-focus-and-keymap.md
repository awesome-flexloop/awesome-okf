---
type: Concept
title: 终端输入、Renderable 焦点与 Keymap
description: 区分终端窗口焦点、Renderable 焦点、键盘分发和鼠标事件，并理解何时引入 Keymap。
source: "OpenTUI Core source and official interaction, keyboard, and Keymap documentation"
tags: [opentui, interaction, keyboard, focus, keymap]
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

# 终端输入、Renderable 焦点与 Keymap

终端交互并不直接复用浏览器 DOM 语义。OpenTUI 有 terminal-window focus report，也有当前 renderable 的 `focused` 状态；键盘和鼠标事件通过 renderer、可聚焦节点与应用定义的逻辑处理。先辨明焦点属于哪一层，通常就能更快找到“控件为什么收不到按键”的原因。

## 两种焦点状态

- **Terminal-window focus**：终端模拟器报告窗口进入或离开焦点时，renderer 可以发出相应事件。终端能力支持情况会影响这些报告。
- **Renderable focus**：renderer 跟踪当前获得键盘/paste 输入的 renderable。节点必须为 `focusable` 才能通过 `focus()` 获得焦点；焦点切换时前一个节点会 blur。

终端窗口重新获得焦点，不会自动将输入焦点转给某个 renderable。Core 也不提供自动 Tab traversal 或 focus-order 属性；应用应明确选择下一个控件并调用 `focus()`。[官方 interaction 指南](https://opentui.com/docs/core-concepts/interaction/) · [Renderable focus 实现](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/Renderable.ts#L579-L655)

## 键盘事件从哪处理

应用可以在 renderer 层监听全局按键，也可将事件交给当前 focused renderable。事件的停止传播和阻止默认动作影响后续监听与组件内建处理；输入框、文本区、列表等组件还可能有自己的按键行为。覆盖这些行为时，应先确认 handler 顺序与 `preventDefault()` 的效果。[Keyboard input](https://opentui.com/docs/core-concepts/keyboard/)

当快捷键只是一两个全局动作，直接监听 Core 键盘事件通常更简单。当命令依赖焦点、scope、模式、优先级或多键序列时，可选用 `@opentui/keymap`。该包提供 host-agnostic Keymap、command/addon 模型和 OpenTUI、React、Solid 等集成入口；选择后仍需理解它如何消费匹配事件以及如何释放资源。[Keymap overview](https://opentui.com/docs/keymap/overview/) · [包入口登记](/references/package-surface.md)

## 鼠标与可访问性

Mouse input 通过终端上 renderable 对应的 cell bounds 进行路由。鼠标 down/up 与浏览器 click 不是同一套事件模型；若应用依赖 pointer interaction，应提供键盘替代、可见焦点状态和文本标签。OpenTUI 不会为应用自动生成浏览器 accessibility tree。[Interaction](https://opentui.com/docs/core-concepts/interaction/)

鼠标行为依赖 terminal protocol 与终端模拟器能力。涉及 hover、拖拽、焦点报告或 modifier 的应用，应对 keyboard-only 使用路径进行单独设计，避免把特定终端的能力当作所有用户的保证。

## 测试交互

`createTestRenderer(options)` 提供 `mockInput` 和 `mockMouse`。它们向 parser 发送终端序列，可用于验证输入是否抵达预期 renderable、焦点是否切换，以及鼠标事件是否命中目标。更多内容见[测试](/concepts/08-testing.md)和[测试 renderer 示例](/examples/02-test-renderer-and-input.md)。

## 相关概念

- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
- [测试](/concepts/08-testing.md)
- [OpenTUI 生态包](/concepts/09-ecosystem-packages.md)
