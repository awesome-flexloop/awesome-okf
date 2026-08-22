---
type: Reference
title: "App 类信源"
description: "jupyverse 核心 App 类，包装 FastAPI 提供路径冲突检测、活动追踪和异常处理。"
tags: [app, fastapi, wrapper, routing, middleware]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: app
    resource: /external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/app/__init__.py
    title: jupyverse_api/app/__init__.py
  - id: api_init
    resource: /external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/__init__.py
    title: jupyverse_api/__init__.py
  - id: exceptions
    resource: /external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/exceptions.py
    title: jupyverse_api/exceptions.py
---

# App 类信源

## App 类

`App` 类位于 `jupyverse_api.app`，是 FastAPI 的包装器：

```python
class App:
    def __init__(self, app: FastAPI, mount_path: str | None = None):
        # mount_path 不为 None 时创建子应用并挂载
        # 注册 RedirectException 全局处理器
        # 初始化 _router_paths 用于路径冲突检测
        # 记录 _started_time 和 _last_activity
        # 添加 HTTP 中间件更新 last_activity
```

### 核心方法

| 方法 | 说明 |
|------|------|
| `_include_router(router, _type, **kwargs)` | 注册路由，检测路径冲突，记录到 `_router_paths` |
| `_mount(path, _type, *args, **kwargs)` | 挂载子应用/静态文件，检测路径冲突 |
| `add_middleware(middleware, *args, **kwargs)` | 添加中间件，委托给底层 FastAPI |
| `started_time` (property) | 服务器启动时间（UTC） |
| `last_activity` (property) | 最后一次 HTTP 请求时间（UTC） |

### 路径冲突检测

`_include_router` 在注册路由时遍历所有路由路径，检查是否与已有路由冲突：

```python
for route in route_iter:
    path = kwargs.get("prefix", "") + route.path
    for _router, _paths in self._router_paths.items():
        if path in _paths:
            raise RuntimeError(
                f"{_type} adds a handler for a path that is already defined in "
                f"{_router}: {path}"
            )
```

## Router 基类

`Router` 类位于 `jupyverse_api`，是所有服务类（Contents、Kernels 等）的基类：

```python
class Router:
    def __init__(self, app: App):
        self._app = app

    def include_router(self, router, **kwargs):
        self._app._include_router(router, self._type, **kwargs)

    def mount(self, path: str, *args, **kwargs):
        self._app._mount(path, self._type, *args, **kwargs)

    def add_middleware(self, middleware, *args, **kwargs):
        self._app.add_middleware(middleware, *args, **kwargs)
```

`_type` 属性返回类名（如 `_Contents`、`_Kernels`），用于路径冲突日志中的类型标识。

## Config 基类

```python
class Config(BaseModel):
    model_config = {"extra": "forbid"}
```

所有配置类继承 `Config`，使用 Pydantic 的 `extra: forbid` 禁止未声明字段。

## Singleton 元类

```python
class Singleton(type):
    _instances: dict = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
```

## RedirectException

```python
class RedirectException(Exception):
    def __init__(self, redirect_to: str):
        self.redirect_to = redirect_to
```

配合全局异常处理器 `_redirect_exception_handler` 返回 `RedirectResponse`。
