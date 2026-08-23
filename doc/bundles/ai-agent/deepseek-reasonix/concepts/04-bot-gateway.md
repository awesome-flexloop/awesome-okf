---
type: Concept
title: Bot 网关
description: 多平台 IM bot 消息网关——gateway.go 核心、QQ/飞书适配器、connloop 重连、session 管理、消息渲染、队列模式
tags: [deepseek-reasonix, bot, gateway, qq, feishu, im, adapter]
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

## Bot 网关概述

`internal/bot` 包实现 Reasonix 的多渠道 IM bot 消息网关，支持 QQ、飞书、微信、钉钉四个平台。架构参考 Hermes Agent 的 gateway/adapter/session 模式。（F-068）

## 平台与会话类型

```go
type Platform string

const (
    PlatformQQ       Platform = "qq"
    PlatformFeishu   Platform = "feishu"
    PlatformWeixin   Platform = "weixin"
    PlatformDingtalk Platform = "dingtalk"
)

type ChatType string

const (
    ChatDM     ChatType = "dm"
    ChatGroup  ChatType = "group"
    ChatGuild  ChatType = "guild"
    ChatDirect ChatType = "direct"
    ChatThread ChatType = "thread"
)
```

（F-068, F-069）

## 消息结构

统一入站消息：

```go
type InboundMessage struct {
    Platform     Platform
    ConnectionID string
    Domain       string
    ChatType     ChatType
    ChatID       string
    UserID       string
    UserName     string
    OperatorID   string
    Text         string
    MessageID    string
    ThreadID     string
    MediaURLs    []string
    Media        []InboundMedia
    ResolveUserName func(context.Context) string
    Raw          any
}
```

出站消息支持文本、媒体、内联键盘和交互式卡片：

```go
type OutboundMessage struct {
    ConnectionID  string
    ChatID        string
    Text          string
    MediaURLs     []string
    ReplyToMsgID  string
    Keyboard      *InlineKeyboard
    Card          *InteractiveCard
}
```

（F-070）

## GatewayConfig

网关配置包含模型、审批模式、队列、配对、路由、白名单等：

```go
type GatewayConfig struct {
    Model             string
    ToolApprovalMode  string
    MaxSteps          int
    QueueMode         string
    QueueCap          int
    PairingEnabled    bool
    PairingTTL        time.Duration
    ApprovalTimeout   time.Duration
    WorkspaceRoot     string
    Channels          map[Platform]ChannelConfig
    Routes            []RouteConfig
    Allowlist         AllowlistConfig
    OnInbound         func(InboundMessage)
    OnSessionReady    func(InboundMessage, string) error
    Desktop           DesktopBridge
}
```

关键回调：
- `OnInbound`——每条白名单入站消息的观察者
- `OnSessionReady`——bot 创建/复用/恢复 controller 后通知宿主
- `OnToolApprovalModeChange`——持久化远程 IM 的审批模式变更（如 `/yolo`）

（F-071）

## 会话隔离

`BuildSessionKey` 按会话类型生成稳定的 session key：

```go
func BuildSessionKey(src SessionSource) string {
    switch src.ChatType {
    case ChatDM:
        scope = fmt.Sprintf("%s:dm:%s", source, src.ChatID)
    case ChatGroup:
        scope = fmt.Sprintf("%s:group:%s:%s", source, src.ChatID, src.UserID)
    case ChatThread:
        scope = fmt.Sprintf("%s:thread:%s", source, threadID)
    // ...
    }
    h := sha256.Sum256([]byte(scope))
    return hex.EncodeToString(h[:])[:16]
}
```

隔离策略：
- **DM**：按 chat 隔离（同一私聊共享历史）
- **群聊**：按 user 隔离（每人独立会话）
- **Thread**：thread 内所有人共享上下文

（F-073）

## 队列模式

并发入站消息通过四种队列模式处理：

```go
const (
    QueueModeSteer     = "steer"
    QueueModeFollowup  = "followup"
    QueueModeCollect   = "collect"
    QueueModeInterrupt = "interrupt"
)
```

- `steer`（默认）：将消息作为 mid-turn 引导注入活跃 turn
- `followup`：被动排队，下一轮排空
- `collect`：收集多条消息
- `interrupt`：中断当前 turn

默认队列容量 `DefaultQueueCap = 20`，丢弃策略有 `summarize`（默认）、`old`、`new`。（F-072）

## 连接生命周期

`RunWithRetry` 为持久连接适配器提供取消感知的指数退避重连：

