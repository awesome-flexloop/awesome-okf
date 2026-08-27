---
type: Concept
title: ACP 协议
description: Agent Client Protocol v1 实现——NDJSON JSON-RPC 2.0、protocol.go 消息格式、server/client、inbox 队列、dispatch 事件映射、Factory 组装
tags: [deepseek-reasonix, acp, json-rpc, protocol, editor, ndjson]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-23T00:00:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-23T00:00:00Z
status: stable
stale_after: 2027-08-23
sources:
  - id: SRC-001
    resource: /references/source.md
    title: DeepSeek-Reasonix 源码信源索引
---

## ACP 概述

ACP（Agent Client Protocol）是 Reasonix 与编辑器（如 VS Code）通信的协议。Reasonix 实现 ACP v1，通过标准输入/输出上的 NDJSON JSON-RPC 2.0 通信。编辑器启动进程，打开一个或多个工作区范围的 session，接收流式消息、工具活动、计划、权限请求和配置更新。（F-056）

包注释明确声明 ACP 是 v2 内核之上的**适配层**，仅依赖稳定契约：

```go
// Package acp implements the Agent Client Protocol
// (https://agentclientprotocol.com) transport: a stdio JSON-RPC 2.0 agent
// that editors and other host clients speak to drive Reasonix.
```

（F-056）

## 协议版本与错误码

```go
const ProtocolVersion = 1

const (
    ErrParse          = -32700
    ErrInvalidRequest = -32600
    ErrMethodNotFound = -32601
    ErrInvalidParams  = -32602
    ErrInternal       = -32603
)
```

（F-057, F-058）

## 连接层：Conn

`Conn` 封装 NDJSON JSON-RPC 连接：

```go
type Conn struct {
    r       io.Reader
    wmu     sync.Mutex
    enc     *json.Encoder
    nextID  atomic.Int64
    pending map[int64]chan rpcResult
    reqH    map[string]RequestHandler
    notH    map[string]NotificationHandler
    closed  chan struct{}
}
```

关键设计：
- **写序列化**：`wmu sync.Mutex` 确保多 goroutine 的写不交错行
- **请求并发**：每个 inbound request/notification 在独立 goroutine 运行，长 prompt 不阻塞 cancellation
- **出站请求**：通过 `pending` map 按 id 关联回复（如 `session/request_permission`）
- **消息大小限制**：`maxMessageBytes = 32 MiB`
- **HTML 转义禁用**：encoder 设置 `SetEscapeHTML(false)` 以匹配 main 分支的 `JSON.stringify` 输出

（F-061, F-062）

Handler 类型：

```go
type RequestHandler func(ctx context.Context, params json.RawMessage) (any, error)
type NotificationHandler func(ctx context.Context, params json.RawMessage)
```

## 能力协商

### 客户端能力

`InitializeParams` 携带客户端信息：

```go
type InitializeParams struct {
    ProtocolVersion    int                `json:"protocolVersion"`
    ClientInfo         *Implementation    `json:"clientInfo,omitempty"`
    ClientCapabilities ClientCapabilities `json:"clientCapabilities,omitempty"`
}

type ClientCapabilities struct {
    FS       FSCapabilities `json:"fs,omitempty"`
    Terminal bool           `json:"terminal,omitempty"`
    Meta     map[string]any `json:"_meta,omitempty"`
}
```

客户端可提供：
- **FS 代理**：`fs/read_text_file`、`fs/write_text_file`——让文件工具看到未保存的编辑器缓冲区
- **Terminal**：客户端拥有的终端运行前台 bash
- **Meta**：vendor 能力块（容忍解析，未知条目只是关闭该特性）

（F-059）

### Agent 能力

`InitializeResult` 通告 agent 支持：

```go
type AgentCapabilities struct {
    LoadSession         bool
    SessionCapabilities SessionCapabilities  // list/resume/close/delete
    PromptCapabilities  PromptCapabilities   // image/audio/embeddedContext
    MCPCapabilities     MCPCapabilities      // http/sse
    Meta                map[string]any
}
```

- `loadSession: true`——支持持久化会话加载
- Prompt 支持 `embeddedContext`（内联资源文本），不支持 image/audio
- MCP 支持 `http` 和 stdio，不支持 legacy `sse`

（F-060）

