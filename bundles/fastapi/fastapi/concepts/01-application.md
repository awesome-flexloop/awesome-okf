---
type: Concept
title: FastAPI 应用类
description: 详解 FastAPI 类的构造参数分组、内部 router 委托、中间件栈顺序、OpenAPI 版本缓存、文档路由注册与路由方法委托机制。
tags: [fastapi, application, middleware, openapi, lifecycle]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/applications.md
    title: FastAPI v0.141.1 源码信源
---

# FastAPI 应用类

`FastAPI` 类是框架的核心入口，定义于 `fastapi/applications.py`，类签名为 `class FastAPI(Starlette)`（F-006）。它继承 Starlette 的全部 ASGI 能力，并在 `__init__` 中完成内部路由器创建、默认异常处理器注册、中间件栈构建与 OpenAPI 缓存初始化。FastAPI 本身不直接持有路由列表，而是将路由管理委托给内部 `APIRouter` 实例（F-009）。

## 类继承与类型变量

```python
from starlette.applications import Starlette

AppType = TypeVar("AppType", bound="FastAPI")

class FastAPI(Starlette):
    ...
```

`AppType` 类型变量（F-006）用于类方法的返回类型注解，使子类化 FastAPI 时方法返回类型能被正确推断。`FastAPI(Starlette)` 的继承关系意味着实例本身即是合法的 ASGI 可调用对象，`__call__` 方法直接处理 ASGI scope/receive/send 三元组。

## __init__ 参数分组

`FastAPI.__init__` 接收 40+ 关键字参数及 `**extra`（F-007），按功能可分为六组：

**元数据组**：`title`、`summary`、`description`、`version`、`terms_of_service`、`contact`、`license_info`、`openapi_external_docs`。这些字段最终进入 OpenAPI document 的 `info` 对象。

**OpenAPI 配置组**：`openapi_url`、`openapi_tags`、`servers`、`openapi_prefix`、`root_path`、`root_path_in_servers`、`swagger_ui_init_oauth`、`swagger_ui_parameters`、`generate_unique_id_function`、`separate_input_output_schemas`、`strict_content_type`。其中 `strict_content_type` 控制 CSRF 防护行为——为 `True` 时无 Content-Type 的请求不解析 JSON 请求体。

**路由组**：`routes`、`redirect_slashes`、`responses`、`callbacks`、`webhooks`、`deprecated`、`include_in_schema`、`default_response_class`、`dependencies`。`dependencies` 是应用级全局依赖列表，会应用到所有路由。

**中间件与异常组**：`middleware`、`exception_handlers`。`middleware` 接收 `Middleware` 实例列表，`exception_handlers` 是异常类到处理函数的映射。

**生命周期组**：`on_startup`、`on_shutdown`、`lifespan`。`lifespan` 是推荐的异步上下文管理器方式，`on_startup`/`on_shutdown` 为旧版生命周期事件。

**文档 UI 组**：`docs_url`、`redoc_url`、`swagger_ui_oauth2_redirect_url`。将任一设为 `None` 可禁用对应文档路由。

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    version="1.0.0",
    description="A sample API",
    docs_url="/docs",
    redoc_url="/redoc",
    strict_content_type=True,
)
```

## 内部组件初始化

`__init__` 中设置三个 OpenAPI 版本字段（F-008）：

```python
self.openapi_version = "3.1.0"
self.openapi_schema = None
self._openapi_routes_version = None
```

`openapi_schema` 初始为 `None`，首次访问 `openapi()` 时懒加载生成。`_openapi_routes_version` 记录上次生成 schema 时的路由版本号，用于增量缓存判断。

内部路由器与依赖替换字典的创建（F-009）：

```python
self.webhooks = webhooks or routing.APIRouter()
self.dependency_overrides = {}
self.router = routing.APIRouter(...)
```

`self.router` 是主路由器，所有 `add_api_route`、`get`、`post` 等方法均委托给它。`self.webhooks` 是独立的 webhook 路由器，与主路由对等。`self.dependency_overrides` 是字典，用于测试时替换依赖实现——键为原始依赖函数，值为替换函数。

## 默认异常处理器

构造时注册三个默认异常处理器（F-010）：

| 异常类 | 处理器函数 |
|--------|-----------|
| `HTTPException` | `http_exception_handler` |
| `RequestValidationError` | `request_validation_exception_handler` |
| `WebSocketRequestValidationError` | `websocket_request_validation_exception_handler` |

`RequestValidationError` 在请求参数校验失败时由依赖求解器抛出，处理器返回 422 响应并附带错误详情。用户可通过 `exception_handlers` 参数覆盖这些默认处理器。

## 中间件栈构建顺序

`build_middleware_stack` 方法构建中间件链，按反向包裹顺序（最内层最先执行）（F-011）：

1. **`ServerErrorMiddleware`**（最外层）：捕获未处理异常，返回 500 响应
2. **`self.user_middleware`**：用户通过 `middleware` 参数或 `add_middleware` 添加的中间件
3. **`ExceptionMiddleware`**：将路由处理中抛出的 `HTTPException` 等转换为响应
4. **`AsyncExitStackMiddleware`**：建立 ASGI 级异步上下文栈，支撑 `yield` 依赖的 request 级生命周期
5. **`self.router`**（最内层）：实际路由匹配与请求处理

```python
# 中间件栈结构示意（从外到内）
ServerErrorMiddleware(
    user_middleware(
        ExceptionMiddleware(
            AsyncExitStackMiddleware(
                router
            )
        )
    )
)
```

`AsyncExitStackMiddleware` 位于 `ExceptionMiddleware` 与 `router` 之间，这意味着 `yield` 依赖的清理逻辑在响应发送阶段执行，但异常处理中间件仍能捕获依赖设置阶段抛出的异常。

## OpenAPI 版本缓存机制

`openapi()` 方法实现基于路由版本号的增量缓存（F-012）：

```python
def openapi(self):
    routes_version = self.router._get_routes_version()
    if self.openapi_schema is not None and self._openapi_routes_version == routes_version:
        return self.openapi_schema
    self.openapi_schema = get_openapi(...)
    self._openapi_routes_version = routes_version
    return self.openapi_schema
