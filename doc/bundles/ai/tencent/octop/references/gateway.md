---
type: Reference
title: "Gateway：全局 AI 交互入口与通道管理"
description: "Gateway 类的源码信源登记，涵盖 ChannelManager、GlobalProcessor、WebSocket/CLI Hub、IM 通道注册、Cron 投递、Slash 抢占取消、通道探测。"
tags: [octop, gateway, channel, im, websocket, cron]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-073~F-088
---

# Gateway：全局 AI 交互入口与通道管理

本信源登记 `src/octop/infra/gateway/gateway.py` 的全部可验证事实。

## 类定义与外部依赖

```python
from harness_gateway.channel import ChannelCredentialsError
from harness_gateway.channels import ChannelKind
from harness_gateway.manager import ChannelManager
from harness_gateway.models import ChannelSubject

class Gateway:
    def __init__(self, *, agent_manager: AgentManager, repos: RepoBundle) -> None: ...
```

Gateway 是全局 AI 交互入口，拥有 harness-gateway 的 `ChannelManager`，通过 `GlobalProcessor` 按 `InboundMessage.tenant_id`（== agent ULID）路由 IM 消息（F-073、F-074）。

## 持有组件

| 成员 | 类型 | 说明 |
|------|------|------|
| `_thread_registry` | `ThreadRegistry` | 会话/线程元数据 |
| `_channel_manager` | `ChannelManager \| None` | harness-gateway 通道管理器 |
| `_processor` | `GlobalProcessor \| None` | 全局消息处理器 |
| `_dispatcher` | `SlashDispatcher` | Slash 命令分发 |
| `_ws_hub` | `WebSocketHub` | Dashboard WebSocket 连接池 |
| `_cli_hub` | `CliHub` | CLI REPL 连接池 |
| `_ws_channel` | `WebSocketChannel \| None` | 内置 Dashboard 通道 |
| `_cli_channel` | `CliChannel \| None` | 内置 CLI 通道 |
| `_runtime_status` | `dict[str, ChannelRuntimeStatus]` | 通道运行时状态 |

来源：F-075。

## 数据结构

### ChannelRuntimeStatus

```python
@dataclass(frozen=True)
class ChannelRuntimeStatus:
    connected: bool
    reason: str | None = None      # disabled / unregistered / error
    detail: str | None = None
    updated_at: int = 0
```

`reason` 是 locale-neutral 代码，序列化时本地化（F-076）。

### SlashRuntimeMeta

```python
@dataclass(frozen=True)
class SlashRuntimeMeta:
    version: str
    started_at: int
```

由 OctopServer 在 `_boot_runtime` 中通过 `set_slash_meta` 注入（F-077）。

### ChannelCreateSpec

```python
@dataclass
class ChannelCreateSpec:
    channel_id: str
    agent_id: str
    user_id: int
    kind: ChannelKind | str
    name: str
    config: dict[str, Any] = field(default_factory=dict)
```

来源：F-078。

## boot() 启动流程

```
1. 构造 GlobalProcessor（传入 agent_manager, thread_registry, 9 个 repos, dispatcher, gateway）
2. ChannelManager(channels={})
3. set_pre_lock_handler(_preempt_cancel_on_stop)
4. await channel_manager.start()
5. 创建 WebSocketChannel(processor, hub=ws_hub, channel_id=WS_CHANNEL_ID)
6. 创建 CliChannel(processor, hub=cli_hub, channel_id=CLI_CHANNEL_ID)
7. 从 DB 加载所有 enabled channels → _safe_register_channel
```

来源：F-079。

## 内置通道

Gateway 始终注册两个内置通道：

| 通道 | ID 常量 | Hub | 用途 |
|------|---------|-----|------|
| `WebSocketChannel` | `WS_CHANNEL_ID` | `WebSocketHub` | Dashboard 实时聊天 |
| `CliChannel` | `CLI_CHANNEL_ID` | `CliHub` | CLI REPL (`octop chats repl`) |

这两个通道在 `reload_channels_from_db` 时不会被移除（F-081）。

## 通道 CRUD

### create_channel(spec)

- 若同名同 agent 已存在且 kind 相同 → 更新
- 若同名但 kind 不同 → 抛出 `CHANNEL_NAME_TAKEN`
- 否则创建 DB 行并注册到 ChannelManager
- enabled 时注册，否则标记 `reason="disabled"`

来源：F-082。

### update_channel / delete_channel

- update：更新 DB → unregister → 若 enabled 则重新 register
- delete：删除 DB → unregister → 清除 runtime status

来源：F-083。

## 消息投递

### push_text_from_session

Cron 任务投递入口（F-083）：

```
task_type="text" → 直接推送文本
task_type="agent"（默认）→
  1. 合并 MCP servers（显式选择或 default_open）
  2. prepare_chat_mcp 加载工具
  3. build_harness_request 构造请求
  4. agent_manager.stream 流式运行 LLM
  5. 收集 token/delta → outbound 文本
  → virtual_stream（dashboard/CLI）：通过 WS/CLI hub 推送
  → IM 通道：通过 channel_manager.push_text 推送
```

### push_text

```python
async def push_text(self, channel_type, channel_id, subject, text):
    await self._require_channel_manager().push_text(channel_id, subject, text)
```

主动推送文本到 IM 用户（F-084）。

## 抢占式取消

`_preempt_cancel_on_stop` 是 ChannelManager 的 pre-lock handler（F-086）：

- 解析消息文本中的 `/stop` 或 `/cancel` slash 命令
- 在 session 锁被获取**之前**调用 `agent_manager.cancel_stream(agent_id, thread_id)`
- 解决了同 session IM turn 串行化时 `/stop` 被阻塞无法中断正在运行的 turn 的问题

## 通道探测

- `probe_channel(channel_id)`：对已持久化通道启动临时实例验证凭证
- `probe_config(*, agent_id, kind, config)`：不持久化，直接探测给定配置

探测通过 `manager.probe_channel(kind, config, tenant_id, channel_id, processor=_probe_processor)` 完成，捕获 `ChannelCredentialsError` 并返回本地化错误（F-085）。

## 通道注册内部流程

`_register_channel(row)`（F-087）：

1. 解析 row.config_json
2. `normalize_channel_response_mode` 规范化响应模式
3. `processor_for_response_mode` 选择 processor
4. `manager.add_channel(kind, config, tenant_id=row.agent_id, channel_id, processor)`
5. 获取已注册 channel，设置 media backend
6. 更新 `_runtime_status[channel_id] = connected`

## 媒体后端

`refresh_media_backends()` 在 agents 启动完成后调用（Gateway 先于 agents boot），为所有已注册 channel 解析并设置 media backend（`media_backend_for_agent`），解决启动顺序间隙（F-080）。

## 备份恢复后重建

`reload_channels_from_db()`（F-081）：
1. 移除所有非内置 IM channels
2. 清除非内置 runtime status
3. 从 DB 重新加载 enabled channels
4. `refresh_media_backends()`
5. 无需进程重启

## 控制面重绑定

`replace_repos(repos)` 重定向 `_thread_registry` 到新的 DB pool（F-088）。

## 相关概念

- [/concepts/03-gateway-channels.md](../concepts/03-gateway-channels.md)
- [/concepts/01-server-lifecycle.md](../concepts/01-server-lifecycle.md)
- [/concepts/02-agent-runtime.md](../concepts/02-agent-runtime.md)
