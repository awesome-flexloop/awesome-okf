---
type: Reference
title: JupyterHub 认证器体系源码参考
description: Authenticator 基类及内置认证器（PAM/Dummy/Null/SharedPassword）的 API 参考
tags: [auth, authenticator, pam, oauth, authentication]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T21:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: auth-source
    resource: https://github.com/jupyterhub/jupyterhub/blob/main/jupyterhub/auth.py
    title: jupyterhub/auth.py
---

# Authenticator 认证器体系源码参考

## Authenticator 基类

继承自 `traitlets.config.LoggingConfigurable`。

### 核心配置 Traitlets

| Traitlet | 类型 | 默认值 | 说明 |
|----------|------|--------|------|
| `enable_auth_state` | Bool | `False` | 启用加密持久化 auth_state |
| `auth_refresh_age` | Integer | `300` | 认证信息刷新间隔（秒） |
| `refresh_pre_spawn` | Bool | `False` | Spawn 前强制刷新认证 |
| `refresh_pre_stop` | Bool | `False` | Stop 前强制刷新认证 |
| `admin_users` | Set | `set()` | 管理员用户集合 |
| `allowed_users` | Set | `set()` | 允许登录的用户集合 |
| `blocked_users` | Set | `set()` | 禁止登录的用户集合 |
| `allow_all` | Bool | `False` | 允许所有用户登录 |
| `allow_existing_users` | Bool | `False` | 允许数据库中已有用户登录 |
| `auto_login` | Bool | `False` | 自动跳转登录（无登录页） |
| `delete_invalid_users` | Bool | `False` | 自动删除无效用户 |
| `username_pattern` | Unicode | `r'^[a-z][a-z0-9._-]{2,}$'` | 用户名正则校验 |
| `minimum_password_length` | Integer | `1` | 最小密码长度 |

### 核心方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `authenticate` | `async (handler, data) → username/dict/None` | 抽象方法，子类必须实现认证逻辑 |
| `get_authenticated_user` | `async (handler, data) → dict/None` | 核心认证流程，返回认证用户 dict |
| `refresh_user` | `async (user, handler=None) → bool/dict` | 刷新用户认证信息 |
| `is_admin` | `(handler, authentication) → bool` | 判断用户是否为管理员 |
| `check_allowed` | `(username, authentication=None) → bool` | 检查用户是否在允许列表中 |
| `check_blocked_users` | `(username, authentication=None) → bool` | 检查用户是否被阻止 |
| `validate_username` | `(username) → username` | 验证并规范化用户名 |
| `add_user` | `(user)` | 添加用户钩子 |
| `delete_user` | `(user)` | 删除用户钩子 |
| `pre_spawn_start` | `async (user, spawner)` | Spawner 启动前钩子 |
| `post_spawn_stop` | `async (user, spawner)` | Spawner 停止后钩子 |
| `manage_groups` | `async (user) → dict` | 管理用户组成员关系 |

## 内置认证器

### PAMAuthenticator

继承链：`Authenticator → LocalAuthenticator → PAMAuthenticator`

- 使用操作系统 PAM（Pluggable Authentication Module）进行认证
- 默认认证器，适用于本地系统用户场景
- 支持 PAM 服务配置（`pam_service` trait）
- 通过 PAM 组成员判断管理员权限

### DummyAuthenticator

继承自 `Authenticator`。

- 测试用认证器，接受任意用户名和密码
- 不做任何验证，直接返回用户名
- 仅用于开发和测试环境，不可用于生产

### NullAuthenticator

继承自 `Authenticator`。

- 禁止所有登录的认证器
- `auto_login = True`，`authenticate()` 始终返回 `None`
- 用于完全禁用登录的场景

### SharedPasswordAuthenticator

位于 `jupyterhub/authenticators/shared.py`。

- 共享密码认证器，所有用户使用同一个密码
- 适用于简单的临时部署场景
