---
type: Concept
title: CSS 引擎、Worker 后台任务与 Driver 驱动层
description: Textual 三大基础设施：CSS 样式表引擎（加载/优先级/变量）、Worker 后台任务（线程/异步）与 Driver 驱动抽象层（抽象基类 + 五子类）。
tags: [textualize, textual, tui]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---

# CSS 引擎、Worker 后台任务与 Driver 驱动层

## 概述

`Textual` 的框架底座由三套彼此独立的基础设施构成：**CSS 引擎**把 `Stylesheet` 中的样式规则按特异性（specificity）合并到每个节点的 `Styles`/`RenderStyles`；**Worker** 体系把后台任务绑定到指定节点并隔离线程/协程执行；**Driver** 抽象层把终端差异封装进一套统一接口，使同一套 `App` 能以 Linux 终端、内联终端、Windows 终端、Web（浏览器）或无头（headless）模式运行。三者分别对应 `src/textual/css/`、`src/textual/worker*.py` 与 `src/textual/driver.py(＋drivers/)`，是理解渲染、异步与平台适配的关键。

## CSS 样式表加载与优先级

`Stylesheet` 定义于 `src/textual/css/stylesheet.py:145`，构造 `__init__(*, variables=None)`，初始化 `_rules: list[RuleSet]`、`_rules_map`、`_variables`、`source: dict[CSSLocation, CssSource]`、`_require_parse`、`_invalid_css`、`_parse_cache: LRUCache(64)`、`_style_parse_cache: LRUCache(1024 * 4)`。

- 加载源：`Stylesheet.read(filename)`（`:288`）、`read_all(paths)`（`:308`）从文件读取；`add_source(css, read_from=None, is_default_css=False, tie_breaker=0, scope="")`（`:333`）注入 CSS 字符串——`read_from` 缺省为 `("", str(hash(css)))`，同位置相同 CSS 内容去重（仅更新 `tie_breaker`），调用后置 `_require_parse = True`、`_rules_map = None`。
- 解析与作用域：`parse()`（`:372`）统一解析所有源；`add_source` 的 `scope` 参数可把规则限定到某 CSS 类型名；`parse_style(style_text)`（`:223`）解析单条样式。
- 应用：`apply(node, *, animate=False, cache=None)`（`:470`）按 `node._selector_names` 过滤规则，对每条匹配规则按 `Specificity6` 降序排序取最高优先级构建 `rules_map`，最终 `node._css_styles.merge_rules(rules_map)`；同时设置节点标志 `_has_hover_style`、`_has_focus_within`、`_has_order_style`、`_has_odd_or_even`。
- 更新：`replace_rules(...)`（`:636`）、`update(root, animate=False)`（`:703`）、`update_nodes(nodes, animate=False)`（`:713`）。
- 异常：`StylesheetParseError(StylesheetError)`（`:34`）、`StylesheetErrors`（`:44`，渲染错误面板含行号代码片段）。

### CSS 变量

`Stylesheet` 支持通过变量统一主题值：`set_variables(variables: dict[str, str])`（`:211`）写入变量表并失效变量 token 缓存，内部以 `_variables: dict[str, str]` 存放，`tokenize_values(self._variables)` 预解析。文档中变量以 `$name` 形式引用（如 `$background`、`$screen-selection-background` 等。）

### 应用链路

样式最终流向 `DOMNode` 的渲染样式对象（F-T-115 交叉事实）：`Stylesheet.add_source` → `parse()` → `apply(node)` 按特异性合并到 `node._css_styles`（类型 `RulesMap`）→ 由 `DOMNode.styles`（`RenderStyles`）合并 `_css_styles` 与 `_inline_styles`（内联样式优先级更高）。样式对象层次为 `RulesMap(TypedDict)` ← `StylesBase` ← `Styles`/`RenderStyles`（`src/textual/css/styles.py:88/223/886/1334`），其中 `Styles.parse(css, read_from, *, node=None)` classmethod 解析 CSS 字符串生成 `Styles`（`:772`）。

## Worker 后台任务

