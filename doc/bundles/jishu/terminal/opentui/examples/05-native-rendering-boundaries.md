---
type: Example
title: 观察 native-backed cell frame
description: 用 Core test renderer 观察经过 native session 的字符帧，并明确区分内存输出 sink 与真实终端 transport。
tags: [opentui, native, rendering, testing]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: opentui-docs
    resource: /references/official-documentation.md
    title: 官方 Native rendering、frames 与 testing 文档
  - id: opentui-source
    resource: /references/source-code-snapshot.md
    title: 固定源码快照
---

# 观察 native-backed cell frame

这个示例使用公开的 Core test renderer 创建 renderable、推进一帧并检查字符输出。test renderer 仍创建 native Session 与 scene；默认输出 sink 位于内存，因此它适合观察帧内容，却不能证明真实终端 transport 已成功写入或设备已显示该帧。

## 完整示例

```typescript
import assert from "node:assert/strict"
import { TextRenderable } from "@opentui/core"
import { createTestRenderer } from "@opentui/core/testing"

const setup = await createTestRenderer({ width: 30, height: 5 })

try {
  setup.renderer.root.add(
    new TextRenderable(setup.renderer, {
      content: "Native-backed cell frame",
    }),
  )

  await setup.renderOnce()
  const frame = setup.captureCharFrame()

  assert.ok(frame.includes("Native-backed cell frame"))
  console.log(frame)
} finally {
  setup.renderer.destroy()
}
```

## 沿输出路径阅读

| 阶段 | 本例中可定位的对象 | 可以得出的结论 |
|---|---|---|
| 应用对象树 | `renderer.root.add(TextRenderable)` | Core renderable 被加入 renderer root |
| native scene 与布局 | renderer 创建的 native scene、Yoga node 与布局流程 | layout/paint 所需的 native scene 路径已参与渲染 |
| cell frame | `renderOnce()` 后的 `captureCharFrame()` | 提交帧的字符内容可被读取并断言 |
| 输出交付 | test renderer 默认的内存 sink | 本例不覆盖真实终端 transport，也不证明终端设备最终显示 |

`packages/native/src/scene.zig` 可用于继续追踪 scene 与 Yoga child 的关联；官方 Native Frames 文档则把 layout、paint、frame encoding 与 output delivery 分开说明。两类资料都不意味着应用应直接调用一个未公开的 Zig rendering API。本例只调用公开的 TypeScript testing API。

## 适用边界

- 适合检查 Core 节点变更是否产生预期字符帧。
- 不适合单独验证真实 stdout 写入、终端能力协商或最终显示效果。
- 若目标是自定义 stream 或真实 transport，应使用官方 testing 文档明确描述的配置路径，并为相应 I/O 边界增加独立验证。

## 相关概念

- [Layout、native scene 与终端帧渲染](/concepts/03-layout-and-native-rendering.md)
- [Test renderer 与交互测试](/concepts/08-testing.md)
- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