```

每次添加/删除路由时，`APIRouter.add_api_route` 调用 `_mark_routes_changed()` 递增内部版本号（F-036）。仅当 `openapi_schema` 为空或版本号不匹配时才重新调用 `get_openapi` 生成完整 schema。修改已有路由的处理函数不改变路由对象本身，因此不会触发版本递增。

## setup() 文档路由注册

`setup()` 方法注册四个文档路由，均标记 `include_in_schema=False`（F-013）：

| 路由路径参数 | 响应类型 | 用途 |
|-------------|---------|------|
| `openapi_url` | `JSONResponse` | OpenAPI 3.1 JSON 文档 |
| `docs_url` | `swagger_ui_html` | Swagger UI 交互文档页 |
| `swagger_ui_oauth2_redirect_url` | `swagger_ui_redirect` | OAuth2 回调处理页 |
| `redoc_url` | `redoc_html` | ReDoc 文档页 |

Swagger UI 默认从 jsdelivr CDN 加载 swagger-ui-dist@5 资源（F-073），ReDoc 加载 redoc@2 standalone（F-074）。`_html_safe_json` 对 JSON 中 `<>&` 字符做 Unicode 转义以防 XSS（F-071）。

## __call__ 与 root_path

`__call__` 方法在 `self.root_path` 非空时设置 `scope["root_path"]`，再调用 `super().__call__`（F-014）：

```python
async def __call__(self, scope, receive, send):
    if self.root_path:
        scope["root_path"] = self.root_path
    await super().__call__(scope, receive, send)
```

`root_path` 用于反向代理场景，告知应用其挂载的前缀路径，影响 OpenAPI 中服务器 URL 的生成。

## 路由方法委托

FastAPI 将所有路由操作委托给 `self.router`（F-015、F-016、F-017）：

**`add_api_route`**（F-015）：接收 `path`、`endpoint` 及 `response_model`、`status_code`、`tags`、`dependencies`、`responses`、`deprecated`、`methods`、`operation_id`、`response_model_include/exclude`、`response_class`、`name`、`openapi_extra`、`generate_unique_id_function` 等参数，直接转调 `self.router.add_api_route(...)`。

**`frontend`**（F-016）：接收 `path`、`directory`、`fallback="auto"`、`check_dir="auto"`，先调用 `routing._resolve_frontend_check_dir` 解析目录检查策略，再委托 `self.router.frontend(...)`。前端路由被加入 `_low_priority_routes` 低优先级列表（F-037），确保 API 路由优先匹配。

**WebSocket 路由**（F-017）：提供 `add_api_websocket_route(path, endpoint, name=None, *, dependencies=None)` 方法和 `websocket(path, name=None, *, dependencies=None)` 装饰器，用于注册 WebSocket 端点。

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"echo: {data}")
```

`@app.get`、`@app.post`、`@app.put`、`@app.delete`、`@app.patch`、`@app.options`、`@app.head`、`@app.trace` 等装饰器均为 `add_api_route` 的语法糖，预设对应的 HTTP 方法。

## dependency_overrides 测试替换

`self.dependency_overrides = {}`（F-009）是运行时依赖替换字典。在测试中，可将原始依赖函数映射到替代实现：

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

async def get_db():
    yield "real-db"

app = FastAPI()

@app.get("/items")
async def read_items(db = Depends(get_db)):
    return {"db": db}

app.dependency_overrides[get_db] = lambda: "fake-db"
client = TestClient(app)
response = client.get("/items")
assert response.json() == {"db": "fake-db"}
```

`solve_dependencies` 在求解每个依赖前检查该字典，命中时使用替换函数构建子 `Dependant`（F-064）。替换发生在求解时的任意节点，无需重建路由树。

## 相关概念

- [FastAPI 简介](00-introduction.md)
- [路由系统](02-routing-system.md)
- [路径操作与请求处理](03-path-operations.md)
- [依赖注入系统](04-dependency-injection.md)
