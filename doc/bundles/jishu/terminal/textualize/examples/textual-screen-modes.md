---
type: Example
title: textual 示例：Screen 栈、MODES 多模式与 ModalScreen 对话框
description: 用 textual 演示 MODES 多模式切换、push_screen 压入含输入框的 ModalScreen，dismiss 经 callback 回传结果。
tags: [textualize, textual, tui, example, screen, modes, modal]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# textual 示例：Screen 栈、MODES 多模式与 ModalScreen 对话框

## 概述

Textual 的界面以 `Screen` 为全屏单位组织：一个 App 内部为每个**模式（mode）**维护一条独立的**屏幕栈**，`push_screen` / `pop_screen` 在当前模式的栈上压入、弹出屏幕；`MODES` 类变量把「模式名」映射到根屏幕类，`switch_mode` 在模式之间切换（F-T-064、F-T-069）。本示例演示三件事：

- **多模式**：`MODES = {"main": MainScreen, "settings": SettingsScreen}`，用按钮或按键经 `switch_mode` 在两个模式间切换；未知模式名抛 `UnknownModeError`。
- **屏幕栈 + 模态对话框**：主屏按钮 `push_screen(NameDialog())` 压入一个含 `Input` 输入框与两个 `Button` 的 `ModalScreen[str | None]`，它会压暗下层界面，且其按键绑定优先于 App 绑定。
- **结果回传**：对话框按钮（或输入框回车）调用 `self.dismiss(结果)`，`push_screen` 时传入的 `callback` 收到结果并写入 `Log`；取消/Esc 则回传 `None`。

## 可运行示例

```python
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Input, Label, Log


class NameDialog(ModalScreen[str | None]):
    """模态输入对话框：确定/回车以输入文本 dismiss，取消/Esc 以 None dismiss（F-T-058）。"""

    # ModalScreen 的绑定链优先于 App 绑定：Esc 由对话框自己接管。
    # action_dismiss 是 Screen 内置动作，内部调用 self.dismiss(result)。
    BINDINGS = [Binding("escape", "dismiss(None)", "取消对话框", show=False)]

    CSS = """
    NameDialog {
        align: center middle;
    }
    #dialog-box {
        width: 70;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #dialog-prompt {
        margin-bottom: 1;
        text-style: bold;
    }
    #dialog-buttons {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog-box"):
            yield Label("模态对话框（ModalScreen）：请输入你的名字", id="dialog-prompt")
            yield Input(placeholder="输入名字后回车，或点击按钮", id="name-input")
            with Horizontal(id="dialog-buttons"):
                yield Button("确定", variant="success", id="ok")
                yield Button("取消", variant="error", id="cancel")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # 输入框回车：直接以输入值关闭对话框（F-T-093：Submitted 携带 value）
        self.dismiss(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # 注意：在屏幕自身的消息处理器里不能 await self.dismiss()，
        # 否则会抛 ScreenError；直接调用即可（F-T-058）。
        if event.button.id == "ok":
            name = self.query_one("#name-input", Input).value
            self.dismiss(name)
        else:
            self.dismiss(None)


class MainScreen(Screen):
    """主屏幕：main 模式的根屏幕。"""

    BINDINGS = [Binding("s", "app.switch_mode('settings')", "切换到设置模式")]

    CSS = """
    #main-title {
        margin: 1 2;
        text-style: bold;
        color: $accent;
    }
    #main-buttons {
        height: auto;
        margin: 0 2 1 2;
    }
    #result-log {
        margin: 0 2;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("主屏幕（main 模式）：s 切换模式，按钮打开模态对话框", id="main-title")
        with Horizontal(id="main-buttons"):
            yield Button("打开模态对话框", variant="primary", id="open-dialog")
            yield Button("切换到设置模式", variant="warning", id="go-settings")
        yield Log(id="result-log")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open-dialog":
            # push_screen 把对话框压到当前模式的屏幕栈顶（F-T-064）；
            # 旧屏幕收 ScreenSuspend，对话框收 ScreenResume。
            # callback 在对话框 dismiss(result) 时被调用，参数即 dismiss 的结果。
            self.app.push_screen(NameDialog(), callback=self.on_name_entered)
        elif event.button.id == "go-settings":
            # 未知模式名会抛 UnknownModeError（app.py:2648）
            self.app.switch_mode("settings")

    def on_name_entered(self, result: str | None) -> None:
        """push_screen 的 callback：接收 ModalScreen dismiss 回来的结果。"""
        log = self.query_one("#result-log", Log)
        if result:
            log.write_line(f"对话框返回结果：你好，{result}！")
        else:
            log.write_line("对话框返回结果：None（点了取消或按了 Esc）")


class SettingsScreen(Screen):
    """设置屏幕：settings 模式的根屏幕。"""

    BINDINGS = [Binding("escape", "app.switch_mode('main')", "返回主模式")]

    CSS = """
    #settings-title {
        margin: 1 2;
        text-style: bold;
        color: $accent;
    }
    #settings-tip {
        margin: 0 2;
    }
    #back-main {
        margin: 1 2;
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("设置屏幕（settings 模式）", id="settings-title")
        yield Label("每个模式拥有独立的屏幕栈。按 Esc 或点按钮返回 main 模式。", id="settings-tip")
        yield Button("返回主模式", variant="primary", id="back-main")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-main":
            self.app.switch_mode("main")


class ScreenModesDemo(App):
    """Screen 栈、MODES 多模式与 ModalScreen 对话框示例。"""

    BINDINGS = [Binding("q", "quit", "退出")]

    # MODES 的值必须是屏幕类或可调用对象，不能是屏幕实例
    # （实例会在初始化时抛 TypeError，app.py:2604-2608）。
    MODES = {
        "main": MainScreen,
        "settings": SettingsScreen,
    }

    def on_mount(self) -> None:
        # App 启动时处于内置默认模式 "_default"（DEFAULT_MODE，app.py:390），
        # 这里显式进入 main 模式。
        self.switch_mode("main")


if __name__ == "__main__":
    ScreenModesDemo().run()
```

