---
type: concept
title: "Sphinx Docker 镜像项目介绍"
description: "了解 sphinx-docker-images 项目是什么、提供哪些镜像、解决什么问题"
tags: [sphinx, docker, introduction, documentation]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: readme, resource: "/references/readme-source.md", title: "README 原文与使用说明" }
---

# Sphinx Docker 镜像项目介绍

sphinx-docker-images 是 [Sphinx](https://www.sphinx-doc.org/) 官方维护的 Docker 镜像项目，为文档构建提供开箱即用的容器化环境。

## 项目是什么

Sphinx 是 Python 生态最主流的文档生成器，但搭建完整的文档构建环境（特别是 LaTeX/PDF 输出）需要安装大量系统依赖和 TeXLive 包，过程繁琐且容易出错。sphinx-docker-images 项目通过预配置的 Docker 镜像，让用户无需手动配置环境即可一键构建 Sphinx 文档。

## 提供的镜像

项目提供三个 Docker 镜像：

| 镜像 | Docker Hub | GHCR | 用途 | 体积 |
|------|-----------|------|------|------|
| `sphinx` | `sphinxdoc/sphinx` | `ghcr.io/sphinx-doc/sphinx` | HTML/EPUB 构建 | 精简（~200MB） |
| `sphinx-latexpdf` | `sphinxdoc/sphinx-latexpdf` | `ghcr.io/sphinx-doc/sphinx-latexpdf` | LaTeX/PDF 构建 | >2GiB |
| `docker-ci` | `sphinxdoc/docker-ci` | `ghcr.io/sphinx-doc/sphinx-ci` | Sphinx 自身 CI 测试 | 较大 |

> **注意**：`sphinx-latexpdf` 镜像包含完整的 TeXLive 发行版，体积超过 2GiB。如果只需要构建 HTML 或 EPUB，使用基础的 `sphinx` 镜像即可。[^1]

## 镜像版本

- 当前版本：**Sphinx 8.2.3**
- 许可证：BSD-2-Clause
- 支持架构：linux/amd64、linux/arm64（Apple Silicon 原生支持）
- 基础镜像：`python:slim`（sphinx/latexpdf）、`ubuntu:24.04`（ci）

## 核心特性

- **零配置**：预装好 Sphinx 和所有系统依赖，拉取即用
- **多输出格式**：支持 HTML、EPUB、PDF（LaTeX）等多种输出
- **双 Registry**：同时发布到 Docker Hub 和 GitHub Container Registry
- **多架构**：支持 amd64 和 arm64 双平台
- **可扩展**：可作为基础镜像自定义安装额外依赖
- **CI 就绪**：提供专门的 CI 测试镜像

## 适用场景

- 本地不想安装 Python/LaTeX 环境，只想快速构建文档
- CI/CD 流水线中需要一致的文档构建环境
- 多平台开发（Windows/macOS/Linux）需要统一构建环境
- 需要 CJK（中日韩）语言支持的 PDF 输出

## 相关概念

- [快速上手](/concepts/01-getting-started.md)：5 分钟内用 Docker 构建第一份 Sphinx 文档
- [三镜像架构解析](/concepts/02-image-architecture.md)：理解三个镜像的分工与设计思路
- [Base 镜像详解](/concepts/03-base-image.md)：深入了解基础镜像的构成

[^1]: 参考来源
