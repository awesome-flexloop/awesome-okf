---
type: Concept
title: 参数声明系统
description: 详解 ParamTypes 枚举、Param/Path/Query/Header/Cookie 参数类继承体系、Pydantic FieldInfo 元数据复用、校验约束、别名机制与 Annotated 类型注解写法。
tags: [fastapi, parameters, field-info, pydantic, validation]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/params.md
    title: FastAPI v0.141.1 源码信源
---

# 参数声明系统

FastAPI 的参数声明系统是"类型注解即校验、校验即文档"设计哲学的核心载体。参数类（`Path`/`Query`/`Header`/`Cookie`）继承自 Pydantic v2 的 `FieldInfo`，使参数默认值、校验约束、JSON Schema 元数据和 OpenAPI 文档生成共用同一个元数据对象。开发者通过 `Annotated[..., Query(...)]` 声明一次，框架同时完成运行时校验、schema 生成和 IDE 类型推断。

## ParamTypes 枚举

`ParamTypes` 定义参数在 HTTP 请求中的位置（F-038）：

```python
class ParamTypes(Enum):
    query = "query"
    header = "header"
    path = "path"
    cookie = "cookie"
```

四个成员对应 HTTP 请求的四个参数来源：URL 查询字符串、请求头、URL 路径、Cookie。每个 `Param` 子类通过类属性 `in_` 声明自己的位置。

## Param 基类

`Param` 继承 Pydantic 的 `FieldInfo`（F-039），是所有位置参数类的基类：

```python
class Param(FieldInfo):
    in_: ParamTypes
```

`__init__` 支持完整的 Pydantic 字段参数：

- **默认值**：`default`、`default_factory`、`annotation`
- **别名**：`alias`、`alias_priority`、`validation_alias`、`serialization_alias`
- **元数据**：`title`、`description`、`examples`、`example`、`openapi_examples`、`deprecated`、`include_in_schema`、`json_schema_extra`
- **数值校验**：`gt`（大于）、`ge`（大于等于）、`lt`（小于）、`le`（小于等于）、`multiple_of`、`allow_inf_nan`、`max_digits`、`decimal_places`
- **字符串校验**：`min_length`、`max_length`、`pattern`、`regex`
- **其他**：`discriminator`、`strict`、`**extra`

**弃用警告**（F-040）：`example` 参数（非 `examples`）非 `_Unset` 时发出 `FastAPIDeprecationWarning`；`regex` 参数非空时同样发出弃用警告，内部映射为 `kwargs["pattern"] = pattern or regex`。推荐使用 `examples`（复数）和 `pattern`。

## 四个位置参数类

### Path 类

`Path(Param)` 设置 `in_ = ParamTypes.path`（F-041），并在 `__init__` 中断言默认值必须为空：

```python
class Path(Param):
    in_ = ParamTypes.path

    def __init__(self, default=..., **kwargs):
        assert default is ..., "Path parameters cannot have a default value"
```

路径参数是 URL 的一部分，必须有值，因此不允许默认值。使用 `...`（Ellipsis）作为占位符表示必填。

### Query 类

`Query(Param)` 设置 `in_ = ParamTypes.query`（F-042），`default` 默认为 `Undefined`（即 Pydantic v2 的 `PydanticUndefined`，F-132），表示必填查询参数。提供默认值（包括 `None`）则变为可选。

### Header 类

`Header(Param)` 设置 `in_ = ParamTypes.header`（F-043），独有参数 `convert_underscores: bool = True`。HTTP 头名称通常使用连字符（如 `X-API-Key`），而 Python 标识符不允许连字符。`convert_underscores=True` 时，参数名中的下划线自动转换为连字符来匹配头名称。

```python
from fastapi import FastAPI, Header
from typing import Annotated

app = FastAPI()

@app.get("/items/")
async def read_items(x_api_key: Annotated[str | None, Header()] = None):
    return {"x-api-key": x_api_key}
```

上述代码中 `x_api_key` 参数自动匹配请求头 `X-Api-Key`。

### Cookie 类

`Cookie(Param)` 设置 `in_ = ParamTypes.cookie`（F-044），用于声明 Cookie 参数，用法与 Query 类似。

## Body 类的独立分支

`Body` 不继承 `Param`，而是直接继承 `FieldInfo`（F-045），因为请求体没有 `in_` 位置语义。`Body` 独有两个属性：

- `embed: bool | None = None`：是否将参数嵌入到以参数名为键的 JSON 对象中
- `media_type: str = "application/json"`：请求体媒体类型

`Form` 继承 `Body`，默认 `media_type = "application/x-www-form-urlencoded"`，无 `embed` 参数（F-046）。`File` 继承 `Form`，默认 `media_type = "multipart/form-data"`（F-047）。这三个类构成请求体参数体系，详见 [请求体与数据验证](06-request-body.md)。

## 工厂函数与 Annotated 写法

`param_functions.py` 定义九个工厂函数，每个返回对应 `params.*` 类实例（F-050）：`Path()`、`Query()`、`Header()`、`Cookie()`、`Body()`、`Form()`、`File()`、`Depends()`、`Security()`。

工厂函数签名使用 `Annotated[..., Doc(...)]` 为每个参数附加文档字符串（F-051），部分参数附加 `deprecated(...)` 装饰器。这使得函数签名本身即携带完整的参数文档，IDE 可直接展示。

