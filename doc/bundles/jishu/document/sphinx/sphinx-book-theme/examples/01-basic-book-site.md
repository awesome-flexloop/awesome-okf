---
type: Example
title: "从零搭建一个书籍站点"
description: "完整可复制的 Sphinx + sphinx-book-theme 工程：conf.py、首页、分组目录、章节页、构建命令与验收清单"
tags: [sphinx, theme, example, conf.py, toctree, build]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-getstarted
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/tutorials/get-started.html
    title: Get started
  - id: sbt-local
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme
    title: 本地源码快照（1.5.0.dev）
---

# 从零搭建一个书籍站点

目标：一个能构建、能导航、能发布的三章小书。

## 1. 创建工程

```bash
mkdir my-book && cd my-book
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install "sphinx>=8.2" sphinx-book-theme myst-parser
sphinx-quickstart docs --sep -p "My Book" -a "My Team" -v 1.0 -l zh_CN
```

生成后删除 `docs/index.rst`，改用 `docs/index.md`。

## 2. 目录结构

```text
my-book/
├── docs/
│   ├── conf.py
│   ├── index.md
│   ├── _static/
│   │   └── custom.css
│   ├── _templates/
│   ├── part-1/
│   │   ├── index.md
│   │   ├── chapter-1.md
│   │   └── chapter-2.md
│   └── part-2/
│       ├── index.md
│       └── chapter-3.md
└── .gitignore
```

## 3. docs/conf.py

```python
# -- Project ---------------------------------------------------------------
project = "My Book"
author = "My Team"
copyright = "2026, My Team"
release = "1.0"

# -- General ---------------------------------------------------------------
extensions = [
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
]

# -- HTML ------------------------------------------------------------------
html_theme = "sphinx_book_theme"
html_title = "My Book"
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.ico"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
templates_path = ["_templates"]

html_theme_options = {
    # 仓库与源码按钮
    "repository_url": "https://github.com/your-org/my-book",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "use_source_button": True,

    # 导航
    "show_navbar_depth": 2,
    "max_navbar_depth": 4,
    "collapse_navbar": False,
    "home_page_in_toc": True,

    # 页内目录
    "toc_title": "本页目录",
    "show_toc_level": 2,

    # 页脚
    "footer_content_items": [
        "author.html",
        "copyright.html",
        "last-updated.html",
    ],

    # 公告（可选）
    "announcement": "第一版发布，欢迎反馈。",
}
```

> `html_logo` 指向的文件必须存在，否则构建会警告。没有 logo 就删掉这两行。

## 4. docs/index.md

````md
# My Book

一本用 Sphinx + sphinx-book-theme 写成的示例书。

## 第一部分：基础

```{toctree}
:maxdepth: 2
:caption: 第一部分

part-1/index
```

## 第二部分：进阶

```{toctree}
:maxdepth: 2
:caption: 第二部分

part-2/index
```
````

`caption` 会成为左侧目录的分组标题；多个 `toctree` 让一本长书有清晰层级。

## 5. 分组首页

`docs/part-1/index.md`：

````md
# 第一部分：基础

介绍本书的基本概念与工作流。

```{toctree}
:maxdepth: 1

chapter-1
chapter-2
```
````

`docs/part-2/index.md`：

````md
# 第二部分：进阶

```{toctree}
:maxdepth: 1

chapter-3
```
````

## 6. 章节页

`docs/part-1/chapter-1.md`：

````md
# 第一章：为什么写书

这一章说明动机。

:::{note}
这是一个提示框。
:::

## 小节一

正文内容。
````

`docs/part-1/chapter-2.md`：

````md
# 第二章：工具链

```bash
pip install sphinx-book-theme
```

## 小节一

正文内容。
````

`docs/part-2/chapter-3.md`：

````md
# 第三章：发布

把 `_build/html` 部署到静态托管即可。

## 小节一

正文内容。
````

## 7. 自定义 CSS

`docs/_static/custom.css`：

```css
:root {
    --pst-color-primary: #0b5fff;
    --pst-color-link: #0b5fff;
}

h1, h2 {
    letter-spacing: 0.01em;
}

/* 让下载按钮更醒目（label 生成的稳定 class） */
.btn-download-buttons {
    border: 1px solid var(--pst-color-primary);
}
```

## 8. 构建

```bash
sphinx-build -b html docs _build/html
```

开发时用自动重建：

```bash
pip install sphinx-autobuild
sphinx-autobuild docs _build/html --open-browser
```

## 9. 验收清单

| 检查项 | 预期 |
|--------|------|
| 首页 | 两个 `toctree` 分组出现在左侧目录 |
| 左侧目录 | 默认展开到第 2 层；首页在目录顶部 |
| 章节页 | 右侧显示"本页目录"；H2 常驻 |
| 页眉 | 有仓库、编辑、issue、源码、下载、全屏按钮 |
| 页脚 | 显示作者、版权、最后更新时间 |
| 构建日志 | 无 `WARNING: document isn't included in any toctree` |
| 移动端 | 左右侧栏可折叠；正文可读 |

## 10. 常见问题

### 首页没有出现在左侧目录

设置 `"home_page_in_toc": True`。

### 目录只显示一级

`show_navbar_depth` 默认是 `1`；改成 `2` 或更高。

### 右侧目录没有

当前页没有二级标题时，父主题会隐藏右侧栏。加几个 `##` 标题即可。

### 构建警告 `document isn't included in any toctree`

某个 `.md` 没有被任何 `toctree` 引用。补进分组首页，或在 `exclude_patterns` 中排除。

### 中文搜索效果差

Sphinx 默认搜索对中文分词有限。可在 `conf.py` 配置 `html_search_language = "zh"`，或接入 jieba 等分词方案。本书主题不改变搜索实现，搜索来自父主题与 Sphinx。

## 下一步

- 加仓库与在线运行按钮：[仓库按钮与在线启动按钮](02-repository-and-launch-buttons.md)
- 加边注与全宽图表：[边注、margin 与自定义 CSS](03-margin-notes-and-custom-css.md)
- 加 Notebook：[Notebook 内容流水线](04-notebook-content-pipeline.md)
