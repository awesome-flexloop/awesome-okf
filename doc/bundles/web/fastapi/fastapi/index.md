---
okf_version: "0.2"
type: bundle
title: FastAPI 核心知识库
---

# FastAPI 核心知识库

本知识包是 Python 高性能 ASGI Web 框架 [FastAPI](https://fastapi.tiangolo.com/)（v0.141.1，MIT 许可证）的系统化中文源码教程，基于 FastAPI 源码（`external/libs/fastapi/fastapi/fastapi/` 目录）深度阅读生成，覆盖从应用类初始化到请求处理全链路、从依赖注入树到 OpenAPI 自动生成、从中间件栈到流式响应的完整知识体系。所有内容均溯源至 FastAPI 源码核心模块，遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

## 入门篇（concepts/）

* [FastAPI 简介](concepts/00-introduction.md) — 基于 Starlette + Pydantic 的 ASGI 框架、四大核心特性、设计哲学、与 Flask/Django 对比。
* [FastAPI 应用类](concepts/01-application.md) — FastAPI(Starlette) 继承关系、__init__ 六组参数、中间件栈五层顺序、OpenAPI 版本缓存、setup 四个文档路由。

## 核心机制篇（concepts/）

* [路由系统](concepts/02-routing-system.md) — APIRouter 组合模式、APIRoute 状态填充、_populate_api_route_state、include_router 合并语义（OR/AND/拼接）、frontend 低优先级路由。
* [路径操作与请求处理](concepts/03-path-operations.md) — get_request_handler 工厂、双层 AsyncExitStack（fastapi_inner_astack/fastapi_function_astack）、请求体解析三分支、strict_content_type CSRF 防护、同步/异步端点分流。
* [依赖注入系统](concepts/04-dependency-injection.md) — Depends/Security dataclass、Dependant 依赖树、三个 lru_cache 可调用类型判定、solve_dependencies 递归求解、yield 依赖生命周期、dependency_overrides。
* [参数声明系统](concepts/05-parameter-declaration.md) — Param(FieldInfo) 基类、Path/Query/Header/Cookie 四子类、Pydantic v2 校验约束、Annotated+Doc 文档注解、九个工厂函数。
* [请求体与数据验证](concepts/06-request-body.md) — Body/Form/File 三层继承链、media_type 区分、embed_body_fields 多参数嵌入、Pydantic ModelField 验证、UploadFile。

## 高级功能篇（concepts/）

* [响应模型与序列化](concepts/07-response-model.md) — response_model、serialize_response 验证+序列化双阶段、dump_json Rust 核心快速路径、Response 类族、separate_input_output_schemas。
* [OpenAPI 自动生成](concepts/08-openapi-generation.md) — get_openapi 管线、routes_version 增量缓存、get_openapi_path、Swagger UI/ReDoc 四路由、operationId/unique_id、callbacks/webhooks。
* [安全机制](concepts/09-security.md) — OAuth2PasswordBearer 密码流、HTTPBasic/HTTPBearer/HTTPDigest、Security scopes 权限校验、get_authorization_scheme_param。
* [中间件与 CORS](concepts/10-middleware-cors.md) — build_middleware_stack 五层顺序（ServerError→user→Exception→AsyncExitStack→router）、AsyncExitStackMiddleware contextvars 保持、CORS/GZip/WSGI 中间件。
* [异常处理](concepts/11-exception-handling.md) — HTTPException/FastAPIError/RequestValidationError/ResponseValidationError 层级、三个默认处理器、EndpointContext 错误定位（file/line/function/path）。
* [流式响应与 WebSocket](concepts/12-streaming-websocket.md) — SSE EventSourceResponse + anyio memory stream + keepalive、JSONL 流式、生成器端点自动检测、APIWebSocketRoute、WebSocketDisconnect。
* [测试与高级特性](concepts/13-testing-advanced.md) — TestClient、dependency_overrides 测试替换、BackgroundTasks + ParamSpec、Default/DefaultPlaceholder 延迟解析、frontend 静态前端服务。

## 实战示例（examples/）

* [基础 CRUD API](examples/01-basic-crud-api.md) — 完整增删改查：FastAPI 创建、HTTP 装饰器、Pydantic 模型、response_model、HTTPException、APIRouter 组织。
* [依赖注入实战](examples/02-dependency-injection.md) — 函数/类/yield 依赖、子依赖嵌套、use_cache 缓存、全局/路由级依赖、dependency_overrides 测试替换。
* [OAuth2 安全认证](examples/03-security-oauth2.md) — OAuth2 密码流完整流程：OAuth2PasswordBearer、OAuth2PasswordRequestForm、Security scopes、安全端点。
* [流式响应与 WebSocket](examples/04-streaming-sse.md) — SSE 实时通知（EventSourceResponse/ServerSentEvent）、JSONL 数据流、WebSocket 双向通信。
* [中间件与测试](examples/05-middleware-testing.md) — CORS/GZip 配置、自定义 BaseHTTPMiddleware、TestClient 断言测试、BackgroundTasks。

## 信源登记簿（references/）

* [applications.md](references/applications.md) — FastAPI 类、__init__ 参数、build_middleware_stack、openapi()、setup()、add_api_route、frontend（F-006~F-017）。
* [routing.md](references/routing.md) — APIRouter、APIRoute、APIWebSocketRoute、request_response、get_request_handler、SSE/JSONL 流式（F-018~F-037）。
* [dependencies.md](references/dependencies.md) — Dependant dataclass、solve_dependencies、get_dependant、三个 callable 判定函数（F-054~F-066）。
* [params.md](references/params.md) — Param/Path/Query/Header/Cookie/Body/Form/File 类、Depends/Security、九个工厂函数（F-038~F-053）。
* [openapi.md](references/openapi.md) — get_openapi、get_openapi_path、Swagger UI/ReDoc HTML、OpenAPI 模型（F-067~F-079）。
* [security.md](references/security.md) — SecurityBase、HTTPBasic/Bearer/Digest、OAuth2、OAuth2PasswordBearer、get_authorization_scheme_param（F-080~F-091, F-157~F-158）。
* [middleware-exceptions.md](references/middleware-exceptions.md) — CORS/GZip/WSGI/AsyncExitStack 中间件、HTTPException/ValidationError 层级、默认处理器（F-092~F-106）。
* [responses-encoders.md](references/responses-encoders.md) — Response 类族、jsonable_encoder、UploadFile、DefaultPlaceholder、SSE、BackgroundTasks、_compat（F-107~F-156）。

## 信任与生命周期说明

* **status 判定依据**：全部 27 个内容文档（14 个概念 + 5 个示例 + 8 个信源登记）均 `status: stable`。内容基于对 FastAPI v0.141.1 源码（`external/libs/fastapi/fastapi/fastapi/` 目录）的逐模块阅读与事实提取（158 条源码事实 F-001~F-158），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-23`。FastAPI 核心架构（Starlette 继承+Pydantic 校验+Dependant 依赖树+APIRouter 组合）自 0.x 以来保持稳定，新特性（SSE/JSONL 流式、frontend、strict_content_type）在 v0.141 中已成型；该日期作为针对未来大版本（如 1.0）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-23）；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 27 个内容文档（14 个概念 + 5 个示例 + 8 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
