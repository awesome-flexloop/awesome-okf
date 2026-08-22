---
type: Concept
title: "认证授权系统"
description: "Jupyter Server 2.0 全新安全架构：IdentityProvider 认证层与 Authorizer 授权层分离、User 模型、Token/密码认证、自定义安全后端"
tags: [auth, authentication, authorization, identity, security, password, token]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: auth
    resource: /references/auth-source.md
    title: auth/ 认证授权源码信源
---

# 认证授权系统

Jupyter Server 2.0 引入了**认证与授权分离**的安全架构，取代了 v1.x 中单一 login_handler 的设计。新架构将"你是谁"（认证）和"你能做什么"（授权）解耦，支持更灵活的安全扩展。

## 核心概念

### 认证（Authentication）vs 授权（Authorization）

| 维度 | IdentityProvider | Authorizer |
|------|-----------------|------------|
| 回答的问题 | 你是谁？ | 你能做什么？ |
| 输入 | HTTP 请求（Cookie/Token/Header） | 用户对象 + 操作 + 资源 |
| 输出 | User 对象 或 None | bool（允许/拒绝） |
| 默认实现 | PasswordIdentityProvider | AllowAllAuthorizer |

## User 数据模型

v2.0 使用 `@dataclass` 定义的 User 类表示用户身份：

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    username: str                    # 必填：唯一用户名
    name: str = ""                   # 真实姓名
    display_name: str = ""           # 显示名/昵称
    initials: Optional[str] = None   # 首字母缩写
    avatar_url: Optional[str] = None # 头像 URL
    color: Optional[str] = None      # 用户颜色（UI标识）
```

`__post_init__` 自动填充缺失字段：如果 `name` 为空则用 `username`，`display_name` 为空则用 `name`。

向后兼容：`_backward_compat_user()` 函数支持从旧版的字符串用户名或 dict 转换为 User 对象。

## IdentityProvider（认证层）

`IdentityProvider` 是所有认证方式的抽象基类，定义了认证流程的标准接口。

### 核心配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `cookie_name` | Unicode | `username-${Host}` | 认证 Cookie 名称 |
| `cookie_options` | Dict | {} | set_secure_cookie 参数 |
| `secure_cookie` | Bool | None | 是否仅 HTTPS（None=自动检测） |
| `token` | Unicode | 随机生成 | 认证 Token |
| `login_available` | Bool | True | 是否提供登录页面 |
| `login_handler_class` | Type | LoginFormHandler | 登录 Handler 类 |

### 核心方法

| 方法 | 说明 |
|------|------|
| `get_user(handler)` | **认证入口**：从请求中提取用户，返回 User 或 None |
| `identity_model(user)` | User → JSON dict（/api/me 端点返回） |
| `get_cookie_name(handler)` | 获取 Cookie 名称 |
| `set_login_cookie(handler, user)` | 设置登录 Cookie |
| `clear_login_cookie(handler)` | 清除登录 Cookie |
| `is_token_authenticated(handler)` | 请求是否使用 Token 认证 |
| `should_check_origin(handler)` | 是否检查 Origin 头（Token 认证可跳过） |
| `validate_security(handler, obj, action)` | 请求前安全验证钩子 |
| `handlers(app)` | 返回认证相关 URL Handlers |

### 认证流程

```
请求到达 Handler.prepare()
    │
    ▼
identity_provider.get_user(handler)
    │
    ├── 检查 URL 参数 ?token=xxx
    ├── 检查 Authorization: token xxx 头
    ├── 检查 Cookie
    └── 检查自定义认证方式
    │
    ├── 返回 User → 请求继续处理
    └── 返回 None → 重定向到 login_url 或返回 403
