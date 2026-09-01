---
type: Concept
title: OpenAPI 文档自动生成
description: 详解 openapi() 方法的版本缓存机制、get_openapi 生成管线、get_openapi_path 路径项提取、operationId 生成、callbacks/webhooks、setup() 四个文档路由注册与 Swagger UI/ReDoc 配置。
tags: [fastapi, openapi, swagger, redoc, documentation, schema]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/openapi.md
    title: FastAPI v0.141.1 源码信源
---

# OpenAPI 文档自动生成

FastAPI 的 OpenAPI 文档完全从路由签名和 Pydantic 模型自动推导，无需手写 YAML 或 JSON Schema。框架在应用构造时设置 OpenAPI 版本为 `"3.1.0"`（F-008），通过路由版本号增量缓存 schema，仅在路由增删时重新生成。内置 Swagger UI 和 ReDoc 两种交互式文档 UI，在 `setup()` 阶段自动注册四个文档路由。本章从缓存机制、生成管线、路径项提取到 UI 渲染逐层解析。

## openapi() 方法与版本缓存

`FastAPI.openapi()` 方法是 OpenAPI schema 的入口（F-012），实现懒加载与增量缓存：

```python
def openapi(self) -> dict:
    if not self.openapi_schema:
        self.openapi_schema = get_openapi(...)
        self._openapi_routes_version = self.router._get_routes_version()
    elif self._openapi_routes_version != self.router._get_routes_version():
        self.openapi_schema = get_openapi(...)
        self._openapi_routes_version = self.router._get_routes_version()
    return self.openapi_schema
```

缓存逻辑追踪三个状态（F-008）：
- `self.openapi_schema = None`：初始未生成
- `self._openapi_routes_version = None`：上次生成时的路由版本
- `self.openapi_version = "3.1.0"`：OpenAPI 规范版本

`self.router._get_routes_version()` 返回路由列表的版本号。`add_api_route` 创建路由后调用 `_mark_routes_changed()` 递增版本号（F-036），使缓存失效。这一设计确保添加或删除路由时 schema 自动更新，而无需手动刷新。

## get_openapi 生成管线

`get_openapi` 函数组装完整的 OpenAPI 文档（F-070），接收以下关键字参数：

- `title`、`version`：API 标题和版本（必填）
- `openapi_version="3.1.0"`：OpenAPI 规范版本
- `summary`、`description`、`terms_of_service`：API 元数据
- `contact`、`license_info`：联系人和许可证信息
- `routes`：路由列表（必填）
- `webhooks=None`：Webhook 路由
- `tags=None`：标签列表
- `servers=None`：服务器列表
- `separate_input_output_schemas=True`：是否分离输入输出 schema
- `external_docs=None`：外部文档链接

生成管线执行顺序：

1. 组装 `info` 字典（title/version/summary/description/termsOfService/contact/license）
2. `get_fields_from_routes(...)` 从所有路由收集字段（F-069）：`flat_params`、`body_field`、`response_field`、`stream_item_field`、`response_fields`
3. `get_flat_models_from_fields(...)` 从字段中提取所有关联的 Pydantic 模型
4. `get_model_name_map(...)` 生成模型名称映射（处理同名模型）
5. `get_definitions(...)` 使用 Pydantic v2 的 `GenerateJsonSchema` 生成 JSON Schema 定义，按 validation/serialization 模式拆分字段（F-134），截断 description 中 `\f` 之后的内容
6. 遍历 `routes` 调用 `get_openapi_path(...)` 生成每个路径项
7. 遍历 `webhooks` 同样调用 `get_openapi_path(...)` 生成 webhook 定义
8. 最终调用 `jsonable_encoder(OpenAPI(**output), by_alias=True, exclude_none=True)` 序列化为可 JSON 化的字典

## get_openapi_path 路径项生成

`get_openapi_path` 从单个 `APIRoute` 提取 OpenAPI 路径项（F-068），返回三元组 `(path_dict, security_schemes, definitions)`：

