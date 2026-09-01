---
type: Concept
title: Markdown：MarkdownIt 令牌到元素类的映射
description: Rich 用 MarkdownIt 解析 Markdown 为令牌流，再按令牌类型映射到 MarkdownElement 元素类与样式上下文，实现控制台渲染；令牌树经 _flatten_tokens 展开逐令牌派发。
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
# Markdown：MarkdownIt 令牌到元素类的映射

## 概述

本概念文档介绍 Rich 的 Markdown 渲染管线：**MarkdownIt** 先把 Markdown 文本解析成令牌（token）树，Rich 再通过**上下文栈（MarkdownContext）** 与**令牌类型→元素类映射表（Markdown.elements）** 把令牌逐个派发到不同的 `MarkdownElement` 子类上，最终渲染为控制台段落。渲染本质是「令牌流 + 样式栈 + 元素对象栈」的三者协同，而元素在栈内通过 on_enter/on_text/on_leave 生命周期驱动。

> 事实范围：F-R-057..062（markdown.py）。

## MarkdownIt 解析深度

`class Markdown(JupyterMixin)` 构造签名（F-R-061）：

```python
Markdown(
    markup: str,
    code_theme: str = "monokai",
    justify=None,
    style="none",
    hyperlinks=True,
    inline_code_lexer=None,
    inline_code_theme=None,
)
```

解析在构造时完成：`parser = MarkdownIt().enable("strikethrough").enable("table")`，随后 `self.parsed = parser.parse(markup)`（F-R-061）。要点：

- **「parser builder」链式启用**：默认 MarkdownIt 实例不开启删除线与表格，Rich 通过 `.enable("strikethrough")`、`.enable("table")` 两个扩展开关补齐这两类语法；
- `inline_code_theme` 缺省回落 `code_theme`，二者之一决定行内代码高亮主题；
- MarkdownIt 产出的是递归的令牌树，`:inline` 令牌内部携带 `children`（行内展开后的字令牌）。

### 令牌扁平化（_flatten_tokens）

`Markdown._flatten_tokens(tokens) -> Iterable[Token]`（F-R-062）把递归令牌树拍平成线性流（F-R-069 邻域的渲染入口）：

```python
for token in tokens:
    is_fence = token.type == "fence"
    is_image = token.tag == "img"
    if token.children and not (is_image or is_fence):
        yield from self._flatten_tokens(token.children)
    else:
        yield token
```

- 含 `children` 的 inline/块级令牌逐层递归展开；
- `fence`（代码围栏）与 `img` 令牌除外——它们的 `children` 不参与扁平化，保留为独立令牌下发。

### 行内令牌在渲染中的占比

`__rich_console__` 中 `inline_style_tags = self.inlines = {"em", "strong", "code", "s"}`（F-R-062）。遍历令牌时按 `token.nesting` 区分开/闭/自闭合（`entering = nesting == 1`、`exiting == -1`、`self_closing == 0`），对行内令牌：开令牌 `enter_style`、闭令牌 `pop` 回退栈、自闭合（如 `code_inline`）直接应用；`html_inline` 中 `<kbd>`/`</kbd>` 映射到 `markdown.kbd` 样式；`link_open`/`link_close` 依 `self.hyperlinks` 决定是压入 `Link` 元素还是直接应用链接样式。行内文本的样式密度由此决定——每枚行内令牌都对应一次样式进出栈操作。

## MarkdownElement 元素基类

`class MarkdownElement`（F-R-057）：

- 类变量 `new_line: ClassVar[bool] = True`；
- `create(cls, markdown, token)`（classmethod）：工厂，返回 `cls()`；
- `on_enter(context)`、`on_text(context, text)`、`on_leave(context)`：生命周期钩子；
- `on_child_close(context, child) -> bool`：子元素关闭回调，默认返回 `True`；
- `__rich_console__(console, options)`：默认返回 `()`（空渲染）。

### 元素类继承关系

`MarkdownElement` 派生树（F-R-058）：

