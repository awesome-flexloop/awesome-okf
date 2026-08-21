---
type: reference
title: "版本发布工作流 build.yml"
description: "GitHub Actions 版本镜像构建与推送工作流配置源码解析"
tags: [github-actions, ci-cd, docker, build-pipeline]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: src-build, resource: "external/libs/docs/sphinx-docker-images/.github/workflows/build.yml", title: "build.yml 源码" }
---

# 版本发布工作流 build.yml

## 完整源码

```yaml
name: Create Docker images

on:
  push:
    tags:
      - '*.*.*'

jobs:
  build:
    if: github.repository_owner == 'sphinx-doc' && startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - name: sphinx
            context: base
          - name: sphinx-latexpdf
            context: latexpdf
    steps:
      - uses: actions/checkout@v6
      - uses: docker/setup-qemu-action@c7c53464625b32c7a7e944ae62b3e17d2b600130  # v3.7.0
      - uses: docker/setup-buildx-action@e468171a9de216ec08956ac3ada2f0791b6bd435  # v3.11.1
      - name: Log in to Docker Hub
        uses: docker/login-action@5e57cd118135c172c3672efd75eb46360885c0ef  # v3.6.0
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@5e57cd118135c172c3672efd75eb46360885c0ef  # v3.6.0
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Extract metadata (tags, labels) for Docker
        id: meta
        uses: docker/metadata-action@c299e40c65443455700f0fdfc63efafe5b349051  # v5.10.0
        with:
          images: |
            sphinxdoc/${{ matrix.name }}
            ghcr.io/sphinx-doc/${{ matrix.name }}
          tags: type=pep440,pattern={{version}}
      - name: Build and push Docker image
        uses: docker/build-push-action@263435318d21b8e681c14492fe198d362a7d2c83  # v6.18.0
        with:
          context: ${{ matrix.context }}
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

## 工作流解析

### 触发条件

- **触发事件**：`push` 到 `tags`，匹配 `*.*.*`（语义化版本号，如 `8.2.3`）
- **执行条件**：仓库 owner 必须是 `sphinx-doc`，且 ref 以 `refs/tags/` 开头（双重保护）

### 构建矩阵

| name | context | 镜像名 |
|------|---------|--------|
| sphinx | base/ | sphinxdoc/sphinx, ghcr.io/sphinx-doc/sphinx |
| sphinx-latexpdf | latexpdf/ | sphinxdoc/sphinx-latexpdf, ghcr.io/sphinx-doc/sphinx-latexpdf |

### 构建步骤

1. **checkout**：检出代码（actions/checkout@v6）
2. **setup-qemu**：配置 QEMU 模拟器（支持跨架构构建）
3. **setup-buildx**：配置 Docker Buildx（多架构构建引擎）
4. **login Docker Hub**：使用 DOCKERHUB_USERNAME/DOCKERHUB_TOKEN secrets
5. **login GHCR**：使用 GITHUB_TOKEN 登录 ghcr.io
6. **metadata**：提取 OCI 元数据，使用 PEP 440 版本 tag
7. **build-and-push**：构建并推送，支持 linux/amd64 + linux/arm64 双架构

### 关键配置

- **双 Registry**：同时推送到 Docker Hub 和 GHCR
- **双架构**：linux/amd64 和 linux/arm64
- **Tag 格式**：PEP 440 版本号（如 8.2.3）
- **Action 版本**：使用 commit hash 锁定版本，注释标明版本号
