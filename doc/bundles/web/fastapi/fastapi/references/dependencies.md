---
type: Reference
title: dependencies — FastAPI 源码信源
description: 依赖注入系统核心实现，涵盖 Dependant 数据模型、可调用类型检测缓存、依赖树构建与递归求解、参数分析及生成器依赖生命周期管理
tags: [fastapi, source, dependencies]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/dependencies.md
    title: FastAPI v0.141.1 源码
---

# dependencies 源码信源

## 基本信息
- **源码路径**: `fastapi/dependencies/models.py`、`fastapi/dependencies/utils.py`
- **版本**: 0.141.1
- **事实范围**: F-054 ~ F-066

## 公开 API 清单

### 类
| 类名 | 继承自 | 关键属性/方法 | 事实编号 |
|------|--------|--------------|---------|
| `Dependant` | `@dataclass(slots=True)` | path_params/query_params/header_params/cookie_params/body_params、dependencies 子依赖列表、call、use_cache、scope 等 | F-054 |
| `ParamDetails` | `@dataclass` | type_annotation、depends、field | F-060 |
| `SolvedDependency` | `@dataclass` | values、errors、background_tasks、response、dependency_cache | F-063 |

### 函数
| 函数名 | 签名摘要 | 事实编号 |
|--------|---------|---------|
| `_is_gen_callable` | `_is_gen_callable(call)` → bool，`@lru_cache(maxsize=4096)` | F-055 |
| `_is_async_gen_callable` | `_is_async_gen_callable(call)` → bool，`@lru_cache(maxsize=4096)` | F-055 |
| `_is_coroutine_callable` | `_is_coroutine_callable(call)` → bool，`@lru_cache(maxsize=4096)` | F-055 |
| `_get_computed_scope` | `_get_computed_scope(*, dependant)` → `"request"` \| `None` | F-056 |
| `ensure_multipart_is_installed` | `ensure_multipart_is_installed()` → None，检测 python_multipart/multipart | F-057 |
| `get_dependant` | `get_dependant(*, path, call, name=None, own_oauth_scopes=None, parent_oauth_scopes=None, use_cache=True, scope=None)` → Dependant | F-058 |
| `add_non_field_param_to_dependency` | `add_non_field_param_to_dependency(*, param_name, type_annotation, dependant)` → bool \| None | F-059 |
| `analyze_param` | `analyze_param(*, param_name, annotation, value, is_path_param)` → ParamDetails | F-061 |
| `add_param_to_fields` | `add_param_to_fields(*, field, dependant)` → None | F-062 |
| `solve_dependencies` | `async solve_dependencies(*, request, dependant, body=None, background_tasks=None, response=None, dependency_overrides_provider=None, dependency_cache=None, async_exit_stack, embed_body_fields, _uses_scopes_cache=None)` → SolvedDependency | F-064 |
| `request_params_to_args` | `request_params_to_args(fields, received_params)` → tuple[dict, list] | F-065 |
| `get_stream_item_type` | `get_stream_item_type(annotation)` → type \| None | F-066 |

## 关键实现细节

### Dependant dataclass 字段（F-054）
`@dataclass(slots=True) class Dependant` 包含：
- **五类参数列表**：`path_params`/`query_params`/`header_params`/`cookie_params`/`body_params`（均 `list[ModelField]`）
- **子依赖树**：`dependencies: list["Dependant"]`
- **标识信息**：`name`、`call`、`path`
- **特殊参数名**：`request_param_name`、`websocket_param_name`、`http_connection_param_name`、`response_param_name`、`background_tasks_param_name`、`security_scopes_param_name`
- **OAuth scopes**：`own_oauth_scopes`、`parent_oauth_scopes`
- **缓存与生命周期**：`use_cache=True`、`scope`

### 三个可调用类型判定函数（F-055）
- `_is_gen_callable`、`_is_async_gen_callable`、`_is_coroutine_callable` 均经 `@lru_cache(maxsize=4096)` 缓存
- 使用 `_CallIdentity` 作为缓存键，按 `id(call)` 哈希和 `is` 比较，避免对不可哈希的可调用对象缓存失败

