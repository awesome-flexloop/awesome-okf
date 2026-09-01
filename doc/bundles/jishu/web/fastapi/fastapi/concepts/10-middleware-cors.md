---
type: Concept
title: 中间件系统与 CORS
description: 详解 build_middleware_stack 五层中间件顺序、AsyncExitStackMiddleware 的 contextvars 上下文保持、CORSMiddleware/GZipMiddleware/WSGIMiddleware 薄再导出层、add_middleware 方法与 CORS 配置参数。
tags: [fastapi, middleware, cors, gzip, wsgi, starlette, asgi]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/middleware-exceptions.md
    title: FastAPI v0.141.1 源码信源
---

# 中间件系统与 CORS

FastAPI 的中间件系统建立在 Starlette 之上，通过 `build_middleware_stack` 构建五层洋葱模型。FastAPI 自身新增的中间件只有 `AsyncExitStackMiddleware`（用于依赖注入的异步上下文管理），其余中间件（CORS、GZip、WSGI）均从 Starlette 薄再导出。这种设计使 FastAPI 保持与 Starlette 中间件生态的完全兼容，同时在请求处理链中精确插入依赖注入生命周期管理。

## build_middleware_stack 五层顺序

`FastAPI.build_middleware_stack` 构建中间件栈（F-011），按包裹顺序（从外到内）为：

```text
ServerErrorMiddleware
  └── user_middleware（用户添加的中间件，按添加顺序包裹）
        └── ExceptionMiddleware
              └── AsyncExitStackMiddleware
                    └── router（路由处理）
```

构建过程使用 Starlette 的 `Middleware` 封装，反向包裹——即最后添加的中间件位于最内层。每一层的职责：

| 层级 | 类 | 职责 |
|------|-----|------|
| 最外层 | `ServerErrorMiddleware` | 捕获所有未处理异常，返回 500 响应，确保异常不泄漏到 ASGI 服务器 |
| 第二层 | `user_middleware` | 用户通过 `add_middleware` 或构造参数 `middleware` 添加的中间件 |
| 第三层 | `ExceptionMiddleware` | 将注册的异常处理器映射到 HTTP 响应，处理 `HTTPException` 等 |
| 第四层 | `AsyncExitStackMiddleware` | FastAPI 特有，维护 `AsyncExitStack` 以保持 contextvars 上下文并管理异步资源清理 |
| 最内层 | `self.router` | `APIRouter` 实例，执行路由匹配和端点调用 |

`ServerErrorMiddleware` 位于最外层至关重要——它是 500 错误的最后一道防线，即使 `ExceptionMiddleware` 或用户中间件本身抛出异常也能被捕获。`ExceptionMiddleware` 在内层负责将 `HTTPException` 和自定义异常转换为对应响应，但无法捕获更外层中间件中的异常。

## AsyncExitStackMiddleware

`AsyncExitStackMiddleware` 是 FastAPI 唯一新增的中间件类（F-011），位于 `ExceptionMiddleware` 与 `router` 之间。其核心职责是为依赖注入系统提供请求级的异步上下文管理：

1. **保持 contextvars 上下文**：在中间件层建立 `AsyncExitStack`，确保 `contextvars` 在整个请求生命周期内正确传播。这对 `yield` 依赖尤其重要——依赖中设置的 contextvar 值在端点执行和响应发送期间可见
2. **关闭文件和异步资源**：`solve_dependencies` 中 `scope="request"` 的生成器依赖进入 request 级 `AsyncExitStack`（绑定到 `fastapi_inner_astack`），在响应完全发送后才执行清理（F-064）。这包括数据库连接关闭、文件句柄释放等
3. **与双层栈协作**：`request_response` 在路由内部还建立了 function 级栈（`fastapi_function_astack`），在端点返回时立即关闭；而 request 级栈由 `AsyncExitStackMiddleware` 管理，生命周期更长

`AsyncExitStackMiddleware` 位于 user middleware **内部**（即 user middleware 的下游），这意味着用户中间件无法访问 FastAPI 依赖注入的上下文，但也意味着用户中间件中的异常在依赖清理之前就被 `ExceptionMiddleware` 处理，避免资源泄漏。

## add_middleware 方法

`add_middleware` 方法继承自 Starlette，用于在应用构造后动态添加中间件：

```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

也可以在 `FastAPI()` 构造时通过 `middleware` 参数传入（F-007）：

```python
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    middleware=[
        Middleware(CORSMiddleware, allow_origins=["*"])
    ]
)
```

两种方式等效。中间件按添加顺序包裹，后添加的位于内层。`build_middleware_stack` 在首次请求时调用（由 Starlette 生命周期触发），之后缓存。在应用启动后再调用 `add_middleware` 不会重建已构建的栈，因此应在构造时或启动事件前注册全部中间件。

## BaseHTTPMiddleware

Starlette 提供 `BaseHTTPMiddleware` 作为编写 HTTP 中间件的基类，FastAPI 完全兼容。自定义中间件继承 `BaseHTTPMiddleware` 并实现 `dispatch` 方法：

```python
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Custom"] = "value"
        return response

