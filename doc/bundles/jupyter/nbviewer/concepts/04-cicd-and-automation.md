---
type: Concept
title: "CI/CD与自动化"
description: "GitHub Actions两个工作流详解：cd.yml部署流水线、watch-dependencies.yaml自动更新、pre-commit和dependabot"
tags: [nbviewer, deploy, ci-cd, github-actions, automation, watch-dependencies, pre-commit]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cicd
    resource: "/references/cicd-source.md"
    title: "CI/CD工作流信源"
---

# CI/CD与自动化

nbviewer.org-deploy 使用 GitHub Actions 实现自动化部署和依赖更新，辅以 pre-commit 代码质量检查和 Dependabot 依赖更新。

## 自动化体系概览

| 自动化 | 工具 | 触发 | 频率 |
|--------|------|------|------|
| 生产部署 | cd.yml | push to main | 合并PR时 |
| 版本检查 | watch-dependencies.yaml | cron + 手动 | 每日UTC 5:00 |
| 代码质量 | pre-commit | git commit | 每次提交 |
| 依赖更新 | Dependabot | schedule | 每月 |

## cd.yml（部署流水线）

### 并发控制

```yaml
concurrency: deploy
```

使用 GitHub Actions 的 concurrency 功能确保同一时间只有一个部署工作流运行。如果多个PR在短时间内合并到main，它们会排队依次执行，避免并发部署冲突。

### 触发规则

- **分支**：仅 `main` 分支的push事件
- **路径忽略**：
  - `*.md` — Markdown文件变更不触发部署
  - `.pre-commit-config.yaml` — pre-commit配置变更不触发部署
  - `.github/**` — GitHub配置变更不触发（但cd.yml自身变更除外）
  - `!.github/workflows/cd.yml` — cd.yml本身的变更会触发部署

### 环境配置

| 工具 | 版本 | 安装方式 |
|------|------|---------|
| Python | 3.13 | `actions/setup-python@v5` |
| kubectl | v1.29.15 | `azure/setup-kubectl@v4` |
| Helm | v3.12.0 | curl helm安装脚本 |

**关键环境变量**：

| 变量 | 值 | 说明 |
|------|---|------|
| `KUBECONFIG` | `secrets/ovh-kubeconfig.yaml` | kubeconfig路径（相对于工作目录） |
| `NBVIEWER_VERSION` | 完整commit hash | 要部署的nbviewer版本 |
| `NBVIEWER_CHART` | `nbviewer/helm-chart/nbviewer` | Helm chart在nbviewer仓库中的路径 |

### 执行步骤详解

**Step 1-2: 代码检出**

```yaml
- uses: actions/checkout@v5          # 检出部署仓库 (fetch-depth: 0)
- uses: actions/checkout@v5          # 检出nbviewer仓库
  with:
    repository: jupyter/nbviewer
    ref: ${{ env.NBVIEWER_VERSION }}
    path: nbviewer
```

部署需要两个仓库：
1. nbviewer.org-deploy（部署配置）
2. jupyter/nbviewer（Helm chart + nbviewer源码）

**Step 3-6: 环境准备**

1. 设置Python 3.13 + pip缓存
2. `pip install --upgrade setuptools pip && pip install --upgrade -r requirements.txt`
3. 安装kubectl
4. 安装Helm（通过官方get-helm-3脚本）

**Step 7: 解锁密钥**

```yaml
- uses: sliteteam/github-action-git-crypt-unlock@...
  env:
    GIT_CRYPT_KEY: ${{ secrets.GIT_CRYPT_KEY }}
```

使用 `GIT_CRYPT_KEY` secret解密仓库中的git-crypt加密文件，包括kubeconfig和Helm密钥配置。

**Step 8: 部署**

```yaml
- name: deploy
  run: bash deploy.sh
```

在CI环境中（`CI` 环境变量由GitHub Actions自动设置），`deploy.sh` 跳过交互式确认，直接执行 `helm upgrade --cleanup-on-fail`，然后等待 `kubectl rollout status`。

**Step 9: 测试**

```yaml
- name: test
  run: pytest
```

部署完成后运行冒烟测试，验证线上nbviewer.org正常工作。

### 所需Secrets

| Secret | 用途 |
|--------|------|
| `GIT_CRYPT_KEY` | 解密git-crypt加密的secrets文件 |

## watch-dependencies.yaml（自动版本更新）

### 触发条件

| 触发方式 | 配置 | 说明 |
|---------|------|------|
| 定时 | `cron: "0 5 * * *"` | 每日UTC 5:00运行 |
| 手动 | `workflow_dispatch` | GitHub UI手动触发 |
| 推送 | paths包含workflow文件本身 | 工作流配置变更时 |

### Fork保护

```yaml
if: github.repository == 'jupyter/nbviewer.org-deploy' || github.event_name != 'schedule'
```

定时任务只在官方仓库运行（不在fork上），但手动触发和推送触发在fork上也可运行（用于CI开发测试）。

### 执行步骤

**Step 1-3: 环境准备**

1. Checkout代码
2. 设置Python 3.13 + pip缓存
3. 安装requirements.txt依赖

**Step 4: 检查更新**

