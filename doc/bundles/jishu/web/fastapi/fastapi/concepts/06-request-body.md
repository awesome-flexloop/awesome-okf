---
type: Concept
title: 请求体与数据验证
description: 详解 Body/Form/File 参数类继承体系、请求体 JSON 解析与 strict_content_type CSRF 防护、embed 嵌入机制、UploadFile 文件上传与 Pydantic 模型验证。
tags: [fastapi, request-body, body, form, file, uploadfile, pydantic]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/params.md
    title: FastAPI v0.141.1 源码信源
---

# 请求体与数据验证

请求体（Request Body）是客户端发送给 API 的数据载荷。FastAPI 通过 `Body`、`Form`、`File` 三个参数类声明请求体参数，它们构成独立的继承体系（不继承 `Param`，因为请求体没有 `in_` 位置语义）。框架根据参数类型和 Content-Type 自动选择解析策略，并通过 Pydantic v2 的 `TypeAdapter` 执行数据验证。本章还涉及 `strict_content_type` 的 CSRF 防护机制和 `UploadFile` 文件上传处理。

## Body 参数类

`Body` 直接继承 Pydantic 的 `FieldInfo`，而非 `Param`（F-045）。这是因为请求体参数不存在"位置"概念（不像 Path/Query/Header/Cookie 对应 HTTP 请求的特定位置），因此不需要 `in_` 类属性。`Body` 独有两个参数：

- **`embed: bool | None = None`**：是否将参数值嵌入到以参数名为键的 JSON 对象中。当端点有多个 `Body` 参数时，框架自动设置 `embed=True`，要求客户端发送 `{"param1": ..., "param2": ...}` 而非裸值。
- **`media_type: str = "application/json"`**：请求体的媒体类型，默认为 JSON。

`Body.__init__` 结构与 `Param` 类似，支持 default/alias/gt/ge/lt/le/min_length/max_length/pattern/strict/examples/json_schema_extra 等全部 Pydantic 字段参数（F-045）。

```python
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Annotated

class Item(BaseModel):
    name: str
    price: float

class User(BaseModel):
    username: str
    email: str

app = FastAPI()

@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0)] = 0,
):
    return {"item_id": item_id, "item": item, "user": user}
```

上述代码中有两个 Pydantic 模型参数和一个标量 Body 参数，框架自动启用 `embed_body_fields`，客户端需发送：

```json
{
  "item": {"name": "Book", "price": 9.99},
  "user": {"username": "alice", "email": "a@b.com"},
  "importance": 5
}
```

## Form 与 File 继承体系

`Form` 和 `File` 构成请求体参数的子类链：

```text
FieldInfo
  └── Body（media_type="application/json", embed）
        └── Form（media_type="application/x-www-form-urlencoded", 无 embed）
              └── File（media_type="multipart/form-data"）
```

**`Form(Body)`**（F-046）：默认 `media_type = "application/x-www-form-urlencoded"`，无 `embed` 参数。用于 HTML 表单提交的键值对数据。使用 `Form` 参数时，框架调用 `ensure_multipart_is_installed()` 检查 `python-multipart` 依赖（F-057）。

**`File(Form)`**（F-047）：默认 `media_type = "multipart/form-data"`。用于文件上传，通常与 `UploadFile` 类型注解配合使用。`File` 继承自 `Form` 而非 `Body`，因为文件上传本质上是 multipart 表单提交的一种形式。

```python
from fastapi import FastAPI, File, Form, UploadFile
from typing import Annotated

app = FastAPI()

@app.post("/upload/")
async def upload_file(
    file: Annotated[UploadFile, File()],
    description: Annotated[str, Form()] = "",
):
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "description": description,
    }
```

## 请求体解析流程

请求体解析在 `get_request_handler` 返回的内部协程中执行（F-024），根据参数类型和 Content-Type 分支处理：

**表单请求**（`is_body_form` 为真，即端点包含 `Form` 或 `File` 参数）：
1. 调用 `await request.form()` 解析 `application/x-www-form-urlencoded` 或 `multipart/form-data` 数据
2. 注册 `body.close` 回调确保底层资源释放

**非表单请求**（JSON 等）：
1. 读取 `body_bytes = await request.body()` 获取原始字节
2. 检查 Content-Type：主类型为 `application` 且子类型为 `json` 或以 `+json` 结尾时，调用 `json.loads(body_bytes)` 解析
3. 其他 Content-Type 保留原始字节，交由 Pydantic 模型自行处理

**strict_content_type CSRF 防护**：当应用构造时 `strict_content_type=True`，若请求缺少 Content-Type 头，则不解析 JSON 请求体。这一设计防止跨站请求伪造（CSRF）——浏览器在某些跨域简单请求（如表单提交）中可能不发送 `application/json` Content-Type，不解析 JSON 体可避免恶意网站利用简单请求触发状态变更端点。