```

### PasswordIdentityProvider（默认实现）

`PasswordIdentityProvider` 是默认的认证提供者，支持**密码 + Token 双模式**。

#### Token 认证

启动时自动生成随机 Token（可通过 `--IdentityProvider.token=xxx` 设置），通过以下方式传递：
- URL 参数：`?token=abc123`
- 请求头：`Authorization: token abc123`
- Cookie：`_xsrf` Cookie 中存储 Token

设置 `--IdentityProvider.token=''` 可禁用 Token 认证（仅限开发环境）。

#### 密码认证

密码使用 `argon2-cffi` 库哈希存储：

```bash
# 设置密码
jupyter server password
```

密码哈希存储在 `jupyter_config_dir/jupyter_server_config.json`：

```json
{
  "IdentityProvider": {
    "hashed_password": "argon2:$argon2id$v=19$m=10240,t=10,p=8$..."
  }
}
```

登录流程：
1. GET `/login` → 显示登录表单
2. POST `/login` → 验证密码 → 设置 Cookie → 重定向
3. 后续请求通过 Cookie 认证

### LegacyIdentityProvider

兼容 v1.x 的旧登录处理方式，继承 `PasswordIdentityProvider`，提供向后兼容的 `login_handler_class` 接口。

## Authorizer（授权层）

`Authorizer` 控制已认证用户对资源的访问权限。

### 核心方法

```python
class Authorizer(LoggingConfigurable):
    async def is_authorized(self, handler, user, action, resource):
        """判断用户是否有权执行操作
        返回 True/False
        """
        return True  # 默认允许所有

    async def get_permissions(self, handler, user):
        """返回用户的权限模型
        用于前端 UI 权限控制
        """
        return {}
```

`is_authorized` 在每次请求被 `@authorized` 装饰器标记的 Handler 方法时调用：
- `handler`: 当前 RequestHandler
- `user`: User 对象
- `action`: 字符串动作（如 `'read'`、`'write'`、`'execute'`）
- `resource`: 资源标识（如文件路径、kernel_id）

### AllowAllAuthorizer（默认实现）

默认授权器，允许所有已认证用户执行任何操作。适用于个人开发环境。

### 自定义 Authorizer

生产环境应实现细粒度授权控制：

```python
from jupyter_server.auth.authorizer import Authorizer

class MyAuthorizer(Authorizer):
    async def is_authorized(self, handler, user, action, resource):
        # 只读用户只能读取
        if user.username.startswith("readonly_") and action != "read":
            return False
        # 只允许访问自己目录下的文件
        if resource and not resource.startswith(f"/home/{user.username}/"):
            return False
        return True
```

## 安全配置最佳实践

### 生产环境安全清单

| 配置 | 推荐值 | 说明 |
|------|--------|------|
| `ServerApp.allow_remote_access` | True（需要远程访问时） | 允许非 localhost 访问 |
| `IdentityProvider.token` | 强随机 Token | 不要使用空字符串 |
| `ServerApp.password` | argon2 哈希密码 | 设置密码 |
| `ServerApp.certfile` | SSL 证书路径 | 启用 HTTPS |
| `ServerApp.keyfile` | SSL 密钥路径 | 启用 HTTPS |
| `ServerApp.disable_check_xsrf` | False | 保持 XSRF 保护开启 |
| `ServerApp.allow_origin` | 具体域名 | 不要用 `'*'` |
| `ServerApp.allow_credentials` | True（需要跨域认证） | CORS 凭证 |

### CORS 跨域配置

```python
# 允许特定来源
c.ServerApp.allow_origin = "https://myapp.example.com"

# 允许多个来源（用列表）
c.ServerApp.allow_origin = ["https://app1.example.com", "https://app2.example.com"]

# 允许所有来源（仅限开发！）
c.ServerApp.allow_origin = "*"
c.ServerApp.allow_credentials = False  # 通配符时必须禁用凭证
```

### 自定义认证示例

```python
from jupyter_server.auth.identity import IdentityProvider, User
import requests

class OAuthIdentityProvider(IdentityProvider):
    """通过 OAuth 令牌认证"""

    def get_user(self, handler):
        token = handler.request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return None
        # 调用 OAuth 服务验证
        resp = requests.get("https://auth.example.com/userinfo",
                          headers={"Authorization": f"Bearer {token}"})
        if resp.status_code != 200:
            return None
        info = resp.json()
        return User(
            username=info["sub"],
            name=info.get("name", ""),
            display_name=info.get("preferred_username", info["sub"]),
        )
```

## 安全警告

- **永远不要在生产环境中设置 `token=''`**：这会禁用所有认证
- **不要在公网暴露无密码的 Jupyter Server**：任何人都可以执行任意代码
- **使用 HTTPS**：Token 和密码在 HTTP 下以明文传输
- **定期更新密码**：使用 `jupyter server password` 定期更换
- **不要直接以 root 运行**：使用普通用户 + `--allow-root` 仅在容器环境

## 相关概念

- [Handler 继承体系](04-handler-hierarchy.md) — 认证在请求处理链中的位置
- [部署与安全](15-deployment-and-security.md) — 生产部署安全指南
