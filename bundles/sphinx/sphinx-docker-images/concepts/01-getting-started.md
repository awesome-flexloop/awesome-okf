---
type: concept
title: "5 分钟快速上手"
description: "从零开始：拉取镜像、创建项目、构建 HTML 和 PDF 文档的完整入门教程"
tags: [sphinx, docker, getting-started, quickstart]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: readme, resource: "/references/readme-source.md", title: "README 原文与使用说明" }
  - { id: base, resource: "/references/dockerfile-base.md", title: "Base 镜像 Dockerfile 源码" }
---

# 5 分钟快速上手

本教程带你从零开始，使用 Docker 构建你的第一份 Sphinx 文档。

## 前置条件

- 已安装 [Docker](https://docs.docker.com/get-docker/)（Docker Desktop 或 Docker Engine）
- 终端可用（PowerShell、bash、zsh 等）
- 无需安装 Python 或 Sphinx

## 步骤 1：创建项目目录

```bash
# 创建文档目录
mkdir my-docs
cd my-docs
```

## 步骤 2：初始化 Sphinx 项目

使用 `sphinx-quickstart` 交互式创建项目：

```bash
docker run -it --rm -v "$(pwd):/docs" sphinxdoc/sphinx sphinx-quickstart
```

**参数说明**：
- `-it`：交互式终端（quickstart 需要回答问题）
- `--rm`：退出后自动删除容器
- `-v "$(pwd):/docs"`：将当前目录挂载到容器的 `/docs`（工作目录）
- `sphinxdoc/sphinx`：使用基础镜像
- `sphinx-quickstart`：执行初始化命令

按提示输入项目名称、作者名、语言等信息。完成后当前目录会生成 `conf.py`、`index.rst`、`Makefile` 等文件。

## 步骤 3：构建 HTML 文档

```bash
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx sphinx-build -M html . _build
```

构建完成后，打开 `_build/html/index.html` 即可预览文档。

**Windows PowerShell 用户**：将 `$(pwd)` 替换为 `${PWD}` 或使用绝对路径：
```powershell
docker run --rm -v "${PWD}:/docs" sphinxdoc/sphinx sphinx-build -M html . _build
```

## 步骤 4：构建 EPUB 电子书

```bash
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx sphinx-build -M epub . _build
```

EPUB 文件输出到 `_build/epub/` 目录。

## 步骤 5：构建 PDF 文档

PDF 构建需要使用 `sphinx-latexpdf` 镜像（体积较大，首次拉取需等待）：

```bash
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx-latexpdf sphinx-build -M latexpdf . _build
```

PDF 文件输出到 `_build/latex/` 目录。

> **提示**：latexpdf 镜像内置了 CJK 语言包（中文、日文、韩文），构建中文 PDF 无需额外安装字体。

## 常用命令速查

| 目的 | 命令 |
|------|------|
| 初始化项目 | `docker run -it --rm -v "$(pwd):/docs" sphinxdoc/sphinx sphinx-quickstart` |
| 构建 HTML | `docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx sphinx-build -M html . _build` |
| 构建 EPUB | `docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx sphinx-build -M epub . _build` |
| 构建 PDF | `docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx-latexpdf sphinx-build -M latexpdf . _build` |
| 清理构建 | `docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx make clean` |

## 从 GHCR 拉取（可选）

如果 Docker Hub 访问缓慢，可以从 GitHub Container Registry 拉取：

```bash
# HTML 构建
docker run --rm -v "$(pwd):/docs" ghcr.io/sphinx-doc/sphinx sphinx-build -M html . _build

# PDF 构建
docker run --rm -v "$(pwd):/docs" ghcr.io/sphinx-doc/sphinx-latexpdf sphinx-build -M latexpdf . _build
```

## 相关概念

- [三镜像架构解析](/concepts/02-image-architecture.md)：理解三个镜像的分工
- [Base 镜像详解](/concepts/03-base-image.md)：了解基础镜像的具体构成
- [基础 HTML 构建示例](/examples/01-basic-html-build.md)：更详细的构建示例