```python
from fastapi import FastAPI

app = FastAPI(strict_content_type=True)

@app.post("/webhook/")
async def webhook(payload: dict):
    return payload
```

在上述配置下，不带 Content-Type 头的 POST 请求不会解析 JSON body，从而返回 422 校验错误而非处理恶意载荷。

## Pydantic 模型验证

请求体数据解析后，通过 `ModelField` 桥接到 Pydantic v2 验证。`ModelField` 在 `__post_init__` 中通过 `asdict(field_info)` 构造 `Annotated` 注解并创建 `TypeAdapter`（F-133），其 `validate` 方法返回 `(value, errors)` 元组而非直接抛异常。

这种"返回错误而非抛出"的设计使得框架能够聚合多个参数（路径、查询、请求体）的校验错误后一次性返回 `RequestValidationError`（422 响应），而不是在第一个错误处中断。验证通过的值经 `field.serialize` 或 `field.serialize_json` 序列化为端点函数可用的 Python 对象。

Pydantic 模型支持嵌套定义、字段校验器（`@field_validator`）、模型校验器（`@model_validator`）等全部 v2 功能。非标量类型注解（Pydantic 模型、dataclass、TypedDict 等）在未显式声明时自动推断为 `Body` 参数（F-061）。

```python
from pydantic import BaseModel, Field, field_validator

class Item(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    tags: list[str] = []

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        return v.strip()
```

## UploadFile 文件上传

`UploadFile` 继承自 Starlette 的 `StarletteUploadFile`（F-112），在 FastAPI 中增加了 Pydantic 集成：

**类注解属性**：`file`、`filename`、`size`、`headers`、`content_type`。

**异步方法**：`async write(data)`、`async read(size)`、`async seek(offset)`、`async close()`，均委托 `super()` 实现。

**Pydantic v2 集成**：
- `__get_pydantic_json_schema__` 返回 `{"type": "string", "contentMediaType": "application/octet-stream"}`，使 OpenAPI schema 将 UploadFile 表示为二进制字符串
- `__get_pydantic_core_schema__` 调用 `with_info_plain_validator_function(cls._validate)` 注册自定义验证器
- `_validate` 类方法断言输入是 `StarletteUploadFile` 实例

```python
from fastapi import FastAPI, UploadFile, File
from typing import Annotated

app = FastAPI()

@app.post("/files/")
async def create_file(
    file: Annotated[UploadFile, File(description="The file to upload")],
):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
```

`UploadFile` 使用 SpooledTemporaryFile——文件内容先存于内存，超过阈值后写入磁盘临时文件，避免大文件耗尽内存。可通过 `await file.read()` 读取全部内容，或通过 `async for` 分块读取。

## multipart 依赖检测

`ensure_multipart_is_installed()` 在首次使用 `Form` 或 `File` 参数时调用（F-057），检测流程：

1. 尝试导入 `python_multipart.__version__`，断言版本 > "0.0.12"
2. 失败时尝试导入 `multipart` 包（python-multipart 的替代包名）
3. 若检测到错误的 `multipart` 包（非 python-multipart），抛出 `RuntimeError` 提示安装正确的包

这是 FastAPI 对可选依赖的延迟检测策略——仅在实际使用表单/文件功能时才要求安装 `python-multipart`，不使用时无需安装。

## 数据结构再导出

`fastapi.datastructures` 模块从 Starlette 重新导出常用数据结构（F-111）：`URL`、`Address`、`FormData`、`Headers`、`QueryParams`、`State`，并导入 `UploadFile as StarletteUploadFile` 作为 FastAPI 版 `UploadFile` 的基类。

值得注意的是，v0.141 中不存在 `StreamUploadFile` 类和 `_Wrapper` 类（F-114，经全目录 grep 确认），这些是旧版本或其他分支中的概念，在本文档对应版本中不适用。

## RequestValidationError

当请求体验证失败时，框架抛出 `RequestValidationError`（F-105），它继承自 `ValidationException`，包含：
- `_errors`：校验错误列表
- `body`：原始请求体数据（用于调试）
- `endpoint_ctx`：端点上下文信息（函数名、文件、行号）
- `errors()` 方法：返回格式化的错误列表

默认异常处理器 `request_validation_exception_handler`（F-010）返回 422 状态码，响应体包含错误详情数组。用户可通过 `@app.exception_handler(RequestValidationError)` 自定义错误响应格式。

## 相关概念

- [参数声明系统](05-parameter-declaration.md)
- [路径操作与请求处理](03-path-operations.md)
- [依赖注入系统](04-dependency-injection.md)
- [路由系统](02-routing-system.md)
