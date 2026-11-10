---
okf_version: "0.2"
type: Concept
title: "四个编程入口：Claude、Codex、OpenCode 与 Pi"
description: "对照四家 coding harness 的编程入口、进程模型、传输方式、会话机制与适合场景，并给出最小调用形状。"
tags: [claude-agent-sdk, codex-sdk, opencode, pi, sdk, rpc, comparison]
generated: { by: "lobsterai/main", at: "2026-11-10T15:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:05:00+08:00" }
status: stable
stale_after: "2027-04-30"
sources:
  - id: radar
    resource: https://www.thoughtworks.com/radar/techniques/coding-harness-for-general-purpose-agents
  - id: claude-sdk
    resource: https://code.claude.com/docs/en/agent-sdk/overview
  - id: codex-sdk
    resource: https://github.com/openai/codex/blob/main/sdk/typescript/README.md
  - id: codex-app-server
    resource: https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md
  - id: opencode-sdk
    resource: https://opencode.ai/docs/sdk/
  - id: opencode-server
    resource: https://opencode.ai/docs/server/
  - id: pi-sdk
    resource: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md
  - id: pi-cli
    resource: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli-integration.md
---

# 四个编程入口：Claude、Codex、OpenCode 与 Pi

> 文章点名了四条路：Claude Agent SDK、Codex SDK 与 app-server、OpenCode server 与 SDK、Pi SDK 与 RPC（F-007～F-010）。名字相近，形态差别很大；选型时先看进程边界，再看会话与权限。

## 1. 一张总表

| 入口 | 主要形态 | 进程/传输 | 会话 | 语言与包 |
|---|---|---|---|---|
| Claude Agent SDK | 库，驱动 Claude Code 运行时 | SDK 启动 `claude` CLI 子进程，stdio 通信（F-045） | 内置 sessions，可恢复/分叉（F-038） | Python、TypeScript |
| Codex SDK | 库，包装 Codex CLI | 启动 CLI，stdin/stdout 交换 JSONL（F-039） | `Thread` 可继续；`resumeThread()` 恢复（F-039） | TypeScript，`@openai/codex-sdk` |
| Codex app-server | 服务端 | JSON-RPC，长驻进程（F-040） | 线程管理、审批、记忆摘要（F-040） | 任意能发 JSON-RPC 的客户端 |
| OpenCode server + SDK | 无头 HTTP 服务 + 类型化客户端 | `opencode serve` 暴露 OpenAPI 3.1；SDK 由规范生成（F-041） | session API（F-041） | TypeScript，`@opencode-ai/sdk` |
| Pi SDK | 进程内库 | 直接嵌入 Node.js/Bun 进程（F-042） | `SessionManager` 持久化或内存模式（F-042） | TypeScript，`@earendil-works/pi-coding-agent` |
| Pi RPC | 长驻子进程 | JSONL 命令/响应/事件（F-042） | 会话由 Pi 进程持有（F-042） | 任意能读写 JSONL 的客户端 |

## 2. Claude Agent SDK：把 Claude Code 当库

官方定位很直接：SDK 提供与 Claude Code 相同的工具、agent loop 与上下文管理，用 Python 或 TypeScript 编程（F-037）。能力表里包括内置工具、hooks、subagents、MCP、permissions、sessions、skills/commands/memory 与 plugins（F-038）。

最小调用形状（官方文档示例，节选）。

```python
from claude_agent_sdk import query

async for message in query(prompt="Summarize the files in this directory"):
    print(message)
```

关键特征。

1. **子进程模型**：每个会话对应一个 `claude` CLI 子进程，会话记录默认落在本地磁盘（F-045）。这意味着部署时要考虑进程数、文件系统与状态持久化。
2. **能力完整**：技能、子代理、MCP、hooks 都在 SDK 层可用（F-038），适合“把编码 agent 原样搬进后端”的场景。
3. **权限在 SDK 层**：permissions 决定哪些工具自动运行、哪些需要审批；沙箱更多属于托管/容器层（F-045，口径见 E-1）。

