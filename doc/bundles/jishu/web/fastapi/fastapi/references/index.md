# 信源登记簿

| 信源文件 | 覆盖模块 | 事实范围 |
|---------|---------|---------|
| [applications.md](applications.md) | FastAPI 应用类：构造参数、中间件栈、OpenAPI 缓存、文档路由、路由委托、frontend、WebSocket 路由 | F-006 ~ F-017 |
| [routing.md](routing.md) | 路由系统：双层 AsyncExitStack、请求处理管线、SSE/JSONL 流式、APIRoute、APIRouter 组合模式、WebSocket 路由 | F-018 ~ F-037 |
| [dependencies.md](dependencies.md) | 依赖注入：Dependant 模型、可调用类型检测缓存、依赖树构建、递归求解、参数分析、生成器生命周期 | F-054 ~ F-066 |
| [params.md](params.md) | 参数系统：ParamTypes 枚举、Param/Path/Query/Header/Cookie/Body/Form/File 继承体系、Depends/Security、九个工厂函数 | F-038 ~ F-053 |
| [openapi.md](openapi.md) | OpenAPI 生成：get_openapi 管线、路径项生成、Schema 定义、Swagger UI/ReDoc HTML、40 个 OpenAPI 模型类 | F-067 ~ F-079 |
| [security.md](security.md) | 安全认证：SecurityBase、HTTP Basic/Bearer/Digest、OAuth2 密码模式、Authorization 头解析 | F-080 ~ F-091, F-144, F-145, F-157, F-158 |
| [middleware-exceptions.md](middleware-exceptions.md) | 中间件与异常：CORS/GZip/WSGI 薄再导出、AsyncExitStackMiddleware、HTTPException/ValidationError 异常层级、默认处理器 | F-092 ~ F-094, F-100 ~ F-106, F-138 ~ F-143 |
| [responses-encoders.md](responses-encoders.md) | 响应与编码：响应类再导出、jsonable_encoder、UploadFile、DefaultPlaceholder、SSE、BackgroundTasks、_compat 兼容层 | F-095 ~ F-098, F-107 ~ F-137, F-152 ~ F-156 |

```{toctree}
:hidden:
:maxdepth: 7

applications
dependencies
middleware-exceptions
openapi
params
responses-encoders
routing
security
```
