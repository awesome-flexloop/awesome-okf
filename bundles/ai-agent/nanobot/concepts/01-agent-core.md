---
type: concept
title: Agent 核心：Nanobot 门面
description: Nanobot 门面类、run/stream/run_streamed 三种运行方式、Session/Memory/Runtime 三客户端与 RunResult 值对象
tags: [nanobot, sdk, agent, facade]
sources:
  - resource: "/references/agent-api.md"
    title: "Nanobot SDK 门面 API"
  - resource: "/references/bus-sdk-api.md"
    title: "MessageBus 与 SDK 类型 API"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# Agent 核心：Nanobot 门面

`Nanobot` 是 nanobot 高级 Python SDK 的程序化门面（F-008、F-010）。它把底层的 `AgentLoop` 封装成"从一个配置即可运行 agent"的单一入口：`Nanobot.from_config()` 之后即可调用 `run`/`run_streamed`/`stream`。

## 门面的组合结构

`Nanobot.__init__` 接收一个 `AgentLoop`，可选地接收 `Config` 与 `MCPProvider`，并在构造时组合三个轻量客户端（F-011）：

```python
self.sessions = SessionClient(loop)   # 会话管理
self.memory   = MemoryClient(loop)    # 长期记忆
self.runtime  = RuntimeClient(loop)   # 运行时控制
```

`from_config` 是真正的"重工作"触发点：它加载并解析配置、构造 `ToolRegistry`、`MCPProvider.from_config`、`AgentLoop.from_config`，最后返回 `Nanobot(loop, ...)`（F-012）。鉴于此，纯 `import nanobot` 本身成本很低——`__init__.py` 用 `_LAZY_EXPORTS` + `__getattr__` 延迟导入，首次访问 `Nanobot` 才真正加载 `.nanobot` 模块（F-040、F-041）。

## 三种运行方式

| 方法 | 返回 | 特点 |
|---|---|---|
| `run(message, ...)` | `RunResult` | 一次性运行，等待完成后取最终结果 |
| `run_streamed(message, ...)` | `RunStream` | 启动流式运行，返回一个可等待的句柄 |
| `stream(message, ...)` | `AsyncIterator[StreamEvent]` | `run_streamed` 的便捷迭代封装 |

三者的参数一致（F-013、F-014、F-015）：`session_key` 默认 `"sdk:default"`，`channel` 默认 `"cli"`，`chat_id` 默认 `"direct"`，`sender_id` 默认 `"user"`，另支持 `media`、`ephemeral`、`attributes`、`hooks`、`model`、`model_preset`。

`run` 内部先构造一个 `SDKCaptureHook` 捕获工具调用与用量，再通过 `build_process_direct_kwargs` 组装参数，最终调用 `self._loop.process_direct(message, **kwargs, hooks=per_run_hooks)`，并把响应转换为 `RunResult`（F-013）。

### 建立与延续会话

`session_key` 用于会话隔离——不同 key 拥有独立历史，复用同一 key 即可延续线程：

```python
await bot.run("My name is Alice.", session_key="user:alice")
result = await bot.run("What is my name?", session_key="user:alice")
print(result.content)
```

### 流式事件

`run_streamed` 内部创建 `asyncio.Queue(maxsize=256)`、`SDKStreamEmitter`、`SDKStreamingHook` 与 `SDKCaptureHook`，把 agent 生命周期钩子转为公共 `StreamEvent` 写入队列（F-014）。运行时依次可能产生 `run.started`、`text.delta`、`tool.started`、`run.completed` 等事件（F-026、F-027）。

```python
from nanobot import STREAM_EVENT_TEXT_DELTA

async for event in bot.stream("Write a migration plan"):
    if event.type == STREAM_EVENT_TEXT_DELTA:
        print(event.delta, end="", flush=True)
```

## RunResult 与资源管理

`RunResult` 是一个 `@dataclass(slots=True)`，字段为 `content/tools_used/messages/usage/stop_reason/error/metadata`（F-028），因此一次运行拿到的不只是文本：

```python
result = await bot.run("Review this repository")
print(result.content)      # 最终回答
print(result.tools_used)   # agent 用过的工具
print(result.usage)        # token 用量
print(result.stop_reason)  # 停止原因
```

`Nanobot` 实现了 `async __aenter__/__aexit__`（F-016），推荐用 `async with` 关闭工具连接与后台清理：

```python
async with Nanobot.from_config() as bot:
    result = await bot.run("Summarize this repo")
```

## 三个客户端

`bot.sessions` / `bot.memory` / `bot.runtime` 分别暴露会话、记忆、运行时能力（F-032~F-035）：

- `bot.sessions`：`ingest`（导入 transcript 不跑模型）、`get`、`list`、`export`（可信完整快照）、`restore`、`clear`、`delete`、`flush`。
- `bot.memory`：`read`/`write`（`memory/MEMORY.md`）、`append_history`/`read_history`（`memory/history.jsonl`）。
- `bot.runtime`：`model`/`workspace` property、`add_context_provider`、`on_session_turn_persisted`、`compact_session`、`compact_idle_session`。

`export` 与普通快照存在边界区分：普通操作返回"显示安全"快照（省略仅模型可见的运行时上下文），`export()` 是显式备份边界，会包含内部上下文以便 `restore()` 精确还原模型可见历史——不应直接把导出的快照暴露给聊天用户（F-033 相关语义）。

## 相关概念

- [Nanobot 项目概览](/concepts/00-overview.md)
- [消息总线系统](/concepts/02-bus-system.md)
- [CLI 与 SDK](/concepts/03-cli-sdk.md)
- [Nanobot SDK 门面 API](/references/agent-api.md)