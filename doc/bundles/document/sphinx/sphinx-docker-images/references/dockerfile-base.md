---
type: reference
title: "Base 镜像 Dockerfile 源码"
description: "sphinxdoc/sphinx 基础镜像 Dockerfile 完整源码与逐行解析"
tags: [docker, dockerfile, base-image, sphinx]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: src-base, resource: "external/libs/docs/sphinx-docker-images/base/Dockerfile", title: "base/Dockerfile 源码" }
---

# Base 镜像 Dockerfile 源码

## 完整源码

```dockerfile
FROM python:slim

LABEL org.opencontainers.image.authors="Sphinx Team <https://www.sphinx-doc.org/>"
LABEL org.opencontainers.image.documentation="https://sphinx-doc.org/"
LABEL org.opencontainers.image.source="https://github.com/sphinx-doc/sphinx-docker-images"
LABEL org.opencontainers.image.version="8.2.3"
LABEL org.opencontainers.image.licenses="BSD-2-Clause"
LABEL org.opencontainers.image.description="Base container image for Sphinx"

WORKDIR /docs
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
      graphviz \
      imagemagick \
      make \
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade pip \
 && python3 -m pip install --no-cache-dir Sphinx==8.2.3 Pillow

CMD ["sphinx-build", "-M", "html", ".", "_build"]
```

## 逐行解析

| 行 | 指令 | 说明 |
|----|------|------|
| 1 | `FROM python:slim` | 基于 Python 官方 slim 镜像（Debian 精简版） |
| 3-8 | `LABEL` | OCI 标准标签：作者、文档、源码、版本 8.2.3、许可证 BSD-2-Clause、描述 |
| 10 | `WORKDIR /docs` | 设置工作目录为 `/docs`，用户需挂载文档到此目录 |
| 11-18 | `RUN apt-get` | 安装系统依赖：graphviz（图表渲染）、imagemagick（图片处理）、make（构建工具）；使用 `--no-install-recommends` 最小化安装；清理 apt 缓存减小镜像体积 |
| 20-21 | `RUN pip install` | 升级 pip 并安装 Sphinx 8.2.3 + Pillow（图片处理库）；`--no-cache-dir` 禁用 pip 缓存 |
| 23 | `CMD` | 默认命令：`sphinx-build -M html . _build`，构建 HTML 文档 |

## 关键事实

- **基础镜像**：`python:slim`（Debian 精简版，非 Alpine）
- **Sphinx 版本**：锁定为 8.2.3
- **系统包**：graphviz、imagemagick、make（3个）
- **Python 包**：Sphinx==8.2.3、Pillow（最新版）
- **默认命令**：HTML 构建模式
- **工作目录**：`/docs`
- **镜像标签**：`sphinxdoc/sphinx`（Docker Hub）、`ghcr.io/sphinx-doc/sphinx`（GHCR）
