---
type: Reference
title: responses-encoders — FastAPI 源码信源
description: 响应类、JSON 编码器、数据结构、通用工具、SSE 流式响应、后台任务及 Pydantic v2 兼容层的完整实现
tags: [fastapi, source, responses, encoders, sse, compat]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/responses-encoders.md
    title: FastAPI v0.141.1 源码
---

# responses-encoders 源码信源

## 基本信息
- **源码路径**: `fastapi/responses.py`、`fastapi/encoders.py`、`fastapi/datastructures.py`、`fastapi/utils.py`、`fastapi/sse.py`、`fastapi/background.py`、`fastapi/_compat/`
- **版本**: 0.141.1
- **事实范围**: F-095 ~ F-098, F-107 ~ F-137, F-152 ~ F-156

## 公开 API 清单

### 类（responses.py）
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `Response` | Starlette 再导出 | 基础响应类 | F-095 |
| `HTMLResponse` | Starlette 再导出 | HTML 响应 | F-095 |
| `JSONResponse` | Starlette 再导出 | JSON 响应 | F-095 |
| `PlainTextResponse` | Starlette 再导出 | 纯文本响应 | F-095 |
| `RedirectResponse` | Starlette 再导出 | 重定向响应 | F-095 |
| `StreamingResponse` | Starlette 再导出 | 流式响应 | F-095 |
| `FileResponse` | Starlette 再导出 | 文件响应 | F-095 |
| `EventSourceResponse` | `StreamingResponse`（从 sse 再导出） | `media_type = "text/event-stream"` | F-095, F-123 |
| `UJSONResponse` | `JSONResponse` | `@deprecated`；render 用 ujson | F-097 |
| `ORJSONResponse` | `JSONResponse` | `@deprecated`；render 用 orjson | F-098 |

### 类（datastructures.py）
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `UploadFile` | `StarletteUploadFile` | write/read/seek/close、`_validate`、`__get_pydantic_json_schema__`、`__get_pydantic_core_schema__` | F-112 |
| `DefaultPlaceholder` | — | `value` 属性、`__bool__`、`__eq__` | F-113 |

### 类（sse.py）
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `EventSourceResponse` | `StreamingResponse` | `media_type = "text/event-stream"` | F-123 |
| `ServerSentEvent` | `BaseModel` | data/raw_data/event/id/retry/comment 字段及校验 | F-124 |

### 类（background.py）
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `BackgroundTasks` | `StarletteBackgroundTasks` | 重写 `add_task(func, *args, **kwargs)` 委托 super | F-127, F-152, F-153 |

### 类（_compat/v2.py）
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `ModelField` | — | field_info/name/mode/config、validate/serialize/serialize_json/get_default | F-133 |

### 函数（encoders.py）
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| `jsonable_encoder` | `jsonable_encoder(obj, *, include=None, exclude=None, by_alias=True, exclude_unset=False, exclude_defaults=False, exclude_none=False, custom_encoder=None, sqlalchemy_safe=True)` | F-110 |
| `decimal_encoder` | `decimal_encoder(Decimal)` → int \| float | F-108 |
| `generate_encoders_by_class_tuples` | `generate_encoders_by_class_tuples(type_encoder_map)` → dict | F-109 |

### 函数（utils.py）
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| `generate_unique_id` | `generate_unique_id(route)` → str | F-118 |
| `create_model_field` | `create_model_field(name, type_, default=Undefined, field_info=None, alias=None, mode="validation")` → ModelField | F-117 |
| `get_value_or_default` | `get_value_or_default(first_item, *extra_items)` → Any | F-120 |
| `is_body_allowed_for_status_code` | `is_body_allowed_for_status_code(status_code)` → bool | F-115 |
| `get_path_param_names` | `get_path_param_names(path)` → set[str] | F-116 |
| `deep_dict_update` | `deep_dict_update(main_dict, update_dict)` → None | F-119 |

### 函数（sse.py）
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| `format_sse_event` | `format_sse_event(*, data_str=None, event=None, id=None, retry=None, comment=None) -> bytes` | F-125 |

### 常量
| 名称 | 值 | 事实编号 |
|------|-----|---------|
| `ENCODERS_BY_TYPE` | dict[type, Callable]，注册 bytes/datetime/Decimal/Enum/IPv4/UUID 等类型编码器 | F-107 |
| `KEEPALIVE_COMMENT` | `b": ping\n\n"` | F-126 |
| `_PING_INTERVAL` | `15.0` | F-126 |
| `_SSE_EVENT_SCHEMA` | type=object，properties 含 data/event/id/retry | F-122 |