## 3. Codex：SDK 与 app-server 是两条路

Codex 有两个容易混淆的入口。

**TypeScript SDK**：包装 `codex` CLI，通过 stdin/stdout 交换 JSONL 事件；npm 包 `@openai/codex-sdk`，要求 Node.js 18+（F-039）。

```typescript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();
const thread = codex.startThread();
const turn = await thread.run("Diagnose the test failure and propose a fix");
console.log(turn.finalResponse);
```

**app-server**：JSON-RPC 服务端，暴露线程管理、审批请求、记忆摘要等接口（F-040）。它适合需要长驻服务、多客户端连接、统一审批流的场景。

选型判断很简单。

1. 单进程脚本、批处理、CI 任务：优先 SDK。
2. 需要多客户端、集中审批、服务化：优先 app-server。
3. 两者不是互斥的“新旧版本”，而是不同边界（E-3）。

## 4. OpenCode：server 是本体，SDK 是客户端

OpenCode 的架构是“TUI 是客户端，server 是本体”。`opencode serve` 启动无头 HTTP server，暴露 OpenAPI 3.1 规范；SDK 由该规范生成（F-041）。

```typescript
import { createOpencode } from "@opencode-ai/sdk";

const { client } = await createOpencode();
```

关键特征。

1. **HTTP/OpenAPI 边界**：任何语言都能通过 HTTP 接入，不必绑定 TypeScript。
2. **会话 API 完整**：创建、列出、获取、子会话等都在 server API 中（F-041）。
3. **权限可配置**：allow、deny、ask 三种效果，无匹配规则时默认 ask（F-044）。
4. **版本要注意**：核验时文档重定向到 V1，页面同时给出 V2 入口（E-4）。

## 5. Pi：最小运行时，两种嵌入方式

Pi 的官方自述是 “minimal, extensible agent harness”（F-043）。它提供两种编程方式。

**SDK（进程内）**：`@earendil-works/pi-coding-agent` 直接在 Node.js 或 Bun 进程里创建会话（F-042）。

```typescript
import { createAgentSession } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession();
try {
  await session.prompt("What files are in the current directory?");
  console.log(session.getLastAssistantText());
} finally {
  session.dispose();
}
```

**RPC（进程外）**：`pi --mode rpc` 保持长驻，用 JSONL 双向传输命令、响应与事件（F-042）。

关键特征。

1. **进程内最轻**：没有额外的 CLI 子进程，适合嵌入桌面应用或本地工具。
2. **会话可控**：`SessionManager` 支持持久化与内存模式，适合“不想落盘”的场景（F-042）。
3. **默认克制**：跳过 sub-agents、plan mode 等功能，护栏留给扩展（F-043，措辞见 E-2）。

## 6. 怎么读这张表

不要先问“哪个最强”，先问四个问题。

1. **边界**：你要进程内库、子进程、HTTP 服务，还是 JSON-RPC 服务？
2. **语言**：团队主力是 Python、TypeScript，还是多语言？
3. **会话**：需要跨请求恢复、分叉、审计吗？
4. **权限**：审批与沙箱要在 SDK 层、服务层，还是交给扩展？

这四个问题的答案，通常比“模型谁更强”更能决定选型。

## 7. 小结

四个入口的代表性差异。

| 如果你想要 | 优先看 |
|---|---|
| 能力最全、与 Claude Code 行为一致 | Claude Agent SDK |
| TypeScript 单进程脚本、快速嵌入 | Codex SDK |
| 服务化、多客户端、统一审批 | Codex app-server |
| HTTP/OpenAPI、多语言接入 | OpenCode server + SDK |
| 最小依赖、进程内嵌入、完全可控 | Pi SDK |
| 进程隔离、跨语言控制 | Pi RPC |

下一篇进入运行时内部，看这些 harness 到底替你做了哪些事。
