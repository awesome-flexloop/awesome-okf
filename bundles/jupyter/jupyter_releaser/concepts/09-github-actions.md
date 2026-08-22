---
type: Concept
title: "GitHub Actions 集成"
description: "Composite Actions 使用方式、工作流模板、权限配置、Secrets 管理、check-release 自动检查"
tags: [github-actions, workflow, permissions, secrets, oidc]
stage: "进阶"
prerequisites: ["05-release-pipeline.md"]
sources:
  - /facts.md
  - /references/actions-source.md
---

# GitHub Actions 集成

jupyter_releaser 通过 GitHub Composite Actions 提供主要的用户界面，配合工作流文件（workflows）实现自动化发布。

## Composite Actions 清单

jupyter_releaser 提供 6 个 composite actions：

| Action | 用途 | 主要输入 |
|--------|------|---------|
| `jupyter-server/jupyter_releaser/.github/actions/prep-release@v2` | 阶段一：准备发布 | `version_spec`, `post_version_spec`, `branch`, `since`, `silent` |
| `jupyter-server/jupyter_releaser/.github/actions/populate-release@v2` | 阶段二：填充资产 | `release_url`, `assets` |
| `jupyter-server/jupyter_releaser/.github/actions/finalize-release@v2` | 阶段三：完成发布 | `release_url`, `npm_token`, `twine_repository_url` |
| `jupyter-server/jupyter_releaser/.github/actions/check-release@v2` | Dry-run 检查 | `version_spec` |
| `jupyter-server/jupyter_releaser/.github/actions/publish-changelog@v2` | 发布changelog | `release_url`, `branch` |
| `jupyter-server/jupyter_releaser/.github/actions/install-releaser@v2` | 安装工具 | （辅助action，无主要输入） |

### Action 内部结构

每个 composite action 的 `action.yml` 结构：
```yaml
name: 'Prep Release'
runs:
  using: 'composite'
  steps:
    - uses: jupyter-server/jupyter_releaser/.github/actions/install-releaser@v2
    - shell: bash
      run: python -m jupyter_releaser.actions.prep_release
      env:
        RH_VERSION_SPEC: ${{ inputs.version_spec }}
        # ... 其他环境变量
    - id: step-id
      shell: bash
      run: echo "release_url=$RH_RELEASE_URL" >> $GITHUB_OUTPUT
```

Composite action 做三件事：
1. 调用 `install-releaser` 安装 jupyter-releaser CLI
2. 设置环境变量（将 inputs 映射到 RH_* 环境变量）
3. 运行对应的 Python action 模块
4. 将关键输出写入 `$GITHUB_OUTPUT`

## 工作流模板

### Prep Release 工作流

```yaml
name: Step 1: Prep Release
on:
  workflow_dispatch:
    inputs:
      version_spec:
        description: "Version spec (new/patch/minor/major/dev or explicit version)"
        required: false
        default: "next"
      post_version_spec:
        description: "Post version (e.g. dev)"
        required: false
      branch:
        description: "Branch to release from"
        required: false
      since:
        description: "Use PRs since this tag/PR"
        required: false
      since_last_stable:
        description: "Start from last stable release"
        type: boolean
        required: false
        default: true
      silent:
        description: "Silent mode - placeholder changelog"
        type: boolean
        required: false
        default: false
  pull_request:
    types: [labeled]
  issues:
    types: [labeled]

jobs:
  prep_release:
    if: contains(github.event.pull_request.labels.*.name, 'prep-release') || contains(github.event.issue.labels.*.name, 'prep-release') || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: jupyter-server/jupyter_releaser/.github/actions/prep-release@v2
        with:
          version_spec: ${{ github.event.inputs.version_spec }}
          post_version_spec: ${{ github.event.inputs.post_version_spec }}
          branch: ${{ github.event.inputs.branch }}
          since: ${{ github.event.inputs.since }}
          since_last_stable: ${{ github.event.inputs.since_last_stable }}
        env:
          ADMIN_GITHUB_TOKEN: ${{ secrets.ADMIN_GITHUB_TOKEN }}
```

### Full Release 工作流（Populate + Finalize）

