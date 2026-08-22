---
type: Concept
title: "App 与 Router 基础设施"
description: "App 类包装 FastAPI 提供路径冲突检测和活动追踪，Router 基类为所有服务类提供统一的路由注册、挂载和中间件机制。"
tags: [app, router, fastapi, path-conflict, middleware, singleton, config]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: app
    resource: /references/app-source.md
    title: App 类信源
  - id: main
    resource: /references/main-module-source.md
    title: JupyverseModule 主模块信源
---

# App 与 Router 基础设施

App 和 Router 是 Jupyverse 的 HTTP 层基础设施。App 包装 FastAPI 应用实例，Router 为所有功能服务提供统一的路由注册入口。

## App 类

`App` 类位于 `jupyverse_api.app`，是 FastAPI 的包装器，提供三个核心能力：

### 1. 路径冲突检测

当多个插件尝试注册相同的 URL 路径时，App 会立即抛出 `RuntimeError`：

```python
def _include_router(self, router, _type, **kwargs) -> None:
    for route in route_iter:
        path = kwargs.get("prefix", "") + route.path
        for _router, _paths in self._router_paths.items():
            if path in _paths:
                raise RuntimeError(
                    f"{_type} adds a handler for a path that is already defined in "
                    f"{_router}: {path}"
                )
```

这防止了插件间意外的路由覆盖，确保每个 URL 路径只有一个处理者。`_type` 参数记录注册者的类名（如 `_Contents`、`_Kernels`），便于调试冲突来源。

### 2. 子应用挂载

App 支持通过 `mount_path` 创建子应用：

```python
def __init__(self, app: FastAPI, mount_path: str | None = None):
    if mount_path is None:
        self._app = app
    else:
        subapi = FastAPI()
        app.mount(mount_path, subapi)
        self._app = subapi
```

这允许在特定路径前缀下挂载独立的 API 子应用。

### 3. 活动时间追踪

App 自动记录服务器启动时间和最后一次 HTTP 请求时间：

```python
self._started_time = datetime.now(timezone.utc)
self._last_activity = self._started_time

@app.middleware("http")
async def get_last_activity(request: Request, call_next):
    self._last_activity = datetime.now(timezone.utc)
    return await call_next(request)
```

这些属性可用于空闲超时、状态监控等功能。

### 4. 重定向异常处理

App 全局注册 `RedirectException` 处理器：

```python
class RedirectException(Exception):
    def __init__(self, redirect_to: str):
        self.redirect_to = redirect_to

async def _redirect_exception_handler(request: Request, exc: Exception) -> RedirectResponse:
    return RedirectResponse(url=exc.redirect_to)
```

插件可以在任何地方抛出 `RedirectException` 来执行 HTTP 重定向，无需直接操作 Response 对象。

### FastAPI 版本兼容

App 对 FastAPI 0.137.0+ 的路由 API 变更做了兼容处理：

```python
fastapi_version = Version(version("fastapi"))
if fastapi_version >= Version("0.137.2"):
    from fastapi.routing import iter_route_contexts
    route_iter = iter_route_contexts(router.routes)
else:
    route_iter = router.routes
```

## Router 基类

`Router` 是所有服务类（Contents、Kernels、Lab、Yjs、Terminals 等）的共同基类：

```python
class Router:
    _app: App

    def __init__(self, app: App):
        self._app = app

    @property
    def _type(self):
        return self.__class__.__name__

    def include_router(self, router, **kwargs):
        self._app._include_router(router, self._type, **kwargs)

    def mount(self, path: str, *args, **kwargs):
        self._app._mount(path, self._type, *args, **kwargs)

    def add_middleware(self, middleware, *args, **kwargs):
        self._app.add_middleware(middleware, *args, **kwargs)
```

### 为什么路由在 ABC __init__ 中注册？

Jupyverse 的一个关键设计是**路由定义在抽象基类的 `__init__` 中**，而非在实现类中：

```python
class Contents(Router, ABC):
    def __init__(self, app: App, auth: Auth):
        super().__init__(app=app)
        router = APIRouter()

        @router.get("/api/contents/{path:path}")
        async def get_content(path: str, ...):
            return await self.get_content(path, content, user)

        @router.post("/api/contents{path:path}")
        async def create_content(...):
            return await self.create_content(path, request, user)

        # ... 更多端点 ...

        self.include_router(router)

    @abstractmethod
    async def get_content(self, path, content, user) -> Content: ...
    @abstractmethod
    async def create_content(self, path, request, user) -> Content: ...
```

这种设计保证了：
- **API 契约一致性**：所有 Contents 实现（无论本地文件系统、S3、数据库）都暴露相同的 REST API
- **权限声明集中**：每个端点的权限要求在基类中统一声明，实现类无需关心权限
- **路由冲突检测**：基类注册路由时，App 自动检测路径冲突

## Config 基类

所有配置类继承自 `Config`，它是 Pydantic BaseModel 的子类：

```python
class Config(BaseModel):
    model_config = {"extra": "forbid"}
```

`extra: forbid` 意味着传入未声明的配置字段会导致验证错误，这防止了拼写错误和无效配置被静默忽略。

## Singleton 元类

```python
class Singleton(type):
    _instances: dict = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
```

提供单例模式支持，适用于全局唯一的管理器类。

## CORS 中间件配置

JupyverseModule 在 prepare 阶段根据配置添加 CORS 中间件：

```python
if self.jupyverse_config.allow_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=self.jupyverse_config.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

通过 `--allow-origin` CLI 选项或配置文件指定允许的源。

## 相关概念

- [架构总览](02-architecture-overview.md) — 整体架构中 App/Router 的位置
- [FPS 模块系统](03-fps-module-system.md) — Module 如何获取 App 依赖
- [认证授权系统](05-auth-system.md) — Router 中如何使用 auth.current_user()
