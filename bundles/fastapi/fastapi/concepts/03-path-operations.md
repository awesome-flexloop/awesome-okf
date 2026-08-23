---
type: Concept
title: 路径操作与请求处理
description: 详解 get_request_handler 请求处理管线、请求体解析、SSE/JSONL 流式响应、同步异步端点执行模型与响应序列化机制。
tags: [fastapi, path-operation, request-handler, streaming, sse]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/routing.md
    title: FastAPI v0.141.1 源码信源
---

# 路径操作与请求处理

路径操作（Path Operation）是 FastAPI 中端点函数与 HTTP 路由的绑定单元。当请求到达匹配的 `APIRoute` 时，框架通过 `get_request_handler` 工厂构建的内部协程处理完整请求生命周期：请求体解析、依赖求解、端点执行、响应序列化与流式分支。本章基于 `routing.py` 中的 F-018 至 F-028 事实，详解这一管线的内部机制。

## request_response 与双层栈

`request_response(func)` 是 Starlette 同名函数的修改副本（F-018），它将端点函数包装为 ASGI 可调用对象。核心区别在于建立两层 `AsyncExitStack`：

- `scope["fastapi_inner_astack"]`：request 级栈，在整个请求生命周期（含响应发送）保持开启
- `scope["fastapi_function_astack"]`：function 级栈，在端点函数返回后立即关闭

若内部 app 产生的 response 未被 await（如端点忘记返回 Response 对象），抛出 `FastAPIError`。`websocket_session(func)` 同样设置两层栈（F-019），并包裹 `wrap_app_handling_exceptions` 以统一处理 WebSocket 异常。

## get_request_handler 工厂

`get_request_handler` 是请求处理的核心工厂函数（F-022），接收以下关键参数：

- `dependant`：预构建的依赖树
- `body_field`：请求体的 `ModelField`
- `status_code`：默认响应状态码
- `response_class`：响应类
- `response_field`：响应模型字段
- `response_model_include/exclude/by_alias/exclude_unset/exclude_defaults/exclude_none`：序列化控制
- `dependency_overrides_provider`：依赖覆盖提供者（通常是 app 实例）
- `embed_body_fields`：是否嵌入请求体字段
- `strict_content_type`：严格 Content-Type 模式
- `stream_item_field`：流式 item 字段
- `is_json_stream`：是否为 JSONL 流式

返回一个 `async def app(request)` 协程。内部首先通过 `lenient_issubclass(actual_response_class, EventSourceResponse)` 判断 `is_sse_stream`（F-023）。

## 请求体解析

请求体解析逻辑位于处理协程的起始阶段（F-024），按内容类型分支：

**表单请求**（`is_body_form` 为真）：调用 `await request.form()` 解析表单数据，并注册 `body.close` 回调确保资源释放。

**非表单请求**：读取 `body_bytes = await request.body()`，然后按 Content-Type 判断是否解析为 JSON：
- Content-Type 主类型为 `application`，子类型为 `json` 或以 `+json` 结尾（如 `application/vnd.api+json`）时，调用 `json.loads(body_bytes)` 解析
- 其他情况保留原始字节

**strict_content_type 防护**：当 `strict_content_type=True` 时，若请求缺少 Content-Type 头，则不解析 JSON 请求体。这是 CSRF 防护措施——某些浏览器在跨域表单提交时不发送 Content-Type，不解析 JSON 可防止恶意站点利用简单请求触发状态变更。

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

app = FastAPI(strict_content_type=True)

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## 依赖求解与端点执行

请求体解析完成后，调用 `solve_dependencies(...)` 递归求解依赖树（F-064），获得端点参数值与校验错误。若 errors 非空，抛出 `RequestValidationError`。

`run_endpoint_function` 负责实际调用端点（F-021）：

```python
async def run_endpoint_function(*, dependant, values, is_coroutine):
    assert dependant.call is not None
    if is_coroutine:
        return await dependant.call(**values)
    else:
        return await run_in_threadpool(dependant.call, **values)
```

协程端点（`async def`）直接 await 执行；同步端点（`def`）通过 `run_in_threadpool` 在线程池中运行，避免阻塞事件循环。`is_coroutine` 由 `is_async_callable` 判定。

## SSE 流式分支

当 `is_sse_stream` 为真时进入 Server-Sent Events 流式分支（F-025）。处理流程：

1. 调用 `dependant.call(**values)` 得到异步生成器
2. 通过 `anyio.create_memory_object_stream[bytes](max_buffer_size=1)` 创建内存流——`max_buffer_size=1` 实现背压：消费者未取走消息时生产者自动暂停
3. 在 `anyio.create_task_group()` 中启动两个任务：
   - `_producer`：从生成器拉取 item，经 `_serialize_sse_item` 序列化后放入内存流
   - `_keepalive_inserter`：使用 `anyio.fail_after(_PING_INTERVAL)` 设置 15 秒超时，超时则发送 `KEEPALIVE_COMMENT = b": ping\n\n"` 防止反向代理断开空闲连接
