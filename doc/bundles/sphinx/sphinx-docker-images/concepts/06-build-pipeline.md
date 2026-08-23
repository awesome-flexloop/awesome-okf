---
type: concept
title: "构建流水线详解"
description: "深入解析 GitHub Actions 双工作流设计——版本发布与 CI 镜像构建的触发条件、矩阵策略、多架构构建与双 Registry 推送"
tags: [github-actions, ci-cd, docker, build-pipeline, multi-arch]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: build, resource: "/references/workflow-build.md", title: "版本发布工作流 build.yml" }
  - { id: build-ci, resource: "/references/workflow-build-ci.md", title: "CI 镜像工作流 build-ci.yml" }
---

# 构建流水线详解

sphinx-docker-images 使用 GitHub Actions 实现自动化的 Docker 镜像构建和发布，采用两个独立的工作流分别处理版本发布和 CI 镜像更新。

## 工作流架构

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Events                             │
│  ┌──────────────┐              ┌──────────────────┐         │
│  │ push tag     │              │ push to master   │         │
│  │ (*.*.*)      │              │ (branch: master) │         │
│  └──────┬───────┘              └────────┬─────────┘         │
│         │                               │                   │
│         ▼                               ▼                   │
│  ┌──────────────┐              ┌──────────────────┐         │
│  │  build.yml   │              │  build-ci.yml    │         │
│  │ (版本发布)    │              │ (CI镜像日构建)    │         │
│  └──────┬───────┘              └────────┬─────────┘         │
│         │                               │                   │
│         ▼                               ▼                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           共同步骤                                    │   │
│  │  checkout → setup-qemu → setup-buildx                │   │
│  │  → login(Docker Hub + GHCR) → metadata → build-push  │   │
│  └──────────┬───────────────────────────┬───────────────┘   │
│             ▼                           ▼                   │
│  ┌──────────────────┐        ┌──────────────────────┐       │
│  │ sphinx (base/)   │        │ docker-ci (ci/)      │       │
│  │ sphinx-latexpdf  │        │ tag: 日期 + latest   │       │
│  │ (latexpdf/)      │        │                      │       │
│  │ tag: PEP 440     │        │                      │       │
│  └──────────────────┘        └──────────────────────┘       │
│             │                           │                   │
│             ▼                           ▼                   │
│  ┌──────────────────┐        ┌──────────────────────┐       │
│  │ Docker Hub       │        │ Docker Hub           │       │
│  │ GHCR             │        │ GHCR                 │       │
│  │ linux/amd64      │        │ linux/amd64          │       │
│  │ linux/arm64      │        │ linux/arm64          │       │
│  └──────────────────┘        └──────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## build.yml：版本发布工作流

### 触发条件

```yaml
on:
  push:
    tags:
      - '*.*.*'
```

- **触发事件**：推送语义化版本 tag（如 `v8.2.3` 或 `8.2.3`）
- **执行守卫**：`if: github.repository_owner == 'sphinx-doc' && startsWith(github.ref, 'refs/tags/')`
  - 仅在官方仓库（sphinx-doc）执行
  - 双重确认是 tag 推送（防止分支名匹配误触发）

### 构建矩阵

```yaml
strategy:
  matrix:
    include:
      - name: sphinx
        context: base
      - name: sphinx-latexpdf
        context: latexpdf
```

使用 matrix 策略并行构建两个镜像，共享相同的构建步骤：

| name | context | 说明 |
|------|---------|------|
| sphinx | `base/` | 基础镜像，从 base/Dockerfile 构建 |
| sphinx-latexpdf | `latexpdf/` | PDF 镜像，从 latexpdf/Dockerfile 构建 |

### 构建步骤详解

#### 步骤 1：检出代码

```yaml
- uses: actions/checkout@v6
```

使用 actions/checkout@v6 检出仓库代码。注意所有 Action 版本都使用 **commit hash 锁定**（如 `c7c53464625b32c7a7e944ae62b3e17d2b600130`），并在注释中标明语义版本（`# v3.7.0`）。这种做法：
- **安全**：防止 Action 维护者 force push 恶意代码到 tag
- **可复现**：固定版本确保构建行为一致
- **可读**：注释标明版本号，方便人工更新

#### 步骤 2-3：多架构构建配置

```yaml
- uses: docker/setup-qemu-action@...  # v3.7.0
- uses: docker/setup-buildx-action@...  # v3.11.1
```