app.add_middleware(CustomHeaderMiddleware)
```

`dispatch` 方法接收 `Request` 和 `call_next` 回调，在调用 `call_next(request)` 前后执行逻辑。需要注意，`BaseHTTPMiddleware` 在某些场景下与 `contextvars` 和流式响应存在已知限制，对于高性能场景可直接实现纯 ASGI 中间件。

## CORSMiddleware

`CORSMiddleware` 从 Starlette 单行再导出（F-092, F-138, F-139）：

```python
from starlette.middleware.cors import CORSMiddleware as CORSMiddleware  # noqa
```

整个模块仅 1 行代码，无 `__all__` 定义，不做任何子类化或扩展。这确保 FastAPI 始终使用与 Starlette 版本匹配的 CORS 实现。

CORS 配置参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `allow_origins` | `list[str]` | 允许的源列表，`["*"]` 允许所有 |
| `allow_methods` | `list[str]` | 允许的 HTTP 方法，`["*"]` 允许所有（默认 `["GET"]`） |
| `allow_headers` | `list[str]` | 允许的请求头，`["*"]` 允许所有 |
| `allow_credentials` | `bool` | 是否允许 Cookie 和认证头（默认 `False`） |
| `allow_origin_regex` | `str \| None` | 匹配允许源的正则表达式 |
| `expose_headers` | `list[str]` | 浏览器可访问的响应头列表 |
| `max_age` | `int` | 预检请求缓存时间（秒） |

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com", "https://www.example.com"],
    allow_origin_regex=r"https://.*\.example\.com",
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    expose_headers=["X-Request-ID"],
    max_age=600,
)
```

`CORSMiddleware` 自动处理预检请求（`OPTIONS`）和实际请求的 CORS 头。当 `allow_credentials=True` 时，`allow_origins` 不能设为 `["*"]`（浏览器安全限制），必须明确指定源。

## GZipMiddleware

`GZipMiddleware` 同样单行再导出（F-093, F-140, F-141）：

```python
from starlette.middleware.gzip import GZipMiddleware as GZipMiddleware  # noqa
```

用于压缩 HTTP 响应。配置 `minimum_size` 参数控制最小压缩阈值（字节），小于该值的响应不压缩。典型用法：

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

GZip 中间件检查请求的 `Accept-Encoding` 头，包含 `gzip` 时压缩响应。注意流式响应（`StreamingResponse`）通常也会被压缩，但 SSE 响应因需要实时发送而不应启用压缩。

## WSGIMiddleware

`WSGIMiddleware` 从 Starlette 再导出（F-094, F-142, F-143），导入语句跨多行：

```python
from starlette.middleware.wsgi import WSGIMiddleware as WSGIMiddleware  # pragma: no cover # noqa
```

标注 `# pragma: no cover` 表示该导入不纳入测试覆盖率统计（因为依赖 WSGI 应用运行时环境）。`WSGIMiddleware` 允许在 FastAPI（ASGI）应用中挂载 WSGI 应用（如 Flask、Django），实现渐进式迁移：

```python
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask

flask_app = Flask(__name__)

@flask_app.route("/legacy")
def legacy():
    return "Hello from Flask"

app = FastAPI()
app.mount("/v1", WSGIMiddleware(flask_app))
```

## 中间件模块的薄再导出模式

FastAPI 的三个中间件模块全部采用薄再导出模式：

| 模块 | 行数 | 实现位置 |
|------|------|---------|
| `middleware/cors.py` | 1 行 | `starlette.middleware.cors` |
| `middleware/gzip.py` | 1 行 | `starlette.middleware.gzip` |
| `middleware/wsgi.py` | 3 行 | `starlette.middleware.wsgi` |

这些模块无 `__all__` 定义、无类定义、无函数定义，仅通过 `as` 别名重新导出 Starlette 类（F-138~F-143）。这一设计有明确的架构意图：

1. **上游同步**：中间件实现完全由 Starlette 维护，FastAPI 升级 Starlette 版本即自动获得中间件更新和安全修复
2. **导入路径一致**：用户可以从 `fastapi.middleware.cors` 导入，保持与其他 FastAPI 模块一致的导入路径风格
3. **零维护成本**：FastAPI 团队不需要为标准中间件编写测试和文档

## 相关概念

- [异常处理与校验错误](11-exception-handling.md)
- [FastAPI 应用类与生命周期](01-application.md)
- [路由系统](02-routing-system.md)
- [依赖注入系统](04-dependency-injection.md)
- [测试与高级特性](13-testing-advanced.md)
