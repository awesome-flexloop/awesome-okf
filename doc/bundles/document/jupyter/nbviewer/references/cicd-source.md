---
type: Reference
title: "CI/CD工作流源码"
description: "GitHub Actions两个工作流：cd.yml（Helm部署流水线）和watch-dependencies.yaml（自动检查nbviewer更新）"
tags: [nbviewer, deploy, ci-cd, github-actions, helm, kubernetes, automation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cd-yml
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/.github/workflows/cd.yml"
    title: ".github/workflows/cd.yml"
  - id: watch-deps
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/.github/workflows/watch-dependencies.yaml"
    title: ".github/workflows/watch-dependencies.yaml"
  - id: dependabot
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/.github/dependabot.yml"
    title: ".github/dependabot.yml"
  - id: deploy-sh
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/deploy.sh"
    title: "deploy.sh"
---

# CI/CD工作流源码

本信源登记 GitHub Actions 工作流和相关自动化脚本。

## 工作流一览

| 工作流 | 文件 | 触发 | 用途 |
|--------|------|------|------|
| Deploy | `cd.yml` | push to main | Helm部署到Kubernetes |
| Watch Dependencies | `watch-dependencies.yaml` | 每日5点/手动/推送 | 自动检查nbviewer更新并开PR |

## cd.yml（部署流水线）

### 并发控制

```yaml
concurrency: deploy
```

使用 GitHub Actions concurrency 确保同一时间只有一个部署工作流运行，序列化多个待处理的部署。

### 触发条件

```yaml
on:
  push:
    branches:
      - main
    paths-ignore:
      - "*.md"
      - .pre-commit-config.yaml
      - .github/**
      - "!.github/workflows/cd.yml"
```

- **触发分支**：仅 `main` 分支
- **路径过滤**：忽略Markdown文件、pre-commit配置、`.github/`目录下大部分文件，但`cd.yml`本身的变更会触发部署

### 环境变量

| 变量 | 值 | 说明 |
|------|---|------|
| `KUBECTL_VERSION` | `v1.29.15` | kubectl版本 |
| `HELM_VERSION` | `v3.12.0` | Helm版本 |
| `KUBECONFIG` | `secrets/ovh-kubeconfig.yaml` | kubeconfig路径 |
| `NBVIEWER_VERSION` | `a53d108134e34e073344c1e2c6006a2eee86433a` | nbviewer chart版本（完整commit hash） |
| `NBVIEWER_CHART` | `nbviewer/helm-chart/nbviewer` | Helm chart路径（在检出的nbviewer仓库中） |

### Deploy Job 步骤

运行环境：`ubuntu-24.04`

| 步骤 | 操作 | 说明 |
|------|------|------|
| Checkout repo | `actions/checkout@v5` (fetch-depth: 0) | 检出部署仓库（完整历史） |
| Checkout nbviewer | `actions/checkout@v5` (repository: jupyter/nbviewer, ref: NBVIEWER_VERSION, path: nbviewer) | 检出指定版本的nbviewer仓库（包含Helm chart） |
| Setup Python | `actions/setup-python@v5` (python-version: "3.13", cache: pip) | 设置Python 3.13环境 |
| Install dependencies | `pip install --upgrade setuptools pip && pip install --upgrade -r requirements.txt` | 安装Python依赖 |
| Install kubectl | `azure/setup-kubectl@v4` (version: KUBECTL_VERSION) | 安装kubectl |
| Install helm | curl helm安装脚本 (DESIRED_VERSION=HELM_VERSION) | 安装Helm v3.12.0 |
| Unlock git-crypt | `sliteteam/github-action-git-crypt-unlock@...` (GIT_CRYPT_KEY: secrets.GIT_CRYPT_KEY) | 解密secrets文件 |
| deploy | `bash deploy.sh` | 执行部署脚本 |
| test | `pytest` | 运行冒烟测试 |

### CI模式下的deploy.sh行为

在CI环境中，`CI` 环境变量被设置（GitHub Actions自动设置），`deploy.sh` 行为如下：

1. 设置 `KUBECONFIG=$PWD/secrets/ovh-kubeconfig.yaml`
2. 执行 `helm dep up $nbviewer_chart`（更新chart依赖）
3. **跳过** `helm diff` 和交互式确认（因为 `CI` 环境变量非空）
4. 执行 `helm upgrade nbviewer $nbviewer_chart -f config/nbviewer.yaml -f secrets/config/nbviewer.yaml --cleanup-on-fail`
5. 执行 `kubectl rollout status -w deployment/nbviewer`（等待滚动更新完成）

**与本地模式的区别**：
- 本地模式：执行 `helm diff -C 5` 预览变更 → 交互式确认 → 执行部署
- CI模式：直接执行部署，无预览无确认
- **deploy.sh 不执行CDN同步**（Fastly后端更新需要手动运行 `invoke fastly`）

## watch-dependencies.yaml（自动更新检查）

### 触发条件

```yaml
on:
  push:
    paths:
      - ".github/workflows/watch-dependencies.yaml"
  schedule:
    - cron: "0 5 * * *"    # 每日UTC 5:00
  workflow_dispatch:        # 手动触发
```

- 每日自动运行一次
- 工作流文件本身推送时也触发
- 支持手动触发

### Job条件

```yaml
if: github.repository == 'jupyter/nbviewer.org-deploy' || github.event_name != 'schedule'
```

- 定时任务仅在官方仓库运行（fork不执行定时任务）
- 手动触发和push触发在fork中也可运行

运行环境：`ubuntu-24.04`，环境：`watch-dependencies`

### 步骤

| 步骤 | 操作 | 说明 |
|------|------|------|
| Checkout | `actions/checkout@v4` | 检出代码 |
| Setup Python | `actions/setup-python@v5` (python-version: "3.13", cache: pip) | 设置Python |
| Install requirements | `pip install -r requirements.txt` | 安装依赖 |
| Check for updates | `python3 scripts/update-nbviewer.py` | 运行更新脚本 |
| git diff | 检查是否有变更 | 设置 `changed=true/false` 输出 |
| Fetch PR summary | `./scripts/get-prs.py` (仅当有变更时) | 获取版本间的PR列表 |
| Create PR | `peter-evans/create-pull-request@v7` | 创建更新PR |

### PR创建条件

```yaml
if: github.repository == 'jupyter/nbviewer.org-deploy' && (github.event_name != 'push' || github.ref == 'refs/heads/main')
```

- 仅在官方仓库创建PR
- push事件仅在main分支创建PR
- 使用 `BOT_PAT` secret认证
- 提交者和作者为 "Jupyter Bot Account"

### PR内容

自动创建的PR包含：
- 更新nbviewer chart到最新commit
- 更新nbviewer镜像到最新tag
- PR描述中包含版本间的PR列表摘要

## scripts/update-nbviewer.py 更新脚本

此脚本被 `watch-dependencies.yaml` 调用，也可本地运行。

### 核心函数

| 函数 | 功能 |
|------|------|
| `get_current_chart()` | 从 `cd.yml` 读取当前 `NBVIEWER_VERSION`（chart commit） |
| `get_latest_chart()` | 通过 `git ls-remote` 获取nbviewer仓库HEAD的commit hash |
| `get_current_image()` | 从 `config/nbviewer.yaml` 读取当前 `image` 值 |
| `get_latest_image()` | 从Docker Hub API获取最新镜像tag |
| `update_chart()` | 如果有新版本，替换 `cd.yml` 中的版本号 |
| `update_image()` | 如果有新版本，替换 `config/nbviewer.yaml` 中的镜像标签 |
| `main()` | 依次执行 `update_chart()` 和 `update_image()` |

### 输出变量

脚本通过 `GITHUB_OUTPUT` 环境变量向GitHub Actions输出（如果在CI中运行）：

| 输出变量 | 说明 |
|---------|------|
| `chart_before` | 更新前的chart commit |
| `chart_after` | 更新后的chart commit |
| `chart_short` | 新版本短hash（前7位） |
| `image_before` | 更新前的镜像 |
| `image_after` | 更新后的镜像 |
| `image_tag` | 新镜像tag部分 |

## scripts/get-prs.py PR摘要脚本

从mybinder.org-deploy项目复制（BSD-3-Clause许可），用于获取两个commit之间的PR列表。

- 使用PyGithub库调用GitHub API
- 支持提取git ref中的commit hash（支持chartpress格式版本号）
- 输出Markdown格式的PR列表
- 支持写入GitHub Actions输出变量

## dependabot.yml

```yaml
version: 2
updates:
  - package-ecosystem: "pypi"
    directory: "/"
    allow:
      - dependency-type: all
    schedule:
      interval: "monthly"
    open-pull-requests-limit: 3
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
    open-pull-requests-limit: 3
```

Dependabot每月检查Python依赖和GitHub Actions更新，最多同时打开3个PR。

## 部署流水线全景

```
watch-dependencies (每日5:00或手动)
  │
  ├─ python3 scripts/update-nbviewer.py
  │    ├─ 检查nbviewer repo最新commit
  │    ├─ 检查Docker Hub最新镜像tag
  │    └─ 更新cd.yml和config/nbviewer.yaml
  │
  └─ 有变更? → 创建PR → 人工审查 → 合并到main
                                    │
                                    ▼
                           cd.yml (push to main)
                                    │
                            ┌───────┴───────┐
                            │ 并发锁: deploy │
                            └───────┬───────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │ checkout      │ 检出nbviewer   │
                    │ install deps  │ install helm   │
                    │ git-crypt解锁 │                │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                           bash deploy.sh (CI模式)
                                    │
                         ┌──────────┴──────────┐
                         │ helm dep up          │
                         │ helm upgrade         │
                         │   --cleanup-on-fail  │
                         │ kubectl rollout      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                              pytest (冒烟测试)
                                    │
                                    ▼
                           部署完成 ✓
                           (CDN需手动更新: invoke fastly)
```

## 相关信源

- [deploy.sh部署脚本](#deploysh在ci中的行为)
- [部署配置文件源码](config-source.md)
- [测试源码解析](tests-source.md)
- [CI/CD与自动化](/concepts/04-cicd-and-automation.md)
