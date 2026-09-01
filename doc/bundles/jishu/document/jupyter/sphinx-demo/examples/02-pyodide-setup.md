---
type: Example
title: Pyodide 内核完整配置示例
description: 基于 sphinx-demo 的 Pyodide 内核完整站点配置，包含所有 JSON 配置文件、自定义内容、TryExamples 和样式定制
tags: [pyodide, configuration, complete-setup, example]
difficulty: intermediate
estimated_time: 20min
prerequisites:
  - Python 3.10+
  - 完成最小站点示例
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyodide-example
    resource: /references/conf-py-source.md
    title: pyodide-kernel-example 完整源码
---

## 目标

构建一个功能完整的 Pyodide 内核 JupyterLite Sphinx 站点，复刻 sphinx-demo 的 Pyodide 示例的所有功能：
- 自动 TryExamples 按钮
- 预装 Notebook 内容
- 自定义按钮样式
- 四层 JSON 配置
- JupyterLite/NotebookLite/REPL 指令演示

## 项目结构

```
pyodide-docs/
├── docs/
│   ├── Makefile
│   └── source/
│       ├── _static/
│       │   ├── button_styling.css
│       │   └── icon.svg
│       ├── conf.py
│       ├── custom_contents/
│       │   ├── arrays_in_numpy.ipynb
│       │   └── data/
│       ├── index.md
│       ├── example.py
│       ├── jupyter-lite.json
│       ├── jupyter_lite_config.json
│       ├── jupyterlite/
│       │   └── demo.md
│       ├── notebooklite/
│       │   └── demo.md
│       ├── replite/
│       │   └── demo.md
│       ├── try_examples.json
│       ├── try_examples.md
│       └── overrides.json
└── requirements.txt
```

## requirements.txt

```txt
sphinx>=7.0
jupyterlite-sphinx
jupyterlite-pyodide-kernel
pydata-sphinx-theme
myst-nb
numpydoc
sphinx-design
```

## conf.py 完整配置

```python
import os
import sys

# 使 autodoc 可以导入当前目录和 disabled_examples 目录的模块
sys.path.insert(0, os.path.abspath("."))

project = "jupyterlite-sphinx-demo (Pyodide)"
copyright = "2025, JupyterLite Contributors"
author = "JupyterLite Contributors"
release = "1.0.0"

# ── 扩展列表 ──
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "jupyterlite_sphinx",
    "sphinx_design",
    "myst_nb",
    "numpydoc",
]

# ── MyST 配置 ──
nb_execution_mode = "auto"

# ── HTML 输出 ──
html_theme = "pydata_sphinx_theme"
html_logo = "_static/icon.svg"
html_static_path = ["_static"]
html_css_files = ["button_styling.css"]

# ── JupyterLite 配置 ──
jupyterlite_contents = ["custom_contents/*"]
jupyterlite_silence = True
strip_tagged_cells = True

# ── TryExamples 配置 ──
global_enable_try_examples = True
try_examples_global_button_text = "Try it online"
try_examples_global_warning_text = (
    "⚠️ Interactive examples are experimental and may not work as expected "
    "compared to the native Jupyter experience."
)

# ── PyData 主题选项 ──
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/your-username/your-repo",
            "icon": "fa-brands fa-github",
        },
    ],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "use_edit_page_button": True,
    "secondary_sidebar_items": {
        "**": ["page-toc", "sourcelink", "edit-this-page"],
        "index": ["page-toc"],
    },
}

# ── GitHub 编辑链接 ──
html_context = {
    "github_url": "https://github.com",
    "github_user": "your-username",
    "github_repo": "your-repo",
    "github_version": "main",
    "doc_path": "docs/source/",
}
```

## JSON 配置文件

### jupyter-lite.json

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "jupyterlite-sphinx-demo (Pyodide)",
    "defaultKernelName": "python",
    "faviconUrl": "./lab/favicon.ico"
  }
}
```

### jupyter_lite_config.json

```json
{
  "LiteBuildConfig": {
    "no_sourcemaps": true
  }
}
```

### overrides.json（添加 Download 按钮）

```json
{
  "@jupyterlab/notebook-extension:panel": {
    "toolbar": [
      {
        "name": "download",
        "label": "Download",
        "args": {},
        "command": "docmanager:download",
        "icon": "ui-components:download",
        "rank": 50
      }
    ]
  }
}
```

### try_examples.json

```json
{
  "global_min_height": "400px",
  "ignore_patterns": []
}
```

## 自定义 CSS（button_styling.css）

```css
.try_examples_button {
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    background-color: #f37726;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin: 10px 0;
}

.try_examples_button::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        120deg,
        transparent,
        rgba(255, 255, 255, 0.3),
        transparent
    );
}

.try_examples_button:hover::before {
    animation: shine 0.5s ease forwards;
}

.try_examples_button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

@keyframes shine {
    0% { left: -100%; }
    100% { left: 100%; }
}
```

## 示例代码模块（example.py）

```python
"""Example module demonstrating TryExamples with NumPy-style docstrings."""
import math


def fibonacci_sequence(n):
    """Generate the Fibonacci sequence up to the nth term.

    Parameters
    ----------
    n : int
        Number of terms to generate. Must be positive.

    Returns
    -------
    list
        List containing the first n Fibonacci numbers.

    Examples
    --------
    >>> fibonacci_sequence(10)
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    """
    if n <= 0:
        return []
    seq = [0, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]


def solve_quadratic(a, b, c):
    """Solve quadratic equation ax² + bx + c = 0.

    Parameters
    ----------
    a, b, c : float
        Coefficients of the quadratic equation.

    Returns
    -------
    tuple
        Two roots as (x1, x2).

    Examples
    --------
    >>> solve_quadratic(1, -5, 6)
    (3.0, 2.0)
    """
    discriminant = b**2 - 4*a*c
    sqrt_d = math.sqrt(discriminant)
    x1 = (-b + sqrt_d) / (2*a)
    x2 = (-b - sqrt_d) / (2*a)
    return (x1, x2)


def image_processing(image_path):
    """Apply filters to an image.

    .. disable_try_examples

    Examples
    --------
    This example requires a local image file and is disabled for TryExamples.
    """
    pass  # Requires local files
```

## 文档页面示例

### jupyterlite/demo.md

````markdown
# JupyterLite Demo

This page embeds a full JupyterLab environment:

```{jupyterlite}
:width: 100%
:height: 600px
```
````

### replite/demo.md

````markdown
# REPL Demo

Try a lightweight Python REPL:

```{replite}
:width: 100%
:height: 400px
```
````

## 构建与预览

```bash
cd docs
make html
cd build/html
python -m http.server 8000
```

访问 `http://localhost:8000`，你将看到：
1. 首页展示模块 API 文档，每个 Examples 旁有"Try it online"按钮
2. JupyterLite 页面嵌入完整 JupyterLab
3. REPL 页面提供轻量代码执行
4. 按钮带有橙色光泽动画效果

## Pyodide 中安装额外包

在 JupyterLite Notebook 中使用 piplite 安装：

```python
import piplite
await piplite.install("sympy")
import sympy
x = sympy.Symbol('x')
print(sympy.integrate(x**2, x))
```

## 相关内容

- [/concepts/04-kernel-comparison.md](../concepts/04-kernel-comparison.md)：Pyodide vs Xeus 对比
- [/examples/03-xeus-setup.md](03-xeus-setup.md)：Xeus 内核配置
- [/examples/01-minimal-site.md](01-minimal-site.md)：最小站点示例
- [/concepts/06-try-examples.md](../concepts/06-try-examples.md)：TryExamples 详解
