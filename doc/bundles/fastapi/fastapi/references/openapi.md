---
type: Reference
title: openapi — FastAPI 源码信源
description: OpenAPI 文档生成系统，涵盖 get_openapi 生成管线、路径项与 Schema 定义生成、Swagger UI/ReDoc HTML 渲染及 40 个 OpenAPI 模型类
tags: [fastapi, source, openapi]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/openapi.md
    title: FastAPI v0.141.1 源码
---

# openapi 源码信源

## 基本信息
- **源码路径**: `fastapi/openapi/utils.py`、`fastapi/openapi/docs.py`、`fastapi/openapi/models.py`
- **版本**: 0.141.1
- **事实范围**: F-067 ~ F-079

## 公开 API 清单

### 类（openapi/models.py）
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `BaseModelWithConfig` | `BaseModel` | OpenAPI 模型基类 | F-076 |
| `Contact` | `BaseModelWithConfig` | 联系信息 | F-076 |
| `License` | `BaseModelWithConfig` | 许可证信息 | F-076 |
| `Info` | `BaseModelWithConfig` | API 基本信息 | F-076 |
| `Server` | `BaseModelWithConfig` | 服务器配置 | F-076 |
| `Reference` | `BaseModelWithConfig` | $ref 引用 | F-076 |
| `Schema` | `BaseModelWithConfig` | JSON Schema 2020-12 全词汇覆盖 | F-077 |
| `Parameter` | `ParameterBase` | `name: str`、`in_: ParameterInType = Field(alias="in")` | F-078 |
| `Header` | `ParameterBase` | 空类 | F-078 |
| `RequestBody` | `BaseModelWithConfig` | 请求体 | F-076 |
| `Response` | `BaseModelWithConfig` | 响应 | F-076 |
| `Operation` | `BaseModelWithConfig` | 操作 | F-076 |
| `PathItem` | `BaseModelWithConfig` | 路径项 | F-076 |
| `Components` | `BaseModelWithConfig` | schemas/responses/parameters/securitySchemes 等 | F-079 |
| `OpenAPI` | `BaseModelWithConfig` | 顶层文档模型 | F-079 |
| （共 40 个类） | — | 含 SecurityScheme*/APIKey*/HTTP*/OAuthFlow*/OAuth2/OpenIdConnect/Tag 等 | F-076 |

### 函数（openapi/utils.py）
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| `get_openapi` | `get_openapi(*, title, version, openapi_version="3.1.0", summary=None, description=None, routes, webhooks=None, tags=None, servers=None, terms_of_service=None, contact=None, license_info=None, separate_input_output_schemas=True, external_docs=None)` → dict | F-070 |
| `get_openapi_path` | `get_openapi_path(*, route, operation_ids, model_name_map, field_mapping, separate_input_output_schemas=True)` → tuple[dict, dict, dict] | F-068 |
| `get_fields_from_routes` | `get_fields_from_routes(...)` → 收集路由字段 | F-069 |

### 函数（openapi/docs.py）
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| `get_swagger_ui_html` | `get_swagger_ui_html(*, openapi_url, title, swagger_js_url=..., swagger_css_url=..., swagger_favicon_url=..., oauth2_redirect_url=None, init_oauth=None, swagger_ui_parameters=None)` → HTMLResponse | F-073 |
| `get_redoc_html` | `get_redoc_html(*, openapi_url, title, redoc_js_url=..., redoc_favicon_url=..., with_google_fonts=True)` → HTMLResponse | F-074 |
| `get_swagger_ui_oauth2_redirect_html` | `get_swagger_ui_oauth2_redirect_html()` → HTMLResponse | F-075 |

### 常量/字典
| 名称 | 说明 | 事实编号 |
|------|------|---------|
| `swagger_ui_default_parameters` | Swagger UI 默认配置：dom_id="#swagger-ui"、layout="BaseLayout"、deepLinking=True、showExtensions=True、showCommonExtensions=True | F-072 |

## 关键实现细节

### 从 _compat 导入的核心工具（F-067）
`get_definitions`/`get_flat_models_from_fields`/`get_model_name_map`/`get_schema_from_model_field` 等函数从 `fastapi._compat` 导入，Pydantic v2 兼容层隔离了版本差异。

