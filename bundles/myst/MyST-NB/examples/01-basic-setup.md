---
type: Example
title: 基础 Sphinx + MyST-NB 配置
description: 从零开始配置 Sphinx + MyST-NB 的完整 conf.py 和项目结构示例
tags: [myst-nb, sphinx, setup, conf.py, quickstart]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 基础 Sphinx + MyST-NB 配置

本示例展示一个完整的 Sphinx + MyST-NB 最小可用配置。

## 项目结构

```
my-notebook-docs/
├── conf.py
├── index.md
├── notebooks/
│   ├── intro.ipynb
│   └── analysis.md
└── _static/
    └── custom.css
```

## conf.py 完整配置

```python
# conf.py

# -- 项目信息 -----------------------------------------------------
project = "我的 Notebook 文档"
author = "作者名"
copyright = "2024, 作者名"
release = "1.0.0"

# -- 扩展配置 -----------------------------------------------------
extensions = [
    "myst_nb",
]

# -- MyST 配置（由 myst-parser 提供，myst_nb 自动加载）-------------
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "colon_fence",
    "deflist",
    "html_image",
    "linkify",
    "smartquotes",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3

# -- MyST-NB 执行配置 ---------------------------------------------
# 执行模式：auto（默认，有缺失输出时执行）
nb_execution_mode = "auto"

# 单 cell 超时（秒）
nb_execution_timeout = 60

# 执行时是否允许错误
nb_execution_allow_errors = False

# 临时目录执行（避免污染源码目录）
nb_execution_in_temp = True

# 排除不执行的 notebook
nb_execution_excludepatterns = [
    "notebooks/drafts/*",
    "notebooks/long_running_*.ipynb",
]

# -- MyST-NB 渲染配置 ---------------------------------------------
# 代码输出渲染
nb_merge_streams = True              # 合并 stdout/stderr 流
nb_output_stderr = "show"            # show/remove/remove-warn/warn/error/severe
nb_number_source_lines = False       # 是否显示代码行号

# stderr 的 Pygments lexer
nb_render_error_lexer = "ipythontb"
# 普通文本输出的 Pygments lexer
nb_render_text_lexer = "myst-ansi"

# Markdown 输出渲染格式
nb_render_markdown_format = "commonmark"

# -- 源文件配置 ---------------------------------------------------
source_suffix = {
    ".rst": "restructuredtext",
    ".ipynb": "myst-nb",
    ".md": "myst-nb",
}

master_doc = "index"
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
]

# -- HTML 输出配置 ------------------------------------------------
html_theme = "sphinx_book_theme"  # 推荐使用 sphinx-book-theme
html_static_path = ["_static"]
```

## index.md

```markdown
# 我的 Notebook 文档

欢迎使用 MyST-NB 文档！

```{toctree}
:maxdepth: 2
:caption: 内容

notebooks/intro
notebooks/analysis
```
```

## 文本格式 Notebook 示例（notebooks/analysis.md）

````markdown
---
file_format: mystnb
kernelspec:
  name: python3
---

# 数据分析

本 notebook 展示基本的数据分析流程。

## 数据加载

```{code-cell}
import numpy as np
import pandas as pd

# 创建示例数据
data = pd.DataFrame({
    "x": np.arange(10),
    "y": np.random.randn(10).cumsum()
})
data.head()
```

## 数据统计

```{code-cell}
:tags: [hide-input]

print(f"数据共 {len(data)} 行")
print(f"y 均值: {data['y'].mean():.3f}")
print(f"y 标准差: {data['y'].std():.3f}")
```

## 可视化

```{code-cell}
---
mystnb:
  figure:
    caption: "随机游走图"
    name: fig-random-walk
---
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(data['x'], data['y'])
ax.set_xlabel("x")
ax.set_ylabel("y")
plt.show()
```

图 {ref}`fig-random-walk` 展示了随机游走的结果。
````

## 构建命令

```bash
# 安装依赖
pip install myst-nb sphinx-book-theme ipykernel

# 构建 HTML
sphinx-build -b html . _build/html

# 使用 cache 模式加速构建
nb_execution_mode=cache sphinx-build -b html . _build/html

# 自动重建（sphinx-autobuild）
pip install sphinx-autobuild
sphinx-autobuild . _build/html
```

## 推荐主题

MyST-NB 文档推荐配合以下主题使用：

| 主题 | 说明 |
|------|------|
| `sphinx-book-theme` | Jupyter Book 主题，Notebook 支持最佳 |
| `pydata-sphinx-theme` | PyData 风格，美观现代 |
| `alabaster` | Sphinx 默认主题，轻量 |
| `furo` | 干净现代的 Sphinx 主题 |

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [Sphinx 集成机制](/concepts/10-sphinx-integration.md)
- [配置系统](/concepts/04-config-system.md)
- [MyST Notebook 文件格式](/concepts/02-notebook-format.md)
