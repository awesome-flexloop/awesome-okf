---
type: Example
title: 基础配置示例
description: 从零开始配置 Alabaster 主题的完整 conf.py 示例，包含常用选项
tags: [sphinx, theme, alabaster, example, configuration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:59:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-source
    resource: /references/alabaster-source.md
    title: Alabaster 源码路径映射
---

# 基础配置示例

本文档提供从零开始配置 Alabaster 主题的完整 `conf.py` 示例，适用于大多数 Python 开源项目。

## 完整 conf.py 示例

```python
# conf.py — Sphinx 配置文件

import os
import sys
sys.path.insert(0, os.path.abspath('..'))  # 如需 autodoc，导入项目路径

# -- 项目信息 -----------------------------------------------------

project = 'My Package'
copyright = '2024, Your Name'
author = 'Your Name'
release = '1.0.0'
version = '1.0'

# -- 通用配置 -----------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'zh_CN'  # 或 'en'

# -- HTML 输出配置 ------------------------------------------------

html_theme = 'alabaster'

# 侧边栏组件（必须配置，否则 Alabaster 自定义组件不加载）
html_sidebars = {
    '**': [
        'about.html',
        'searchfield.html',
        'navigation.html',
        'relations.html',
        'donate.html',
    ]
}

# 静态文件路径（logo、custom.css 等）
html_static_path = ['_static']

# 主题选项
html_theme_options = {
    # 基础信息
    'description': '一个简洁优雅的 Python 库',
    'github_user': 'your-username',
    'github_repo': 'my-package',
    'github_button': True,
    'github_type': 'star',
    'github_count': True,
    'show_powered_by': False,

    # 布局
    'page_width': '940px',
    'sidebar_width': '220px',
    'fixed_sidebar': False,

    # 配色
    'link': '#004B6B',
    'link_hover': '#6D4100',
    'code_bg': '#ecf0f3',
}

html_favicon = '_static/favicon.ico'

# -- 扩展配置 -----------------------------------------------------

# intersphinx 映射
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
```

## 项目目录结构

```
my-package/
├── docs/
│   ├── _static/
│   │   ├── custom.css      # 可选：自定义 CSS 覆盖
│   │   ├── favicon.ico     # 可选：网站图标
│   │   └── logo.png        # 可选：Logo 图片
│   ├── _templates/         # 可选：自定义模板覆盖
│   ├── conf.py             # 上述配置文件
│   ├── index.rst           # 文档入口
│   └── ...
├── mypackage/
│   └── __init__.py
└── pyproject.toml
```

## 最小 index.rst 示例

```rst
.. My Package documentation master file

Welcome to My Package's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   usage
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

## 构建文档

```bash
# 单次构建
sphinx-build -b html docs docs/_build/html

# 实时预览（需要 sphinx-autobuild）
sphinx-autobuild docs docs/_build/html --open-browser
```

## 验证配置正确性

构建完成后检查以下内容：

1. 左侧边栏显示项目名称和描述
2. GitHub Star 按钮正常显示
3. 目录树可展开/折叠
4. 上下页导航链接正常工作
5. 代码块语法高亮正常
6. 页脚不显示 "Powered by Sphinx"（因为 `show_powered_by = False`）

## 常见问题

**Q: 侧边栏没有显示 about.html 内容（Logo/描述/GitHub 按钮）？**

A: 确保 `html_sidebars` 配置了 `'about.html'`，并且 `html_theme = 'alabaster'` 设置正确。

**Q: 自定义 CSS 不生效？**

A: 确认 `html_static_path = ['_static']` 已配置，且 CSS 文件名为 `custom.css` 放在 `_static/` 目录下。

**Q: GitHub 按钮不显示？**

A: 需要同时设置 `github_user` 和 `github_repo`，且 `github_button = True`（默认值为 True）。

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [主题配置选项体系](/concepts/04-theme-options.md)
- [主题选项定制示例](custom-theme-options.md)
