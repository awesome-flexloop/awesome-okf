---
okf_version: "0.2"
type: "concept"
title: "5分钟快速上手"
description: "从零开始搭建pr-triage-board-bot：创建GitHub App、复制项目板、本地运行和配置GitHub Action定时执行"
tags: [getting-started, setup, github-app, local-run, action-workflow, dry-run]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/README.md"
    title: "README.md"
  - id: action-yml
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/action.yml"
    title: "action.yml"
  - id: main-source
    resource: /references/main-source.md
    title: "入口与CLI源码"
---

# 5分钟快速上手

## 前置条件

- Node.js 23.x 或更高版本
- 一个GitHub组织账户（非个人账户）
- 在该组织中创建GitHub App的权限

## 步骤一：创建GitHub App

1. 进入组织的 `Settings > Developer Settings > GitHub Apps`（注意不是 `Settings > 3rd Party Access > GitHub Apps`）
2. 点击 "New GitHub App"，填写：
   - **GitHub App Name**：全局唯一名称，如 `[Org Name] PR Triage Bot`
   - **Webhooks**：禁用（Disable webhooks，本项目不用webhook）
3. 配置权限：
   - Repository Permissions → Metadata → **Read-only**（获取仓库协作者列表）
   - Organization Permissions → Members → **Read-only**（获取团队成员）
   - Organization Permissions → Projects → **Read and write**（管理Project看板）
4. "Where can this GitHub App be installed?" 选择 `Only on this account`
5. 创建后在App设置页面：
   - 生成并下载私钥（Private Key，.pem文件）
   - 记录 **App ID**
   - 点击 "Install App" 安装到组织（授权所有仓库访问）
6. 记录Installation ID：在安装设置页面URL末尾的数字，格式为 `https://github.com/organizations/<org>/settings/installations/<installation-id>`

## 步骤二：复制项目板

1. 访问参考项目板（如 [JupyterHub看板](https://github.com/orgs/jupyterhub/projects/4/views/9)）
2. 点击右上角菜单 → "Make a copy" 复制到你的组织
3. 记录复制后的项目编号：URL中 `projects/<project-number>/` 的数字

> 💡 机器人首次运行时会自动创建缺失的字段，因此不需要手动创建所有字段——只需要复制一个包含视图布局的看板即可。

## 步骤三：本地脚本运行

克隆仓库后：

```bash
# 安装依赖
npm install

# 编译TypeScript
npm run build

# 运行机器人
node dist/src/main.js \
  --gh-app-id <github-app-id> \
  --gh-app-installation-id <installation-id> \
  --gh-app-pem-file <path-to-private-key.pem> \
  [--repositories repo1,repo2,repo3] \
  <github-org-name> <project-number>
```

参数说明：
- `--gh-app-id`：步骤一中记录的App ID（数字）
- `--gh-app-installation-id`：步骤一中记录的Installation ID（数字）
- `--gh-app-pem-file`：下载的私钥.pem文件路径
- `--repositories`：可选，逗号分隔的仓库名列表，不指定则查询组织内所有仓库
- `<github-org-name>`：组织名称
- `<project-number>`：步骤二中记录的项目编号

### Dry Run模式

添加 `--dry-run` 参数可以试运行而不实际修改项目板：

```bash
node dist/src/main.js --dry-run \
  --gh-app-id 12345 \
  --gh-app-installation-id 67890 \
  --gh-app-pem-file ./private-key.pem \
  my-org 1
```

Dry run模式会打印将要执行的操作（创建/更新/删除），但不会发送任何GraphQL mutation。

## 步骤四：配置GitHub Action定时运行

1. 在组织的集中管理仓库（如 `.github` 仓库）中创建Organization Secret：
   - 路径：`Org Settings > Secrets and variables > Actions`
   - 名称：`GH_APP_PRIVATE_KEY`
   - 值：私钥.pem文件的全部内容

2. 创建Workflow文件 `.github/workflows/pr-triage.yml`：

```yaml
name: 'Update PR Triage Board'

on:
  schedule:
    - cron: '0 * * * *'  # 每小时运行
  workflow_dispatch:      # 支持手动触发

jobs:
  pr-triage:
    runs-on: ubuntu-latest
    steps:
      - name: Update PR Triage Board
        uses: yuvipanda/pr-triage-board-bot@main
        with:
          organization: 'your-org-name'
          project-number: '1'
          gh-app-id: '12345'
          gh-app-installation-id: '67890'
          gh-app-private-key: ${{ secrets.GH_APP_PRIVATE_KEY }}
          # 可选：限定到特定仓库
          # repositories: 'repo1,repo2'
```

3. 提交后，Action将每小时自动运行一次，也可在Actions页面手动触发。

## 验证运行结果

成功运行后，控制台会输出类似以下的日志：

```
Verifying project fields...
Field already exists: Author Kind
Field already exists: Opened At
...
Field verification complete.
Fetching open PRs...
Fetching existing project items...
Found 42 open PRs and 38 existing project items.
Syncing project fields...
[1 / 5] Removing https://github.com/org/repo/pull/123
[1 / 42] Setting Author Kind to Maintainer for https://github.com/org/repo/pull/456
[2 / 42] Setting CI Status to Tests Passing for https://github.com/org/repo/pull/457
...
Summary: Updated 15 field values, skipped 279 unchanged values
```

访问你的项目板，确认字段已被自动填充。

## 常见问题

**Q: 机器人报错"Resource not accessible by integration"？**
A: 检查GitHub App权限是否配置正确——Projects需要Read and write，Metadata和Members需要Read-only，且App已安装到目标组织。

**Q: 某些PR的字段值为空（null）？**
A: 这是正常的——当CI状态为PENDING、合并状态为UNKNOWN、或没有维护者审查时，对应字段会被清空而非填充错误值。

**Q: 如何限定到特定仓库？**
A: 使用 `--repositories` 参数（CLI）或 `repositories` 输入（Action），逗号分隔仓库名。

## 相关概念

- [pr-triage-board-bot 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [CLI与GitHub Action集成](08-cli-and-action.md)
