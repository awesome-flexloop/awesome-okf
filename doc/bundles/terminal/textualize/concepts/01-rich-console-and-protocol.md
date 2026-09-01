---
type: Concept
title: rich 入门：渲染协议与 Console
description: 剖析 rich 渲染协议三要素（is_renderable / RichCast / RenderableType），沿 Console.render 递归主线理解协议判定、__rich__ 降级与 Segment 流生成，并掌握 Console 构造与选项入口。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources:
  - id: "rich"
    resource: /references/rich.md
    title: Rich 仓库信源登记
---
# rich 入门：渲染协议与 Console

## 概述

Rich 是一个终端富文本渲染库，其核心是一条**渲染协议（Console Protocol）**：任何对象只要满足协议约定，就能被 `Console` 渲染成终端可见的样式化输出。本概念沿「**协议判定 → Console.render 递归 → Segment 流**」主线讲解：如何判定一个对象可被渲染（`is_renderable`）、协议定义了哪些类型（`RenderableType` 三成员）、如何统一降级为可渲染对象（`__rich__` / `rich_cast`）、以及 `Console.render` 如何递归地把 renderable 解析为 `Segment`（段落）流。

## 协议判定入口：is_renderable

判断任意对象「是否可被 Console 渲染」，由 `protocol.py` 的模块级函数承担：

```python
# rich/protocol.py
def is_renderable(check_object: Any) -> bool:
    return (
        isinstance(check_object, str)
        or hasattr(check_object, "__rich__")
        or hasattr(check_object, "__rich_console__")
    )
```

三条路径即**三条件**（F-R-001）：普通字符串、实现了 `__rich__` 协议的对象、实现了 `__rich_console__` 协议的对象。满足任一即视为可渲染。

## 渲染协议类型：RenderableType 三成员

协议类型集中在 `console.py`，由两个 `Protocol` 类与一个 `Union` 别名构成 `RenderableType`（F-R-039）：

```python
# rich/console.py
class RichCast(Protocol):                  # @runtime_checkable
    def __rich__(self) -> Union["ConsoleRenderable", "RichCast", str]: ...
class ConsoleRenderable(Protocol):         # @runtime_checkable
    def __rich_console__(self, console: "Console", options: "ConsoleOptions") -> "RenderResult": ...
RenderableType = Union[ConsoleRenderable, RichCast, str]
RenderResult = Iterable[Union[RenderableType, Segment]]
```

- **ConsoleRenderable**：核心协议，要求对象实现 `__rich_console__(self, console, options)`，返回 `RenderResult`。
- **RichCast**：降级协议，要求实现可链式返回 renderable 的 `__rich__()`。
- **str**：字符串直接作为 renderable。
- **RenderResult** 是 `Iterable[Union[RenderableType, Segment]]`，允许产出「另一可渲染对象」或直接产出 `Segment`——这正是 `Console.render` 递归展开的依据。

## 对象降级：__rich__ 协议与 rich_cast

`RichCast` 的 `__rich__` 允许一个对象「变身」为另一个可渲染对象，`protocol.py` 的 `rich_cast()` 负责递归调用：

```python
# rich/protocol.py
def rich_cast(renderable: object) -> "RenderableType":
    from rich.console import RenderableType
    rich_visited_set: Set[type] = set()  # 防止潜在无限循环
    while hasattr(renderable, "__rich__") and not isinstance(renderable, type):
        if hasattr(renderable, _GIBBERISH):       # 挡下伪装对象
            return repr(renderable)
        cast_method = getattr(renderable, "__rich__")
        renderable = cast_method()
        if type(renderable) in rich_visited_set:
            break
        rich_visited_set.add(type(renderable))
```

要点（F-R-002）：`while` 循环反复调用 `__rich__()` 逐层降级；用 `rich_visited_set: Set[type]` 记录已出现的类型以跳出循环；模块级常量 `_GIBBERISH`（`"aihwerij235234..."`）用于识别「声称拥有全部属性」的伪装对象——若对象 `hasattr(renderable, _GIBBERISH)` 则直接返回 `repr(renderable)`。

## Console.render 递归解析

渲染核心 `Console.render(renderable, options=None) -> Iterable[Segment]`（F-R-046 / `console.py`）串联协议、降级与分段：