保存为 `screen_modes_demo.py`，运行 `python screen_modes_demo.py`：点「打开模态对话框」（或对话框打开后输入文字回车/点确定/Esc）体验 `dismiss` 结果回传；点「切换到设置模式」或按 `s` / `Esc` 在两个模式间切换；`q` 退出。

## 讲解

### 1. Screen 与 ModalScreen 的类关系

`Screen(Generic[ScreenResultType], Widget)` 定义于 `src/textual/screen.py:148`（F-T-054），其 `__init__` 把 `_modal` 置为 `False` 并创建自己的 `Compositor()`（`screen.py:289/291`）。`ModalScreen(Screen[ScreenResultType])`（`screen.py:2158`）在 `__init__` 末尾把 `_modal` 改为 `True`（`screen.py:2182`），默认 CSS 用 `$background 60%` 半透明背景压暗下层屏幕，并且模态屏幕的绑定链优先于 App 绑定——所以对话框打开时 `Esc` 由对话框的 `dismiss(None)` 接管，而不会触发 App 或下层屏幕的绑定。泛型参数 `ScreenResultType` 只用于类型标注，标明 `dismiss(result)` 回传值的类型，本例为 `ModalScreen[str | None]`。

### 2. 屏幕栈：push_screen / dismiss / pop_screen

- `App.push_screen(screen, callback=None, wait_for_dismiss=False, *, mode=None)`（`app.py:2895`，F-T-064）把屏幕压入指定模式（默认当前模式）的栈顶：向原活动屏幕投递 `ScreenSuspend`、向新屏幕投递 `ScreenResume`（`app.py:2943/2956`），并登记结果回调。`mode` 未知名抛 `UnknownModeError`（`app.py:2938`）；`wait_for_dismiss=True` 只能在 worker 中使用，否则抛 `NoActiveWorker`（`app.py:2958-2964`）——本例不使用该参数。
- `Screen.dismiss(result=None) -> AwaitComplete`（`screen.py:2048`，F-T-058）先调用结果回调栈顶 `_result_callbacks[-1]`（即 `push_screen` 传入的 callback，`screen.py:2064-2066`），再执行 `app.pop_screen()` 把自己弹出栈。**在被关闭屏幕自身的消息处理器中 `await self.dismiss()` 会抛 `ScreenError`**（`screen.py:2072-2077`），所以按钮/输入处理器里直接调用 `self.dismiss(value)` 而不 await；按键绑定则可用内置动作 `action_dismiss`（`screen.py:2100`），写作 `Binding("escape", "dismiss(None)", ...)`。
- 其余栈操作：`pop_screen()`（`app.py:3096`，栈中只剩一屏时抛 `ScreenStackError`）、`switch_screen(screen)`（`app.py:3001`，替换栈顶）、`install_screen(screen, name)`（`app.py:3036`，按名安装常驻屏幕）（F-T-065）。

### 3. MODES 多模式与 switch_mode

`App.MODES` 是类变量，类型为 `dict[str, str | Callable[[], Screen]]`（`app.py:361`），把模式名映射到**屏幕类或可调用对象**（不能是屏幕实例，`app.py:2604-2608`）。App 启动时处于内置默认模式 `DEFAULT_MODE = "_default"`（`app.py:390`），因此本例在 `on_mount` 中调用 `self.switch_mode("main")` 进入首个业务模式。

`App.switch_mode(mode)`（`app.py:2630`，F-T-069）切换当前模式：旧屏幕收 `ScreenSuspend`、目标模式的根屏幕收 `ScreenResume`（`app.py:2653/2670`），每个模式各自维护一条独立屏幕栈；切换到未知模式抛 `UnknownModeError`（`app.py:2648-2649`）。配套的 `remove_mode(mode)`（`app.py:2699`）移除模式，但移除**当前活动模式**会抛 `ActiveModeError`（`app.py:2711-2712`）。按键绑定里的动作串 `app.switch_mode('settings')` 对应 App 内置动作 `action_switch_mode`（`app.py:4502`）。

## 相关概念

- [18 · Screen 栈：模式、焦点管理与屏幕切换](/concepts/18-textual-screen-stack.md)
- [13 · App 入口：类变量契约、run 循环与 notify](/concepts/13-textual-app-entry.md)
- [17 · 事件体系、按键绑定与 @on 装饰器](/concepts/17-textual-events-bindings.md)
