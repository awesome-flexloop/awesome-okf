---
type: Concept
title: nanobot 简介
description: nanobot 是一个用 Python 编写的超轻量级开源个人 AI 代理框架，提供 CLI、TUI 和 WebUI 三种交互接口，围绕小型代理循环构建。
tags: [nanobot, introduction, overview]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: nanobot 源码信源
---

# nanobot 简介

nanobot 是一个超轻量级、开源、自托管的个人 AI 代理框架，使用 Python 编写。它可以在 WebUI、终端或聊天应用中运行，将工具调用、长期记忆、MCP 集成、模型路由、多代理委派、定时自动化和 OpenAI 兼容 API 整合在一个小巧可读的核心中。

## 核心定位

nanobot 的包名为 `nanobot-ai`，当前版本为 `0.3.0`（代号 "The Agency Release"），要求 Python 3.11 或更高版本，采用 MIT 许可证。

```toml
[project]
name = "nanobot-ai"
version = "0.3.0"
description = "A lightweight personal AI agent framework"
requires-python = ">=3.11"
license = {text = "MIT"}
```

来源：`pyproject.toml:2-7`

## Python Agent 核心

nanobot 的核心是一个小型异步代理循环。消息从聊天通道进入，LLM 决定何时需要调用工具，记忆和技能仅在需要时作为上下文拉入，而非成为重型编排层。这保持了核心路径的可读性和可扩展性。

核心数据流如下：

1. **通道（Channels）** 从外部平台接收消息，向总线发布 `InboundMessage` 事件。
2. **AgentLoop** 消费入站消息，构建上下文，协调本轮对话。
3. **AgentRunner** 处理实际的 LLM 对话循环：向 provider 发送消息、接收工具调用、执行工具、流式返回响应。
4. 响应作为 `OutboundMessage` 事件发布回相应通道。

来源：`AGENTS.md:33-38`

编程式入口是 `Nanobot` 类，它作为门面封装了 `AgentLoop`：

```python
from nanobot import Nanobot

bot = Nanobot.from_config()
result = await bot.run("Summarize this repo")
print(result.content)
```

来源：`nanobot/nanobot.py:66-74`

## 多接口架构

nanobot 提供三种用户接口，全部共享同一个 Agent 核心：

| 接口 | 命令 | 技术栈 | 适用场景 |
|------|------|--------|----------|
| CLI（经典） | `nanobot agent --classic` | Python + prompt-toolkit + Rich | 传统终端对话 |
| TUI（原生） | `nanobot agent` | Bun + TypeScript + @opentui/core | 现代终端体验 |
| WebUI | `nanobot webui` | React 18 + Vite + TypeScript | 浏览器图形界面 |

此外还有：

- **Gateway**（`nanobot gateway`）：长运行进程，连接聊天通道并提供健康端点
- **OpenAI 兼容 API**（`nanobot serve`）：HTTP `/v1/chat/completions` 端点
- **Python SDK**：通过 `from nanobot import Nanobot` 在代码中直接调用

TUI 和 WebUI 均通过 WebSocket 协议连接到网关，而非在进程内直接调用 Python 核心。这使得终端和浏览器体验共享同一套网络协议。

```typescript
// TUI 通过 WebSocket 连接网关
const client = new NanobotClient({
  resolveConnection: () => fetchGatewayConnection(...),
  onEvent: (event) => this.accept(event),
  onStatus: (status, detail) => this.handleStatus(status, detail),
});
```

来源：`tui/src/app.ts:498-523`

## 主要能力

- 在浏览器 WebUI 或终端中运行
- 连接 Telegram、Discord、Slack、微信、邮件、Mattermost 等聊天应用
- 使用文件、Shell、网页搜索/抓取、MCP、cron、图像生成、子代理等工具
- 通过 Dream 机制保持会话历史和长期记忆
- 运行长周期目标和定时自动化
- 暴露 Python SDK 和 OpenAI 兼容 API
- 部署为长运行的本地或服务端代理网关

来源：`README.md:53-61`

## 相关概念

- [整体架构](/concepts/01-architecture.md)
- [Agent 运行时](/concepts/02-agent-runtime.md)
- [消息总线](/concepts/03-bus-messaging.md)
- [多接口架构](/concepts/05-multi-interface.md)
