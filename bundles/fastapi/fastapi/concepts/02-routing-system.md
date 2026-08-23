---
type: Concept
title: 路由系统
description: 详解 APIRouter 组合模式、APIRoute 状态填充、include_router 合并语义、双层 AsyncExitStack 生命周期与前端低优先级路由机制。
tags: [fastapi, routing, apirouter, apiroute, asgi]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/routing.md
    title: FastAPI v0.141.1 源码信源
---

# 路由系统

FastAPI 的路由系统建立在 Starlette 路由之上，核心由 `APIRouter`、`APIRoute` 和 `APIWebSocketRoute` 三个类构成。`APIRouter` 继承 Starlette 的 `routing.Router`（F-034），通过 prefix/tags/dependencies 等组合参数实现模块化路由组织；`APIRoute` 继承 `routing.Route`（F-032），携带依赖树、响应模型、流式标记等全部路由状态。FastAPI 应用本身不直接持有路由列表，而是委托给内部 `self.router = APIRouter(...)`（F-009）。

## APIRouter 类

### __init__ 参数

`APIRouter.__init__` 接收以下关键字参数（F-034）：

- **组合前缀与标签**：`prefix`、`tags`、`dependencies`、`responses`、`callbacks`
- **默认行为**：`default_response_class`、`redirect_slashes`、`route_class`（默认 `APIRoute`）
- **路由集合**：`routes`
- **生命周期**：`on_startup`、`on_shutdown`、`lifespan`
- **Schema 控制**：`deprecated`、`include_in_schema`、`generate_unique_id_function`、`strict_content_type`
- **依赖覆盖**：`dependency_overrides_provider`

```python
from fastapi import APIRouter, Depends

async def verify_token():
    ...

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(verify_token)],
    responses={404: {"description": "Not found"}},
)
```

### 生命周期与版本初始化

`__init__` 中对 `lifespan` 做包装（F-035）：为 `None` 时使用 `_DefaultLifespan(self)`；async generator 函数经 `asynccontextmanager` 包装；普通 generator 经 `_wrap_gen_lifespan_context` 包装。同时初始化：

```python
self._routes_version = 0
self._low_priority_routes = []
self._frontend_routes = None
```

`_routes_version` 是路由版本号，每次增删路由时由 `_mark_routes_changed()` 递增，供 OpenAPI schema 增量缓存使用（F-012）。`_low_priority_routes` 存放前端静态资源路由，确保 API 路由优先匹配。

## APIRoute 类

`APIRoute` 继承 Starlette 的 `routing.Route`，在类级别声明了全部路由状态注解（F-032），包括 `response_model`、`summary`、`description`、`deprecated`、`operation_id`、`response_model_include/exclude/by_alias/exclude_unset/exclude_defaults/exclude_none`、`include_in_schema`、`response_class`、`dependency_overrides_provider`、`callbacks`、`openapi_extra`、`generate_unique_id_function`、`strict_content_type`、`tags`、`responses`、`unique_id`、`status_code`、`response_field`、`stream_item_field`、`dependencies`、`response_fields`、`dependant`、`_embed_body_fields`、`body_field`、`is_sse_stream`、`is_json_stream`。

`__init__` 调用 `_populate_api_route_state` 填充上述属性后，设置 `self.app = request_response(self.get_route_handler())`（F-033）。`get_route_handler` 读取 `_effective_route_context_var` 上下文变量并调用 `get_request_handler(...)` 构建请求处理协程。

## _populate_api_route_state 状态填充

`_populate_api_route_state` 函数接收路由实例和全部参数，设置路由的所有属性（F-030、F-031）：

**HTTP 方法默认值**：`methods` 为 `None` 时默认 `["GET"]`。

**描述提取**：`description` 从 `inspect.cleandoc(endpoint.__doc__)` 提取，并按 `\f`（换页符）截断——`\f` 之后的内容不进入 OpenAPI 文档，但保留在源码 docstring 中供本地阅读。

```python
@app.get("/items/")
async def list_items():
    """列出所有物品。

    \f
    这段文字不会出现在 OpenAPI 文档中，但会出现在源码和 help() 中。
    """
    return []
```

**生成器端点检测**（F-031）：通过 `_is_async_gen_callable` 或 `_is_gen_callable` 判断端点是否为生成器函数。若是，根据 `response_class` 类型分流：
- `response_class` 是 `EventSourceResponse` 子类 → `is_sse_stream=True`
- `response_class` 是 `DefaultPlaceholder` → `is_json_stream=True`

返回注解经 `get_stream_item_type` 提取流式 item 类型——该函数检查 `get_origin(annotation)` 是否在 `_STREAM_ORIGINS` 中，是则返回第一个类型参数（F-066）。

**response_model 推导**：若未显式指定 `response_model`，从端点函数的返回类型注解自动推导。随后创建 `response_field`（`ModelField` 实例）用于响应序列化。

## add_api_route 与合并语义

