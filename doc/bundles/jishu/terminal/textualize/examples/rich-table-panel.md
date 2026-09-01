---
type: Example
title: "rich 示例：Table + Panel + box 组合排版"
description: 用 Table 构建带标题的多列表格，以 box.DOUBLE 覆盖默认 HEAVY_HEAD 边框，再嵌进 Panel 形成「面板 + 表格」组合排版，展示 32 字符盒模型与 18 种边框常量的应用。
tags: [textualize, rich, example]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---
# rich 示例：Table + Panel + box 组合排版

> 概念入口：[Table 表格](/concepts/06-rich-table.md) · [Panel 与 Box 盒模型](/concepts/07-rich-panel-and-box.md)

## 概述

本示例演示 Rich 结构化排版的两个核心组件如何组合：用 **`Table`**（F-R-052）声明「表头 + 单元格」的多列网格，用 **`Panel`**（F-R-085）作为带标题/说明的外框把表格夹住，并通过 **`Box`** 常量（F-R-087..089）切换边框风格（`box.DOUBLE` 覆盖 `Table` 默认的 `box.HEAVY_HEAD`）。三种组件彼此独立却共用同一渲染协议，最终被 `Console` 统一输出。

> 事实范围：F-R-052（Table 构造）、F-R-054（add_column）、F-R-055（add_row）、F-R-085（Panel 构造）、F-R-087..089（Box 盒模型与 18 种常量）。

## Table 构建多列网格

`Table(*headers, title=None, box=box.HEAVY_HEAD, show_lines=False, header_style="table.header", ...)`（F-R-052）——`str` 类型位置参数会经 `add_column(header=...)` 转列，默认边框为 `HEAVY_HEAD`、默认隐藏行间线。这里用 `add_column`（F-R-054）逐列设置对齐与样式，用 `add_row`（F-R-055）填充数据。

```python
from rich.table import Table
from rich.console import Console
from rich import box

console = Console()

table = Table(
    title="Textualize 生态",      # 标题（默认居中）
    box=box.DOUBLE,               # 覆盖默认 box.HEAVY_HEAD
    show_lines=True,             # 显示行间横线
    header_style="bold magenta",
)
table.add_column("序号", justify="center", style="cyan")
table.add_column("框架", style="bold")
table.add_column("特点")
table.add_row("1", "Rich", "终端富文本渲染")
table.add_row("2", "Textual", "终端 TUI 框架")
table.add_row("3", "Frogmouth", "Markdown 查看器")

console.print(table)
```

期望输出（无真实终端时不含 ANSI 转义序列）：`//` 由 `box.DOUBLE` 绘制的双重线框包围三列三行网格，顶部居中标题「Textualize 生态」，表头「序号 框架 特点」以加粗品红显示，数据行间有横线。若去掉 `box=box.DOUBLE`，则回落到 `Table` 默认的 `HEAVY_HEAD`（重点表头）边框——同一盒模型的不同常量决定视觉风格。

## Panel 包裹表格并叠加标题

`Panel(renderable, box=ROUNDED, *, title=None, subtitle=None, border_style="none", padding=(0, 1), ...)`（F-R-085）默认 `ROUNDED` 圆角框、`expand=True` 铺满宽度；`title`/`subtitle` 为 str 时经 `Text.from_markup` 解析（F-R-086），因此标题内也可用 markup 标签。

```python
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich import box

console = Console()

table = Table(title="Textualize 生态", box=box.DOUBLE, show_lines=True,
              header_style="bold magenta")
table.add_column("序号", justify="center", style="cyan")
table.add_column("框架", style="bold")
table.add_column("特点")
table.add_row("1", "Rich", "终端富文本渲染")
table.add_row("2", "Textual", "终端 TUI 框架")
table.add_row("3", "Frogmouth", "Markdown 查看器")

panel = Panel(
    table,                             # Panel 包裹任意 renderable（Table 亦然）
    title="[bold]面板 + 表格组合[/bold]",
    subtitle="box=DOUBLE 覆盖 Table 默认 HEAVY_HEAD",
    border_style="green",
    padding=(1, 1),
)
console.print(panel)
```

期望输出：绿色圆角边框（`ROUNDED`）将整张 `DOUBLE` 线框表格夹住，面板顶部标题「面板 + 表格组合」、底部说明居中展示。由于 `Table` 与 `Panel` 都实现 `__rich_console__`/`__rich_measure__`（F-R-056、F-R-086），`Table` 可作为 `Panel.renderable` 直接嵌套。

## Box 常量对比：ASCII

`panel.py` 的 `Panel.fit(cls, renderable, box=ROUNDED, *, ...)`（F-R-086）是 `__init__` 同参但强制 `expand=False` 的 classmethod。`box.ASCII`（F-R-089）是 `ascii=True` 的纯字符盒（`+`/`-`/`|`），支持在纯 ASCII 终端下渲染而不产生乱码。

```python
from rich import print
from rich.panel import Panel
from rich import box

print(Panel.fit("[green]Panel.fit 紧凑模式[/green]", box=box.ASCII, title="ascii"))
```

期望输出（此段已实测运行）：

```
+------ ascii -------+
| Panel.fit 紧凑模式 |
+--------------------+
```

`Panel.fit` 让面板收缩到恰好包裹内容，`box.ASCII` 提供确定性可见的 ASCII 盒——便于在非彩色终端/文档中观察盒结构。

## 讲解：盒模型是三者协作的公共语言

- **Box**（F-R-087..089）用 8 行字符串定义 32 个框位字符（`top_left`、`head_*`、`row_*`、`bottom_*`……），18 个模块级常量（`HEAVY_HEAD`、`DOUBLE`、`ROUNDED`、`ASCII`……）各自预设一套「组合矩阵」，供 `Table` 与 `Panel` 复用；
- **Table** 默认取 `box.HEAVY_HEAD`，**Panel** 默认取 `box.ROUNDED`（F-R-089），二者通过 `box=` 参数在构造时选用同一盒模型的不同风格；
- 组合规则：`Table` 作为 renderable 传入 `Panel`，`Console`（F-R-046）递归调用二者的 `__rich_console__` 完成逐段渲染。

于是「换盒」只需改一个 `box` 常量，边框视觉与数据结构彻底解耦——这是 `Box` 盒模型设计的核心价值。

## 相关概念

- Table 表格（Column/Row 数据模型与宽度计算）：[/concepts/06-rich-table.md](/concepts/06-rich-table.md)
- Panel 与 Box（32 字符盒模型与 18 种边框）：[/concepts/07-rich-panel-and-box.md](/concepts/07-rich-panel-and-box.md)
- Console 渲染入口：[/concepts/01-rich-console-and-protocol.md](/concepts/01-rich-console-and-protocol.md)
- 信源登记：[/references/rich.md](/references/rich.md)