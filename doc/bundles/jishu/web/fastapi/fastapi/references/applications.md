---
type: Reference
title: applications — FastAPI 源码信源
description: FastAPI 应用类定义，涵盖构造参数分组、中间件栈构建顺序、OpenAPI 缓存机制、文档路由注册及路由委托方法
tags: [fastapi, source, applications]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/applications.md
    title: FastAPI v0.141.1 源码
---

# applications 源码信源

## 基本信息
- **源码路径**: `fastapi/applications.py`
- **版本**: 0.141.1
- **事实范围**: F-006 ~ F-017

## 公开 API 清单

### 类
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `FastAPI` | `Starlette` | `__init__`、`build_middleware_stack`、`openapi`、`setup`、`__call__`、`add_api_route`、`frontend`、`add_api_websocket_route`、`websocket` | F-006 |

### 函数
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| — | 本模块无模块级公开函数，所有功能通过 `FastAPI` 类方法暴露 | — |

### 类型别名
| 名称 | 定义 | 事实编号 |
|------|------|---------|
| `AppType` | `TypeVar("AppType", bound="FastAPI")` | F-006 |

## 关键实现细节

### FastAPI 类定义（F-006）
- `class FastAPI(Starlette)`，FastAPI 是 Starlette 的子类而非替代
- 定义 `AppType = TypeVar("AppType", bound="FastAPI")` 用于类方法类型注解

### __init__ 关键参数分组（F-007）
`__init__` 接收 40+ 关键字参数及 `**extra`，按功能分组：

- **元数据**: `title`、`summary`、`description`、`version`、`terms_of_service`、`contact`、`license_info`、`openapi_external_docs`
- **OpenAPI**: `openapi_url`、`openapi_tags`、`servers`、`openapi_prefix`、`root_path`、`root_path_in_servers`、`swagger_ui_init_oauth`、`swagger_ui_parameters`、`generate_unique_id_function`、`separate_input_output_schemas`、`strict_content_type`
- **路由**: `routes`、`redirect_slashes`、`responses`、`callbacks`、`webhooks`、`deprecated`、`include_in_schema`、`default_response_class`、`dependencies`
- **中间件**: `middleware`、`exception_handlers`
- **生命周期**: `on_startup`、`on_shutdown`、`lifespan`
- **文档 UI**: `docs_url`、`redoc_url`、`swagger_ui_oauth2_redirect_url`
- **调试**: `debug`

### OpenAPI 版本与缓存初始化（F-008）
- `self.openapi_version = "3.1.0"`
- `self.openapi_schema = None`（懒加载缓存）
- `self._openapi_routes_version = None`（路由版本追踪）

### 内部组件初始化（F-009）
- `self.webhooks = webhooks or routing.APIRouter()`
- `self.dependency_overrides = {}`（依赖替换字典，测试时使用）
- `self.router = routing.APIRouter(...)`（FastAPI 不直接持有路由列表，委托给内部 APIRouter）

### 默认异常处理器注册（F-010）
构造时注册三个默认异常处理器：
- `HTTPException` → `http_exception_handler`
- `RequestValidationError` → `request_validation_exception_handler`
- `WebSocketRequestValidationError` → `websocket_request_validation_exception_handler`

### build_middleware_stack 中间件顺序（F-011）
构建顺序（反向包裹，最内层最先执行）：
1. `ServerErrorMiddleware`（最外层，捕获未处理异常）
2. `self.user_middleware`（用户添加的中间件）
3. `ExceptionMiddleware`（异常处理中间件）
4. `AsyncExitStackMiddleware`（异步上下文栈中间件，支撑 yield 依赖生命周期）
5. `self.router`（最内层，路由处理）

### openapi() 缓存机制（F-012）
- 调用 `self.router._get_routes_version()` 获取当前路由版本号
- 当 `self.openapi_schema` 为空或版本不匹配时，调用 `get_openapi(...)` 重新生成
- 生成结果缓存到 `self.openapi_schema`
- 路由增删时 `_mark_routes_changed()` 递增版本号，触发缓存失效

### setup() 四个文档路由（F-013）
注册四个文档路由，均设置 `include_in_schema=False`：
1. `openapi_url` → 返回 OpenAPI JSON（`JSONResponse`）
2. `docs_url` → Swagger UI HTML（`swagger_ui_html`）
3. `swagger_ui_oauth2_redirect_url` → OAuth2 回调页面（`swagger_ui_redirect`）
4. `redoc_url` → ReDoc HTML（`redoc_html`）

### __call__ root_path 注入（F-014）
- 当 `self.root_path` 非空时设置 `scope["root_path"] = self.root_path`
- 然后 `await super().__call__` 委托给 Starlette

### add_api_route 路由委托（F-015）
`add_api_route(path, endpoint, *, response_model=Default(None), status_code, tags, dependencies, summary, description, response_description="Successful Response", responses, deprecated, methods, operation_id, response_model_include, response_model_exclude, response_model_by_alias=True, response_model_exclude_unset, response_model_exclude_defaults, response_model_exclude_none, include_in_schema=True, response_class=Default(JSONResponse), name, openapi_extra, generate_unique_id_function=Default(generate_unique_id))`
- 直接委托给 `self.router.add_api_route(...)`
- 使用 `Default(None)` / `Default(JSONResponse)` / `Default(generate_unique_id)` 作为占位符，区分"未传入"与"传入 None"

### frontend 静态前端路由（F-016）
`frontend(path, *, directory, fallback="auto", check_dir="auto")`
- 调用 `routing._resolve_frontend_check_dir(...)` 解析目录检查策略
- 委托给 `self.router.frontend(...)`

### WebSocket 路由方法（F-017）
- `add_api_websocket_route(path, endpoint, name=None, *, dependencies=None)`
- `websocket(path, name=None, *, dependencies=None)` 装饰器方法

## 相关信源
- [routing.md](routing.md) — APIRouter、APIRoute 及请求处理管线
- [openapi.md](openapi.md) — get_openapi 生成函数与文档 UI
- [middleware-exceptions.md](middleware-exceptions.md) — 异常处理器与中间件
