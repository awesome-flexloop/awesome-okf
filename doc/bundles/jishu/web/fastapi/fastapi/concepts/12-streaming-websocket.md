---
type: Concept
title: 流式响应与 WebSocket
description: 详解 SSE 流式响应的 anyio 内存流背压与 keepalive 保活机制、JSONL 自动检测流式、ServerSentEvent 数据模型与线格式、生成器端点自动检测、WebSocket 路由与 APIWebSocketRoute 及 WebSocketDisconnect。
tags: [fastapi, streaming, sse, websocket, jsonl, event-source, anyio]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source-routing
    resource: /references/routing.md
    title: FastAPI v0.141.1 源码信源（routing）
  - id: fastapi-source-responses
    resource: /references/responses-encoders.md
    title: FastAPI v0.141.1 源码信源（responses-encoders）
---

# 流式响应与 WebSocket

FastAPI 支持三种流式响应模式：SSE（Server-Sent Events）、JSONL（JSON Lines）和原始生成器流式。框架通过检测端点是否为生成器函数及 `response_class` 类型自动选择流式模式，开发者无需手动构造 `StreamingResponse`。SSE 模式使用 anyio 内存对象流实现生产者-消费者背压，配合 15 秒超时的 keepalive 任务防止代理断开连接。WebSocket 路由则通过 `APIWebSocketRoute` 和双层 AsyncExitStack 提供与 HTTP 路由一致的依赖注入体验。

## 生成器端点自动检测

流式响应的触发在路由状态填充阶段由 `_populate_api_route_state` 自动检测（F-031）。检测逻辑基于两个条件：

1. **端点是否为生成器函数**：通过 `_is_async_gen_callable`（`async def` + `yield`）或 `_is_gen_callable`（普通 `def` + `yield`）判断，两者均经 `@lru_cache(maxsize=4096)` 缓存（F-055）
2. **response_class 类型**：
   - `response_class` 是 `EventSourceResponse` 子类 → `is_sse_stream=True`
   - `response_class` 是 `DefaultPlaceholder`（即未指定，使用默认值）→ `is_json_stream=True`

```python
from collections.abc import AsyncIterator
from fastapi import FastAPI
from fastapi.responses import EventSourceResponse
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

app = FastAPI()

@app.get("/items/stream")
async def stream_items() -> AsyncIterator[Item]:
    for i in range(10):
        yield Item(name=f"Item {i}", price=i * 1.5)
```

上述代码中，端点是异步生成器且未指定 `response_class`（使用默认 `DefaultPlaceholder`），框架自动设置 `is_json_stream=True`，返回 JSONL 流。若指定 `response_class=EventSourceResponse`，则切换为 SSE 模式。

返回注解中的流式 item 类型通过 `get_stream_item_type` 提取（F-066）：检查 `get_origin(annotation)` 是否在 `_STREAM_ORIGINS` 中（`typing.AsyncIterator`/`typing.Iterator`/`collections.abc.AsyncIterator`/`collections.abc.Iterator` 等），是则返回第一个类型参数，无参数返回 `Any`，否则返回 `None`。提取的类型存入 `stream_item_type`，并创建 `stream_item_field`（`ModelField`）用于每个 item 的校验和序列化。

## SSE 流式响应

SSE（Server-Sent Events）是基于 HTTP 的单向服务器推送协议。FastAPI 的 SSE 实现位于 `routing.py` 的流式分支和 `sse.py` 模块中。

### EventSourceResponse

`EventSourceResponse` 继承自 `StreamingResponse`（F-123），类属性固定 `media_type = "text/event-stream"`。它从 `fastapi.sse` 模块导出并在 `responses.py` 中重新导出（F-095）。

### ServerSentEvent 数据模型

`ServerSentEvent` 是 Pydantic BaseModel，定义 SSE 事件的结构（F-124）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | `Any = None` | 事件数据 |
| `raw_data` | `str \| None = None` | 原始数据字符串（与 data 互斥） |
| `event` | `str \| None = None` | 事件类型（AfterValidator 校验单行） |
| `id` | `str \| None = None` | 事件 ID（AfterValidator 校验单行且无 null 字符） |
| `retry` | `int \| None = None` | 重连等待时间（Field(ge=0)） |
| `comment` | `str \| None = None` | 注释行（用于 keepalive） |

