---
okf_version: "0.2"
type: "concept"
title: "5分钟快速上手"
description: "从零开始安装依赖、配置环境变量、编译 TypeScript、本地运行 jupyterlab-probot，以及 Docker 部署方法。"
tags: [jupyter, probot, getting-started, setup, installation, docker, npm]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:55:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pkg
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/package.json"
    title: "package.json"
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/README.md"
    title: "README.md"
  - id: dockerfile
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/Dockerfile"
    title: "Dockerfile"
  - id: env-example
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/.env.example"
    title: ".env.example"
---

# 5分钟快速上手

## 前置条件

- **Node.js** ≥ 10.13.0（推荐 18.x，与 Dockerfile 基础镜像一致）
- **npm**（随 Node.js 安装）
- 一个 GitHub 账号，用于创建 GitHub App

## 第1步：克隆仓库并安装依赖

```bash
git clone https://github.com/jupyterlab/jupyterlab-probot.git
cd jupyterlab-probot
npm install
```

这会安装：
- **核心依赖**：`probot` ^12.3.1（GitHub App 框架）、`ajv` ^8.6.2（JSON Schema 验证）
- **开发依赖**：TypeScript ^4.1.3、Jest ^26.6.3、ts-jest ^26.4.4、nock ^13.0.5、smee-client ^1.2.2

## 第2步：编译 TypeScript

```bash
npm run build
```

编译配置（tsconfig.json）：
- 编译目标：ES5 + CommonJS
- 输出目录：`./lib/`
- 启用严格模式（`strict: true`）
- 生成 source map 和 `.d.ts` 声明文件
- 包含 `src/` 目录

开发时可以使用 watch 模式自动重编译：

```bash
npm run watch
```

## 第3步：创建 GitHub App

jupyterlab-probot 需要一个 GitHub App 来接收 Webhook 事件。按照以下步骤创建：

1. 前往 GitHub → Settings → Developer settings → GitHub Apps → New GitHub App
2. 填写基本信息（名称、描述、主页 URL）
3. **Webhook URL**：本地开发时使用 [smee.io](https://smee.io/) 代理（见下方说明）
4. **Webhook Secret**：设置一个密钥，记录下来
5. **权限配置**（参考 app.yml）：
   - Issues: **Read & write**
   - Metadata: **Read-only**
   - Pull requests: **Read & write**（如果需要 Binder 链接功能）
   - Actions: **Read & write**（如果需要 CI 去重功能）
6. **订阅事件**：
   - Issue comment
   - Issues
   - Pull request
   - Workflow run
7. 点击 Create GitHub App
8. 在 App 详情页面，生成并下载私钥（Private Key，PEM 格式）
9. 记录 App ID（在 App 详情页顶部）

## 第4步：配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下必要变量：

```env
# GitHub App ID（从 App 设置页面获取）
APP_ID=123456

# Webhook Secret（创建 App 时设置的密钥）
WEBHOOK_SECRET=your-webhook-secret

# 私钥内容（PEM 格式，可以是文件路径或直接粘贴）
PRIVATE_KEY_PATH=.data/private-key.pem
# 或者直接使用 PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
```

> **注意**：私钥文件不要提交到 Git 仓库。项目已配置 `.gitignore` 忽略 `.data/` 目录。

## 第5步：本地运行（使用 Smee 代理）

本地开发时 GitHub 无法直接向 `localhost` 发送 Webhook，需要使用 [smee.io](https://smee.io/) 代理：

1. 访问 https://smee.io/ ，点击 **Start a new channel**，获取一个 Webhook Proxy URL（如 `https://smee.io/abc123`）
2. 将 GitHub App 的 Webhook URL 设置为该 URL
3. 安装 smee-client（已在 devDependencies 中）
4. 启动代理（在一个终端中）：

```bash
npx smee -u https://smee.io/abc123 -p 3000 -P /
```

5. 在另一个终端中启动 Probot 应用：

```bash
npm start
```

`npm start` 实际执行 `probot run ./lib/index.js`，它会：
- 加载编译后的 JavaScript（`lib/index.js`）
- 读取 `.env` 中的环境变量
- 在 `http://localhost:3000` 启动 Webhook 接收服务
- 验证 GitHub Webhook 签名
- 将事件分发给对应的处理器

## 第6步：验证运行

1. 在目标仓库中创建一个 Issue，应自动添加 triage 标签（如果配置了 `triageLabel`）
2. 创建一个 PR，应自动评论 Binder 链接（如果配置了 `addBinderLink: true`）
3. 多次 push 触发 CI，应自动取消重复运行
4. 在 Issue/PR 下评论 `@jupyterlab-bot, please restart ci`，应触发 close→open

## Docker 部署

项目提供了 Dockerfile（基于 `node:18-slim`），适合生产部署：

```bash
# 构建镜像
docker build -t jupyterlab-probot .

# 运行容器
docker run -e APP_ID=<app-id> -e PRIVATE_KEY="<pem-content>" -e WEBHOOK_SECRET=<secret> jupyterlab-probot
```

Dockerfile 构建流程：
1. 基础镜像 `node:18-slim`
2. 设置工作目录 `/usr/src/app`
3. 复制 `package.json` 和 `package-lock.json`
4. `npm ci --production` 安装生产依赖
5. 清理 npm 缓存
6. 设置 `NODE_ENV=production`
7. 复制项目文件
8. 启动命令 `npm start`

## Heroku 部署

README 推荐使用 Heroku 部署：

```bash
# 首次部署
git push heroku main

# 设置环境变量
heroku config:set LOG_LEVEL=trace
heroku config:set APP_ID=<app-id>
heroku config:set PRIVATE_KEY="$(cat private-key.pem)"
heroku config:set WEBHOOK_SECRET=<secret>

# 查看日志
heroku logs --tail
```

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Error: secret mismatch` | Webhook Secret 不匹配 | 确保 `.env` 中的 `WEBHOOK_SECRET` 与 GitHub App 设置一致 |
| `Error: PEM_read_bio_PrivateKey failed` | 私钥格式错误 | 确保 PEM 文件中换行符正确，或使用 `PRIVATE_KEY` 环境变量 |
| 事件不触发 | Webhook 未送达 | 检查 smee 代理是否运行、GitHub App 的 Webhook URL 是否正确 |
| 标签未添加 | 未配置 `triageLabel` | 在目标仓库创建 `.github/jupyterlab-probot.yml` 配置文件 |

## 下一步

- → [Probot 框架与应用架构](02-probot-architecture.md)：深入理解事件驱动模型
- → [配置系统详解](03-config-system.md)：了解四个配置项的详细用法
- → [本地开发环境搭建与调试](../examples/01-local-setup.md)：完整的本地调试指南
