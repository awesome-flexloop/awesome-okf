---
type: Concept
title: "Gateway 与通道：IM 消息路由、WS/CLI Hub"
description: "Gateway 全局交互入口、GlobalProcessor 消息处理、ChannelManager 通道管理、WebSocket/CLI 内置通道、飞书/钉钉/QQ/Discord/企微等 IM 通道、Slash 抢占取消。"
tags: [octop, gateway, channel, im, websocket, slash, cron]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/gateway.md
    title: Gateway 源码信源
---

# Gateway 与通道

`Gateway` 是 Octop 的全局 AI 交互入口，负责接收来自 Dashboard（WebSocket）、CLI REPL 和各种 IM 平台的消息，路由到对应的 Agent 执行，并将响应推送回来源通道。

## Gateway 架构

```
                    ┌──────────────────────┐
  Dashboard WS ────►│  WebSocketChannel    │
                    │  (WS_CHANNEL_ID)     │
  CLI REPL ────────►│  CliChannel          │
                    │  (CLI_CHANNEL_ID)    │
  飞书 / 钉钉 ─────►│  IM Channel (harness-│
  QQ / Discord ───►│  gateway 提供)        │
  企微 / 其他 ─────►│                      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   ChannelManager      │ (harness-gateway)
                    │   - pre_lock_handler  │
                    │   - session 串行化     │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   GlobalProcessor     │
                    │   - agent_manager     │
                    │   - thread_registry   │
                    │   - slash_dispatcher  │
                    │   - 9 个 repos        │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   AgentManager        │
                    │   → HarnessAgent      │
                    └──────────────────────┘
```

## 核心组件

### Gateway

Gateway 持有以下组件（F-075）：

| 组件 | 类型 | 职责 |
|------|------|------|
| `_channel_manager` | `ChannelManager` | harness-gateway 通道管理器 |
| `_processor` | `GlobalProcessor` | 消息处理核心 |
| `_thread_registry` | `ThreadRegistry` | 会话/线程元数据 |
| `_dispatcher` | `SlashDispatcher` | Slash 命令分发 |
| `_ws_hub` | `WebSocketHub` | Dashboard WS 连接池 |
| `_cli_hub` | `CliHub` | CLI REPL 连接池 |
| `_runtime_status` | `dict[str, ChannelRuntimeStatus]` | 通道连接状态 |

### GlobalProcessor

`GlobalProcessor` 在 `boot()` 中构造，接收以下依赖（F-079）：
- `agent_manager`：调用 Agent 执行
- `thread_registry`：会话/线程管理
- 9 个 repos：audit、agent、user、connector、knowledge、settings、provider、usage
- `dispatcher`：Slash 命令处理
- `gateway`：回推引用

GlobalProcessor 按 `InboundMessage.tenant_id`（== Agent ULID）路由消息到对应 Agent。

### ChannelRuntimeStatus

```python
@dataclass(frozen=True)
class ChannelRuntimeStatus:
    connected: bool
    reason: str | None = None    # disabled / unregistered / error
    detail: str | None = None
    updated_at: int = 0
```

`reason` 是 locale-neutral 代码，序列化时通过 `channel_runtime_reason()` 本地化（F-076）。

## 内置通道

Gateway 始终注册两个内置通道（F-079）：

### WebSocketChannel

- 通道 ID：`WS_CHANNEL_ID`
- 连接 Hub：`WebSocketHub`
- 用途：Dashboard 实时聊天
- 所有浏览器 WebSocket 连接通过此通道收发消息

### CliChannel

- 通道 ID：`CLI_CHANNEL_ID`
- 连接 Hub：`CliHub`
- 用途：`octop chats repl` 交互式聊天
- 终端中的 REPL 会话通过此通道收发消息

这两个通道在 `reload_channels_from_db()` 时不会被移除（F-081）。

## IM 通道

外部 IM 通道（飞书、钉钉、QQ、Discord、企微等）由 `harness-gateway` 包提供实现。Octop 只负责：

1. 从 DB 加载通道配置（`channel_repo.list_all`）
2. 通过 `ChannelManager.add_channel(kind, config, tenant_id=agent_id, ...)` 注册
3. 为每个通道设置 media backend
4. 跟踪运行时状态

