---
type: Concept
title: 扩展语法系统
description: MyST 的 18 个可选扩展语法详解——启用方式、语法格式、配置项
tags: [myst, sphinx, extensions, syntax, dollarmath, colon-fence, myst-parser]
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

## 扩展语法系统

MyST 的扩展语法通过 `myst_enable_extensions` 配置按需启用。默认模式下 MyST 仅支持 CommonMark + GFM 表格 + 脚注 + frontmatter + MyST 指令/角色，其他高级语法需显式启用。

## 启用扩展

### 全局启用

```python
# conf.py
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
    "linkify",
    "substitution",
    "smartquotes",
    "replacements",
]
```

### 文件级启用

```markdown
---
myst:
  enable_extensions: ["dollarmath", "tasklist"]
---
```

## 扩展详解

### dollarmath — 美元符数学公式

支持 LaTeX 风格的 `$...$`（行内）和 `$$...$$`（块级）数学公式。

```markdown
行内：质能方程 $E = mc^2$

块级：
$$
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$ (quadratic)
```

配置项：
- `myst_dmath_allow_labels`（默认 True）：允许 `$$...$$ (label)` 标签
- `myst_dmath_allow_space`（默认 True）：允许 `$ x $` 首尾空格
- `myst_dmath_allow_digits`（默认 True）：允许 `1$x$2` 首尾数字
- `myst_dmath_double_inline`（默认 False）：允许行内 `$$x$$`
- `myst_update_mathjax`（默认 True）：自动配置 MathJax 跳过 `$` 定界符

### amsmath — AMS 数学环境

支持 LaTeX AMS 数学环境（align、gather、multline 等）：

```markdown
$$
\begin{align}
a &= b + c \\
  &= d + e + f
\end{align}
$$
```

需同时启用 `dollarmath`。

### colon_fence — 冒号围栏

使用 `:::` 代替反引号创建围栏，解决嵌套围栏中反引号冲突问题：

```markdown
:::{note} 提示内容
普通文本

```python
# 嵌套代码块
print("hello")
```
:::
```

配置项：
- `myst_colon_fence_exact_match`（默认 False）：开闭冒号数必须完全相同

### deflist — 定义列表

支持 Pandoc 风格定义列表：

```markdown
术语 1
: 这是术语 1 的定义

术语 2
: 定义行 1
: 定义行 2
```

### fieldlist — 字段列表

支持 RST 风格字段列表（常用于文档元数据和指令选项）：

```markdown
:作者: 张三
:版本: 1.0
:日期: 2024-01-01
```

### tasklist — 任务列表

支持 GitHub 风格任务列表复选框：

```markdown
- [x] 已完成任务
- [ ] 未完成任务
- [ ] 另一个待办
```

配置项：
- `myst_enable_checkboxes`（默认 False）：HTML 输出中复选框可交互（可点击勾选）

### substitution — 变量替换

支持在文中插入预定义变量：

```markdown
---
myst:
  substitutions:
    version: "2.0"
    repo: "[MyST-Parser](https://github.com/executablebooks/MyST-Parser)"
---

当前版本：{{version}}

项目地址：{{repo}}
```

配置项：
- `myst_substitutions`：全局替换变量字典（全局 conf.py 中也可设置）
- `myst_sub_delimiters`（默认 `("{", "}")`）：替换定界符

### linkify — 自动链接

自动识别文本中的 URL 并转换为链接（需安装 `linkify-it-py`）：

```markdown
访问 https://example.com 获取更多信息。
```

配置项：
- `myst_linkify_fuzzy_links`（默认 True）：识别无前缀 URL（如 www.example.com）

### smartquotes — 智能引号

自动将直引号转换为排版引号：`"text"` → "text"，`'text'` → 'text'，`--` → –。

### replacements — 文本替换

自动替换文本符号：`(c)` → ©、`(tm)` → ™、`(r)` → ®、`...` → …、`---` → —。

### strikethrough — 删除线

支持 `~~删除线~~` 语法。

配置项：
- `myst_strikethrough_single_tilde`（默认 False）：允许单个 `~text~` 作为删除线

### attrs_inline / attrs_block — 属性语法

为行内/块级元素添加 CSS 类、ID 等属性：

```markdown
``[链接](url)``{.external #link1}

{.highlight}
> 这个引用块有 highlight 类
```

### html_image / html_admonition — HTML 元素

支持 HTML `<img>` 标签和 HTML 风格提示块。

### gfm_autolink — GFM 自动链接

支持 GFM 风格的 `<http://example.com>` 自动链接。

### alert — GitHub Alert

支持 GitHub 风格 alert 块：

```markdown
> [!NOTE]
> 有用信息

> [!WARNING]
> 关键警告
```

## 扩展依赖关系

```
dollarmath ← amsmath（amsmath 需要 dollarmath 的 $$ 围栏）
attrs_image（已弃用）→ attrs_inline（替代方案）
linkify → linkify-it-py（可选依赖，缺失时自动禁用并警告）
```

## 模式预设

- **commonmark_only**：仅 CommonMark 标准，不启用任何扩展
- **gfm_only**：GitHub Flavored Markdown（含 tasklist），不启用 MyST 特有扩展
- **默认模式**：CommonMark + table + footnote + frontmatter + MyST 指令/角色 + 按需扩展

## 相关概念

- [MyST 语法概览](02-myst-syntax-overview.md)
- [配置系统](04-config-system.md)
- [指令与角色](07-directives-and-roles.md)
- [数学公式与 MathJax](13-math-and-mathjax.md)
- [扩展语法速查](../references/extensions-cheatsheet.md)
