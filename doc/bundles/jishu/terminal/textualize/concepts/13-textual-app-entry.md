---
type: Concept
title: App 入口：类变量契约、run 循环与 notify
description: 解析 Textual TUI 应用入口 App 类：类变量构成的配置契约（CSS/BINDINGS/MODES 等）、run() 运行循环的封装与退出，以及 notify/toast 应用级通知机制。
tags: [textualize, textual, tui]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources:
  - id: "textual"
    resource: /references/textual.md
    title: Textual 仓库信源登记
---
# App 入口：类变量契约、run 循环与 notify

## 概述

Textual 应用的**入口**是 `App` 类，定义于 `src/textual/app.py:296`，继承链为 `MessagePump` ← `DOMNode` ← `App`（F-T-112）。`App`（F-T-060）承担框架中两条最核心的职责：以**类变量**声明应用级配置契约（CSS 样式、按键绑定 `BINDINGS`、屏幕模式 `MODES`、标题等），并以 `run()` 封装完整的事件循环，用 `notify()` 向用户抛送应用级 toast 通知。作为 TUI 框架，`textual` 建立在生态基座 `rich` 之上（见 /concepts/00-ecosystem-overview.md 的三层依赖），`App` 是每个 Textual 应用的零依赖组装起点——只被子类继承配置，运行期由框架驱动。

本文以 F-T-060..063、F-T-066、F-T-067、F-T-071 为依据，聚焦 `App` 的类变量契约、`run()` 循环、退出与 `notify()` 通知三条主线。

## 类变量契约（应用级配置）

`App` 继承链使其天然具备 DOM 节点的类级元编程：`DOMNode.__init_subclass__` 沿 MRO 收集响应式属性与合并绑定（F-T-037）。在 `App` 层，类变量构成面向子类开放的应用配置契约（F-T-060），子类通过覆盖这些类变量"声明式"地装配应用：

| 类变量 | 默认值 | 含义 |
|---|---|---|
| `CSS` | `""` | 内嵌 CSS，加载于 `CSS_PATH` 之后（`app.py:300`） |
| `CSS_PATH` | `None` | 外部 CSS 文件路径（`app.py:410`） |
| `MODES` | `{}` | 屏幕模式名 → Screen 工厂的映射 |
| `DEFAULT_MODE` | `"_default"` | 默认启动模式 |
| `SCREENS` | `{}` | 命名屏幕注册表 |
| `AUTO_FOCUS` | `"*"` | 挂载后自动聚焦的 widget 选择器 |
| `ALLOW_SELECT` | `True` | 是否允许文本选择 |
| `TITLE` / `SUB_TITLE` | `None` | 应用标题与副标题 |
| `ENABLE_COMMAND_PALETTE` | `True` | 是否启用命令面板 |
| `NOTIFICATION_TIMEOUT` | `5` | 通知默认超时（秒） |
| `COMMAND_PALETTE_BINDING` | `"ctrl+p"` | 命令面板触发键 |
| `CLICK_CHAIN_TIME_THRESHOLD` | `0.5` | 连击判定阈值 |
| `CLOSE_TIMEOUT` | `5.0` | 关闭挂起 widget 的超时 |
| `TOOLTIP_DELAY` | `0.5` | 提示气泡显示延迟（秒） |

`App` 默认的键盘绑定 `BINDINGS`（F-T-061，`app.py:454-464`）仅两条系统级快捷键，均 `show=False`：

```python
BINDINGS: ClassVar[list[BindingType]] = [
    Binding("ctrl+q", "quit", "Quit", show=False, priority=True),
    Binding("ctrl+c", "help_quit", show=False, system=True),
]
```

子类若要增补按键，通常再声明自己的 `BINDINGS`，框架在 `DOMNode.__init_subclass__` 阶段沿 MRO 合并（F-T-037）。构造器 `App.__init__`（F-T-062，`app.py:572-578`）接收 `driver_class / css_path / watch_css / ansi_color`，其中 `css_path` 缺省回退到 `CSS_PATH` 类变量（`app.py:731`），`features` 由环境变量 `TEXTUAL` 经 `parse_features` 解析。构造时 `super().__init__(classes=self.DEFAULT_CLASSES)` 把自身作为根 DOM 节点初始化。

