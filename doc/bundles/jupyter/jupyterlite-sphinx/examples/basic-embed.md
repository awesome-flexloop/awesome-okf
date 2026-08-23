---
type: Example
title: 基础嵌入：空 JupyterLab 环境
description: 最简示例：在文档中嵌入一个空白 JupyterLab 环境，带点击加载按钮
tags: [example, basic, jupyterlab, embed]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
---

本示例展示 jupyterlite-sphinx 最基础的用法——在 Sphinx 文档中嵌入一个空白的 JupyterLab（Jupyter 实验室）环境。读者点击按钮后，会在页面内以 iframe（内联框架）形式加载完整的 JupyterLab 界面，可以自由创建 Notebook、编写代码并运行。这是所有高级用法的起点，适合作为快速体验入口。

## 项目结构

```
my-docs/
├── conf.py
├── index.rst
└── _build/           # 构建输出目录
```

## conf.py 配置

`conf.py` 是 Sphinx 的核心配置文件。最简配置只需在 `extensions` 列表中添加 `jupyterlite_sphinx`：

```python
# conf.py

project = 'My JupyterLite Docs'
copyright = '2026, Your Name'
author = 'Your Name'
release = '0.1'

extensions = [
    'jupyterlite_sphinx',
]

html_theme = 'alabaster'
```

无需额外的 JupyterLite 配置项，扩展会自动处理 JupyterLite 构建、静态资源复制和指令注册。默认的 JupyterLite 输出目录为 `lite/`，内容暂存目录为 `_contents/`。

## RST 文档内容

在 `index.rst` 中使用 `.. jupyterlite::` 指令嵌入 JupyterLab。以下示例设置了宽度、高度和点击加载按钮：

```rst
Welcome to My Docs
==================

点击下方按钮，在浏览器中启动 JupyterLab：

.. jupyterlite::
   :width: 100%
   :height: 600px
   :prompt: Try JupyterLite!
```

## 选项说明

| 选项 | 值 | 说明 |
|------|----|------|
| `:width:` | `100%` | iframe 宽度，支持 CSS 单位（`%`、`px` 等），默认 `100%` |
| `:height:` | `600px` | iframe 高度，默认 `1000px` |
| `:prompt:` | `Try JupyterLite!` | 启用懒加载模式，显示可点击按钮；按钮文本为指定字符串。省略此选项则直接加载 iframe（无按钮） |
| `:prompt_color:` | 例如 `#f7dc1e` | 自定义按钮背景色，默认黄色 `#f7dc1e` |

`:prompt:` 选项的作用是启用"点击加载"模式（懒加载）。不设置 `:prompt:` 时，页面加载后 iframe 会立即请求 JupyterLite 资源，可能拖慢页面首次渲染速度；设置后仅显示一个按钮，用户点击后才加载 JupyterLite 实例，显著提升页面加载性能。

## 构建命令

在项目目录下执行 `sphinx-build` 构建 HTML 文档：

```bash
sphinx-build -b html . _build/html
```

或使用 sphinx-quickstart 生成的 Makefile：

```bash
make html
```

首次构建时，jupyterlite-sphinx 会在 `build-finished` 阶段自动调用 `jupyter lite build` 命令，生成 JupyterLab、REPL、Notebook 等应用的静态资源，输出到 `_build/html/lite/` 目录。首次构建可能需要 30 秒到数分钟（取决于网络和机器性能），后续构建会利用缓存加速。

## 查看效果

构建完成后，使用 HTTP 服务器访问生成的文档：

```bash
cd _build/html
python -m http.server 8000
```

在浏览器中访问 `http://localhost:8000`。页面中会显示一个黄色按钮，文字为 "Try JupyterLite!"。点击按钮后，按钮区域变为 JupyterLab 的加载界面，加载完成后即可在 iframe 中使用完整的 JupyterLab 环境——创建 Notebook、编写 Python 代码、运行单元格，一切均在浏览器中完成，无需本地安装 Python。

## 直接嵌入（无按钮）

如果不需要懒加载按钮，可以省略 `:prompt:` 选项，iframe 会在页面加载时直接渲染：

```rst
.. jupyterlite::
   :width: 100%
   :height: 600px
```

此时页面直接显示 JupyterLab iframe，无点击加载步骤。但需要注意，这会在页面加载时立即请求 JupyterLite 资源，增加首次加载时间。

## 相关概念

- [jupyterlite 指令详解](/concepts/04-jupyterlite-directive.md)
- [指令系统总览](/concepts/03-directive-overview.md)
- [配置参考](/references/config-reference.md)
- [快速开始](/concepts/02-quick-start.md)
- [构建流程](/concepts/10-build-process.md)
