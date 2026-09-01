---
type: Concept
title: 事件体系、按键绑定与 @on 装饰器
description: 剖析 Textual 事件与绑定机制：Event 事件类体系、生命周期事件与鼠标/焦点事件的 bubble 声明、定时器即消息 Timer、BINDINGS 声明、@on 装饰器与按键 Key，含约定与陷阱小节。
tags: [textualize, textual, tui]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---
# 事件体系、按键绑定与 @on 装饰器

## 概述

Textual 的交互完全由「事件 + 消息派发 + 绑定」驱动。事件本体是 `Event(Message)` 及其庞大子类族（键盘 `Key`、鼠标 `MouseEvent`、生命周期事件、焦点事件、定时器 `Timer`）；按键绑定由冻结 dataclass `Binding` 与 `BindingsMap` 声明；处理器既可命名约定 `on_<handler_name>`，也可用 `@on` 装饰器显式注册并携带 CSS 选择器。本文串起这三套机制，并归拢约定与陷阱。

开头延伸阅读：[/concepts/14-textual-message-system.md](/concepts/14-textual-message-system.md)（派发与 `__init_subclass__` 生成 handler_name）、[/concepts/16-textual-dom-widget-builtin.md](/concepts/16-textual-dom-widget-builtin.md)（内置组件如何声明 BINDINGS）。

## 事件类体系

`Event(Message)` 是所有事件的基类（`src/textual/events.py:39`），`InputEvent(Event)` 是输入事件基类（:256）（F-T-029）。这类事件本质仍是 `Message`，因此继承 `Message.__init_subclass__` 自动生成的 `handler_name`（`on_<name>`）与 `MessagePump._get_dispatch_methods` 的 `on_` 命名约定派发逻辑（F-T-113）。

`bubble` 是事件传播的关键开关：为真时事件沿 DOM 向上冒泡，可在祖先节点统一处理；为假则只发给目标。

```python
from textual import events

class MyWidget(Widget):
    def on_mount(self, event: events.Mount):
        pass  # 命名约定处理器
```

## 生命周期事件（均 bubble=False）

生命周期事件全部以 `bubble=False` 声明，只送达目标节点自身（`src/textual/events.py:66-206`）（F-T-030）：

- `Load`（:66）、`Resize`（:100）
- `Compose`（:156，`verbose=True`）
- `Mount`（:167）、`Unmount`（:175）
- `Show`（:183）、`Hide`（:191）、`Ready`（:206）
- `Idle`（:78）

常用挂载链为 `Compose`（构建子组件）→ `Mount`（挂载完成）→ 生命周期推进；`Idle` 是文本刷新的调度时点（`Widget.refresh` 置脏后实质在下一 idle 执行，F-T-114）。

## 鼠标/焦点事件的 bubble 声明

输入类事件多数声明 `bubble=True`，可向上冒泡便于祖先统一响应（F-T-032~F-T-034）：

- `MouseEvent(InputEvent, bubble=True)`：构造携带 `widget, x, y, delta_x, delta_y, button, shift, meta, ctrl, screen_x=None, screen_y=None, style=None`，`screen_x/screen_y` 缺省时取 `x/y`（F-T-032）。
- 鼠标子类均 `bubble=True`：`MouseMove`、`MouseDown`、`MouseUp`、`MouseScrollDown/Up/Left/Right`、`Click`（F-T-033）。
- 焦点事件分两组：`Focus`/`Blur`（`bubble=False`）、`AppFocus`/`AppBlur`（`bubble=False`）；而 `DescendantFocus`/`DescendantBlur`（`bubble=True, verbose=True`）（F-T-034）用于感知后代焦点变化。

其他事件（F-T-035）：`Enter`/`Leave`（`bubble=True`）、`Paste`（`bubble=True`）、`TextSelected`（`bubble=True`）；`ScreenResume`/`ScreenSuspend`/`Print`/`DeliveryComplete`/`DeliveryFailed` 与 `MouseCapture`/`MouseRelease` 均 `bubble=False`；`Timer`/`Callback` 为 `Event, bubble=False, verbose=True`。

## 定时器即消息：Timer(Event)

定时器走的是消息而非回调线程。`Timer(Event, bubble=False, verbose=True)`（`src/textual/events.py:723`）由消息泵的 `set_timer(delay, callback=None, *, name=None, pause=False) -> Timer`（message_pump.py:378）与 `set_interval(interval, callback=None, *, name=None, repeat=0, pause=False) -> Timer`（message_pump.py:418）创建（F-T-009、F-T-035）。定时器到期会作为一条 `Timer` 事件投递到队列入 `on_timer` 派发，因此可用 `self.set_timer(2, self.say_hello)` 延迟执行，也可在 `on_timer` 中收到携带的定时器对象。