`Worker` 体系把长时间任务移到后台并绑定到节点生命周期，避免阻塞 UI 主循环。

`Worker(Generic[ResultType])` 定义于 `src/textual/worker.py:119`，构造签名 `__init__(node, work, *, name="", group="default", description="", exit_on_error=True, thread=False)`；`description` 超 1000 字符截断加 `"..."`；构造末尾 `post_message(self.StateChanged(self, self._state))`。

- 状态：`WorkerState(enum.Enum)`：`PENDING=1`、`RUNNING=2`、`CANCELLED=3`、`ERROR=4`、`SUCCESS=5`（`worker.py:82-94`）。
- 消息：`Worker.StateChanged(Message, bubble=False, namespace="worker")` 携带 `worker` 与 `state` 字段（`:123`），供 UI 监听工作状态。
- 执行：`Worker.run() -> ResultType`（`:346`）按 `_thread_worker` 分派到 `_run_threaded()`（后台线程）或 `_run_async()`（协程）；`cancel()`（`:416`）置 `_cancelled=True`、取消 `_task`、`cancelled_event.set()`。
- 等待与异常：`wait()`（`:423`）在 worker 内部调用抛 `DeadlockError`，`PENDING` 状态抛 `WorkerError`，`ERROR` 抛 `WorkerFailed`，`CANCELLED` 抛 `WorkerCancelled`。模块异常：`WorkerError`（`:45`）、`WorkerFailed(WorkerError)`（`:49`）、`WorkerCancelled(WorkerError)`（`:61`）；`WorkType` TypeAlias 为协程/同步可调用/`Awaitable` 的 Union（`:100-104`）。
- 管理层：`App.workers` 属性返回 `WorkerManager`（`app.py:959`）。`WorkerManager`（`worker_manager.py:24`）构造接收 `app: App`，方法：`add_worker`（`:65`）、`start_all`（`:129`）、`cancel_all`（`:134`）、`cancel_group(node, group) -> list[Worker]`（`:139`）、`cancel_node(node) -> list[Worker]`（`:158`）、`async wait_for_complete(workers=None)`（`:172`）。
- 装饰器：`work(method=None, *, name="", group="default", exit_on_error=True, exclusive=False, description=None, thread=False)`（`_work_decorator.py:74`）；非协程函数未设 `thread=True` 时抛 `WorkerDeclarationError`（`:112-115`）——即同步耗时要显式声明 `thread=True` 才会在线程中执行。

其他跨线程工具：`App.call_from_thread(callback, *args, **kwargs)`（`app.py:1788`）从其他线程调度回调回主循环；`async App.run_action(...)`（`:4223`）、`App.set_focus(widget, scroll_visible=True)`（`:3150`）、`App.capture_mouse(widget)`（`:3222`）。

### Pilot（测试驾驶）

`Pilot(Generic[ReturnType])`（`src/textual/pilot.py:62`）构造接收 `app: App[ReturnType]`，异步方法 `press(*keys)`（`:76`）、`click(...)`（`:192`）、`hover(...)`（`:349`）、`pause(delay=None)`（`:535`）。`App.run_async` 在 `auto_pilot` 非空时创建 `Pilot(app)` 并在任务中执行回调（`app.py:2258-2277`），用于测试与自动化驾驶。

## Driver 抽象层

**Driver 抽象**是平台适配的统一接口，把「写终端、进入/退出应用模式、投递消息」等终端差异封装为基类抽象方法与钩子，让 `App` 与具体终端解耦。定义于 `src/textual/driver.py:17`，`Driver(ABC)` 构造签名 `__init__(app, *, debug=False, mouse=True, size=None)`，抽象方法为 `write(data: str)`、`start_application_mode()`、`disable_input()`、`stop_application_mode()`；属性 `is_headless`/`is_inline`/`is_web`/`can_suspend` 默认均返回 `False`（子类可覆盖）。

核心成员：

