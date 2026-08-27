---
type: Example
title: 基础书籍配置
description: sphinx-book-theme 的最小配置、常用配置和完整书籍项目结构示例
tags:
- sphinx-book-theme
- example
- setup
- configuration
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
- pyproject.toml
---

# 基础书籍配置示例

## 最小 conf.py

```python
# conf.py — sphinx-book-theme 最小配置
project = "我的技术书籍"
author = "作者名"
release = "0.1"

extensions = [
    "sphinx_book_theme",
]

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/username/my-book",
    "use_repository_button": True,
    "use_download_button": True,
    "use_fullscreen_button": True,
}
```

## 常用配置示例

### 带源码操作按钮的配置

```python
html_theme_options = {
    # 仓库配置
    "repository_url": "https://github.com/username/my-book",
    "repository_branch": "main",
    "path_to_docs": "docs",
    # 按钮配置
    "use_repository_button": True,
    "use_source_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "use_download_button": True,
    "use_fullscreen_button": True,
    # 导航配置
    "home_page_in_toc": True,
    "show_navbar_depth": 2,
    "max_navbar_depth": 4,
    "collapse_navbar": False,
    # 目录标题
    "toc_title": "本页目录",
}
```

### 带公告栏的配置

```python
html_theme_options = {
    "repository_url": "https://github.com/username/my-book",
    "use_repository_button": True,
    "announcement": (
        "<p>📢 《我的技术书籍》正在持续更新中，"
        "<a href='https://github.com/username/my-book/discussions'>"
        "欢迎反馈</a>！</p>"
    ),
}
```

### 带Logo和图标的配置

```python
html_theme_options = {
    "repository_url": "https://github.com/username/my-book",
    "use_repository_button": True,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/username/my-book",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/my-package",
            "icon": "fa-solid fa-box",
        },
    ],
}

html_logo = "_static/logo-wide.svg"
html_favicon = "_static/favicon.ico"
```

### 带边注功能的配置

```python
extensions = [
    "sphinx_book_theme",
    "myst_parser",  # 或 myst_nb
]

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/username/my-book",
    "use_repository_button": True,
    "use_sidenotes": True,  # 启用脚注→边注转换
}
```

### 暗色模式代码高亮配置

```python
html_theme_options = {
    "repository_url": "https://github.com/username/my-book",
    "pygments_light_style": "tango",
    "pygments_dark_style": "monokai",
}
```

## MyST（Markdown）项目完整配置

使用 MyST-Parser 编写 Markdown 文档的完整 conf.py：

```python
project = "MyST 技术书籍"
author = "作者名"
copyright = "2024, 作者名"
release = "1.0"

extensions = [
    "sphinx_book_theme",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_togglebutton",
]

# MyST 配置
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "linkify",
    "replacements",
    "smartquotes",
    "tasklist",
]
myst_heading_anchors = 3

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/username/myst-book",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "use_sidenotes": True,
    "home_page_in_toc": True,
    "show_navbar_depth": 2,
}

html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
```

## 项目目录结构

```
my-book/
├── docs/
│   ├── _static/
│   │   ├── css/
│   │   │   └── custom.css
│   │   ├── logo-wide.svg
│   │   └── favicon.ico
│   ├── _templates/
│   │   └── ... (自定义模板覆盖)
│   ├── index.md           # 首页
│   ├── chapter1.md        # 第一章
│   ├── chapter2.md        # 第二章
│   ├── conf.py            # Sphinx配置
│   └── _toc.yml           # 目录配置(如使用sphinx-external-toc)
├── pyproject.toml
└── README.md
```

## 构建命令

```bash
# 安装依赖
pip install sphinx-book-theme myst-parser

# 构建HTML
sphinx-build docs docs/_build/html

# 或使用Makefile
make html

# 自动重新构建（开发模式）
pip install sphinx-autobuild
sphinx-autobuild docs docs/_build/html --port 8000
```

## 边注使用示例（MyST）

```markdown
# 第一章：入门

这是正文内容，这里有一个带编号的旁注[^1]和一个无编号的边注[^2]。

[^1]: 这是旁注内容，会自动显示在右侧边距，带编号上标。
[^2]: {-} 这是边注内容，不显示编号，适合补充说明。

```{margin} 小贴士
Margin指令可以放置任意内容，包括**加粗文字**、列表：
- 第一项
- 第二项
```

普通段落内容继续...
```

## 相关概念

- [安装与基础配置](../concepts/01-getting-started.md)
- [配置系统详解](../concepts/03-configuration.md)
- [Margin指令与边注旁注](../concepts/05-margin-sidenotes.md)
- [交互式计算书籍配置](interactive-book.md)