Reasonix 特定扩展通过 `_meta["reasonix.io"]` 通告：
- `sessionSteer`——mid-turn 引导方法
- `sessionInbox`——持久化 session 级指令队列（schemaVersion 1）
- `sessionReloadExtensions`——运行时重载扩展
- `extensionSurface`——结构化扩展 UI surface

## 消息处理：Serve

`Serve` 是 `reasonix acp` 命令调用的唯一入口点：

```go
func Serve(ctx context.Context, r io.Reader, w io.Writer,
    factory Factory, info AgentInfo) error
```

注册的 handler 包括：

| 方法 | 说明 |
|------|------|
| `initialize` | 握手和能力协商 |
| `authenticate` | 认证 |
| `session/new` | 创建新 session |
| `session/load` | 加载持久化 session |
| `session/resume` | 恢复 session |
| `session/prompt` | 发送 prompt（阻塞直到 turn 完成） |
| `_reasonix.io/session/steer` | mid-turn 引导 |
| `_reasonix.io/session/inbox/*` | inbox 队列操作 |

（F-064）

## Factory 模式

ACP 包不直接组装 agent，而是通过 `Factory` 接口委托给 composition root：

```go
type Factory interface {
    NewSession(ctx context.Context, p SessionParams) (*control.Controller, error)
}

type SessionParams struct {
    Cwd             string
    MCPServers      []plugin.Spec
    Sink            event.Sink
    Model           string
    EffortOverride  *string
    RuntimeProfile  string
    FileOverlay     builtin.FileOverlay
    Terminal        builtin.TerminalRunner
    // ...
}
```

CLI 的 `reasonix acp` 命令实现 Factory，复用 `setup()` 的组装逻辑（Provider、以 Cwd 为根的工具 Registry、per-session MCP host、event Sink）。返回的 Controller 拥有自己的清理（Close 停止 MCP 子进程）。（F-063）

## 事件分发：updateSink

`updateSink` 是绑定到单个 session 的 `event.Sink`，将 agent 的类型化事件流映射到 ACP `session/update` 通知：

```go
type updateSink struct {
    conn      notifier
    sessionID string
    cwd       string
    approve   func(id string, allow, session, persist bool)
    answer    func(id string, answers []event.AskAnswer)
    // ...
}
```

事件映射：
- **ToolDispatch** → 发出 pending `tool_call`（携带 rawInput）
- **ToolResult** → 发出 `tool_call_update`（completed/failed）
- **ApprovalRequest** → 发起 `session/request_permission` 往返请求，等待用户批准
- Message/Usage/Phase/TurnStarted/TurnDone 不在 main 的 update 集合中，被丢弃（TurnDone 的结果作为 `session/prompt` 的 stopReason 返回）

tool result 跨线传输时裁剪到 `maxResultChars = 8000` 字符（完整结果仍发送给 model）。（F-065, F-066）

## Inbox 队列

ACP 支持持久化 session 级指令队列，两种意图：

```go
if intent == sessioninbox.IntentSteer {
    rec, err = api.TryEnqueueAndSteer(req)
} else {
    rec, err = api.EnqueueInbox(req)
}
```

- **Steer**：尝试入队并立即注入活跃 turn
- **Followup**：被动入队，prompt handler 在下一轮排空

Inbox 方法包括：enqueue、list、get、update、delete、move、pause、retry。（F-067）

## stdout/stderr 纪律

标准输出是 JSON-RPC 通道。所有其他输出（日志、诊断）必须走 stderr，否则会破坏 wire 格式。文档明确警告：

> stdout is the JSON-RPC channel: callers must keep all other output (logs, diagnostics) off w and on stderr, or the wire corrupts.

## 启动命令

```sh
reasonix acp
reasonix acp --model deepseek-pro
```

`--model` 选择客户端未覆盖时的启动模型。未配置 provider 时，initialize 响应通告 terminal 认证方法，启动 `reasonix setup`。

## 相关概念

- [项目架构](01-project-architecture.md)——boot.BuildRuntime 如何被 Factory 使用
- [Agent 运行循环](02-agent-run-loop.md)——ACP session/prompt 驱动的核心循环
- [CLI 与 TUI](05-cli-tui.md)——CLI 的 acp 子命令
- [Bot 网关](04-bot-gateway.md)——另一种前端传输方式
