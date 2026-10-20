---
type: Concept
title: Test renderer 与交互测试
description: 使用 @opentui/core/testing 创建隔离 renderer，驱动输入与鼠标事件，并断言渲染帧及清理行为。
source: "OpenTUI test renderer source and official testing documentation"
tags: [opentui, testing, test-renderer, input]
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

# Test renderer 与交互测试

OpenTUI Core 提供 `@opentui/core/testing`，以测试 renderer 验证 renderable tree、终端输入、鼠标交互和 frame 内容。测试代码无需默认接管真实 terminal；可用 mock drivers 驱动同一条 parser/renderer 逻辑，再根据断言目标决定是否需要覆盖真实 output transport。

## 创建测试环境

`createTestRenderer(options)` 要求一个 options 对象。`TestRendererOptions` 扩展 `CliRendererConfig`，另有 width、height 和键盘能力相关参数。返回的 setup 提供 renderer、mock input/mouse、render/flush/wait helpers、frame capture、resize 与 disposal 能力。[Test renderer API](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/testing/test-renderer.ts#L14-L72) · [official testing](https://opentui.com/docs/core-concepts/testing/)

## 输入和帧断言

- 用 `mockInput` 驱动按键、文本、modifier 或 paste 输入。
- 用 `mockMouse` 产生 pointer/mouse terminal input。
- 用 `renderOnce()`、`flush()` 或 `waitFor...()` 等 helper 推进/等待测试 renderer。
- 用 `captureCharFrame()` 断言字符帧；需要颜色和 style span 时选择 `captureSpans()`。

应根据测试目标选择 wait helper：断言最终字符帧与断言某一瞬间的状态不是同一件事；有动画或异步组件时，等待条件应可观察且带合理超时。

## 资源清理

测试必须负责清理 setup。可在 `finally` 中调用 `setup.renderer.destroy()`，或等待 `setup.dispose()`；返回对象还声明了 `Symbol.asyncDispose`。每个测试独立创建 renderer，避免焦点、输入状态或 native scene 泄漏到后续用例。[setup types](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/testing/test-renderer.ts#L53-L72)

默认 in-memory test sink 适合验证 frame 和交互。若测试目的是验证自定义 stream 或真实 transport，应使用官方 testing 文档明确说明的配置路径，不要从内存帧断言推断终端写入已成功。

## Framework 测试

Core 提供基础 test renderer；React 和 Solid 还提供框架相关的 test helpers。React 官方入口包括 `@opentui/react/test-utils` 的 `testRender()`；Solid 包有自己的 `testRender` API。检查框架行为时使用对应 binding 的 harness，以便断言 JSX reconciliation、hooks/signals 和 framework cleanup，而不是只测试 Core node。

## 示例

[Test renderer 与输入示例](/examples/02-test-renderer-and-input.md)给出 setup、mock input、frame capture 与 finally cleanup 的完整流程。API 细节可对照官方 [Testing](https://opentui.com/docs/core-concepts/testing/) 文档和固定 commit 的 test renderer 源码。

## 相关概念

- [输入、焦点和 Keymap](/concepts/04-input-focus-and-keymap.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
- [Test renderer 与输入示例](/examples/02-test-renderer-and-input.md)