- `UnknownElement(MarkdownElement)`——未知类型兜底；
- `TextElement(MarkdownElement)`（`style_name = "none"`）——文本基类；
  - `Paragraph(TextElement)`（`style_name = "markdown.paragraph"`）；
  - `Heading(TextElement)`；`CodeBlock(TextElement)`；`BlockQuote(TextElement)`；
  - `ListItem(TextElement)`；`Link(TextElement)`；`ImageItem(TextElement)`；
- `HorizontalRule(MarkdownElement)`；
- `TableElement`/`TableHeaderElement`/`TableBodyElement`/`TableRowElement`/`TableDataElement`/`ListElement` 均直接继承 `MarkdownElement`。

### Heading 对齐与样式

`class HeadingFormat`（`@dataclass`）：字段 `justify: JustifyMethod = "left"`、`style: str = ""`（F-R-059）。`Heading` 类变量 `LEVEL_ALIGN: ClassVar[dict[str, JustifyMethod]]` 将 `h1` 映射到 `"center"`，`h2`-`h6` 映射到 `"left"`——即一级标题居中、其余左对齐。

## 令牌到元素类的映射表

`Markdown.elements: ClassVar[dict[str, type[MarkdownElement]]]` 共 16 个键（F-R-062），是「令牌类型 → 元素类」的静态查找表：

| 令牌类型 | 元素类 |
|---|---|
| `paragraph_open` | `Paragraph` |
| `heading_open` | `Heading` |
| `fence` | `CodeBlock` |
| `code_block` | `CodeBlock` |
| `blockquote_open` | `BlockQuote` |
| `hr` | `HorizontalRule` |
| `bullet_list_open` `/` `ordered_list_open` | `ListElement` |
| `list_item_open` | `ListItem` |
| `image` | `ImageItem` |
| `table_open` | `TableElement` |
| `tbody_open` | `TableBodyElement` |
| `thead_open` | `TableHeaderElement` |
| `tr_open` | `TableRowElement` |
| `td_open` `/` `th_open` | `TableDataElement` |

## MarkdownContext 渲染上下文

`class MarkdownContext`（F-R-060）构造：`__init__(self, console, options, style, inline_code_lexer=None, inline_code_theme="monokai")`，持有：

- `style_stack: StyleStack` 与 `stack: Stack[MarkdownElement]` 两个栈；
- `on_text(text, node_type)`：当 `node_type` 为 `fence`/`code_inline` 且 `_syntax`（由 `inline_code_lexer` 构建的 `Syntax("", lexer, theme=...)`）非空时，经 `Syntax.highlight` 做语法高亮（F-R-060 源码：`self._syntax = Syntax("", inline_code_lexer, theme=inline_code_theme)`，`inline_code_lexer` 为空则该字段为 `None`）；
- `enter_style(style_name)` / `leave_style()`：进出样式栈；
- 属性 `current_style`。

## 渲染驱动（__rich_console__）

`Markdown.__rich_console__(console, options)`（F-R-061/F-R-062）：先取样式 `style = console.get_style(self.style, default="none")`、`options.update(height=None)`，构建 `MarkdownContext`；随后对 `_flatten_tokens(self.parsed)` 的结果逐令牌派发：普通文本走 `context.on_text`，结构性令牌根据 `token.type` 查 `elements` 表创建/压栈对应元素，行内令牌则直接操作 `style_stack`。元素对象栈让每个 block 元素在离开时回写其排版属性，实现「令牌流 → 元素 → 控制台段」的完整链。

## 相关概念

- 元素对象栈与 StyleStack 的进出栈语义复用：[/concepts/03-rich-style-system.md](03-rich-style-system.md)
- 代码块与行内代码的高亮依托高亮器体系：[/concepts/04-rich-highlighters.md](04-rich-highlighters.md)
- Console 如何消费 `__rich_console__` 渲染结果：[/concepts/01-rich-console-and-protocol.md](01-rich-console-and-protocol.md)
- 信源登记：[/references/rich.md](/references/rich.md)