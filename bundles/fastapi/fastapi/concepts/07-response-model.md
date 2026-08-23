---
type: Concept
title: 响应模型与序列化
description: 详解 response_model 参数、serialize_response 序列化管线、ResponseValidationError、response_model_include/exclude 过滤、separate_input_output_schemas、响应类体系与 jsonable_encoder 编码管线。
tags: [fastapi, response-model, serialization, jsonable-encoder, response, pydantic]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/responses-encoders.md
    title: FastAPI v0.141.1 源码信源
---

# 响应模型与序列化

响应模型（Response Model）是 FastAPI 将端点返回值转换为 HTTP 响应体的核心机制。通过 `response_model` 参数声明输出 schema，框架自动完成数据校验、字段过滤和 JSON 序列化。与请求体验证类似，响应序列化也通过 Pydantic v2 的 `TypeAdapter` 桥接执行，但有一个关键区别：响应校验失败会抛出 `ResponseValidationError`（服务端错误），而非 `RequestValidationError`（客户端错误）。本章还涉及响应类继承体系、`jsonable_encoder` 通用编码器和响应字段过滤参数。

## response_model 参数

`response_model` 在路由注册时通过 `add_api_route` 或路径操作装饰器传入（F-015, F-030）。`_populate_api_route_state` 函数接收 `response_model` 参数并将其设置到 `APIRoute` 实例上（F-030）。当 `response_model` 非空时，框架通过 `create_model_field` 创建一个 `response_field`（类型为 `ModelField`），用于后续的响应校验和序列化。

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    secret: str

app = FastAPI()

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    return {"name": "Book", "price": 9.99, "secret": "hidden"}
```

上述代码中，端点返回的字典包含 `secret` 字段，但如果 `Item` 模型未声明该字段，Pydantic 默认会忽略额外字段。更精确的字段过滤通过 `response_model_include` 和 `response_model_exclude` 实现。

## serialize_response 序列化函数

`serialize_response` 是响应序列化的核心函数（F-020），签名如下：

```python
async def serialize_response(
    *,
    field: ModelField | None = None,
    response_content: Any,
    include: IncEx | None = None,
    exclude: IncEx | None = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    is_coroutine: bool = True,
    endpoint_ctx: EndpointContext | None = None,
    dump_json: bool = False,
) -> Any:
```

函数逻辑分为两个分支：

**有 field（声明了 response_model）**：
1. 调用 `field.validate(response_content)` 执行校验，协程通过 `run_in_threadpool` 在线程池中执行以避免阻塞事件循环
2. 若返回的 `errors` 非空，抛出 `ResponseValidationError`，携带 errors、原始 response_content 和 endpoint_ctx
3. 校验通过后，根据 `dump_json` 参数选择序列化方法：
   - `dump_json=True`：调用 `field.serialize_json(value, include=..., exclude=..., by_alias=..., exclude_unset=..., exclude_defaults=..., exclude_none=...)` 返回 `bytes`
   - `dump_json=False`：调用 `field.serialize(value, ...)` 返回 Python 对象（通常是 dict）

**无 field（未声明 response_model）**：
- 直接返回 `jsonable_encoder(response_content, include=..., exclude=..., by_alias=..., exclude_unset=..., exclude_defaults=..., exclude_none=...)`

`dump_json` 快速路径在响应类为默认 `JSONResponse` 时启用——直接生成 JSON bytes 并包装为 `Response(content, media_type="application/json")`，跳过二次编码（F-027）。

## ResponseValidationError

`ResponseValidationError` 继承自 `ValidationException`（F-105），在响应数据校验失败时抛出。与 `RequestValidationError` 不同，它表示服务端代码返回了不符合声明 schema 的数据，属于服务端编程错误。该异常携带：
- `_errors`：校验错误列表
- `body`：原始响应内容（用于调试）
- `endpoint_ctx`：端点上下文（函数名、文件、行号、路径）

默认情况下，`ResponseValidationError` 会被 `ServerErrorMiddleware` 捕获并返回 500 错误。开发者应确保端点返回值始终符合 `response_model` 声明。

## 响应字段过滤参数

`add_api_route` 和路径操作装饰器支持六个序列化控制参数（F-015, F-030）：

| 参数 | 类型 | 默认值 | 作用 |
|------|------|--------|------|
| `response_model_include` | `IncEx \| None` | `None` | 只序列化指定字段 |
| `response_model_exclude` | `IncEx \| None` | `None` | 排除指定字段 |
| `response_model_by_alias` | `bool` | `True` | 是否使用字段别名序列化 |
| `response_model_exclude_unset` | `bool` | `False` | 排除未显式设置的字段 |
| `response_model_exclude_defaults` | `bool` | `False` | 排除等于默认值的字段 |
| `response_model_exclude_none` | `bool` | `False` | 排除值为 `None` 的字段 |

这些参数透传到 `field.serialize`/`field.serialize_json` 或 `jsonable_encoder`。`IncEx` 类型可以是字段名集合或嵌套字典，实现深度字段过滤：

```python
@app.get(
    "/items/{item_id}",
    response_model=Item,
    response_model_exclude={"secret"},
    response_model_exclude_none=True,
)
async def read_item(item_id: int):
    return Item(name="Book", price=9.99, secret="hidden", description=None)
