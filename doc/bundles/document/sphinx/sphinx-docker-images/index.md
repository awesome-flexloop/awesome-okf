---
okf_version: "0.2"
type: index
title: "Sphinx Docker 镜像教程"
description: "Sphinx 官方 Docker 镜像（sphinxdoc/sphinx）系统化学习教程——从快速上手到自定义扩展、CI 集成的完整指南"
tags: [sphinx, docker, documentation, latex, pdf, ci-cd]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: src-readme, resource: "external/libs/docs/sphinx-docker-images/README.rst", title: "项目 README" }
  - { id: src-base, resource: "external/libs/docs/sphinx-docker-images/base/Dockerfile", title: "base/Dockerfile" }
  - { id: src-latex, resource: "external/libs/docs/sphinx-docker-images/latexpdf/Dockerfile", title: "latexpdf/Dockerfile" }
  - { id: src-ci, resource: "external/libs/docs/sphinx-docker-images/ci/Dockerfile", title: "ci/Dockerfile" }
  - { id: src-build, resource: "external/libs/docs/sphinx-docker-images/.github/workflows/build.yml", title: "版本发布工作流" }
  - { id: src-build-ci, resource: "external/libs/docs/sphinx-docker-images/.github/workflows/build-ci.yml", title: "CI 镜像工作流" }
---

# Sphinx Docker 镜像教程

> 基于 sphinx-docker-images 源码（BSD-2-Clause）的系统化学习教程

sphinx-docker-images 是 [Sphinx](https://www.sphinx-doc.org/) 官方维护的 Docker 镜像项目，为文档构建提供开箱即用的容器化环境。无需手动安装 Python、LaTeX 和各种系统依赖，一条命令即可构建 HTML、EPUB、PDF 文档。

## 快速导航

### 入门

| 文档 | 说明 |
|------|------|
| [项目介绍](concepts/00-introduction.md) | 是什么、提供哪些镜像、适用场景 |
| [5 分钟快速上手](concepts/01-getting-started.md) | 拉取镜像→创建项目→构建文档 |

### 核心架构

| 文档 | 说明 |
|------|------|
| [三镜像架构解析](concepts/02-image-architecture.md) | sphinx/sphinx-latexpdf/docker-ci 的分层设计与选型 |
| [Base 镜像详解](concepts/03-base-image.md) | 逐层 Dockerfile 解析、体积优化策略 |
| [LaTeX/PDF 镜像详解](concepts/04-latexpdf-image.md) | TeXLive 包选择、CJK 中文支持 |
| [CI 测试镜像详解](concepts/05-ci-image.md) | Ubuntu 全工具链 CI 环境设计 |

### 高级主题

| 文档 | 说明 |
|------|------|
| [构建流水线详解](concepts/06-build-pipeline.md) | GitHub Actions 双工作流、多架构、双 Registry |
| [自定义扩展与最佳实践](concepts/07-customization.md) | 自定义镜像、docker-compose、性能优化 |

### 实战示例

| 示例 | 说明 |
|------|------|
| [基础 HTML 文档构建](examples/01-basic-html-build.md) | 初始化项目→编写内容→构建 HTML 完整流程 |
| [PDF 文档构建（含中文）](examples/02-pdf-build.md) | XeLaTeX + ctex 配置中文 PDF |
| [自定义镜像扩展](examples/03-custom-image.md) | 创建包含额外依赖的自定义 Docker 镜像 |
| [CI 集成：GitHub Actions](examples/04-ci-integration.md) | CI 自动构建+部署到 GitHub Pages |

### 信源登记簿

* [信源索引](references/index.md) — Dockerfile 源码、CI 工作流配置、README 原文

## 学习路径建议

**快速使用路径**：
```
00 → 01（快速上手）→ examples/01（HTML构建）
```

**PDF 输出路径**：
```
00 → 01 → 04（PDF镜像详解）→ examples/02（PDF构建）
```

**CI/CD 集成路径**：
```
00 → 01 → 02（架构解析）→ 06（构建流水线）→ examples/04（CI集成）
```

**自定义/进阶路径**：
```
00 → 01 → 02 → 03 → 07（最佳实践）→ examples/03（自定义镜像）
```

## 镜像版本信息

- **Sphinx 版本**：8.2.3
- **许可证**：BSD-2-Clause
- **镜像仓库**：
  - Docker Hub：`sphinxdoc/sphinx`、`sphinxdoc/sphinx-latexpdf`、`sphinxdoc/docker-ci`
  - GHCR：`ghcr.io/sphinx-doc/sphinx`、`ghcr.io/sphinx-doc/sphinx-latexpdf`、`ghcr.io/sphinx-doc/sphinx-ci`
- **支持架构**：linux/amd64、linux/arm64
- **基础镜像**：python:slim（sphinx/latexpdf）、ubuntu:24.04（ci）

```{toctree}
:hidden:

concepts/index
examples/index
references/index
log
```