## run() 运行循环

`App.run()`（F-T-063，`app.py:2308`）是应用的实际启动入口，签名只收关键字参数：

```python
def run(
    self, *,
    headless: bool = False,
    inline: bool = False,
    inline_no_clear: bool = False,
    mouse: bool = True,
    size: tuple[int, int] | None = None,
    auto_pilot: AutopilotCallbackType | None = None,
    loop: AbstractEventLoop | None = None,
) -> ReturnType | None: ...
```

`run()` 内部定义一个 `run_app()` 协程并委托给 `run_async(...)`（F-T-063，`app.py:2220`）。`run_async` 参数与 `run()` 基本相同（无 `loop`）；它调用 `app._process_messages(...)` 驱动消息泵，结束时 `await asyncio.shield(app._shutdown())` 完成关闭，并返回保存在 `app.return_value` 上的值。`headless=True` 时配合 `HeadlessDriver`（F-T-108，`is_headless` 返回 True）可无终端输出运行，常用于测试；`auto_pilot` 非空时 `run_async` 会创建 `Pilot(app)` 并在任务中执行回调（F-T-111），用于自动化测试脚本。

退出与结果通过 `App.exit()`（F-T-066，`app.py:1270`）主动触发：

```python
def exit(result=None, return_code=0, message=None) -> None: ...
```

`exit()` 将实例标记 `_exit=True`、暂存 `_return_value`/`_return_code`，然后 `post_message(messages.ExitApp())`，由消息泵在循环中唤醒并完成 `_shutdown` 流程；`run()` 最终把 `result` 作为返回值交还给调用方。运行期的焦点等状态由属性透传，例如 `App.focused`（F-T-071，`app.py:1290-1299`）直接返回 `self.screen.focused`。

## notify() 与 toast 通知

`App.notify()`（F-T-067，`app.py:4621`）提供应用级一次性通知，呈现在屏幕右下角的 `Toast` 中：

```python
def notify(
    self,
    message: str, *,
    title: str = "",
    severity: SeverityLevel = "information",
    timeout: float | None = None,
    markup: bool = True,
) -> None: ...
```

`severity` 取 `information`/`warning`/`error` 三档（默认 `information`），`timeout` 缺省回退到类变量 `NOTIFICATION_TIMEOUT`，`markup=True` 表示消息按 Content Markup 渲染。该方法 **线程安全**（docstring 明示），可在后台线程直接调用。实现上通过屏幕的 `ToastRack`（`textual.widgets._toast`，`app.py:4606` 按其类型取子组件）承载通知；`timeout=None` 时按 `NOTIFICATION_TIMEOUT` 决定显示时长。

## 与 rich 的关系

`App` 是 Textualize 依赖分层中框架层的顶点：Textualize 生态呈 `rich`（渲染基座）→ `textual`（TUI 框架）→ 卫星应用三层依赖 DAG（见 /concepts/00-ecosystem-overview.md），`textual` 的 `pyproject.toml` 声明依赖 `rich`。因此 `App` 的样式渲染、`notify()` 的消息富文本化（Content Markup）最终都由 `rich` 的渲染协议兜底——写 `App` 代码时传入的字符串、标题、`markup=True` 的文案底层都经 rich 的 Console/渲染管线输出到终端。

## 相关概念

- /concepts/00-ecosystem-overview.md —— Textualize 生态三层依赖，`rich`→`textual` 渲染基座关系
- /concepts/14-textual-message-system.md —— `App` 继承的消息泵 `MessagePump` 与消息分发
- /concepts/15-textual-reactive.md —— `App` 经 `DOMNode.__init_subclass__` 装配的响应式属性体系
- /references/textual.md —— Textual 仓库信源登记（commit `06dbeef`）