```bash
python3 scripts/update-nbviewer.py
```

此脚本（详见[版本更新机制](05-version-update.md)）：
1. 获取当前cd.yml中的NBVIEWER_VERSION
2. 查询nbviewer仓库的最新HEAD commit
3. 获取当前config/nbviewer.yaml中的image tag
4. 查询Docker Hub的最新镜像tag
5. 如果有更新，替换文件中的版本号

**Step 5: 检查变更**

```bash
if git --no-pager diff --color=always --exit-code; then
  echo "changed=false" >> "$GITHUB_OUTPUT"
else
  echo "changed=true" >> "$GITHUB_OUTPUT"
fi
```

通过git diff检测是否有文件变更，设置 `changed` 输出变量。

**Step 6: 获取PR摘要（仅当有变更时）**

```bash
./scripts/get-prs.py jupyter/nbviewer <old_commit> <new_commit> \
    --write-github-actions-output=prs
```

使用 `scripts/get-prs.py` 提取两个版本之间的PR列表，用于生成PR描述。

**Step 7: 创建PR**

```yaml
- uses: peter-evans/create-pull-request@v7
  with:
    token: "${{ secrets.BOT_PAT }}"
    author: Jupyter Bot Account <bot-account@jupyter.org.local>
    committer: Jupyter Bot Account <bot-account.org.local>
    branch: update-nbviewer
    commit-message: "Update nbviewer version to <short_hash>"
    title: "Update nbviewer version to <short_hash>"
    body: |
      - Updates nbviewer chart to jupyter/nbviewer@<new_commit>
      - Update nbviewer image to `<image_tag>`
      <PR摘要>
```

PR创建条件：
- 仅在官方仓库创建
- push事件仅在main分支创建PR
- 使用 `BOT_PAT` secret（机器人个人访问令牌）认证
- 使用固定分支名 `update-nbviewer`（幂等，重复运行更新同一PR）

### 所需Secrets

| Secret | 用途 |
|--------|------|
| `GITHUB_TOKEN` | 自动提供，用于调用GitHub API |
| `BOT_PAT` | 机器人PAT，用于创建PR |

## pre-commit 代码质量

每次提交前自动运行代码检查和格式化：

| Hook | 工具 | 功能 |
|------|------|------|
| ruff | ruff-pre-commit v0.14.3 | Python lint，自动修复（--fix --show-fixes） |
| ruff-format | ruff-pre-commit v0.14.3 | Python代码格式化 |
| prettier | mirrors-prettier v3.6.2 | Markdown/YAML/JavaScript格式化 |
| end-of-file-fixer | pre-commit-hooks v6.0.0 | 确保文件末尾有换行 |
| check-executables-have-shebangs | pre-commit-hooks v6.0.0 | 可执行文件必须有shebang |

**排除规则**：`exclude: "(.*/)?secrets/.*"` 排除加密文件。

pre-commit.ci 每月自动更新hooks版本。

安装hooks：
```bash
pip install pre-commit
pre-commit install
```

## Dependabot

每月检查两类依赖更新：

| 生态系统 | 目录 | 限制 |
|---------|------|------|
| pip | `/` | 最多3个并发PR |
| github-actions | `/` | 最多3个并发PR |

Dependabot PR需要人工审查和合并。

## 自动化全景

```
┌─────────────────────────────────────────────────────┐
│                  日常自动化                           │
│                                                      │
│  每日5:00                                            │
│  watch-dependencies                                  │
│    │                                                 │
│    ├─ 有更新? ──否──→ 无操作                          │
│    │                                                 │
│    └─是→ 创建update-nbviewer PR                      │
│           │                                          │
│           ▼                                          │
│      人工审查PR                                      │
│           │                                          │
│           ▼ 合并到main                               │
│      cd.yml 触发                                     │
│           │                                          │
│           ├─ 检出代码+helm/kubectl                   │
│           ├─ git-crypt解锁                           │
│           ├─ bash deploy.sh                          │
│           └─ pytest冒烟测试                          │
│                                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  辅助自动化                           │
│                                                      │
│  每次git commit → pre-commit hooks (lint+format)     │
│  每月 → Dependabot检查pip和GitHub Actions更新        │
│  每月 → pre-commit.ci更新hooks版本                   │
└─────────────────────────────────────────────────────┘
```

## 手动干预场景

尽管大部分流程自动化，以下场景需要手动操作：

| 场景 | 操作 |
|------|------|
| 紧急回滚 | 手动revert PR或直接编辑config/nbviewer.yaml回退镜像tag |
| 后端IP变更 | 编辑tasks.py中all_instances()，运行invoke fastly |
| Cloudflare DNS变更 | 在Cloudflare Dashboard手动更新DNS记录 |
| 密钥轮换 | 更新git-crypt加密文件，重新提交 |
| 部署失败排查 | 检查cd.yml Actions日志，手动运行deploy.sh调试 |

## 相关文档

- [Helm部署流程](06-helm-deploy-process.md)
- [版本更新机制](05-version-update.md)
- [测试与密钥管理](08-testing-and-secrets.md)
- [CI/CD信源](/references/cicd-source.md)
