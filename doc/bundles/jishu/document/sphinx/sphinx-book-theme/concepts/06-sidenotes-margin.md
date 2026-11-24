---
type: Concept
title: "边注、margin 与全宽内容：文档树层面的排版"
description: "sphinx-book-theme 如何用 post-transform 把脚注搬到引用点、SideNoteNode 生成桌面/移动双形态 HTML、{margin} 指令与 margin/full-width CSS 类的适用边界"
tags: [sphinx, theme, sidenote, marginnote, tufte, doctree, transform]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-transforms
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/_transforms.py
    title: HandleFootnoteTransform
  - id: sbt-nodes
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/nodes.py
    title: SideNoteNode
  - id: sbt-directives
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/directives.py
    title: Margin directive
---

# 边注、margin 与全宽内容：文档树层面的排版

## 三种"出边"方式

| 方式 | 语法 | 是否编号 | 内容形态 | 适用 |
|------|------|---------|---------|------|
| 边注（sidenote） | 普通脚注 `[^id]` + `use_sidenotes: True` | 是 | 行内内容 | 补充说明、术语解释 |
| margin note | 脚注内容以 `{-}` 开头 | 否 | 行内内容 | 旁注、提示 |
| `{margin}` 块 | 指令 | 可带标题 | 块级内容 | 代码、图片、提示框、表格 |
| 全宽内容 | `:class: full-width` | — | 块级内容 | 大图、宽表、长公式 |

核心区别：**边注/margin note 是行内内容**，不能放代码块、列表、嵌套提示框；需要块级内容时用 `{margin}`。

## 开关

```python
html_theme_options = {
    "use_sidenotes": True,
}
```

默认关闭。关闭时脚注仍是普通页脚注释；开启后，**所有脚注**都会被转成边注或 margin note。

## 脚注如何变成边注

实现是一个 Sphinx post-transform：`HandleFootnoteTransform`。

```python
class HandleFootnoteTransform(SphinxPostTransform):
    default_priority = 1
    formats = ("html",)

    def run(self, **kwargs):
        if theme_options.get("use_sidenotes", False) is False:
            return None
        ...
```

执行步骤：

1. 遍历文档中所有 `footnote_reference` 节点。
2. 找到 `backrefs[0]` 与该引用 `ids[0]` 匹配的 `footnote` 节点。
3. 取脚注的 `children[0]` 作为编号标签，`children[1].children` 作为正文内容。
4. 如果正文以 `{-}` 开头：去掉标记，加 `marginnote` class，节点名 `marginnote-role-<label>`。
5. 否则：生成 `<sup>` 编号，加 `sidenote` class，节点名 `sidenote-role-<label>`。
6. 用 `SideNoteNode` + 内容段落替换原引用。
7. 删除原脚注节点，避免页尾重复。

### 嵌套场景的处理

如果脚注引用位于提示框、表格等容器内，直接替换会破坏容器结构。变换会向上找到 `section` 或 `document` 级祖先，把内容段落插到容器**之前**，并在原引用处放入一份带 `d-n` class 的副本（窄屏展开用），保证桌面端边注与移动端展开都能工作。

这也是为什么"边注写在提示框里"有时看起来位置略有偏移——不是 CSS bug，而是文档树复制策略。

## SideNoteNode 生成的 HTML

`nodes.py` 定义了自定义节点与 HTML visitor。桌面端与移动端共用一套结构：

```html
<label for="sidenote-role-1" class="margin-toggle">
  <span class="sidenote">...</span>
</label>
<input type="checkbox" id="sidenote-role-1" class="margin-toggle">
```

要点：

- `<label for>` + `<input type="checkbox">` 实现"点击编号展开/收起"，不依赖 JavaScript。
- `marginnote` 的 label 额外带 `marginnote-label` class。
- 编号本身是 `<sup>`，所以视觉上仍像脚注上标。
- 窄屏下 CSS 默认隐藏边注内容，点击后显示。

