---
type: Reference
title: "NoAuth 实现信源"
description: "无认证后端实现，提供匿名访问的 Auth 实现，返回空 User 对象，适用于开发和本地使用。"
tags: [noauth, authentication, anonymous, backend]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: noauth_backends
    resource: /external/libs/jupyter/jupyverse/plugins/noauth/src/fps_noauth/backends.py
    title: fps_noauth/backends.py
  - id: noauth_main
    resource: /external/libs/jupyter/jupyverse/plugins/noauth/src/fps_noauth/main.py
    title: fps_noauth/main.py
---

# NoAuth 实现信源

## _NoAuth 类

fps-noauth 插件提供最简单的认证后端——无认证，所有请求都返回同一个匿名用户。

```python
USER = User()

class _NoAuth(Auth):
    def current_user(self, *args, **kwargs):
        async def _():
            return USER
        return _

    def websocket_auth(self, permissions=None):
        async def _(websocket: WebSocket):
            return websocket, permissions
        return _

    async def update_user(self):
        async def _(data: dict[str, Any]) -> User:
            global USER
            user = dict(USER)
            user.update(data)
            USER = User(**user)
            return USER
        return _
```

### 行为说明

- `current_user()`：直接返回空 User 对象（所有字段为空字符串/None）
- `websocket_auth()`：接受 WebSocket 连接，直接返回 (websocket, permissions) 元组
- `update_user()`：支持更新全局 USER 对象的属性（如 workspace、settings）

### 使用场景

- 本地开发和测试
- 已通过其他方式（如反向代理）处理认证的部署
- 完全公开的 Jupyter 实例

### 注意

使用 noauth 时，所有访问者共享同一个 User 对象，`update_user()` 的修改对所有连接可见。
