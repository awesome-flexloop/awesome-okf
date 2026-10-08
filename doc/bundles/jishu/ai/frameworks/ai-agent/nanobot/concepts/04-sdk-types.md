---
type: Concept
title: SDK 类型系统
description: sdk/types.py 定义流式事件类型、RunResult、StreamEvent、SessionSnapshot 等公共值对象，使用 dataclass(slots=True) 和 TypeAlias 构建类型安全的 SDK 契约。
tags: [nanobot, sdk, types, dataclass, streaming]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: nanobot 源码信源
---

# SDK 类型系统

`nanobot/sdk/types.py` 是 nanobot Python SDK 的公共类型定义模块。它定义了流式事件类型、运行结果、会话快照等值对象，以及在 SDK 和运行时之间传递数据的标准化契约。所有类型使用 Python 3.11+ 的 `dataclass(slots=True)` 和 `TypeAlias` 构建。

## 流式事件类型

`StreamEventType` 是一个 `Literal` 类型联合，定义了 10 种稳定的 v1 事件类型：

```python
StreamEventType: TypeAlias = Literal[
    "run.started",
    "text.delta",
    "text.completed",
    "reasoning.delta",
    "reasoning.completed",
    "tool.started",
    "tool.completed",
    "tool.failed",
    "run.completed",
    "run.failed",
]
```

来源：`nanobot/sdk/types.py:11-22`

每种事件类型对应一个字符串常量：

```python
STREAM_EVENT_RUN_STARTED: StreamEventType = "run.started"
STREAM_EVENT_TEXT_DELTA: StreamEventType = "text.delta"
STREAM_EVENT_TEXT_COMPLETED: StreamEventType = "text.completed"
STREAM_EVENT_REASONING_DELTA: StreamEventType = "reasoning.delta"
STREAM_EVENT_REASONING_COMPLETED: StreamEventType = "reasoning.completed"
STREAM_EVENT_TOOL_STARTED: StreamEventType = "tool.started"
STREAM_EVENT_TOOL_COMPLETED: StreamEventType = "tool.completed"
STREAM_EVENT_TOOL_FAILED: StreamEventType = "tool.failed"
STREAM_EVENT_RUN_COMPLETED: StreamEventType = "run.completed"
STREAM_EVENT_RUN_FAILED: StreamEventType = "run.failed"
```

来源：`nanobot/sdk/types.py:24-33`

`STREAM_EVENT_TYPES` 元组按逻辑顺序包含所有事件值，可用于迭代或验证：

```python
STREAM_EVENT_TYPES: tuple[StreamEventType, ...] = (
    STREAM_EVENT_RUN_STARTED,
    STREAM_EVENT_TEXT_DELTA,
    STREAM_EVENT_TEXT_COMPLETED,
    STREAM_EVENT_REASONING_DELTA,
    STREAM_EVENT_REASONING_COMPLETED,
    STREAM_EVENT_TOOL_STARTED,
    STREAM_EVENT_TOOL_COMPLETED,
    STREAM_EVENT_TOOL_FAILED,
    STREAM_EVENT_RUN_COMPLETED,
    STREAM_EVENT_RUN_FAILED,
)
```

来源：`nanobot/sdk/types.py:35-46`

这些常量在 `nanobot/__init__.py` 中通过 `_LAZY_EXPORTS` 延迟导出，可直接从顶层包导入：

```python
from nanobot import STREAM_EVENT_TEXT_DELTA, STREAM_EVENT_RUN_COMPLETED
```

## RunResult

`RunResult` 表示单次代理运行的最终结果，使用 `@dataclass(slots=True)` 装饰：

```python
@dataclass(slots=True)
class RunResult:
    """Result of a single agent run."""
    content: str
    tools_used: list[str] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=dict)
    stop_reason: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

来源：`nanobot/sdk/types.py:49-59`

各字段含义：

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | `str` | 代理的最终文本响应 |
| `tools_used` | `list[str]` | 运行过程中使用的工具名称 |
| `messages` | `list[dict]` | 运行结束时的最终消息列表 |
| `usage` | `dict[str, int]` | Token 使用量（如 prompt_tokens、completion_tokens） |
| `stop_reason` | `str \| None` | 停止原因（如 `"completed"`、`"max_iterations"`） |
| `error` | `str \| None` | 代理运行时内部失败的错误文本 |
| `metadata` | `dict` | 出站元数据（如延迟） |

`RunResult` 由 `result_from_response()` 工厂函数从内部响应对象和捕获钩子构建：

```python
def result_from_response(response: Any, capture: Any) -> RunResult:
    content = (response.content if response else None) or ""
    metadata = dict(response.metadata) if response and response.metadata else {}
    return RunResult(
        content=content,
        tools_used=capture.tools_used,
        messages=capture.messages,
        usage=capture.usage,
        stop_reason=capture.stop_reason,
        error=capture.error,
        metadata=metadata,
    )
