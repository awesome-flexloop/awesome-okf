---
type: reference
title: "CI 镜像工作流 build-ci.yml"
description: "GitHub Actions CI 测试镜像构建与推送工作流配置源码解析"
tags: [github-actions, ci, docker, testing]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: src-build-ci, resource: "external/libs/docs/sphinx-docker-images/.github/workflows/build-ci.yml", title: "build-ci.yml 源码" }
---

# CI 镜像工作流 build-ci.yml

## 完整源码

```yaml
name: Create Docker image for CI

on:
  push:
    branches: ['master']

jobs:
  build:
    if: github.repository_owner == 'sphinx-doc'
    runs-on: ubuntu-latest
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
            sphinxdoc/docker-ci
            ghcr.io/sphinx-doc/sphinx-ci
          tags: |
            type=schedule,pattern={{date 'YYYY-MM-DD'}}
            type=raw,value=latest,enable={{is_default_branch}}
      - name: Build and push Docker image
        uses: docker/build-push-action@263435318d21b8e681c14492fe198d362a7d2c83  # v6.18.0
        with:
          context: ci
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

## 工作流解析

### 触发条件

- **触发事件**：`push` 到 `master` 分支（每次合并到主分支都触发）
- **执行条件**：仓库 owner 必须是 `sphinx-doc`（无 tag 检查，因为不依赖 tag）

### 与 build.yml 的关键差异

| 项目 | build.yml | build-ci.yml |
|------|-----------|--------------|
| 触发 | tag 推送（*.*.*） | master 分支 push |
| 构建上下文 | base/ 和 latexpdf/（矩阵） | ci/（单镜像） |
| 镜像名（Docker Hub） | sphinxdoc/sphinx, sphinxdoc/sphinx-latexpdf | sphinxdoc/docker-ci |
| 镜像名（GHCR） | ghcr.io/sphinx-doc/sphinx, ghcr.io/sphinx-doc/sphinx-latexpdf | ghcr.io/sphinx-doc/sphinx-ci |
| Tag 策略 | PEP 440 版本号 | 日期 tag（YYYY-MM-DD）+ latest |
| 用途 | 用户使用的正式版本镜像 | Sphinx 自身 CI 测试用镜像 |

### Tag 策略说明

- **日期 tag**：`type=schedule,pattern={{date 'YYYY-MM-DD'}}` — 每次构建生成日期标签（如 `2026-08-21`）
- **latest tag**：`type=raw,value=latest,enable={{is_default_branch}}` — master 分支额外标记 `latest`
- 日期 tag 保留历史版本，latest 始终指向最新 CI 镜像