## `{margin}` 指令

`directives.py` 的实现非常短：

```python
class Margin(Sidebar):
    optional_arguments = 1
    required_arguments = 0

    def run(self):
        if not self.arguments:
            self.arguments = [""]
        nodes = super().run()
        nodes[0].attributes["classes"].append("margin")
        if not self.arguments:
            nodes[0].children.pop(0)
        return nodes
```

它继承 docutils 的 `Sidebar`，因此：

- 支持一个可选标题参数。
- 支持块级内容。
- 通过追加 `margin` class，由 SCSS 把整个块移到右侧留白。

用法（MyST）：

````md
```{margin} **旁注标题**
这里可以放代码、图片、提示框。
```
````

无标题：

````md
```{margin}
没有标题的 margin 块。
```
````

> 源码细节：`Margin.run` 在无参数时先把 `self.arguments` 设为 `[""]`，随后删除空标题的分支因条件为假而不可达。无标题用法仍可用，但可能保留一个空标题节点；介意时给一个标题参数。

### 重要限制

`{margin}` 与 `{sidebar}` **不要嵌套在 topic、admonition 等容器内**。docutils 的 Sidebar 在这些容器中的定位行为不稳定，容易出现重叠或错位。需要"提示框里的旁注"时，改用行内边注。

## 给任意元素加 margin class

不限于 `{margin}` 指令，任何支持 `:class:` 的指令都可以：

````md
:::{note}
:class: margin
这个提示框会出现在右侧留白。
:::
````

````md
```{figure} image.png
---
figclass: margin
---
整张图放进右侧留白。
```
````

````md
```{figure} image.png
---
figclass: margin-caption
---
图片在正文，图注在右侧留白。
```
````

| class | 效果 |
|-------|------|
| `margin` | 整个元素移到右侧留白 |
| `margin-caption` | 元素留在正文，caption 移到右侧 |
| `full-width` | 元素向右扩展，占据右侧留白 |

`full-width` 可用于提示框、代码块、公式、表格：

````md
```{note}
:class: full-width
这是一条全宽提示。
```
````

````md
```{math}
:class: full-width
...
```
````

## Notebook 中的等价写法

MyST-NB 用单元格标签实现同样效果：

| 标签 | 效果 |
|------|------|
| `margin` | 单元格（含输出）放入右侧留白 |
| `full_width` / `full-width` | 单元格全宽 |
| `remove_cell` | 删除整个单元格 |
| `remove_input` / `hide_input` | 隐藏代码，保留输出 |
| `hide-cell` | 隐藏代码与输出 |
| `output_scroll` | 输出区可滚动 |
| `scroll-input` | 输入区可滚动 |

Markdown 单元格用 `+++ {"tags": ["margin"]}` 也能触发 margin 布局。

## 移动端行为

| 元素 | 窄屏 |
|------|------|
| sidenote | 编号可点，点击展开内容 |
| marginnote | 显示符号，点击展开 |
| `{margin}` 块 | 回到正文流，位于引用位置附近 |
| `margin-caption` | caption 回到图片下方 |
| `full-width` | 回到普通宽度 |

因此不要用 margin 承载"不读也不影响理解"的关键内容；它在窄屏会变成正文的一部分。

## 设计建议

- 边注用于**补充**，不用于主线论证。主线必须在正文里读得通。
- 一个段落不要放超过 2 个边注，否则右侧会拥挤。
- 代码块、表格、图片一律用 `{margin}`，不要塞进脚注。
- 全宽内容适合"需要更大画布"的图，不适合普通段落。
- 打印时边注会回到正文流；检查打印样式是否可读。

## 相关概念

- [Notebook 与在线交互](07-jupyter-interactivity.md)
- [边注、margin 与全宽内容示例](../examples/03-margin-notes-and-custom-css.md)
- [定制、子主题与主题开发](08-customization-and-development.md)
