---
type: Concept
title: FastAPI 简介
description: 基于 Starlette 与 Pydantic v2 构建的现代 ASGI Web 框架，通过类型注解驱动自动校验、依赖注入与 OpenAPI 文档生成。
tags: [fastapi, introduction, asgi, starlette, pydantic]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/applications.md
    title: FastAPI v0.141.1 源码信源
---

# FastAPI 简介

FastAPI 是一个基于 Starlette 与 Pydantic v2 构建的现代 Python ASGI（Asynchronous Server Gateway Interface，异步服务器网关接口）Web 框架。它以 Python 类型注解（type hints）为唯一真相源，在运行时自动完成请求参数校验、依赖注入求解与 OpenAPI 文档生成。本概念文档基于 FastAPI v0.141.1 源码事实撰写，对应 `__version__ = "0.141.1"`（F-001）。

## 框架定位与基座关系

FastAPI 的类定义为 `class FastAPI(Starlette)`（F-006），即它直接继承自 Starlette，而非在其外部做包装。这意味着 FastAPI 是 Starlette 的超集：所有 Starlette 的能力（路由、中间件、WebSocket、测试客户端等）在 FastAPI 中均可直接使用，FastAPI 在此之上叠加了类型驱动的参数校验、依赖注入与自动文档。

Starlette 提供 ASGI 底层能力（请求/响应抽象、路由匹配、中间件栈、WebSocket 会话），Pydantic v2 提供数据模型定义、校验与序列化能力。FastAPI 在二者之间架起桥梁，将函数签名中的类型注解翻译为运行时校验逻辑与 OpenAPI schema。源码中通过 `_compat` 兼容层统一封装 Pydantic v2 的 `TypeAdapter`，核心代码只依赖 `ModelField.validate/serialize` 协议（F-133）。

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello"}
```

`FastAPI` 类继承 `Starlette`（F-006），因此上述 `app` 同时是合法的 Starlette 与 ASGI 应用实例。

## 公开 API 全景

FastAPI 的公开 API 通过 `fastapi/__init__.py` 导出，分为三组（F-003、F-004、F-005）：

**核心类**：`FastAPI`、`BackgroundTasks`、`UploadFile`、`HTTPException`、`WebSocketException`（F-003）。

**九个参数工厂函数**：`Body`、`Cookie`、`Depends`、`File`、`Form`、`Header`、`Path`、`Query`、`Security`（F-004）。这些函数返回对应参数类实例，用于在端点签名中声明参数的位置、校验约束与元数据。

**请求/响应/路由原语**：`Request`、`Response`、`APIRouter`、`WebSocket`、`WebSocketDisconnect`（F-005）。

此外，`starlette.status` 模块以 `from starlette import status as status` 的形式整体重新导出（F-002），开发者可通过 `fastapi.status.HTTP_404_NOT_FOUND` 等常量引用标准 HTTP 状态码。响应类 `FileResponse`、`HTMLResponse`、`JSONResponse`、`PlainTextResponse`、`RedirectResponse`、`Response`、`StreamingResponse` 以及 `EventSourceResponse` 均从 `fastapi.responses` 重新导出（F-095）；`TestClient` 直接来自 `starlette.testclient`（F-128）。

## 核心特性

**类型注解驱动**：端点函数的参数类型注解同时承担三重职责——运行时数据校验、OpenAPI schema 生成、IDE 类型提示。即使不写 `Query()` 等显式声明，FastAPI 也能根据参数类型自动推断参数位置（路径参数→`Path`、非标量→`Body`、标量→`Query`，F-061）。

**自动 OpenAPI 文档**：`FastAPI.__init__` 设置 `self.openapi_version = "3.1.0"`（F-008），OpenAPI 文档从路由列表与 Pydantic 模型自动推导。`setup()` 方法注册四个文档路由：OpenAPI JSON（`openapi_url`）、Swagger UI（`docs_url`）、OAuth2 回调页、ReDoc（`redoc_url`），均标记 `include_in_schema=False`（F-013）。

**依赖注入**：通过 `Depends` 声明依赖，框架递归构建 `Dependant` 树并在请求处理时后序求解（F-058、F-064）。支持子依赖嵌套、`use_cache` 请求级缓存、`yield` 依赖的异步生命周期管理，以及测试时的 `dependency_overrides` 运行时替换。

**异步支持**：端点可以是 `async def` 协程或普通 `def` 同步函数。协程直接 `await` 执行，同步函数通过 `run_in_threadpool` 在线程池中运行（F-021），避免阻塞事件循环。`yield` 依赖通过双层 `AsyncExitStack` 管理清理时机（F-018）。

## 设计哲学

FastAPI 的设计哲学可概括为"声明一次，四处生效"：一个参数声明同时是默认值、校验器、文档 schema 与类型提示。框架通过继承 Pydantic `FieldInfo` 的参数类（`Param`、`Body` 及其子类）实现元数据复用（F-039、F-045），通过 `Annotated[..., Doc(...)]` 在工厂函数签名中内嵌文档字符串（F-051）。

在框架边界上，FastAPI 采取"薄再导出"策略：CORS/GZip/WSGI 中间件、TestClient、Request、WebSocket 等均直接从 Starlette 再导出而不在本地重写（F-092、F-093、F-128、F-099、F-121），保持与上游同步。Pydantic 版本差异通过 `_compat` 层隔离，v0.141 已显式不支持 Pydantic v1（F-104、F-117）。

## 与 Flask/Django 对比

| 维度 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| 协议标准 | ASGI（原生异步） | WSGI（同步，异步需扩展） | WSGI（同步，ASGI 可选） |
| 基座 | Starlette + Pydantic | Werkzeug + Jinja2 | 自研全栈 |
| 参数校验 | 类型注解自动推导 | 需手动校验或扩展 | 表单层手动校验 |
| API 文档 | 自动生成 OpenAPI 3.1 | 需扩展 | DRF 需额外配置 |
| 依赖注入 | 内建 `Depends` 树 | 无内建 | 无内建 |
| 异步 | 原生 `async/await` | 有限支持 | 有限支持 |

FastAPI 不追求 Django 式的"全栈内置"（不自带 ORM、Admin、模板引擎），而是聚焦于 API 层，通过依赖注入机制与任意 ORM/服务集成。

## 版本与兼容性

- **FastAPI 版本**：0.141.1（F-001）
- **OpenAPI 版本**：3.1.0（F-008）
- **Pydantic**：仅支持 v2，检测到 v1 抛 `PydanticV1NotSupportedError`（F-104、F-117）
- **Python 类型注解**：全面采用 `Annotated` 写法（F-051）

## 相关概念

- [FastAPI 应用类](01-application.md)
- [路由系统](02-routing-system.md)
- [路径操作与请求处理](03-path-operations.md)
- [依赖注入系统](04-dependency-injection.md)
- [参数声明系统](05-parameter-declaration.md)
- [请求体与数据验证](06-request-body.md)
