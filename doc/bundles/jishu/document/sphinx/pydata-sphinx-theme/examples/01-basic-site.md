---
type: Example
title: 基础站点配置
description: 从零搭建一个可用的 PST 文档站：conf.py、目录结构、toctree 与构建验收
tags: [sphinx, theme, pydata, example, configuration]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:26:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 基础站点配置

## 目标

搭建一个包含首页、指南、API 三个顶层章节的文档站，具备顶部导航、左侧章节树、右侧页内目录、暗色模式与 GitHub 编辑链接。

## 目录结构

```text
mydocs/
├── conf.py
├── index.md
├── guide/
│   ├── index.md
│   ├── install.md
│   └── usage.md
├── api/
│   └── index.md
└── _static/
    ├── logo-light.svg
    └── logo-dark.svg
```

## conf.py

```python
project = "Acme Toolkit"
author = "Acme Docs Team"
copyright = "2026, Acme"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

myst_enable_extensions = ["colon_fence", "linkify"]
myst_heading_anchors = 3

language = "zh_CN"
html_theme = "pydata_sphinx_theme"
html_title = "Acme Toolkit"
html_static_path = ["_static"]
html_logo = "_static/logo-light.svg"
html_favicon = "_static/logo-light.svg"
html_baseurl = "https://docs.acme.example/"

html_theme_options = {
    "logo": {
        "text": "Acme Toolkit",
        "image_light": "_static/logo-light.svg",
        "image_dark": "_static/logo-dark.svg",
        "alt_text": "Acme Toolkit - Home",
    },
    "github_url": "https://github.com/acme/toolkit",
    "navbar_align": "content",
    "header_links_before_dropdown": 5,
    "show_nav_level": 1,
    "navigation_depth": 3,
    "show_toc_level": 1,
    "use_edit_page_button": True,
    "back_to_top_button": True,
}

html_context = {
    "github_user": "acme",
    "github_repo": "toolkit",
    "github_version": "main",
    "doc_path": "docs",
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
```

## index.md

````markdown
# Acme Toolkit

Acme Toolkit 是……

```{toctree}
:maxdepth: 2
:caption: 指南

guide/index
```

```{toctree}
:maxdepth: 2
:caption: API

api/index
```
````

## guide/index.md

````markdown
# 指南

```{toctree}
:maxdepth: 2

install
usage
```
````

## 构建

```console
$ sphinx-build -b html . _build/html -W
$ python -m http.server -d _build/html 8000
```

## 你会看到

1. 顶部：logo + “Acme Toolkit”，中部是“指南 / API”，右侧是主题切换与 GitHub 图标。
2. 左侧：进入“指南”后显示 install / usage；进入 API 后切换为 API 子树。
3. 右侧：页内目录 + “Edit on GitHub” + “View source”。
4. 右上角：light / dark / auto。

## 验收与常见调整

| 需求 | 改动 |
|---|---|
| 顶部导航左对齐 | `"navbar_align": "left"` |
| 隐藏上一页/下一页 | `"show_prev_next": False` |
| 首页不显示左侧栏 | `html_sidebars = {"index": []}` |
| 某页不显示右侧栏 | 页面元数据 `html_theme.sidebar_secondary.remove: true` |
| 增加外链 | `"external_links": [{"name": "官网", "url": "https://acme.example"}]` |

## 相关概念

- [快速开始](../concepts/01-getting-started.md)
- [布局与模板区段](../concepts/03-layout-and-sections.md)
- [导航与 toctree](../concepts/04-navigation-and-toctree.md)
