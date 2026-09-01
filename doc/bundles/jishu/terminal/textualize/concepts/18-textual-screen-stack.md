---
type: Concept
title: Screen 栈：模式、焦点管理与屏幕切换
description: Textual 的屏幕（Screen）体系：Screen 类、push/pop/switch 屏幕栈管理、模态屏幕、焦点管理与应用模式（Mode），含 dismiss 返回值传递。
tags: [textualize, textual, tui]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# Screen 栈：模式、焦点管理与屏幕切换

## 概述

在 Textual 中，`Screen` 是承载界面内容的顶层 Widget，一个应用同一时刻可挂载多个屏幕并按「屏幕栈」压入/弹出地切换；栈顶屏幕决定当前可见内容与活动焦点。本概念覆盖 `Screen` 类定义、`push_screen`/`pop_screen`/`switch_screen` 三种切换方式、模态屏幕（modal）、焦点管理，以及应用模式（Mode）这一屏幕级别的多态切换机制。它们共同构成 Textual 多界面（多屏）导航的核心骨架。

## Screen 类

`Screen` 定义于 `src/textual/screen.py:148`，签名 `Screen(Generic[ScreenResultType], Widget)`——它本身就是一个泛型 `Widget`，泛型参数 `ScreenResultType` 表示该屏幕 dismiss 时的返回结果类型。

- 类变量：`AUTO_FOCUS: ClassVar[str | None] = None`（激活屏幕时自动聚焦的选择器，`None` 继承应用设置，`""` 禁用）、`CSS: ClassVar[str] = ""`（内联 CSS，优先级高于 `CSS_PATH`）、`CSS_PATH: ClassVar[CSSPathType | None] = None`（从文件加载 CSS 的路径）、组件类 `COMPONENT_CLASSES = {"screen--selection"}`。
- 默认按键绑定 `Screen.BINDINGS`（`screen.py:269-273`）：`tab → app.focus_next`、`shift+tab → app.focus_previous`、`ctrl+c,super+c → screen.copy_text`，均 `show=False`（不显示在帮助栏），焦点导航由此在屏幕层接管。
- 响应式属性（reactive）：`focused: Reactive[Widget | None] = Reactive(None)`（当前聚焦 Widget）、`stack_updates: Reactive[int] = Reactive(0, repaint=False)`、`maximized: Reactive[Widget | None] = Reactive(None, layout=True)`、`selections: var[dict[Widget, Selection]] = var(dict)`。
- 构造 `__init__(name=None, id=None, classes=None)`：置 `_modal = False`，创建 `Compositor()`、`_dirty_widgets` 集合、回调列表 `_callbacks` 与 `_result_callbacks: list[ResultCallback]`、tooltip 相关属性，并将 `CSS_PATH` 解析为相对路径列表。

## 屏幕栈：push / pop / switch

应用通过三个方法操作屏幕栈（均定义于 `src/textual/app.py`）：

- `App.push_screen(screen, callback=None, wait_for_dismiss=False, *, mode=None) -> AwaitMount | asyncio.Future`（`:2895`）：把 `screen` 压入栈顶。切换过程中向原活动屏幕派发 `events.ScreenSuspend()`、向新屏幕派发 `events.ScreenResume()`；`mode` 未知时抛 `UnknownModeError`；`wait_for_dismiss=True` 且不在 worker 中时抛 `NoActiveWorker`；最后发布 `screen_change_signal.publish(next_screen)`。
- `App.pop_screen() -> AwaitComplete`（`:3096`）：弹出栈顶屏幕。
- `App.switch_screen(screen) -> AwaitComplete`（`:3001`）：原地切换当前屏幕（不改变栈深度）。

配套方法：`App.install_screen(screen, name) -> None`（`:3036`）把屏幕实例注册到命名表；`App.get_default_screen() -> Screen`（`:1380`）；`App.compose() -> ComposeResult`（`:1393`）定义应用初始屏幕。

使用 `push_screen` 时，`callback` 会在被压入的屏幕 `dismiss` 时收到其返回值，从而把结果传回上一屏。

## 模态屏幕

`Screen.__init__` 中 `_modal = False` 声明屏幕默认非模态。模态屏幕（modal）用于强制用户交互——它在栈上时禁止访问背后的屏幕。

屏幕通过 `Screen.dismiss(result=None) -> AwaitComplete`（`screen.py:2048`）结束自身并返回结果：先调用 `_result_callbacks[-1]`（即 push 时的回调），再执行 `self.app.pop_screen()`；若在屏幕自身消息处理器中 `await` dismiss，则抛 `ScreenError`，提示不要在处理器内部直接等待。

## 焦点管理

屏幕承载并协调整个界面焦点：

- 导航：`Screen.focus_next(selector="*") -> Widget | None`（`:897`）、`Screen.focus_previous(selector="*") -> Widget | None`（`:914`）按选择器在可聚焦 Widget 间移动焦点，由 `tab`/`shift+tab` 绑定触发。
- 命中测试：`Screen.get_widget_at(x, y) -> tuple[Widget, Region]`（`:633`）返回坐标处 Widget 与所在区域。
- 动作（action）：`action_copy_text`（`:985`）、`action_maximize`（`:993`）、`action_minimize`（`:998`）、`action_blur`（`:1002`）。
- 应用级焦点：`App.focused` 属性返回 `self.screen.focused`（`app.py:1290-1299`），应用始终读取活动屏幕的焦点 Widget。App 相关 reactive 属性（`app.py:548-553`）：`title: Reactive[str] = Reactive("", compute=False)`、`sub_title` 同构、`app_focus = Reactive(True, compute=False)`。

## 应用模式（Mode）

Mode 允许在应用层同时声明多个命名屏幕并按名快速互相切换。App 类变量 `MODES: ClassVar[dict[str, str | Callable[[], Screen]]] = {}`、`DEFAULT_MODE: ClassVar[str] = "_default"`、`SCREENS: ClassVar[dict[str, Callable[[], Screen[Any]]]] = {}` 提供屏幕注册表（参见 `/concepts/13-textual-app-entry.md`）。

切换与移除：

- `App.switch_mode(mode) -> AwaitMount`（`app.py:2630`）：切换到已声明模式，未知 mode 抛 `UnknownModeError`。
- `App.remove_mode(mode) -> AwaitComplete`（`:2699`）：移除某模式，移除当前活动模式抛 `ActiveModeError`。

## 相关概念

- [/concepts/16-textual-dom-widget-builtin.md](/concepts/16-textual-dom-widget-builtin.md) — `Screen` 继承自 `Widget`（`Widget` ← `DOMNode` ← `MessagePump`），其 DOM 与组件方法与内置 Widget 一致
- [/concepts/17-textual-events-bindings.md](/concepts/17-textual-events-bindings.md) — `ScreenSuspend`/`ScreenResume`/`Focus`/`Blur` 等事件与 `Screen.BINDINGS` 按键绑定体系