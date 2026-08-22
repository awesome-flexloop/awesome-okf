---
type: Concept
title: Agent 通信协议
description: Agent 与外部世界的通信标准——MCP 工具协议、ACP 客户端协议、传输层抽象与 COM/OSC 原生集成
tags: [ai-agent, protocol, mcp, acp, transport, com, osc, json-rpc, named-pipe]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:55:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md
  - id: terminal
    resource: /references/ai-agent-sources.md#intelligent-terminal
  - id: dsh
    resource: /references/ai-agent-sources.md#deepseek-harness
  - id: zleap
    resource: /references/ai-agent-sources.md#zleap-agent
  - id: hermes
    resource: /references/ai-agent-sources.md#hermes-agent
---

# Agent 通信协议

Agent 不是孤立运行的——它需要与宿主应用、外部工具、其他 Agent 通信。随着 Agent 生态的成熟，通信协议正在从各框架私有的实现走向标准化。本文分析四种通信协议/机制：MCP（模型上下文协议）、ACP（Agent 客户端协议）、hermes 的传输层抽象，以及 intelligent-terminal 的 COM/OSC 原生集成。

## 协议分层

Agent 通信可以分为几个层次：

```
┌─────────────────────────────────────────────────┐
│ 应用层协议                                       │
│ MCP（工具调用）│ ACP（Agent控制）│ 私有API       │
├─────────────────────────────────────────────────┤
│ 会话层                                           │
│ JSON-RPC 2.0 │ SSE │ WebSocket │ stdio          │
├─────────────────────────────────────────────────┤
│ 传输层                                           │
│ Named Pipe │ stdio │ HTTP │ COM │ OSC序列        │
└─────────────────────────────────────────────────┘
```

## MCP：Model Context Protocol

**MCP（Model Context Protocol）** 是一个开放协议，标准化 Agent 如何与外部工具和数据源交互。Zleap-Agent 和 deepseek-harness 都内置了 MCP 支持。

### MCP 的核心模型

MCP 定义了三种原语：

| 原语 | 方向 | 用途 |
|------|------|------|
| **Tools** | Server → Client | Agent 可调用的函数 |
| **Resources** | Server → Client | Agent 可读取的数据源（文件、数据库记录等） |
| **Prompts** | Server → Client | 可复用的提示词模板 |

### MCP 通信模式

MCP 使用 JSON-RPC 2.0  over stdio 或 SSE：

```
┌──────────┐ stdio/SSE ┌──────────┐
│  Agent   │◄─────────►│ MCP      │
│ (Client) │  JSON-RPC │ Server   │
└──────────┘  2.0      └──────────┘
                          │
                    ┌─────┴─────┐
                    │ 工具/数据/  │
                    │ 提示词     │
                    └───────────┘
```

**典型交互流程**：

```json
// 1. Agent 连接 MCP Server
// → initialize
{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}

// 2. Server 响应能力
// ← initialize result
{"capabilities": {"tools": {"listChanged": true}, "resources": {"subscribe": true}}}

// 3. Agent 列出可用工具
// → tools/list
{"jsonrpc": "2.0", "method": "tools/list", "id": 1}

// 4. Agent 调用工具
// → tools/call
{"jsonrpc": "2.0", "method": "tools/call", "params": {
    "name": "read_file",
    "arguments": {"path": "/workspace/main.py"}
}, "id": 2}

// 5. 工具返回结果
// ← tools/call result
{"content": [{"type": "text", "text": "def main():\n    print('hello')"}]}
```

### deepseek-harness 的 MCP 包

deepseek-harness 有独立的 `mcp` 包实现 MCP 客户端，可以连接外部 MCP server 并将其工具注册到框架的工具系统中：

```typescript
// cordis.yml 中配置 MCP servers
plugins:
  mcp:
    servers:
      filesystem:
        command: npx
        args: ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
      github:
        command: npx
        args: ["-y", "@modelcontextprotocol/server-github"]
        env:
          GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_TOKEN}"
```

配置后，MCP server 提供的工具自动对 Agent 可用，与内置工具无差别使用。