### 通道注册流程

`_register_channel(row)`（F-087）：

```
1. 解析 config_json → dict
2. normalize_channel_response_mode(config.get("response_mode"))
3. processor_for_response_mode(processor, response_mode)
4. channel_manager.add_channel(
       kind=row.kind,
       config=parsed_config,
       tenant_id=row.agent_id,     # 路由到对应 Agent
       channel_id=row.channel_id,
       processor=selected_processor,
   )
5. media_backend_for_agent(agent_manager, row.agent_id)
   → registered.set_media_backend(backend)
6. _runtime_status[channel_id] = connected
```

### 通道 CRUD

- `create_channel(spec)`：同名同 kind 存在则更新，否则创建并注册（F-082）
- `update_channel(...)`：更新 DB → unregister → 重新 register
- `delete_channel(channel_id)`：删除 DB → unregister → 清除 status
- `probe_channel(channel_id)` / `probe_config(...)`：启动临时通道实例验证凭证（F-085）

### 备份恢复后重建

`reload_channels_from_db()` 在备份恢复后调用（F-081）：
1. 移除所有非内置 IM 通道
2. 从 DB 重新加载并注册
3. `refresh_media_backends()`
4. 无需进程重启

## 消息投递

### Cron 任务投递

`push_text_from_session()` 是定时任务向通道推送消息的入口（F-083）：

```
task_type="text":
  → 直接推送文本

task_type="agent"（默认）:
  1. 合并 MCP servers（显式选择或 default_open）
  2. prepare_chat_mcp() 加载工具
  3. build_harness_request() 构造请求
  4. agent_manager.stream() 流式运行 LLM
  5. 收集 token/delta → outbound 文本
  → virtual stream (dashboard/CLI):
      通过 WS/CLI hub 推送
  → IM channel:
      通过 channel_manager.push_text() 推送
```

### 主动推送

`push_text(channel_type, channel_id, subject, text)` 通过 ChannelManager 向 IM 用户主动推送消息（F-084）。

## 抢占式 Slash 取消

`_preempt_cancel_on_stop` 是 ChannelManager 的 pre-lock handler（F-086），解决了一个关键的并发问题：

**问题**：同一 session 的 IM turn 由 ChannelManager 串行化（session lock）。当用户发送 `/stop` 或 `/cancel` 时，如果上一个 turn 正在运行，`/stop` 会等待 session 锁，无法中断正在执行的 turn。

**解决**：在 session 锁被获取**之前**（pre-lock）解析消息：
1. 检测是否为 `/stop` 或 `/cancel` slash 命令
2. 获取 `agent_id`（来自 `tenant_id`）和 `thread_id`
3. 直接调用 `agent_manager.cancel_stream(agent_id, thread_id)`
4. 信号到达 harness-agent，中断正在运行的流

这使得 `/stop` 能够抢占式地取消正在执行的 LLM 调用。

## ThreadRegistry

`ThreadRegistry` 管理会话和线程元数据：
- Session：一个通道上的对话会话（如某个飞书用户 + 某个 Agent）
- Thread：对话线程，对应 LangGraph checkpointer 中的 thread_id
- Dashboard/CLI 会话被标记为 "virtual stream"，消息通过 Hub 推送而非 IM channel

`_bump_dashboard_session()` 在收到新消息时更新 last_active、设置标题（如果为空）、递增未读计数（F-083）。

## Media Backend

`refresh_media_backends()` 在 Agent 启动完成后为所有通道设置 media backend（F-080）。这解决了启动顺序问题：Gateway.boot() 在 AgentManager.boot() 之前执行，此时 Agent 尚未启动，无法解析 media backend。因此在所有 Agent 启动后，Gateway 重新遍历通道并设置 backend。

## 控制面重绑定

`replace_repos(repos)` 在控制面 DB 热交换后重定向 ThreadRegistry 到新的 DB pool（F-088）。通道本身不需要重新注册，因为它们持有 Gateway/Processor 引用而非直接持有 repos。

## 相关概念

- [/concepts/02-agent-runtime.md](/concepts/02-agent-runtime.md)
- [/concepts/01-server-lifecycle.md](/concepts/01-server-lifecycle.md)
- [/concepts/04-db-di.md](/concepts/04-db-di.md)
