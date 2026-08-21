---
type: "concept"
title: "5分钟快速上手"
description: "安装Sphinx、sphinx-quickstart初始化、sphinx-build构建、conf.py配置基础、Python API快速体验"
tags: [getting-started, installation, quickstart, CLI]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: pyproject
    resource: pyproject.toml
    title: "Sphinx pyproject.toml CLI入口点"
  - id: cmd-build
    resource: sphinx/cmd/build.py
    title: "sphinx-build命令行入口"
  - id: cmd-quickstart
    resource: sphinx/cmd/quickstart.py
    title: "sphinx-quickstart"
---

# 5分钟快速上手

## 安装 Sphinx

Sphinx 要求 Python ≥ 3.12 [F-003]，使用 pip 安装：

```bash
pip install sphinx
```

安装后可获得三个命令行工具 [F-007]：

| 命令 | 入口模块 | 用途 |
|------|---------|------|
| `sphinx-build` | `sphinx.cmd.build:main` | 从源文件构建文档 |
| `sphinx-quickstart` | `sphinx.cmd.quickstart:main` | 交互式初始化Sphinx项目 |
| `sphinx-apidoc` | `sphinx.ext.apidoc:main` | 从Python包自动生成API文档骨架 |

此外 `sphinx-autogen`（`sphinx.ext.autosummary.generate:main`）由 autosummary 扩展提供。

验证安装：

```bash
sphinx-build --version
# 输出：sphinx-build 9.1.1
```

## 使用 sphinx-quickstart 初始化项目

```bash
mkdir mydocs && cd mydocs
sphinx-quickstart
```

`sphinx-quickstart` 会交互式询问项目名称、作者、版本等信息，然后生成以下目录结构：

```
mydocs/
├── conf.py          # Sphinx配置文件
├── index.rst        # 主文档（toctree入口）
├── Makefile         # make命令（Unix）
└── make.bat         # make命令（Windows）
```

## 编写第一个文档

编辑 `index.rst`：

```rst
.. My Documentation master file

Welcome to My Documentation
===========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   intro

Introduction
============

This is my first Sphinx document.

.. note::

   This is a note directive.

.. code-block:: python

   def hello():
       print("Hello, Sphinx!")
```

创建 `intro.rst` 并在 toctree 中引用它。

## 使用 sphinx-build 构建文档

```bash
# HTML输出
sphinx-build -b html . _build/html

# 指定源目录和输出目录
sphinx-build -b html sourcedir outputdir

# 只构建特定文件
sphinx-build -b html . _build/html intro.rst

# 全量重建（清除缓存）
sphinx-build -b html -E . _build/html

# 将警告视为错误
sphinx-build -b html -W . _build/html

# 并行构建（4个进程）
sphinx-build -b html -j 4 . _build/html
```

`-b` 参数指定构建器名称（默认 `html`）。常用选项：

| 选项 | 说明 |
|------|------|
| `-b <builder>` | 选择构建器（html/latex/text/epub3/linkcheck等） |
| `-E` | 不使用缓存，全量重建 |
| `-j N` | N个并行构建进程 |
| `-W` | 警告转为错误 |
| `-c <dir>` | 指定配置文件目录 |
| `-D <setting=value>` | 覆盖配置项 |
| `-t <tag>` | 设置标签（用于only指令） |
| `-v` / `-vv` | 增加详细程度 |

构建完成后，用浏览器打开 `_build/html/index.html` 查看结果。

## conf.py 配置基础

`conf.py` 是一个 Python 文件，Sphinx 在构建时执行它来加载配置。最小配置：

```python
# conf.py
project = 'My Documentation'
copyright = '2026, Your Name'
author = 'Your Name'
release = '0.1.0'

# 扩展模块
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

# 主题
html_theme = 'alabaster'
```

常用配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|-------|
| `project` | 项目名称 | - |
| `author` | 作者名 | - |
| `release` | 完整版本号 | - |
| `version` | 短版本号 | release值 |
| `extensions` | 启用的扩展列表 | `[]` |
| `source_suffix` | 源文件后缀 | `.rst` |
| `master_doc` / `root_doc` | 主文档名 | `'index'` |
| `html_theme` | HTML主题 | `'alabaster'` |
| `language` | 文档语言 | `None`（英文） |
| `exclude_patterns` | 排除的文件模式 | `[]` |

## 使用 Python API 构建文档

除了命令行，Sphinx 也提供 Python API [F-008]：

```python
from sphinx.application import Sphinx

# 创建Sphinx应用实例
app = Sphinx(
    srcdir='./source',        # 源文件目录
    confdir='./source',       # 配置文件目录
    outdir='./build/html',    # 输出目录
    doctreedir='./build/.doctrees',  # doctree缓存目录
    buildername='html',       # 构建器名称
    freshenv=True,            # 清除缓存环境
    warningiserror=False,     # 警告不转错误
    verbosity=0,              # 详细程度
    parallel=0,               # 并行进程数
)

# 执行构建
app.build()

# 构建完成后检查状态码
if app.statuscode == 0:
    print("Build succeeded!")
else:
    print(f"Build finished with problems (status code: {app.statuscode})")
```

也可以通过 `app.connect()` 在构建过程中插入自定义逻辑：

```python
def on_build_finished(app, exception):
    if exception is None:
        print("Build finished successfully!")

app.connect('build-finished', on_build_finished)
app.build()
```

## 使用 Makefile 便捷构建

`sphinx-quickstart` 生成的 `Makefile` 提供便捷命令：

```bash
make html       # 构建HTML
make clean      # 清理构建输出
make latexpdf   # 构建LaTeX并编译为PDF
make epub       # 构建EPUB
make linkcheck  # 检查链接
make help       # 查看所有可用目标
```

## 相关概念

- [Sphinx 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [Sphinx应用类](03-application-class.md)
