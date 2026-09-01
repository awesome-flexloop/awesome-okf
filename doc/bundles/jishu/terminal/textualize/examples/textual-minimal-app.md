---
type: Example
title: "最小 Textual 应用：App 子类 + compose + @on 事件处理"
description: 用最小可运行代码演示 Textual TUI 的三块基石：继承 App 并运行、compose() 用 yield 产出组件、@on 装饰器处理按钮点击事件并更新界面。零依赖凭据，可直接运行。
tags: [textualize, textual, tui, example]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# 最小 Textual 应用：App 子类 + compose + @on 事件处理

## 概述

Textual 里任何 TUI 应用都从继承 `App` 开始（F-T-060，`app.py:296`），在 `compose()` 中用 `yield` 逐个产出组件（F-T-050，`widget.py:1679`），再用 `@on` 装饰器或 `on_<handler>` 命名约定（F-T-003、F-T-012）处理组件发来的消息。本例用一个"点击按钮后更新文本"的最小场景串起这三个环节，可作为从零起步的模板。

```python
from textual.app import App, ComposeResult
from textual import on
from textual.widgets import Button, Static


class MinimalApp(App):
    """最小 Textual 应用：compose 声明组件，@on 处理事件。"""

    TITLE = "最小 Textual 应用"          # F-T-060：TITLE 类变量（app.py:413）

    def compose(self) -> ComposeResult:
        # F-T-050：compose() 用 yield 一次产出一个组件，构成界面 DOM
        yield Static("点下面的按钮试试", id="message")
        yield Button("点击我", id="greet")

    @on(Button.Pressed, "#greet")        # F-T-110：按组件 id 的 CSS 选择器匹配消息
    def greet(self, event: Button.Pressed) -> None:
        # F-T-089：Button.press() 会 post Button.Pressed 消息，event.button 即被点按钮
        self.query_one("#message", Static).update("你好，Textual！")


if __name__ == "__main__":
    MinimalApp().run()                    # F-T-063：run() 进入事件循环并驱动整棵 DOM
```

## 运行

```bash
python textual-minimal-app.md  # 实际使用时把示例代码另存为 .py 文件执行
```

启动后可见一行 `点下面的按钮试试` 和一个 `点击我` 按钮；用鼠标点按按钮后，第一行文本变成 `你好，Textual！`。按 `Ctrl+Q` 退出（F-T-061：App 默认 `ctrl+q → quit`）。

## 讲解

### 1. App 子类即应用入口（F-T-060 / F-T-063）

`MinimalApp(App)` 继承自泛型 `App(Generic[ReturnType], DOMNode)`（`app.py:296`）。`run(*, headless=False, inline=False, ...)` 是同步入口（`app.py:2308`），其异步对应是 `run_async()`；调用后框架创建默认 `Screen`、装配 `compose()` 产出的 DOM、进入消息循环。`TITLE = "..."` 走的是类变量（`app.py:413`），会被渲染到屏幕顶栏。

### 2. compose() 用 yield 产出组件（F-T-050）

`compose() -> ComposeResult` 是**生成器**：方法体的每个 `yield` 产出一个待挂载组件。Textual 自行收集并挂载它们到当前 `Screen`，建立组件树。组件顺序即默认布局的先后顺序——本例 `Static` 在上、`Button` 在下。组件通常用关键字 `id`/`name`/`classes` 命名，便于之后用 CSS 选择器精准定位。

### 3. @on 处理消息（F-T-110）

`@on(message_type, selector)` 装饰器（`_on.py:24`）把被装饰方法注册为消息处理器，第二个参数 `"#greet"` 是 CSS 选择器——它限定只在**发送者的 `control`/sender** 匹配该选择器时才派发该处理器。本例选择器命中 `id="greet"` 的按钮，于是只有点这个按钮才触发 `greet`。

处理器里 `self.query_one("#message", Static).update("...")`（F-T-038 查询 API）找到 `Static` 组件并调用其 `update()` 更新文本——一套完整的"事件 → 查找组件 → 改状态 → 重绘"交互闭环。

> **命名约定的备选写法**：不使用 `@on` 时，基于 `Message` 类名自动生成的 `handler_name`（F-T-003，`Button.Pressed` → `on_button_pressed`）也会被 `_get_dispatch_methods` 按 `on_<handler_name>` 查找并派发（F-T-012）。也就是把方法名写成 `on_button_pressed` 同样有效；`@on` 的优势是能自由命名方法并加上选择器过滤。

## 相关概念

- [13-textual-app-entry.md](/concepts/13-textual-app-entry.md) — App 入口、run/run_async 与生命周期
- [16-textual-dom-widget-builtin.md](/concepts/16-textual-dom-widget-builtin.md) — Widget 基类、compose 与内置组件（Button/Static）