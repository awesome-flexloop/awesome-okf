---
type: Concept
title: Pi AI CLI 项目简介
description: Pi 是一个自扩展编码代理项目，采用多包 monorepo 架构，包含统一 LLM API、代理运行时、终端 UI 和交互式编码 CLI。
tags: [pi-cli, 项目简介, monorepo]
generated: 2026-08-23
verified: 2026-08-23
status: stable
stale_after: 2026-11-23
sources:
  - README.md:13-36
  - package.json:2-4
---

# Pi AI CLI 项目简介

Pi（Pi Agent Harness）是一个自扩展编码代理项目，项目网站为 [pi.dev](https://pi.dev)。项目以 npm monorepo 形式组织，包名为 `pi-monorepo`，使用 ES 模块（`"type": "module"`）。

## 三个核心包

项目围绕三个层级构建：

1. **`@earendil-works/pi-coding-agent`**：交互式编码代理 CLI，是面向最终用户的入口。
2. **`@earendil-works/pi-agent-core`**：带工具调用和状态管理的代理运行时，构建于 pi-ai 之上。
3. **`@earendil-works/pi-ai`**：统一多提供商 LLM API，支持 OpenAI、Anthropic、Google 等提供商。

## 辅助包

除核心三包外，monorepo 还包含：

- **`@earendil-works/pi-tui`**：带差分渲染的终端 UI 组件库。
- **`@earendil-works/pi-telemetry`**：厂商中立的遥测契约和参考适配器。
- **`@earendil-works/pi-client`**：传输无关的远程 pi 会话客户端。
- **`@earendil-works/pi-server`**：实验性的 pi 会话服务器。
- **`@earendil-works/pi-protocol`**：客户端/服务器之间的 CBOR 线协议。
- **`@earendil-works/pi-session-backend-sqlite-node`**：基于 SQLite 的会话后端。

## 权限模型

Pi 不内置文件系统、进程、网络或凭证访问的权限限制系统。默认情况下，它以启动用户和进程的权限运行。如需更强边界，项目文档提供了三种容器化/沙箱方案：Gondolin 扩展、Plain Docker 和 OpenShell。

## 开发环境要求

- Node.js >= 22.19.0
- 使用 npm workspaces 管理依赖
- 代码检查使用 Biome 2.3.5
- TypeScript 5.9.3，使用 Node strip-only 模式（仅可擦除语法）

## 相关概念

- [Monorepo 架构](/concepts/01-monorepo-architecture.md)
- [AI 包详解](/concepts/02-ai-package.md)
- [TUI 终端 UI 系统](/concepts/03-tui-system.md)
- [内置 Prompt 模板](/concepts/04-builtin-prompts.md)