- `setup-qemu-action`：安装 QEMU 模拟器，允许在 amd64 runner 上构建 arm64 镜像
- `setup-buildx-action`：配置 Docker Buildx，这是 Docker 的多架构构建引擎

#### 步骤 4-5：双 Registry 登录

```yaml
# Docker Hub
- uses: docker/login-action@...
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

# GHCR
- uses: docker/login-action@...
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

- Docker Hub 使用配置的 secrets 认证（需要提前在仓库设置中配置 DOCKERHUB_USERNAME 和 DOCKERHUB_TOKEN）
- GHCR 使用 GitHub 自动提供的 GITHUB_TOKEN，无需额外配置 secrets

#### 步骤 6：元数据提取

```yaml
- uses: docker/metadata-action@...
  with:
    images: |
      sphinxdoc/${{ matrix.name }}
      ghcr.io/sphinx-doc/${{ matrix.name }}
    tags: type=pep440,pattern={{version}}
```

`docker/metadata-action` 自动从 Git tag 生成 Docker tag 和 OCI 标签：
- 自动为两个 Registry 生成镜像名
- Tag 类型为 `pep440`，即从 Git tag 中提取 PEP 440 格式的版本号
- 自动添加 OCI 标准标签（如创建时间、源码 URL 等）

#### 步骤 7：构建并推送

```yaml
- uses: docker/build-push-action@...
  with:
    context: ${{ matrix.context }}
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
```

- `context`：Docker 构建上下文目录（base/ 或 latexpdf/）
- `platforms`：目标架构为 amd64 + arm64（通过 QEMU 跨架构构建）
- `push: true`：构建完成后直接推送到 Registry
- `tags`/`labels`：使用 metadata action 输出的 tag 和标签

## build-ci.yml：CI 镜像工作流

### 触发条件

```yaml
on:
  push:
    branches: ['master']
```

- **触发事件**：每次推送到 master 分支（即 PR 合并后）
- **执行守卫**：`if: github.repository_owner == 'sphinx-doc'`（仅官方仓库）

### 关键差异

| 配置 | build.yml | build-ci.yml |
|------|-----------|--------------|
| 触发 | tag 推送 | master 分支 push |
| 矩阵 | 2 个镜像并行 | 单镜像（无 matrix） |
| 构建上下文 | base/, latexpdf/ | ci/ |
| 镜像名（Hub） | sphinxdoc/sphinx, sphinxdoc/sphinx-latexpdf | sphinxdoc/docker-ci |
| 镜像名（GHCR） | ghcr.io/sphinx-doc/sphinx, .../sphinx-latexpdf | ghcr.io/sphinx-doc/sphinx-ci |
| Tag 类型 | `pep440`（版本号） | `schedule`（日期）+ `raw:latest` |
| Tag 示例 | 8.2.3 | 2026-08-21, latest |

### Tag 策略详解

```yaml
tags: |
  type=schedule,pattern={{date 'YYYY-MM-DD'}}
  type=raw,value=latest,enable={{is_default_branch}}
```

- **日期 tag**：每天构建生成一个日期标签（如 `2026-08-21`），保留历史版本便于排查问题
- **latest tag**：仅在默认分支（master）构建时标记 `latest`，供 CI 脚本引用 `:latest`

## Dependabot 配置

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
    groups:
       all-github-actions:
          patterns:
            - "*"
```

Dependabot 每月检查 GitHub Actions 更新：
- 生态系统：`github-actions`
- 频率：每月一次
- 分组：所有 Action 更新合并为一个 PR（`all-github-actions` 组）

## 安全最佳实践

从工作流配置中可以学到的 CI/CD 安全实践：

1. **Action 版本锁定**：使用 commit hash 而非 tag，防止供应链攻击
2. **双重执行守卫**：tag 格式匹配 + repository_owner 检查
3. **最小权限**：GITHUB_TOKEN 由 GitHub 自动管理，权限最小化
4. **Secrets 管理**：Docker Hub 凭证存放在 repository secrets 中
5. **多架构支持**：QEMU + Buildx 实现 amd64/arm64 双架构
6. **双 Registry 冗余**：同时发布到 Docker Hub 和 GHCR，单一 Registry 故障不影响使用

## 相关概念

- [三镜像架构解析](/concepts/02-image-architecture.md)：三个镜像的用途
- [CI 镜像详解](/concepts/05-ci-image.md)：CI 镜像的 Dockerfile 细节
- [CI 集成测试示例](/examples/04-ci-integration.md)：在 GitHub Actions 中使用这些镜像
