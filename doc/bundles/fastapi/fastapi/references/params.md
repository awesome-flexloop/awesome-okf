---
type: Reference
title: params — FastAPI 源码信源
description: 参数系统类定义与工厂函数，涵盖 ParamTypes 枚举、Param/Path/Query/Header/Cookie/Body/Form/File 继承体系、Depends/Security 数据类及九个工厂函数
tags: [fastapi, source, params]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/params.md
    title: FastAPI v0.141.1 源码
---

# params 源码信源

## 基本信息
- **源码路径**: `fastapi/params.py`、`fastapi/param_functions.py`
- **版本**: 0.141.1
- **事实范围**: F-038 ~ F-053

## 公开 API 清单

### 类
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `ParamTypes` | `Enum` | 成员：query/header/path/cookie | F-038 |
| `Param` | `FieldInfo` | 类属性 `in_: ParamTypes`；`__init__` 支持全部 Pydantic 字段参数 | F-039, F-040 |
| `Path` | `Param` | `in_ = ParamTypes.path`；`__init__` 断言 default 为占位符 | F-041 |
| `Query` | `Param` | `in_ = ParamTypes.query`；default 默认 Undefined | F-042 |
| `Header` | `Param` | `in_ = ParamTypes.header`；独有 `convert_underscores: bool = True` | F-043 |
| `Cookie` | `Param` | `in_ = ParamTypes.cookie` | F-044 |
| `Body` | `FieldInfo` | 独有 `embed` 和 `media_type`；不继承 Param | F-045 |
| `Form` | `Body` | 默认 `media_type = "application/x-www-form-urlencoded"`；无 embed | F-046 |
| `File` | `Form` | 默认 `media_type = "multipart/form-data"` | F-047 |
| `Depends` | `@dataclass(frozen=True)` | 字段：dependency/use_cache/scope | F-048 |
| `Security` | `Depends` | 新增字段 `scopes` | F-049 |

### 函数
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| `Path` | `Path(default=..., *, alias, title, description, gt, ge, lt, le, ...)` → `params.Path` | F-050, F-051 |
| `Query` | `Query(default=Undefined, *, alias, title, description, gt, ge, ...)` → `params.Query` | F-050, F-051 |
| `Header` | `Header(default=Undefined, *, convert_underscores=True, alias, ...)` → `params.Header` | F-050, F-051 |
| `Cookie` | `Cookie(default=Undefined, *, alias, title, ...)` → `params.Cookie` | F-050, F-051 |
| `Body` | `Body(default=Undefined, *, embed=False, media_type="application/json", ...)` → `params.Body` | F-050, F-051 |
| `Form` | `Form(default=Undefined, *, media_type="application/x-www-form-urlencoded", ...)` → `params.Form` | F-050, F-051 |
| `File` | `File(default=Undefined, *, media_type="multipart/form-data", ...)` → `params.File` | F-050, F-051 |
| `Depends` | `Depends(dependency=None, *, use_cache=True, scope=None)` → `params.Depends` | F-052 |
| `Security` | `Security(dependency=None, *, scopes=None, use_cache=True)` → `params.Security` | F-053 |

## 关键实现细节

### ParamTypes 枚举（F-038）
`class ParamTypes(Enum)` 成员：`query`、`header`、`path`、`cookie`，值均为字符串。

### Param 基类（F-039, F-040）
`class Param(FieldInfo)`：
- 声明类属性 `in_: ParamTypes`
- `__init__` 支持参数：default/default_factory/annotation/alias/alias_priority/validation_alias/serialization_alias/title/description/gt/ge/lt/le/min_length/max_length/pattern/regex/discriminator/strict/multiple_of/allow_inf_nan/max_digits/decimal_places/examples/example/openapi_examples/deprecated/include_in_schema/json_schema_extra 及 `**extra`
- `example` 非 `_Unset` 时发出 `FastAPIDeprecationWarning`
- `regex` 非空时同样发出弃用警告
- `kwargs["pattern"] = pattern or regex`（regex 映射到 pattern）

### Path 类（F-041）
- `in_ = ParamTypes.path`
- `__init__` 断言 `default is ...`（"Path parameters cannot have a default value"）

### Query 类（F-042）
- `in_ = ParamTypes.query`
- default 默认 `Undefined`

### Header 类（F-043）
- `in_ = ParamTypes.header`
- 独有参数 `convert_underscores: bool = True`，在 `__init__` 中存为 `self.convert_underscores`

### Cookie 类（F-044）
- `in_ = ParamTypes.cookie`

### Body 类（F-045）
- `class Body(FieldInfo)` 不继承 Param（body 没有 `in_` 位置语义）
- 独有 `embed: bool | None = None` 和 `media_type: str = "application/json"`
- `__init__` 结构与 Param 类似但无 `in_`

### Form 类（F-046）
- `class Form(Body)`
- 默认 `media_type = "application/x-www-form-urlencoded"`
- 无 embed 参数

### File 类（F-047）
- `class File(Form)`
- 默认 `media_type = "multipart/form-data"`

### Depends 数据类（F-048）
`@dataclass(frozen=True) class Depends`：
- `dependency: Callable | None = None`
- `use_cache: bool = True`
- `scope: Literal["function", "request"] | None = None`

### Security 数据类（F-049）
`@dataclass(frozen=True) class Security(Depends)`：
- 新增 `scopes: Sequence[str] | None = None`

### 九个工厂函数（F-050）
`param_functions.py` 定义 `Path()`/`Query()`/`Header()`/`Cookie()`/`Body()`/`Form()`/`File()`/`Depends()`/`Security()` 九个函数，每个函数返回对应 `params.*` 类实例。

### Annotated 文档注解（F-051）
- Path/Query/Header/Cookie/Body/Form/File 函数签名使用 `Annotated[..., Doc(...)]` 为每个参数附加文档字符串
- 部分参数附加 `deprecated(...)` 装饰器

### Depends 工厂函数（F-052）
`Depends(dependency=None, *, use_cache=True, scope=None)` 返回 `params.Depends(dependency=dependency, use_cache=use_cache, scope=scope)`。

### Security 工厂函数（F-053）
`Security(dependency=None, *, scopes=None, use_cache=True)` 返回 `params.Security(dependency=dependency, scopes=scopes, use_cache=use_cache)`。

## 相关信源
- [dependencies.md](dependencies.md) — analyze_param 解析 Param/Depends，add_param_to_fields 按 in_ 分发
- [openapi.md](openapi.md) — 参数类元数据用于 OpenAPI schema 生成
