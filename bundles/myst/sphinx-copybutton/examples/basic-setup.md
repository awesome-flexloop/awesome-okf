---
type: Example
title: 基础配置示例
description: sphinx-copybutton 的最小化和常用配置完整 conf.py 示例，从零开始启用代码块复制功能
tags: [sphinx, sphinx-extension, copybutton, example, configuration, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: copybutton-source
    resource: /references/copybutton-source.md
    title: sphinx-copybutton 源码路径映射
---

# 基础配置示例

本文档提供 sphinx-copybutton 的完整配置示例，从最小化配置到常用定制场景。

## 最小化 conf.py

以下是启用 sphinx-copybutton 的最小配置：

```python
# conf.py — Sphinx 配置文件

# -- 项目信息 -----------------------------------------------------
project = 'My Project'
copyright = '2024, Your Name'
author = 'Your Name'
release = '1.0.0'

# -- 通用配置 -----------------------------------------------------
extensions = [
    'sphinx_copybutton',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'zh_CN'

# -- HTML 输出配置 ------------------------------------------------
html_theme = 'alabaster'  # 或其他你喜欢的主题
html_static_path = ['_static']
```

安装依赖并构建：

```bash
pip install sphinx sphinx-copybutton
sphinx-build -b html . _build/html
```

此时所有代码块都有复制按钮，但不会剥离任何提示符。

## 含提示符剥离的常用配置

适用于包含 Bash/Python 代码示例的技术文档：

```python
# conf.py
project = 'My Project'
copyright = '2024, Your Name'
author = 'Your Name'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_copybutton',
]

exclude_patterns = ['_build']
language = 'zh_CN'

# -- sphinx-copybutton 配置 ---------------------------------------

# Bash 提示符
copybutton_prompt_text = "$ "
copybutton_remove_prompts = True
copybutton_only_copy_prompt_lines = True
copybutton_copy_empty_lines = True

# -- HTML 输出 ---------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
```

## 完整定制配置示例

包含所有常用选项和自定义样式：

```python
# conf.py
import os
import sys
from pathlib import Path

project = 'My Python Package'
copyright = '2024, Your Name'
author = 'Your Name'
release = '2.0.0'
version = '2.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'zh_CN'

# -- sphinx-copybutton 完整配置 -----------------------------------

# 提示符配置：匹配 Bash $ 和 Python >>> / ...
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

# 文本处理选项
copybutton_only_copy_prompt_lines = True   # 只复制含提示符的行（跳过输出）
copybutton_remove_prompts = True           # 复制时移除提示符
copybutton_copy_empty_lines = True         # 保留空行
copybutton_line_continuation_character = "\\"  # Shell 续接符
copybutton_here_doc_delimiter = ""         # 不使用 HERE 文档

# 选择器配置
copybutton_selector = "div.highlight pre"  # 默认选择器
copybutton_exclude = ".linenos, .gp"       # 排除行号和 Pygments 提示符span

# 自定义图标（可选）
# icon_path = Path("_static/copy-icon.svg")
# if icon_path.exists():
#     copybutton_image_svg = icon_path.read_text()

# -- HTML 输出 ---------------------------------------------------
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_css_files = ['custom-copybutton.css']
```

## 项目目录结构

```
my-project/
├── docs/
│   ├── _static/
│   │   ├── custom-copybutton.css  # 可选：自定义按钮样式
│   │   └── copy-icon.svg         # 可选：自定义复制图标
│   ├── _templates/
│   ├── conf.py                   # 上述配置文件
│   ├── index.rst                 # 文档入口
│   └── ...
├── mypackage/
│   └── __init__.py
└── pyproject.toml
```

## 最小 index.rst 示例

```rst
.. My Project documentation master file

Welcome to My Project's documentation!
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   usage

代码块示例
==========

Bash 命令：

.. code-block:: bash

   $ pip install my-package
   $ python -c "import mypackage; print(mypackage.__version__)"

Python 代码：

.. code-block:: python

   >>> import mypackage
   >>> obj = mypackage.MyClass()
   >>> obj.run()
   'Hello, World!'

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

## custom-copybutton.css 示例

在 `_static/custom-copybutton.css` 中自定义按钮外观：

```css
/* 让按钮始终可见 */
button.copybtn {
    opacity: 0.5;
    transition: opacity 0.2s;
}
button.copybtn:hover,
button.copybtn.success {
    opacity: 1;
}

/* 调整按钮大小 */
button.copybtn {
    width: 2em;
    height: 2em;
    top: 0.25em;
    right: 0.25em;
}

/* 自定义颜色 */
button.copybtn {
    background-color: #e7f3ff;
    border-color: #b3d9ff;
    color: #0066cc;
}
button.copybtn.success {
    background-color: #e6ffe6;
    border-color: #66cc66;
    color: #009900;
}
```

## 构建文档

```bash
# 单次构建
sphinx-build -b html docs docs/_build/html

# 实时预览（需要 sphinx-autobuild）
pip install sphinx-autobuild
sphinx-autobuild docs docs/_build/html --open-browser
```

## 验证配置

构建后验证以下功能：

1. 所有代码块右上角在悬停时显示复制按钮
2. 点击按钮复制代码内容
3. Bash 代码块复制后不包含 `$` 提示符
4. Python REPL 代码块复制后不包含 `>>>` 和 `...`
5. 复制成功后按钮短暂显示绿色对勾
6. 打印预览中不显示复制按钮
7. 中文页面显示"复制"/"复制成功!"提示

## 常见问题排查

**Q: 按钮不显示？**

```bash
# 检查扩展是否正确加载
sphinx-build -b html . _build/html 2>&1 | grep -i copybutton
```

**Q: 复制时没有剥离提示符？**

检查 `copybutton_prompt_text` 是否与实际提示符匹配。注意空格——`$ `（dollar+空格）和 `$`（只有dollar）是不同的。

**Q: 行号被复制了？**

确保 `copybutton_exclude` 包含 `.linenos`，且 Pygments 生成的行号使用的是该类名。某些主题可能使用不同的类名，需要用浏览器开发者工具检查。

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [文本处理与提示符剥离](/concepts/03-text-processing.md)
- [自定义样式与图标](/concepts/04-customization.md)
- [Shell 提示符配置示例](shell-prompts.md)
