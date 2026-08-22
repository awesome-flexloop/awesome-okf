---
type: Example
title: CLI 安装与基本使用
description: 展示如何从源码安装 pi-cli、构建项目、使用 pi-ai CLI 登录 provider，以及通过 Agent API 发起基本对话。
tags: [pi-cli, 安装, cli, agent, 快速开始]
generated: 2026-08-23
verified: 2026-08-23
status: stable
stale_after: 2026-11-23
sources:
  - README.md:52-61
  - packages/ai/src/cli.ts:79-114
  - packages/agent/README.md:15-43
---

# CLI 安装与基本使用

## 环境要求

- Node.js >= 22.19.0
- npm（随 Node 安装）

## 从源码安装

```bash
# 克隆仓库后，在项目根目录执行：
npm install --ignore-scripts
```

`--ignore-scripts` 是项目推荐的安装方式，避免运行依赖的生命周期脚本。

## 构建项目

```bash
# 完整构建（会刷新模型数据，需要网络访问）
npm run build

# 离线构建（使用已有模型数据，无需网络）
npm run build:offline
```

构建按 tui → telemetry → ai → agent → session-backends → protocol → client → server → coding-agent 的顺序进行。

## 代码检查

```bash
npm run check
```

该命令运行 Biome lint/format、固定依赖检查、TypeScript 导入检查、shrinkwrap 验证、tsgo 类型检查和浏览器冒烟测试。

## 运行测试

```bash
# 从仓库根目录运行非 e2e 测试
./test.sh

# 从源码运行 pi（可在任意目录执行）
./pi-test.sh
```

## 使用 pi-ai CLI 登录 Provider

`@earendil-works/pi-ai` 包附带一个 CLI 工具用于 OAuth 登录：

```bash
# 列出所有支持 OAuth 的 provider
npx @earendil-works/pi-ai list

# 登录指定 provider
npx @earendil-works/pi-ai login anthropic

# 交互式选择 provider 登录
npx @earendil-works/pi-ai login
```

登录成功后，凭证保存到当前目录的 `auth.json` 文件。

## 使用 Agent API 发起对话

以下示例展示如何使用 `@earendil-works/pi-agent-core` 和 `@earendil-works/pi-ai` 发起基本对话：

```typescript
import { Agent } from "@earendil-works/pi-agent-core";
import { createModels } from "@earendil-works/pi-ai";
import { anthropicProvider } from "@earendil-works/pi-ai/providers/anthropic";

const models = createModels();
models.setProvider(anthropicProvider());

const model = models.getModel("anthropic", "claude-sonnet-4-6");
if (!model) throw new Error("Model not found");

const agent = new Agent({
  initialState: {
    systemPrompt: "You are a helpful assistant.",
    model,
  },
  streamFn: models.streamSimple.bind(models),
});

agent.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

await agent.prompt("Hello!");
```

## 事件序列参考

调用 `agent.prompt("Hello")` 时的事件顺序：

```
agent_start
├─ turn_start
├─ message_start   { userMessage }
├─ message_end     { userMessage }
├─ message_start   { assistantMessage }
├─ message_update  { partial... }
├─ message_end     { assistantMessage }
├─ turn_end
└─ agent_end
```

如果模型调用工具，会在 assistant message 后触发 `tool_execution_start`、`tool_execution_update`、`tool_execution_end` 事件，然后进入下一轮 turn。

## 相关概念

- [项目简介](/concepts/00-introduction.md)
- [AI 包详解](/concepts/02-ai-package.md)
- [Monorepo 架构](/concepts/01-monorepo-architecture.md)
