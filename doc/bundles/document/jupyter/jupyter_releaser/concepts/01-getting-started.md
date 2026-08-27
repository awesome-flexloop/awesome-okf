---
type: Concept
title: "快速开始"
description: "两种模式的接入步骤：Fork 模式与仓库内模式，以及首次发布检查清单"
tags: [getting-started, setup, workflow_dispatch, labels]
stage: "入门"
prerequisites: ["00-introduction.md"]
sources:
  - actions-source.md#github-composite-actionsgithubactions
  - /facts.md
---

# 快速开始

## 前置条件

- GitHub 仓库（Python 包、npm 包或两者混合）
- Python 3.8+（pip install jupyter-releaser）
- 管理员权限（或信任的发布管理员权限）
- 对 PyPI/npm 包有发布权限（finalize 阶段需要）

## 模式一：Fork 模式接入（推荐）

### Step 1：Fork jupyter-releaser 仓库

将 `jupyter-server/jupyter_releaser` fork 到你的 GitHub 账号或组织下。

### Step 2：配置 Fork 仓库 Secrets

在 fork 仓库的 Settings → Secrets → Actions 中添加：

| Secret | 必需 | 说明 |
|--------|:----:|------|
| `ADMIN_GITHUB_TOKEN` | ✅ | 具有 `repo`, `workflow` 权限的 Personal Access Token (PAT) |
| `NPM_TOKEN` | 视情况 | npm 发布令牌（有 npm 包时需要） |
| `PYPI_TOKEN` | 视情况 | PyPI API token（纯 token 模式需要） |

### Step 3：在目标仓库配置标签

在目标仓库中创建两个标签：
- `prep-release`：触发 prep-release 工作流
- `publish-release`：触发 finalize-release 工作流

### Step 4：复制工作流文件

将 jupyter_releaser 提供的示例工作流文件复制到目标仓库的 `.github/workflows/` 目录。关键工作流：
- `publish-release.yml`：监听 release event 和 `publish-release` 标签
- `prep-release.yml`：监听 workflow_dispatch 和 `prep-release` 标签

### Step 5：第一次发布

1. 在目标仓库打开一个 Issue 或 PR，添加 `prep-release` 标签
2. GitHub Actions 会在 fork 仓库中自动运行 prep-release 工作流
3. 审核生成的 Changelog PR 和 Draft Release
4. 合并 Changelog PR
5. 在目标仓库打开一个 Release，添加 `publish-release` 标签
6. Populate 工作流自动运行，构建资产并上传到 Draft Release
7. 审核 Draft Release 中的资产
8. 点击 Publish Release，finalize 工作流自动运行
9. 完成！

## 模式二：仓库内模式接入

### Step 1：添加工作流文件

在目标仓库创建以下工作流文件：

**`.github/workflows/prep-release.yml`**：
```yaml
name: Step 1: Prep Release
on:
  workflow_dispatch:
    inputs:
      version_spec:
        description: "Version specifier"
        required: false
      post_version_spec:
        description: "Post version specifier"
        required: false
      branch:
        description: "Branch to release from"
        required: false
      repo:
        description: "Target repo (owner/name)"
        required: false
      since:
        description: "Since commit/PR"
        required: false
      since_last_stable:
        description: "Since last stable release"
        type: boolean
        required: false
```

**`.github/workflows/full-release.yml`**：
```yaml
name: Step 2: Populate Release
on:
  release:
    types: [edited]
  pull_request:
    types: [labeled]
```

### Step 2：配置 Secrets

| Secret | 说明 |
|--------|------|
| `ADMIN_GITHUB_TOKEN` | GitHub PAT（需 repo:workflow 权限） |
| `NPM_TOKEN` | npm 发布令牌 |
| `PYPI_TOKEN` | PyPI API token |

### Step 3：安装 jupyter-releaser

在工作流中使用 `jupyter-server/jupyter_releaser/.github/actions/install-releaser@v2` action 安装。

### Step 4：触发首次发布

1. 到 Actions → Step 1: Prep Release → Run workflow
2. 选择分支，可选指定版本号
3. 审核 Changelog PR 和 Draft Release
4. 合并 Changelog PR
5. 到 Releases 编辑 Draft Release，点击 Publish（或编辑一下触发 populate）
6. Populate 和 Finalize 工作流自动运行

## 首次发布检查清单

在执行第一次发布前，确认以下事项：

- [ ] 版本号管理工具已配置（tbump.toml、hatch version、bumpversion.cfg 等）
- [ ] CHANGELOG.md 已存在（或确认 jupyter_releaser 能创建）
- [ ] pyproject.toml 中包含正确的包名和版本信息
- [ ] GitHub Token 有 `workflow` 权限（能操作 GitHub Actions）
- [ ] PyPI 包已创建（或第一次发布时自动创建）
- [ ] npm 包已创建（如适用）
- [ ] 分支保护规则不会阻止 release commit 推送
- [ ] 本地测试过 dry-run（参见 [Dry-Run测试](../examples/03-dry-run-testing.md)）

## 常用触发方式对比

| 触发方式 | 适用阶段 | 说明 |
|---------|---------|------|
| `prep-release` 标签 | Prep | 在 Issue/PR 上打标签触发 prep |
| workflow_dispatch | Prep | 在 Actions 页面手动触发，可输入参数 |
| Release edited | Populate | 编辑 draft release 触发 populate |
| `publish-release` 标签 | Populate/Finalize | 在 Release 上打标签 |
| Release published | Finalize | 点击 Publish Release 触发 finalize |

## 常见第一次错误

| 错误 | 原因 | 解决 |
|------|------|------|
| "403 Resource not accessible" | Token 权限不足 | 确保 PAT 有 repo:workflow 权限 |
| "Branch not found" | ref 参数不匹配 | 检查 RH_BRANCH 是否为默认分支 |
| "Tag already exists" | 版本号已发布 | 使用 `since` 参数跳过已有 tag |
| "No version tool found" | 未配置版本管理 | 添加 tbump.toml 或使用 hatch |
| npm 404 | 包名不存在或 token 无效 | 确认包已在 npm 创建、token 正确 |

## 下一步

- 了解[架构总览](02-architecture-overview.md)，理解 CLI 和 Actions 的双层关系
- 深入[发布流水线详解](05-release-pipeline.md)，了解三阶段的内部逻辑
- 学习[配置与 Hooks](04-config-and-hooks.md)，自定义发布行为
