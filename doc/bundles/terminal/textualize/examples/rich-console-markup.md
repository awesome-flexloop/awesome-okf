---
type: Example
title: "rich 示例：Console.print 与标记语言样式"
description: 用 Console.print 输出带标记语言样式文本，演示 markup 标签（加粗/配色/自定义色/链接/嵌套）解析，以及 Style.parse 与 Style.from_color 两种样式构造方式。
tags: [textualize, rich, example]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich", resource: "/references/rich.md", title: "Rich 仓库信源登记" }]
---
# rich 示例：Console.print 与标记语言样式

> 概念入口：[Console 与渲染协议](/concepts/01-rich-console-and-protocol.md) · [Text 对象与标记语言](/concepts/02-rich-text-and-markup.md)

## 概述

本示例演示 Rich 最常用的一条链路：**`Console.print` 输出带「标记语言（markup）」样式的富文本**。`Console.print` 默认 `markup=True`（F-R-042），会把字符串里的 `[bold red] ... [/]` 标签交给 `markup.render()` 解析为 `Text`（F-R-011）再渲染；同时用 `Style.parse` 与 `Style.from_color` 两种方式（F-R-019..020）构造样式对象，展示「字符串式标签」与「对象式样式」的等价关系。

> 事实范围：F-R-042（Console 构造默认值）、F-R-043（Console 内部赋值）、F-R-044（print 签名）、F-R-011（markup.render）、F-R-019..020（Style 构造与 classmethod）。

## Console.print 与 markup 标签

`Console.print(self, *objects, sep=" ", end="\n", style=None, ..., markup=None, highlight=None, ...)`（F-R-044）。由于构造函数默认 `markup=True`、`highlight=True`（F-R-042），传给 `print` 的字符串直接按标签方言解析。

```python
from rich.console import Console

console = Console()

# 加粗 + 颜色
console.print("[bold red]这是粗体红色[/bold red]")
# 多个标签并列
console.print("[green]绿文本[/green] [cyan]青文本[/cyan]")
# 十六进制自定义色
console.print("[#ff00ff]自定义十六进制色[/#ff00ff]")
# 链接（@ 开头回调标签经 ast.literal_eval 解析）
console.print("[link=https://example.com]链接文本[/link]")
# 显式闭合与嵌套
console.print("[bold red]嵌套[/] [italic blue]斜体蓝[/italic blue]")
```

期望输出（无真实终端时不含 ANSI 转义序列，仅呈现文本内容）：五行文本依次为「这是粗体红色」「绿文本 青文本」「自定义十六进制色」「链接文本」「嵌套 斜体蓝」，在彩色终端中分别呈现对应颜色与效果。`markup` 标签由 `markup.render()` 的 `style_stack`/`spans` 解析（F-R-011）：`/` 开头的为闭合标签，标签失配会抛 `MarkupError`。

## Style.parse 解析样式定义

`Style.parse(style_definition: str) -> Style`（F-R-020）把「空格分隔的样式描述串」解析为 `Style` 对象，与 markup 标签内的样式串为同一套语法——`[bold red]` 内部的 `bold red` 即交给它解析。

```python
from rich.style import Style

s = Style.parse("bold red")
print("parse bold:", s.bold)    # 期望输出: parse bold: True
print("parse color:", s.color)  # 期望输出: parse color: Color('red', ColorType.STANDARD, number=1)
```

`Style` 内部以位掩码记录 13 个布尔属性（`bold=1`、`italic=4`、`underline=8` 等，F-R-019）；`parse` 将描述串映射到颜色与这些布尔位。因此 `s.bold` 为 `True`、`s.color` 为 `Color('red', ColorType.STANDARD, number=1)`。

## Style.from_color 直接构造

`Style.from_color(color=None, bgcolor=None)`（F-R-020）跳过解析，直接以 `Color` 值构造样式，适合颜色已程序化给定的场景。

```python
from rich.style import Style

s2 = Style.from_color(color="green", bgcolor="black")
print("from_color color:", s2.color, "bgcolor:", s2.bgcolor)
# 期望输出: from_color color: green bgcolor: black
```

这里 `color="green"`、`bgcolor="black"` 直接进入样式，无需经过 `parse` 的分词/映射步骤，是在知晓具体颜色时的首选构造方式。

## 讲解：一条链路的两种样式表达

- **字符串式**：`"[bold red] ... [/]"` → 由 `markup.render()`（F-R-011）拆分为 `Span` 区间，再映射到各区间上的 `Style`；
- **对象式**：`Style.parse`/`Style.from_color`（F-R-020）在代码中直接构造 `Style`，可复用于 `print(..., style=...)`、`Table`/`Panel` 的样式参数等。

二者共享同一套样式语法与位掩码存储（F-R-019），区别仅在于「声明在文本字面量里」还是「声明在代码对象里」。理解了这条等价关系，即可在「硬编码标签」与「动态构造样式」之间自由切换。

## 相关概念

- Console 与渲染协议（`print`/`markup`/`highlight` 默认值来源）：[/concepts/01-rich-console-and-protocol.md](/concepts/01-rich-console-and-protocol.md)
- Text 对象与标记语言（`markup.render` / `Span` 区间）：[/concepts/02-rich-text-and-markup.md](/concepts/02-rich-text-and-markup.md)
- Style 系统与位掩码存储：[/concepts/03-rich-style-system.md](/concepts/03-rich-style-system.md)
- 信源登记：[/references/rich.md](/references/rich.md)