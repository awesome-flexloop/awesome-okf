---
type: Concept
title: "插件开发指南"
description: "Jupyverse 的模块化架构允许通过 FPS 插件扩展功能，本指南介绍插件的目录结构、模块生命周期、依赖注入模式、路由注册和认证集成。"
tags: [plugin, development, fps, module, extension, custom-plugin]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: fps_kernels
    resource: /references/fps-kernels-source.md
    title: fps-kernels 实现信源
  - id: noauth
    resource: /references/noauth-source.md
    title: NoAuth 实现信源
  - id: main
    resource: /references/main-module-source.md
    title: JupyverseModule 主模块信源
---

# 插件开发指南

Jupyverse 基于 FPS（FastAPI Plugin System）实现插件化架构。开发插件意味着创建一个 FPS Module，可以注册路由、提供服务实现、注册配置和扩展现有功能。

## 插件目录结构

一个标准的 Jupyverse 插件采用 API-Plugin 双层结构：

```
my-feature/
├── pyproject.toml              # 包配置和 entry points
└── src/
    └── fps_my_feature/         # 插件包（fps_ 前缀）
        ├── __init__.py
        ├── config.py           # 配置类（可选）
        ├── main.py             # FPS Module 入口
        └── routes.py           # 路由和服务实现
```

## Step 1：定义配置类

配置类继承 `Config`（即 Pydantic BaseModel，`extra="forbid"`）：

```python
from jupyverse_api.config import Config

class MyFeatureConfig(Config):
    greeting: str = "Hello"
    enable_feature_x: bool = False
    max_items: int = 100
```

## Step 2：实现服务类（继承 ABC 或 Router）

如果插件提供新的 API 端点，创建服务类继承 `Router`：

```python
from jupyverse_api.app import App
from jupyverse_auth import Auth, User
from jupyverse_api.router import Router
from fastapi import APIRouter, Depends
from .config import MyFeatureConfig

class _MyFeature(Router):
    def __init__(
        self,
        app: App,
        auth: Auth,
        config: MyFeatureConfig,
    ):
        super().__init__(app=app)
        self.config = config
        router = APIRouter()

        @router.get("/api/my-feature/greet")
        async def greet(
            name: str = "World",
            user: User = Depends(auth.current_user()),
        ):
            return {"message": f"{config.greeting}, {name}!"}

        @router.get("/api/my-feature/status")
        async def status(
            user: User = Depends(
                auth.current_user(permissions={"my_feature": ["read"]})
            ),
        ):
            return {"enabled": config.enable_feature_x, "max_items": config.max_items}

        self.include_router(router)
```

如果插件实现已有的抽象接口（如 Auth、Contents），继承对应的 ABC：

```python
from jupyverse_auth import Auth, User
from jupyverse_api.app import App

class _MyAuth(Auth):
    def current_user(self, permissions=None):
        async def _():
            # 实现认证逻辑
            return User(username="custom-user", name="Custom User")
        return _

    async def update_user(self):
        async def _(user: User):
            # 实现用户更新逻辑
            pass
        return _

    def websocket_auth(self, permissions=None):
        async def _(websocket):
            # 实现 WebSocket 认证
            await websocket.accept()
            return websocket, permissions
        return _
```

## Step 3：创建 FPS Module

Module 是插件的入口，负责依赖注入和生命周期管理：

```python
from fps import Module
from jupyverse_api.app import App
from jupyverse_auth import Auth
from .config import MyFeatureConfig
from .routes import _MyFeature

class MyFeatureModule(Module):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.config = MyFeatureConfig(**kwargs)

    async def prepare(self) -> None:
        # 1. 注册配置（供其他模块获取）
        self.put(self.config, MyFeatureConfig)

        # 2. 获取依赖
        app = await self.get(App)
        auth = await self.get(Auth)  # type: ignore[type-abstract]

        # 3. 创建服务实例
        service = _MyFeature(app, auth, self.config)

        # 4. 注册服务（附带清理回调）
        self.put(service, MyFeature, teardown_callback=service.stop if hasattr(service, 'stop') else None)

        self.done()
```

### 对于替换抽象实现的插件（如 Auth）

```python
class MyAuthModule(Module):
    async def prepare(self) -> None:
        app = await self.get(App)
        auth = _MyAuth(app)
        self.put(auth, Auth)  # 注册为 Auth 类型，其他模块获取 Auth 时得到本实例
```

## Step 4：注册 entry point

在 `pyproject.toml` 中声明插件：

```toml
[project.entry-points."jupyverse.modules"]
my_feature = "fps_my_feature.main:MyFeatureModule"
```

安装包后，Jupyverse 会自动发现并加载该插件。

## Step 5：配置包元数据

```toml
[project]
name = "fps-my-feature"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fps>=0.6.3",
    "jupyverse-api>=0.14.0",
    "fastapi",
]
```

## 生命周期最佳实践

### prepare() 中的异步任务

```python
async def prepare(self) -> None:
    service = _MyService()
    self.put(service, MyService)

    async with create_task_group() as tg:
        tg.start_soon(service.background_loop)  # 启动后台任务
        self.done()  # 标记 prepare 完成，任务组内的任务继续运行
```

### teardown_callback 清理资源

```python
async def stop_service(service):
    await service.close()

self.put(service, MyService, teardown_callback=stop_service)
```

## 依赖注入模式

### 获取可选依赖

```python
try:
    yjs = await self.get(Yjs)
    has_yjs = True
except Exception:
    yjs = None
    has_yjs = False
```

### 条件注册

```python
if self.config.collaborative:
    # 仅在协作模式下注册 Yjs 相关服务
    self.put(collab_service, CollabService)
```

## 路由注册注意事项

1. **路径冲突**：App 类自动检测路径冲突，确保路由路径不与其他插件重复。建议使用前缀如 `/api/my-feature/`。
2. **权限声明**：在路由装饰器中通过 `auth.current_user(permissions=...)` 声明权限。
3. **静态文件**：使用 `self.mount(path, app)` 挂载静态文件目录。
4. **WebSocket**：使用 `@router.websocket()` 注册 WebSocket 端点，使用 `auth.websocket_auth()` 认证。

## 测试插件

### 开发模式安装

```bash
pip install -e .
```

### 启动时启用/禁用

```bash
# 启用自定义插件（自动发现，无需额外参数）
jupyverse

# 如果插件与其他插件互斥，禁用其他实现
jupyverse --disable auth
```

### 验证加载

启动后查看日志确认插件已加载，或访问端点验证功能：

```bash
curl http://127.0.0.1:8000/api/my-feature/greet?name=Jupyverse
```

## 现有插件参考

| 插件 | 模式 | 参考价值 |
|------|------|---------|
| fps-noauth | Auth 替换实现 | 最简单的认证后端 |
| fps-kernels | 核心服务实现 | 复杂服务+后台任务+WebSocket |
| fps-contents | 核心服务实现 | 文件操作+ResourceLock |
| fps-yjs | 核心服务实现 | WebSocket+CRDT 协作 |
| fps-terminals | 核心服务实现 | 子进程+WebSocket |

## 相关概念

- [FPS 模块系统](03-fps-module-system.md) — Module 生命周期和依赖注入详解
- [App 与 Router 基础设施](04-app-and-router.md) — 路由注册和路径冲突检测
- [认证授权系统](05-auth-system.md) — Auth ABC 和权限模型
- [架构总览](02-architecture-overview.md) — 插件在整体架构中的位置
