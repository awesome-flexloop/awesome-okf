---
type: Concept
title: MyST 语法概览
description: MyST Markdown 的核心语法特性——CommonMark 基础、指令、角色、交叉引用、扩展语法总览
tags: [myst, sphinx, syntax, markdown, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
  - id: extensions-cheatsheet
    resource: /references/extensions-cheatsheet.md
    title: MyST 扩展语法速查
---

## MyST 语法概览

MyST（Markedly Structured Text）是专为技术文档设计的 Markdown 方言，在 CommonMark 基础上增加了 RST 风格的指令（Directive）和角色（Role）机制，实现了 Markdown 简洁性与 RST 表达力的结合。

## CommonMark 基础语法

MyST 支持所有标准 CommonMark 语法：

| 语法 | 示例 |
|------|------|
| 标题 | `# H1`、`## H2`、`### H3` |
| 粗体/斜体 | `**粗体**`、`*斜体*` |
| 列表 | `-`/`*`/`1.` |
| 链接 | `[文本](URL)` |
| 图片 | `![alt](src)` |
| 代码块 | ` ```lang ... ``` ` |
| 行内代码 | `` `code` `` |
| 引用 | `> 引用文本` |
| 表格 | GFM 表格语法 |
| 水平线 | `---` |

## 指令（Directives）

指令是 MyST 的块级扩展机制，相当于 RST 的 `.. directive::`，用于插入提示块、图片、代码块输出等复杂元素。

### 反引号围栏语法

````markdown
```{directivename}  arguments
:key1: val1
:key2: val2

指令内容
```
````

### 冒号围栏语法（需启用 colon_fence 扩展）

```markdown
:::{directivename} arguments
:option: value

内容
:::
```

冒号围栏的优势是可以在代码块中嵌套指令（避免反引号冲突）：

````markdown
::::{note} 嵌套示例
```python
print("代码块中的代码")
```
:::{tip}
嵌套提示
:::
::::
````

### 常用内置指令

```markdown
```{note} 注意
这是一个注意提示。
```

```{warning} 警告
这是一个警告。
```

```{image} img/photo.png
:alt: 图片描述
:width: 300px
```

```{figure} img/diagram.png
:align: center

图注文字
```

```{code-block} python
:linenos:

print("带行号的代码块")
```

```{include} subfile.md
```
```

## 角色（Role）

角色是 MyST 的行内扩展机制，相当于 RST 的 `:role:`text``，用于在文本中插入特殊元素。

### 语法格式

```markdown
{role-name}`text`
```

### 常用角色

```markdown
{math}`E=mc^2`          — 行内数学
{py:func}`print`        — Python 函数交叉引用
{doc}`/other-page`      — 文档交叉引用
{ref}`my-label`         — 标签引用
{sub-ref}`key`          — 替换引用
```

## 交叉引用

### Markdown 风格引用

```markdown
``[显示文本](target.md)``           — 引用其他文档
``[显示文本](target.md#anchor)``     — 引用文档中的锚点
[显示文本](#anchor)             — 引用本文档内锚点
```

### 引用标签

```markdown
(my-label)=
## 我的标题

可以通过 [链接到此处](#my-label) 引用。
```

### 自动标题锚点

启用 `myst_heading_anchors = N` 后（N 为标题深度），标题自动生成 slug 锚点：

```markdown
## 我的标题 → #我的标题（自动锚点）
```

## YAML Frontmatter

每个文件开头可以包含 YAML 元数据：

```markdown
---
title: 文档标题
myst:
  enable_extensions: ["dollarmath"]
  substitutions:
    version: "1.0"
html_meta:
  description: "页面描述"
---
```

## 注释

```markdown
% 这是一行注释，不会出现在输出中

%
多行注释也可以，
用 % 开头加换行
```

## 相关概念

- [MyST-Parser 简介](/concepts/00-introduction.md)
- [扩展语法系统](/concepts/05-extension-system.md)
- [指令与角色](/concepts/07-directives-and-roles.md)
- [交叉引用](/concepts/08-cross-references.md)
- [YAML Frontmatter](/concepts/12-frontmatter.md)