- 消息投递：`Driver.send_message(message)`（`:67-75`）经 `asyncio.run_coroutine_threadsafe(self._app._post_message(message), loop=self._loop)` 从驱动线程投递到主循环；`Driver.process_message(message)`（`:77-132`）按 `cursor_origin` 偏移修正 `MouseEvent` 坐标、维护 `_down_buttons` 列表，并在按住按键的 MouseMove 中补发 MouseUp。
- 生命周期钩子：`suspend_application_mode()`/`resume_application_mode()`（`:157/:166`）、`no_automatic_restart()` 上下文管理器（`:177`）、内嵌事件 `Driver.SignalResume(events.Event)`（`:174`）。
- 平台能力：`open_url(url, new_tab=True)`（`:195`）、`deliver_binary(binary, *, delivery_key, save_path, open_method="download", encoding=None, mime_type=None, name=None)`（`:208`，线程中分块写文件，成功/失败分别发 `DeliveryComplete`/`DeliveryFailed`）。

五个驱动子类（`src/textual/` 下的 `drivers/`）：

- `LinuxDriver(Driver)`（`linux_driver.py:38`）：标准 Linux 终端驱动，含 `_enable_mouse_support`、`_enable_bracketed_paste`、`start_application_mode`、`stop_application_mode`、`run_input_thread`、`process_message`、`can_suspend` 等。
- `LinuxInlineDriver(Driver)`（`linux_inline_driver.py:28`）：内联（inline）终端驱动，供 `App.run(inline=True)` 使用。
- `WindowsDriver(Driver)`（`windows_driver.py:16`）：Windows 终端驱动。
- `WebDriver(Driver)`（`web_driver.py:41`）：`is_web` 返回 True，另有 `write_meta`、`on_meta`、`open_url`、`deliver_binary`、`_on_meta`，用于浏览器端运行。
- `HeadlessDriver(Driver)`（`headless_driver.py:10`）：`is_headless` 返回 True，无真实终端，用于测试。

输入读取（`drivers/_input_reader.py`）按 `sys.platform == "win32"` 从 `_input_reader_windows` 或 `_input_reader_linux` 导入 `InputReader`；`drivers/win32.py` 定义 Win32 结构体（`COORD`、`KEY_EVENT_RECORD`、`MOUSE_EVENT_RECORD`、`WINDOW_BUFFER_SIZE_RECORD`、`INPUT_RECORD`）与 `set_console_mode`、`get_console_mode`、`enable_application_mode`、`wait_for_handles` 及 `EventMonitor(threading.Thread)`。

### 驱动选择：平台判定与 TEXTUAL_DRIVER 钩子

`App.__init__(driver_class=None, ...)`（`app.py:572-578`）默认传入 `driver_class=None`，此时由 `App.get_driver_class()`（`:1573`）决定：先检查环境变量钩子——读取 `constants.DRIVER`（由 `TEXTUAL_DRIVER` 环境变量设定，`constants.py:113`），若非 `None` 则按 `module:Symbol` 形式导入（`importlib.import_module` 后取属性），并校验其为 `Driver` 子类，否则报错；未设置时按平台回退，Windows（`sys.platform == "win32"`）选 `WindowsDriver`，否则选 `LinuxDriver`。

> 该 `TEXTUAL_DRIVER` 钩子可在不修改代码时强制指定任意 Driver 子类（例如 WebDriver / 无头驱动），是后续 Web/Serve 场景接入的预埋连接点，参见 [/concepts/25-textual-serve.md](/concepts/25-textual-serve.md) 与 [/concepts/26-textual-web.md](/concepts/26-textual-web.md)。

## 相关概念

- [/concepts/13-textual-app-entry.md](/concepts/13-textual-app-entry.md) — `App` 是 Worker/驱动/CSS 的宿主，构造签名与 `run()`/`run_async()` 入口
- [/concepts/25-textual-serve.md](/concepts/25-textual-serve.md) — 待文档化：Serve 场景的 Driver 接入
- [/concepts/26-textual-web.md](/concepts/26-textual-web.md) — 待文档化：`WebDriver` 与浏览器运行机制
- [/references/textual.md](/references/textual.md) — Textual 仓库信源登记与模块清单