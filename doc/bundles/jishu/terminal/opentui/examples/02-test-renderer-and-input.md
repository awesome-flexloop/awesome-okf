---
type: Example
title: Test renderer 与键盘输入
description: 通过 test renderer 渲染字符帧并注入方向键，验证可观察输出和 renderer 清理。
tags: [opentui, testing, keyboard]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: opentui-docs
    resource: /references/official-documentation.md
    title: 官方 Testing 文档
  - id: opentui-source
    resource: /references/source-code-snapshot.md
    title: 固定源码快照
---

# Test renderer 与键盘输入

`createTestRenderer(options)` 提供真实 Core renderer、mock keyboard input 与 frame capture。默认输出写入内存 sink，不接管真实终端；此示例同时断言字符帧和一个键盘事件，并在 `finally` 中销毁 renderer。

## 完整示例

```typescript
import assert from "node:assert/strict"
import { TextRenderable } from "@opentui/core"
import { KeyCodes, createTestRenderer } from "@opentui/core/testing"

const setup = await createTestRenderer({ width: 30, height: 5 })

try {
  setup.renderer.root.add(
    new TextRenderable(setup.renderer, { content: "Ready for input" }),
  )

  let lastKey = ""
  setup.renderer.keyInput.on("keypress", (key) => {
    lastKey = key.name
  })

  setup.mockInput.pressKey(KeyCodes.ARROW_LEFT)
  await setup.renderOnce()

  const frame = setup.captureCharFrame()
  assert.ok(frame.includes("Ready for input"))
  assert.equal(lastKey, "left")
  console.log(frame)
} finally {
  setup.renderer.destroy()
}
```

## 观察与边界

- `renderOnce()` 推进一次测试 renderer 的渲染循环；完成后 `captureCharFrame()` 读取已提交帧中的字符。
- `mockInput.pressKey(...)` 向 renderer 的输入路径发送键盘事件；此例用 `renderer.keyInput` 观察解析后的按键名称。
- `setup.renderer.destroy()` 是同步关闭路径；也可使用 setup 暴露的 `dispose()` 等待 `renderer.closed`。
- 字符帧和 mock 输入验证的是 renderer、native session 与 parser 路径，不等价于真实终端 transport 的端到端验证。

若断言涉及样式或颜色，可将 `captureCharFrame()` 换为 `captureSpans()`；若需要验证 host output transport，应按官方 testing 文档选择对应配置，而不要从内存 sink 推断终端写入结果。

## 相关概念

- [Test renderer 与交互测试](/concepts/08-testing.md)
- [输入、焦点和 Keymap](/concepts/04-input-focus-and-keymap.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
