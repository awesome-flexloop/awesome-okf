---
type: Concept
title: DOMNode、Widget 与内置组件剖析（Button/Input/DataTable/TextArea）
description: 剖析 Textual 组件继承链 DOMNode→Widget→内置组件，讲解 __init_subclass__ 元编程收集 reactive/binding/compute、DOM 查询 API、四个内置组件（Button/Input/DataTable/TextArea）及后台 Worker。
tags: [textualize, textual, tui]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual", resource: "/references/textual.md", title: "Textual 仓库信源登记" }]
---
# DOMNode、Widget 与内置组件剖析（Button/Input/DataTable/TextArea）

## 概述

Textual 的一切可用组件都建立在统一继承链之上：`Message` ← `Event` ← 各事件，`MessagePump` ← `DOMNode` ← `Widget` ← `Screen`，同时 `App` 直接继承 `DOMNode`（F-T-112）。`DOMNode` 是「树节点 + 消息泵 + 响应式」的基座，`Widget` 在此之上加入布局、渲染、滚动与挂载能力，而 `Button`/`Input`/`DataTable`/`TextArea` 等内置组件则以 `Widget`/`ScrollView` 为父类，各自声明 reactive 属性、绑定、消息与 CSS 组件类。本文沿此继承链自上而下剖析，并补上后台执行单元 `Worker`。

开头延伸阅读：[/concepts/14-textual-message-system.md](/concepts/14-textual-message-system.md)（消息基座与派发）、[/concepts/15-textual-reactive.md](/concepts/15-textual-reactive.md)（响应式描述符）。

## DOMNode：`MessagePump` 的直接子类

`DOMNode(MessagePump)` 定义于 `src/textual/dom.py:135`（F-T-036）。构造签名 `__init__(*, name=None, id=None, classes=None)`，其中 `id` 与 `classes` 会经 `check_identifiers` 校验。每次创建实例时初始化：

- `_nodes: NodeList`（子节点列表）
- `_css_styles: Styles` 与 `_inline_styles: Styles`，并由二者合并出 `styles: RenderStyles`
- `_component_styles: dict[str, RenderStyles]`
- `_bindings`：取类级 `_merged_bindings.copy()`，未定义则用空 `BindingsMap`
- `_query_one_cache: LRUCache(1024)`（`query_one` 的结果缓存）

模块级异常 `BadIdentifier`、`DOMError`、`NoScreen(DOMError)`（F-T-043）在此抛出。

## `__init_subclass__`：继承时的元编程收集

`DOMNode.__init_subclass__(inherit_css=True, inherit_bindings=True, inherit_component_classes=True)` 在每个子类被定义时沿 MRO 执行（F-T-037）：

1. 收集所有 `Reactive` 描述符实例到 `cls._reactives`；
2. 计算 `cls._merged_bindings`（把基类与子类 `BINDINGS` 合并）；
3. 计算 `cls._css_type_names`；
4. 扫描以 `_compute_`/`compute_` 开头的方法名，去前缀后存集合 `cls._computes`。

由此，`BINDINGS`、reactive 属性、`watch_*`/`compute_*` 方法都在类定义时被统一登记，供派发系统、绑定表与样式系统在运行时查找。挂载完成后 `DOMNode._post_mount()` 会调用 `Reactive._initialize_object(self)` 初始化全部 reactive 属性（F-T-042）；`get_component_styles(*names) -> RenderStyles` 在 name 不在 `_component_styles` 时会抛 `KeyError`（F-T-042）。

## DOM 查询与 CSS 类 API

`DOMNode` 提供完整的节点查询与类名操作（F-T-038、F-T-039）：

- 查询：`query(selector=None) -> DOMQuery`、`query_children`、`query_one`（带 LRU 缓存）、`query_one_optional`、`query_exactly_one`、`query_ancestor`；selector 可为字符串（CSS 选择器）或 `Widget` 类型。
- CSS 类：`has_class(*class_names) -> bool`、`set_class(add, *class_names, update=True) -> Self`、`set_classes(classes)`、`add_class(*class_names, update=True)`、`remove_class(*class_names, update=True)`、`toggle_class(*class_names)`。

这是所有内置组件「通过类名做样式钩子」的底层能力支撑。

## Widget：可渲染组件基座

`Widget(DOMNode)` 定义于 `src/textual/widget.py:283`（F-T-045），类级声明了一组关键标志与 reactive 属性：`COMPONENT_CLASSES`、`BORDER_TITLE`、`BORDER_SUBTITLE`、`ALLOW_MAXIMIZE`、`ALLOW_SELECT=True`、`FOCUS_ON_CLICK=True`、`BLANK=False`、`can_focus=False`、`can_focus_children=True`。

