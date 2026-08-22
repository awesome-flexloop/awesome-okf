---
okf_version: "0.2"
type: "reference"
title: "配置 Schema 与 GitHub App 清单"
description: "jupyterlab-probot 的 schema.json 配置验证规则、app.yml GitHub App 权限清单、环境变量说明等配置相关信源。"
tags: [config, schema, app-yml, permissions, environment-variables, json-schema]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:55:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: schema
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/schema.json"
    title: "schema.json"
  - id: app-yml
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/app.yml"
    title: "app.yml"
  - id: dockerfile
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/Dockerfile"
    title: "Dockerfile"
---

# 配置 Schema 与 GitHub App 清单

本文档汇总 jupyterlab-probot 的所有配置相关信源文件。

## schema.json（JSON Schema 配置验证）

> 源码路径：`external/libs/jupyter/jupyterlab-probot/schema.json`

```json
{
  "title": "JupyterLab Probot Configuration",
  "description": "JupyterLab Probo configuration metadata",
  "properties": {
    "addBinderLink": {
      "title": "Add Binder Link",
      "description": "Add a binder link PR comment",
      "type": "boolean"
    },
    "binderUrlSuffix": {
      "title": "Binder URL Suffix",
      "description": "Suffix for Binder URL",
      "type": "string"
    },
    "triageLabel": {
      "title": "Triage label",
      "description": "Triage label to apply on newly opened issues",
      "type": "string"
    },
    "botUser": {
      "title": "Bot user name",
      "description": "The name of the bot user for issue comments",
      "type": "string",
      "default": "jupyterlab-bot"
    }
  },
  "additionalProperties": false,
  "type": "object"
}
```

### Schema 字段说明

| 字段 | JSON 类型 | 默认值 | 可选 | 说明 |
|------|----------|--------|------|------|
| `addBinderLink` | boolean | 无 | ✅ | 为 true 时在新 PR 上评论 Binder 链接 |
| `binderUrlSuffix` | string | `""`（代码中） | ✅ | Binder URL 后缀，如 `?urlpath=lab-dev` |
| `triageLabel` | string | 无 | ✅ | 新 Issue 自动添加的标签名 |
| `botUser` | string | `"jupyterlab-bot"` | ✅ | Bot 用户名，用于重启 CI 命令识别 |

### Schema 设计要点

1. **所有字段可选**：没有 `required` 数组，配置文件可以为空或只包含部分字段
2. **禁止额外字段**：`"additionalProperties": false` 防止拼写错误（如 `triageLabal`）
3. **唯一默认值**：只有 `botUser` 有 `"default": "jupyterlab-bot"`，通过 AJV 的 `useDefaults: true` 自动填充
4. **类型严格**：不接受隐式类型转换（如数字 `1` 不会被当作 `true`）

---

## app.yml（GitHub App Manifest）

> 源码路径：`external/libs/jupyter/jupyterlab-probot/app.yml`

这是 GitHub App 的清单文件，定义了 App 的默认权限和事件订阅。**注意**：此文件是模板参考，实际权限需要在 GitHub App 设置页面手动配置。

### 默认订阅事件

```yaml
default_events:
  - issues          # Issue 事件（Triage 标签功能必需）
  # 以下事件默认注释掉，需要手动启用：
  # - issue_comment   # Issue 评论（重启 CI 功能必需）
  # - pull_request    # PR 事件（Binder 链接功能必需）
  # - workflow_run    # Workflow 运行（CI 去重功能必需）
```

### 默认权限

```yaml
default_permissions:
  issues: write       # 添加标签、创建评论、关闭/打开 Issue/PR（必需）
  metadata: read      # 基础仓库元数据（GitHub 要求必须启用）
  # 以下权限默认注释掉，需要手动启用：
  # pull_requests: read  # Binder 链接功能需要读取 PR 信息
  # actions: write       # CI 去重功能需要取消 Workflow Run
```

### 启用所有功能所需的完整权限

| 权限 | 访问级别 | 功能 |
|------|---------|------|
| Issues | Read & write | Triage 标签 + Binder 评论 + 重启 CI |
| Metadata | Read-only | 基础元数据（必须） |
| Pull requests | Read & write | Binder 链接（读取 PR head 信息） |
| Actions | Read & write | CI 去重（取消 Workflow Run） |