### _get_computed_scope 自动推断（F-056）
- `dependant.scope` 非空 → 返回该值
- call 为生成器/异步生成器 → 返回 `"request"`（跨整个请求生命周期）
- 其余 → 返回 `None`（即 function 级，端点返回时关闭）

### ensure_multipart_is_installed（F-057）
- 尝试导入 `python_multipart.__version__`（断言 > "0.0.12"）
- 失败时尝试 `multipart`
- 检测到错误包（名不副实的 multipart 包）抛 RuntimeError

### get_dependant 依赖树构建（F-058）
- 遍历 `get_typed_signature(call).parameters`
- 对每个参数调用 `analyze_param`
- `Depends` 类型递归构建子 `Dependant`
- 非字段参数调 `add_non_field_param_to_dependency`
- `Body` 加入 `body_params`，其余调 `add_param_to_fields`

### add_non_field_param_to_dependency 特殊注入（F-059）
按 `lenient_issubclass` 依次识别并设置对应 param_name：
1. `Request` → `request_param_name`
2. `WebSocket` → `websocket_param_name`
3. `HTTPConnection` → `http_connection_param_name`
4. `Response` → `response_param_name`
5. `StarletteBackgroundTasks` → `background_tasks_param_name`
6. `SecurityScopes` → `security_scopes_param_name`
- 均不匹配返回 None

### ParamDetails（F-060）
`@dataclass class ParamDetails` 字段：`type_annotation`、`depends`、`field`

### analyze_param 参数分析（F-061）
- 解析 `Annotated[..., FieldInfo/Depends]`
- 从默认值识别 Depends/FieldInfo
- 无显式注解时按规则自动推断：
  - `is_path_param` → `Path`
  - `UploadFile` 注解 → `File`
  - 非标量 → `Body`
  - 标量 → `Query`
- `Form` 类型调用 `ensure_multipart_is_installed`

### add_param_to_fields 字段分发（F-062）
按 `field.field_info.in_` 分发：
- `ParamTypes.path` → `path_params`
- `ParamTypes.query` → `query_params`
- `ParamTypes.header` → `header_params`
- `ParamTypes.cookie` → `cookie_params`（通过 assert 确认）

### SolvedDependency 求解结果（F-063）
`@dataclass class SolvedDependency` 字段：
- `values`：求解出的参数字典
- `errors`：校验错误列表
- `background_tasks`：后台任务
- `response`：响应对象
- `dependency_cache`：依赖缓存

### solve_dependencies 递归求解（F-064）
`async solve_dependencies(...)` 是依赖注入的核心：
- 递归求解子依赖（支持 `dependency_overrides` 运行时替换）
- 按 `use_cache` 和 `_get_cache_key` 缓存（请求级缓存，非全局单例）
- 生成器依赖按 scope 进入对应 AsyncExitStack：
  - `scope="function"` → `function_astack`
  - `scope="request"` → `request_astack`
- 调用 `request_params_to_args` 求解 path/query/header/cookie
- `body_params` 调 `request_body_to_args`
- 注入 Request/WebSocket/BackgroundTasks/Response/SecurityScopes

### request_params_to_args 参数求解（F-065）
- 单字段 BaseModel 时展开为模型字段
- Headers 类型按 `convert_underscores` 转换别名
- 序列类型在 `ImmutableMultiDict`/`Headers` 上调用 `getlist`
- 未在 fields 中出现的键透传到 `params_to_process`
- 返回 `(values, errors)`

### get_stream_item_type 流式类型提取（F-066）
- 检查 `get_origin(annotation)` 是否在 `_STREAM_ORIGINS` 中
- 是则返回第一个类型参数（无参数返回 `Any`）
- 否则返回 None

## 相关信源
- [routing.md](routing.md) — 请求处理管线调用 solve_dependencies
- [params.md](params.md) — Param/Depends/Security 参数类定义
- [applications.md](applications.md) — dependency_overrides 字典初始化
