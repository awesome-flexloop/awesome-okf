---
type: Concept
title: 整体架构
description: nanobot 围绕异步消息总线解耦通道与代理核心，nanobot.py 提供 SDK 门面，cli 层分层入口，网关模式支撑长运行服务。
tags: [nanobot, architecture, message-bus, gateway]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: nanobot 源码信源
---

# 整体架构

nanobot 的架构以"小核心、多入口"为原则。一个异步消息总线将聊天通道与代理核心解耦，多个入口点（CLI、TUI、WebUI、SDK、API）共享同一组运行时组件。

## 架构总览

```text
┌─────────────────────────────────────────────────┐
│                   入口层                          │
│  CLI (classic)  │  TUI (Bun)  │  WebUI (React)  │
│  Python SDK     │  OpenAI API │  Gateway        │
└───────┬──────────────┬──────────────┬───────────┘
        │              │              │
        │   process_direct()   WebSocket
        │              │              │
┌───────▼──────────────▼──────────────▼───────────┐
│              MessageBus (asyncio.Queue)          │
│         inbound ←──────→ outbound                │
└───────────────────────┬─────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────┐
│                  AgentCore                       │
│  ┌─────────────┐  ┌──────────┐  ┌────────────┐  │
│  │  AgentLoop  │→│ AgentRunner│→│ Providers  │  │
│  │  (session,  │  │ (LLM loop,│  │ (Anthropic,│  │
│  │   hooks,    │  │  tools)   │  │  OpenAI,   │  │
│  │   context)  │  │           │  │  Ollama…)  │  │
│  └─────────────┘  └──────────┘  └────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Tools   │ │ Memory   │ │ Session Manager  │ │
│  │ (fs,sh,  │ │ (Dream,  │ │ (compaction,     │ │
│  │  web,mcp)│ │  Git)    │ │  TTL, goals)     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────┘
```

## nanobot.py 主入口

`Nanobot` 类是编程式接口的门面，位于 `nanobot/nanobot.py`。它持有 `AgentLoop`、可选的 `Config` 和 `MCPProvider`，并暴露三个子客户端：

```python
class Nanobot:
    def __init__(
        self,
        loop: AgentLoop,
        *,
        config: Config | None = None,
        mcp_provider: MCPProvider | None = None,
    ) -> None:
        self._loop = loop
        self._config = config
        self._mcp_provider = mcp_provider
        self.sessions = SessionClient(loop)
        self.memory = MemoryClient(loop)
        self.runtime = RuntimeClient(loop)
```

来源：`nanobot/nanobot.py:76-88`

`from_config()` 类方法完成配置加载、工具注册表创建、MCP provider 初始化和 AgentLoop 构建：

```python
@classmethod
def from_config(cls, config_path=None, *, workspace=None, model=None, model_preset=None):
    config = resolve_config_env_vars(load_config(resolved), config_path=resolved)
    tools = ToolRegistry()
    mcp_provider = MCPProvider.from_config(config, tools)
    loop = AgentLoop.from_config(
        config,
        image_generation_provider_configs=image_gen_provider_configs(config),
        hook_factories=[create_file_edit_activity_hook],
        tool_registry=tools,
    )
    return cls(loop, config=config, mcp_provider=mcp_provider)
```

来源：`nanobot/nanobot.py:90-140`

## 消息总线

`MessageBus` 是通道与代理核心之间的解耦层，实现极为简洁——仅持有两个 `asyncio.Queue`：

```python
class MessageBus:
    def __init__(self):
        self.inbound: asyncio.Queue[InboundMessage] = asyncio.Queue()
        self.outbound: asyncio.Queue[OutboundMessage] = asyncio.Queue()

    async def publish_inbound(self, msg: InboundMessage) -> None:
        await self.inbound.put(msg)

    async def consume_outbound(self) -> OutboundMessage:
        return await self.outbound.get()
```

来源：`nanobot/bus/queue.py:8-34`

这种设计使得：
- 单发 CLI 模式可绕过 bus 直接调用 `process_direct()`
- 交互模式和网关模式通过 bus 收发，与外部通道行为一致
- 新增通道只需向 inbound 发布消息、从 outbound 消费响应

## CLI 入口分层

CLI 入口 `nanobot/cli/entry.py` 实现了两级启动策略：

1. **TUI 快速路径**：当参数为 `nanobot agent`（无 `--classic`、`-m` 等）时，仅加载 typer 和 agent 模块，跳过整个 classic 依赖图
2. **完整路径**：其他所有命令导入 `nanobot.cli.commands.app`（完整 Typer 应用）

```python
def main() -> None:
    _configure_windows_console()
    if _native_tui_candidate(sys.argv[1:]):
        import typer
        from nanobot.cli.agent import agent
        fast_app = typer.Typer(add_completion=False)
        fast_app.command()(agent)
        command = typer.main.get_command(fast_app)
        command.main(args=sys.argv[2:], prog_name="nanobot agent")
        return
    from nanobot.cli.commands import app
    app()
```

来源：`nanobot/cli/entry.py:35-51`

## 网关模式

`nanobot gateway` 是长运行进程，负责：
- 连接所有已启用的聊天通道
- 托管 WebSocket 通道（供 TUI/WebUI 连接）
- 运行 Dream 记忆整合和 heartbeat 定时任务
- 提供健康端点（默认 `127.0.0.1:18790`）
- 提供 WebUI 服务（默认端口 `8765`）

TUI 和 WebUI 启动器共享一个按需本地网关：任一命令可启动它，每个启动器仅释放自己的客户端，最后一个退出的交互式启动器停止它。使用 `nanobot gateway --background` 可将网关提升为持久后台模式。

来源：`README.md:181-204`、`docs/concepts.md:77-87`

## 关键子系统

| 子系统 | 位置 | 职责 |
|--------|------|------|
| Agent Loop | `nanobot/agent/loop.py`, `runner.py` | 会话键管理、钩子、上下文构建、多轮 LLM 对话 |
| Providers | `nanobot/providers/` | LLM 后端适配（Anthropic、OpenAI、Ollama、Bedrock 等） |
| Channels | `nanobot/channels/` | 平台集成，pkgutil 自动发现 |
| Tools | `nanobot/agent/tools/` | 文件、Shell、Web、MCP、cron、图像生成、子代理 |
| Memory | `nanobot/agent/memory.py` | Dream 两阶段记忆整合，原子写入 |
| Session | `nanobot/session/` | 会话历史、上下文压缩、TTL 自动压缩 |
| Config | `nanobot/config/` | Pydantic 配置，从 `~/.nanobot/config.json` 加载 |
| API Server | `nanobot/api/server.py` | OpenAI 兼容 HTTP API |

来源：`AGENTS.md:40-55`

## 相关概念

- [nanobot 简介](00-introduction.md)
- [Agent 运行时](02-agent-runtime.md)
- [消息总线](03-bus-messaging.md)
- [SDK 类型系统](04-sdk-types.md)
- [多接口架构](05-multi-interface.md)