```python
def get_openapi_path(
    *,
    route,
    operation_ids,
    model_name_map,
    field_mapping,
    separate_input_output_schemas=True,
) -> tuple[dict, dict, dict]:
```

对 `route.methods` 中的每个 HTTP 方法：
1. 调用 `get_openapi_operation_metadata` 提取 summary/description/deprecated/operationId/tags 等元数据
2. 调用 `_get_openapi_security_definitions` 提取安全方案
3. 调用 `_get_openapi_operation_parameters` 生成 path/query/header/cookie 参数列表
4. 对 `METHODS_WITH_BODY`（POST/PUT/PATCH/DELETE）调用 `get_openapi_operation_request_body` 生成 requestBody
5. 递归处理 `route.callbacks` 中的回调路由

`description` 从端点函数的 docstring 提取，使用 `inspect.cleandoc` 清理缩进，并按 `\f`（换页符）截断（F-030）。这允许在 docstring 中写入长篇文档但只将 `\f` 之前的部分用于 OpenAPI。

## operationId 与 unique_id

每个路径操作需要唯一的 `operationId`。`_populate_api_route_state` 支持路由级 `operation_id` 参数（F-030）。若未显式指定，使用 `generate_unique_id_function`（默认为 `generate_unique_id`）自动生成（F-118）：

```python
def generate_unique_id(route: APIRoute) -> str:
    return (
        re.sub(r"\W", "_", f"{route.name}{route.path_format}")
        + "_"
        + list(route.methods)[0].lower()
    )
```

该函数将路由名和路径格式中的非单词字符替换为下划线，追加 HTTP 方法名。例如路由名 `read_item`、路径 `/items/{item_id}`、方法 `GET` 生成 `read_item_items_item_id_get`。

用户可通过 `generate_unique_id_function` 参数自定义 ID 生成策略（F-007, F-015），实现更简洁或符合团队命名规范的 operationId。`operation_ids` 集合在 `get_openapi_path` 中用于检测重复 ID。

## callbacks 与 webhooks

FastAPI 支持两种异步回调机制：

**callbacks**（F-007, F-030）：在路由注册时通过 `callbacks` 参数传入 `APIRouter` 实例，定义该操作可能触发的回调请求。OpenAPI 中在 operation 对象的 `callbacks` 字段生成回调定义，`get_openapi_path` 递归处理回调路由。

**webhooks**（F-009）：应用级 webhook 路由通过 `FastAPI.__init__` 的 `webhooks` 参数传入，内部创建独立的 `APIRouter` 实例（`self.webhooks = webhooks or routing.APIRouter()`）。与 callbacks 不同，webhooks 是应用全局的出站 webhook 定义，不绑定到特定操作。`get_openapi` 单独遍历 webhooks 路由并在顶层 `webhooks` 字段生成定义。

```python
webhook_router = APIRouter()

@webhook_router.post("/webhook")
async def webhook_received(data: dict):
    pass

app = FastAPI(webhooks=webhook_router)
```

## setup() 文档路由注册

`setup()` 方法在应用首次接收请求时（由 Starlette 触发）注册四个文档路由（F-013），均设置 `include_in_schema=False` 避免自引用：

| 路由 | 默认路径 | 响应 | 说明 |
|------|---------|------|------|
| openapi_url | `/openapi.json` | `JSONResponse` | OpenAPI schema JSON |
| docs_url | `/docs` | `get_swagger_ui_html` | Swagger UI 交互式文档 |
| swagger_ui_oauth2_redirect_url | `/docs/oauth2-redirect` | `get_swagger_ui_oauth2_redirect_html` | OAuth2 回调页面 |
| redoc_url | `/redoc` | `get_redoc_html` | ReDoc 文档 |

所有 URL 均可通过构造参数自定义，设为 `None` 可禁用对应路由。例如 `docs_url=None` 关闭 Swagger UI，`redoc_url=None` 关闭 ReDoc。

