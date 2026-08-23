---
okf_version: "0.2"
type: "concept"
title: "CLI与GitHub Action集成"
description: "commander命令行接口设计、composite action编排、私钥安全处理、CI/CD流水线、本地开发与部署模式"
tags: [cli, commander, github-action, composite-action, cicd, deployment, security]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: main-source
    resource: /references/main-source.md
    title: "入口与CLI源码"
  - id: action-yml
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/action.yml"
    title: "action.yml"
  - id: ci-yaml
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/.github/workflows/ci.yaml"
    title: ".github/workflows/ci.yaml"
  - id: run-yaml
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/.github/workflows/run.yaml"
    title: ".github/workflows/run.yaml"
---

# CLI与GitHub Action集成

pr-triage-board-bot提供两种运行方式：本地CLI脚本和GitHub Action定时任务。CLI基于commander框架，Action采用composite类型编排构建和运行步骤。

## CLI设计

### commander配置

```typescript
program
    .option("--dry-run", "Do not actually make any changes")
    .option("--gh-app-id <number>", "GitHub App ID", parseInt)
    .option("--gh-app-installation-id <number>", "GitHub App Installation ID", parseInt)
    .option("--gh-app-pem-file <string>", "Path to .pem file containing private key")
    .option("--repositories <repos>", "Comma-separated list of repository names")
    .argument("<organization>")
    .argument("<projectNumber>")
    .action(async (organization, projectNumber) => {
        const options = program.opts();
        const repositories = options.repositories
            ? options.repositories.split(',').map((repo: string) => repo.trim())
            : undefined;
        await main(organization, parseInt(projectNumber), makeOctokit(
            options.ghAppId,
            options.ghAppInstallationId,
            options.ghAppPemFile
        ), repositories, options.dryRun);
    });

program.parse();
```

### CLI参数详解

| 参数 | 类型 | 是否必填 | 默认值 | 说明 |
|------|------|---------|--------|------|
| `<organization>` | argument | ✅ | - | GitHub组织名 |
| `<projectNumber>` | argument | ✅ | - | 项目板编号（URL中projects/<N>） |
| `--gh-app-id` | number option | ✅ | - | GitHub App ID |
| `--gh-app-installation-id` | number option | ✅ | - | GitHub App Installation ID |
| `--gh-app-pem-file` | string option | ✅ | - | 私钥.pem文件路径 |
| `--repositories` | string option | ❌ | 全组织 | 逗号分隔仓库名，如 `repo1,repo2` |
| `--dry-run` | boolean flag | ❌ | false | 试运行模式 |

### 参数处理细节

- **数字参数**：`--gh-app-id` 和 `--gh-app-installation-id` 使用 `parseInt` 作为coerce函数，自动将字符串转为数字
- **仓库列表**：`--repositories` 传入逗号分隔字符串，在action handler中通过 `split(',').map(repo => repo.trim())` 解析为数组，并trim空格
- **projectNumber**：作为argument接收为字符串，在调用main时通过 `parseInt(projectNumber)` 转为数字

### 本地运行命令

```bash
# 完整运行
node dist/src/main.js \
  --gh-app-id 12345 \
  --gh-app-installation-id 67890 \
  --gh-app-pem-file ./private-key.pem \
  my-org 1

# 限定仓库
node dist/src/main.js \
  --gh-app-id 12345 \
  --gh-app-installation-id 67890 \
  --gh-app-pem-file ./private-key.pem \
  --repositories repo1,repo2,repo3 \
  my-org 1

# 试运行
node dist/src/main.js \
  --gh-app-id 12345 \
  --gh-app-installation-id 67890 \
  --gh-app-pem-file ./private-key.pem \
  --dry-run \
  my-org 1
```

## GitHub Action设计

### Action类型：composite

action.yml声明为 `composite` 类型而非JavaScript Action，原因：
- 需要先执行 `npm ci` 安装依赖和 `npm run build` 编译TypeScript
- composite类型允许多个run步骤编排
- 不需要将node_modules打包到发布分支

### Action步骤编排

```yaml
runs:
  using: 'composite'
  steps:
    # 步骤1：复制package-lock.json到WORKSPACE（npm缓存hack）
    - name: copy package-lock.json for npm caching
      run: cp ${{ github.action_path }}/package-lock.json pr-triage-bot-package-lock.json
      shell: bash

    # 步骤2：设置Node.js
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        cache: 'npm'
        node-version: ${{ inputs.node-version }}
        cache-dependency-path: pr-triage-bot-package-lock.json

    # 步骤3：安装依赖
    - name: Install dependencies
      run: npm ci
      shell: bash
      working-directory: ${{ github.action_path }}

    # 步骤4：构建项目
    - name: Build project
      run: npm run build
      shell: bash
      working-directory: ${{ github.action_path }}

    # 步骤5：写入私钥到临时文件
    - name: Setup GitHub App Private Key
      run: echo "${{ inputs.gh-app-private-key }}" > private-key.pem
      shell: bash
      working-directory: ${{ github.action_path }}

    # 步骤6：运行机器人（条件分支处理repositories参数）
    - name: Run PR Triage Bot
      run: |
        if [ -n "${{ inputs.repositories }}" ]; then
          node dist/src/main.js \
            --gh-app-id ${{ inputs.gh-app-id }} \
            --gh-app-installation-id ${{ inputs.gh-app-installation-id }} \
            --gh-app-pem-file private-key.pem \
            --repositories "${{ inputs.repositories }}" \
            ${{ inputs.organization }} ${{ inputs.project-number }}
        else
          node dist/src/main.js \
            --gh-app-id ${{ inputs.gh-app-id }} \
            --gh-app-installation-id ${{ inputs.gh-app-installation-id }} \
            --gh-app-pem-file private-key.pem \
            ${{ inputs.organization }} ${{ inputs.project-number }}
        fi
      shell: bash
      working-directory: ${{ github.action_path }}

    # 步骤7：清理私钥（always执行）
    - name: Cleanup private key
      run: rm -f private-key.pem
      shell: bash
      if: ${{ always() }}
      working-directory: ${{ github.action_path }}
```

