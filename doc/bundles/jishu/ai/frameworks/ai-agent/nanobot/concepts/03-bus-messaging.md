---
type: Concept
title: 消息总线与事件驱动
description: MessageBus 基于 asyncio.Queue 实现通道与代理核心的解耦，WebSocket 通道提供双向实时通信、流式传输、多聊天复用和令牌认证。
tags: [nanobot, message-bus, websocket, event-driven, async]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: nanobot 源码信源
---

# 消息总线与事件驱动

nanobot 的消息总线是通道与代理核心之间的异步解耦层。所有外部输入（CLI、WebUI、聊天应用）都通过统一的消息模式进入代理循环，响应也通过同一总线返回。WebSocket 通道在此基础上提供了双向实时网络通信能力。

## MessageBus 实现

`MessageBus` 位于 `nanobot/bus/queue.py`，实现极为精简——仅封装两个 `asyncio.Queue`：

```python
from nanobot.bus.events import InboundMessage, OutboundMessage

class MessageBus:
    """Async message bus that decouples chat channels from the agent core."""

    def __init__(self):
        self.inbound: asyncio.Queue[InboundMessage] = asyncio.Queue()
        self.outbound: asyncio.Queue[OutboundMessage] = asyncio.Queue()

    async def publish_inbound(self, msg: InboundMessage) -> None:
        await self.inbound.put(msg)

    async def consume_inbound(self) -> InboundMessage:
        return await self.inbound.get()

    async def publish_outbound(self, msg: OutboundMessage) -> None:
        await self.outbound.put(msg)

    async def consume_outbound(self) -> OutboundMessage:
        return await self.outbound.get()
```

来源：`nanobot/bus/queue.py:1-44`

总线还提供 `inbound_size` 和 `outbound_size` 属性用于监控队列积压：

```python
@property
def inbound_size(self) -> int:
    return self.inbound.qsize()

@property
def outbound_size(self) -> int:
    return self.outbound.qsize()
```

来源：`nanobot/bus/queue.py:36-44`

## 数据流模式

### 经总线的交互模式（网关 / 交互 CLI）

```text
Channel → publish_inbound(InboundMessage) → AgentLoop.run()
                                          → AgentRunner
                                          → Provider/Tools
AgentLoop → publish_outbound(OutboundMessage) → Channel
```

在 classic CLI 交互模式中，CLI 自身充当一个通道：

```python
bus = MessageBus()

# 启动代理循环
bus_task = asyncio.create_task(agent_loop.run())

# 发布用户消息
await bus.publish_inbound(InboundMessage(
    channel=cli_channel,
    sender_id="user",
    chat_id=cli_chat_id,
    content=user_input,
    metadata={"_wants_stream": True},
))

# 消费响应
msg = await asyncio.wait_for(bus.consume_outbound(), timeout=1.0)
event = outbound_event_from_message(msg)
```

来源：`nanobot/cli/agent.py:157,302-405`

### 直发模式（单发 CLI / SDK）

单发请求绕过总线，直接调用 `process_direct()`，避免不必要的队列开销：

```python
# SDK 内部
response = await self._loop.process_direct(
    message,
    **kwargs,
    hooks=per_run_hooks,
)
```

来源：`nanobot/nanobot.py:195-199`

## WebSocket 通信

WebSocket 是 TUI 和 WebUI 与网关通信的核心通道。它支持：

- 双向实时通信
- 流式 token 传输（`delta` + `stream_end`）
- 多聊天复用（一个连接承载多个 `chat_id`）
- 令牌认证（静态令牌和短期签发令牌）
- TLS/SSL（强制最低 TLSv1.2）
- 客户端白名单（`allowFrom`）
- 死连接自动清理

### 默认配置

```json
{
  "channels": {
    "websocket": {
      "host": "127.0.0.1",
      "port": 8765,
      "path": "/",
      "websocketRequiresToken": true,
      "allowFrom": ["*"],
      "streaming": true
    }
  }
}
```

来源：`docs/websocket.md:22-36`

### 连接 URL 格式

```text
ws://{host}:{port}{path}?client_id={id}&token={token}
```

- `client_id`：可选，用于 `allowFrom` 授权，省略时自动生成 `anon-xxxxxxxxxxxx`
- `token`：当 `websocketRequiresToken` 为 true 或配置了静态 token 时必需

来源：`docs/websocket.md:70-80`

### 服务端 → 客户端事件

