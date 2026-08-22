---
type: reference
title: "Agent 核心 API 参考"
description: "internal/agent 与 internal/provider 的核心类型、接口与函数签名速查，覆盖 Agent、Session、SubagentScheduler、TaskTool 与 Provider 抽象。"
tags: [reference, agent, provider, session, scheduler]
sources:
  - resource: "/spec/facts.md"
    title: "DeepSeek Reasonix 事实清单"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# Agent 核心 API 参考

本文件汇总 `internal/provider`、`internal/agent` 两个包中与"编码 Agent 运行时"直接相关的类型与函数。所有签名均与事实清单（`/spec/facts.md`）逐字一致。

## Provider 抽象（internal/provider/provider.go）

```go
// Provider 是模型提供方的接口，所有具体模型实现它。
type Provider interface {
    Name() string
    Stream(ctx context.Context, req Request) (<-chan Chunk, error)
}

// Factory 从解析后的 Config 构建 Provider。
type Factory func(cfg Config) (Provider, error)

// Register 以 kind 字符串注册工厂（供 init() 调用，重复 kind 会 panic）。
func Register(kind string, f Factory)

// New 按 kind 实例化 Provider。
func New(kind string, cfg Config) (Provider, error)
```

请求与协议类型：

```go
// Request 是一次流式补全请求。
type Request struct {
    Messages    []Message
    Tools       []ToolSchema
    Temperature *float64
    MaxTokens   int
    ResponseFormat *ResponseFormat
    EffortOverride string
}

// Message 是会话中的一条消息，含推理回传字段。
type Message struct {
    Role             Role
    Content          string
    ReasoningContent string          // 思考模式链式思考，跨轮回传
    ReasoningID      string          // 提供方颁发的推理条目 id
    ReasoningStatus  string          // "in_progress" | "completed"
    ReasoningSignature string        // 带签名的思考块（Anthropic 要求回放）
    ToolCalls        []ToolCall
    ToolCallID       string
    Name             string
    // ...（另有 RawContent、Images、ResponsesItems、LocalOnly、DecisionReceipts 等）
}

// Chunk 是流式增量。
type Chunk struct {
    Type      ChunkType
    Text      string
    Signature string
    ReasoningID     string
    ReasoningStatus string
    ToolCall  *ToolCall
    ArgChars  int
    Usage     *Usage
    Err       error
}
```

输出预算常量（`AutoOutputBudget` 使用）：

```go
const (
    DefaultOrdinaryOutputTokens      = 16 * 1024
    DefaultReasoningOutputTokens     = 32 * 1024
    DefaultHighReasoningOutputTokens = 64 * 1024
    DefaultHighOutputTokens          = 128 * 1024
    DeepSeekMaxOutputTokens          = 384_000
)

func AutoOutputBudget(reasoningEnabled bool, effort string) int
```

能力探测接口：

```go
// ToolCallReasoningPolicy 标识"工具调用回合是否重放 reasoning_content"。
type ToolCallReasoningPolicy interface {
    RequiresToolCallReasoning() bool
}
```

## Agent 结构（internal/agent/agent.go）

```go
type Agent struct {
    agentConfig
    svc  agentServices
    sess sessionRuntime
    // 推理与响应语言（atomic.Value，值为 auto|zh|en）
    responseLanguage  atomic.Value
    reasoningLanguage atomic.Value
    planMode          atomic.Bool
    mutationDependencyBarrier atomic.Pointer[mutationBarrierCause]
    steerMu           sync.Mutex
    steerQueue        []steerEntry
    task              taskRuntime
    turn              turnRuntime
    // ...（更多会话/任务/回合状态字段）
}

// New 构造一个 Agent。
func New(prov provider.Provider, tools *tool.Registry, session *Session, opts Options, sink event.Sink) *Agent
```

相关常量与辅助函数：

```go
const DefaultMaxSubagentDepth = 2
func NormalizeMaxSubagentDepth(depth int) int

const maxToolOutputBytes = 32 * 1024

// MidTurnSteerPrefix 是"回合中引导"入队时的消息前缀。
const MidTurnSteerPrefix = "[Mid-turn steer queued by the user. ...]"
```

## Session（internal/agent/session.go）

```go
type Session struct {
    mu             sync.RWMutex
    Messages       []provider.Message
    version        uint64
    rewriteVersion int
    // ...（persistedRewriteVersion、normalizedDirty、rawMessages、writeAuth 等）
}

func NewSession(system string) *Session
func (s *Session) Add(m provider.Message)
```

## 子代理调度（internal/agent/scheduler.go）

```go
type SubagentSlotStatus string

const (
    SubagentSlotQueued  SubagentSlotStatus = "queued"
    SubagentSlotRunning SubagentSlotStatus = "running"
    SubagentSlotDone    SubagentSlotStatus = "done"
    SubagentSlotFailed  SubagentSlotStatus = "failed"
)

type AcquireRequest struct {
    Writer     bool
    WritePaths WritePathSet
    Nested     bool
    Label      string
}

type SubagentScheduler struct {
    mu           sync.Mutex
    maxTotal     int
    maxWriters   int
    activeTotal  int
    activeWriters int
    parentClaims []WritePathSet
    waiters      []*schedulerWaiter
}

func NewSubagentScheduler(maxTotal, maxWriters int) *SubagentScheduler
```

## 子代理任务工具（internal/agent/task.go）

```go
type TaskTool struct { /* ... */ }
type ReadOnlyTaskTool struct { /* ... */ }

func NewTaskToolWithOptions(opts TaskToolOptions) *TaskTool
func NewTaskTool(prov provider.Provider, pricing *provider.Pricing, parentReg *tool.Registry, /* ... */)

func RunSubAgentWithSession(ctx context.Context, prov provider.Provider, reg *tool.Registry,
    sess *Session, prompt string, opts Options, sink event.Sink) (string, error)
func NewPlannerAgent(prov provider.Provider, reg *tool.Registry, sess *Session, opts Options, sink event.Sink) *Agent
func RunReadOnlySubAgentWithSession(/* ... */)
```

## 相关概念

- [/concepts/01-agent-runtime.md](/concepts/01-agent-runtime.md)
- [/references/acp-protocol-api.md](/references/acp-protocol-api.md)
- [/references/cli-bot-api.md](/references/cli-bot-api.md)