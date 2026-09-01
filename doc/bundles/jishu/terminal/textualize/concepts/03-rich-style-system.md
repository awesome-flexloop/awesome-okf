---
type: Concept
title: Style 样式系统与位掩码属性
description: Style 是 Rich 样式核心对象，以位掩码紧凑存储 13 个布尔效果属性，提供 parse、from_color、combine、chain 等工厂方法与 StyleStack 样式堆栈。
tags: [textualize, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources:
  - id: "rich"
    resource: "/references/rich.md"
    title: "Rich 仓库信源登记"
---
# Style 样式系统与位掩码属性

## 概述

`Style`（`style.py`）是 Rich 描述「一段文本长什么样」的核心对象：既包含前景色（`color`）、背景色（`bgcolor`）、链接（`link`）与元数据（`meta`），也以**位掩码（bitmask）**紧凑记录 13 个布尔型效果属性（加粗、斜体、下划线等）。它提供解析字符串的 `parse`、按颜色构造的 `from_color`，以及组合（`combine`/`chain`）等工厂方法；`StyleStack` 则管理渲染期的样式进出栈。

> 事实范围：F-R-019..022（style.py）。

## 样式属性集合

`Style` 构造签名（全部 `Optional` 关键字参数）（F-R-019）：

```python
Style(
    *,
    color=None, bgcolor=None,
    bold=None, dim=None, italic=None, underline=None,
    blink=None, blink2=None, reverse=None, conceal=None,
    strike=None, underline2=None, frame=None, encircle=None,
    overline=None, link=None, meta=None,
)
```

其中 `color`/`bgcolor` 为 `Color`，`link`/`meta` 承载链接与元数据，其余为布尔效果属性。

## 位掩码存储

内部以 `_set_attributes`/`_attributes` 两个整型位掩码记录 13 个布尔属性，每个效果占 1 个比特位（F-R-019）：

| 属性 | 位值 | 属性 | 位值 |
|---|---|---|---|
| `bold` | 1 | `italic` | 4 |
| `underline` | 8 | `blink` | 16 |
| `blink2` | 32 | `reverse` | 64 |
| `conceal` | 128 | `strike` | 256 |
| `underline2` | 512 | `frame` | 1024 |
| `encircle` | 2048 | `overline` | 4096 |
| `dim` | 2 | | |

位掩码方案让「是否已显式设置某个属性」与「取值真假」可高效读写，也便于 `_add`（`__add__` 语义）在合并两个 Style 时按位叠加，仅对已显式设置的位做覆盖。

## 工厂类方法（classmethod）

（F-R-020）

- `null()`：返回模块级 `NULL_STYLE`（空样式单例）；
- `from_color(color=None, bgcolor=None)`：仅由前景/背景色构造；
- `from_meta(meta=None)`：由元数据字典构造；
- `on(meta=None, **handlers)`：构造并绑定事件回调；
- `parse(style_definition: str) -> Style`：把 `"bold red on rgb(0,0,0)"` 这类字符串解析成 `Style`，是 markup 样式名解析的底层入口；
- `combine(styles: Iterable[Style])`：合并一组样式；
- `chain(*styles: Style)`：按顺序链式叠加；
- `normalize(style: str) -> str` / `pick_first(*values)`：迭代组合时的归一化与首值选取。

## 实例方法、属性与运算

（F-R-021）

- 方法：`render(text, color_system, reset=True)`、`copy()`、`clear_meta_and_links()`、`update_link(link=None)`、`get_html_style(theme=None)`、`_make_ansi_codes(color_system)`；
- 属性：`color`、`bgcolor`、`link`、`meta`、`link_id`、`transparent_background`、`background_style`、`without_color`；
- 运算：`__add__` 经内部 `_add` 合并两个样式。

```python
from rich.style import Style
s = Style.parse("bold red on #0000ff")
s2 = Style.from_color(color=None)          # 仅按颜色构造
merged = s2 + Style(underline=True)        # __add__ 合并
```

## StyleStack 样式堆栈

`class StyleStack`（F-R-022）：

- `__init__(self, default_style: Style)`；
- 属性 `current`（当前生效样式）；
- `push(style: Style)` / `pop() -> Style`。

`markup.render()`（见 `/concepts/02-rich-text-and-markup.md`）与 Markdown 渲染均依赖 `StyleStack` 管理嵌套标签的样式进出栈。

## Style 与 Span 边界

Style 描述「样式值」本身（颜色 + 效果位掩码），**不包含位置信息**；要作用于文本的某一段，需要用 `Text` 中的 `Span(start, end, style)` 将 `Style` 绑定到 `[start, end)` 字符区间（见 `/concepts/02-rich-text-and-markup.md` 的「Style 与 Span 边界」小节）。因此 CSS 式的关系是：**一个 Style 可被多个 Span 复用**，Span 只持有 Style 的引用/字符串名，渲染期再由 Console 解析成 ANSI 码输出。

## 相关概念

- Style 如何通过 Span 绑定到文本区间：[/concepts/02-rich-text-and-markup.md](02-rich-text-and-markup.md)
- Console 用 StyleStack 组装输出样式：[/concepts/01-rich-console-and-protocol.md](01-rich-console-and-protocol.md)
- 高亮器如何结合样式类前缀生成区间：[/concepts/04-rich-highlighters.md](04-rich-highlighters.md)
- 信源登记：[/references/rich.md](/references/rich.md)