4. 返回 `StreamingResponse`，`media_type="text/event-stream"`
5. 设置响应头 `Cache-Control: no-cache` 和 `X-Accel-Buffering: no`（禁用 Nginx 缓冲）

```python
from collections.abc import AsyncIterator
from fastapi import FastAPI
from fastapi.responses import EventSourceResponse

app = FastAPI()

@app.get("/events")
async def events() -> AsyncIterator[dict]:
    for i in range(10):
        yield {"data": f"message {i}"}
```

当端点是异步生成器且 `response_class` 为 `EventSourceResponse` 子类时，框架自动检测并进入 SSE 分支（F-031）。开发者也可显式返回 `EventSourceResponse`。`ServerSentEvent` Pydantic 模型（F-124）提供 data/event/id/retry/comment 字段的校验，`format_sse_event` 函数（F-125）按 SSE 线格式拼装字节。

## JSONL 流式分支

当 `is_json_stream` 为真时进入 JSON Lines 流式分支（F-026）：

1. 每个 item 经 `_serialize_data(item)` 序列化为 JSON 字节
2. 追加 `b"\n"` 换行符
3. 异步生成器中调用 `await anyio.sleep(0)` 插入取消检查点，使流式响应能及时响应客户端断开
4. 返回 `StreamingResponse`，`media_type="application/jsonl"`

JSONL 模式在端点是生成器函数且 `response_class` 为 `DefaultPlaceholder`（即未显式指定响应类）时自动激活（F-031），返回类型注解如 `AsyncIterator[Item]` 经 `get_stream_item_type` 提取 item 类型（F-066）。

## 非流式响应分支

非流式路径执行以下步骤（F-027）：

1. 调用 `run_endpoint_function` 获取端点返回值
2. 若返回值已是 `Response` 实例，直接使用（注入 `background_tasks` 到 response）
3. 否则经 `serialize_response` 序列化：
   - 有 `response_field` 时调用 `field.validate` 校验（协程在线程池执行），errors 非空抛 `ResponseValidationError`
   - 按 `dump_json` 选择 `field.serialize_json`（返回 bytes）或 `field.serialize`（返回 Python 对象）
   - `dump_json` 快速路径直接构造 `Response(content=content, media_type="application/json")`
4. 通过 `is_body_allowed_for_status_code` 判断状态码是否允许响应体（F-115）：204、205、304 以及 1xx 状态码不允许 body，此时设置 `response.body = b""`

`is_body_allowed_for_status_code` 的判定规则（F-115）：`None`/`"default"`/`"1XX"`/`"2XX"`/`"3XX"`/`"4XX"`/`"5XX"` 返回 `True`；int 状态码 <200 或属于 {204, 205, 304} 返回 `False`；其余返回 `True`。

## serialize_response 序列化

`serialize_response` 函数（F-020）签名为：

```python
def serialize_response(
    *, field=None, response_content,
    include=None, exclude=None, by_alias=True,
    exclude_unset=False, exclude_defaults=False, exclude_none=False,
    is_coroutine=True, endpoint_ctx=None, dump_json=False
):
```

有 `field` 时：调用 `field.validate` 执行 Pydantic 校验，返回 `(value, errors)`。errors 非空时抛 `ResponseValidationError`。通过校验后按 `dump_json` 选择 `field.serialize_json()`（返回 bytes）或 `field.serialize()`（返回 dict）。

无 `field` 时：直接返回 `jsonable_encoder(response_content)`，按类型注册表处理 datetime、Decimal、Enum、UUID 等类型（F-110）。

## WebSocket 处理

`get_websocket_app` 构建 WebSocket 端点的处理协程（F-028）：调用 `solve_dependencies` 求解依赖，errors 非空时抛 `WebSocketRequestValidationError`，然后 `await dependant.call(**solved_result.values)` 执行 WebSocket 端点。与 HTTP 不同，WebSocket 端点不经过响应序列化阶段。

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        pass
```

## 处理管线总览

```text
请求进入
  │
  ▼
request_response 建立双层 AsyncExitStack
  │
  ▼
get_request_handler.app(request)
  │
  ├─ 请求体解析（form/body_bytes/JSON + strict_content_type 检查）
  │
  ├─ solve_dependencies（递归求解依赖树）
  │
  ├─ run_endpoint_function（async→await / sync→threadpool）
  │
  ├─ 流式判断
  │   ├─ SSE 分支 → anyio memory stream + producer/keepalive 任务组
  │   ├─ JSONL 分支 → _serialize_data + b"\n" + sleep(0)
  │   └─ 非流式分支 → serialize_response → Response
  │
  └─ 响应发送 → function_stack 关闭 → request_stack 关闭
```

## 相关概念

- [路由系统](02-routing-system.md)
- [依赖注入系统](04-dependency-injection.md)
- [请求体与数据验证](06-request-body.md)
- [FastAPI 应用类](01-application.md)
