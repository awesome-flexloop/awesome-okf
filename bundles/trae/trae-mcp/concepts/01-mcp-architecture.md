---
type: Concept
title: MCP 三层模型
description: MCP 采用 Transport 层（stdio/SSE）、Protocol 层（JSON-RPC）、Capability 层（Tools/Resources/Prompts）三层架构，理解三层模型有助于正确配置和排错。
tags: [trae-mcp, trae, mcp, architecture, three-layer-model, transport]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# MCP 三层模型

MCP（Model Context Protocol）在 TRAE 生态中呈现清晰的三层架构：**Transport 层**、**Protocol 层**、**Capability 层**。理解这三层模型有助于正确配置 MCP 和进行排错。

## 三层架构总览

```
┌─────────────────────────────────────────────┐
│  Capability 层（能力层）                      │
│  Tools / Resources / Prompts                │
│  具体工具能力：数据库查询、云函数调用、存储管理等 │
├─────────────────────────────────────────────┤
│  Protocol 层（协议层）                        │
│  JSON-RPC 消息格式                           │
│  工具调用、资源读取、提示模板三种交互模式         │
├─────────────────────────────────────────────┤
│  Transport 层（传输层）                       │
│  stdio / SSE                                │
│  command + args + env 启动本地进程或远程连接    │
└─────────────────────────────────────────────┘
```

## Transport 层（传输层）

Transport 层负责进程通信，通过 `command`、`args`、`env` 三个配置字段启动本地进程或建立远程连接。

**常见传输方式**：

- **stdio**：通过标准输入/输出与本地进程通信，这是最常见的方式。例如：
  - `npx -y @cloudbase/cloudbase-mcp@latest`：通过 npx 启动 npm 包
  - `node /absolute/path/to/build/index.js`：启动本地构建的 Node.js MCP 服务器
- **SSE**：Server-Sent Events，用于远程 MCP 服务器连接

**配置三要素**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `command` | string | 启动命令（如 `node`、`npx`、`python`） |
| `args` | string[] | 命令参数数组（如 `["-y", "@cloudbase/cloudbase-mcp@latest"]`） |
| `env` | object | 环境变量对象（如 `{"API_KEY": "your-api-key"}`） |

Transport 层不仅限于本地进程通信，还可以启动 OAuth 等交互式认证流程（如 CloudBase MCP 首次使用时会打开浏览器进行登录和环境选择）。

## Protocol 层（协议层）

Protocol 层定义了标准化的 **JSON-RPC** 消息格式，规定了三种交互模式：

1. **Tools（工具调用）**：Agent 调用 MCP 服务器提供的函数，传入参数，获取返回结果。这是最核心的交互模式。
2. **Resources（资源读取）**：Agent 读取 MCP 服务器暴露的资源（如文件内容、数据库记录）。
3. **Prompts（提示模板）**：MCP 服务器提供预定义的提示词模板，供 Agent 使用。

配置 MCP 时，用户只需要声明 Transport 层信息（command/args/env），TRAE 会在进程启动后自动完成 Protocol 握手，发现服务器支持的全部能力。用户**不需要**手动声明每个工具的名称、参数或返回值格式——这与传统 IDE 插件需要在配置文件中显式声明每个命令/Action 的模式根本不同。

## Capability 层（能力层）

Capability 层是 MCP 服务器实际提供的具体工具能力。以 CloudBase MCP 为例，其能力范围覆盖：

- AI 模型调用
- 认证（auth）
- NoSQL/PostgreSQL 数据库操作
- 云函数调用与管理
- 存储（storage）管理
- CloudRun 服务
- 微信小程序工具

MCP 服务器启动后会自动向 TRAE 注册其全部 Capability，Agent 可以根据任务需要自动选择调用。

## 三层排错法

理解三层模型有助于快速定位 MCP 问题：

| 层级 | 问题表现 | 常见原因 |
|------|---------|---------|
| **Transport 层** | MCP 服务器无法启动 | command 找不到、args 路径错误、env 缺失必要的环境变量/API Key |
| **Protocol 层** | 服务器启动但工具列表为空 | JSON-RPC 版本不兼容、握手失败 |
| **Capability 层** | 特定工具调用失败 | 工具调用参数错误、认证过期、权限不足、API 限流 |

## 相关链接

- [MCP 简介](/concepts/00-introduction.md)
- [MCP 配置格式](/concepts/02-mcp-configuration.md)
- [CloudBase MCP](/concepts/03-cloudbase-mcp.md)
- [MCP 开发入门](/concepts/05-mcp-development.md)
- [配置 MCP 服务器示例](/examples/configure-mcp.md)