## Swagger UI 配置

`get_swagger_ui_html` 生成 Swagger UI HTML 页面（F-073），参数包括：

- `openapi_url`：OpenAPI schema 的 URL
- `title`：页面标题
- `swagger_js_url`：Swagger UI Bundle JS（默认 jsdelivr CDN 的 swagger-ui-dist@5）
- `swagger_css_url`：Swagger UI CSS（同版本）
- `swagger_favicon_url`：网站图标
- `oauth2_redirect_url`：OAuth2 重定向 URL
- `init_oauth`：OAuth2 初始化配置（对应 `swagger_ui_init_oauth` 应用参数）
- `swagger_ui_parameters`：Swagger UI 初始化参数（对应应用构造参数）

`swagger_ui_default_parameters` 字典提供默认值（F-072）：`dom_id="#swagger-ui"`、`layout="BaseLayout"`、`deepLinking=True`、`showExtensions=True`、`showCommonExtensions=True`。用户传入的 `swagger_ui_parameters` 与默认值合并。

`_html_safe_json` 函数对 JSON 输出中的 `<`、`>`、`&` 进行 Unicode 转义（F-071），防止 XSS 攻击。

## ReDoc 配置

`get_redoc_html` 生成 ReDoc HTML 页面（F-074），参数较 Swagger UI 简洁：

- `openapi_url`：schema URL
- `title`：页面标题
- `redoc_js_url`：ReDoc JS（默认 jsdelivr CDN 的 redoc@2 standalone）
- `redoc_favicon_url`：网站图标
- `with_google_fonts=True`：是否加载 Google Fonts

ReDoc 渲染为 `<redoc spec-url="...">` 自定义元素，由 ReDoc JS 自动升级为完整文档界面。

## 应用级元数据

`FastAPI.__init__` 接收一系列 OpenAPI 元数据参数（F-007），透传到 `get_openapi`：

- `title`（默认 `"FastAPI"`）、`version`（默认 `"0.1.0"`）
- `summary`、`description`
- `terms_of_service`：服务条款 URL
- `contact`：联系人信息字典（name/url/email）
- `license_info`：许可证信息字典（name/url）
- `openapi_tags`：标签元数据列表（每个标签含 name/description/externalDocs）
- `servers`：服务器列表
- `openapi_external_docs`：外部文档链接（url/description）

这些元数据填充 OpenAPI 文档的 `info`、`tags`、`servers` 和 `externalDocs` 字段。

## OpenAPI 模型层

`openapi/models.py` 定义了 40 个 Pydantic 模型类（F-076），构成 OpenAPI 3.1.0 规范的类型安全表示。核心类包括：

- `Schema`（F-077）：覆盖 JSON Schema 2020-12 全部核心词汇（`$schema`/`$id`/`$ref`/`$defs`/`allOf`/`anyOf`/`oneOf` 等）、结构验证词汇（type/enum/const/maximum/minimum/maxLength 等）、语义内容词汇（format/contentEncoding/contentMediaType）、元数据词汇（title/description/default/deprecated/readOnly/writeOnly/examples）以及 OpenAPI 特有的 discriminator/xml/externalDocs/example
- `Parameter`（F-078）：新增 `name: str` 和 `in_: ParameterInType = Field(alias="in")`，用 alias 处理 Python 保留字 `in`
- `OpenAPI`（F-079）：顶层文档模型
- `Components`（F-079）：包含 schemas/responses/parameters/securitySchemes/requestBodies/headers 等字段

`deep_dict_update` 工具函数递归合并字典（list 拼接，其余键覆盖）（F-119），用于合并路由级和应用级 responses/tags 等配置。

## 相关概念

- [响应模型与序列化](07-response-model.md)
- [路径操作与请求处理](03-path-operations.md)
- [安全与认证](09-security.md)
- [FastAPI 应用类与生命周期](01-application.md)
- [路由系统](02-routing-system.md)