Widget 自带一组 reactive 属性（F-T-046）：`expand`、`shrink`（布局伸缩）、`auto_links`、`disabled`、`loading`、`virtual_size`、`has_focus`、`mouse_hover`、`scroll_x/scroll_y`、`scroll_target_x/scroll_target_y`、`show_vertical_scrollbar/show_horizontal_scrollbar`。`Widget._PSEUDO_CLASSES` 把 19 个伪类（hover、focus、blur、disabled、enabled、dark、light、focus-within、first-child、odd、even、empty 等）映射到判定 lambda（F-T-047），供样式匹配使用。

核心生命周期与渲染方法（F-T-048~F-T-052）：

- `refresh(*regions, repaint=True, layout=False, recompose=False) -> Self`：置脏区并安排下一 idle 事件刷新；`recompose=True` 时置 `_recompose_required` 并 `call_next(self._check_recompose)`（F-T-048）。
- `mount(*widgets, before=None, after=None) -> AwaitMount`、`remove() -> AwaitRemove`、`focus(scroll_visible=True) -> Self`、`blur() -> Self`、`capture_mouse(capture=True)`、`move_child(...)`、`compose() -> ComposeResult`（F-T-049、F-T-050）。配套的 `AwaitMount`/`AwaitRemove`/`AwaitComplete` 分别定义于 `widget.py`、`await_remove.py`、`await_complete.py`。
- `render() -> RenderResult` 默认返回 `self.label`；`get_content_width/get_content_height` 可被子类覆盖（F-T-052）。
- 滚动 API 九件套：`scroll_to`、`scroll_relative`、`scroll_home`、`scroll_end`、`scroll_left/right/down/up`、`scroll_page_up/down/left/right`、`scroll_to_widget`、`scroll_to_region`、`scroll_visible`、`scroll_to_center`（F-T-051）。
- watcher 示例：`watch_hover_style`、`watch_scroll_x`、`watch_scroll_y`、`watch_has_focus`、`watch_disabled`（F-T-053）。

## 内置组件：Button

`Button(Widget, can_focus=True)`（`src/textual/widgets/_button.py:39`），`ALLOW_SELECT = False`；reactive：`label`、`variant="default"`、`compact`（`toggle_class="-textual-compact"`）、`flat`（F-T-087）。构造 `__init__(label=None, variant="default", *, name, id, classes, disabled, tooltip, action, compact, flat)`，`label is None` 时取 `css_identifier_styled`；`active_effect_duration = 0.2`（F-T-088）。

交互模型：`Button.Pressed(Message)` 携带 `button` 属性且 `control` 返回 button；`press()` 在 `disabled or not self.display` 时直接返回，否则 `action is None` 时 `post_message(Button.Pressed(self))`，否则经 `call_later(self.app.run_action, self.action, ...)` 执行动作；`_on_click` 先 `event.stop()`（F-T-089）。类方法 `success()`、`warning()`、`error()` 生成对应变体按钮；`validate_variant` 对非法变体抛 `InvalidButtonVariant`，`watch_variant`/`watch_flat` 负责切换 `-variant`、`-style-flat/-style-default` 类（F-T-090）。

```python
from textual.widgets import Button

def compose(self):
    yield Button("确定", variant="success", id="ok", action="submit")
```

## 内置组件：Input

`Input(ScrollView)`（`src/textual/widgets/_input.py:71`），`BINDING_GROUP_TITLE = "Input"`。reactive 覆盖：`value`、`selection`、`placeholder`、`password`、`_suggestion`、`restrict`、`type: var[InputType]("text")`、`max_length`、`valid_empty`、`compact`（F-T-091）。构造 `__init__(value=None, placeholder="", highlighter=None, password=False, *, restrict=None, type="text", max_length=0, suggester=None, validators=None, validate_on=None, valid_empty=False, select_on_focus=True, ...)`：`validators` 单实例自动包装为列表，`validate_on` 缺省取全部可能值集合（F-T-092）。

消息均为 `@dataclass` Message 且含 `control` 属性：`Changed`（字段 `input/value/validation_result`）、`Submitted`、`Blurred`（F-T-093）。`COMPONENT_CLASSES = {"input--cursor", "input--placeholder", "input--suggestion", "input--selection"}`；`cursor_position` 对应 `selection.end`；BINDINGS 含 `enter → submit`、`home,ctrl+a → home`、`ctrl+x/c/v → cut/copy/paste`（均 `show=False`）（F-T-094）。校验方法 `validate_selection(selection) -> Selection`、`validate(value) -> ValidationResult | None`（F-T-095）。

