---
type: Concept
title: "认证授权系统"
description: "Jupyverse 的认证系统基于 Auth 抽象基类，支持多种认证后端（Token、Fief、JupyterHub、NoAuth），通过细粒度权限字典控制 HTTP 和 WebSocket 端点访问。"
tags: [auth, authentication, authorization, permissions, token, fief, jupyterhub, noauth]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: auth_api
    resource: /references/auth-api-source.md
    title: Auth API 信源
  - id: noauth
    resource: /references/noauth-source.md
    title: NoAuth 实现信源
  - id: contents
    resource: /references/contents-api-source.md
    title: Contents API 信源
---

# 认证授权系统

Jupyverse 的认证系统设计为**抽象接口 + 可插拔后端**，所有端点通过统一的 Auth 接口进行权限校验，支持多种认证方式。

## Auth 抽象基类

Auth ABC 定义了三个核心方法：

```python
class Auth(ABC):
    @abstractmethod
    def current_user(self, permissions: dict[str, list[str]] | None = None) -> Callable: ...

    @abstractmethod
    async def update_user(self) -> Callable: ...

    @abstractmethod
    def websocket_auth(
        self, permissions: dict[str, list[str]] | None = None,
    ) -> Callable[[Any], Awaitable[tuple[Any, dict[str, list[str]] | None] | None]]: ...
```

### current_user() — HTTP 端点认证

`current_user()` 返回一个 FastAPI Dependency，用于 HTTP 端点的认证和授权：

```python
@router.get("/api/contents/{path:path}")
async def get_content(
    path: str,
    user: User = Depends(auth.current_user(permissions={"contents": ["read"]})),
) -> Content:
    return await self.get_content(path, content, user)
```

如果用户未认证或权限不足，FastAPI 自动返回 401/403 响应。认证通过后返回 User 对象。

### websocket_auth() — WebSocket 认证

`websocket_auth()` 返回 WebSocket 专用的认证依赖：

```python
@router.websocket("/api/kernels/{kernel_id}/channels")
async def kernel_channels(
    kernel_id, session_id,
    websocket_permissions=Depends(
        auth.websocket_auth(permissions={"kernels": ["execute"]})
    ),
):
    return await self.kernel_channels(kernel_id, session_id, websocket_permissions)
```

返回值是 `(websocket, permissions)` 元组，WebSocket 端点接受连接后可使用。

### update_user() — 用户设置更新

`update_user()` 返回更新用户设置（如 workspace、settings 字段）的依赖。

## 权限模型

权限使用 `{resource: [actions]}` 字典格式：

| 资源 (resource) | 动作 (actions) | 使用场景 |
|-----------------|---------------|---------|
| `contents` | `read`, `write` | 文件/目录的读取和修改 |
| `kernels` | `read`, `write`, `execute` | 内核查看、管理和代码执行 |
| `sessions` | `read`, `write` | 会话查看和管理 |
| `kernelspecs` | `read` | 内核规格查看 |
| `terminals` | `read`, `write`, `execute` | 终端管理和交互 |
| `yjs` | `read`, `write` | 协作文档同步 |
| `status` | `read` | 服务器状态查看 |

### 权限粒度示例

```python
# 只读操作：只需 read 权限
Depends(auth.current_user(permissions={"contents": ["read"]}))

# 写操作：需要 write 权限
Depends(auth.current_user(permissions={"contents": ["write"]}))

# WebSocket 执行：需要 execute 权限
Depends(auth.websocket_auth(permissions={"kernels": ["execute"]}))

# 不指定 permissions：只需认证，不需要特定权限
Depends(auth.current_user())
```

## User 模型

```python
class User(BaseModel):
    username: str = ""
    name: str = ""
    display_name: str = ""
    initials: str | None = None
    color: str | None = None
    avatar_url: str | None = None
    workspace: str = "{}"    # JSON 字符串，存储工作区布局
    settings: str = "{}"      # JSON 字符串，存储用户设置
```

User 对象通过 `current_user()` 依赖注入到端点处理函数中，可用于获取当前用户信息和个性化设置。

## 认证后端

Jupyverse 提供四种认证后端，通过安装不同的插件和禁用其他插件来选择：

### 1. NoAuth（无认证）

```bash
pip install "jupyverse[jupyterlab,noauth]"
jupyverse --disable auth --disable auth_fief --disable auth_jupyterhub
```

NoAuth 返回空 User 对象（所有字段为空字符串），所有请求都通过认证，适用于本地开发和测试环境。

```python
class _NoAuth(Auth):
    def current_user(self, *args, **kwargs):
        async def _():
            return USER  # 返回全局空 User
        return _
```

**注意**：NoAuth 模式下所有用户共享同一个 User 对象，`update_user()` 的修改对所有连接可见。

### 2. Token Auth（fps-auth）

```bash
pip install "jupyverse[jupyterlab,auth]"
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth
```

Token 模式使用基于 token 的认证，通过 `fps-auth` 插件实现，底层使用 `fastapi-users` 库进行用户管理。支持：
- 用户名/密码登录
- Token 自动注入 URL 查询参数
- 用户数据库（SQLite）自动创建
- 测试模式自动创建 admin 用户（`admin@jupyter.com`/`jupyverse`）

### 3. Fief Auth（fps-auth-fief）

[Fief](https://www.fief.dev/) 是一个开源的 OAuth2/OIDC 身份管理服务，适用于需要完整用户管理功能的部署。

### 4. JupyterHub Auth（fps-auth-jupyterhub）

与 JupyterHub 集成，使用 JupyterHub 的认证体系，适用于 JupyterHub spawned 服务场景。

## 认证后端选择指南

| 场景 | 推荐后端 | 说明 |
|------|---------|------|
| 本地开发/测试 | NoAuth | 零配置，直接使用 |
| 单用户部署 | Token Auth | 简单的 token 认证 |
| 多用户/团队部署 | Fief | 完整 OAuth2/用户管理 |
| JupyterHub 集成 | JupyterHub Auth | 复用 Hub 认证 |

## 在自定义插件中使用 Auth

开发自定义插件时，在 Router 的端点中使用 auth 依赖：

```python
from jupyverse_auth import Auth, User
from fastapi import APIRouter, Depends

class MyFeature(Router, ABC):
    def __init__(self, app: App, auth: Auth):
        super().__init__(app)
        router = APIRouter()

        @router.get("/api/my-feature")
        async def get_feature(
            user: User = Depends(auth.current_user(permissions={"my_feature": ["read"]})),
        ):
            return await self.get_feature(user)

        self.include_router(router)
```

在 Module 中获取 Auth 依赖：

```python
class MyFeatureModule(Module):
    async def prepare(self) -> None:
        auth = await self.get(Auth)  # type: ignore[type-abstract]
        app = await self.get(App)
        service = _MyFeature(app, auth)
        self.put(service, MyFeature)
```

## 相关概念

- [FPS 模块系统](03-fps-module-system.md) — Auth 如何通过依赖注入获取
- [Contents 文件服务](06-contents-service.md) — 文件端点如何使用权限控制
- [内核管理](07-kernel-management.md) — 内核端点的权限模型
- [插件开发指南](12-plugin-development.md) — 自定义插件中的认证使用
