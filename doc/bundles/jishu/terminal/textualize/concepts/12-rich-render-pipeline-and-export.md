---
type: Concept
title: 渲染管线深潜：递归渲染、钩子、捕获与 HTML/SVG 导出
description: 深入 rich 渲染管线收尾篇：Console.render 递归规约主线、reset_height 高度复位、RenderHook 插入式钩子、Capture 输出捕获，以及 HTML/SVG 导出与 record 缓冲。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---

# 渲染管线深潜：递归渲染、钩子、捕获与 HTML/SVG 导出

## 概述

本文是 rich 概念文档的**进阶收尾篇**，聚焦 `Console` 渲染管线在「终端输出」之上的完整生命周期：`Console.render` 如何通过递归把任意 renderable 规约为 `Segment` 流（对应 `/concepts/01-rich-console-and-protocol.md` 的渲染协议主线）、`reset_height` 如何为嵌套渲染复位高度、`RenderHook` 如何插入式改写渲染过程、`Capture` 如何捕获输出而不落终端，以及 `record` 缓冲、`export_html`/`export_svg` 如何把管线结果导出为 HTML 与 SVG。覆盖事实 **F-R-040、F-R-041、F-R-046、F-R-047、F-R-048**，代码位于 `rich/console.py`。

## 渲染主轴：Console.render 的递归规约

`Console.render(renderable, options=None) -> Iterable[Segment]`（F-R-046）是管线的核心折叠器，它把「任意可渲染对象」逐层规约为纯 `Segment` 流：

```python
# rich/console.py（节选）
def render(self, renderable, options=None) -> Iterable[Segment]:
    renderable = rich_cast(renderable)          # 1. __rich__ 链降级
    if hasattr(renderable, "__rich_console__") and not isinstance(renderable, type):
        render_iterable = renderable.__rich_console__(self, _options)
    elif isinstance(renderable, str):
        text_renderable = self.render_str(renderable, highlight=..., markup=...)
        render_iterable = text_renderable.__rich_console__(self, _options)
    else:
        raise errors.NotRenderableError(...)    # 2. 非可渲染抛错
    _options = _options.reset_height()          # 3. 递归前复位高度
    for render_output in render_iterable:
        if isinstance(render_output, Segment):
            yield render_output                 # 4. 原子段直接产出
        else:
            yield from self.render(render_output, _options)  # 5. 递归展开
```

递归规约的要点：**先 `rich_cast`（F-R-002）统一降级**，让任意 `__rich__` 链对象变身；再按 `__rich_console__`/str 走对应渲染路径；产出的每个元素若已是 `Segment` 直接 `yield`（它就是渲染最终原子，见 `/concepts/05-rich-segment-and-measure.md`），否则**递归 `self.render(...)`** 继续展开——`RenderResult = Iterable[Union[RenderableType, Segment]]`（F-R-039）正是这一递归的依据。

### reset_height：嵌套渲染的高度复位

在递归展开前，代码执行 `_options = _options.reset_height()`（F-R-046、F-R-038）。原因是子 renderable 渲染出来的 `Segment` 会被高层容器（如 `Table`/`Layout` 的行列排布）拼接在一起，父层级的高度约束不应继续限制嵌套内容的行数——复位后每个子渲染都从「无高度上限」重新开始，避免嵌套结构被外层 `max_height` 意外裁剪。

## 插入式改写：RenderHook

`class RenderHook(ABC)`（F-R-040 / `console.py`）定义渲染过程的插入点，抽象方法：

```python
# rich/console.py
class RenderHook(ABC):
    @abstractmethod
    def process_renderables(
        self, renderables: List[ConsoleRenderable]
    ) -> List[ConsoleRenderable]:
        ...
```

它接收一簇待渲染对象，可返回一个新的列表（或改动用返回的同一个列表）替换原渲染列表。`Console` 提供成对的管理方法（F-R-048）：`push_render_hook(hook)` 注册、`pop_render_hook()` 弹出。典型的实现在 rich 生态中是 `Live`（`rich/live.py` 的 `class Live(JupyterMixin, RenderHook)`，F-R-080），它以 RenderHook 接口重绘前改写待渲染对象以叠加动态渲染层。

