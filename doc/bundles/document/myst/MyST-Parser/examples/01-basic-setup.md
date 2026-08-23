---
type: Example
title: 基础 Sphinx 配置
description: 从零开始配置 Sphinx + MyST-Parser 的完整 conf.py 示例
tags: [myst, sphinx, setup, conf.py, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 基础 Sphinx 配置

本示例展示一个完整的 Sphinx + MyST-Parser 最小可用配置。

## 项目结构

```
my-docs/
├── conf.py
├── index.md
├── getting-started.md
├── api.md
└── _static/
    └── custom.css
```

## conf.py 完整配置

```python
# conf.py

# -- 项目信息 -----------------------------------------------------
project = "我的项目文档"
author = "作者名"
copyright = "2024, 作者名"
release = "1.0.0"

# -- 扩展配置 -----------------------------------------------------
extensions = [
    "myst_parser",
]

# -- MyST 配置 ----------------------------------------------------
# 启用常用扩展语法
myst_enable_extensions = [
    "dollarmath",       # $...$ 数学公式
    "amsmath",          # AMS 数学环境
    "colon_fence",      # ::: 围栏指令（支持嵌套）
    "deflist",          # 定义列表
    "fieldlist",        # 字段列表
    "html_image",       # HTML <img> 标签
    "linkify",          # 自动链接识别
    "replacements",     # 文本替换（(c)→©）
    "smartquotes",      # 智能引号
    "strikethrough",    # ~~删除线~~
    "substitution",     # {{key}} 变量替换
    "tasklist",         # - [ ] 任务列表
]

# 自动标题锚点（深度到 H3）
myst_heading_anchors = 3

# 使用 GitHub 风格 slug
myst_heading_slug_func = "github"

# 替换变量
myst_substitutions = {
    "project_name": "我的项目",
    "version": "1.0.0",
}

# HTML meta 标签
myst_html_meta = {
    "description lang=en": "My project documentation",
    "keywords": "myst, sphinx, documentation",
}

# -- 源文件配置 ---------------------------------------------------
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- HTML 输出配置 ------------------------------------------------
html_theme = "alabaster"
html_static_path = ["_static"]
```

## index.md

```markdown
# 我的项目文档

欢迎使用 {{project_name}} 文档！

## 目录

```{toctree}
:maxdepth: 2

getting-started
api
```
```

## getting-started.md

```markdown
# 快速开始

## 安装

```bash
pip install my-project
```

## 使用方法

:::{note}
确保已安装 Python 3.11 或更高版本。
:::

```python
import my_project

my_project.run()
```

## 待办事项

- [x] 完成核心功能
- [ ] 添加测试
- [ ] 编写更多文档

## 数学公式

质能方程：$E = mc^2$

$$
\int_0^1 x^2 dx = \frac{1}{3}
$$
```

## 构建命令

```bash
# 安装依赖
pip install myst-parser sphinx

# 构建 HTML
sphinx-build -b html . _build/html

# 自动重建（需要 sphinx-autobuild）
pip install sphinx-autobuild
sphinx-autobuild . _build/html
```

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [Sphinx 集成机制](/concepts/11-sphinx-integration.md)
- [配置系统](/concepts/04-config-system.md)