### 启用所有功能所需的事件订阅

| 事件 | 功能 |
|------|------|
| Issues | Triage 标签 |
| Pull request | Binder 链接 |
| Issue comment | 重启 CI 命令 |
| Workflow run | CI 去重 |

---

## Dockerfile（容器化配置）

> 源码路径：`external/libs/jupyter/jupyterlab-probot/Dockerfile`

```dockerfile
FROM node:18-slim
WORKDIR /usr/src/app
COPY package.json package-lock.json ./
RUN npm ci --production
RUN npm cache clean --force
ENV NODE_ENV="production"
COPY . .
CMD [ "npm", "start" ]
```

### Dockerfile 说明

| 层 | 指令 | 说明 |
|----|------|------|
| 1 | `FROM node:18-slim` | 基于 Node.js 18 slim 镜像（Debian slim，体积小） |
| 2 | `WORKDIR /usr/src/app` | 设置工作目录 |
| 3 | `COPY package*.json ./` | 先复制依赖文件（利用 Docker 层缓存） |
| 4 | `RUN npm ci --production` | 使用 `npm ci` 安装锁定版本的生产依赖 |
| 5 | `RUN npm cache clean --force` | 清理 npm 缓存减小镜像体积 |
| 6 | `ENV NODE_ENV="production"` | 设置生产环境变量 |
| 7 | `COPY . .` | 复制项目文件（含编译后的 lib/） |
| 8 | `CMD ["npm", "start"]` | 启动命令（执行 `probot run ./lib/index.js`） |

> **注意**：Dockerfile 中没有 TypeScript 编译步骤。构建 Docker 镜像前需要先在本地运行 `npm run build` 编译 TypeScript 到 `lib/` 目录，然后 `COPY . .` 会将编译产物复制到镜像中。

---

## .env.example（环境变量模板）

> 源码路径：`external/libs/jupyter/jupyterlab-probot/.env.example`

标准 Probot 应用需要以下环境变量：

| 变量 | 说明 | 必填 |
|------|------|------|
| `APP_ID` | GitHub App 的 ID | ✅ |
| `PRIVATE_KEY` | PEM 格式私钥内容（与 PRIVATE_KEY_PATH 二选一） | ✅* |
| `PRIVATE_KEY_PATH` | PEM 私钥文件路径（与 PRIVATE_KEY 二选一） | ✅* |
| `WEBHOOK_SECRET` | Webhook 签名验证密钥 | ✅ |
| `WEBHOOK_PROXY_URL` | Smee.io 代理 URL（仅本地开发） | ❌ |
| `LOG_LEVEL` | 日志级别（trace/debug/info/warn/error/fatal） | ❌ |
| `PORT` | HTTP 服务端口（默认 3000） | ❌ |
| `NODE_ENV` | 运行环境（production/development） | ❌ |
| `DEBUG` | 设为 `true` 启用调试输出 | ❌ |

---

## package.json（项目元信息）

> 源码路径：`external/libs/jupyter/jupyterlab-probot/package.json`

### 脚本命令

| 命令 | 实际执行 | 说明 |
|------|---------|------|
| `npm run build` | `tsc` | 编译 TypeScript 到 lib/ |
| `npm start` | `probot run ./lib/index.js` | 启动 Probot 应用 |
| `npm test` | `jest` | 运行测试 |
| `npm run test:cov` | `DEBUG=true; jest --collect-coverage --clear-cache` | 运行测试+覆盖率（启用DEBUG） |
| `npm run watch` | `tsc -w` | TypeScript watch 模式 |

### 依赖版本

| 包名 | 版本 | 类型 |
|------|------|------|
| `probot` | ^12.3.1 | 生产依赖 |
| `ajv` | ^8.6.2 | 生产依赖 |
| `typescript` | ^4.1.3 | 开发依赖 |
| `jest` | ^26.6.3 | 开发依赖 |
| `ts-jest` | ^26.4.4 | 开发依赖 |
| `nock` | ^13.0.5 | 开发依赖 |
| `smee-client` | ^1.2.2 | 开发依赖 |
| `@types/jest` | ^26.0.19 | 开发依赖 |
| `@types/node` | ^14.14.19 | 开发依赖 |