## 输出捕获：Capture

`Console` 的捕获能力由上下文管理器整套提供（F-R-041 / `console.py`）：

```python
# rich/console.py
class Capture:
    def __init__(self, console: "Console") -> None: ...
    def __enter__(self) -> "Capture":
        self._console.begin_capture()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._result = self._console.end_capture()
    def get(self) -> str: ...
class CaptureError(Exception): ...
```

`Console` 方法（F-R-048）与之对应的三件套：`begin_capture()` 开启捕获、`end_capture() -> str` 结束并返回捕获到的字符串、`capture() -> Capture` 返回一个 `Capture` 上下文管理器。使用方式：进入 `Console.capture()` 上下文期间打印的内容不再落到终端，而是被缓冲；上下文退出后调用 `cap.get()` 取回纯文本。若在上下文尚未退出时调用 `get()`，会抛 `CaptureError`（"Capture result is not available until context manager exits."）。注意 `Capture.get()` 返回的是**去样式后的字符串**，与 `export_text(styles=False)` 类似，不含样式信息。

```python
from rich.console import Console

console = Console(record=True)
with console.capture() as cap:
    console.print("This won't hit the terminal")
text = cap.get()  # 捕获到的原样文本
```

## 缓冲与导出：record / export_text / export_html / export_svg

### export_text：纯文本回放

`Console.export_text(*, clear: bool = True, styles: bool = False) -> str`（F-R-048）：把渲染缓冲回放为纯文本，`styles=False` 时剥离样式（默认）；`save_text(...)` 为存文件的便捷包装。

### HTML 导出

`export_html(...)`（F-R-048）把缓冲内容导出为内联 CSS 的 HTML 片段，`save_html(...)` 存文件。HTML 导出依赖样式系统把 `Style` 转成 CSS——`Style.get_html_style(theme)`（`rich/style.py`，`__html_style__`）负责把段样式映射为 CSS 类/内联样式（F-R-021）。配合 `Console(...)` 构造时的 `record` 参数生效：**只有当 `Console` 以 `record=True` 创建时，`Console.print` 等调用才会把产生的内容存入内部缓冲**，导出方法才有数据可读。

```python
from rich.console import Console
from rich.table import Table

table = Table("Name", "Count")
table.add_row("apple", "3")
table.add_row("pear", "5")

console = Console(record=True)   # 必须 record=True
console.print(table)
html = console.export_html()     # 导出内联 CSS 的 HTML
my_console.save_html("out.html") # 或直接存文件
```

### SVG 导出

`export_svg(...)`（F-R-048）把缓冲渲染为等宽字体的 SVG 矢量图（用于 README 徽章/文档插图），`save_svg(...)` 存文件。SVG 导出同样依赖 `record=True` 的缓冲数据，并受 `Console` 尺寸（宽高）影响——默认宽高来自终端环境，导出前可显式设置 `console.width` / `console.height`（F-R-049）以控制图形尺寸。

## 与其它渲染方法的联通

`Console` 的其余渲染/输出方法（F-R-047）与本文主线共享同一条递归逻辑：`render_lines(...)` 把 renderable 规约为「每行一个 segment 列表」的行结构，`render_str(...)` 把字符串经 markup/highlight 渲染为 `Text` 再走 `__rich_console__`，`rule(...)`、`out(...)`、`print_json(...)`、`print_exception(...)`、`log(...)` 等均最终落到 `render` 递归。结构复用的基座是「**一切皆递归规约为 `Segment` 流**」这条主线，导出与捕获只是对规约结果在不同宿主的落地。

## 相关概念

- /references/rich.md —— Rich 仓库信源登记（渲染管线相关模块归属）
- /concepts/01-rich-console-and-protocol.md —— 渲染协议三要素与 `Console.render` 递归入口（`RenderableType`/`rich_cast`/`NotRenderableError`）
- /concepts/05-rich-segment-and-measure.md —— `Segment` 渲染货币与 `Measurement` 测量协议（`render` 递归的原子产物与测量协议）