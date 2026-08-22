---
type: Reference
title: "auth/ 认证授权源码信源"
description: "Jupyter Server 2.0 认证授权体系：IdentityProvider、Authorizer、User 模型与登录登出 Handler"
tags: [auth, authentication, authorization, identity, security, password]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: identity-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/auth/identity.py
    title: jupyter_server/auth/identity.py
  - id: authorizer-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/auth/authorizer.py
    title: jupyter_server/auth/authorizer.py
  - id: security-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/auth/security.py
    title: jupyter_server/auth/security.py
  - id: login-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/auth/login.py
    title: jupyter_server/auth/login.py
  - id: logout-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/auth/logout.py
    title: jupyter_server/auth/logout.py
---

# auth/ 认证授权源码信源

## 模块结构

```
auth/
├── __init__.py
├── __main__.py
├── authorizer.py      # 授权器接口
├── decorator.py       # 认证装饰器
├── identity.py        # 身份提供者接口（v2.0 核心）
├── login.py           # 登录 Handler
├── logout.py          # 登出 Handler
├── security.py        # 密码哈希与验证
└── utils.py           # 工具函数
```

## User 数据类 (identity.py L43)

```python
@dataclass
class User:
    username: str          # 必填：用户名
    name: str = ""         # 真实姓名
    display_name: str = "" # 显示名/昵称
    initials: str | None = None  # 首字母缩写
    avatar_url: str | None = None # 头像 URL
    color: str | None = None     # 用户颜色
```

`__post_init__` 自动调用 `fill_defaults()` 填充缺失字段。

## IdentityProvider (identity.py L118)

v2.0 新增的认证层抽象，替代旧的 login_handler 模式。

**核心配置项**：
| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `cookie_name` | Unicode | `username-${Host}` | Cookie 名称 |
| `cookie_options` | Dict | {} | set_secure_cookie 参数 |
| `secure_cookie` | Bool | None | 是否仅 HTTPS Cookie |
| `token` | Unicode | 随机生成 | 认证 Token |
| `login_available` | Bool | True | 是否显示登录页面 |
| `login_handler_class` | Type | LoginFormHandler | 登录 Handler |
| `token_generated_from_cmdline` | Bool | False | Token 是否命令行生成 |

**核心方法**：
| 方法 | 说明 |
|------|------|
| `get_user(handler)` | 返回 User 对象或 None（认证入口） |
| `identity_model(user)` | User → JSON dict 序列化 |
| `get_cookie_name(handler)` | 获取 Cookie 名称 |
| `set_login_cookie(handler, user)` | 设置登录 Cookie |
| `clear_login_cookie(handler)` | 清除登录 Cookie |
| `is_token_authenticated(handler)` | 是否 Token 认证 |
| `should_check_origin(handler)` | 是否检查 Origin 头 |
| `validate_security(handler, obj, action)` | 安全验证钩子 |
| `get_handlers(app)` | 返回认证相关 Handlers |

### PasswordIdentityProvider (identity.py L631)

基于密码的身份提供者，默认实现。

额外配置：
- `password`: Unicode，空字符串。哈希后的密码
- `hashed_password`: Bool，False。密码是否已哈希
- `allow_password_change`: Bool，True。允许修改密码
- `password_set`: Bool，动态属性。密码是否已设置

### LegacyIdentityProvider (identity.py L769)

兼容 v1.x 的旧登录处理方式，继承 PasswordIdentityProvider。

## Authorizer (authorizer.py L26)

授权接口，控制用户对资源的访问权限。

**核心方法**：
| 方法 | 说明 |
|------|------|
| `is_authorized(handler, user, action, resource)` | 判断是否授权（返回 bool 协程） |
| `get_permissions(handler, user)` | 获取用户权限模型（返回 dict 协程） |

### AllowAllAuthorizer (authorizer.py L74)

默认实现，允许所有认证用户执行所有操作。

## security.py 密码工具

| 函数 | 说明 |
|------|------|
| `set_password(password)` | 使用 argon2-cffi 哈希密码 |
| `passwd_check(hashed_password, password)` | 验证密码是否匹配 |
| `cache_security_check()` | 检查安全配置（Token/密码设置情况） |

## 登录/登出 Handler

- `LoginFormHandler(login.py L18)`: GET 显示登录表单，POST 验证密码
- `LegacyLoginHandler(login.py L108)`: 兼容旧版登录
- `LogoutHandler(logout.py L9)`: 清除登录 Cookie，重定向到登录页

## auth/decorator.py 装饰器

- `@allow_unauthenticated`: 标记方法/Handler 不需要认证
- `@authorized`: 标记需要授权检查，会调用 authorizer.is_authorized
- `@ws_authenticated`: WebSocket 认证装饰器
