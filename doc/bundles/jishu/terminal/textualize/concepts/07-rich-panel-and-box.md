---
type: Concept
title: "Panel 与 Box：32 字符盒模型与 18 种边框"
description: 解析 Rich 的 Panel 容器组件与 Box 盒模型：Panel 构造与 fit 紧缩模式、Box 的 32 字符盒位定义、18 种边框常量及 LegacyWindows/ASCII 替换规则。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---
# Panel 与 Box：32 字符盒模型与 18 种边框

## 概述

`Panel`（F-R-085）与 `Box`（F-R-087..089）构成 Rich 的「带边框容器」能力：`Panel` 是渲染容器，把任意 renderable 用一个带标题（title）与说明（subtitle）的外框夹住；`Box` 是盒模型常量集合，用 8 行字符定义一个盒子的全部 32 个框位字符。本文依事实 F-R-085..089 拆解 `Panel` 的构造、`fit` 模式，以及 `Box` 的字符布局、18 种预设边框与兼容替换规则。

## Panel 构造

`Panel(renderable, box=ROUNDED, *, title=None, title_align="center", subtitle=None, subtitle_align="center", safe_box=None, expand=True, style="none", border_style="none", width=None, height=None, padding=(0, 1), highlight=False)`（F-R-085）：

- `renderable` 是被包裹的内容，可为任意可渲染对象（走 Rich 渲染协议）。
- `box` 默认 `ROUNDED`（圆角边框，来自 `box.py` 模块级常量），默认边框风格与 `Table` 的 `HEAVY_HEAD` 不同——Panel 优先圆角。
- `title` / `subtitle` 为 str 时经 `Text.from_markup` 解析（F-R-086 属性 `_title`/`_subtitle`），因此标题里可使用 markup 标签与样式。
- `expand=True`（默认）：面板铺满可用宽度；`width` / `height` 显式指定时覆盖之。
- `padding=(0, 1)`：内容四周内边距，与 Table 一致。

```python
from rich.panel import Panel
from rich.console import Console

console = Console()
panel = Panel(
    "核心内容",
    title="[bold blue]标题[/]",
    subtitle="subtitle",
    border_style="cyan",
)
console.print(panel)
```

`Panel.fit(cls, renderable, box=ROUNDED, *, ...)`（F-R-086，classmethod）与 `__init__` 同参但**强制 `expand=False`**：面板收缩到恰好包裹内容的最小宽度，而非铺满，适用于让面板贴合内容宽度的场景。

```python
from rich import print
print(Panel.fit("[green]紧凑面板[/]", title="fit 模式"))
```

`Panel` 同时实现 `__rich_console__` 与 `__rich_measure__`（F-R-086），因此像 Table 一样既可渲染也可测量，能被 Console 纳入统一布局。

## Box：32 字符盒模型

`Box.__init__(self, box: str, *, ascii: bool = False)`（F-R-087）解析一段**8 行的字符串**，`box.splitlines()` 后每行 4 个字符，逐字符解包成 32 个字符属性，构成一个盒子视觉骨架的完整位点：

| 行 | 解包出的 4 个字符属性 |
|---|---|
| 第 1 行 | `top_left`、`top`、`top_divider`、`top_right` |
| 表头行 | `head_*`（表头上排） |
| 表头分割行 | `head_row_*`（表头与正文间的横线） |
| 中间分割行 | `mid_*`（正文行间横线） |
| 普通数据行 | `row_*`（正文行上下线） |
| 表脚分割行 | `foot_row_*` |
| 表脚行 | `foot_*` |
| 第 8 行 | `bottom_*`（下排） |

即每个「横断视图」（top、head_row、mid、row、foot_row、foot、bottom）都由`左角、横线、分隔符、右角`四类位点组成，因此一个垂直方向上的不同行的边角与分隔字符可以彼此不同——这正是 `HEAVY_HEAD`、`DOUBLE_EDGE` 等边框"上重下轻 / 双重边 / 混合线宽"风格能成立的根本原因：**边框不是一条直线，而是 32 个可选字符的组合矩阵**。

