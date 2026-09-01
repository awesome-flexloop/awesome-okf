---
type: Concept
title: 快速开始：搭建你的第一个交互文档站点
description: 从安装依赖、创建项目结构、编写配置文件到构建站点的完整快速上手教程
tags: [quickstart, tutorial, setup, build]
difficulty: beginner
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: quickstart
    resource: /references/conf-py-source.md
    title: sphinx-demo README 快速开始
---

## 前置条件

- Python 环境（推荐 3.10+）
- pip 或 uv 包管理器
- 基本的 Sphinx 使用经验

## 第一步：安装依赖

创建项目目录并安装核心依赖：

```bash
pip install jupyterlite-sphinx jupyterlite-pyodide-kernel
```

如果还没有 Sphinx 和主题：

```bash
pip install sphinx pydata-sphinx-theme myst-nb
```

> Pyodide 内核通过 `jupyterlite-pyodide-kernel` 包提供。如需 Xeus 内核，安装 `jupyterlite-xeus` 替代。

## 第二步：创建目录结构

使用 `sphinx-quickstart` 或手动创建以下最小结构：

```
my-docs/
├── docs/
│   ├── Makefile
│   └── source/
│       ├── _static/
│       ├── conf.py
│       └── index.md
└── requirements.txt
```

## 第三步：编写 conf.py

最小配置示例：

```python
project = "My Interactive Docs"
copyright = "2025, Your Name"
author = "Your Name"

extensions = [
    "jupyterlite_sphinx",    # JupyterLite 集成
    "myst_nb",               # Markdown + Notebook 支持
]

# 启用 JupyterLite Notebook 内容
myst_enable_extensions = []

# HTML 主题
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

# JupyterLite 配置
jupyterlite_contents = []  # 可选：预装的 Notebook 文件
```

> **关键**：必须将 `jupyterlite_sphinx` 添加到 `extensions` 列表中，否则 JupyterLite 指令和 TryExamples 功能不会生效。

## 第四步：编写文档首页（index.md）

````markdown
# 我的交互文档

欢迎！点击按钮在浏览器中运行代码：

```{jupyterlite}
:width: 100%
:height: 500px
```
````

这个 `{jupyterlite}` 指令会在页面中嵌入一个可操作的 JupyterLab 环境。

## 第五步：构建站点

```bash
cd docs
make html
```

构建产物在 `build/html/` 目录。首次构建会下载 Pyodide kernel 和 JupyterLite 资源，需要等待较长时间。

## 第六步：预览站点

```bash
cd build/html
python -m http.server 8000
```

打开浏览器访问 `http://localhost:8000`，即可看到嵌入的 JupyterLite 环境。

> **注意**：必须通过 HTTP 服务器访问，不能直接用 `file://` 协议打开 HTML 文件，否则浏览器的安全策略会阻止 WebAssembly 加载。

## 常见问题

### 构建时间很长

首次构建 JupyterLite 需要下载 Pyodide runtime（约 20MB+），后续构建会使用缓存。可以通过设置 `jupyterlite_silence = False` 查看构建进度。

### Notebook 中无法安装包

在 Pyodide 内核中，使用 `piplite` 而非 `pip` 安装纯 Python 包：

```python
import piplite
await piplite.install("numpy")
```

### 构建后页面空白

检查浏览器控制台是否有 CORS 错误——确保通过 HTTP 服务器访问而非 file:// 协议。

## 下一步

- 阅读 [03-sphinx-conf](03-sphinx-conf.md) 了解更多配置选项
- 阅读 [06-try-examples](06-try-examples.md) 为 docstring 示例添加"Try it online"按钮
- 参考 [/examples/01-minimal-site.md](../examples/01-minimal-site.md) 查看完整的最小站点配置

## 相关内容

- [00-introduction](00-introduction.md)
- [03-sphinx-conf](03-sphinx-conf.md)
- [/examples/01-minimal-site.md](../examples/01-minimal-site.md)
- [/examples/02-pyodide-setup.md](../examples/02-pyodide-setup.md)