### package-lock.json缓存Hack

步骤1是一个workaround：GitHub Actions的 `setup-node` 的npm缓存功能使用 `hashFiles()` 计算缓存键，但 `hashFiles()` 只能hash WORKSPACE目录（调用workflow的仓库）中的文件，无法hash action自身目录中的package-lock.json。因此需要先将package-lock.json复制到WORKSPACE目录，缓存才能正确工作。

这在action.yml中有注释说明，引用了GitHub toolkit的issue讨论。

### 私钥安全处理

私钥处理流程：
1. **传入**：通过GitHub Secret（`${{ secrets.GH_APP_PRIVATE_KEY }}`）传入，值不会在日志中暴露
2. **写入**：通过 `echo "..." > private-key.pem` 写入action目录的临时文件
3. **使用**：CLI通过 `--gh-app-pem-file private-key.pem` 读取
4. **清理**：`if: always()` 确保无论成功失败都执行 `rm -f private-key.pem`

> ⚠️ private-key.pem在action运行期间存在于文件系统中，但由于GitHub Actions runner是临时VM，任务结束后销毁，风险可控。

### Action输入

| 输入 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `organization` | ✅ | - | GitHub组织名 |
| `project-number` | ✅ | - | 项目板编号 |
| `gh-app-id` | ✅ | - | GitHub App ID |
| `gh-app-installation-id` | ✅ | - | GitHub App Installation ID |
| `gh-app-private-key` | ✅ | - | 私钥PEM内容（通过Secret传入） |
| `repositories` | ❌ | - | 逗号分隔仓库名 |
| `node-version` | ❌ | `23.x` | Node.js版本 |

## CI/CD流水线

### CI流水线（ci.yaml）

```yaml
on: pull_request (branches: [main])
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4 (node: 23.x, cache: npm)
      - run: npm ci
      - run: npm run typecheck
      - run: npm run build
```

CI检查三个方面：依赖安装成功、TypeScript类型检查通过、SWC编译成功。注意：项目没有单元测试。

### 自身运行workflow（run.yaml）

```yaml
on:
  schedule:
    - cron: '13 * * * *'  # 每小时运行（第13分钟）
  workflow_dispatch:      # 手动触发
  push:
    branches: ["main"]    # main分支推送时也运行

jobs:
  jupyterhub:
    steps:
      - uses: yuvipanda/pr-triage-board-bot@main
        with:
          organization: 'jupyterhub'
          project-number: '4'
          gh-app-id: '1793875'
          gh-app-installation-id: '81302562'
          gh-app-private-key: ${{ secrets.GH_APP_PRIVATE_KEY }}
```

这是项目自身用来维护JupyterHub组织看板的workflow，配置为每小时运行。

## 构建系统

### 编译工具链

- **SWC**（Speedy Web Compiler）：用于快速编译TypeScript→JavaScript
  - 配置文件：`.swcrc`（target: es2024, TypeScript parser）
  - 编译命令：`swc src/ --copy-files --delete-dir-on-start -d dist`
  - `--copy-files` 复制.gql等非TS文件
  - `--delete-dir-on-start` 编译前清空dist目录
- **TypeScript编译器（tsc）**：仅用于类型检查（`tsc --noEmit`），不生成JS文件
- **watch模式**：`build:watch` 使用SWC的--watch标志，文件变更时自动重新编译

### package.json脚本

| 脚本 | 命令 | 用途 |
|------|------|------|
| `start` | `swc ... && node dist/src/main.js` | 编译+运行 |
| `build` | `swc src/ ... -d dist` | 编译 |
| `build:watch` | `swc ... --watch` | 监听模式编译 |
| `typecheck` | `tsc --noEmit` | 类型检查 |

### 输出目录结构

编译后 `dist/` 目录结构与 `src/` 一致：
```
dist/
└── src/
    ├── main.js
    ├── project.js
    ├── utils.js
    ├── fieldconfig.js
    ├── fields/*.js
    └── graphql/*.gql  (--copy-files复制)
```

运行入口为 `node dist/src/main.js`。

## 部署模式对比

| 维度 | 本地CLI | GitHub Action |
|------|---------|--------------|
| 触发方式 | 手动 | 定时（cron）/手动/push |
| 私钥管理 | 本地.pem文件 | GitHub Secrets |
| 运行环境 | 本地Node.js | GitHub Ubuntu runner |
| 依赖安装 | npm install | npm ci（干净安装） |
| 适用场景 | 调试、首次设置、dry run验证 | 生产定时运行 |
| Dry run | 支持 | 不支持（需要修改workflow） |

## 相关概念

- [GitHub App认证与Octokit配置](03-auth-and-octokit.md)
- [同步循环与增量更新](07-sync-loop.md)
- [5分钟快速上手](01-getting-started.md)
