---
type: Example
title: "基础使用示例"
description: "从源码安装构建 pi-monorepo，使用 pi-ai CLI 登录 OAuth provider，通过 coding-agent SDK 创建会话进行对话，以及直接使用 pi-ai 的 createModels API。"
tags: [pi-cli, example, installation, login, sdk, quickstart]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# 基础使用示例

本示例演示从源码构建 Pi、OAuth 登录、交互式对话和 SDK 编程使用。

## 前置条件

- Node.js >= 22.19.0
- npm
- Git

## 1. 安装与构建

克隆仓库后，使用 `--ignore-scripts` 安装依赖（这是默认安全操作模式）：

```bash
git clone <repo-url> pi
cd pi

npm install --ignore-scripts
npm run build
```

构建按顺序编译 9 个包：tui → telemetry → ai → agent → sqlite-node → protocol → client → server → coding-agent。

如需离线构建（使用已有模型数据，不刷新 provider 目录）：

```bash
npm run build:offline
```

运行代码检查（biome + 类型检查 + 供应链检查）：

```bash
npm run check
```

从源码直接运行 pi（可在任意目录执行）：

```bash
./pi-test.sh
```

## 2. OAuth 认证

pi-ai 包提供 CLI 工具登录 OAuth provider。凭证保存到当前目录的 `auth.json`：

```bash
# 列出所有支持 OAuth 的 provider
npx @earendil-works/pi-ai list

# 登录指定 provider
npx @earendil-works/pi-ai login anthropic
npx @earendil-works/pi-ai login openai
```

`login` 命令会打开浏览器 URL 或显示设备码供用户完成授权。CLI 内部调用 `provider.auth.oauth.login()`：

```ts
const credential = await provider.auth.oauth.login({
  signal: new AbortController().signal,
  prompt: (authPrompt) => answerPrompt(rl, authPrompt),
  notify: (event) => {
    switch (event.type) {
      case "auth_url":
        console.log(`\nOpen this URL in your browser:\n${event.url}`);
        break;
      case "device_code":
        console.log(`\nOpen this URL in your browser:\n${event.verificationUri}`);
        console.log(`Enter code: ${event.userCode}`);
        break;
    }
  },
});
```

登录成功后凭证以 JSON 格式写入 `auth.json`：

```json
{
  "anthropic": {
    "accessToken": "...",
    "refreshToken": "...",
    "expiresAt": 1234567890
  }
}
```

## 3. 基本对话（Coding Agent SDK）

最简方式使用 `createAgentSession()`，它自动发现技能、扩展、工具和上下文文件：

```ts
import { createAgentSession } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession();

try {
  session.subscribe((event) => {
    if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
      process.stdout.write(event.assistantMessageEvent.delta);
    }
  });

  await session.prompt("What files are in the current directory?");

  session.state.messages.forEach((msg) => {
    console.log(msg);
  });
  console.log();
} finally {
  session.dispose();
}
```

### 只读模式

限制可用工具为只读操作：

```ts
import { createAgentSession, SessionManager } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession({
  tools: ["read", "grep", "find", "ls"],
  sessionManager: SessionManager.inMemory(),
});
console.log("Read-only session created");
session.dispose();
```

### 指定工作目录和工具

```ts
const { session } = await createAgentSession({
  cwd: "/path/to/project",
  tools: ["read", "bash", "edit", "write"],
  sessionManager: SessionManager.inMemory("/path/to/project"),
});
```

代理支持两种工具执行模式：`parallel`（默认，预检顺序执行、允许的工具并发执行）和 `sequential`（逐个执行）。

代理事件类型包括：

- `agent_start` / `agent_end`
- `turn_start` / `turn_end`
- `message_start` / `message_update` / `message_end`
- `tool_execution_start` / `tool_execution_update` / `tool_execution_end`

## 4. 直接使用 pi-ai API

对于不需要完整代理运行时的场景，可直接使用 `@earendil-works/pi-ai` 的 `createModels()` 和 provider factories：

```ts
import { createModels, hasApi } from "@earendil-works/pi-ai";
import { anthropicProvider } from "@earendil-works/pi-ai/providers/anthropic";

const models = createModels();
models.setProvider(anthropicProvider());

await models.refresh({ allowNetwork: true });

const available = await models.getAvailable();
console.log("Available models:", available.map((m) => m.id));

const model = models.getModel("anthropic", "claude-sonnet-4-20250514");
if (model && hasApi(model, "anthropic-messages")) {
  const stream = models.stream(model, {
    messages: [{ role: "user", content: "Hello, world!" }],
  });

  for await (const event of stream) {
    if (event.type === "text_delta") {
      process.stdout.write(event.delta);
    }
  }
}
```

关键点：

- 先 `createModels()` 再 `setProvider()`。
- 对动态 provider 调用 `refresh({ allowNetwork: true })` 后再查询模型。
- 不要假设 `getModel()` 返回非空——动态 provider 在首次刷新前模型列表为空。
- 使用 `hasApi()` 类型守卫收窄模型类型以获得完整类型化的 stream options。

非流式补全使用 `complete()`：

```ts
const response = await models.complete(model, {
  messages: [{ role: "user", content: "What is 2+2?" }],
});
console.log(response.content);
```

## 5. 使用内置 Slash Prompts

在交互式 pi 会话中可使用五个内置 prompt：

```text
/is 123          # 分析 GitHub issue #123
/pr <PR-URL>     # 审查 PR
/cl              # 审计 changelog 条目
/sa <GHSA-URL>   # 更新安全公告
/wr              # 收尾任务（changelog + commit + push + close）
```

推荐工作流：`/is` 分析问题 → 实现修复 → `/pr` 审查 → `/cl` 审计 changelog → `/wr` 收尾提交。

## 相关概念

- [Pi AI CLI 简介](../concepts/00-introduction.md)
- [Monorepo 架构](../concepts/01-monorepo-architecture.md)
- [AI 包（packages/ai）](../concepts/02-ai-package.md)
- [TUI 系统](../concepts/03-tui-system.md)
- [内置 Prompts](../concepts/04-builtin-prompts.md)