v0.141 推荐使用 `Annotated` 写法声明参数：

```python
from fastapi import FastAPI, Query
from typing import Annotated

app = FastAPI()

@app.get("/items/")
async def list_items(
    q: Annotated[
        str | None,
        Query(
            title="Search query",
            description="Full-text search query string",
            min_length=3,
            max_length=50,
            pattern=r"^[a-zA-Z0-9 ]+$",
        ),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return {"q": q, "limit": limit}
```

`Annotated` 写法的优势在于元数据与类型注解绑定，可复用为类型别名：

```python
SearchQuery = Annotated[str, Query(min_length=3, max_length=50)]

@app.get("/search")
async def search(q: SearchQuery):
    return {"q": q}
```

## 校验约束

参数类支持完整的 Pydantic v2 校验约束，这些约束同时作用于运行时校验和 OpenAPI schema 生成：

**数值约束**：`gt`（>）、`ge`（>=）、`lt`（<）、`le`（<=）、`multiple_of`、`max_digits`、`decimal_places`、`allow_inf_nan`。

**字符串约束**：`min_length`、`max_length`、`pattern`（正则表达式，替代已弃用的 `regex`）。

**严格模式**：`strict=True` 时启用 Pydantic 严格模式，禁止类型强制转换（如字符串 `"123"` 不会自动转为整数 `123`）。

校验失败时，框架聚合所有参数的错误后一次性抛出 `RequestValidationError`，返回 422 响应并附带每个错误的位置、类型和消息。

## 别名机制

FastAPI 参数支持多层级别名控制：

- **`alias`**：同时设置验证别名和序列化别名。参数在请求中的名称与 Python 变量名不同时使用。
- **`alias_priority`**：别名优先级，控制多个别名来源冲突时的取舍。
- **`validation_alias`**：仅用于验证（从请求中取值）的别名，不影响序列化。
- **`serialization_alias`**：仅用于序列化（输出到响应）的别名，不影响验证。

```python
from fastapi import Query
from typing import Annotated

@app.get("/items/")
async def read_items(
    item_id: Annotated[int, Query(alias="item-id", validation_alias="itemId")] = 1,
):
    return {"item_id": item_id}
```

## include_in_schema 控制

`include_in_schema` 参数（默认为 `True`）控制参数是否出现在 OpenAPI 文档中。设为 `False` 时参数仍可正常接收值，但不在生成的 schema 中显示，适用于内部参数或调试参数。

## 自动参数推断

当参数未显式使用 `Query()`/`Path()` 等声明时，`analyze_param` 函数按规则自动推断参数类型（F-061）：

| 条件 | 推断结果 |
|------|---------|
| 参数在路径模板中（`is_path_param=True`） | `Path` |
| 类型注解为 `UploadFile` | `File` |
| 非标量类型（Pydantic 模型、dataclass 等） | `Body` |
| 标量类型（int/str/float/bool/Decimal 等） | `Query` |

`add_param_to_fields` 函数按 `field.field_info.in_` 将字段分发到 `path_params`/`query_params`/`header_params`/`cookie_params` 列表（F-062）。

## ModelField 桥接

FastAPI 内部通过 `create_model_field(name, type_, default, field_info, alias, mode)` 创建 `ModelField` 实例（F-117）。该函数检测 Pydantic v1 并抛 `PydanticV1NotSupportedError`，捕获 `PydanticSchemaGenerationError` 转为 `FastAPIError`。

`ModelField` 类（F-133）在 `__post_init__` 中通过 `asdict(field_info)` 构造 `Annotated` 注解并创建 Pydantic v2 的 `TypeAdapter`，对外提供三个方法：

- `validate(value)` → `(value, errors)`：校验值，返回值与错误列表元组（不直接抛异常，以支持多参数错误聚合）
- `serialize(value)` → Python 对象：序列化为字典
- `serialize_json(value)` → `bytes`：序列化为 JSON 字节

`Undefined` 和 `RequiredParam` 均等于 Pydantic v2 的 `PydanticUndefined`（F-132），统一表示未提供值的状态。

## 类型判断工具

`_compat/shared` 模块提供一系列类型判断函数（F-137）：

- `field_annotation_is_scalar`：是否为标量类型
- `field_annotation_is_scalar_sequence`：是否为标量序列（如 `list[int]`）
- `field_annotation_is_sequence`：是否为序列类型
- `is_uploadfile_or_nonable_uploadfile_annotation`：是否为 UploadFile
- `is_bytes_or_nonable_bytes_annotation`：是否为 bytes

`sequence_types` 元组包含 `Sequence`/`list`/`tuple`/`set`/`frozenset`/`deque`（F-135），`sequence_annotation_to_type` 映射将其统一为可序列化的类型（如 `deque`→`list`）。

`lenient_issubclass(cls, class_or_tuple)`（F-136）是 `issubclass` 的安全版本：在 `isinstance(cls, type)` 为真时才调用 `issubclass`，对 `WithArgsTypes`（如 `List[int]` 等泛型实例）返回 `False`，其他 `TypeError` 重新抛出。

## 相关概念

- [请求体与数据验证](06-request-body.md)
- [依赖注入系统](04-dependency-injection.md)
- [路径操作与请求处理](03-path-operations.md)
- [路由系统](02-routing-system.md)