`model_validator(mode="after")` 校验 `data` 与 `raw_data` 互斥——不能同时设置两者。`_SSE_EVENT_SCHEMA` 字典定义了该模型的 JSON Schema（F-122），包含 type=object 和 properties 定义。

### format_sse_event 线格式

`format_sse_event` 将事件字段拼装为 SSE 线协议格式（F-125）：

```python
def format_sse_event(
    *,
    data_str: str | None = None,
    event: str | None = None,
    id: str | None = None,
    retry: int | None = None,
    comment: str | None = None,
) -> bytes:
```

拼装规则：
- `comment` 以 `: ` 前缀输出（如 `: keepalive`）
- `event` 输出为 `event: <value>`
- `data` 输出为 `data: <value>`
- `id` 输出为 `id: <value>`
- `retry` 输出为 `retry: <value>`
- 末尾追加两个空行（`\n\n`）分隔事件
- 以 `\n` 连接各行，UTF-8 编码为 bytes

### anyio 内存流与背压

SSE 流式分支的核心是 anyio 内存对象流和任务组协作（F-025）：

1. 调用端点函数得到异步生成器
2. 创建 `anyio.create_memory_object_stream[bytes](max_buffer_size=1)`——缓冲区大小为 1
3. 在 `anyio.create_task_group()` 中启动两个并发任务：

**`_producer` 任务**：
- 从端点生成器拉取下一个 item
- 调用 `_serialize_sse_item` 将 item 序列化为 SSE 格式 bytes
- 通过 `send_stream.send(item_bytes)` 发送到内存流
- 生成器耗尽时关闭发送流

**`_keepalive_inserter` 任务**：
- 使用 `anyio.fail_after(_PING_INTERVAL)` 设置 15 秒超时
- 若生产者在超时内未发送新事件，发送 `KEEPALIVE_COMMENT`
- 循环直到生产者完成

`max_buffer_size=1` 实现了背压（backpressure）：如果消费者（HTTP 响应发送）速度慢于生产者，内存流满时生产者自动暂停，避免无界队列导致内存泄漏。

### Keepalive 机制

两个模块级常量定义 keepalive 行为（F-126）：

```python
KEEPALIVE_COMMENT = b": ping\n\n"
_PING_INTERVAL: float = 15.0
```

每 15 秒无数据时发送 `: ping\n\n` 注释帧。SSE 注释帧（以 `:` 开头）被浏览器 EventSource API 忽略，但能防止反向代理（nginx、AWS ALB 等）因空闲超时而关闭连接。这是生产环境长连接的关键防护。

### 响应头设置

SSE 响应设置以下头部（F-025）：
- `Cache-Control: no-cache`：禁止缓存，确保实时性
- `X-Accel-Buffering: no`：禁用 nginx 缓冲，确保事件立即发送到客户端
- `Content-Type: text/event-stream`：由 `EventSourceResponse.media_type` 设置

## JSONL 流式响应

JSONL（JSON Lines）模式在 `is_json_stream=True` 时触发（F-026）。每个生成器 item 经 `_serialize_data(item)` 序列化为 JSON bytes，追加 `b"\n"` 换行符：

```python
async def jsonl_stream():
    async for item in generator:
        yield _serialize_data(item) + b"\n"
```

关键实现细节：
- `media_type="application/jsonl"`
- 异步生成器在每个 item 后调用 `anyio.sleep(0)`，主动让出控制权以支持取消检查
- `stream_item_field` 用于每个 item 的校验和序列化（通过 Pydantic TypeAdapter）
- 同步生成器通过 `iterate_in_threadpool` 包装为异步迭代

```python
from collections.abc import AsyncIterator
from pydantic import BaseModel

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str

@app.get("/logs/stream")
async def stream_logs() -> AsyncIterator[LogEntry]:
    for log in get_logs():
        yield log
```

客户端接收格式为每行一个 JSON 对象：

