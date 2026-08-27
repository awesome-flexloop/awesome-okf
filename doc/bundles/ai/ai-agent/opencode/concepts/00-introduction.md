---
type: Concept
title: OpenCode 简介
description: OpenCode 是一个开源的终端 AI 编码代理，基于 Bun + Turbo + SST 技术栈构建，支持多模型提供商、内置工具系统和可扩展插件架构
tags: [opencode, ai-agent, terminal, tui, bun]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# OpenCode 简介

OpenCode 是一个开源的 AI 编码代理，运行在终端中，帮助开发者完成代码编写、调试、探索等任务。项目以 MIT 许可证发布，仓库位于 `https://github.com/anomalyco/opencode`。

## 核心定位

OpenCode 的定位是"终端中的 AI 开发工具"。它提供：

- **终端用户界面（TUI）**：基于 `@opentui/core` 和 SolidJS 构建的全屏终端界面
- **多模型支持**：通过 AI SDK 集成 20+ 模型提供商，包括 Anthropic、OpenAI、Google、Amazon Bedrock、Azure、Groq、Mistral、xAI 等
- **内置工具系统**：bash 执行、文件读写、代码搜索（grep/glob）、补丁应用、Web 搜索等
- **Agent 系统**：内置 build（全权限）和 plan（只读）两个主 agent，以及 general 子 agent
- **会话持久化**：基于 SQLite 的会话历史存储，支持压缩和上下文管理

## 技术栈

| 层面 | 技术选型 |
|------|---------|
| 运行时 | Bun 1.3.14（主要），Node.js（条件导入支持） |
| 语言 | TypeScript 5.8.2 |
| Monorepo | Turbo 2.10.2 + Bun workspaces |
| 函数式框架 | Effect 4.0.0-beta.83 |
| LLM 抽象 | AI SDK 6.0.168（`ai` 包） |
| HTTP 框架 | Hono 4.10.7 |
| 数据库 | SQLite + Drizzle ORM 1.0.0-rc.2 |
| 终端 UI | @opentui/core 0.4.5 + SolidJS 1.9.10 |
| Web UI | SolidStart + Vite 7.1.4 + TailwindCSS 4.1.11 |
| Schema 验证 | Zod 4.1.8 + Effect Schema |
| 基础设施 | SST 4.13.1（Cloudflare + AWS） |
| 代码检查 | oxlint 1.60.0 |

## 包结构

OpenCode 采用 monorepo 架构，主要包包括：

- **`packages/opencode`**：主 CLI 包，包含命令行入口、TUI 集成、会话执行、工具实现
- **`packages/core`**：核心库，包含配置、会话、模型、provider、插件、工具注册表等
- **`packages/tui`**：终端 UI 组件库，基于 OpenTUI 和 SolidJS
- **`packages/ui`**：Web UI 组件库，包含 i18n 支持
- **`packages/schema`**：共享 Schema 定义，被 Core、Protocol、Client 共同依赖
- **`packages/protocol`**：HTTP API 协议定义，基于 Effect HttpApi
- **`packages/server`**：HTTP 服务器实现
- **`packages/client`**：生成的客户端 SDK（Promise 和 Effect 双版本）
- **`packages/sdk/js`**：JavaScript SDK
- **`packages/sdk-next`**：下一代嵌入式 SDK，组合 Client/Core/Server
- **`packages/plugin`**：插件系统
- **`packages/llm`**：LLM 协议适配层
- **`packages/app`**：Web 应用
- **`packages/desktop`**：桌面应用（Electron）
- **`packages/function`**：Cloudflare Worker 函数
- **`packages/codemode`**：代码模式工具

## 安装方式

OpenCode 支持多种安装方式：

```bash
curl -fsSL https://opencode.ai/install | bash
npm i -g opencode-ai@latest
brew install anomalyco/tap/opencode
scoop install opencode
choco install opencode
```

## 相关概念

- [架构概览](01-architecture.md)
- [配置系统](02-config-system.md)
- [会话与工具](03-session-tools.md)
- [部署与基础设施](04-deployment-infra.md)
