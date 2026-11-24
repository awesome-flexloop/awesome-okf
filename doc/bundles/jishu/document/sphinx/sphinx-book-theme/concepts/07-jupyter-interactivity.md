---
type: Concept
title: "Notebook 与在线交互：主题与执行层的分工"
description: "sphinx-book-theme 如何与 MyST-NB、sphinx-thebe、Binder/Colab 协作：Notebook 单元格样式、标签、下载 .ipynb、Thebe 实时运行与启动按钮的边界"
tags: [sphinx, theme, jupyter, myst-nb, thebe, binder, notebook]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-notebooks
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/content/notebooks.html
    title: Jupyter notebooks
  - id: sbt-launch-doc
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/content/launch.html
    title: Launch buttons for interactivity
  - id: sbt-launch-code
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/header_buttons/launch.py
    title: launch.py
---

# Notebook 与在线交互：主题与执行层的分工

## 职责边界

| 层 | 负责 | 不负责 |
|----|------|--------|
| `myst-nb` | 解析 `.ipynb` / MyST 代码单元格、执行、缓存、生成输出 HTML | 页面布局与按钮 |
| `sphinx-book-theme` | 单元格视觉样式、下载 `.ipynb` 按钮、启动按钮、边注/full-width 标签样式 | 执行代码、管理内核 |
| `sphinx-thebe` | 把静态单元格变成可交互单元格、连接 Binder 内核 | 页面骨架 |
| BinderHub / JupyterHub / Colab | 真正运行代码的环境 | 文档构建 |

理解这条边界，能避免"为什么 Thebe 不执行"这类误判——主题只负责把按钮和配置接上，执行能力来自扩展与外部服务。

## 启用 Notebook 内容

安装：

```bash
pip install myst-nb
```

`conf.py`：

```python
extensions = [
    "myst_nb",
]

source_suffix = {
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
    ".rst": "restructuredtext",
}

nb_execution_mode = "cache"   # 常用：缓存执行结果
```

执行模式：

| 模式 | 行为 |
|------|------|
| `off` | 不执行，直接渲染已有输出 |
| `force` | 每次构建都执行 |
| `cache` | 有缓存则复用，否则执行（推荐） |
| `auto` | 类似 cache，按需执行 |

> 主题本身不设置 `nb_execution_mode`；这是 `myst-nb` 的配置。主题的 `docs/conf.py` 用 `cache` 是为了自己的文档站。

## 单元格视觉样式

主题的 SCSS 在 `assets/styles/content/_notebooks.scss` 与 `extensions/_myst-nb.scss` 中定义单元格样式。最终效果由 MyST-NB 生成的 HTML class 驱动：

| HTML 结构/class | 视觉 |
|----------------|------|
| `.cell` / `.cell_input` / `.cell_output` | 输入区与输出区的边框、背景、间距 |
| `.output` | 输出区留白与滚动 |
| `.cell_output img` | 图片自适应宽度 |
| `.jp-InputPrompt` / `.jp-OutputPrompt` | 执行计数提示 |

主题不改变 Notebook 的语义结构，只负责"看起来像书"。

## 常用单元格标签

标签写在 `.ipynb` 单元格 metadata，或 MyST 的 `:tags:` 选项：

````md
```{code-cell} python
:tags: [hide-input]

print("代码隐藏，输出保留")
```
````

| 标签 | 效果 |
|------|------|
| `hide-input` / `hide_input` | 隐藏代码，保留输出 |
| `hide-output` | 隐藏输出，保留代码 |
| `hide-cell` | 代码与输出都隐藏 |
| `remove-cell` / `remove_cell` | 从文档中彻底移除 |
| `remove-input` | 移除代码，保留输出 |
| `remove-output` | 移除输出，保留代码 |
| `margin` | 单元格放入右侧留白 |
| `full-width` / `full_width` | 单元格全宽 |
| `output_scroll` / `scroll-output` | 输出区可滚动 |
| `scroll-input` | 输入区可滚动 |
| `thebe-init` | 作为 Thebe 初始化单元格 |

Markdown 单元格也可用标签：

```md
+++ {"tags": ["margin"]}

这段 Markdown 会进入右侧留白。
```

