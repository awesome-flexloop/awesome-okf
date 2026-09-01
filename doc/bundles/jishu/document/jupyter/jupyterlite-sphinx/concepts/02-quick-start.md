---
type: Concept
title: 快速开始
description: 5分钟内完成第一个嵌入式 JupyterLite 示例
tags: [quickstart, getting-started, hello-world]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
---

本节将引导你在5分钟内完成第一个嵌入式 JupyterLite 示例。你将学会安装扩展、配置 Sphinx、在 RST 文件中使用 `jupyterlite` 指令，并通过 `sphinx-build` 构建文档查看效果。

## 第 1 步：安装扩展

首先确保你的环境已安装 Python 3.10+，然后通过 pip 安装 jupyterlite-sphinx：

```bash
pip install jupyterlite-sphinx
```

这会自动安装 Sphinx、jupyterlite-core 等核心依赖。安装过程可能需要1-2分钟，因为 jupyterlite-core 会拉取 JupyterLite 的静态资源。

## 第 2 步：创建 Sphinx 项目（如已有项目可跳过）

如果你还没有 Sphinx 项目，可以快速创建一个：

```bash
# 创建项目目录
mkdir my-jupyterlite-docs
cd my-jupyterlite-docs

# 使用 sphinx-quickstart 初始化
sphinx-quickstart
```

在 `sphinx-quickstart` 的交互式向导中，按提示填写项目名称、作者等信息，其他选项保持默认即可。完成后目录结构大致如下：

```
my-jupyterlite-docs/
├── _build/          # 构建输出目录（自动生成）
├── _static/         # 静态文件
├── _templates/      # 模板文件
├── conf.py          # Sphinx 配置文件
├── index.rst        # 文档入口
└── make.bat / Makefile
```

## 第 3 步：配置 conf.py

打开 `conf.py` 文件，找到 `extensions` 配置项，将 `jupyterlite_sphinx` 添加进去。最简配置如下：

```python
# conf.py

# -- Project information -----------------------------------------------------
project = 'My JupyterLite Docs'
copyright = '2026, Your Name'
author = 'Your Name'
release = '0.1'

# -- General configuration ---------------------------------------------------
extensions = [
    'jupyterlite_sphinx',
]

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
```

就是这么简单——不需要任何其他 JupyterLite 相关配置。扩展会自动处理 JupyterLite 的构建、静态资源复制和指令注册。

## 第 4 步：在 RST 文件中嵌入 JupyterLite

打开 `index.rst`（或你自己创建的 RST 文件），在文档内容中添加 `.. jupyterlite::` 指令。

### 示例：嵌入空白 JupyterLab

这是最简单的用法——嵌入一个空白的 JupyterLab 环境，读者可以在其中自由创建和运行 Notebook：

```rst
.. jupyterlite-sphinx 快速开始
   ==========================

欢迎来到 jupyterlite-sphinx 快速开始！

点击下方按钮，在浏览器中启动 JupyterLab：

.. jupyterlite::
   :width: 100%
   :height: 600px
   :prompt: 启动 JupyterLab
```

这里使用了三个选项：

- `:width: 100%`：iframe 宽度占满父容器
- `:height: 600px`：iframe 高度为 600 像素
- `:prompt: 启动 JupyterLab`：显示一个可点击按钮而非直接加载 iframe。按钮上显示"启动 JupyterLab"文本，读者点击后才加载 JupyterLite 实例（懒加载模式）

### 示例：嵌入 REPL 代码

你也可以使用 `.. replite::` 指令嵌入一段预加载的 Python 代码：

```rst
试试这段代码：

.. replite::
   :width: 100%
   :height: 400px
   :prompt: 运行示例

   print("Hello, JupyterLite!")
   for i in range(5):
       print(f"Count: {i}")
```

## 第 5 步：构建文档

在项目目录下执行 `sphinx-build` 命令构建 HTML 文档：

```bash
sphinx-build -b html . _build/html
```

如果你使用了 sphinx-quickstart 生成的 Makefile，也可以：

```bash
make html
```

**构建过程中发生了什么？**

当 `sphinx-build` 执行时，jupyterlite-sphinx 会在 `build-finished` 事件中自动执行以下操作：

1. **清空内容目录**：删除并重建 `_contents/` 目录（Sphinx 源目录下的暂存目录）
2. **收集 Notebook 文件**：将文档中指令引用的 Notebook 文件复制到内容目录
3. **执行 JupyterLite 构建**：调用 `jupyter lite build` 命令，构建完整的 JupyterLite 静态站点到输出目录的 `lite/` 子目录下
4. **复制静态资源**：将 `jupyterlite_sphinx.css` 和 `jupyterlite_sphinx.js` 复制到输出目录的 `_static/` 下

首次构建时 `jupyter lite build` 可能需要较长时间（30秒到数分钟不等），因为它需要生成 JupyterLab、REPL 等应用的前端资源。后续构建如果内容没有变化，会利用缓存加速。

构建成功后，你会看到类似如下输出（`jupyterlite_silence=True` 时 JupyterLite 的构建输出会被静默，只有失败时才会打印错误）：

```
building [mo]: targets for 0 po files that are out of date
building [html]: targets for 1 source files that are out of date
updating environment: [new config] 1 added, 0 changed, 0 removed
looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
writing output... [100%] index
generating indices... genindex done
writing additional pages... search done
copying static files... done
copying extra files... done
dumping search index in English (code: en)... done
dumping object inventory... done
build succeeded.
```

## 第 6 步：查看效果

构建完成后，用浏览器打开生成的 HTML 文件。最简单的方式是使用 Python 内置的 HTTP 服务器：

```bash
cd _build/html
python -m http.server 8000
```

然后在浏览器中访问 `http://localhost:8000`。

你会看到文档中显示一个按钮（文本为"启动 JupyterLab"或你设置的 prompt 文本，默认黄色背景）。点击按钮后，按钮区域会出现加载动画，随后 JupyterLab 界面会以 iframe 形式嵌入到页面中。你可以在其中创建 Notebook、编写 Python 代码并运行——一切都在浏览器中完成，无需安装 Python 或 Jupyter。

## 常见问题

### 构建时提示 jupyterlite 命令找不到

确保 jupyterlite-core 已正确安装：

```bash
pip install "jupyterlite-core>=0.2,<0.9"
```

安装后确认 `jupyter` 命令可用：

```bash
jupyter lite --version
```

### iframe 显示空白或加载失败

检查浏览器控制台是否有跨域（CORS）错误。直接用 `file://` 协议打开 HTML 文件可能导致 iframe 加载问题，请使用 HTTP 服务器（如 `python -m http.server`）访问。

### 构建时间过长

首次构建需要下载和生成 JupyterLite 前端资源，这是正常现象。后续构建会缓存结果。如果需要更详细的构建输出以排查问题，可以临时设置：

```python
jupyterlite_silence = False
```

这样可以在构建时看到 `jupyter lite build` 的详细输出。

## 下一步

- 了解五个指令的详细对比：[指令系统总览](03-directive-overview.md)
- 学习嵌入 Notebook 文件的方法
- 探索 `:new_tab:` 模式和搜索参数传递等高级选项

## 相关概念

- [jupyterlite-sphinx 是什么](00-introduction.md)
- [安装与基础配置](01-installation.md)
- [指令系统总览](03-directive-overview.md)
