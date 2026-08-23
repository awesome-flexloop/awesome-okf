---
type: Concept
title: 依赖注入系统
description: 详解 Depends/Security 声明、Dependant 依赖树递归构建与求解、use_cache 请求级缓存、yield 依赖双层 AsyncExitStack 生命周期与 dependency_overrides 测试替换。
tags: [fastapi, dependency-injection, depends, dependant, async-exit-stack]
generated: { by: "reference_agent/trae", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: fastapi-source
    resource: /references/dependencies.md
    title: FastAPI v0.141.1 源码信源
---

# 依赖注入系统

FastAPI 内建一套基于类型注解的依赖注入（Dependency Injection，DI）系统。开发者通过 `Depends()` 声明依赖，框架在请求处理时递归构建 `Dependant` 依赖树，以后序遍历求解所有子依赖，最终将结果注入端点函数。依赖系统支持子依赖嵌套、请求级缓存、`yield` 依赖的异步资源清理，以及测试时的运行时替换。

## Depends 与 Security 声明

`Depends` 是一个 frozen dataclass（F-048）：

```python
@dataclass(frozen=True)
class Depends:
    dependency: Callable | None = None
    use_cache: bool = True
    scope: Literal["function", "request"] | None = None
```

- `dependency`：依赖可调用对象（函数、类等），为 `None` 时从参数类型注解自动推断
- `use_cache`：同一请求内是否缓存依赖结果，默认 `True`
- `scope`：`yield` 依赖的生命周期范围，`"request"` 跨越整个请求，`"function"` 在端点返回后关闭，`None` 时自动推断

`Security` 继承 `Depends`，新增 `scopes` 字段（F-049）：

```python
@dataclass(frozen=True)
class Security(Depends):
    scopes: Sequence[str] | None = None
```

`Security` 用于 OAuth2 等需要权限范围（scope）声明的场景，框架会将 scopes 注入 `SecurityScopes` 参数。工厂函数 `Depends(dependency=None, *, use_cache=True, scope=None)`（F-052）和 `Security(dependency=None, *, scopes=None, use_cache=True)`（F-053）返回对应数据类实例。

```python
from fastapi import Depends, FastAPI, Security

async def get_token():
    return "token"

async def get_current_user(token: str = Depends(get_token)):
    return {"user": "alice"}

app = FastAPI()

@app.get("/profile")
async def profile(user: dict = Depends(get_current_user)):
    return user
```

## Dependant 依赖树模型

`Dependant` 是 `@dataclass(slots=True)` 数据类，表示依赖树中的一个节点（F-054），包含以下字段：

**五类参数列表**（均为 `list[ModelField]`）：
- `path_params`：路径参数
- `query_params`：查询参数
- `header_params`：请求头参数
- `cookie_params`：Cookie 参数
- `body_params`：请求体参数

**子依赖**：`dependencies: list["Dependant"]`，嵌套的子依赖节点列表。

**特殊参数名**：
- `request_param_name`：`Request` 类型参数名
- `websocket_param_name`：`WebSocket` 类型参数名
- `http_connection_param_name`：`HTTPConnection` 类型参数名
- `response_param_name`：`Response` 类型参数名
- `background_tasks_param_name`：`BackgroundTasks` 参数名
- `security_scopes_param_name`：`SecurityScopes` 参数名

**OAuth scopes**：`own_oauth_scopes`（当前节点声明的 scopes）、`parent_oauth_scopes`（从父依赖继承的 scopes）。

**其他**：`name`（依赖名称）、`call`（依赖可调用对象）、`use_cache`（是否缓存）、`path`（路由路径）、`scope`（生命周期范围）。

## 可调用类型检测与缓存

三个函数用于检测可调用对象的类型（F-055）：

- `_is_gen_callable(call)`：是否为同步生成器函数
- `_is_async_gen_callable(call)`：是否为异步生成器函数（`async def` + `yield`）
- `_is_coroutine_callable(call)`：是否为协程函数（`async def`）

三者均经 `@lru_cache(maxsize=4096)` 缓存，使用 `_CallIdentity` 作为缓存键——`_CallIdentity` 按 `id(call)` 计算哈希并以 `is` 比较相等性。这是因为某些可调用对象（如 functools.partial、绑定方法）不可哈希或哈希成本高，而 `id()` 提供 O(1) 的对象标识。

## scope 自动推断

`_get_computed_scope(*, dependant)` 确定 `yield` 依赖的生命周期范围（F-056）：

1. `dependant.scope` 非空时直接返回该值（显式声明优先）
2. 否则，若 `call` 是生成器或异步生成器，返回 `"request"`
3. 否则返回 `None`（即 function 级）

这意味着 `yield` 依赖默认在 request 级栈中管理，其清理逻辑（yield 之后的代码）在响应完全发送后才执行，而非在端点函数返回时立即执行。非 `yield` 依赖没有清理逻辑，scope 概念不适用。

## get_dependant 构建依赖树

`get_dependant(*, path, call, name=None, own_oauth_scopes=None, parent_oauth_scopes=None, use_cache=True, scope=None)` 为指定端点函数构建 `Dependant` 树（F-058）：

1. 调用 `get_typed_signature(call)` 获取函数签名
2. 遍历每个参数，调用 `analyze_param` 解析得到 `ParamDetails`（F-060，含 `type_annotation`/`depends`/`field`）
3. 若参数是 `Depends` 类型，递归调用 `get_dependant` 构建子 `Dependant`，加入 `dependencies` 列表
4. 非字段参数（Request/WebSocket/HTTPConnection/Response/BackgroundTasks/SecurityScopes）调用 `add_non_field_param_to_dependency`（F-059）按类型识别并设置对应 param_name
5. `Body` 类型参数加入 `body_params`
6. 其余参数（Path/Query/Header/Cookie）调用 `add_param_to_fields`（F-062），按 `field.field_info.in_` 分发到对应参数列表

`add_non_field_param_to_dependency` 使用 `lenient_issubclass` 依次检测参数类型是否为 Request、WebSocket、HTTPConnection、Response、StarletteBackgroundTasks、SecurityScopes，命中则设置对应 param_name 并返回 `True`；均不匹配返回 `None`（F-059）。

## analyze_param 参数分析

`analyze_param(*, param_name, annotation, value, is_path_param)` 解析单个参数的类型注解和默认值（F-061）：

1. 解析 `Annotated[..., FieldInfo/Depends]` 元数据
2. 从默认值识别 `Depends` 或 `FieldInfo` 实例
3. 无显式注解时按规则自动推断：
   - `is_path_param=True` → 推断为 `Path`
   - 类型为 `UploadFile` → 推断为 `File`
   - 非标量类型（Pydantic 模型、dataclass 等）→ 推断为 `Body`
   - 标量类型（int/str/float/bool）→ 推断为 `Query`
4. `Form` 类型参数调用 `ensure_multipart_is_installed()` 检查 `python-multipart` 依赖（F-057）

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(
    item_id: int,
    q: str | None = None,
    limit: int = 10,
):
    return {"item_id": item_id, "q": q, "limit": limit}
```

上述代码中，`item_id` 因在路径中自动推断为 `Path`，`q` 和 `limit` 为标量自动推断为 `Query`，无需显式 `Path()`/`Query()`。

## solve_dependencies 递归求解

`solve_dependencies` 是 async 递归函数，负责运行时求解依赖树（F-064），返回 `SolvedDependency`（F-063，含 `values`/`errors`/`background_tasks`/`response`/`dependency_cache`）。

求解流程：

1. **初始化缓存**：`dependency_cache` 为 `None` 时创建空字典
2. **递归求解子依赖**：遍历 `dependant.dependencies`，对每个子依赖：
   - 检查 `dependency_overrides_provider` 上的 `dependency_overrides` 字典，命中则用替换函数构建新 `Dependant`
   - 按 `use_cache` 和 `_get_cache_key` 检查缓存——命中直接复用结果
   - 递归调用 `solve_dependencies` 求解子依赖
   - 若子依赖是生成器，按 scope 进入对应的 `AsyncExitStack`：
     - `"function"` → `scope["fastapi_function_astack"]`
     - `"request"` → `scope["fastapi_inner_astack"]`
   - 调用依赖函数，结果缓存到 `dependency_cache`
3. **求解请求参数**：
   - path/query/header/cookie 参数调用 `request_params_to_args`（F-065）
   - body 参数调用 `request_body_to_args`
4. **注入特殊参数**：Request、WebSocket、BackgroundTasks、Response、SecurityScopes 直接从请求上下文注入
5. **聚合结果**：所有参数值汇入 `values` 字典，校验错误汇入 `errors` 列表

`request_params_to_args`（F-065）处理细节：
- 单字段 BaseModel 时展开为模型字段
- Headers 类型按 `convert_underscores` 转换下划线为连字符别名
- 序列类型在 `ImmutableMultiDict`/`Headers` 上调用 `getlist`
- 未在 fields 中声明的键透传到 `params_to_process`

## use_cache 缓存机制

`use_cache=True`（默认）时，同一个依赖函数在单个请求内只执行一次，后续引用从 `dependency_cache` 取结果。缓存键由 `_get_cache_key` 生成，包含依赖 callable 标识。这在多个端点/子依赖共享同一依赖（如数据库会话、当前用户）时避免重复执行。

设为 `False` 时每次引用都重新执行依赖函数，适用于需要独立实例的场景。缓存粒度是请求级而非全局单例——不同请求拥有独立的 `dependency_cache`。

## yield 依赖与生命周期

`yield` 依赖通过生成器函数实现资源的设置与清理：

```python
async def get_db():
    db = await create_db_connection()
    try:
        yield db
    finally:
        await db.close()
```

`yield` 之前的代码在依赖求解时执行，`yield` 的值注入端点，`yield` 之后的代码在 `AsyncExitStack` 关闭时执行。scope 决定关闭时机：

- **`scope="request"`（默认，F-056）**：进入 `fastapi_inner_astack`，在响应完全发送后关闭。适用于数据库连接等需要跨越整个请求生命周期的资源。
- **`scope="function"`**：进入 `fastapi_function_astack`，在端点函数返回后立即关闭。适用于仅需在端点执行期间存在的资源。

同步生成器依赖通过 `contextmanager_in_threadpool` 在线程池中管理（F-130），该函数使用 `CapacityLimiter(1)` 限制并发，并通过 `anyio.to_thread.run_sync` 执行同步上下文管理器的 `__enter__`/`__exit__`。

## dependency_overrides 测试替换

`app.dependency_overrides` 字典（F-009）支持运行时替换依赖实现，主要用于测试：

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

async def get_db():
    yield "real-db"

app = FastAPI()

@app.get("/items")
async def list_items(db: str = Depends(get_db)):
    return {"db": db}

app.dependency_overrides[get_db] = lambda: "fake-db"
client = TestClient(app)
response = client.get("/items")
assert response.json() == {"db": "fake-db"}
```

替换发生在 `solve_dependencies` 求解每个子依赖前检查字典（F-064），命中时用替换函数重新构建子 `Dependant`。替换在任意节点生效，无需重建路由树。测试结束后应清空 `app.dependency_overrides`。

## 全局依赖与路由级依赖

依赖可以在多个层级声明：

- **应用级**：`FastAPI(dependencies=[Depends(...)] )`，应用于所有路由
- **路由器级**：`APIRouter(dependencies=[Depends(...)] )`，应用于该 router 的所有路由
- **路由级**：`@router.get("/", dependencies=[Depends(...)] )`，仅应用于该路由
- **参数级**：端点函数参数中的 `Depends()`，仅注入该端点

多层依赖会累加合并（F-036 中 dependencies 做列表拼接），同一个依赖函数在多个层级声明时，`use_cache=True` 确保仍只执行一次。

## 相关概念

- [路径操作与请求处理](03-path-operations.md)
- [参数声明系统](05-parameter-declaration.md)
- [路由系统](02-routing-system.md)
- [FastAPI 应用类](01-application.md)