| 事件 | 说明 |
|------|------|
| `ready` | 连接建立后立即发送，包含默认 `chat_id` |
| `message` | 完整代理响应 |
| `delta` | 流式文本片段 |
| `stream_end` | 流式段结束标记 |
| `reasoning_delta` | 推理/思考内容增量 |
| `reasoning_end` | 推理流结束标记 |
| `runtime_model_updated` | 网关默认运行时模型变更广播 |
| `attached` | `new_chat`/`attach` 确认 |
| `error` | 软错误，连接保持打开 |

来源：`docs/websocket.md:85-181`

`ready` 事件示例：

```json
{
  "event": "ready",
  "chat_id": "uuid-v4",
  "client_id": "alice"
}
```

流式 `delta` 事件示例：

```json
{
  "event": "delta",
  "chat_id": "uuid-v4",
  "text": "Hello",
  "stream_id": "s1"
}
```

来源：`docs/websocket.md:89-120`

### 客户端 → 服务器事件

| 类型 | 字段 | 效果 |
|------|------|------|
| `new_chat` | — | 服务器生成新 `chat_id`，回复 `attached` |
| `attach` | `chat_id` | 订阅已有聊天（如页面重载后） |
| `message` | `chat_id`, `content` | 在指定聊天发送消息，首次使用自动附加 |

来源：`docs/websocket.md:197-205`

TUI 客户端的 `send()` 方法展示了消息信封的构造：

```typescript
send(content: string, options: MessageOptions = {}): string {
    if (!this.chatId) throw new Error("chat is not ready")
    const turnId = crypto.randomUUID()
    this.write({
        type: "message",
        chat_id: this.chatId,
        content,
        turn_id: turnId,
        webui: true,
        ...(options.userShell ? { user_shell: true } : {}),
        ...(options.cliApps?.length ? { cli_apps: options.cliApps } : {}),
        ...(options.mcpPresets?.length ? { mcp_presets: options.mcpPresets } : {}),
    })
    return turnId
}
```

来源：`tui/src/protocol.ts:936-953`

## 多聊天复用

单个 WebSocket 连接可承载多个并发聊天。服务器维护 `chat_id → {connections}` 的扇出集合，同一聊天可跨多个连接镜像（如两个浏览器标签页）。

`chat_id` 格式为 `^[A-Za-z0-9_:-]{1,64}$`，不匹配的值返回 `error` 事件。

```text
client                                server
  | --- connect -------------------->  |
  | <-- {"event":"ready",              |
  |      "chat_id":"d3..."}   (default)|
  | --- {"type":"new_chat"} --------->  |
  | <-- {"event":"attached",            |
  |      "chat_id":"a1..."}             |
  | --- {"type":"message",              |
  |      "chat_id":"a1...",             |
  |      "content":"hi"} ------------>  |
  | <-- {"event":"delta", ...}          |
  | <-- {"event":"stream_end", ...}     |
```

来源：`docs/websocket.md:364-389`

## 认证与安全

### 令牌签发流程

1. 客户端发送 `GET {tokenIssuePath}`，携带 `Authorization: Bearer {tokenIssueSecret}`
2. 服务器返回单次使用令牌：`{"token": "nbwt_...", "expires_in": 300}`
3. 客户端使用 `?token=nbwt_...` 打开 WebSocket
4. 令牌被消费（单次使用），不可重用

限制：
- 签发令牌单次使用
- 未完成令牌上限 10,000（超出返回 HTTP 429）
- 过期令牌在每次签发或验证时惰性清理
- TTL 默认 300 秒（30–86,400 秒可配）

来源：`docs/websocket.md:261-363`

### 安全措施

- **时序安全比较**：静态令牌使用 `hmac.compare_digest` 防止时序攻击
- **纵深防御**：`allowFrom` 在 HTTP 握手和消息两个层级检查
- **TLS 强制**：启用 SSL 时最低 TLSv1.2
- **默认安全**：`websocketRequiresToken` 默认为 `true`
- **chat_id 作为能力令牌**：持有有效认证凭证和 chat_id 即可附加到该对话

来源：`docs/websocket.md:406-413`

### 可信代理无令牌模式

`trustedProxyAuth` 提供两部分无令牌授权，适用于身份感知反向代理（如 Cloudflare Tunnel + Cloudflare Access）：

1. 直接 TCP 对等端必须匹配 `trustedPeerCidrs` 之一
2. 配置的 `assertionHeader` 必须存在且非空

仅信任 CIDR 不足以授权。nanobot 仅使用 `connection.remote_address` 进行对等端检查，不信任 `X-Forwarded-For`、`X-Real-IP` 等转发头。

来源：`docs/websocket.md:283-328`

## 相关概念

- [整体架构](01-architecture.md)
- [Agent 运行时](02-agent-runtime.md)
- [多接口架构](05-multi-interface.md)
- [SDK 类型系统](04-sdk-types.md)
