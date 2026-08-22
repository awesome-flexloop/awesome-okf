---
type: Reference
title: "Auth API 信源"
description: "认证授权抽象层，定义 Auth ABC、User 模型和 AuthConfig，支持 HTTP 和 WebSocket 两种认证模式。"
tags: [auth, authentication, authorization, abc, permissions]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: auth_init
    resource: /external/libs/jupyter/jupyverse/api/auth/src/jupyverse_auth/__init__.py
    title: jupyverse_auth/__init__.py
  - id: auth_models
    resource: /external/libs/jupyter/jupyverse/api/auth/src/jupyverse_auth/models.py
    title: jupyverse_auth/models.py
---

# Auth API 信源

## User 模型

```python
class User(BaseModel):
    username: str = ""
    name: str = ""
    display_name: str = ""
    initials: str | None = None
    color: str | None = None
    avatar_url: str | None = None
    workspace: str = "{}"
    settings: str = "{}"
```

User 是一个 Pydantic 模型，包含用户身份和界面偏好信息。`workspace` 和 `settings` 存储为 JSON 字符串。

## Auth 抽象基类

```python
class Auth(ABC):
    @abstractmethod
    def current_user(self, permissions: dict[str, list[str]] | None = None) -> Callable: ...

    @abstractmethod
    async def update_user(self) -> Callable: ...

    @abstractmethod
    def websocket_auth(
        self,
        permissions: dict[str, list[str]] | None = None,
    ) -> Callable[[Any], Awaitable[tuple[Any, dict[str, list[str]] | None] | None]]: ...
```

### 方法说明

| 方法 | 返回类型 | 用途 |
|------|---------|------|
| `current_user(permissions)` | FastAPI Dependency | HTTP 端点认证依赖，返回当前用户或抛出 403 |
| `update_user()` | FastAPI Dependency | 更新用户设置的依赖，返回更新函数 |
| `websocket_auth(permissions)` | WebSocket Dependency | WebSocket 认证依赖，返回 (websocket, permissions) 元组 |

### 权限格式

权限字典格式为 `{resource: [actions]}`，例如：

```python
{"contents": ["read", "write"]}
{"kernels": ["read", "write", "execute"]}
{"sessions": ["read", "write"]}
{"terminals": ["read", "write", "execute"]}
{"yjs": ["read", "write"]}
```

## AuthConfig

```python
class AuthConfig(Config):
    pass
```

认证配置基类，具体认证后端（如 Fief、JupyterHub）可扩展此类。

## 端点使用模式

在 Router ABC 的 `__init__` 中，认证通过 FastAPI 的 `Depends` 注入：

```python
@router.get("/api/contents/{path:path}")
async def get_content(
    path: str,
    user: User = Depends(auth.current_user(permissions={"contents": ["read"]})),
) -> Content:
    return await self.get_content(path, content, user)
```