```python
from textual.widgets import Input

inp = Input(placeholder="输入...", password=True, max_length=20)
```

## 内置组件：DataTable

`DataTable(ScrollView, Generic[CellType], can_focus=True)`（`src/textual/widgets/_data_table.py:268`）。reactive：`show_header`、`show_row_labels`、`fixed_rows`、`fixed_columns`、`zebra_stripes`、`header_height`、`show_cursor`、`cursor_type: Reactive[CursorType]("cell")`、`cell_padding`、`cursor_coordinate`（`repaint=False, always_update=True`）、`hover_coordinate`（同构）（F-T-096）。

数据 API 与消息（F-T-097~F-T-099）：

- `add_column(label, *, width=None, key=None, default=None) -> ColumnKey`；`add_row(*cells, height=1, key=None, label=None) -> RowKey`、`add_columns`、`add_rows`、`clear(columns=False)`。
- `update_cell`、`update_cell_at`、`get_cell(row_key, column_key)`、`get_cell_at(coordinate)`、`get_cell_coordinate`；`remove_row`（不存在抛 `RowDoesNotExist`）、`remove_column`（不存在抛 `ColumnDoesNotExist`）。
- 消息：`CellHighlighted`、`CellSelected`、`RowSelected`、`HeaderSelected`。

BINDINGS 提供 `enter → select_cursor`、方向键 → `cursor_*`、翻页键 → `page_*`、`home/end → scroll_home/scroll_end` 等（均 `show=False`）；`COMPONENT_CLASSES` 含 `datatable--cursor`、`datatable--header`、`datatable--fixed`、`datatable--odd-row` 等 9 项（F-T-100）。

```python
from textual.widgets import DataTable

table = DataTable()
table.add_columns("名称", "版本")
table.add_row("textual", "0.58.0")
```

## 内置组件：TextArea

`TextArea(ScrollView)`（`src/textual/widgets/_text_area.py:112`）。reactive：`language`（`always_update=True`）、`theme="css"`、`selection`、`show_line_numbers`、`indent_width=4`、`soft_wrap=True`、`read_only=False`（F-T-101）。构造 `__init__(text="", *, language=None, theme="css", soft_wrap=True, tab_behavior="focus", read_only=False, show_cursor=True, show_line_numbers=False, line_number_start=1, max_checkpoints=50, ..., placeholder="")`，内部组装 `EditHistory`、`Document`、`WrappedDocument`、`DocumentNavigator`；`indent_type` 默认 `"spaces"`（F-T-102）。

消息 `Changed`、`SelectionChanged`（均 `@dataclass` 含 `control`）；编辑 API：`get_text_range(start, end) -> str`、`move_cursor`、`move_cursor_relative`、`replace(...)`、`insert_text_at_cursor(text)`（F-T-103）。`TextAreaLanguage`（含 `language: Language | None`）与 `_languages` 字典支持用户经 `register_language` 注册自定义语法高亮（F-T-104）。

```python
from textual.widgets import TextArea

code = TextArea("print(textual)", language="python", soft_wrap=True)
```

## Worker：后台执行单元

`Worker(Generic[ResultType])`（`src/textual/worker.py:119`）构造 `__init__(node, work, *, name="", group="default", description="", exit_on_error=True, thread=False)`，构造末 `post_message(self.StateChanged(...))`（F-T-072）。状态机 `WorkerState(PENDING/RUNNING/CANCELLED/ERROR/SUCCESS)`（F-T-073）；消息 `StateChanged(Message, bubble=False, namespace="worker")` 携带 `worker`/`state`（F-T-074）。`run()` 按是否线程 worker 分派 `_run_threaded`/`_run_async`，`cancel()` 取消任务，`wait()` 在内部调用抛 `DeadlockError`（F-T-075）。配套 `@work` 装饰器（`src/textual/_work_decorator.py:74`）声明异步方法为 worker，非协程函数未设 `thread=True` 时抛 `WorkerDeclarationError`（F-T-078）。

```python
from textual import work

@work(exclusive=True)
async def do_task(self):
    await self.some_async_op()
```

## 相关概念

- [/concepts/14-textual-message-system.md](/concepts/14-textual-message-system.md)：`MessagePump` 消息泵与 `Event` 事件基座，`DOMNode` 的父类链
- [/concepts/15-textual-reactive.md](/concepts/15-textual-reactive.md)：`Reactive` 描述符与 `watch_*`/`compute_*`，`__init_subclass__` 收集 reactive 的支撑机制
- [/concepts/17-textual-events-bindings.md](/concepts/17-textual-events-bindings.md)：内置组件 `BINDINGS` 与 `@on` 装饰器的交互细节
- /references/textual.md —— Textual 仓库信源登记