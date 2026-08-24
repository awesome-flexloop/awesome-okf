---
type: bundle
okf_version: "0.2"
scope: nanobot
name: nanobot
version: "0.1.0"
source: local
description: nanobot 超轻量级个人 AI 代理框架的 OKF 知识库，涵盖架构、运行时、消息总线、SDK 类型和多接口架构。
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
---

# nanobot

nanobot 是一个超轻量级、开源、自托管的个人 AI 代理框架，使用 Python 编写，版本 0.3.0（"The Agency Release"）。它围绕小型异步代理循环构建，支持 CLI、TUI（Bun + TypeScript）和 WebUI（React）三种交互接口，提供工具调用、长期记忆（Dream）、MCP 集成、模型路由、多代理委派、定时自动化和 OpenAI 兼容 API。

- **包名**：`nanobot-ai`
- **Python 要求**：>= 3.11
- **许可证**：MIT
- **仓库**：https://github.com/HKUDS/nanobot
- **文档**：https://nanobot.wiki

## 功能特性

- **多接口访问**：浏览器 WebUI、原生终端 TUI、经典 CLI、Python SDK、OpenAI 兼容 HTTP API
- **多 LLM 提供商**：Anthropic、OpenAI、OpenRouter、Ollama、vLLM、Bedrock、Azure、GitHub Copilot、OpenAI Codex 等
- **工具系统**：文件读写、Shell 执行（含沙箱）、Web 搜索/抓取、MCP 服务器、cron、图像生成、子代理
- **长期记忆**：Dream 两阶段记忆整合，Git 版本化记忆文件
- **聊天通道**：Telegram、Discord、Slack、Feishu、微信、邮件、Mattermost 等 15+ 平台
- **实时通信**：WebSocket 双向流式协议，支持多聊天复用和令牌认证
- **安全默认**：非 root Docker 容器、loopback 绑定、时序安全令牌比较、最小权限 capability 配置

## 导航

### 概念文档

| 文档 | 说明 |
|------|------|
| [nanobot 简介](/concepts/00-introduction.md) | 项目定位、Python Agent 核心、三端接口概览 |
| [整体架构](/concepts/01-architecture.md) | 消息总线、SDK 门面、CLI 入口分层、网关模式 |
| [Agent 运行时](/concepts/02-agent-runtime.md) | AgentLoop、AgentRunner、Provider 抽象、工具调用、钩子 |
| [消息总线与事件驱动](/concepts/03-bus-messaging.md) | MessageBus、WebSocket 协议、多聊天复用、认证安全 |
| [SDK 类型系统](/concepts/04-sdk-types.md) | StreamEvent、RunResult、SessionSnapshot、延迟导出 |
| [多接口架构](/concepts/05-multi-interface.md) | CLI、TUI（OpenTUI）、WebUI（React+Vite）实现细节 |

### 示例

| 文档 | 说明 |
|------|------|
| [基础使用](/examples/01-basic-usage.md) | 安装、配置模型、WebUI/TUI/SDK 基本交互 |

### 参考

| 文档 | 说明 |
|------|------|
| [源码信源索引](/references/source.md) | 关键源文件与事实 ID 映射 |

### 规格

| 文档 | 说明 |
|------|------|
| [事实清单](/spec/facts.md) | 94 条从源码提取的可验证事实（F-001 ~ F-094） |
| [架构洞察](/spec/insights.md) | 4 条架构与工程洞察（陈述/证据/反常识/行动） |

## 目录结构

```text
nanobot/
├── index.md                    # 本文件（bundle 根索引）
├── log.md                      # 变更日志
├── concepts/                   # 概念文档
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-architecture.md
│   ├── 02-agent-runtime.md
│   ├── 03-bus-messaging.md
│   ├── 04-sdk-types.md
│   └── 05-multi-interface.md
├── examples/                   # 示例文档
│   ├── index.md
│   └── 01-basic-usage.md
├── references/                 # 参考文档
│   ├── index.md
│   └── source.md
└── spec/                       # 规格文件
    ├── facts.md
    └── insights.md
```

## 技术栈

| 层 | 技术 |
|----|------|
| Agent 核心 | Python 3.11+, asyncio, Pydantic v2 |
| CLI 框架 | Typer, Rich, prompt-toolkit |
| LLM SDK | anthropic, openai, tiktoken |
| TUI | Bun, TypeScript, @opentui/core 0.5.3 |
| WebUI | React 18, Vite 5, TypeScript, Radix UI, Tailwind CSS |
| 构建 | Hatchling, 自定义 WebUI 构建钩子 |
| 部署 | Docker (多阶段), docker-compose, systemd, LaunchAgent |
| 测试 | pytest, pytest-asyncio, vitest, basedpyright (strict) |

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
