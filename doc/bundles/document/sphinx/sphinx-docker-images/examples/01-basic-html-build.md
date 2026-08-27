---
type: example
title: "基础 HTML 文档构建"
description: "从零开始：使用 sphinxdoc/sphinx 镜像初始化项目、编写文档、构建 HTML 的完整步骤"
tags: [example, html, build, getting-started]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: readme, resource: "/references/readme-source.md", title: "README 原文与使用说明" }
  - { id: base, resource: "/references/dockerfile-base.md", title: "Base 镜像 Dockerfile 源码" }
---

# 基础 HTML 文档构建

本示例完整演示如何使用 Docker 镜像创建一个 Sphinx 项目并构建 HTML 文档。

## 前置条件

- 已安装 Docker
- 终端可用

## 步骤 1：创建项目目录

```bash
mkdir my-sphinx-docs
cd my-sphinx-docs
```

## 步骤 2：初始化项目

```bash
docker run -it --rm -v "$(pwd):/docs" sphinxdoc/sphinx sphinx-quickstart
```

按提示输入：
- **Root path**: 直接回车（使用当前目录）
- **Separate source and build directories**: 推荐选 `y`（分离源码和构建目录）
- **Name prefix**: 直接回车（不需要模板前缀）
- **Project name**: 输入项目名，如 `My Docs`
- **Author name**: 输入作者名
- **Project release**: 输入版本号，如 `1.0.0`
- **Project language**: 输入 `zh_CN`（中文）或 `en`（英文）

完成后目录结构：
```
my-sphinx-docs/
├── Makefile
├── build/          # 如果选择分离目录
├── make.bat
└── source/
    ├── conf.py
    ├── index.rst
    ├── _static/
    └── _templates/
```

> 如果选择不分离目录，conf.py 和 index.rst 直接在根目录。

## 步骤 3：编写内容

编辑 `source/index.rst`（或根目录的 `index.rst`）：

```rst
.. My Docs documentation master file

欢迎来到 My Docs 的文档！
============================

.. toctree::
   :maxdepth: 2
   :caption: 目录:

   install
   usage

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

创建 `source/install.rst`：
```rst
安装指南
========

系统要求
--------

- Python 3.10+
- Docker（推荐）

使用 Docker 安装
----------------

.. code-block:: bash

   docker pull sphinxdoc/sphinx:8.2.3
```

创建 `source/usage.rst`：
```rst
使用指南
========

构建文档
--------

.. code-block:: bash

   docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx \
     sphinx-build -M html . _build
```

## 步骤 4：构建 HTML

如果选择了分离源码和构建目录（source/ 和 build/）：

```bash
cd source
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx \
  sphinx-build -M html . _build
```

如果没有分离目录：

```bash
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx \
  sphinx-build -M html . _build
```

Windows PowerShell 用户：
```powershell
docker run --rm -v "${PWD}:/docs" sphinxdoc/sphinx `
  sphinx-build -M html . _build
```

## 步骤 5：预览文档

构建成功后，HTML 文件输出到 `_build/html/`（或 `build/html/`）目录。用浏览器打开 `_build/html/index.html` 即可预览。

如果需要本地预览服务器，可以使用 Python：
```bash
# 在宿主机上（非 Docker 内）
cd _build/html
python3 -m http.server 8000
# 然后访问 http://localhost:8000
```

或者使用 sphinx-autobuild 实现自动重建（需自定义镜像安装该包）：
```bash
docker run --rm -v "$(pwd):/docs" -p 8000:8000 sphinxdoc/sphinx \
  bash -c "pip install --no-cache-dir sphinx-autobuild && \
           sphinx-autobuild --host 0.0.0.0 --port 8000 . _build/html"
```

## 常见问题排查

**Q: 构建报错 `cannot import name 'contextfunction'`**

这是 Jinja2 版本兼容问题。使用自定义镜像锁定版本：
```dockerfile
FROM sphinxdoc/sphinx
RUN pip install --no-cache-dir Jinja2<3.1
```

**Q: graphviz 指令不工作**

确保你的文档 conf.py 中启用了 graphviz 扩展：
```python
extensions = ['sphinx.ext.graphviz']
```

## 相关概念

- [5 分钟快速上手](../concepts/01-getting-started.md)：快速入门指南
- [Base 镜像详解](../concepts/03-base-image.md)：了解镜像中预装的工具
- [自定义镜像扩展](03-custom-image.md)：安装额外的 Sphinx 扩展
