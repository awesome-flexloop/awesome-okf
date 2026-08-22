---
okf_version: "0.2"
type: "example"
title: "本地开发环境搭建与调试"
description: "从零搭建 jupyterlab-probot 的本地开发环境，包括 GitHub App 创建、Smee.io Webhook 代理、DEBUG 模式调试、事件回放和问题排查。"
tags: [local-development, smee, debug, webhook-proxy, testing, troubleshooting]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:55:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/README.md"
    title: "README.md"
  - id: pkg
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/package.json"
    title: "package.json"
  - id: env-example
    resource: "../../../../../external/libs/jupyter/jupyterlab-probot/.env.example"
    title: ".env.example"
---

# 本地开发环境搭建与调试

## 前置条件

- Node.js ≥ 10.13.0（推荐 18.x）
- npm ≥ 6.x
- 一个 GitHub 账号
- Git

## 完整搭建步骤

### 步骤1：克隆源码并安装依赖

```bash
git clone https://github.com/jupyterlab/jupyterlab-probot.git
cd jupyterlab-probot
npm install
```

验证安装成功：

```bash
npx tsc --version  # 应输出 TypeScript 版本
npx jest --version # 应输出 Jest 版本
```

### 步骤2：创建 GitHub App（开发用）

1. 打开 https://github.com/settings/apps/new
2. 填写基本信息：
   - **GitHub App name**：`jupyterlab-probot-dev-{yourname}`（全局唯一，不能和别人重复）
   - **Homepage URL**：`https://github.com/jupyterlab/jupyterlab-probot`
   - **Webhook URL**：先填 `https://smee.io/`（后面会改）
   - **Webhook secret**：`development`（开发用简单密码，生产环境用强密码）
3. 配置权限：
   - **Issues**: Read & write
   - **Metadata**: Read-only
   - **Pull requests**: Read & write
   - **Actions**: Read & write
4. 订阅事件：
   - ✅ Issue comment
   - ✅ Issues
   - ✅ Pull request
   - ✅ Workflow run
5. 点击 **Create GitHub App**
6. 在 App 页面：
   - 记录 **App ID**（页面顶部的数字）
   - 滚到底部，点击 **Generate a private key**，下载 PEM 文件
   - 点击 **Install App** 左侧菜单，安装到你的测试仓库

### 步骤3：配置 Smee.io Webhook 代理

本地开发时 GitHub 无法向 `localhost` 发送 Webhook，需要 Smee 代理：

1. 访问 https://smee.io/
2. 点击 **Start a new channel**
3. 你会得到一个 URL，如 `https://smee.io/abc123def456`
4. 回到 GitHub App 设置页面，将 **Webhook URL** 更新为这个 Smee URL
5. 在项目目录中启动 Smee 客户端：

```bash
# 安装 smee-client（已在 devDependencies 中）
npx smee -u https://smee.io/abc123def456 -p 3000 -P /
```

这个命令将 Smee 频道上的 Webhook 事件转发到本地 `http://localhost:3000/`。

### 步骤4：配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 复制模板
cp .env.example .env
```

编辑 `.env` 文件：

```env
# GitHub App ID（从 App 设置页面获取）
APP_ID=123456

# Webhook Secret（创建 App 时设置的，开发时用 "development"）
WEBHOOK_SECRET=development

# 私钥文件路径（将下载的 PEM 文件放在项目中的 .data/ 目录下）
PRIVATE_KEY_PATH=.data/private-key.pem

# Smee 代理 URL（开发环境使用）
WEBHOOK_PROXY_URL=https://smee.io/abc123def456

# 日志级别
LOG_LEVEL=debug
```

将下载的私钥 PEM 文件放到 `.data/` 目录：

```bash
mkdir -p .data
# 将下载的 PEM 文件移动到 .data/private-key.pem
mv ~/Downloads/your-app-name.*.private-key.pem .data/private-key.pem
```

> ⚠️ `.data/` 目录已在 `.gitignore` 中，不会被提交。

### 步骤5：编译并启动

打开两个终端：

**终端 1**（Smee 代理，保持运行）：

```bash
npx smee -u https://smee.io/abc123def456 -p 3000 -P /
```

**终端 2**（TypeScript 编译 watch 模式 + Probot 运行）：

```bash
# 编译并启动
npm run build
npm start
```

或者使用 watch 模式自动重编译：

```bash
# 终端 3：watch 模式编译
npm run watch

