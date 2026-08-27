---
okf_version: "0.2"
type: "concept"
title: "测试与部署"
description: "理解 jupyterlab-probot 的 Jest+nock 测试体系、测试固件编写方法、Docker/Heroku 部署方案、GitHub App 权限配置要求。"
tags: [testing, jest, nock, deployment, docker, heroku, github-app-permissions, ci-cd]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:55:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: test
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/test/index.test.ts"
    title: "test/index.test.ts"
  - id: dockerfile
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/Dockerfile"
    title: "Dockerfile"
  - id: app-yml
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/app.yml"
    title: "app.yml"
  - id: jest-config
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/jest.config.js"
    title: "jest.config.js"
  - id: workflow
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/.github/workflows/test.yml"
    title: ".github/workflows/test.yml"
---

# 测试与部署

## 测试体系

jupyterlab-probot 使用 **Jest** 作为测试框架，**nock** 用于拦截 HTTP 请求，**ts-jest** 支持直接测试 TypeScript 源码。

### 测试命令

```bash
# 运行所有测试
npm test

# 运行测试并收集覆盖率（启用 DEBUG 模式）
npm run test:cov
```

`test:cov` 命令设置了 `DEBUG=true` 环境变量，会将调试信息写入 `outputs.txt`。

### 测试文件结构

```
test/
├── fixtures/                    # 测试固件（模拟数据）
│   ├── duplicate_pull_requests.json
│   ├── duplicate_pushes.json
│   ├── issue_comment.created.json
│   ├── issue_labelled.opened.json
│   ├── issue_no_label.opened.json
│   ├── mock-cert.pem           # 模拟私钥（测试用）
│   └── pull_request.opened.json
└── index.test.ts               # 测试文件（12个测试用例）
```

### 测试架构

每个测试用例遵循 Probot 测试的标准模式：

```typescript
describe("My Probot app", () => {
  let probot: any;

  beforeEach(() => {
    nock.disableNetConnect();  // 禁止真实网络请求
    probot = new Probot({
      appId: 123,
      privateKey,              // 使用模拟私钥
      Octokit: ProbotOctokit.defaults({
        retry: { enabled: false },    // 禁用重试
        throttle: { enabled: false }, // 禁用限流
      }),
    });
    probot.load(myProbotApp);  // 加载应用
  });

  test('test case name', async () => {
    // 1. 设置 nock mock（配置 API + 期望 API）
    const mock = nock("https://api.github.com")
      .get("/repos/.../contents/.github%2Fjupyterlab-probot.yml")
      .reply(200, configBuffer)
      .post("/repos/.../issues/.../labels")
      .reply(200);

    // 2. 模拟 Webhook 事件
    await probot.receive({ name: "issues", payload: openedIssueNoLabel });

    // 3. 验证所有 mock 都被调用
    expect(mock.pendingMocks()).toStrictEqual([]);
  });

  afterEach(() => {
    nock.cleanAll();         // 清理 mock
    nock.enableNetConnect(); // 恢复网络连接
  });
});
```

### 关键测试技术

1. **nock HTTP 拦截**：所有对 `https://api.github.com` 的请求都被 nock 拦截，返回预设响应。这确保测试不依赖网络，快速且确定性。

2. **测试固件**：`test/fixtures/` 目录下的 JSON 文件是真实 GitHub Webhook payload 的录制，包含各种事件场景的数据。新增测试时通常需要添加对应的固件。

3. **Mock 私钥**：`mock-cert.pem` 是一个测试用的 RSA 私钥，仅用于 Probot 实例化，不会用于真实认证。

4. **`pendingMocks()` 验证**：每个测试最后调用 `expect(mock.pendingMocks()).toStrictEqual([])` 确保所有注册的 mock 都被调用了。如果有未被调用的 mock，说明代码逻辑有问题。

5. **禁用重试和限流**：测试时创建 Probot 实例时禁用了 Octokit 的重试（`retry: { enabled: false }`）和限流（`throttle: { enabled: false }`），避免测试中的意外等待。

### 12个测试用例覆盖

| # | 测试名 | 测试场景 | 对应功能 |
|---|--------|---------|---------|
| 1 | `add triage label to opened issue` | 配置了 triageLabel，新 Issue 无标签 → 添加标签 | Triage 标签 |
| 2 | `does not add triage label when config lacks triageLabel` | 无 triageLabel 配置 → 不添加标签 | Triage 标签 |
| 3 | `does not add triage label to opened issue that has it already` | Issue 已有标签 → 不重复添加 | Triage 标签 |
| 4 | `does not create a comment with a binder link` | 未配置 addBinderLink → 不创建评论 | Binder 链接 |
| 5 | `creates a comment with a binder link` | 配置了 addBinderLink → 创建评论 | Binder 链接 |
| 6 | `handles bad config` | 配置类型错误（binderUrlSuffix 是数字）→ 不崩溃 | 配置验证 |
| 7 | `cancels duplicate push runs` | push 事件触发，有重复运行 → 取消旧运行 | CI 去重 |
| 8 | `cancels duplicate pull_request runs` | PR 事件触发，有重复运行 → 取消旧运行 | CI 去重 |
| 9 | `no-op when there are no duplicate pull_request runs` | PR 事件触发，无重复运行 → 无操作 | CI 去重 |
| 10 | `it should handle a restart comment` | 正确格式的重启评论 → close+open | 重启 CI |
| 11 | `it should handle a restart comment for no config` | 无配置文件 → 默认 botUser，仍然响应 | 重启 CI |
| 12 | `it should ignore a non-comment` | 不匹配的评论 → 忽略 | 重启 CI |
| 13 | `it should handle bot config for restart comment` | 自定义 botUser → 正确响应 | 重启 CI |