## 关键实现细节

### responses.py 再导出与可选 JSON 引擎（F-095, F-096）
- 从 starlette.responses 重新导出：FileResponse/HTMLResponse/JSONResponse/PlainTextResponse/RedirectResponse/Response/StreamingResponse
- 从 fastapi.sse 重新导出 EventSourceResponse
- 模块级尝试 `importlib.import_module("ujson")` 和 `importlib.import_module("orjson")`，ModuleNotFoundError 时置 None

### UJSONResponse（F-097）
- `@deprecated(...)` 标记 FastAPIDeprecationWarning
- render 方法断言 ujson 已安装
- 返回 `ujson.dumps(content, ensure_ascii=False).encode("utf-8")`

### ORJSONResponse（F-098）
- `@deprecated(...)` 标记 FastAPIDeprecationWarning
- render 返回 `orjson.dumps(content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY)`

### ENCODERS_BY_TYPE 类型编码器注册表（F-107）
注册类型→编码器映射，包含：bytes/Color/PyExtraColor/datetime.date/datetime.datetime/datetime.time/datetime.timedelta/Decimal/Enum/frozenset/deque/GeneratorType/IPv4Address/IPv4Interface/IPv4Network/IPv6*/NameEmail/Path/Pattern/SecretBytes/SecretStr/set/UUID/Url/AnyUrl。

### decimal_encoder（F-108）
根据 `as_tuple().exponent` 判断：int 类型且 >=0 返回 int，否则返回 float。

### generate_encoders_by_class_tuples（F-109）
将 type→encoder 映射反转为 encoder→tuple(types)；模块级 `encoders_by_class_tuples = generate_encoders_by_class_tuples(ENCODERS_BY_TYPE)`。

### jsonable_encoder 管线（F-110）
`jsonable_encoder(obj, *, include=None, exclude=None, by_alias=True, exclude_unset=False, exclude_defaults=False, exclude_none=False, custom_encoder=None, sqlalchemy_safe=True)` 按优先级处理：
1. custom_encoder
2. BaseModel（`model_dump` mode="json"）
3. dataclass
4. Enum
5. PurePath
6. 原始类型
7. PydanticUndefinedType
8. dict
9. list/set/frozenset/GeneratorType/tuple/deque
10. ENCODERS_BY_TYPE/encoders_by_class_tuples
- pydantic.v1 实例抛 PydanticV1NotSupportedError
- 兜底尝试 `dict(obj)` 和 `vars(obj)`

### UploadFile（F-112）
- 继承 StarletteUploadFile
- 声明类注解 file/filename/size/headers/content_type
- 提供 async write/read/seek/close（委托 super）
- 类方法 `_validate` 断言 isinstance(..., StarletteUploadFile)
- `__get_pydantic_json_schema__` 返回 `{"type":"string","contentMediaType":"application/octet-stream"}`
- `__get_pydantic_core_schema__` 调用 `with_info_plain_validator_function(cls._validate)`

### datastructures 再导出（F-111）
从 starlette.datastructures 重新导出 URL/Address/FormData/Headers/QueryParams/State，并导入 `UploadFile as StarletteUploadFile`。

### DefaultPlaceholder 与 Default（F-113）
- `class DefaultPlaceholder` 含 `value` 属性、`__bool__` 返回 `bool(value)`、`__eq__` 比较 value
- `Default(value)` 函数返回 `DefaultPlaceholder(value)`
- `_Unset = Default(None)`

### StreamUploadFile 不存在声明（F-114）
该版本文件中不存在 StreamUploadFile 类和 _Wrapper 类（经全目录 grep 确认）。

### is_body_allowed_for_status_code（F-115）
- None/"default"/"1XX"/"2XX"/"3XX"/"4XX"/"5XX" 返回 True
- int 状态码 <200 或属于 {204,205,304} 返回 False
- 其余返回 True

### get_path_param_names（F-116）
返回 `set(re.findall("{(.*?)}", path))`。

### create_model_field（F-117）
- 检测 pydantic.v1 抛 PydanticV1NotSupportedError
- 调用 `v2.ModelField(mode=mode, name=name, field_info=field_info)`
- 捕获 PydanticSchemaGenerationError 转 FastAPIError

### generate_unique_id（F-118）
返回 `re.sub(r"\W","_",f"{route.name}{route.path_format}") + "_" + list(route.methods)[0].lower()`。

