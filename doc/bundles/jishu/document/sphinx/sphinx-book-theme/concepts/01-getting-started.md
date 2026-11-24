---
type: Concept
title: "安装与最小站点：五分钟让文档变成书"
description: "从 sphinx-quickstart 到启用 sphinx_book_theme 的最小配置、目录骨架、构建命令与常见报错处理"
tags: [sphinx, theme, install, quickstart, conf.py]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-getstarted
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/tutorials/get-started.html
    title: Get started — Sphinx Book Theme
  - id: sbt-local
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme
    title: 本地源码快照（1.5.0.dev）
---

# 安装与最小站点：五分钟让文档变成书

## 前置条件

你需要一个可运行的 Sphinx 工程。没有的话先创建：

```bash
pip install "sphinx>=8.2"
sphinx-quickstart docs
```

`sphinx-quickstart` 会生成 `docs/conf.py`、`docs/index.rst`、`docs/Makefile`。之后所有路径都相对 `docs/`。

> 本书主题要求 Python `>=3.11`、Sphinx `>=8.2`，并会把父主题 `pydata-sphinx-theme==0.23.0` 作为依赖自动安装。

## 安装主题

```bash
pip install sphinx-book-theme
```

验证安装：

```bash
python -c "import sphinx_book_theme; print(sphinx_book_theme.__version__)"
```

本地源码快照的版本号是 `1.5.0.dev`；PyPI 上最近正式版为 `1.4.0`。

## 启用主题

编辑 `docs/conf.py`，只改一行即可看到效果：

```python
html_theme = "sphinx_book_theme"
```

重新构建：

```bash
sphinx-build -b html docs _build/html
```

打开 `_build/html/index.html`，页面应变成"左侧全书目录 + 中间正文 + 右侧页内目录"的书籍布局。

## 一份可直接使用的最小配置

```python
# docs/conf.py
project = "My Book"
author = "My Team"
copyright = "2026, My Team"

extensions = [
    "myst_parser",          # 允许 .md 源文件；纯 reST 项目可删
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

html_theme = "sphinx_book_theme"
html_title = "My Book"
html_logo = "_static/logo.svg"   # 可选
html_static_path = ["_static"]

html_theme_options = {
    "repository_url": "https://github.com/your-org/your-repo",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "show_toc_level": 2,
    "show_navbar_depth": 2,
}

templates_path = ["_templates"]
```

安装 MyST（若使用 Markdown）：

```bash
pip install myst-parser
```

## 目录骨架

书籍主题不强制目录结构，但推荐：

```text
docs/
├── conf.py
├── index.md
├── _static/
│   └── logo.svg
├── _templates/
├── part-1/
│   ├── index.md
│   ├── chapter-1.md
│   └── chapter-2.md
└── part-2/
    ├── index.md
    └── chapter-3.md
```

`index.md` 用 `{toctree}` 组织全书：

````md
# My Book

```{toctree}
:maxdepth: 2
:caption: Part 1

part-1/index
```

```{toctree}
:maxdepth: 2
:caption: Part 2

part-2/index
```
````

`caption` 会变成左侧目录的分组标题——这是本书主题常用的"章节分组"手法。

## 验证清单

| 检查项 | 预期 |
|--------|------|
| 页面顶部 | 默认没有 navbar；只有左侧栏与正文 |
| 左侧栏 | 显示 `html_title`、logo、搜索框、全书目录 |
| 右侧栏 | 显示 `Contents` 页内目录 |
| 页眉按钮 | 默认有"下载"和"全屏"；配置仓库后出现源码类按钮 |
| 控制台 | 无 `ThemeError: no theme named 'sphinx_book_theme'` |
| 静态资源 | 页面样式正常，无 404 的 `sphinx-book-theme.css` |

## 常见报错

### `ThemeError: no theme named 'sphinx_book_theme' found`

主题未安装到当前解释器，或构建用了另一个 Python 环境：

```bash
python -m pip show sphinx-book-theme
python -m sphinx -b html docs _build/html
```

### 页面样式错乱、按钮消失

常见原因是沿用了旧主题的 `html_theme_options`。父主题与本书主题的选项名不同，先注释掉旧配置，再逐项加回：

```python
html_theme_options = {
    # "bootswatch_theme": "cosmo",   # 旧主题选项，本书主题不识别
}
```

### `html_theme_options` 里的布尔值不生效

`theme.conf` 的值从配置系统读出时可能是字符串。主题内部用 `as_bool()` 或模板 `|tobool` 转换；你自己写的模板里也要显式转换，不要直接 `if theme_xxx`。

### 下载按钮的源文件后缀不对

本书主题在用户未显式配置 `html_sourcelink_suffix` 时，把它默认设为空字符串，以便下载 `.md`/`.rst`/`.ipynb` 原文件而不是 `.txt`。若你确实需要 `.txt`，显式设置：

```python
html_sourcelink_suffix = ".txt"
```

### 构建很慢或缓存不更新

主题会为主题 CSS/JS 追加内容哈希做缓存失效。若你改了自定义 CSS 但页面没变，先清理构建目录：

```bash
sphinx-build -E -a -b html docs _build/html
```

## 下一步

- 想理解主题内部如何拼装页面：[主题骨架与构建链](02-theme-architecture.md)
- 想配置导航、页脚、公告条：[页面分区与导航](03-layout-and-navigation.md)
- 想要完整可复制工程：[从零搭建书籍站点](../examples/01-basic-book-site.md)