```python
# rich/console.py（节选）
def render(self, renderable, options=None) -> Iterable[Segment]:
    _options = options or self.options
    if _options.max_width < 1:
        return  # 无空间，防递归错误
    renderable = rich_cast(renderable)
    if hasattr(renderable, "__rich_console__") and not isinstance(renderable, type):
        render_iterable = renderable.__rich_console__(self, _options)
    elif isinstance(renderable, str):
        text_renderable = self.render_str(
            renderable, highlight=_options.highlight, markup=_options.markup)
        render_iterable = text_renderable.__rich_console__(self, _options)
    else:
        raise errors.NotRenderableError(
            "A str, Segment or object with __rich_console__ method is required")
    _options = _options.reset_height()
    for render_output in iter_render:
        if isinstance(render_output, Segment):
            yield render_output
        else:
            yield from self.render(render_output, _options)   # 递归
```

流程要点：

1. **先 `rich_cast`** 统一降级（`__rich__` 链）；
2. 有 `__rich_console__` 则调用之，str 则经 `render_str(...)` 再调用 `__rich_console__`，否则抛 `errors.NotRenderableError`；
3. 对产出的每个元素逐项判断：是 `Segment` 直接 `yield`，否则**递归 `self.render(...)`**（递归前 `_options = _options.reset_height()`）。

因此 `Console.render` 是一个「把 RenderResult 里的嵌套 renderable 一路展开成纯 `Segment` 流」的折叠器，`Segment` 是渲染的最终原子：`Segment` 为 NamedTuple，字段 `text`、`style`、`control`，属性 `cell_length`（control 非空时为 0）、`is_control`（F-R-024 / `segment.py`）。

## Console 构造配置入口

`Console.__init__` 提供大量关键字参数以控制渲染环境（F-R-042，节选关键项）：

```python
# rich/console.py
Console(
    color_system="auto",   # "auto"|"standard"|"256"|"truecolor"|"windows"
    force_terminal=None, force_jupyter=None, force_interactive=None,
    soft_wrap=False, theme=None, stderr=False, quiet=False,
    width=None, height=None, style=None, no_color=None, tab_size=8,
    record=False, markup=True, emoji=True, highlight=True,
    highlighter=ReprHighlighter(), legacy_windows=None, ...
)
```

初始化内部逻辑（F-R-043）：`get_time = get_time or monotonic`、`get_datetime = get_datetime or datetime.now`；`no_color` 未显式给定时取 `NO_COLOR` 环境变量；宽度/高度未给出时读 `COLUMNS`/`LINES`（Jupyter 下读 `JUPYTER_COLUMNS`/`JUPYTER_LINES`）。

常用入口方法与属性：

| 成员 | 事实 | 说明 |
|---|---|---|
| `console.options` | F-R-049 | 当前 `ConsoleOptions` |
| `console.file` | F-R-049 | 底层输出对象（getter/setter） |
| `console.width` / `height` / `size` | F-R-049 | 终端尺寸 |
| `Console.print(*objects, ...)` | F-R-044 | 打印入口，参数含 `sep`/`end`/`justify`/`overflow`/`highlight` 等；无对象且 `end == "\n"` 时以 `NewLine()` 替代 |
| `Console.measure(renderable, ...)` | F-R-045 | 转调 `Measurement.get(self, options or self.options, renderable)` |

## 选项上下文：ConsoleOptions 与 ConsoleDimensions

渲染过程中尺寸/风格上下文由 `ConsoleOptions`（dataclass）承载（F-R-037），其字段含 `size`、`legacy_windows`、`min_width`、`max_width`、`is_terminal`、`encoding`、`max_height`，以及默认值字段 `justify=None`、`overflow=None`、`no_wrap=False`、`highlight=None`、`markup=None`、`height=None`；属性 `ascii_only` 返回 `not self.encoding.startswith("utf")`。提供 `copy()`、`update(...)`（未改参数以哨兵 `NO_CHANGE`/`NoChange` 标记）、`update_width()`、`update_height()`、`reset_height()`、`update_dimensions()` 等（F-R-038）。最小尺寸快照由 `ConsoleDimensions(NamedTuple)` 给出，字段 `width`、`height`（F-R-036）。

## 相关概念

- /00-ecosystem-overview.md —— Textualize 生态总览，rich 在依赖分层中的基座定位
- /references/rich.md —— Rich 仓库信源登记（渲染协议与 Console 的模块归属）
- /references/textual.md —— Textual 仓库信源登记（rich 的框架层下游）