```go
func RunWithRetry(ctx context.Context, log *slog.Logger, name string,
    cfg RetryConfig, attempt func(context.Context) error) {
    delay := cfg.InitialDelay  // 默认 1s
    for {
        err := attempt(ctx)
        if time.Since(start) >= cfg.ResetAfter {  // 默认 60s
            delay = cfg.InitialDelay
        }
        SleepCtx(ctx, delay)
        delay = nextDelay(delay, cfg.MaxDelay)  // 翻倍，上限 30s
    }
}
```

退避序列：1s → 2s → 4s → 8s → 16s → 30s（上限）。连接保持健康 60s 后重置为 1s。（F-074）

`SleepCtx` 替代 `time.Sleep`，使 Stop 及时生效：

```go
func SleepCtx(ctx context.Context, d time.Duration) bool {
    select {
    case <-ctx.Done():
        return false
    case <-t.C:
        return true
    }
}
```

（F-075）

## QQ 适配器

QQ 适配器实现 `bot.Adapter` 接口，使用 `golang.org/x/net/websocket` 连接 QQ Bot API v2 gateway：

```go
type adapter struct {
    cfg    config.QQBotConfig
    msgCh  chan bot.InboundMessage
    conn   *websocket.Conn
    sessionID   string
    seq         int64
    token       string
    tokenExpiry time.Time
    // ...
}

func (a *adapter) Platform() bot.Platform { return bot.PlatformQQ }
func (a *adapter) Start(ctx context.Context) error { ... }
func (a *adapter) Stop() error { ... }
func (a *adapter) Send(ctx context.Context, msg bot.OutboundMessage) (bot.SendResult, error) { ... }
func (a *adapter) Messages() <-chan bot.InboundMessage { return a.msgCh }
```

支持 C2C、group、guild、direct message，inline keyboard 审批。Stop 取消 context、关闭 WebSocket、等待 gatewayLoop 退出。（F-076）

## 飞书适配器

飞书适配器通过 `withTransientRetry` 处理传输级错误：

```go
const (
    transientRetryAttempts  = 3
    transientRetryBaseDelay = 500 * time.Millisecond
    transientRetryMaxDelay  = 5 * time.Second
)

func withTransientRetry(ctx context.Context, logger *slog.Logger,
    op string, fn func(context.Context) error) error {
    // 仅重试 connection reset、timeout、broken pipe 等
    // API 级错误（rate limit、permission）原样返回
}
```

幂等性通过 `newIdempotencyKey` 保证：每次逻辑发送生成 16 字节随机 hex 作为 `uuid` 字段，重试时复用，防止响应读取失败导致重复消息。（F-077, F-078）

## 消息渲染

`renderSink` 将 Reasonix 事件流渲染为平台消息：

```go
type renderSink struct {
    adapter    Adapter
    editor     messageEditor
    buf        strings.Builder
    thinking   strings.Builder
    toolNames  map[string]string
    liveMsgID  string
    // ...
}
```

`messageEditor` 是可选能力接口：

```go
type messageEditor interface {
    EditMessage(ctx context.Context, messageID string, msg OutboundMessage) error
}
```

实现该接口的适配器（飞书，通过 `Im.Message.Patch`）获得回合中流式输出——渲染器不断原地编辑同一条 "live 消息"，而非等到回合结束一次性发送。（F-079）

渲染常量：

| 常量 | 值 | 说明 |
|------|-----|------|
| `renderSoftFlushAfter` | 1200ms | 软刷新间隔 |
| `renderMaxChunkRunes` | 1800 | 单块最大字符数 |
| `renderHardChunkRunes` | 3500 | 硬上限 |
| `renderProgressMinInterval` | 2s | 进度消息最小间隔 |

（F-080）

## 白名单与访问控制

`AllowlistConfig` 控制哪些用户/群可使用 bot：

```go
type AllowlistConfig struct {
    Enabled   bool
    AllowAll  bool
    Users     map[Platform][]string
    Approvers map[Platform][]string
    Admins    map[Platform][]string
    Groups    map[Platform][]string
}
```

`AccessConfig` 对单个 bot 连接做更细粒度控制，支持 pairing 模式。`ApprovalTimeout` 限制工具审批等待远程用户回复的时间（0 用默认值，负值无限等待）。

## 相关概念

- [ACP 协议](/concepts/03-acp-protocol.md)——另一种前端传输
- [Agent 运行循环](/concepts/02-agent-run-loop.md)——bot 会话驱动的核心
- [CLI 与 TUI](/concepts/05-cli-tui.md)——`reasonix bot` 命令
- [Bot 网关示例](/examples/02-bot-gateway.md)——配置和接入示例