### Zleap-Agent 的 MCP 运行时

Zleap-Agent 在 `packages/agent/` 中包含 MCP 运行时，支持动态启动和管理 MCP server 进程。MCP 工具与本地工具统一在 `ToolRegistry` 中注册，Agent 使用时不感知工具来源。

## ACP：Agent Client Protocol

**ACP（Agent Client Protocol）** 是 intelligent-terminal 提出的协议，用于宿主应用（如终端 IDE）与 Agent CLI 进程之间的通信。

### ACP 解决的问题

在 intelligent-terminal 出现之前，每个 IDE/终端想要集成 AI Agent 都需要做专门适配：
- VS Code 使用自己的 Agent 协议
- Cursor 是独立实现
- Claude Code 只能在终端中运行

ACP 提出了一个标准化协议，让**任意 Agent CLI**（Copilot/Claude/Codex/Gemini/OpenCode）可以被**任意宿主应用**（Terminal/IDE/Editor）集成。

### ACP 架构（intelligent-terminal 实现）

```
┌──────────────────────────────────────────────────────┐
│                  Windows Terminal                     │
│                                                       │
│  ┌─────────────┐   COM (MTA/MBM)   ┌──────────────┐  │
│  │ TerminalPage │◄────────────────►│ SharedWta    │  │
│  │ (C++/XAML)  │                   │ (单例)       │  │
│  └──────┬──────┘                   └──────┬───────┘  │
│         │                                 │          │
│         │ 每个标签页                       │ spawn    │
│         ▼                                 ▼          │
│  ┌─────────────┐  named pipe   ┌──────────────┐     │
│  │ wta-helper  │◄─────────────►│ wta-master   │     │
│  │ (Rust)      │   (ACP over   │ (Rust 单例)  │     │
│  │ 每标签页一个 │    Named Pipe)│              │     │
│  │ 预热启动     │               └──────┬───────┘     │
│  │ Stash保留    │                      │ stdio       │
│  └─────────────┘                      ▼             │
│                               ┌──────────────┐      │
│                               │ Agent CLI    │      │
│                               │ (ACP/JSON-RPC)│      │
│                               │ Claude/Codex/│      │
│                               │ Gemini/...   │      │
│                               └──────────────┘      │
└──────────────────────────────────────────────────────┘
```

### 双通道通信

ACP 在 intelligent-terminal 中使用两条通信通道：

| 通道 | 方向 | 传输 | 用途 |
|------|------|------|------|
| helper ↔ master | 双向 | Named Pipe (ACP/JSON-RPC 2.0) | 面板控制、消息传递、状态同步 |
| master ↔ Agent CLI | 双向 | stdio (ACP/JSON-RPC 2.0) | Agent 会话、工具调用、流式输出 |

### helper+master 双进程架构

- **wta-master（单例）**：管理 Agent CLI 进程的生命周期，负责启动/停止/重启 Agent CLI，路由消息
- **wta-helper（每标签页一个）**：每个终端标签页对应一个 helper 进程，维护与 master 的 ACP 会话，预热启动（pre-warmed）以减少延迟

### 预热启动 + Stash 模式

intelligent-terminal 有两个关键的 UX 优化：

1. **预热启动（Pre-warmed）**：创建标签页时就启动 stash 状态的 helper，ACP 会话在后台连接。用户第一次打开 Agent 面板时无需等待启动
2. **Stash 而非 Destroy**：用户按 `Ctrl+Shift+.` 切换 Agent 面板时，helper 进程、ConPTY 连接、ACP 会话、聊天历史全部保留（stash），再次打开时瞬间恢复

### 错误自动检测（Autofix）

Terminal 通过 OSC 133 shell 集成实现自动错误检测：

```
Shell 执行命令 → 退出时发送 OSC 133;D;exit_code
    → TerminalPage 捕获退出事件
    → COM 接口转发给 WTA
    → WTA 分类错误
    → 触发 Agent 修复建议（面板自动弹出或静默准备）
```

整个流程**不需要 Agent 轮询**——OSC 转义序列充当了 Shell→Terminal→Agent 的事件总线。