```python
def on_mount(self):
    self.set_interval(5, self.tick)

def tick(self) -> None:
    self.log("滴答")
```

## BINDINGS：按键绑定声明

`Binding` 是冻结 dataclass（`src/textual/binding.py:55-98`），字段：`key`、`action`、`description=""`、`show=True`、`key_display`、`priority=False`、`tooltip`、`id`、`system=False`、`group`（嵌套冻结 dataclass `Binding.Group` 含 `description`/`compact`）（F-T-024）。`parse_key()` 以 `"+"` 分割返回 `(修饰键列表, 键)`（F-T-025）；`make_bindings(bindings)` 把 2/3 元组转 `Binding`，逗号分隔键（如 `"j,down"`）展开为多个，空键抛 `InvalidBinding`（F-T-026）。`BindingsMap`（:185）提供 `bind`、`get_bindings_for_key(key) -> list[Binding]`、`merge`、`shown_keys`、`from_keys` 等（F-T-027、F-T-028）。

组件在类级声明 `BINDINGS` 并在 `DOMNode.__init_subclass__` 里合并进 `_merged_bindings`：

```python
class MyWidget(Widget):
    BINDINGS = [
        ("ctrl+d", "exit_app", "退出"),
        ("j,down", "cursor_down", "下移"),
        Binding("ctrl+s", "save", "保存", priority=True),
    ]

    def action_exit_app(self) -> None:
        self.app.exit()
```

动态动作/绑定可通过钩子 `DOMNode.check_action(action, parameters) -> bool | None`（`src/textual/dom.py:1909`）做前置判定（F-T-044，详见约定与陷阱）。

## @on 装饰器：声明式处理器

`on(message_type: type[Message], selector: str | None = None, **kwargs: str)` 装饰器（`src/textual/_on.py:24`，异常 `OnDecoratorError`）声明消息处理器，并可选对消息的 `control` 属性暴露的 widget 做 CSS 选择器匹配（F-T-110）。`@on` 注册到对象的 `_decorated_handlers`，在 `MessagePump._get_dispatch_methods` 中优先于命名约定的 `on_<handler_name>` 被执行（F-T-113）。

```python
class MyApp(App):
    def compose(self):
        yield Button("点我", id="btn")

    @on(Button.Pressed, "#btn")
    def btn_pressed(self, event: Button.Pressed):
        self.notify(f"按钮: {event.button.label}")
```

`**kwargs` 允许以键值形式附加选择器匹配，例如 `@on(Input.Changed, value="*")` 这类按属性值过滤的写法。

## 约定与陷阱

- **`bubble` 决定可达性**：生命周期事件（`Mount`/`Unmount`/`Idle`/`Load`）`bubble=False`，在祖先节点收不到；若需统一处理子树挂载，应监听 `DescendantMount` 类冒泡事件而非 `Mount`。
- **`@on` 比命名约定更早**：同一消息两者并存时，`@on` 注册处理器（`_decorated_handlers`）优先于 `on_<handler_name>` 命名约定（F-T-012/F-T-113），避免用命名方法时因选择器冲突产生意外。
- **`priority=True` 的绑定优先**：App 默认绑定 `ctrl+q → quit`（priority=True）、`ctrl+c → help_quit`（system=True）（F-T-061）；子组件可用 `priority=True` 抢占按键，否则按键会冒泡到上层处理。
- **`schedule_idle` 语义**：`refresh()` 只在 idle 时点真正刷新（F-T-114），连续修改 reactive 不会每步重绘。
- **`check_action` 是只读钩子**：它返回判定结果（是否允许动作），不触发动作本身；返回值的空/假值会拦截 `action_*` 执行，可用于运行时禁用单个绑定。
- **绑定键去重**：`get_bindings_for_key` 可能返回多个匹配绑定，处理顺序与 `priority` 及声明先后相关，注释/实验以源码 `binding.py` 为准。

## 相关概念

- [/concepts/14-textual-message-system.md](/concepts/14-textual-message-system.md)：`Message`/`MessagePump` 与 `on_<handler_name>` 派发链
- [/concepts/16-textual-dom-widget-builtin.md](/concepts/16-textual-dom-widget-builtin.md)：内置组件（Button/Input/DataTable/TextArea）各自的 BINDINGS 与消息
- /references/textual.md —— Textual 仓库信源登记