```

来源：`nanobot/sdk/types.py:163-174`

## StreamEvent

`StreamEvent` 是流式运行期间发射的类型化事件：

```python
@dataclass(slots=True)
class StreamEvent:
    """A typed event emitted by Nanobot.stream() and RunStream."""
    type: StreamEventType
    delta: str = ""
    content: str = ""
    result: RunResult | None = None
    name: str | None = None
    tool_call_id: str | None = None
    arguments: dict[str, Any] | None = None
    iteration: int | None = None
    resuming: bool | None = None
    usage: dict[str, int] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

来源：`nanobot/sdk/types.py:62-77`

事件字段按类型有不同的使用方式：

| 事件类型 | 关键字段 |
|----------|----------|
| `run.started` | `metadata`（包含 session_key、channel、model 等） |
| `text.delta` | `delta`（增量文本） |
| `text.completed` | `resuming` |
| `reasoning.delta` | `delta`（推理增量） |
| `tool.started` | `name`、`arguments`、`iteration`、`tool_call_id` |
| `tool.completed` | `name`、`tool_call_id` |
| `tool.failed` | `name`、`error` |
| `run.completed` | `content`、`result`（RunResult）、`usage` |
| `run.failed` | `error`、`metadata`（含 exception_type） |

SDK 流式使用示例：

```python
from nanobot import Nanobot, STREAM_EVENT_TEXT_DELTA, STREAM_EVENT_RUN_COMPLETED

async for event in bot.stream("Write a migration plan"):
    if event.type == STREAM_EVENT_TEXT_DELTA:
        print(event.delta, end="", flush=True)
    elif event.type == STREAM_EVENT_RUN_COMPLETED:
        final = event.result
        print(f"\nTools: {final.tools_used}")
```

来源：`docs/python-sdk.md:117-128`

## SessionSnapshot

`SessionSnapshot` 是会话的可序列化快照：

```python
@dataclass(slots=True)
class SessionSnapshot:
    key: str
    messages: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": deepcopy(self.metadata),
            "messages": deepcopy(self.messages),
        }
```

来源：`nanobot/sdk/types.py:80-98`

`to_dict()` 执行深拷贝，返回 JSON 安全的字典表示。

快照有两个构建函数：

- `snapshot_from_session()`：从内部会话对象构建，可通过 `include_runtime_context=True` 包含模型专用的运行时上下文
- `snapshot_from_payload()`：从字典 payload 构建（用于反序列化）

两个函数在 `include_runtime_context=False`（默认）时都会调用 `public_history_messages()` 过滤出展示安全的消息：

```python
def snapshot_from_session(session, *, include_runtime_context=False):
    messages = cast(list[dict[str, Any]], deepcopy(session.messages))
    if not include_runtime_context:
        messages = public_history_messages(messages)
    return SessionSnapshot(
        key=session.key,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        metadata=deepcopy(session.metadata),
        messages=messages,
    )
```

来源：`nanobot/sdk/types.py:124-138`

## SessionInfo

`SessionInfo` 是会话列表的紧凑元数据：

```python
@dataclass(slots=True)
class SessionInfo:
    key: str
    created_at: str | None = None
    updated_at: str | None = None
    title: str = ""
    preview: str = ""
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "title": self.title,
            "preview": self.preview,
            "path": self.path,
        }
```

来源：`nanobot/sdk/types.py:101-121`

## 延迟导出机制

`nanobot/__init__.py` 通过 `_LAZY_EXPORTS` 字典和 `__getattr__` 实现类型的延迟加载，避免在 `import nanobot` 时加载整个运行时：

```python
_LAZY_EXPORTS = {
    "Nanobot": ".nanobot",
    "RunStream": ".nanobot",
    "RunResult": ".nanobot",
    "StreamEvent": ".nanobot",
    "STREAM_EVENT_RUN_STARTED": ".nanobot",
    # ... 更多导出
}

def __getattr__(name: str) -> Any:
    module_path = _LAZY_EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module
    mod = import_module(module_path, __name__)
    val = getattr(mod, name)
    globals()[name] = val
    return val
```

来源：`nanobot/__init__.py:57-91`

类型导入目标均为 `.nanobot` 模块，该模块从 `nanobot.sdk.types` 重新导出所有类型。首次访问后，值被缓存到模块全局命名空间。

## 相关概念

- [Agent 运行时](02-agent-runtime.md)
- [消息总线](03-bus-messaging.md)
- [整体架构](01-architecture.md)
- [多接口架构](05-multi-interface.md)
