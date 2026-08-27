---
type: Concept
title: 异常处理与校验错误
description: 详解 HTTPException/FastAPIError/ValidationException 异常类层次、RequestValidationError 与 ResponseValidationError 的触发路径、EndpointContext 端点定位、三个默认异常处理器注册及自定义异常处理器机制。
tags: [fastapi, exception, error-handling, validation, http-exception]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/middleware-exceptions.md
    title: FastAPI v0.141.1 源码信源
---

# 异常处理与校验错误

FastAPI 定义了清晰的异常类层次，将 HTTP 错误、框架内部错误和数据校验错误分离。校验异常体系采用"聚合错误"设计——收集所有参数的校验错误后一次性抛出，而非在首个错误处中断。框架在应用构造时注册三个默认异常处理器，自动将 `HTTPException`、`RequestValidationError` 和 `WebSocketRequestValidationError` 转换为符合规范的 HTTP/WebSocket 响应。开发者可通过装饰器或方法注册自定义处理器，统一错误响应格式。

## 异常类层次

FastAPI 的异常定义在 `fastapi/exceptions.py` 中，构成三层结构：

```text
Exception
├── StarletteHTTPException
│     └── HTTPException（F-101）
├── StarletteWebSocketException
│     └── WebSocketException（F-102）
├── ValidationException（F-105）
│     ├── RequestValidationError
│     ├── WebSocketRequestValidationError
│     └── ResponseValidationError
└── RuntimeError
      └── FastAPIError（F-104）
            ├── DependencyScopeError
            └── PydanticV1NotSupportedError
```

### HTTPException

`HTTPException` 继承 Starlette 的 `StarletteHTTPException`（F-101），是最常用的异常类：

```python
class HTTPException(StarletteHTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
```

- `status_code`：HTTP 状态码（如 404、403、401）
- `detail`：错误详情，可以是任意可 JSON 序列化的值
- `headers`：附加到错误响应的 HTTP 头（常用于 `WWW-Authenticate`）

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "Invalid ID"},
        )
    return {"item_id": item_id}
```

### WebSocketException

`WebSocketException` 继承 Starlette 的 `StarletteWebSocketException`（F-102），用于 WebSocket 连接错误：

```python
class WebSocketException(StarletteWebSocketException):
    def __init__(self, code: int, reason: str | None = None) -> None:
```

- `code`：WebSocket 关闭码（如 1008 表示违反策略）
- `reason`：关闭原因字符串

### FastAPIError 框架错误

`FastAPIError(RuntimeError)` 是框架内部错误的基类（F-104），子类包括：

- **`DependencyScopeError`**：依赖作用域配置错误（如在 request 级依赖中访问仅 function 级可用的资源）
- **`PydanticV1NotSupportedError`**：检测到 Pydantic v1 时抛出，v0.141 已不支持 Pydantic v1（F-104, F-117）

这些异常表示框架使用错误或环境配置问题，通常不应由端点代码主动抛出。

## ValidationException 校验异常体系

`ValidationException` 是所有数据校验错误的基类（F-105），核心属性和方法：

- **`_errors`**：校验错误列表
- **`endpoint_ctx`**：端点上下文信息
- **`errors()`**：返回格式化的错误列表
- **`_format_endpoint_context()`**：格式化端点上下文为可读字符串
- **`__str__()`**：返回包含错误详情和端点位置的字符串表示

### 三个具体子类

**`RequestValidationError`**：请求数据校验失败时抛出。额外携带 `body` 属性，保存原始请求体数据，便于调试和错误响应。在 `get_request_handler` 中的两处触发（F-024, F-022）：
1. 请求体解析和校验错误（JSON 解析失败、Pydantic 模型校验失败）
2. 依赖求解错误（`solve_dependencies` 返回的 errors 非空时）

**`WebSocketRequestValidationError`**：WebSocket 连接建立时的参数校验失败。在 `get_websocket_app` 中，依赖求解 errors 非空时抛出（F-028）。

**`ResponseValidationError`**：响应数据校验失败时抛出。在 `serialize_response` 中，`field.validate` 返回 errors 非空时抛出（F-020）。额外携带 `body` 属性保存原始响应内容。与 `RequestValidationError` 不同，这是服务端错误（端点返回了不符合 `response_model` 的数据），通常应通过修复代码解决。

## EndpointContext 端点定位

`EndpointContext` 是一个 `TypedDict(total=False)`（F-100），用于在校验错误中定位出错的端点：

```python
class EndpointContext(TypedDict, total=False):
    function: str
    path: str
    file: str
    line: int