# 终端 2：运行（编译完成后执行）
npm start
```

启动成功后，你应该看到类似输出：

```
INFO (probot): Yay, the app was loaded!
INFO (probot): Running on http://localhost:3000
```

### 步骤6：在测试仓库中验证

1. 在你安装了 App 的测试仓库中，创建 `.github/jupyterlab-probot.yml`：

```yaml
addBinderLink: true
binderUrlSuffix: "?urlpath=lab"
triageLabel: "needs-triage"
botUser: "jupyterlab-bot"
```

2. 创建一个 Issue，检查是否自动添加了 `needs-triage` 标签
3. 创建一个 PR，检查是否有 Binder 链接评论
4. 在 Issue 下评论 `@jupyterlab-bot, please restart ci`，检查是否触发 close→open

## DEBUG 模式调试

启用 DEBUG 模式可以将完整的 Webhook payload 和 API 响应写入 `outputs.txt` 文件：

```bash
# Linux/Mac
DEBUG=true npm start

# Windows PowerShell
$env:DEBUG="true"; npm start
```

触发事件后，检查 `outputs.txt`：

```bash
cat outputs.txt
```

文件包含：
- Webhook 事件的完整 payload（JSON 格式）
- GitHub API 响应数据
- 用于排查事件处理问题

## 运行测试

```bash
# 运行所有测试
npm test

# 运行测试并查看覆盖率
npm run test:cov
```

测试不依赖网络，使用 nock 拦截 HTTP 请求，可以随时运行。

### 编写新测试

参考现有测试模式，在 `test/index.test.ts` 中添加测试：

```typescript
test('your test name', async () => {
  // 1. 准备配置
  const config = { triageLabel: 'test-label' };
  const configBuffer = Buffer.from(JSON.stringify(config));

  // 2. 设置 nock mock
  const mock = nock("https://api.github.com")
    .persist()
    .post("/app/installations/2/access_tokens")
    .reply(200, { token: "test", permissions: { actions: "write" } })
    .get("/repos/{owner}/{repo}/contents/.github%2Fjupyterlab-probot.yml")
    .reply(200, configBuffer.toString())
    // 添加你期望的 API 调用 mock
    .post("/repos/{owner}/{repo}/issues/{n}/labels")
    .reply(200);

  // 3. 发送模拟事件
  await probot.receive({ name: "issues", payload: testFixture });

  // 4. 验证所有 mock 都被调用
  expect(mock.pendingMocks()).toStrictEqual([]);
});
```

### 使用测试固件

测试固件位于 `test/fixtures/`，是真实 GitHub Webhook 事件的 JSON 录制。如果需要添加新的事件类型：

1. 使用 DEBUG 模式捕获真实事件 payload（保存到 `outputs.txt`）
2. 将 payload JSON 保存为 `test/fixtures/{event-name}.json`
3. 在测试中 import 使用

## 常见问题排查

### 问题1：App 启动但事件不触发

**症状**：Probot 启动正常，但创建 Issue/PR 时没有反应。

**排查步骤**：

1. 检查 Smee 代理是否在运行，是否接收到事件：
   - 访问 Smee URL（如 https://smee.io/abc123def456），可以看到事件列表
   - 如果没有事件 → GitHub App 的 Webhook URL 配置有误
2. 检查 GitHub App 是否安装到了目标仓库
3. 检查 App 是否订阅了正确的事件（Issues / Pull request / Issue comment / Workflow run）
4. 检查 `.env` 中的 `APP_ID` 和 `WEBHOOK_SECRET` 是否正确

### 问题2：私钥错误

**症状**：启动时报错 `Error: error:0909006C:PEM routines:get_name:no start line`

**原因**：PEM 私钥文件格式错误。

**解决**：
- 确认 PEM 文件包含 `-----BEGIN RSA PRIVATE KEY-----` 和 `-----END RSA PRIVATE KEY-----`
- 确认换行符正确（Unix 格式 `\n`，不是 Windows 的 `\r\n`）
- 尝试使用 `PRIVATE_KEY` 环境变量直接粘贴私钥内容（注意用 `\n` 代替换行）

### 问题3：标签未添加

**症状**：创建 Issue 后没有自动添加标签。

**排查**：
1. 确认仓库中存在 `.github/jupyterlab-probot.yml` 文件
2. 确认配置文件中设置了 `triageLabel`
3. 确认标签在仓库中已存在（GitHub API 不会自动创建不存在的标签）
4. 检查 App 是否有 Issues write 权限

### 问题4：Binder 链接未出现

**症状**：创建 PR 后没有 Binder 评论。

**排查**：
1. 确认配置中设置了 `addBinderLink: true`（不是 `True` 或 `1`）
2. 确认 App 订阅了 Pull request 事件
3. 确认 App 有 Pull requests write 权限

### 问题5：重启 CI 命令不工作

**症状**：评论 `@jupyterlab-bot, please restart ci` 无反应。

**排查**：
1. 确认评论内容**完全精确匹配**：`@jupyterlab-bot, please restart ci`（注意逗号和空格）
2. 确认 `botUser` 配置与实际 Bot 用户名一致（默认 `jupyterlab-bot`）
3. 确认 App 订阅了 Issue comment 事件
4. 注意：评论者必须是对仓库有写权限的人吗？不需要，任何人都可以触发
