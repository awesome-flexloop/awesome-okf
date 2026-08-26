# 概念文档索引

## 入门篇

* [00 · FastAPI 简介](00-introduction.md) — 基于 Starlette + Pydantic 的高性能 ASGI 框架，类型注解驱动、自动 OpenAPI 文档、原生异步支持
* [01 · FastAPI 应用类](01-application.md) — FastAPI 主类详解、初始化参数六组分类、中间件栈五层顺序、OpenAPI 缓存、setup 文档路由

## 核心机制篇

* [02 · 路由系统](02-routing-system.md) — APIRouter 组合模式、APIRoute 状态填充、include_router 合并语义、frontend 低优先级路由
* [03 · 路径操作与请求处理](03-path-operations.md) — get_request_handler 完整流程、双层 AsyncExitStack、请求体解析三分支、SSE/JSONL 流式响应
* [04 · 依赖注入系统](04-dependency-injection.md) — Depends/Security、Dependant 依赖树、solve_dependencies 递归求解、yield 依赖生命周期、dependency_overrides
* [05 · 参数声明系统](05-parameter-declaration.md) — Param/Path/Query/Header/Cookie 继承链、Pydantic FieldInfo 校验、Annotated+Doc 文档注解、验证约束
* [06 · 请求体与数据验证](06-request-body.md) — Body/Form/File 三层继承、embed_body_fields、strict_content_type CSRF 防护、Pydantic 模型验证、UploadFile

## 高级功能篇

* [07 · 响应模型与序列化](07-response-model.md) — response_model、serialize_response 验证+序列化、dump_json 快速路径、Response 类族、separate_input_output_schemas
* [08 · OpenAPI 自动生成](08-openapi-generation.md) — get_openapi 管线、routes_version 缓存、Swagger UI/ReDoc 集成、operationId、callbacks/webhooks
* [09 · 安全机制](09-security.md) — OAuth2PasswordBearer、HTTPBasic/HTTPBearer/HTTPDigest、Security scopes、get_authorization_scheme_param
* [10 · 中间件与 CORS](10-middleware-cors.md) — build_middleware_stack 五层顺序、AsyncExitStackMiddleware、CORSMiddleware/GZipMiddleware/WSGIMiddleware
* [11 · 异常处理](11-exception-handling.md) — HTTPException/RequestValidationError/ResponseValidationError 层级、三个默认处理器、EndpointContext 错误定位
* [12 · 流式响应与 WebSocket](12-streaming-websocket.md) — SSE anyio 内存流+keepalive、JSONL 流式、生成器端点自动检测、APIWebSocketRoute
* [13 · 测试与高级特性](13-testing-advanced.md) — TestClient、dependency_overrides 测试替换、BackgroundTasks、Default/DefaultPlaceholder、frontend 静态前端

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-application
02-routing-system
03-path-operations
04-dependency-injection
05-parameter-declaration
06-request-body
07-response-model
08-openapi-generation
09-security
10-middleware-cors
11-exception-handling
12-streaming-websocket
13-testing-advanced
```