## 18 种边框常量

`box.py` 模块级定义了 18 个 `Box` 实例常量（F-R-089）：

| 常量 | 特征 |
|---|---|
| `ASCII` | 纯 ASCII 字符盒（`+`/`-`/`|`），`ascii=True` |
| `ASCII_DOUBLE_HEAD` | ASCII 盒 + 双重表头 |
| `SQUARE` | 直角方框 |
| `SQUARE_DOUBLE_HEAD` | 方框 + 双重表头 |
| `MINIMAL` | 极简（去外框侧边） |
| `MINIMAL_HEAVY_HEAD` | 极简 + 重点表头 |
| `MINIMAL_DOUBLE_HEAD` | 极简 + 双重表头 |
| `SIMPLE` | 简单线框 |
| `SIMPLE_HEAD` | 简单线框 + 表头 |
| `SIMPLE_HEAVY` | 简单线框 + 重点线 |
| `HORIZONTALS` | 仅横向线 |
| `ROUNDED` | 圆角边框（Panel 默认） |
| `HEAVY` | 重点（粗）线框 |
| `HEAVY_EDGE` | 重点外缘 |
| `HEAVY_HEAD` | 重点表头（Table 默认） |
| `DOUBLE` | 双重线框 |
| `DOUBLE_EDGE` | 双重外缘 |
| `MARKDOWN` | Markdown 表格风格 |

`Table` 的 `box` 默认取 `box.HEAVY_HEAD`，`Panel` 默认取 `box.ROUNDED`——同一盒模型在不同容器间以常量选择不同视觉风格。

## 兼容替换规则

`Box.substitute(self, options, safe=True) -> Box`（F-R-088）在渲染期做两项替换，保证兼容性：

- **Legacy Windows**：当 `options.legacy_windows and safe` 时，从 `LEGACY_WINDOWS_SUBSTITUTIONS` 查到可用替代盒，把不支持的 Unicode 框线字符替换为兼容字符。
- **ASCII-only**：当 `options.ascii_only and not box.ascii` 时整体替换为 `ASCII` 盒，确保纯 ASCII 终端下不出现乱码。

另有 `get_plain_headed_box()`（F-R-088）查 `PLAIN_HEADED_SUBSTITUTIONS`，把带复杂表头的盒子降级为平头版本；`get_top(widths)` / `get_row(...)` / `get_bottom(widths)`（F-R-088）则按列宽拼接出盒子顶线、行跨线与底线，供渲染层绘制。

因此 Box 既描述了"盒子长什么样"（32 字符盒模型），也承担了"在不同终端特性下降级绘制"的兼容职责，是 Rich 跨终端一致性（Safe Box）的关键一环。

## 与 Table 的关系

`Table` 与 `Panel` 共用同一 `Box` 盒模型：`Table` 用 `box.HEAVY_HEAD` + `show_lines`/`expand`/`padding` 等参数在 8 行盒骨架上扩展出多列、表头表脚与分段线；`Panel` 用 `ROUNDED` + `title`/`subtitle` 复用 `top_left`/`head_*`/`foot_*`/`bottom_*` 等位点绘制标题栏。理解 32 字符盒位点，即可推知某一边框在"表头有无、行间有无横线"时的具体表现。

## 相关概念

- /concepts/06-rich-table.md —— Table 表格组件，Box 盒模型在网格场景的落地与默认 `box.HEAVY_HEAD`
- /concepts/02-rich-text-and-markup.md —— Text/Markup，`Panel.title` 的 `Text.from_markup` 解析来源
- /concepts/01-rich-console-and-protocol.md —— Console 渲染入口，Panel 的 `__rich_console__`/`__rich_measure__` 调用链
- /references/rich.md —— Rich 仓库信源登记