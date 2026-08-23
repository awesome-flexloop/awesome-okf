---
type: Reference
title: routing — FastAPI 源码信源
description: 路由系统核心实现，涵盖双层 AsyncExitStack、请求处理管线、SSE/JSONL 流式响应、APIRoute/APIRouter 组合模式及 WebSocket 路由
tags: [fastapi, source, routing]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/routing.md
    title: FastAPI v0.141.1 源码
---

# routing 源码信源

## 基本信息
- **源码路径**: `fastapi/routing.py`
- **版本**: 0.141.1
- **事实范围**: F-018 ~ F-037

## 公开 API 清单

### 类
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `APIRoute` | `routing.Route` (Starlette) | `__init__`、`get_route_handler`、类级注解（response_model/dependant/body_field/is_sse_stream/is_json_stream 等） | F-032, F-033 |
| `APIWebSocketRoute` | `routing.WebSocketRoute` (Starlette) | 构造时构建 dependant，`matches` 写入 child_scope | F-029 |
| `APIRouter` | `routing.Router` (Starlette) | `__init__`、`add_api_route`、`frontend`、`include_router` | F-034, F-035, F-036, F-037 |
| `_DefaultLifespan` | — | 包装 lifespan，支持 asyncgen/generator | F-035 |

### 函数
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| `request_response` | `request_response(func)` → 内部 ASGI app，建立双层 AsyncExitStack | F-018 |
| `websocket_session` | `websocket_session(func)` → 内部 ASGI app，设置双层栈并包裹异常处理 | F-019 |
| `serialize_response` | `serialize_response(*, field, response_content, include, exclude, by_alias, exclude_unset, exclude_defaults, exclude_none, is_coroutine, endpoint_ctx, dump_json)` | F-020 |
| `run_endpoint_function` | `run_endpoint_function(*, dependant, values, is_coroutine)` | F-021 |
| `get_request_handler` | `get_request_handler(dependant, body_field, status_code, response_class, response_field, response_model_include, response_model_exclude, response_model_by_alias, response_model_exclude_unset, response_model_exclude_defaults, response_model_exclude_none, dependency_overrides_provider, embed_body_fields, strict_content_type, stream_item_field, is_json_stream)` → `app(request)` | F-022 |
| `get_websocket_app` | `get_websocket_app(dependant, dependency_overrides_provider=None, embed_body_fields=False)` | F-028 |
| `_populate_api_route_state` | `_populate_api_route_state(route, path, endpoint, *, response_model, status_code, tags, ...)` | F-030 |

## 关键实现细节

### request_response 双层 AsyncExitStack（F-018）
`request_response(func)` 是 Starlette 同名函数的修改副本，在内部 app 中建立两层 AsyncExitStack：
- `scope["fastapi_inner_astack"]`（request_stack）：request 级栈，生命周期跨越整个请求含后台任务
- `scope["fastapi_function_astack"]`（function_stack）：function 级栈，端点返回时即关闭
- response 未 await 时抛 `FastAPIError`

### websocket_session 双层栈（F-019）
- 同样设置 `fastapi_inner_astack` 和 `fastapi_function_astack`
- 包裹 `wrap_app_handling_exceptions`

### serialize_response 响应序列化（F-020）
`serialize_response(*, field=None, response_content, include=None, exclude=None, by_alias=True, exclude_unset=False, exclude_defaults=False, exclude_none=False, is_coroutine=True, endpoint_ctx=None, dump_json=False)`
- 有 field 时调用 `field.validate`（协程在线程池执行）
- errors 非空抛 `ResponseValidationError`
- 按 `dump_json` 选择 `field.serialize_json`（返回 bytes）或 `field.serialize`（返回 Python 对象）
- 无 field 时返回 `jsonable_encoder(response_content)`

### run_endpoint_function 端点执行（F-021）
- 断言 `dependant.call` 非空
- 协程端点直接 `await dependant.call(**values)`
- 同步端点 `await run_in_threadpool(dependant.call, **values)`

### get_request_handler 完整参数（F-022）
参数含：`dependant`/`body_field`/`status_code`/`response_class`/`response_field`/`response_model_include`/`response_model_exclude`/`response_model_by_alias`/`response_model_exclude_unset`/`response_model_exclude_defaults`/`response_model_exclude_none`/`dependency_overrides_provider`/`embed_body_fields`/`strict_content_type`/`stream_item_field`/`is_json_stream`，返回内部 `app(request)` 协程。

### SSE 流式检测（F-023）
通过 `lenient_issubclass(actual_response_class, EventSourceResponse)` 判断 `is_sse_stream`。

### 请求体解析逻辑（F-024）
- `is_body_form` 时 `await request.form()` 并注册 `body.close` 回调
- 非 form 时读取 `body_bytes`
- 按 content-type 主类型 `application` 且子类型 `json` 或 `+json` 才解析 JSON
- `strict_content_type=True` 时无 content-type 不解析 JSON

