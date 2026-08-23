---
type: Concept
title: jupyterlite-sphinx 是什么
description: jupyterlite-sphinx 是将 JupyterLite 嵌入 Sphinx 文档的扩展，提供交互式代码示例和 Notebook 嵌入能力
tags: [introduction, sphinx, jupyterlite]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
---

jupyterlite-sphinx 是一个 Sphinx 文档扩展（extension），版本 0.23.0，要求 Python >= 3.10。它的核心功能是将 JupyterLite——一个完全在浏览器中运行的 Jupyter 环境——嵌入到 Sphinx 生成的 HTML 文档中，使技术文档的读者无需安装任何本地环境即可直接运行代码、编辑 Notebook 和交互探索。

在技术文档中嵌入可运行的代码示例一直是文档作者的痛点：静态代码块无法执行，外部链接（如 Binder、Colab）需要跳转且依赖网络服务，而本地运行要求读者配置环境。jupyterlite-sphinx 通过在 Sphinx 构建流程中自动集成 JupyterLite，提供了"文档即环境"的体验——读者在阅读文档时点击按钮即可在当前页面内启动一个完整的 Jupyter 会话，所有计算在浏览器端通过 Pyodide 或 JavaScript 内核完成。

## 五个核心指令

jupyterlite-sphinx 提供了五个 RST（reStructuredText）指令（directive），覆盖了不同的嵌入场景：

| 指令名 | 嵌入内容 | 前端界面 |
|--------|---------|---------|
| `jupyterlite` | 空 JupyterLab 环境或指定 Notebook | JupyterLab |
| `notebooklite` | 经典 Notebook 界面打开 Notebook 文件 | Jupyter Notebook（经典界面） |
| `replite` | REPL（Read-Eval-Print Loop）交互式控制台 | Jupyter REPL |
| `voici` | Voici 仪表板渲染 | Voici dashboards |
| `try_examples` | 自动将 doctest 代码示例转为可运行 Notebook | Notebook tree 视图 |

其中 `retrolite` 是 `notebooklite` 的别名，两者指向同一个指令类。

## 核心能力概述

**嵌入空环境**：使用 `.. jupyterlite::` 指令可以在文档中嵌入一个空白的 JupyterLab 界面，读者可以自由创建 Notebook、编写代码、安装纯 Python 包。这适用于"动手试一试"类的教学场景。

**嵌入 Notebook 文件**：通过 `.. jupyterlite:: path/to/notebook.ipynb` 或 `.. notebooklite:: path/to/notebook.ipynb` 可以将已有的 `.ipynb` 文件嵌入文档。构建过程中，Sphinx 会自动收集引用的 Notebook 文件，复制到 JupyterLite 的内容目录中，最终嵌入到生成的 HTML 页面里。支持 Markdown 格式的 Notebook（`.md`），但需要安装可选依赖 jupytext。

**嵌入 REPL 代码**：使用 `.. replite::` 指令可以直接在指令内容中写入 Python 代码块，渲染为一个 REPL 控制台，代码会预加载到 REPL 中。读者可以直接运行、修改这段代码，适合展示短小的交互式示例。支持 `:kernel:` 选项指定内核，以及 `:execute:` 选项控制是否自动执行代码。

**嵌入 Voici 仪表板**：Voici 是基于 JupyterLite 的仪表板渲染工具，可以将 Notebook 转为静态交互式仪表板。使用 `.. voici:: path/to/notebook.ipynb` 指令可以在文档中嵌入 Voici 渲染的仪表板。注意 Voici 是可选依赖，需要单独安装 `voici` 包。

**嵌入 doctest 示例**：`.. try_examples::` 指令是 jupyterlite-sphinx 最独特的功能之一。它能够解析指令内容中的 doctest 格式代码块（以 `>>>` 开头的行），自动转换为 Jupyter Notebook JSON，并嵌入到文档中。这使得文档中的 Python 交互式示例可以直接运行，无需读者复制粘贴到本地环境。

## 构建集成机制

jupyterlite-sphinx 在 Sphinx 构建流程中深度集成了 JupyterLite 的构建过程。当执行 `sphinx-build` 生成 HTML 文档时，扩展会在 `build-finished` 事件中自动调用 `jupyter lite build` 命令，将 JupyterLite 的静态资源（包括 JupyterLab、REPL、Notebook 等应用）构建到输出目录的 `lite/` 子目录下。

构建过程中，扩展会自动：

1. 收集文档中通过指令引用的 Notebook 文件，复制到内容暂存目录（默认为 `_contents/`）。
2. 如果配置了额外内容目录（`jupyterlite_contents`），使用 glob 匹配并复制。
3. 调用 `jupyter lite build` 生成完整的 JupyterLite 站点，默认启用 lab、repl、tree、notebooks、edit、consoles 等应用。
4. 如果安装了 voici，也会自动包含 voici 应用。

构建完成后，输出目录的 `lite/` 下就是一个完整的、自包含的 JupyterLite 部署，可以直接通过静态文件服务器访问，无需后端服务。

## 两种嵌入模式

对于除 `try_examples` 之外的四个指令，jupyterlite-sphinx 支持两种嵌入模式：

**iframe 嵌入模式（默认）**：指令渲染为一个 `<iframe>` 元素，将 JupyterLite 界面直接嵌入到文档页面中。可以通过 `:width:` 和 `:height:` 选项控制 iframe 尺寸。通过 `:prompt:` 选项可以启用懒加载——先显示一个可点击按钮（默认黄色 "Try It Live!"），点击后才加载 iframe 内容，避免页面加载时同时启动多个 JupyterLite 实例。

**新标签页模式**：设置 `:new_tab: True` 选项后，指令不再渲染 iframe，而是渲染一个按钮，点击后在浏览器新标签页中打开 JupyterLite。这适合嵌入较大 Notebook 或仪表板时使用，避免 iframe 内的体验受限。按钮文本可以通过 `:new_tab_button_text:` 选项自定义，也有对应的全局配置项。

## 技术架构

从实现上看，jupyterlite-sphinx 的核心模块是 `jupyterlite_sphinx/jupyterlite_sphinx.py`，它定义了：

- **自定义 docutils 节点**：`_PromptedIframe`、`_LiteIframe`、`_InTab` 等节点类，分别负责渲染带提示按钮的 iframe、普通 iframe、新标签页按钮等 HTML 元素。每个具体指令对应一个 iframe 节点类和一个 tab 节点类（如 `JupyterLiteIframe`/`JupyterLiteTab`）。
- **Sphinx 指令类**：继承自 `SphinxDirective`，负责解析 RST 指令选项、处理 Notebook 文件路径、生成对应的节点。`_LiteDirective` 是处理 Notebook 嵌入的基类，`RepliteDirective` 和 `TryExamplesDirective` 各自独立实现。
- **事件处理函数**：在 Sphinx 的 `config-inited` 和 `build-finished` 等事件钩子上执行初始化和构建逻辑。
- **前端资源**：`jupyterlite_sphinx.js` 处理按钮点击、iframe 懒加载、搜索参数传递、移动端适配等交互逻辑；`jupyterlite_sphinx.css` 提供按钮和 iframe 容器的样式。

## 相关概念

- [安装与基础配置](/concepts/01-installation.md)
- [快速开始](/concepts/02-quick-start.md)
- [指令系统总览](/concepts/03-directive-overview.md)