```yaml
name: "Step 2: Populate & Finalize Release"
on:
  release:
    types: [edited, published]
  pull_request:
    types: [labeled]

jobs:
  populate_release:
    if: github.event_name == 'release' && github.event.action == 'edited'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      id-token: write  # 用于 OIDC Trusted Publishing
    steps:
      - uses: jupyter-server/jupyter_releaser/.github/actions/populate-release@v2
        env:
          ADMIN_GITHUB_TOKEN: ${{ secrets.ADMIN_GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}

  finalize_release:
    if: github.event_name == 'release' && github.event.action == 'published'
    runs-on: ubuntu-latest
    environment: pypi  # PyPI 环境保护规则
    permissions:
      contents: write
      id-token: write
    steps:
      - uses: jupyter-server/jupyter_releaser/.github/actions/finalize-release@v2
        env:
          ADMIN_GITHUB_TOKEN: ${{ secrets.ADMIN_GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Check Release 工作流（PR 检查）

```yaml
name: "Check Release"
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  check_release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jupyter-server/jupyter_releaser/.github/actions/check-release@v2
        with:
          version_spec: next
        env:
          ADMIN_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 权限配置

### 必需的 GitHub Token 权限

| 权限 | 用途 | 阶段 |
|------|------|------|
| `contents: write` | Push commits/tags、创建 release、上传 assets | 全部 |
| `pull-requests: write` | 创建 changelog PR、forwardport PR | Prep、Finalize |
| `id-token: write` | OIDC 认证（Trusted Publishing） | Finalize |

在 Fork 模式下，由于 `pull_request` 事件来自 fork 的 context，自动获得 `contents: write` 权限（这是 fork 模式的一个安全优势）。

### GitHub 环境保护

建议对 finalize 阶段使用 GitHub Environment 保护规则：

1. 在 Settings → Environments 创建 `pypi` 环境
2. 设置必需的审核者（required reviewers）
3. 限制特定分支（main）
4. Finalize job 指定 `environment: pypi`

这样在 finalize 阶段实际执行前，需要指定人员手动批准。

## Secrets 配置

### Fork 模式（推荐）

在 fork 仓库中配置 secrets：

| Secret | 必需 | 说明 |
|--------|:----:|------|
| `ADMIN_GITHUB_TOKEN` | ✅ | PAT，需 `repo` 和 `workflow` 权限 |
| `NPM_TOKEN` | npm包 | npm 自动化令牌 |
| `PYPI_TOKEN` | 不推荐 | 长期 PyPI token（推荐用 OIDC 替代） |

目标仓库**不需要**配置这些 secrets——工作流在 fork 仓库中运行。

### 仓库内模式

在目标仓库中配置 secrets：

| Secret | 必需 | 说明 |
|--------|:----:|------|
| `ADMIN_GITHUB_TOKEN` | ✅ | PAT（默认 GITHUB_TOKEN 没有 workflow 权限） |
| `NPM_TOKEN` | npm包 | npm 令牌 |

注意：默认的 `GITHUB_TOKEN` 没有触发其他 workflow 的权限，因此必须使用 PAT 作为 `ADMIN_GITHUB_TOKEN`。

## 触发方式汇总

| 事件 | 条件 | 触发阶段 |
|------|------|---------|
| `workflow_dispatch` | 手动在 Actions 页面触发 | Prep |
| `issues.labeled` | 标签包含 `prep-release` | Prep |
| `pull_request.labeled` | 标签包含 `prep-release` 或 `publish-release` | Prep 或 Finalize |
| `release.edited` | Draft release 被编辑 | Populate |
| `release.published` | Release 被发布（点击Publish按钮） | Finalize |
| `pull_request` (check) | PR 到 main | Check（dry-run） |
| `push` (main) | Push 到 main | Check（dry-run） |

## install-releaser Action

`install-releaser` 是辅助 action，负责：
1. 设置 Python 环境
2. 安装指定版本的 jupyter-releaser（pip install）
3. 安装 twine、build、pipx 等依赖
4. 配置 git 用户（用于 commit/tag）
5. 设置 Node.js 环境（用于 npm 操作）

它不调用发布逻辑，只是准备运行环境。

## 相关文档

- [认证体系](10-authentication.md)
- [快速开始](01-getting-started.md)
- [Dry-Run与Mock机制](08-dry-run-and-mock.md)