## 下载 `.ipynb`

当页面由 Notebook 生成时，`launch.py` 会把构建目录里的 `jupyter_execute/<pagename>.ipynb` 复制到 `_sources/<pagename>.ipynb`，然后下载组里出现 `.ipynb` 按钮。

前提：

- 页面元数据含 `kernelspec`，或源文件后缀含 `ipynb`；
- `use_download_button` 为真（默认）；
- 构建确实产生了 `jupyter_execute` 下的 notebook。

如果按钮不出现，先检查 `_build/jupyter_execute/` 是否有对应文件。

## 启动按钮

完整 URL 规则见[页眉按钮机制](05-header-buttons.md)。这里只列配置骨架：

```python
html_theme_options = {
    "repository_url": "https://github.com/org/repo",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "colab_url": "https://colab.research.google.com",
        "thebe": True,
        "notebook_interface": "jupyterlab",
    },
}
```

### Binder 能启动的前提

Binder 不是"读你的 HTML"，而是"克隆仓库 + 安装环境 + 打开 notebook"。因此仓库需要：

- 公开可访问（或 Binder 能访问）；
- 根目录或 `binder/` 下有 `environment.yml` / `requirements.txt` / `postBuild` 等环境描述；
- notebook 路径与 `path_to_docs` 拼接结果一致。

否则按钮能点开，但 Binder 构建会失败。

### Colab 的限制

- 只支持 GitHub。
- 打开的是仓库中的 notebook 文件；Markdown 页面需要配套 `.ipynb` 才能获得较好体验。
- 私有仓库需要 Colab 有访问权限。

### Deepnote 的副作用

每次点击都会创建一个新的 Deepnote 项目。不要把 Deepnote 按钮放在高频入口。

## Thebe：页面内实时运行

Thebe 的目标：读者不离开页面就能运行代码。

### 启用

```bash
pip install sphinx-thebe
```

```python
extensions = [
    "myst_nb",
    "sphinx_thebe",
]

html_theme_options = {
    "repository_url": "https://github.com/org/repo",
    "repository_branch": "main",
    "launch_buttons": {
        "thebe": True,
    },
}
```

主题会：

- 追加一个"Live Code"按钮，调用 `initThebeSBT()`；
- 设置 `context["use_thebe"] = True`；
- 把 `repository_url` / `repository_branch` 补进 `thebe_config`（若用户没写）。

### 初始化单元格

第一个需要执行的单元格加 `thebe-init` 标签，让 Thebe 在激活时先运行它（通常是 import 与全局配置）：

````md
```{code-cell} python
:tags: [thebe-init]

import numpy as np
import matplotlib.pyplot as plt
```
````

### 自定义 Thebe 配置

```python
thebe_config = {
    "repository_url": "https://github.com/binder-examples/jupyter-stacks-datascience",
    "repository_branch": "master",
}
```

`thebe_config` 会覆盖主题从 `html_theme_options` 推导的值。完整字段见 `sphinx-thebe` 文档。

### Thebe 的常见失败

| 现象 | 原因 |
|------|------|
| 按钮出现但点击无反应 | 未安装/未启用 `sphinx_thebe` |
| 一直转圈 | Binder 环境构建失败或网络不可达 |
| 代码能显示但不能运行 | 缺少 `thebe-init` 单元格或内核未就绪 |
| 样式错乱 | 自定义 CSS 覆盖了 Thebe 的按钮/单元格 class |

## 交互内容的设计建议

- 把"必须运行才能理解"的代码放在页面内，把"可选探索"放到 Binder。
- 每个 Notebook 页面只保留一个 `thebe-init`，避免重复初始化内核。
- 输出很大的单元格加 `output_scroll`，不要让页面被一张表撑爆。
- 图片输出优先用静态 PNG/SVG；交互图（Plotly、folium）要确认离线/在线行为。
- 私有数据不要放进公开仓库，Binder/Colab 会把它暴露给任何点击按钮的人。

## 相关概念

- [页眉按钮机制](05-header-buttons.md)
- [Notebook 内容流水线](../examples/04-notebook-content-pipeline.md)
- [配置选项全解](04-theme-options.md)
