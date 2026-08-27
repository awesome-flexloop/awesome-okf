---
type: "concept"
title: 快速开始
description: 安装Sphinx、使用sphinx-quickstart创建项目、sphinx-build命令用法、conf.py配置文件概览。
tags: [sphinx, getting-started, installation, quickstart]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /spec/facts.md
    title: Sphinx源码事实清单
  - id: application-api
    resource: /references/application-api.md
    title: Sphinx应用类API参考
---
# 快速开始

## 安装

使用 pip 安装 Sphinx：

```bash
pip install sphinx
```

验证安装：

```bash
sphinx-build --version
# sphinx-build 9.1.1
```

## 创建项目：sphinx-quickstart

Sphinx 提供交互式项目初始化工具：

```bash
sphinx-quickstart docs
```

这会在 `docs/` 目录下创建以下文件结构：

```
docs/
├── build/           # 构建输出目录（生成）
├── source/          # 源文件目录
│   ├── _static/     # 静态资源（图片、CSS等）
│   ├── _templates/  # 自定义模板
│   ├── conf.py      # 配置文件（核心）
│   └── index.rst    # 根文档
└── Makefile         # make命令入口
```

### 非交互式创建

```bash
sphinx-quickstart docs --no-sep -p "My Project" -a "Author Name" -v "0.1" -l en
```

关键参数：
- `--no-sep`：源文件和构建目录不分离
- `-p`：项目名
- `-a`：作者名
- `-v`：版本号
- `-l`：语言（如 `en`、`zh_CN`）

## 构建文档：sphinx-build

基本构建命令：

```bash
sphinx-build -b html <sourcedir> <outdir>
```

参数说明（对应 [F-005](../spec/facts.md) Sphinx.__init__ 参数）：

| 参数 | 说明 | 对应Sphinx参数 |
|------|------|------|
| `-b <builder>` | 指定构建器（html/latex/epub/text/man等） | `buildername` |
| `-c <confdir>` | 指定配置目录（默认同源目录） | `confdir` |
| `-d <doctreedir>` | 指定doctree缓存目录 | `doctreedir` |
| `-E` | 不使用缓存，全量重建（freshenv=True） | `freshenv` |
| `-W` | 警告视为错误 | `warningiserror` |
| `-j N` | N个并行构建任务 | `parallel` |
| `-v` | 详细输出 | `verbosity` |
| `-D <key>=<value>` | 覆盖配置项 | `confoverrides` |
| `-t <tag>` | 添加标签 | `tags` |

### 常用构建示例

```bash
# 构建HTML
sphinx-build -b html docs/source docs/build/html

# 构建HTML（全量重建）
sphinx-build -b html -E docs/source docs/build/html

# 构建PDF（需LaTeX环境）
sphinx-build -b latex docs/source docs/build/latex
cd docs/build/latex && make

# 构建ePub
sphinx-build -b epub docs/source docs/build/epub

# 并行构建（4线程）
sphinx-build -b html -j 4 docs/source docs/build/html

# 检查链接
sphinx-build -b linkcheck docs/source docs/build/linkcheck
```

### 使用Makefile

quickstart 生成的 Makefile 提供便捷命令：

```bash
cd docs
make html          # 构建HTML
make clean         # 清理构建输出
make html SPHINXOPTS="-E -j 4"  # 带参数
```

## 配置文件 conf.py

`conf.py` 是 Sphinx 项目的核心配置文件（见 [F-032](../spec/facts.md)），它本身是一个 Python 文件，在 Sphinx 初始化时被执行。

### 基本配置项

```python
# 项目信息
project = 'My Project'
copyright = '2024, Author Name'
author = 'Author Name'
release = '0.1.0'

# 通用配置
extensions = [
    'sphinx.ext.autodoc',      # 自动API文档
    'sphinx.ext.napoleon',     # NumPy/Google风格docstring
    'sphinx.ext.viewcode',     # 源码链接
    'sphinx.ext.intersphinx',  # 跨项目引用
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML输出配置
html_theme = 'alabaster'
html_static_path = ['_static']

# 语言
language = 'en'
```

### conf.py 作为扩展

`conf.py` 本身可以作为一个 Sphinx 扩展——如果定义了 `setup(app)` 函数，Sphinx 会自动调用它（见 [F-014](../spec/facts.md) 初始化流程中config.setup的处理）：

```python
def setup(app):
    app.add_config_value('my_setting', 'default', 'env')
    app.connect('build-finished', my_handler)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

这使得在 conf.py 中也能注册自定义组件和事件监听。

## 编写第一个文档

在 `source/index.rst` 中：

```rst
Welcome to My Project's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   usage
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

创建 `source/install.rst`：

```rst
Installation
============

To install My Project::

   pip install my-project
```

然后运行 `make html`，在 `build/html/index.html` 查看输出。

## 相关概念

- [00-简介](00-introduction.md) — Sphinx是什么
- 02-应用类 — Sphinx初始化流程详解
- 03-配置系统 — conf.py配置系统深入
- 07-扩展开发 — 编写自定义扩展