### 覆盖率阈值

项目虽然没有在 jest 配置中显式设置覆盖率阈值，但从测试用例覆盖来看，核心逻辑覆盖率很高。`/* istanbul ignore if */` 注释标记了难以测试的防御性分支。

### CI/CD 流水线

项目配置了 GitHub Actions 工作流（`.github/workflows/test.yml`），在 push 和 PR 时自动运行测试。

## 部署方案

### Docker 部署（推荐生产方案）

Dockerfile 基于 `node:18-slim`：

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

**构建和运行**：

```bash
# 构建
docker build -t jupyterlab-probot .

# 运行（传入环境变量）
docker run -d \
  -e APP_ID=<your-app-id> \
  -e PRIVATE_KEY="$(cat private-key.pem)" \
  -e WEBHOOK_SECRET=<your-webhook-secret> \
  -p 3000:3000 \
  jupyterlab-probot
```

**Docker 部署要点**：
- 使用 `npm ci --production` 安装生产依赖，确保版本锁定
- `npm cache clean --force` 减小镜像体积
- 设置 `NODE_ENV=production` 启用生产模式
- 私钥通过环境变量 `PRIVATE_KEY` 传入
- 容器暴露 3000 端口（Probot 默认端口）
- 需要反向代理（如 nginx）处理 HTTPS 和 Webhook 转发

### Heroku 部署

README 推荐 Heroku 部署，因为 Probot 原生支持 Heroku：

```bash
# 添加 heroku 远程
heroku create jupyterlab-probot

# 部署
git push heroku main

# 配置环境变量
heroku config:set APP_ID=<app-id>
heroku config:set PRIVATE_KEY="$(cat private-key.pem)"
heroku config:set WEBHOOK_SECRET=<secret>
heroku config:set LOG_LEVEL=trace

# 查看日志
heroku logs --tail
```

Heroku 会自动检测 Node.js 应用，运行 `npm start`，并提供 HTTPS 端点。

### 其他部署方式

Probot 应用可以部署在任何支持 Node.js 的平台上：
- **AWS Lambda / Vercel / Netlify**：Serverless 部署（需要适配）
- **自建服务器**：使用 PM2 或 systemd 管理进程
- **Railway / Render / Fly.io**：现代 PaaS 平台

## GitHub App 权限配置

创建 GitHub App 时需要配置正确的权限和事件订阅。参考 app.yml：

### 必需权限

| 权限 | 访问级别 | 用途 |
|------|---------|------|
| Issues | Read & write | 添加标签、创建评论、关闭/打开 Issue |
| Metadata | Read-only | 基础仓库元数据访问（必须启用） |

### 需要额外启用的权限（根据功能）

| 权限 | 访问级别 | 功能 |
|------|---------|------|
| Pull requests | Read & write | Binder 链接评论（PR opened 事件） |
| Actions | Read & write | CI 重复运行取消 |

### 需要订阅的事件

| 事件 | 功能 |
|------|------|
| Issues | Issue 打开（Triage 标签） |
| Pull request | PR 打开（Binder 链接） |
| Issue comment | 评论创建（重启 CI 命令） |
| Workflow run | Workflow 运行请求（CI 去重） |

> **注意**：app.yml 中默认只启用了 `issues` 事件，其他事件需要手动启用。这是因为不同功能需要的权限不同，可以按需开启。

### Webhook 配置

- **Webhook URL**：部署后可公开访问的 HTTPS URL（如 `https://your-app.example.com/`）
- **Webhook Secret**：自定义密钥，与 `WEBHOOK_SECRET` 环境变量一致
- **SSL 验证**：启用（确保 Webhook 安全）

## 环境变量清单

| 变量 | 必填 | 说明 |
|------|------|------|
| `APP_ID` | ✅ | GitHub App ID |
| `PRIVATE_KEY` | ✅ 或 `PRIVATE_KEY_PATH` | PEM 格式私钥内容 |
| `PRIVATE_KEY_PATH` | ✅ 或 `PRIVATE_KEY` | PEM 私钥文件路径 |
| `WEBHOOK_SECRET` | ✅ | Webhook 签名验证密钥 |
| `LOG_LEVEL` | ❌ | 日志级别（trace/debug/info/warn/error/fatal） |
| `DEBUG` | ❌ | 设为 `true` 启用调试输出到 outputs.txt |
| `NODE_ENV` | ❌ | 设为 `production` 生产模式 |
| `PORT` | ❌ | HTTP 端口（默认 3000） |
| `WEBHOOK_PROXY_URL` | ❌ | Smee.io 代理 URL（本地开发用） |

## 下一步

- → 返回 [教程首页](../index.md)
- → [本地开发环境搭建与调试](../examples/01-local-setup.md)：完整的本地开发和调试指南