`APIRouter.add_api_route` 方法创建路由并加入路由表，关键在于配置合并的方向性（F-036）：

```python
def add_api_route(self, path, endpoint, *, ..., route_class_override=None, ...):
    route_class = route_class_override or self.route_class
    # 合并 responses/tags/dependencies/callbacks
    combined_responses = {**self.responses, **responses}
    combined_tags = [*self.tags, *(tags or [])]
    combined_dependencies = [*self.dependencies, *(dependencies or [])]
    # deprecated 用 OR
    deprecated = deprecated or self.deprecated
    # include_in_schema 用 AND
    include_in_schema = include_in_schema and self.include_in_schema
    route = route_class(...)
    self.routes.append(route)
    self._mark_routes_changed()
```

各字段的合并操作符不同（F-036）：

| 字段 | 合并操作 | 语义 |
|------|---------|------|
| `responses` | 字典合并（路由级覆盖 router 级同键） | 路由级优先 |
| `tags` | 列表拼接 | 累加 |
| `dependencies` | 列表拼接 | 累加（可能重复） |
| `callbacks` | 列表拼接 | 累加 |
| `deprecated` | 逻辑 OR | 父级标记废弃则全部废弃 |
| `include_in_schema` | 逻辑 AND | 父级隐藏则全部隐藏 |

`route_class_override` 参数允许在单次路由注册时使用自定义路由类（如 `WebSocketRoute`），覆盖 router 的默认 `self.route_class`。创建路由后调用 `_mark_routes_changed()` 递增版本号，触发 OpenAPI 缓存失效。

## include_router 机制

`include_router` 将另一个 `APIRouter` 的路由合并到当前 router。合并时处理：

- **prefix 拼接**：当前 router 的 prefix 与子 router 的 prefix 拼接
- **tags 合并**：列表拼接
- **dependencies 合并**：列表拼接
- **responses 合并**：字典合并
- **deprecated/include_in_schema**：按上述 OR/AND 语义传播

这使得父路由的配置能以不同语义"向下传染"到所有子路由。

## 路由装饰器

`APIRouter` 提供九个 HTTP 方法装饰器：`get`、`post`、`put`、`delete`、`patch`、`options`、`head`、`trace`，以及 `api_route`（允许自定义 methods 列表）。这些装饰器内部调用 `add_api_route` 并预设对应方法。

```python
@router.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@router.post("/items/", status_code=201)
async def create_item(item: Item):
    return item
```

路径参数名通过 `get_path_param_names(path)` 提取，该函数使用正则 `re.findall("{(.*?)}", path)` 返回参数名集合（F-116）。

## 前端低优先级路由

`frontend(path, *, directory, fallback="auto", check_dir="auto")` 方法（F-037）调用 `_resolve_frontend_check_dir` 和 `_normalize_frontend_path` 解析配置，首次调用时创建 `_FrontendRouteGroup` 并加入 `_low_priority_routes`，然后调用 `add_frontend_route(...)`。低优先级路由在匹配顺序上排在普通 API 路由之后，避免前端静态资源路径拦截 API 请求。

## 双层 AsyncExitStack

`request_response(func)` 是 Starlette 同名函数的修改副本（F-018），在内部 app 中建立两层 `AsyncExitStack`：

```python
def request_response(func):
    async def app(scope, receive, send):
        request_stack = AsyncExitStack()
        scope["fastapi_inner_astack"] = request_stack
        function_stack = AsyncExitStack()
        scope["fastapi_function_astack"] = function_stack
        try:
            await request_stack.__aenter__()
            await function_stack.__aenter__()
            # 执行端点与依赖
            response = await func(request)
            await response(scope, receive, send)
        finally:
            await function_stack.__aexit__(...)
            await request_stack.__aexit__(...)
```

- **`fastapi_inner_astack`（request 级栈）**：生命周期跨越整个请求，包含 `scope="request"` 的 `yield` 依赖，在响应完全发送后才关闭
- **`fastapi_function_astack`（function 级栈）**：在端点函数返回后即关闭，包含默认 `scope="function"` 的 `yield` 依赖

若 response 未被 await（如端点忘记返回 Response），抛出 `FastAPIError`。`websocket_session(func)` 同样设置两层栈（F-019），并包裹 `wrap_app_handling_exceptions`。

## APIWebSocketRoute

`APIWebSocketRoute` 继承 Starlette 的 `routing.WebSocketRoute`（F-029），构造时调用 `_build_dependant_with_parameterless_dependencies` 构建依赖树，并设置 `self.app = websocket_session(get_websocket_app(...))`。路由匹配时在 child_scope 中写入 `route=self`，供 WebSocket 处理流程访问路由元数据。

## 相关概念

- [FastAPI 应用类](01-application.md)
- [路径操作与请求处理](03-path-operations.md)
- [依赖注入系统](04-dependency-injection.md)
- [参数声明系统](05-parameter-declaration.md)