### deep_dict_update（F-119）
递归合并 dict，list 拼接，其余键覆盖。

### get_value_or_default（F-120）
按优先级返回首个非 DefaultPlaceholder 项，否则返回 first_item。

### SSE 事件 Schema（F-122）
`_SSE_EVENT_SCHEMA` 字典定义 type=object，properties 含 data/event/id（string）和 retry（integer, minimum 0）。

### EventSourceResponse（F-123）
`class EventSourceResponse(StreamingResponse)` 类属性 `media_type = "text/event-stream"`。

### ServerSentEvent 模型（F-124）
`class ServerSentEvent(BaseModel)` 字段：
- `data: Any = None`
- `raw_data: str | None = None`
- `event: str | None`（AfterValidator 校验单行）
- `id: str | None`（AfterValidator 校验单行且无 null 字符）
- `retry: int | None`（Field(ge=0)）
- `comment: str | None`
- `model_validator(mode="after")` 校验 data 与 raw_data 互斥

### format_sse_event（F-125）
按 SSE 线格式拼装：
- comment（以 `: ` 前缀）
- event
- data
- id
- retry
- 末尾追加两个空行
- 以 `\n` 连接并 UTF-8 编码

### SSE Keepalive 常量（F-126）
- `KEEPALIVE_COMMENT = b": ping\n\n"`
- `_PING_INTERVAL: float = 15.0`

### BackgroundTasks（F-127, F-152, F-153）
- `class BackgroundTasks(StarletteBackgroundTasks)`
- 重写 `add_task(func, *args, **kwargs)`，方法体直接 `return super().add_task(func, *args, **kwargs)`
- 模块顶部从 typing_extensions 导入 `ParamSpec` 并定义 `P = ParamSpec("P")`
- add_task 方法签名中 `*args: P.args`/`**kwargs: P.kwargs` 引用该 ParamSpec
- 未新增字段或重写 __init__，仅重写 add_task 方法并为参数添加 `Annotated[..., Doc(...)]` 文档注解

### _compat 兼容层（F-131 ~ F-137, F-155, F-156）
- `_compat/__init__.py` 是纯再导出模块，无任何函数或类定义，共 40 行 import 语句
- 从 `.shared` 导入：PYDANTIC_VERSION_MINOR_TUPLE/annotation_is_pydantic_v1/field_annotation_is_scalar/field_annotation_is_scalar_sequence/field_annotation_is_sequence/is_bytes_*/is_pydantic_v1_model_instance/is_uploadfile_*/lenient_issubclass/sequence_types/value_is_sequence
- 从 `.v2` 导入：ModelField/PydanticSchemaGenerationError/RequiredParam/Undefined/Url/copy_field_info/create_body_model/evaluate_forwardref/get_cached_model_fields/get_definitions/get_flat_models_from_fields/get_missing_field_error/get_model_name_map/get_schema_from_model_field/is_scalar_field/serialize_sequence_value/with_info_plain_validator_function
- `RequiredParam = PydanticUndefined`，`Undefined = PydanticUndefined`
- `ModelField` 含 field_info/name/mode/config 属性，`__post_init__` 通过 asdict(field_info) 构造 Annotated 并创建 TypeAdapter；方法 validate 返回 (value, errors)、serialize 调 dump_python、serialize_json 返回 bytes
- `get_definitions` 使用 `GenerateJsonSchema(ref_template=REF_TEMPLATE)`，按 mode 拆分 validation/serialization 字段
- `lenient_issubclass` try 中执行 isinstance(cls,type) and issubclass，捕获 TypeError：WithArgsTypes 实例返回 False
- `sequence_annotation_to_type` 映射 Sequence/list/tuple/set/frozenset/deque→list/list/tuple/set/frozenset/list；`sequence_types` 为其键元组
- `_compat/shared` 定义 field_annotation_is_scalar/is_sequence/is_uploadfile_annotation/is_bytes_annotation 等类型判断函数

## 相关信源
- [routing.md](routing.md) — serialize_response 调用 jsonable_encoder，SSE 流式使用 EventSourceResponse
- [dependencies.md](dependencies.md) — create_model_field 用于参数 ModelField 创建
- [openapi.md](openapi.md) — get_definitions 从 _compat 导入，jsonable_encoder 用于最终序列化
- [middleware-exceptions.md](middleware-exceptions.md) — PydanticV1NotSupportedError 异常定义
