---
type: Concept
title: 消息系统：Message / MessagePump 与派发约定
description: 拆解 Textual 消息驱动的核心骨架：Message 基类与 handler_name 生成、MessagePump 派发队列、post_message 投递、can_replace 合并、on_event/_on_message 分流与 @on 装饰器优先级。
tags: [textualize, textual, tui]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# 消息系统：Message / MessagePump 与派发约定

## 概述

Textual 是**消息驱动（message-driven）**的 TUI 框架：几乎一切运行时行为——按键、鼠标、生命周期、组件内部状态——都以 `Message` 对象的形式在节点间流转，并由每个节点的 `MessagePump` 异步消费。本文是 textual 概念文档中**最核心的一篇**，覆盖内置组件消息（如 `Button.Pressed`、`Input.Changed`）与派发机制的完整链路：`Message`/`MessagePump` 的构造与类变量（F-T-001..F-T-016）、`post_message` 的投递语义、`can_replace` 的队列合并、`on_event`/`_on_message` 的双路分流、`handler_name` 与 `camel_to_snake` 的命名约定、`@on` 装饰器的优先级与选择器匹配（F-T-113），以及 `Message → Event`、`MessagePump → DOMNode → Widget → Screen` 的继承骨架（F-T-112）。代码位于 `src/textual/message.py`、`src/textual/message_pump.py`、`src/textual/_on.py`。

## 继承骨架：消息与消息泵

两条主线构成了 Textual 的动态部分：

- **消息链**：`Message` ← `Event` ← 各具体事件（F-T-029，`Event` 定义于 `events.py:39`）。
- **泵链**：`MessagePump` ← `DOMNode` ← `Widget` ← `Screen`；`MessagePump` ← `DOMNode` ← `App`（F-T-112）。

`DOMNode` 从 `MessagePump` 继承，意味着**每个 DOM 节点（App/屏幕/Widget）自己就是一个消息泵**，拥有独立的 `_message_queue`、`_task` 与派发循环（F-T-016 列举的实例属性含 `_running`、`_closing`、`_closed`、`_disabled_messages`、`_pending_message`、`_task`、`_timers`、`_is_mounted`、`_next_callbacks`、`_thread_id`、`message_signal`）。

`MessagePump` 构造签名 `__init__(self, parent: MessagePump | None = None)`（F-T-008），模块级异常有 `CallbackError`（`message_pump.py:59`）与 `MessagePumpClosed`（:63）。

## Message 基类：bubble / no_dispatch / prevent / stop

`Message` 定义于 `src/textual/message.py:23`，`__slots__ = ["_sender", "time", "_forwarded", "_no_default_action", "_stop_propagation", "_prevent"]`（F-T-001），并声明一组类级标志（F-T-002）：

```python
# src/textual/message.py（节选）
ALLOW_SELECTOR_MATCH: ClassVar[set[str]] = set()
bubble: ClassVar[bool] = True        # 是否向父节点冒泡
no_dispatch: ClassVar[bool] = False  # 是否不派发
namespace: ClassVar[str] = ""
handler_name: ClassVar[str]          # 自动生成
```

- **`bubble: bool = True`**（类变量）：为 `True` 时消息会沿父链逐级冒泡；生命周期事件（`Mount`/`Unmount`/`Show`/`Hide`/`Load`/`Compose`/`Ready`/`Resize`/`Idle`，F-T-030）与焦点基础事件（`Focus`/`Blur`/`AppFocus`/`AppBlur`，F-T-034）均声明 `bubble=False`，只在自身派发、不向上冒泡。鼠标事件（`MouseMove`/`MouseDown`/`Click`/`MouseScroll*` 等，F-T-033）与 `Enter`/`Leave`/`Paste` 则 `bubble=True`。
- **`no_dispatch`**：`_dispatch_message` 首行即检查——`message.no_dispatch` 为真时直接返回、不派发（F-T-011）。
- **`Message.prevent_default(prevent=True) -> Message`** 置 `_no_default_action` 并返回 self（F-T-005）；`Message.stop(stop=True) -> Message` 置 `_stop_propagation` 并返回 self。
- **`Message.can_replace(message) -> bool`** 默认返回 `False`（F-T-006），子类覆盖以声明"新消息可替换待处理队列中的旧同款消息"。

实例初始化由 `__post_init__` 完成（F-T-004）：`_sender` 取 `active_message_pump.get(None)`，`time` 取 `_time.get_time()`，并复位 `_forwarded/_no_default_action/_stop_propagation/_prevent`。

## handler_name 与 camel_to_snake 命名约定

这是"命名即派发"的核心（F-T-003）：

```python
Message.__init_subclass__(cls, bubble=True, verbose=False,
                          no_dispatch=False, namespace=None)
```

