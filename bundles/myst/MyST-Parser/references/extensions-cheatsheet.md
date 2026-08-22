---
type: Reference
title: MyST 扩展语法速查
description: MyST-Parser 支持的 18 个扩展语法的语法格式、配置项和使用示例速查表
tags: [myst, sphinx, syntax, extensions, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-repo
    resource: https://myst-parser.readthedocs.io
    title: MyST-Parser Documentation
---

# MyST 扩展语法速查

本文档列出 `myst_enable_extensions` 可启用的所有扩展语法及其格式。

## 数学公式类

### dollarmath（美元符数学）

启用行内 `$...$` 和块级 `$$...$$` 数学公式。

```markdown
行内公式：$E=mc^2$

块级公式：
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$ (label)
```

相关配置：
- `myst_dmath_allow_labels`（默认 True）：允许 `$$...$$ (label)` 标签语法
- `myst_dmath_allow_space`（默认 True）：允许 `$ ... $` 首尾空格
- `myst_dmath_allow_digits`（默认 True）：允许 `1$ ...$2` 首尾数字
- `myst_dmath_double_inline`（默认 False）：允许行内 `$$...$$`

### amsmath（AMS 数学环境）

支持 LaTeX AMS 数学环境：

```markdown
$$
\begin{align}
a &= b + c \\
  &= d + e
\end{align}
$$
```

## 块级语法类

### colon_fence（冒号围栏）

使用 `:::` 代替反引号创建围栏，用于嵌套指令和代码块：

```markdown
:::{note}
这是一个提示块
:::

::::{important}
外层提示
:::{tip}
嵌套提示
:::
::::
```

相关配置：
- `myst_colon_fence_exact_match`（默认 False）：开闭冒号数必须精确匹配

### deflist（定义列表）

支持 Pandoc 风格的定义列表：

```markdown
术语 1
: 定义 1

术语 2
: 定义 2a
: 定义 2b
```

### fieldlist（字段列表）

支持 RST 风格的字段列表（用于文档元数据、指令选项等）：

```markdown
:term1: value1
:term2: value2
```

### tasklist（任务列表）

支持 GitHub 风格任务列表：

```markdown
- [x] 已完成任务
- [ ] 未完成任务
```

相关配置：
- `myst_enable_checkboxes`（默认 False）：复选框可在 HTML 中编辑

### alert（警告块）

支持 GitHub 风格 alert 块：

```markdown
> [!NOTE]
> 这是一个提示

> [!WARNING]
> 这是一个警告
```

## 行内语法类

### substitution（变量替换）

在文中插入预定义的替换变量：

```markdown
---
myst:
  substitutions:
    project: "MyST-Parser"
---

欢迎使用 {{project}}！
```

相关配置：
- `myst_substitutions`：替换变量字典
- `myst_sub_delimiters`（默认 `("{", "}")`）：替换定界符

### smartquotes（智能引号）

自动将直引号转换为弯引号：`"text"` → "text"，`'text'` → 'text'。

### replacements（文本替换）

自动替换文本符号：`(c)` → ©、`(tm)` → ™、`---` → — 等。

### strikethrough（删除线）

支持 `~~删除线~~` 语法。

相关配置：
- `myst_strikethrough_single_tilde`（默认 False）：允许单个 `~text~` 作为删除线

### linkify（自动链接）

自动识别文本中的 URL 并转为链接（需安装 `linkify-it-py`）。

相关配置：
- `myst_linkify_fuzzy_links`（默认 True）：识别无 scheme 前缀的 URL

### attrs_inline（行内属性）

为行内元素添加 CSS 类、ID 等属性：

```markdown
``[带类链接](url)``{.my-class #my-id}
`代码`{.custom}
```

### attrs_block（块级属性）

为块级元素添加属性：

```markdown
{.my-class #my-id}
# 带属性的标题
```

### html_image（HTML 图片）

支持 `<img>` HTML 标签。

### html_admonition（HTML 提示块）

支持 HTML `<div class="admonition">` 等提示块语法。

### gfm_autolink（GFM 自动链接）

支持 GFM 风格的自动链接（`<http://example.com>`）。

## 相关概念

- [MyST 语法概览](/concepts/02-myst-syntax-overview.md)
- [扩展语法系统](/concepts/05-extension-system.md)
- [配置系统](/concepts/04-config-system.md)
