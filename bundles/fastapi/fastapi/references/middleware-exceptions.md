---
type: Reference
title: middleware-exceptions — FastAPI 源码信源
description: 中间件薄再导出层与异常体系，涵盖 CORS/GZip/WSGI 中间件、AsyncExitStackMiddleware、HTTPException/ValidationError 异常层级及默认异常处理器
tags: [fastapi, source, middleware, exceptions]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/middleware-exceptions.md
    title: FastAPI v0.141.1 源码
---

# middleware-exceptions 源码信源

## 基本信息
- **源码路径**: `fastapi/middleware/cors.py`、`fastapi/middleware/gzip.py`、`fastapi/middleware/wsgi.py`、`fastapi/middleware/asyncexitstack.py`、`fastapi/exceptions.py`、`fastapi/exception_handlers.py`
- **版本**: 0.141.1
- **事实范围**: F-092 ~ F-094, F-100 ~ F-106, F-138 ~ F-143

## 公开 API 清单

### 类（exceptions.py）
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `EndpointContext` | `TypedDict(total=False)` | 字段：function/path/file/line | F-100 |
| `HTTPException` | `StarletteHTTPException` | `__init__(status_code, detail=None, headers=None)` | F-101 |
| `WebSocketException` | `StarletteWebSocketException` | `__init__(code, reason=None)` | F-102 |
| `FastAPIError` | `RuntimeError` | 框架错误基类 | F-104 |
| `DependencyScopeError` | `FastAPIError` | 依赖 scope 错误 | F-104 |
| `PydanticV1NotSupportedError` | `FastAPIError` | Pydantic v1 不支持错误 | F-104 |
| `ValidationException` | `Exception` | `_errors`/`endpoint_ctx` 属性、`errors()` 方法、`_format_endpoint_context()`、`__str__()` | F-105 |
| `RequestValidationError` | `ValidationException` | 额外 `body` 属性 | F-105 |
| `WebSocketRequestValidationError` | `ValidationException` | WebSocket 校验错误 | F-105 |
| `ResponseValidationError` | `ValidationException` | 额外 `body` 属性 | F-105 |
| `FastAPIDeprecationWarning` | `UserWarning` | 弃用警告 | F-106 |

### 类（middleware，薄再导出）
| 类名 | 来源 | 事实编号 |
|------|------|---------|
| `CORSMiddleware` | `starlette.middleware.cors`（纯再导出） | F-092, F-138, F-139 |
| `GZipMiddleware` | `starlette.middleware.gzip`（纯再导出） | F-093, F-140, F-141 |
| `WSGIMiddleware` | `starlette.middleware.wsgi`（纯再导出） | F-094, F-142, F-143 |
| `AsyncExitStackMiddleware` | FastAPI 自定义（在中间件栈中位于 ExceptionMiddleware 与 router 之间） | F-011 |

### 函数（exception_handlers.py）
| 函数名 | 说明 | 事实编号 |
|--------|------|---------|
| `http_exception_handler` | HTTPException 默认处理器，在 `FastAPI.__init__` 中注册 | F-010 |
| `request_validation_exception_handler` | RequestValidationError 默认处理器 | F-010 |
| `websocket_request_validation_exception_handler` | WebSocketRequestValidationError 默认处理器 | F-010 |

### 模块级动态模型
| 名称 | 说明 | 事实编号 |
|------|------|---------|
| `RequestErrorModel` | `create_model("Request")` 动态创建 | F-103 |
| `WebSocketErrorModel` | `create_model("WebSocket")` 动态创建 | F-103 |

## 关键实现细节

### CORSMiddleware（F-092, F-138, F-139）
- 单行模块：`from starlette.middleware.cors import CORSMiddleware as CORSMiddleware  # noqa`
- 模块不含 `__all__` 定义
- 文件无其他 import 语句、类定义或函数定义，整文件长度为 1 行
- 类本身不在本模块定义，直接复用 Starlette 实现

### GZipMiddleware（F-093, F-140, F-141）
- 单行模块：`from starlette.middleware.gzip import GZipMiddleware as GZipMiddleware  # noqa`
- 仅含此一行导入语句
- GZipMiddleware 类本身不在本模块定义，直接复用 starlette.middleware.gzip 中的实现

### WSGIMiddleware（F-094, F-142, F-143）
- 导入语句跨多行用括号包裹：`from starlette.middleware.wsgi import WSGIMiddleware as WSGIMiddleware  # pragma: no cover # noqa`
- 模块无 `__all__` 定义
- WSGIMiddleware 为唯一公开名称

### AsyncExitStackMiddleware（F-011）
- 在 `FastAPI.build_middleware_stack` 中位于 ExceptionMiddleware 与 self.router 之间
- 支撑 `fastapi_inner_astack` 和 `fastapi_function_astack` 双层 AsyncExitStack 的 ASGI 生命周期
- 是 yield 依赖清理逻辑编织进 ASGI 调用链的关键中间件

### EndpointContext（F-100）
`class EndpointContext(TypedDict, total=False)` 字段：`function`、`path`、`file`、`line`，用于错误信息中的端点定位。

### HTTPException（F-101）
`class HTTPException(StarletteHTTPException)`：
- `__init__(status_code: int, detail: Any = None, headers: Mapping[str, str] | None = None)`
- 调用 `super().__init__`

### WebSocketException（F-102）
`class WebSocketException(StarletteWebSocketException)`：
- `__init__(code: int, reason: str | None = None)`

### 动态错误模型（F-103）
模块级通过 `create_model` 动态创建：
- `RequestErrorModel = create_model("Request")`
- `WebSocketErrorModel = create_model("WebSocket")`

### FastAPIError 层级（F-104）
- `class FastAPIError(RuntimeError)`：框架错误基类
- `class DependencyScopeError(FastAPIError)`：依赖 scope 错误
- `class PydanticV1NotSupportedError(FastAPIError)`：显式声明不支持 Pydantic v1

### ValidationException 体系（F-105）
`class ValidationException(Exception)`：
- 含 `_errors`/`endpoint_ctx` 属性
- `errors()` 方法返回校验错误列表
- `_format_endpoint_context()` 方法格式化端点上下文
- `__str__()` 方法生成错误描述
- 三个子类：
  - `RequestValidationError`：额外 `body` 属性
  - `WebSocketRequestValidationError`：WebSocket 场景
  - `ResponseValidationError`：额外 `body` 属性

### FastAPIDeprecationWarning（F-106）
`class FastAPIDeprecationWarning(UserWarning)`，用于 example/regex/UJSONResponse/ORJSONResponse 等弃用标记。

### 默认异常处理器注册（F-010）
`FastAPI.__init__` 中注册三个默认异常处理器：
- `HTTPException` → `http_exception_handler`
- `RequestValidationError` → `request_validation_exception_handler`
- `WebSocketRequestValidationError` → `websocket_request_validation_exception_handler`

## 相关信源
- [applications.md](applications.md) — build_middleware_stack 中间件顺序、默认异常处理器注册
- [responses-encoders.md](responses-encoders.md) — RequestValidationError 相关的 jsonable_encoder
