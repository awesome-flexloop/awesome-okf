---
okf_version: "0.2"
type: "example"
title: "GitHub Action部署workflow配置"
description: "完整的GitHub Actions workflow配置示例，包含定时运行、手动触发、多仓库/多看板部署"
tags: [github-action, workflow, deployment, scheduled, cron]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: concepts-cli-action
    resource: /concepts/08-cli-and-action.md
    title: "CLI与GitHub Action集成"
  - id: concepts-getting-started
    resource: /concepts/01-getting-started.md
    title: "5分钟快速上手"
---

# GitHub Action部署workflow配置

本示例提供完整的GitHub Actions workflow配置，用于定时运行pr-triage-board-bot同步PR看板。

## 基础配置：单组织单看板

```yaml
# .github/workflows/pr-triage.yml
name: PR Triage Board Sync

on:
  schedule:
    - cron: '13 * * * *'  # 每小时第13分钟运行
  workflow_dispatch:      # 支持手动触发
  push:
    branches: ["main"]    # 推送到main时也运行（便于验证配置变更）

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Run PR Triage Bot
        uses: yuvipanda/pr-triage-board-bot@main
        with:
          organization: 'your-org'
          project-number: '1'
          gh-app-id: ${{ secrets.GH_APP_ID }}
          gh-app-installation-id: ${{ secrets.GH_APP_INSTALLATION_ID }}
          gh-app-private-key: ${{ secrets.GH_APP_PRIVATE_KEY }}
```

## 需要配置的Secrets

在仓库 **Settings → Secrets and variables → Actions** 中添加：

| Secret名 | 值 | 获取方式 |
|----------|---|---------|
| `GH_APP_ID` | App ID数字 | GitHub App设置页面 |
| `GH_APP_INSTALLATION_ID` | Installation ID数字 | 安装URL中的数字 |
| `GH_APP_PRIVATE_KEY` | PEM私钥完整内容 | 下载.pem文件后复制全部内容 |

> ⚠️ `gh-app-private-key` 是通过Secret传入的**私钥内容**（不是文件路径），action内部会自动写入临时文件。

## 限定特定仓库

如果只想监控部分仓库（而非组织全部）：

```yaml
      - name: Run PR Triage Bot
        uses: yuvipanda/pr-triage-board-bot@main
        with:
          organization: 'your-org'
          project-number: '1'
          gh-app-id: ${{ secrets.GH_APP_ID }}
          gh-app-installation-id: ${{ secrets.GH_APP_INSTALLATION_ID }}
          gh-app-private-key: ${{ secrets.GH_APP_PRIVATE_KEY }}
          repositories: 'repo1,repo2,repo3'  # 逗号分隔
```

## 多看板部署

如果组织有多个项目板（如一个给JupyterHub，一个给JupyterLab）：

```yaml
jobs:
  jupyterhub-board:
    runs-on: ubuntu-latest
    steps:
      - name: Sync JupyterHub board
        uses: yuvipanda/pr-triage-board-bot@main
        with:
          organization: 'jupyterhub'
          project-number: '4'
          gh-app-id: ${{ secrets.GH_APP_ID }}
          gh-app-installation-id: ${{ secrets.JUPYTERHUB_INSTALLATION_ID }}
          gh-app-private-key: ${{ secrets.GH_APP_PRIVATE_KEY }}

  jupyterlab-board:
    runs-on: ubuntu-latest
    steps:
      - name: Sync JupyterLab board
        uses: yuvipanda/pr-triage-board-bot@main
        with:
          organization: 'jupyterlab'
          project-number: '11'
          gh-app-id: ${{ secrets.GH_APP_ID }}
          gh-app-installation-id: ${{ secrets.JUPYTERLAB_INSTALLATION_ID }}
          gh-app-private-key: ${{ secrets.GH_APP_PRIVATE_KEY }}
```

> 💡 如果不同组织的看板使用同一个GitHub App，只需要不同的installation ID（每个组织安装一次App会产生不同的ID）。如果使用不同的App，则需要配置不同的App ID和私钥。

## Dry Run验证模式

首次部署建议先添加一个dry run workflow验证配置：

```yaml
on:
  workflow_dispatch:  # 仅手动触发

jobs:
  dry-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '23.x'
      - name: Install and build
        run: |
          git clone https://github.com/yuvipanda/pr-triage-board-bot.git
          cd pr-triage-board-bot
          npm ci
          npm run build
      - name: Setup private key
        run: echo "${{ secrets.GH_APP_PRIVATE_KEY }}" > pr-triage-board-bot/private-key.pem
      - name: Dry run
        run: |
          cd pr-triage-board-bot
          node dist/src/main.js \
            --gh-app-id ${{ secrets.GH_APP_ID }} \
            --gh-app-installation-id ${{ secrets.GH_APP_INSTALLATION_ID }} \
            --gh-app-pem-file private-key.pem \
            --dry-run \
            your-org 1
      - name: Cleanup
        if: always()
        run: rm -f pr-triage-board-bot/private-key.pem
```

> ⚠️ composite action本身不支持传入--dry-run参数（action.yml没有暴露dry-run输入），所以dry run需要手动clone构建运行。

## Cron调度建议

| 频率 | Cron表达式 | 适用场景 |
|------|-----------|---------|
| 每小时 | `13 * * * *` | 默认推荐（避开整点） |
| 每30分钟 | `7,37 * * * *` | 活跃组织/PR量多 |
| 每2小时 | `17 */2 * * *` | 小型组织 |
| 每天一次 | `31 2 * * *` | 仅每日概览 |

避开整点（如用13分而非0分）可以减少GitHub Actions调度高峰期的延迟。

## 监控运行状态

- **Actions页面**：查看每次运行的日志和状态
- **失败通知**：默认会发邮件通知workflow失败
- **Slack通知**（可选）：在job末尾添加slack通知步骤

```yaml
      - name: Notify Slack on Failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          text: "PR Triage Bot sync failed! Check Actions logs."
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 版本固定

生产环境建议固定到特定版本而非`@main`：

```yaml
        uses: yuvipanda/pr-triage-board-bot@v1.0.0  # 固定版本
```

或使用commit SHA固定：
```yaml
        uses: yuvipanda/pr-triage-board-bot@a1b2c3d4e5f6  # 固定commit
```

## 相关示例

- [GitHub App创建与配置完整流程](01-github-app-setup.md)：部署前先完成App创建和权限配置
- [添加自定义字段扩展](02-adding-custom-field.md)：扩展字段后重新构建和部署Action

## 相关概念

- [CLI与GitHub Action集成](../concepts/08-cli-and-action.md)：action.yml内部步骤、composite编排、构建系统详解
- [同步循环与增量更新](../concepts/07-sync-loop.md)：了解每次Action运行时的同步算法
- [5分钟快速上手](../concepts/01-getting-started.md)：首次部署的完整流程
