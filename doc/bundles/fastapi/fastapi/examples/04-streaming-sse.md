---
type: Example
title: 流式响应与 SSE
description: 演示 FastAPI 流式响应的三种模式：EventSourceResponse 自动 SSE 推送、AsyncIterator 返回类型触发的 JSONL 流、手动 StreamingResponse，以及 WebSocket 双向通信。
tags: [fastapi, example, streaming, sse, websocket]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: routing-source
    resource: /references/routing.md
    title: routing 模块源码信源
  - id: responses-source
    resource: /references/responses-encoders.md
    title: responses 与 sse 模块信源
---

# 流式响应与 SSE

本示例演示 FastAPI v0.141.1 的流式响应能力。FastAPI 能从异步生成器端点的返回类型注解自动检测流式模式（F-031）：当 `response_class=EventSourceResponse` 时启用 SSE 模式，当返回类型为 `AsyncIterator[T]` 时启用 JSONL 模式。SSE 内置 15 秒 keepalive 保活机制（F-126）和基于 anyio 内存流的背压控制（F-025）。示例同时包含手动 `StreamingResponse` 和 `WebSocket` 双向通信。

## 场景说明

构建一个实时监控系统，包含三个子场景：

1. **SSE 实时通知**：服务器每秒推送一条系统监控事件，支持事件类型、ID 和注释
2. **JSONL 数据流**：批量数据导出，每条记录作为独立 JSON 行传输，客户端可边收边解析
3. **WebSocket 双向通信**：实时聊天室，客户端发送消息，服务器广播给所有连接者

## 完整代码

```python
import asyncio
import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import EventSourceResponse, StreamingResponse
from fastapi.routing import APIRouter
from fastapi.sse import ServerSentEvent, format_sse_event
from pydantic import BaseModel

router = APIRouter(tags=["streaming"])


class MetricEvent(BaseModel):
    timestamp: float
    cpu_percent: float
    memory_mb: float


class DataRecord(BaseModel):
    id: int
    name: str
    value: float


@router.get("/metrics/stream", response_class=EventSourceResponse)
async def stream_metrics() -> AsyncIterator[ServerSentEvent]:
    import time

    for i in range(10):
        await asyncio.sleep(1)
        metric = MetricEvent(
            timestamp=time.time(),
            cpu_percent=40.0 + i * 3.5,
            memory_mb=512.0 + i * 12.3,
        )
        yield ServerSentEvent(
            data=metric.model_dump(),
            event="metric",
            id=str(i),
        )


@router.get("/metrics/stream-simple", response_class=EventSourceResponse)
async def stream_metrics_simple():
    import time

    for i in range(5):
        await asyncio.sleep(0.5)
        yield {
            "timestamp": time.time(),
            "index": i,
            "message": f"heartbeat {i}",
        }


@router.get("/data/export")
async def export_data() -> AsyncIterator[DataRecord]:
    for i in range(100):
        await asyncio.sleep(0.05)
        yield DataRecord(
            id=i,
            name=f"record-{i}",
            value=i * 1.5,
        )


@router.get("/events/manual")
async def manual_sse():
    async def generate():
        for i in range(5):
            await asyncio.sleep(0.3)
            yield format_sse_event(
                data_str=json.dumps({"step": i, "status": "processing"}),
                event="progress",
                id=str(i),
            )
        yield format_sse_event(
            data_str=json.dumps({"status": "complete"}),
            event="complete",
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client has left the chat")


@router.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass


app = FastAPI(
    title="流式响应示例",
    version="1.0.0",
    description="SSE、JSONL、StreamingResponse 与 WebSocket 演示",
)
app.include_router(router)
```

## 代码解析

### SSE 自动检测与 EventSourceResponse

`stream_metrics` 端点的返回类型注解为 `AsyncIterator[ServerSentEvent]`，且路由使用默认响应类。FastAPI 在 `_populate_api_route_state` 中通过 `_is_async_gen_callable` 检测到异步生成器（F-031），并根据 `response_class` 类型判断流式模式。当 `response_class` 是 `EventSourceResponse` 子类时设置 `is_sse_stream=True`（F-023）。

在 `get_request_handler` 的 SSE 分支中（F-025），FastAPI 创建 `anyio.create_memory_object_stream[bytes](max_buffer_size=1)` 实现生产者-消费者背压——缓冲区满时生产者自动暂停，防止内存泄漏。任务组并行运行两个任务：`_producer` 从端点生成器拉取数据并经 `_serialize_sse_item` 序列化；`_keepalive_inserter` 在 `anyio.fail_after(_PING_INTERVAL)` 超时时发送 `KEEPALIVE_COMMENT`（F-126），默认间隔 15 秒，防止反向代理因空闲超时断开连接。

### ServerSentEvent 模型

`ServerSentEvent(BaseModel)` 定义五个字段（F-124）：`data`（任意 JSON 可序列化值）、`raw_data`（原始字符串，不进行 JSON 编码）、`event`（事件类型，单行校验）、`id`（事件 ID，单行且无 null 字符校验）、`retry`（重连间隔，非负整数）、`comment`（注释行，以 `:` 开头）。`data` 与 `raw_data` 互斥，由 `model_validator(mode="after")` 校验。

