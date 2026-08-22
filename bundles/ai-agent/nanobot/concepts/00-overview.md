---
type: concept
title: Nanobot 项目概览
description: Nanobot 是什么、六部件运行时、CLI/网关/API/WebUI 入口、配置与工作区、技术栈总览
tags: [nanobot, overview, agent, architecture]
sources:
  - resource: "/references/agent-api.md"
    title: "Nanobot SDK 门面 API"
  - resource: "/references/bus-sdk-api.md"
    title: "MessageBus 与 SDK 类型 API"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# Nanobot 项目概览

Nanobot（PyPI 包名 `nanobot-ai`）是一个轻量、开源的 AI Agent 框架，由 Python 核心 + React/TypeScript WebUI + TypeScript TUI 三部分构成。它围绕一条小型的 agent loop 展开：loop 从聊天频道接收消息、调用 LLM provider、执行工具、管理会话记忆，再把回复送回来源频道（F-001、F-056）。

对使用者来说，nanobot 与一般"调用模型的 SDK"最根本的区别在于：它运行的是"围绕模型的一个 agent"，一次调用即可串起读文件、调工具、保会话、用记忆、流式输出与结构化运行时信息（F-062）。

## 运行时六部件

docs/concepts.md 的 Runtime Shape 表把运行时分成了六块（F-056）：

- **Agent loop**：构建上下文、选择会话、调用 provider、执行工具、发布回复。
- **Providers**：LLM 后端，如 OpenRouter、Anthropic、OpenAI、Bedrock、Ollama、vLLM 及其它 OpenAI 兼容 API。
- **Channels**：面向用户的传输层，如 CLI、WebUI/WebSocket、Telegram、Discord、Slack、Feishu、WeChat、Email 等。
- **Tools**：模型可调用的能力，包括文件、shell、web 搜索、MCP、cron、图像生成、子 agent 等。
- **Memory**：跨轮次保留上下文的工作区文件与会话历史。
- **Gateway**：连接已启用频道的长驻进程，并提供健康检查端点。

## 入口点

| 入口 | 命令 | 用途 |
|---|---|---|
| CLI 一次性 | `nanobot agent -m "..."` | 首轮检查、脚本、快速本地提问 |
| CLI 交互 | `nanobot agent` | 带持久会话历史的终端聊天 |
| Gateway | `nanobot gateway` | 聊天应用、WebUI、心跳、Dream、长驻服务 |
| OpenAI 兼容 API | `nanobot serve` | 通过 `/v1/chat/completions` 程序化访问 |
| WebUI | `nanobot webui` | 准备本地 WebUI、启动 gateway、打开浏览器工作台 |

`nanobot webui` 是普通浏览器的入口，底层由 gateway 保持 WebSocket 频道与其它长驻服务存活。gateway 健康端点位于 `gateway.port`（默认 `18790`），浏览器 WebUI 默认在 `8765` 提供（F-059）。

最简单的路径是 `nanobot agent -m "Hello!"`：一条入站消息经过 agent loop 并在终端打印回复；长驻路径是 `nanobot gateway`：频道从聊天应用或 WebUI 收消息，发布到同一条 agent loop，再把回复送回来源频道。

## 配置与工作区

`config.json` 控制 nanobot *可以用什么*，工作区则保存该实例的*状态*。默认实例位于 `~/.nanobot/` 下（F-057）：

- `~/.nanobot/config.json`：实例配置——providers、模型默认值、channels、tools、gateway、API、运行时选项。
- `~/.nanobot/workspace/`：agent 工作区——记忆、心跳任务、cron 作业、skills、生成产物。
- `~/.nanobot/sessions/<workspace-id>/`：会话历史，存放在 agent 可访问工作区之外，不透明 ID 随工作区移动而保持稳定。

二者都可以用命令行标志覆盖：

```bash
nanobot onboard --config ./bot-a/config.json --workspace ./bot-a/workspace
nanobot agent --config ./bot-a/config.json --workspace ./bot-a/workspace -m "Hello"
```

## 一次 agent 轮次

无论消息从 CLI、WebUI、Telegram、Discord 还是其它频道开始，一次正常轮次都遵循同一流程（F-058）：

1. 频道收到用户消息并发布到消息总线。
2. agent loop 选择 session key，并从有效项目工作区、agent 拥有的 profile/skills/memory、最近消息、频道元数据与运行时设置构建上下文。
3. provider 收到模型请求。
4. 若模型请求工具，runner 执行它们并把结果回填给模型。
5. 最终回复保存到会话并经由频道回传。

## 技术栈

- **Python 核心**：`requires-python = ">=3.11"`，全异步（asyncio），许可证 MIT（F-002、F-003）。
- **核心依赖**（F-004）：`typer`（CLI）、`anthropic`/`openai`（provider）、`pydantic`+`pydantic-settings`（配置）、`loguru`（日志）、`rich`（终端渲染）、`mcp`（MCP 服务）、`prompt-toolkit`、`croniter` 等。
- **可选依赖**（F-005）：`api`（aiohttp）、`azure`、`bedrock`（boto3）、`documents` 等 extras。
- **TypeScript TUI**（F-051）：包名 `@nanobot/tui`，基于 `@opentui/core`，用 Bun 启动。
- **React WebUI**（F-052）：包名 `nanobot-webui`，React 18 + Vite 5，构建产物打进 Python wheel。

## 相关概念

- [Agent 核心：Nanobot 门面](/concepts/01-agent-core.md)
- [消息总线系统](/concepts/02-bus-system.md)
- [CLI 与 SDK](/concepts/03-cli-sdk.md)
- [TUI 与 WebUI 架构](/concepts/04-tui-webui.md)