### get_openapi_path 路径项生成（F-068）
- 返回 `tuple[dict, dict, dict]`（path/security_schemes/definitions）
- 遍历 `route.methods`
- 调用 `get_openapi_operation_metadata`、`_get_openapi_security_definitions`、`_get_openapi_operation_parameters`
- `METHODS_WITH_BODY` 方法调用 `get_openapi_operation_request_body`
- 递归处理 callbacks

### get_fields_from_routes 字段收集（F-069）
从路由收集 flat_params/body_field/response_field/stream_item_field/response_fields 等字段。

### get_openapi 生成管线（F-070）
`get_openapi(*, title, version, openapi_version="3.1.0", ...)` 执行流程：
1. 组装 info 字典
2. 调用 `get_fields_from_routes` → `get_flat_models_from_fields` → `get_model_name_map` → `get_definitions`
3. 遍历 routes 和 webhooks 调 `get_openapi_path`
4. 最终返回 `jsonable_encoder(OpenAPI(**output), by_alias=True, exclude_none=True)`

`separate_input_output_schemas=True` 参数控制输入/输出 schema 是否拆分，传递给 `get_definitions`。

### _html_safe_json XSS 防护（F-071）
`_html_safe_json(value)` 对 `json.dumps(value)` 结果替换：
- `<` → `\u003c`
- `>` → `\u003e`
- `&` → `\u0026`

### Swagger UI HTML 渲染（F-073）
`get_swagger_ui_html` 返回 HTMLResponse：
- 默认从 jsdelivr CDN 加载 swagger-ui-dist@5
- 合并默认参数后渲染 SwaggerUIBundle 初始化脚本
- 支持 OAuth2 redirect URL 和 init_oauth 配置

### ReDoc HTML 渲染（F-074）
`get_redoc_html` 返回 HTMLResponse：
- 默认从 jsdelivr CDN 加载 redoc@2 standalone
- 渲染 `<redoc spec-url=...>` 自定义元素
- 支持 with_google_fonts 选项

### OAuth2 Redirect 页面（F-075）
`get_swagger_ui_oauth2_redirect_html()` 返回内嵌 OAuth2 回调处理 JS 的 HTMLResponse。

### OpenAPI 模型层（F-076）
文件定义 40 个 Pydantic 模型类，包括：BaseModelWithConfig/Contact/License/Info/ServerVariable/Server/Reference/Discriminator/XML/ExternalDocumentation/Schema/Example/ParameterInType/Encoding/MediaType/ParameterBase/Parameter/Header/RequestBody/Link/Response/Operation/PathItem/SecuritySchemeType/SecurityBase/APIKeyIn/APIKey/HTTPBase/HTTPBearer/OAuthFlow*/OAuthFlows/OAuth2/OpenIdConnect/Components/Tag/OpenAPI。

### Schema 类 JSON Schema 覆盖（F-077）
`class Schema(BaseModelWithConfig)` 声明：
- **核心词汇**：$schema/$id/$ref/$defs/allOf/anyOf/oneOf/not/properties/items 等
- **结构验证词汇**：type/enum/const/multipleOf/maximum/minimum/maxLength/minLength/pattern/maxItems/required 等
- **语义内容词汇**：format/contentEncoding/contentMediaType/contentSchema
- **元数据词汇**：title/description/default/deprecated/readOnly/writeOnly/examples
- **OpenAPI 3.1.0 扩展**：discriminator/xml/externalDocs/example

### Parameter 与 Header（F-078）
- `class Parameter(ParameterBase)` 新增 `name: str` 和 `in_: ParameterInType = Field(alias="in")`（处理 Python 保留字 `in`）
- `class Header(ParameterBase)` 为空类

### OpenAPI 与 Components 顶层模型（F-079）
- `class OpenAPI(BaseModelWithConfig)` 为顶层文档模型
- `class Components(BaseModelWithConfig)` 包含 schemas/responses/parameters/securitySchemes/requestBases/headers 等字段

## 相关信源
- [applications.md](applications.md) — setup() 注册文档路由，openapi() 缓存机制
- [routing.md](routing.md) — _populate_api_route_state 提供路由元数据
- [responses-encoders.md](responses-encoders.md) — jsonable_encoder 用于最终序列化
- [params.md](params.md) — 参数类元数据驱动 schema 生成