```
{"timestamp":"2026-08-23T10:00:00","level":"INFO","message":"Started"}
{"timestamp":"2026-08-23T10:00:01","level":"ERROR","message":"Failed"}
```

## 原始生成器流式

当端点返回普通 `StreamingResponse` 实例或生成器被直接传递时，进入非流式分支的 generator 路径（F-027 中 generator 分支）。这是 Starlette 原生的流式响应，FastAPI 不做额外处理：

```python
from fastapi.responses import StreamingResponse

@app.get("/raw-stream")
async def raw_stream():
    async def generate():
        for i in range(10):
            yield f"chunk {i}\n".encode()
    return StreamingResponse(generate(), media_type="text/plain")
```

此模式不做 item 级校验，适用于二进制流、分块文件传输等不需要 schema 验证的场景。

## WebSocket 路由

### websocket 装饰器与注册

FastAPI 提供两种 WebSocket 路由注册方式（F-017）：

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

app.add_api_websocket_route("/ws2", websocket_endpoint)
```

两种方式均委托给内部 router，支持 `dependencies` 参数注入路由级依赖。

### APIWebSocketRoute

`APIWebSocketRoute` 继承 Starlette 的 `routing.WebSocketRoute`（F-029）：

- 构造时调用 `_build_dependant_with_parameterless_dependencies` 构建依赖树
- 设置 `self.app = websocket_session(get_websocket_app(...))`
- `matches` 方法在 child_scope 中写入 `route=self`，使依赖求解能访问路由上下文

### websocket_session

`websocket_session` 包裹 WebSocket 端点，建立双层 AsyncExitStack（F-019）：
- `fastapi_inner_astack`（request 级栈）
- `fastapi_function_astack`（function 级栈）

与 HTTP 的 `request_response` 类似，双层栈支持 `yield` 依赖在 WebSocket 会话中的生命周期管理。外层包裹 `wrap_app_handling_exceptions` 处理 WebSocket 异常。

### get_websocket_app

`get_websocket_app` 是 WebSocket 端点的请求处理器工厂（F-028），执行流程：

1. 调用 `solve_dependencies` 求解全部依赖
2. 若 errors 非空，抛出 `WebSocketRequestValidationError`
3. 调用 `await dependant.call(**solved_result.values)` 执行端点函数

WebSocket 依赖注入支持与 HTTP 相同的参数类型（Path/Query/Header/Cookie/Depends），但不支持 Body（WebSocket 没有 HTTP 请求体语义）。

### WebSocket 与 WebSocketDisconnect

FastAPI 从 Starlette 重新导出三个 WebSocket 相关名称（F-121, F-150, F-151）：

- `WebSocket`：WebSocket 连接对象，提供 `accept()`、`receive_text()`/`receive_bytes()`/`receive_json()`、`send_text()`/`send_bytes()`/`send_json()`、`close()` 等方法
- `WebSocketDisconnect`：客户端断开连接时抛出的异常，含 `code` 属性
- `WebSocketState`：连接状态枚举（CONNECTING/CONNECTED/DISCONNECTED）

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

三行导入均带 `# noqa` 注释以抑制未使用导入警告（F-151）。

## SSE 与 JSONL 的选择

| 维度 | SSE | JSONL |
|------|-----|-------|
| 触发条件 | `response_class=EventSourceResponse` | 生成器端点 + 默认 response_class |
| Media-Type | `text/event-stream` | `application/jsonl` |
| 数据格式 | 结构化事件（event/data/id/retry/comment） | 每行一个 JSON 对象 |
| 浏览器支持 | 原生 EventSource API | 需手动解析 ReadableStream |
| Keepalive | 内置 15 秒 ping | 无 |
| 背压 | max_buffer_size=1 | 依赖 anyio 调度 |
| 适用场景 | 实时通知、事件推送 | 日志流、批量数据导出 |

## 相关概念

- [响应模型与序列化](07-response-model.md)
- [路由系统](02-routing-system.md)
- [路径操作与请求处理](03-path-operations.md)
- [依赖注入系统](04-dependency-injection.md)
- [异常处理与校验错误](11-exception-handling.md)