### SSE 流式实现（F-025）
- 调用 `dependant.call(**values)` 得到生成器
- 通过 `anyio.create_memory_object_stream[bytes](max_buffer_size=1)` 创建内存流（背压控制）
- 任务组中运行两个任务：
  - `_producer`：拉取生成器并 `_serialize_sse_item`
  - `_keepalive_inserter`：在 `anyio.fail_after(_PING_INTERVAL)` 超时时发送 `KEEPALIVE_COMMENT`
- 返回 `StreamingResponse`，media_type="text/event-stream"
- 设置 `Cache-Control: no-cache` 和 `X-Accel-Buffering: no`

### JSONL 流式实现（F-026）
- `is_json_stream` 为真时，每个 item 经 `_serialize_data(item) + b"\n"` 序列化
- 异步生成器调用 `anyio.sleep(0)` 以支持取消
- 返回 `StreamingResponse`，media_type="application/jsonl"

### 非流式分支（F-027）
- 调用 `run_endpoint_function`
- 返回 Response 实例直接使用（注入 background_tasks）
- 否则经 `serialize_response` 序列化
- `dump_json` 路径返回 `Response(content=content, media_type="application/json")`
- 状态码不允许 body 时设置 `response.body = b""`

### get_websocket_app（F-028）
- 求解依赖
- errors 非空抛 `WebSocketRequestValidationError`
- 然后 `await dependant.call(**solved_result.values)`

### APIWebSocketRoute（F-029）
- 构造时调用 `_build_dependant_with_parameterless_dependencies`
- 设置 `self.app = websocket_session(get_websocket_app(...))`
- `matches` 时在 child_scope 写入 `route=self`

### _populate_api_route_state（F-030）
接收 `response_model`/`status_code`/`tags`/`dependencies`/`summary`/`description`/`response_description`/`responses`/`deprecated`/`name`/`methods`/`operation_id`/`response_model_*`/`include_in_schema`/`response_class`/`dependency_overrides_provider`/`callbacks`/`openapi_extra`/`generate_unique_id_function`/`strict_content_type`/`stream_item_type`，设置 route 全部属性。
- `methods` 为 None 时默认 `["GET"]`
- `description` 从 `inspect.cleandoc(endpoint.__doc__)` 提取并按 `\f` 截断

### 生成器端点自动检测（F-031）
`_populate_api_route_state` 中：
- `_is_async_gen_callable` 或 `_is_gen_callable` 为真时：
  - `response_class` 是 `EventSourceResponse` 子类 → `is_sse_stream=True`
  - `response_class` 是 `DefaultPlaceholder` → `is_json_stream=True`
- 返回注解经 `get_stream_item_type` 提取流式 item 类型

### APIRoute 类（F-032, F-033）
- `class APIRoute(routing.Route)` 声明类级注解：stream_item_type/response_model/summary/response_description/deprecated/operation_id/response_model_*/include_in_schema/response_class/dependency_overrides_provider/callbacks/openapi_extra/generate_unique_id_function/strict_content_type/tags/responses/unique_id/status_code/response_field/stream_item_field/dependencies/description/response_fields/dependant/_embed_body_fields/body_field/is_sse_stream/is_json_stream
- `__init__` 调用 `_populate_api_route_state` 后设置 `self.app = request_response(self.get_route_handler())`
- `get_route_handler` 读取 `_effective_route_context_var` 并调用 `get_request_handler(...)`

### APIRouter 类（F-034, F-035）
`class APIRouter(routing.Router)`：

`__init__` 关键字参数含：prefix/tags/dependencies/default_response_class/responses/callbacks/routes/redirect_slashes/default/dependency_overrides_provider/route_class（默认 APIRoute）/on_startup/on_shutdown/lifespan/deprecated/include_in_schema/generate_unique_id_function/strict_content_type。

- lifespan 为 None 时使用 `_DefaultLifespan(self)`
- asyncgen 函数经 `asynccontextmanager` 包装
- 普通 generator 经 `_wrap_gen_lifespan_context` 包装
- 初始化 `self._routes_version=0`、`self._low_priority_routes=[]`、`self._frontend_routes=None`

### add_api_route 合并语义（F-036）
- 含 `route_class_override` 参数，使用 `route_class_override or self.route_class`
- 合并 self.responses/tags/dependencies/callbacks（列表拼接）
- `deprecated=deprecated or self.deprecated`（OR 语义）
- `include_in_schema=include_in_schema and self.include_in_schema`（AND 语义）
- 创建 route 后 append 到 self.routes 并调用 `_mark_routes_changed()`（递增版本号触发 OpenAPI 缓存失效）

### frontend 方法（F-037）
`frontend(path, *, directory, fallback="auto", check_dir="auto")`
- 调用 `_resolve_frontend_check_dir` 和 `_normalize_frontend_path`
- 首次调用时创建 `_FrontendRouteGroup` 并加入 `_low_priority_routes`
- 然后调用 `add_frontend_route(...)`

## 相关信源
- [applications.md](applications.md) — FastAPI 类委托给 APIRouter
- [dependencies.md](dependencies.md) — dependant 构建与依赖求解
- [responses-encoders.md](responses-encoders.md) — EventSourceResponse、jsonable_encoder、流式工具
