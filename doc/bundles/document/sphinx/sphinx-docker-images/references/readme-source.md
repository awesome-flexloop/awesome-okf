---
type: reference
title: "README 原文与使用说明"
description: "sphinx-docker-images 项目 README.rst 原文与中文使用说明"
tags: [readme, usage, docker, sphinx]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: src-readme, resource: "external/libs/docs/sphinx-docker-images/README.rst", title: "README.rst 源码" }
---

# README 原文与使用说明

## README.rst 原文

```rst
=========================
Docker Images for Sphinx_
=========================

Images
======

- ``sphinx`` --
  Main Sphinx image --
  `Docker Hub <https://hub.docker.com/r/sphinxdoc/sphinx>`__,
  `GitHub Container Registry <https://ghcr.io/sphinx-doc/sphinx>`__
- ``sphinx-latexpdf`` --
  Image for LaTeX --
  `Docker Hub <https://hub.docker.com/r/sphinxdoc/sphinx-latexpdf>`__,
  `GitHub Container Registry <https://ghcr.io/sphinx-doc/sphinx-latexpdf>`__

.. note:: The ``sphinx-latexpdf`` container contains TeXLive images,
          meaning it is very large (over 2GiB).

Usage
=====

Create a Sphinx project:

.. code:: bash

   $ docker run -it --rm -v /path/to/document:/docs sphinxdoc/sphinx sphinx-quickstart

Build HTML document:

.. code:: bash

   $ docker run --rm -v /path/to/document:/docs sphinxdoc/sphinx sphinx-build -M html . _build

Build EPUB document:

.. code:: bash

   $ docker run --rm -v /path/to/document:/docs sphinxdoc/sphinx sphinx-build -M epub . _build

Build PDF document:

.. code:: bash

   $ docker run --rm -v /path/to/document:/docs sphinxdoc/sphinx-latexpdf sphinx-build -M latexpdf . _build

Tips
====

To install additional dependencies, use ``sphinxdoc/sphinx`` as a base image:

.. code:: dockerfile

   # in your Dockerfile
   FROM sphinxdoc/sphinx

   WORKDIR /docs
   ADD requirements.txt /docs
   RUN python3 -m pip install -r requirements.txt

Sphinx CI Docker Image
======================

The Docker image used for testing Sphinx_ in continuous integration is defined
in the ``ci`` directory.

.. _Sphinx: http://www.sphinx-doc.org/
```

## 官方使用命令汇总

| 场景 | 命令 | 镜像 |
|------|------|------|
| 创建项目 | `docker run -it --rm -v /path/to/docs:/docs sphinxdoc/sphinx sphinx-quickstart` | sphinx |
| 构建 HTML | `docker run --rm -v /path/to/docs:/docs sphinxdoc/sphinx sphinx-build -M html . _build` | sphinx |
| 构建 EPUB | `docker run --rm -v /path/to/docs:/docs sphinxdoc/sphinx sphinx-build -M epub . _build` | sphinx |
| 构建 PDF | `docker run --rm -v /path/to/docs:/docs sphinxdoc/sphinx-latexpdf sphinx-build -M latexpdf . _build` | latexpdf |
| 自定义扩展 | FROM sphinxdoc/sphinx + pip install -r requirements.txt | 自定义 |

## Docker 命令参数说明

| 参数 | 说明 |
|------|------|
| `-it` | 交互式终端（quickstart 需要交互输入） |
| `--rm` | 容器退出后自动删除 |
| `-v /path/to/document:/docs` | 将本地文档目录挂载到容器 /docs |
| `sphinxdoc/sphinx` | 使用的镜像名 |
| `sphinx-build -M html . _build` | 在容器内执行的命令 |
