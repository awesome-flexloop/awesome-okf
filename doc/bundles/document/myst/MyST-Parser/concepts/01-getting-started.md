---
type: Concept
title: 快速开始
description: 安装 MyST-Parser、配置 Sphinx conf.py、编写第一个 MyST Markdown 文档
tags: [myst, sphinx, getting-started, setup, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 快速开始

### 安装

使用 pip 安装 MyST-Parser：

```bash
pip install myst-parser
```

如需 linkify 自动链接功能，安装可选依赖：

```bash
pip install "myst-parser[linkify]"
```

### 最小 Sphinx 配置

在 Sphinx 项目的 `conf.py` 中添加 `myst_parser` 到扩展列表：

```python
# conf.py
extensions = [
    "myst_parser",
]

# 可选：启用常用扩展语法
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "fieldlist",
    "html_image",
    "colon_fence",
    "smartquotes",
    "replacements",
    "substitution",
    "tasklist",
    "linkify",
]

# 可选：自动生成标题锚点（深度到3级标题）
myst_heading_anchors = 3
```

### 创建第一个 MyST 文档

在 Sphinx 源目录创建 `index.md`：

```markdown
# 我的项目文档

欢迎使用 MyST Markdown！

## 功能示例

这是**粗体**和*斜体*文本。

### 代码块

```python
def hello():
    print("Hello, MyST!")
```

### 数学公式

行内公式：$E=mc^2$

块级公式：
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$

### 指令

:::{note}
这是一个提示块，使用 colon_fence 语法。
:::

### 交叉引用

参见 [配置章节](/concepts/04-config-system.md)。
```

### 构建文档

```bash
sphinx-build -b html . _build/html
```

或使用 Sphinx 的快速启动工具初始化项目：

```bash
sphinx-quickstart
# 然后编辑 conf.py 添加 myst_parser
```

### 在 RST 文档中包含 Markdown

在 RST 文件中使用 `.. include::` 指令引入 Markdown 文件：

```rst
.. include:: path/to/file.md
   :parser: myst_parser.sphinx_
```

### 文件级配置

每个 Markdown 文件可以通过 frontmatter 覆盖全局配置：

```markdown
---
myst:
  enable_extensions: ["dollarmath"]
  substitutions:
    version: "1.0.0"
---

# 本文档使用 {{version}} 版本
```

### 验证安装

构建后检查 HTML 输出，确认：
- Markdown 标题正确渲染为 HTML 标题层级
- 代码块有语法高亮
- 数学公式通过 MathJax 渲染
- `:::{note}` 等指令正确渲染为提示块

## 相关概念

- [MyST-Parser 简介](/concepts/00-introduction.md)
- [MyST 语法概览](/concepts/02-myst-syntax-overview.md)
- [配置系统](/concepts/04-config-system.md)
- [基础配置示例](/examples/01-basic-setup.md)