```

四个字段均为可选：
- `function`：端点函数名
- `path`：路由路径模板
- `file`：源文件路径
- `line`：行号

`ValidationException._format_endpoint_context()` 将这些信息格式化为人类可读字符串，附加到错误消息中，帮助开发者快速定位校验失败的端点。

## 错误模型

模块级通过 Pydantic 的 `create_model` 动态创建两个错误模型（F-103）：

```python
RequestErrorModel = create_model("Request")
WebSocketErrorModel = create_model("WebSocket")
```

这两个空模型在 OpenAPI schema 生成中作为校验错误响应的占位引用，使 422 响应有明确的 schema 定义。它们由框架内部使用，开发者通常不需要直接引用。

## 默认异常处理器

FastAPI 在 `__init__` 中注册三个默认异常处理器（F-010）：

| 异常类 | 处理器函数 | 响应 |
|--------|-----------|------|
| `HTTPException` | `http_exception_handler` | JSON 响应，状态码为异常的 status_code，body 含 `detail` |
| `RequestValidationError` | `request_validation_exception_handler` | 422 响应，body 含 `detail`（错误列表） |
| `WebSocketRequestValidationError` | `websocket_request_validation_exception_handler` | 关闭 WebSocket 连接 |

`http_exception_handler` 还会将异常的 `headers` 字典附加到响应中，这对认证场景（如 `WWW-Authenticate` 头）至关重要。

`request_validation_exception_handler` 返回 422 Unprocessable Entity，响应体格式为：

```json
{
  "detail": [
    {
      "type": "string",
      "loc": ["body", "name"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

每个错误包含 `type`（错误类型）、`loc`（错误位置，如 `["body", "field_name"]` 或 `["query", "param_name"]`）、`msg`（错误消息）和 `input`（导致错误的输入值）。

## exception_handlers 字典与自定义处理器

`FastAPI.__init__` 接收 `exception_handlers` 参数（F-007），它是一个字典，键为异常类或状态码，值为处理器函数。默认三个处理器在构造时合并到该字典中。

注册自定义异常处理器有两种方式：

**装饰器方式**：

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class CustomError(Exception):
    def __init__(self, message: str):
        self.message = message

app = FastAPI()

@app.exception_handler(CustomError)
async def custom_error_handler(request: Request, exc: CustomError):
    return JSONResponse(
        status_code=400,
        content={"error": exc.message},
    )
```

**方法调用方式**（继承自 Starlette）：

```python
async def custom_error_handler(request: Request, exc: CustomError):
    return JSONResponse(status_code=400, content={"error": exc.message})

app.add_exception_handler(CustomError, custom_error_handler)
```

也可以为 HTTP 状态码注册处理器：

```python
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"error": "Not found"})
```

异常处理器在 `ExceptionMiddleware`（中间件栈第三层）中匹配，按异常类的 MRO 顺序查找最具体的处理器。未注册处理器的异常由 `ServerErrorMiddleware`（最外层）捕获并返回 500。

## 校验错误的触发路径

理解校验错误在请求处理管线中的触发位置有助于调试和定制：

**请求校验**（`RequestValidationError`）：
1. `get_request_handler` 内部协程开始执行
2. `solve_dependencies` 递归求解所有依赖（F-064），path/query/header/cookie 参数校验错误收集到 `errors`
3. 请求体解析：form 请求调用 `request.form()`，JSON 请求读取 body_bytes 并解析（F-024）
4. `body_field.validate` 校验请求体，错误追加到 `errors`
5. 若 `errors` 非空，抛出 `RequestValidationError`，携带 errors、原始 body 和 endpoint_ctx

**响应校验**（`ResponseValidationError`）：
1. 端点函数执行完成，返回原始值
2. `serialize_response` 调用 `field.validate(response_content)`（F-020）
3. 校验通过则继续序列化；errors 非空则抛出 `ResponseValidationError`
4. 由于响应校验在端点返回后发生，此时请求已被处理，错误通常表示 schema 声明与实际返回不一致

**WebSocket 校验**（`WebSocketRequestValidationError`）：
1. `get_websocket_app` 求解依赖（F-028）
2. errors 非空时抛出 `WebSocketRequestValidationError`
3. 默认处理器关闭 WebSocket 连接而非发送 HTTP 响应

## FastAPIDeprecationWarning

`FastAPIDeprecationWarning(UserWarning)` 是 FastAPI 的弃用警告类（F-106），用于标记即将移除的功能。当前触发场景包括：
- 使用 `example` 参数（应使用 `examples` 复数）（F-040）
- 使用 `regex` 参数（应使用 `pattern`）（F-040）
- 使用 `UJSONResponse` 和 `ORJSONResponse`（F-097, F-098）

与 `DeprecationWarning` 不同，`UserWarning` 默认在正常运行时显示，确保开发者注意到弃用信息。

## 相关概念

- [中间件系统与 CORS](10-middleware-cors.md)
- [响应模型与序列化](07-response-model.md)
- [路径操作与请求处理](03-path-operations.md)
- [请求体与数据验证](06-request-body.md)
- [FastAPI 应用类与生命周期](01-application.md)
