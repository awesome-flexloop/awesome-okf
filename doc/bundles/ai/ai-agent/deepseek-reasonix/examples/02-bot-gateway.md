---
type: Example
title: Bot 网关配置
description: 配置和启动 Reasonix Bot 网关，接入 QQ 和飞书平台，管理会话隔离和消息队列
tags: [deepseek-reasonix, bot, gateway, qq, feishu, config]
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

Reasonix Bot 网关将 agent 能力接入即时通讯平台。目前支持 QQ、飞书、微信、钉钉四个平台。网关采用三层架构：Adapter（平台连接）、Session（会话隔离）、Render（消息渲染）。

## 启动 Bot

```sh
reasonix bot start
```

启动前需要在配置中启用至少一个平台。网关使用 `boot.BuildRuntime` 组装 controller，与 CLI/ACP/Desktop 共享同一核心引擎。

## 平台配置

### QQ Bot

QQ 适配器实现 QQ 官方 Bot API v2，使用 WebSocket gateway 连接：

```toml
[bot.qq]
enabled = true
app_id = "your_app_id"
secret = "your_secret"
token = "your_token"
```

QQ 适配器特性：
- WebSocket gateway 连接、heartbeat、resume
- REST API 回复消息
- C2C / group / guild / direct message 支持
- Inline keyboard 审批
- Access token 自动获取和刷新

适配器通过 `bot.Adapter` 接口实现四个方法：

```go
type Adapter interface {
    Platform() Platform
    Name() string
    Start(ctx context.Context) error
    Stop() error
    Send(ctx context.Context, msg OutboundMessage) (SendResult, error)
    SendTyping(ctx context.Context, chatID string) error
    Messages() <-chan InboundMessage
}
```

QQ 适配器的 `Stop` 会取消 context、关闭 WebSocket 连接并等待 gatewayLoop 退出——不等待会留下占用 gateway session 的僵尸连接。

### 飞书 Bot

```toml
[bot.feishu]
enabled = true
app_id = "cli_xxx"
app_secret = "xxx"
verification_token = "xxx"
encrypt_key = "xxx"
```

飞书适配器特性：
- HTTP webhook 接收消息
- `Im.Message.Patch` 原地编辑实现流式输出
- 传输级错误自动重试（3 次，500ms→5s 指数退避）
- 幂等 key 防止重复消息

飞书的 `withTransientRetry` 仅重试传输级错误（connection reset、timeout、broken pipe），API 级错误（rate limit、permission）原样返回：

```go
const (
    transientRetryAttempts  = 3
    transientRetryBaseDelay = 500 * time.Millisecond
    transientRetryMaxDelay  = 5 * time.Second
)
```

每次逻辑发送生成 16 字节随机 hex 作为 `uuid` 去重字段，重试时复用同一 key。

## 会话隔离

网关根据会话类型自动隔离上下文：

```go
func BuildSessionKey(src SessionSource) string {
    switch src.ChatType {
    case ChatDM:
        // 私聊：按 chat 隔离（同一 DM 共享历史）
        scope = source + ":dm:" + src.ChatID
    case ChatGroup:
        // 群聊：按 user 隔离（每人独立会话）
        scope = source + ":group:" + src.ChatID + ":" + src.UserID
    case ChatThread:
        // Thread：thread 内所有人共享
        scope = source + ":thread:" + threadID
    }
    h := sha256.Sum256([]byte(scope))
    return hex.EncodeToString(h[:])[:16]
}
```

这意味着：
- 私聊中同一人的消息共享一个 agent 会话
- 群聊中每个人有独立的会话（互不干扰）
- Thread 话题中所有人共享上下文

## 队列模式

当 agent 正在处理 turn 时收到新消息，网关支持四种处理模式：

| 模式 | 行为 |
|------|------|
| `steer`（默认） | 将消息作为 mid-turn 引导注入当前 turn |
| `followup` | 排队等待，下一轮处理 |
| `collect` | 收集多条消息 |
| `interrupt` | 中断当前 turn |

```toml
[bot]
queue_mode = "steer"
queue_cap = 20
queue_drop = "summarize"
```

丢弃策略：
- `summarize`（默认）：摘要后丢弃
- `old`：丢弃最旧的
- `new`：丢弃最新的

## 白名单与访问控制

```toml
[bot.allowlist]
enabled = true
allow_all = false

[bot.allowlist.users.feishu]
users = ["ou_xxx", "ou_yyy"]
admins = ["ou_zzz"]

[bot.allowlist.groups.qq]
groups = ["group_id_1"]
```

角色层级：
- **Users**：可使用 bot
- **Approvers**：可审批工具调用
- **Admins**：管理员权限

也支持 per-connection 的 `AccessConfig`，可为每个 bot 连接单独配置访问规则。

## 工具审批

Bot 会话中的工具审批通过交互式消息完成：

- **QQ**：使用 inline keyboard 按钮批准/拒绝
- **飞书**：使用交互式卡片

审批超时通过 `ApprovalTimeout` 配置：
- `0`：使用默认超时
- 负值：无限等待
- 正值：指定超时时间

超时可防止被遗弃的审批永久阻塞 bot 会话。

## 消息渲染

`renderSink` 将 agent 事件流渲染为平台消息：

- 支持 `messageEditor` 接口的平台（飞书）获得原地编辑流式输出
- 不支持的平台（QQ）分段发送
- 软刷新间隔 1200ms，单块最大 1800 字符，硬上限 3500 字符
- 进度消息最小间隔 2 秒，最多 3 条

渲染器处理 thinking 块、tool call 卡片、最终答案的 Markdown 格式化。

## 连接重连

所有持久连接适配器使用 `RunWithRetry`：

```go
bot.RunWithRetry(ctx, logger, "qq", bot.RetryConfig{
    InitialDelay: 1 * time.Second,
    MaxDelay:     30 * time.Second,
    ResetAfter:   60 * time.Second,
}, func(ctx context.Context) error {
    // 一次完整连接生命周期，阻塞直到断开或出错
    return adapter.connectAndServe(ctx)
})
```

退避序列：1s → 2s → 4s → 8s → 16s → 30s（上限）。连接保持健康 60 秒后重置为 1s。

`SleepCtx` 替代 `time.Sleep`，确保 `Stop()` 及时生效而非阻塞到退避结束。

## 桌面集成

当网关嵌入桌面应用时，通过 `DesktopBridge` 接口提供：
- 全局桌面会话状态查看
- 事件订阅
- 远程审批任何活跃桌面会话
- `/desktop` 系列命令

独立运行（`reasonix bot start`）时 `Desktop` 字段为 nil。

## 相关概念

- [Bot 网关](../concepts/04-bot-gateway.md)——网关架构详解
- [Agent 运行循环](../concepts/02-agent-run-loop.md)——steer 队列如何注入 turn
- [CLI 与 TUI](../concepts/05-cli-tui.md)——`reasonix bot` 命令
- [基础使用](01-basic-usage.md)——安装和配置
