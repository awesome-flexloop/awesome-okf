---
okf_version: "0.2"
type: reference
title: "Pygments样式定义源码（style.py）"
description: "jupyterlab_pygments/style.py 中 JupyterStyle 类的完整API、token映射与CSS变量体系"
tags: [pygments, style, syntax-highlighting, css-variables, jupyterlab-theme, token-mapping]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: style-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/jupyterlab_pygments/style.py"
    title: "jupyterlab_pygments/style.py"
---

# Pygments样式定义源码（style.py）

本信源登记 `jupyterlab_pygments/style.py`（共133行）的核心类与样式映射。style.py 是整个包的核心模块，定义了 `JupyterStyle` 类——一个使用 JupyterLab CSS 变量的 Pygments 语法高亮样式。

## 模块导入

```python
from pygments.style import Style
from pygments.token import (
    Comment, Error, Generic, Keyword, Literal, Name, Number, Operator, Other,
    Punctuation, String, Text, Whitespace)
```

导入 `pygments.style.Style` 作为基类，以及 `pygments.token` 中的各类 token 类型用于样式映射。

## JupyterStyle 类

### 类定义

```python
class JupyterStyle(Style):
```

继承自 `pygments.style.Style`，是 Pygments 的样式类。

### 类属性

| 属性 | 值 | 说明 |
|------|-----|------|
| `default_style` | `''` | 默认样式为空字符串 |
| `background_color` | `'var(--jp-cell-editor-background)'` | 编辑器背景色，使用 JupyterLab CSS 变量 |
| `highlight_color` | `'var(--jp-cell-editor-active-background)'` | 高亮行背景色，使用 JupyterLab CSS 变量 |
| `styles` | 字典（见下方） | Token 类型到 CSS 样式的映射表 |

### styles 字典完整映射

Token 类型按 Pygments 分类组织，注释中标注了对应的 CSS class 名：

**基础文本类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `Text` | `'var(--jp-mirror-editor-variable-color)'` | 无 class |
| `Whitespace` | `''` | `w` |
| `Error` | `'var(--jp-mirror-editor-error-color)'` | `err` |
| `Other` | `''` | `x` |

**注释类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `Comment` | `'italic var(--jp-mirror-editor-comment-color)'` | `c` |

注释子类（Comment.Multiline, Comment.Preproc, Comment.Single, Comment.Special）均被注释掉，值为空。

**关键字类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `Keyword` | `'bold var(--jp-mirror-editor-keyword-color)'` | `k` |

关键字子类（Keyword.Constant, Keyword.Declaration, Keyword.Namespace, Keyword.Pseudo, Keyword.Reserved, Keyword.Type）均被注释掉。

**操作符类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `Operator` | `'bold var(--jp-mirror-editor-operator-color)'` | `o` |
| `Operator.Word` | `''` | `ow` |

**字面量类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `Literal` | `''` | `l` |
| `Literal.Date` | `''` | `ld` |

**字符串类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `String` | `'var(--jp-mirror-editor-string-color)'` | 未标注 |

字符串子类（String.Backtick, String.Char, String.Doc, String.Double, String.Escape, String.Heredoc, String.Interpol, String.Other, String.Regex, String.Single, String.Symbol）均被注释掉。

**数字类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `Number` | `'var(--jp-mirror-editor-number-color)'` | `m` |

数字子类（Number.Float, Number.Hex, Number.Integer, Number.Integer.Long, Number.Oct）均被注释掉。

**名称类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `Name` | `''` | `n` |

名称子类（Name.Attribute, Name.Builtin, Name.Builtin.Pseudo, Name.Class, Name.Constant, Name.Decorator, Name.Entity, Name.Exception, Name.Function, Name.Property, Name.Label, Name.Namespace, Name.Other, Name.Tag, Name.Variable, Name.Variable.Class, Name.Variable.Global, Name.Variable.Instance）均被注释掉。

**通用标记类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `Generic` | `''` | `g` |

Generic 子类（Generic.Deleted, Generic.Emph, Generic.Error, Generic.Heading, Generic.Inserted, Generic.Output, Generic.Prompt, Generic.Strong, Generic.Subheading, Generic.Traceback）均被注释掉。

**标点类：**

| Token | CSS 值 | CSS Class |
|-------|--------|-----------|
| `Punctuation` | `'var(--jp-mirror-editor-punctuation-color)'` | `p` |

## CSS 变量完整列表

JupyterStyle 类文档中列出了 22 个 `--jp-mirror-editor-*` CSS 变量（来自 `@jupyterlab/codemirror` 包），加上实际使用的 2 个 cell 背景变量：

**编辑器背景：**
- `--jp-cell-editor-background` — 单元格编辑器背景色
- `--jp-cell-editor-active-background` — 活动单元格编辑器背景色

**语法高亮（mirror-editor）：**
- `--jp-mirror-editor-keyword-color` — 关键字颜色
- `--jp-mirror-editor-atom-color` — 原子值颜色
- `--jp-mirror-editor-number-color` — 数字颜色
- `--jp-mirror-editor-def-color` — 定义（函数/类名）颜色
- `--jp-mirror-editor-variable-color` — 变量颜色
- `--jp-mirror-editor-variable-2-color` — 变量2颜色
- `--jp-mirror-editor-variable-3-color` — 变量3颜色
- `--jp-mirror-editor-punctuation-color` — 标点颜色
- `--jp-mirror-editor-property-color` — 属性颜色
- `--jp-mirror-editor-operator-color` — 操作符颜色
- `--jp-mirror-editor-comment-color` — 注释颜色
- `--jp-mirror-editor-string-color` — 字符串颜色
- `--jp-mirror-editor-string-2-color` — 字符串2颜色
- `--jp-mirror-editor-meta-color` — 元信息颜色
- `--jp-mirror-editor-qualifier-color` — 限定符颜色
- `--jp-mirror-editor-builtin-color` — 内置名称颜色
- `--jp-mirror-editor-bracket-color` — 括号颜色
- `--jp-mirror-editor-tag-color` — 标签颜色
- `--jp-mirror-editor-attribute-color` — 属性颜色
- `--jp-mirror-editor-header-color` — 标题颜色
- `--jp-mirror-editor-quote-color` — 引号颜色
- `--jp-mirror-editor-link-color` — 链接颜色
- `--jp-mirror-editor-error-color` — 错误颜色

## 已知限制（文档记录）

JupyterStyle 类文档中明确记录了两个 Pygments 与 CodeMirror 的 token 分类差异：

1. **点号（`.`）分类差异**：在 Pygments 中，`foo.bar` 中的点号被归类为 `Operator`（CSS class: `o`），而在 CodeMirror 中是普通文本
2. **属性名分类差异**：在 Pygments 中，`from foo import bar` 和 `foo.bar` 中的 `bar` 都被归类为 `Name`（CSS class: `n`），而在 CodeMirror 中后者应被识别为属性（property）