```

## separate_input_output_schemas

`separate_input_output_schemas` 是 `FastAPI.__init__` 的参数（F-007），默认为 `True`，控制 OpenAPI schema 生成时是否分离输入和输出模型。当设为 `True` 时，`get_definitions` 使用 Pydantic v2 的 `GenerateJsonSchema` 按 validation 模式和 serialization 模式分别生成 schema（F-134）。

这一机制解决了输入输出字段不一致的场景。例如，用户模型在创建时不需要 `id`（数据库自动生成），但在响应中必须包含 `id`。通过 `Field(..., json_schema_extra={"mode": "input"})` 或 `response_model` 与请求模型分离，框架能在 OpenAPI 文档中正确区分请求 schema 和响应 schema。

## 响应类体系

FastAPI 从 Starlette 重新导出全部响应类（F-095）：

```text
Response
├── HTMLResponse
├── PlainTextResponse
├── JSONResponse
│   ├── UJSONResponse（@deprecated，F-097）
│   └── ORJSONResponse（@deprecated，F-098）
├── RedirectResponse
├── StreamingResponse
│   └── EventSourceResponse（SSE，F-123）
└── FileResponse
```

`default_response_class` 参数控制全局默认响应类（F-007），默认为 `Default(JSONResponse)`。`Default(value)` 返回 `DefaultPlaceholder` 实例（F-113），用于延迟解析默认值——这允许路由级 `response_class` 覆盖应用级默认值，而无需在路由定义时引用应用实例。

当端点直接返回 `Response` 实例时，框架跳过序列化直接使用该实例，但会注入 `background_tasks`（如果有）（F-027）。这允许开发者完全控制响应：

```python
from fastapi import Response

@app.get("/custom")
async def custom():
    return Response(content=b"raw bytes", media_type="application/octet-stream")
```

## is_body_allowed_for_status_code

`is_body_allowed_for_status_code(status_code)` 函数判断指定状态码是否允许包含响应体（F-115）：

- `None`、`"default"`、`"1XX"`、`"2XX"`、`"3XX"`、`"4XX"`、`"5XX"` 返回 `True`
- 整数状态码 `< 200` 返回 `False`
- 状态码 `204`（No Content）、`205`（Reset Content）、`304`（Not Modified）返回 `False`
- 其余返回 `True`

当状态码不允许 body 时，非流式分支设置 `response.body = b""`（F-027），确保符合 HTTP 规范。

## jsonable_encoder

`jsonable_encoder` 是 FastAPI 的通用 JSON 编码器（F-110），在没有 `response_field` 时用于序列化任意 Python 对象。其处理管线按优先级依次执行：

1. **custom_encoder**：用户传入的自定义编码器字典优先匹配
2. **Pydantic BaseModel**：调用 `model_dump(mode="json")`
3. **dataclass**：通过 `dataclasses.asdict` 转换
4. **Enum**：返回 `.value`
5. **PurePath**：返回 `str(obj)`
6. **原始类型**：str/int/float/bool/None 直接返回
7. **PydanticUndefinedType**：返回 `None`
8. **dict**：递归编码每个键值
9. **list/set/frozenset/GeneratorType/tuple/deque**：递归编码每个元素
10. **ENCODERS_BY_TYPE**：查注册表匹配特定类型编码器
11. **兜底**：尝试 `dict(obj)`，再尝试 `vars(obj)`

`ENCODERS_BY_TYPE` 字典注册了常见类型的编码器（F-107），包括 `bytes`、`datetime`/`date`/`time`/`timedelta`、`Decimal`、`Enum`、`IPv4Address`/`IPv6Address`、`UUID`、`Path`、`SecretStr`/`SecretBytes`、`Url` 等。`decimal_encoder` 根据 `as_tuple().exponent` 判断：指数 >= 0 返回 `int`，否则返回 `float`（F-108）。

`generate_encoders_by_class_tuples` 将 type→encoder 映射反转为 encoder→tuple(types) 以加速类继承查找（F-109）。Pydantic v1 实例会抛出 `PydanticV1NotSupportedError`（F-110）。

## 相关概念

- [路径操作与请求处理](/concepts/03-path-operations.md)
- [流式响应与 WebSocket](/concepts/12-streaming-websocket.md)
- [OpenAPI 文档生成](/concepts/08-openapi-generation.md)
- [参数声明系统](/concepts/05-parameter-declaration.md)
- [异常处理与校验错误](/concepts/11-exception-handling.md)