在路由层的 `_serialize_sse_item` 中，如果 item 是 `ServerSentEvent` 实例，直接读取其字段调用 `format_sse_event`；如果是普通 dict/模型，则通过 `_serialize_data` JSON 编码后包装在 `data:` 字段中（F-025）。

### format_sse_event 线格式

`format_sse_event(*, data_str, event, id, retry, comment)` 按 SSE 规范拼装线格式字节（F-125）：注释行以 `: ` 前缀，然后依次是 `event:`、`data:`、`id:`、`retry:` 行，末尾追加两个空行（`\n\n`）作为事件分隔符，最终以 UTF-8 编码返回 bytes。多行 data 会被拆分为多个 `data:` 行。

### 简化 SSE：yield 普通对象

`stream_metrics_simple` 端点不指定返回类型注解，直接 `yield` dict 对象。FastAPI 同样检测到生成器端点，普通对象经 `_serialize_data` 序列化为 JSON 字符串后包装为 `data:` 字段发送。这是最简单的 SSE 用法，适合不需要自定义 event/id 的场景。

### JSONL 流式

`export_data` 端点的返回类型为 `AsyncIterator[DataRecord]`。`get_stream_item_type` 检查注解的 origin 是否在 `_STREAM_ORIGINS` 中，提取第一个类型参数 `DataRecord`（F-066）。当 `response_class` 为默认的 `DefaultPlaceholder` 时设置 `is_json_stream=True`（F-031）。

在 JSONL 分支中（F-026），每个 item 经 `_serialize_data(item)` 序列化为 JSON bytes，追加 `b"\n"` 换行符。异步生成器在每个 item 后调用 `anyio.sleep(0)` 以支持取消。返回的 `StreamingResponse` media_type 为 `"application/jsonl"`。客户端可以逐行读取并解析，无需等待整个响应完成。

### 手动 StreamingResponse

`manual_sse` 端点直接返回 `StreamingResponse(generate(), media_type="text/event-stream")`。这种方式绕过 FastAPI 的自动 SSE 检测和 keepalive 机制，开发者完全控制生成逻辑。需要手动设置 `Cache-Control: no-cache` 和 `X-Accel-Buffering: no` 头以禁用代理缓冲。`format_sse_event` 可用于手动构造符合规范的 SSE 帧。

### WebSocket 双向通信

`@router.websocket("/ws/chat")` 装饰器注册 WebSocket 路由（F-017）。`APIWebSocketRoute` 在构造时构建 dependant 并设置 `self.app = websocket_session(get_websocket_app(...))`（F-029）。`websocket_session` 同样建立两层 AsyncExitStack（F-019）。

`WebSocket` 和 `WebSocketDisconnect` 从 starlette 再导出（F-121、F-150）。`await websocket.accept()` 接受连接，`receive_text()`/`send_text()` 进行文本通信。当客户端断开时，`receive_text()` 抛出 `WebSocketDisconnect`，应在 except 块中清理连接。`ConnectionManager` 类管理活动连接列表并实现广播模式。

## 运行方式

```bash
pip install fastapi uvicorn pydantic
uvicorn main:app --reload
```

### SSE 测试

```bash
curl -N http://127.0.0.1:8000/metrics/stream
```

`-N` 禁用 curl 缓冲，实时显示事件流。输出格式：

```text
event: metric
data: {"timestamp": ..., "cpu_percent": 40.0, "memory_mb": 512.0}
id: 0

```

### JSONL 测试

```bash
curl -N http://127.0.0.1:8000/data/export
```

每行一个 JSON 对象：

```text
{"id":0,"name":"record-0","value":0.0}
{"id":1,"name":"record-1","value":1.5}
```

### WebSocket 测试

使用 wscat 或浏览器控制台：

```bash
pip install wscat
wscat -c ws://127.0.0.1:8000/ws/chat
```

## 源码溯源

| API/概念 | 源码位置 | 事实编号 |
|---------|---------|---------|
| `EventSourceResponse` | `sse.py:20-33` | F-123 |
| `ServerSentEvent` 模型 | `sse.py:52-156` | F-124 |
| `format_sse_event` | `sse.py:165-233` | F-125 |
| `KEEPALIVE_COMMENT`/`_PING_INTERVAL` | `sse.py:237-241` | F-126 |
| SSE 流式分支 | `routing.py:520-646` | F-025 |
| JSONL 流式分支 | `routing.py:647-682` | F-026 |
| 生成器端点自动检测 | `routing.py:1071-1098` | F-031 |
| `is_sse_stream` 判断 | `routing.py:400` | F-023 |
| `get_stream_item_type` | `dependencies/utils.py:261-268` | F-066 |
| `StreamingResponse` 再导出 | `responses.py:5-12` | F-095 |
| `WebSocket`/`WebSocketDisconnect` | `websockets.py:1-3` | F-121 |
| `APIWebSocketRoute` | `routing.py:801-837` | F-029 |
| `websocket_session` 双栈 | `routing.py:165-186` | F-019 |
| `websocket` 装饰器 | `applications.py:1361-1439` | F-017 |

## 相关概念

- [流式响应与 WebSocket](/concepts/12-streaming-websocket.md)
- [路由系统与请求处理管线](/concepts/02-routing-system.md)
- [路径操作与端点执行](/concepts/03-path-operations.md)
- [响应模型与序列化](/concepts/07-response-model.md)