### wtcli：Agent 控制终端的工具

`wtcli` 是命令行工具，让 Agent 可以反过来控制终端：

```bash
# Agent 通过 shell out 调用 wtcli 控制终端
wtcli list-panes          # 列出所有面板
wtcli capture-pane --id 0 # 捕获面板内容
wtcli listen              # 监听终端事件
wtcli send-keys "ls"      # 向终端发送按键
```

这让 Agent 可以"看到"终端输出并"操作"终端。

## hermes-agent：多平台传输层

hermes-agent 实现了传输层抽象，支持同一套 Agent 逻辑部署到多个平台：

| 传输层 | 平台 | 特点 |
|--------|------|------|
| CLI Transport | 命令行终端 | 交互式终端会话 |
| Telegram Transport | Telegram Bot | 长轮询/Telegram Bot API |
| Discord Transport | Discord Bot | Discord Gateway/WebSocket |
| Webhook Transport | HTTP Webhook | 无状态 HTTP 请求-响应 |

传输层负责：
1. **接收用户消息**（从平台 API/长轮询/WebSocket）
2. **转换为统一消息格式**
3. **调用 Agent 处理**
4. **将回复发送回平台**
5. **处理平台特有功能**（如 Telegram 内联键盘、Discord 嵌入消息）

每个传输层有对应的"安全工具集"——例如 `hermes-telegram` 和 `hermes-discord` 工具集包含发送消息到对应平台的工具，`webhook-safe` 工具集排除危险操作（终端、写文件）。

## deepseek-harness：多协议集成

dsh 内置了丰富的协议支持：

| 协议/传输 | 包 | 用途 |
|-----------|-----|------|
| MCP | `mcp` | 工具/资源/提示词集成 |
| ACP | `acp` | Agent Client Protocol server |
| JSON-RPC | `sdk` | BFF 通信协议 |
| HTTP/WebSocket | `api` | BFF 层 |
| stdio | `shell`/`subprocess` | 子进程通信 |

特别是 `acp` 包让 dsh 可以作为 ACP server 运行，被支持 ACP 的宿主（如 intelligent-terminal）直接集成。

## 协议设计对比

| 维度 | MCP | ACP | hermes 传输层 | COM/OSC |
|------|-----|-----|--------------|---------|
| **定位** | 工具/数据/提示词协议 | Agent 控制协议 | 多平台部署 | 原生桌面集成 |
| **通信模式** | Client/Server (Agent调用外部工具) | Host/Agent (宿主控制Agent) | 平台适配层 | OS级IPC/终端序列 |
| **传输** | stdio, SSE | stdio, Named Pipe | HTTP, WebSocket, 长轮询 | COM(MTA), Named Pipe, OSC |
| **序列化** | JSON-RPC 2.0 | JSON-RPC 2.0 | 平台特定 | COM MBM/ANSI转义序列 |
| **典型场景** | Agent连接外部工具 | IDE/终端嵌入Agent | Agent部署到聊天平台 | 深度OS集成 |
| **状态** | 无状态(请求-响应) | 有状态(会话持久) | 平台相关 | 有状态(Stash) |
| **代表实现** | dsh/zleap mcp包 | intelligent-terminal | hermes transports | Windows Terminal |

## 协议选择指南

| 需求 | 推荐协议 |
|------|---------|
| 让 Agent 使用外部工具/数据源 | MCP（写 MCP Server） |
| 将 Agent 嵌入 IDE/终端/编辑器 | ACP（实现 ACP Server） |
| 将 Agent 部署到聊天平台 | hermes 式传输层抽象 |
| 深度桌面/OS 原生集成 | COM/Named Pipe/OSC 等 OS 机制 |
| 多 Agent 进程间通信 | JSON-RPC over stdio/pipe |

## 相关概念

- [工具系统](02-tool-system.md) — MCP 工具如何注册到框架的工具系统
- [插件化架构模式](08-plugin-architecture.md) — 协议包如何作为 Cordis 插件
- [Intelligent Terminal ACP 集成模式](/examples/intelligent-terminal-acp.md) — intelligent-terminal 代码级架构分析
