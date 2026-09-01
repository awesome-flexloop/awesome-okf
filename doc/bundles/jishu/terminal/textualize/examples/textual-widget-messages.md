---
type: Example
title: textual 示例：Button.Pressed 与 Input.Submitted 消息流
description: 用 Button 与 Input 拼装一个 Textual 小应用，演示按钮点击触发 Pressed 消息冒泡、输入框回车触发 Submitted 消息，以及用 Message.stop / prevent_default 控制冒泡与默认动作。
tags: [textualize, textual, message, bubble, event, tui-widget]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# textual 示例：Button.Pressed 与 Input.Submitted 消息流

## 概述

Textual 的消息系统是「消息泵 + 冒泡」驱动：消息沿 widget 父链向上传递（默认 `bubble=True`），命名约定处理器 `on_<handler_name>` 逐层截获。本示例用内置 `Button` 与 `Input` 拼装一个小表单，演示两条典型消息流：

- **`Button.Pressed`**：点击 `Button` 时由 `Button.press()` 投递（F-T-089），携带 `button`/`control` 属性，默认向祖先 widget 冒泡。
- **`Input.Submitted`**：输入框按回车时投递（F-T-093），携带 `value`/`control` 属性。

并展示 `Message.stop()`（阻止继续冒泡，F-T-005 设置 `_stop_propagation`）与 `Message.prevent_default()`（抑制默认动作，F-T-005 设置 `_no_default_action`）两条控制途径。

## 可运行示例

```python
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Input, Label


class StopGuard(Vertical):
    """一个空的容器 widget，仅作为「冒泡截断层」示范。

    它的 on_button_pressed 处理器会调用 event.stop()，
    从而阻止 Pressed 消息继续上浮到外层 App（F-T-005）。
    """

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()  # _stop_propagation = True，消息在此停止冒泡


class MessageFlowDemo(App):
    """Button.Pressed 与 Input.Submitted 消息流示例。"""

    CSS = """
    StopGuard {
        height: auto;
        padding: 1;
        border: round $primary;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("输入文字后按回车，或点击按钮：")
        yield Input(placeholder="Input.Submitted 演示", id="name")
        yield Button("普通按钮（Pressed 冒泡到 App）", id="plain")
        yield StopGuard(
            Button("守卫按钮（Pressed 被 StopGuard 截断）", id="guarded")
        )
        yield Label("", id="status")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # F-T-093: Submitted 携带 value 与 control
        text = f"Input.Submitted: value={event.value!r} control={event.control.id}"
        self._set_status(text)
        # event.prevent_default()  # F-T-005: 如需抑制默认动作可启用

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Pressed 默认 bubble=True：能从按钮冒泡到 App。
        # 被 StopGuard.stop() 截断的 guarded 按钮不会到达这里。
        self._set_status(
            f"Button.Pressed 已冒泡到 App：button={event.button.id!r} "
            f"control={event.control.id!r}"
        )

    def _set_status(self, text: str) -> None:
        self.query_one("#status", Label).update(text)


if __name__ == "__main__":
    MessageFlowDemo().run()
```

保存为 `messages_demo.py`，并在终端运行 `python messages_demo.py` 即可交互体验消息流。

## 讲解

### 1. 消息从哪来

- `Button.press()`（F-T-089）：当按钮未被禁用且可见时，若未配置 `action`，调用 `post_message(Button.Pressed(self))` 投递 `Button.Pressed`；若配置了 `action` 则改走 `run_action`。点击动作的 `_on_click` 会先 `event.stop()`。
- `Input.Submitted` 由输入框回车触发（F-T-091..093），`Input.Changed/Submitted/Blurred` 均为 `@dataclass` 的 `Message`，且都带 `control` 属性。

### 2. 消息怎么冒泡

`Message` 默认 `bubble=True`（F-T-002），`MessagePump._process_messages_loop` 派发后沿父链逐层调用 `on_<handler_name>`（F-T-012、F-T-113）。因此：

- 普通按钮的 `Pressed` 会一路冒泡到 `App.on_button_pressed`；
- 守卫按钮的 `Pressed` 先被所在 `StopGuard.on_button_pressed` 截获并 `event.stop()`，此后 App 层不再收到。

### 3. stop 与 prevent_default

二者都由 `Message` 提供（F-T-005）：

```python
event.stop()            # 置 _stop_propagation，阻止继续冒泡
event.prevent_default() # 置 _no_default_action，抑制该消息的"默认动作"
```

`prevent_default` 常用于「消息已被高层处理、不希望底层再执行默认行为」的场景；`stop` 则用于将消息终止在当前 widget，避免上层 UI 组件（如外层卡片、Tab 容器）也做出响应。

## 相关概念

- [16 · Textual DOM 与内置 Widget](/concepts/16-textual-dom-widget-builtin.md)
- [17 · Textual 事件与按键绑定](/concepts/17-textual-events-bindings.md)
- [14 · Textual 消息系统](/concepts/14-textual-message-system.md)