`__init_subclass__` 自动生成 `cls.handler_name = f"on_{name}"`，其中 `name` 由类限定名经 `camel_to_snake` 拼接；**深层嵌套类只保留最后两段**（如 `A.B.C.D` → `C.D`）。于是 `Button.Pressed` 的 `handler_name` 即 `on_pressed`，配套处理器写作 `def on_button_pressed(...)`——命名约定把"消息类型"与"处理器方法"绑在一起（F-T-113）。

## post_message：投递语义

`post_message(message) -> bool` 是投递入口（F-T-010）：

- `_closing or _closed` 时返回 `False`（泵已关闭，不投递）。
- `check_message_enabled(message)` 失败时返回 `False`（消息被 `disable_messages` 禁用）。
- 调用线程与 `self._thread_id` 不同时，经 `loop.call_soon_threadsafe(self._message_queue.put_nowait, message)` 投递，保证线程安全（F-T-010、源码 `message_pump.py:885`）。
- 缺少 `_prevent` 属性时抛 `RuntimeError`，提示**忘记调用 `super().__init__()`**——这是自定义 Widget 最常见的坑之一。

单发调度工具（F-T-009、F-T-014）：`set_timer`（:378）、`set_interval`（:418，可 `repeat`）、`call_later`（:490）、`call_next`（:507）、`call_after_refresh`（:451）、`wait_for_refresh`（:469）、`check_idle`（:841）。

## 派发：on_event / _on_message / @on 优先级

`_dispatch_message(message)`（F-T-011、`message_pump.py:707-741`）在派发中心 `self.prevent(*message._prevent)` 的上下文中执行：

```python
# 源码节选语义
if message.no_dispatch:
    return
if isinstance(message, Event):
    await self.on_event(message)      # 事件走 on_event
else:
    await self._on_message(message)   # 普通消息走 _on_message
```

`on_event`（:802）本质是 `await self._on_message(event)` 的再包装，即**事件与普通消息最终统一走 `_on_message`**；区别只在于入口分流。

真正的方法解析在 `_get_dispatch_methods(method_name, message)`（F-T-012、:743-800）：沿 `self.__class__.__mro__`，**先派发 `_decorated_handlers`（`@on` 装饰器注册的处理器）**，再回退到 `on_<handler_name>` 命名约定方法；一旦 `message._no_default_action` 被置位，立即终止 MRO 遍历（防止下层默认处理）。

`@on(message_type, selector=None, **kwargs)`（F-T-110、`src/textual/_on.py:24`）声明消息处理器，可对消息 `control` 暴露的 widget 做 CSS 选择器匹配；非法用法抛 `OnDecoratorError`。

## 队列循环与 can_replace 合并

`_process_messages_loop` 从队列取消息的关键优化（F-T-015、`message_pump.py:634-694`）：取到消息后，用 `message.can_replace(pending)` 判断**新消息是否可替换待处理的旧消息**（`if pending is None or not message.can_replace(pending)`）——命中则合并、跳过重复派发。派发异常时调用 `self.app._handle_exception(error)` 并 break；每条消息派发后 `message_signal.publish(message)` 通知外部监听。这解释了为何高频事件（如滚动、`cursor_coordinate`，见 `/concepts/15-textual-reactive.md`）不会造成消息风暴。

## 约定与陷阱

- **命名即派发**：处理器方法名必须是 `on_<handler_name>`（如 `on_button_pressed`），`handler_name` 由 `camel_to_snake(类限定名两段)` 自动生成，别手写错格式。
- **`@on` 优先于命名约定**：装饰器注册的处理器沿 MRO 先派发（F-T-012/F-T-113），适合对 `control` 做选择器匹配的场景；命名约定是回退路径。
- **`prevent_default`/`stop` 返回 self**：可链式调用，且会终止 MRO 遍历/默认动作，底层处理者要预留检查。
- **忘记 `super().__init__()`**：`post_message` 会因缺 `_prevent` 抛 `RuntimeError`，这是自定义 Widget 头号诊断线索。
- **线程安全投递**：跨线程投递自动转 `call_soon_threadsafe`，但前提是消息泵在运行中（`_closed` 则拒投）。
- **`can_replace` 默认关闭**：只有子类显式覆盖才启用队列合并，默认每条消息都独立派发。
- **生命周期事件不冒泡**（`bubble=False`）：`Mount`/`Show`/`Hide` 等只在目标节点派发，需父级感知时用 `DescendantFocus` 这类显式 `bubble=True` 事件（F-T-034）。

## 相关概念

- [13-textual-app-entry.md](/concepts/13-textual-app-entry.md) — App 生命周期与应用层入口
- [15-textual-reactive.md](/concepts/15-textual-reactive.md) — 消息派发后驱动的响应式更新链路
- [17-textual-events-bindings.md](/concepts/17-textual-events-bindings.md) — 具体事件类型与按键绑定