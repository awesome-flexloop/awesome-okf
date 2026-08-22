---
type: reference
title: Nanobot SDK 门面 API
description: Nanobot 门面类与 Session/Memory/Runtime 三个客户端的方法签名及其源码位置
tags: [nanobot, sdk, api, reference]
sources:
  - resource: "/references/bus-sdk-api.md"
    title: "MessageBus 与 SDK 类型 API"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# Nanobot SDK 门面 API

本页登记 `Nanobot` 高级 Python SDK 的公共 API 签名与源码位置，作为 concepts/ 与 examples/ 的信源。所有签名均直接摘录自 `nanobot/nanobot.py` 与 `nanobot/sdk/clients.py`。

## 顶层门面 Nanobot

源码：`nanobot/nanobot.py`

| 成员 | 签名 | 说明 |
|---|---|---|
| 类 | `class Nanobot`（L66） | 程序化运行 agent 的门面类 |
| 构造 | `Nanobot(loop: AgentLoop, *, config=None, mcp_provider=None)`（L76-88） | 保存 loop/config/mcp_provider，并组合三个客户端 |
| 组合 | `self.sessions` / `self.memory` / `self.runtime`（L86-88） | 依次为 `SessionClient` / `MemoryClient` / `RuntimeClient` |
| 类方法 | `from_config(config_path=None, *, workspace=None, model=None, model_preset=None) -> Nanobot`（L90-98） | 从 config 构建；内部构造 `ToolRegistry`、`MCPProvider.from_config`、`AgentLoop.from_config` |
| 方法 | `async run(message, *, session_key="sdk:default", channel="cli", chat_id="direct", sender_id="user", media=None, ephemeral=False, attributes=None, hooks=None, model=None, model_preset=None) -> RunResult`（L142-156） | 单次运行并返回 `RunResult` |
| 方法 | `async run_streamed(...) -> RunStream`（L203-217） | 启动流式运行，返回 `RunStream` 句柄 |
| 方法 | `async stream(...) -> AsyncIterator[StreamEvent]`（L308-322） | `run_streamed` 的便捷迭代封装 |
| 方法 | `async aclose()`（L345-351） | 释放 loop 与 mcp_provider 资源 |
| 上下文 | `async __aenter__` / `__aexit__`（L353-357） | 支持 `async with Nanobot.from_config() as bot` |

`run` 与 `run_streamed`/`stream` 内部都通过 `SDKCaptureHook` 捕获工具调用与用量，用 `build_process_direct_kwargs` 组装参数，再调用 `self._loop.process_direct`（L175-199、L261-282）。

## SessionClient

源码：`nanobot/sdk/clients.py`，通过 `bot.sessions` 暴露。

| 成员 | 签名 | 说明 |
|---|---|---|
| 常量 | `_RESERVED_MESSAGE_KEYS = {"role", "content", RUNTIME_CONTEXT_HISTORY_META}`（L26） | 摄入时保留的保留字段 |
| 常量 | `_VALID_ROLES = {"user", "assistant", "tool", "system"}`（L27） | 合法消息角色 |
| 方法 | `async ingest(session_key, messages, *, metadata=None, source=None, save=True) -> SessionSnapshot`（L32-65） | 导入既有 transcript，不运行模型 |
| 方法 | `get(session_key) -> SessionSnapshot | None`（L67-75） | 显示安全的快照，不创建磁盘会话 |
| 方法 | `list() -> list[SessionInfo]`（L77-89） | 列出持久化会话 |
| 方法 | `export(session_key) -> SessionSnapshot | None`（L91-99） | 可信完整快照（含运行时上下文） |
| 方法 | `async restore(snapshot, *, session_key=None, save=True) -> SessionSnapshot`（L101-136） | 将快照恢复到空会话 |
| 方法 | `clear(session_key) -> SessionSnapshot`（L138-144） | 清空并持久化一个会话 |
| 方法 | `delete(session_key) -> bool`（L146-148） | 删除磁盘与会话缓存 |
| 方法 | `flush() -> int`（L150-152） | 将缓存刷到持久化存储 |

## MemoryClient

源码：`nanobot/sdk/clients.py`，通过 `bot.memory` 暴露。

| 成员 | 签名 | 说明 |
|---|---|---|
| 方法 | `read() -> str`（L161-163） | 读 `memory/MEMORY.md` |
| 方法 | `write(text) -> None`（L165-167） | 覆盖 `memory/MEMORY.md` |
| 方法 | `append_history(text, *, session_key=None) -> int`（L169-171） | 追加 `memory/history.jsonl` 并返回游标 |
| 方法 | `read_history(*, session_key=None) -> list[dict]`（L173-178） | 读历史条目，可按 session 过滤 |

## RuntimeClient

源码：`nanobot/sdk/clients.py`，通过 `bot.runtime` 暴露。

| 成员 | 签名 | 说明 |
|---|---|---|
| property | `model -> str`（L187-190） | 当前运行模型名 |
| property | `workspace -> Path`（L192-195） | 当前运行工作区 |
| 方法 | `add_context_provider(provider) -> Callable[[], None]`（L197-202） | 注册每轮上下文 provider，返回取消回调 |
| 方法 | `on_session_turn_persisted(handler) -> Callable[[], None]`（L204-209） | 注册持久化轮次回调，返回取消回调 |
| 方法 | `async compact_session(session_key) -> SessionSnapshot`（L211-219） | 单会话 token 合并 |
| 方法 | `async compact_idle_session(session_key, *, max_suffix=8) -> str | None`（L221-229） | 空闲会话压缩并返回摘要 |

## 顶层懒加载导出

源码：`nanobot/__init__.py`

- `_LAZY_EXPORTS` 字典（L57-80）将 `Nanobot`/`RunStream`/`RunResult`/`SessionInfo`/`SessionSnapshot`/`STREAM_EVENT_*`/`StreamEvent`/`StreamEventType`/`SessionTurnPersisted` 映射到模块路径。
- `__getattr__(name)`（L83-91）首次访问时 `import_module` 并缓存到 `globals()`。
- `__version__ = _resolve_version()`（L54）、`__logo__ = "🐈"`（L55）。

## 相关概念

- [Agent 核心：Nanobot 门面](/concepts/01-agent-core.md)
- [MessageBus 与 SDK 类型 API](/references/bus-sdk-api.md)