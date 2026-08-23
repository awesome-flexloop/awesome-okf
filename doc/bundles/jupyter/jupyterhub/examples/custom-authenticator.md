---
type: Example
title: 自定义 Authenticator 认证器
description: 从零开始实现 JupyterHub v6.0.0b2 自定义认证器，包括最小实现、字典认证、管理员支持、auth_state 持久化和自定义登录表单
tags: [jupyterhub, example, authenticator, custom-auth, authentication, extension]
sources:
  - id: auth-source
    resource: ../references/auth-source.md
    title: JupyterHub 认证器体系源码参考
generated: { by: reference_agent/source-code-to-okf-wiki, at: "2026-08-22" }
status: stable
stale_after: "2027-08-22"
---

# 自定义 Authenticator 认证器

本示例将指导你从零开始实现一个 JupyterHub 自定义认证器（Authenticator），涵盖最小实现、基于字典的用户名/密码认证、管理员支持、auth_state 持久化和自定义登录表单。

> **前置知识**：建议先阅读 [Authenticator 认证系统](../concepts/authenticator.md) 理解认证器基类的核心方法和认证流程。

## 1. 自定义 Authenticator 的基本结构

所有自定义认证器必须继承 `jupyterhub.auth.Authenticator` 基类。基类继承自 `traitlets.config.LoggingConfigurable`，提供了日志和配置能力。

### 核心方法概览

自定义认证器必须或可选实现的方法：

| 方法 | 必须实现 | 说明 |
|------|:--------:|------|
| `authenticate(handler, data)` | ✅ | 核心认证方法，验证用户名和密码 |
| `check_allowed(username, authentication)` | ❌ | 白名单检查，基类已有默认实现 |
| `is_admin(handler, authentication)` | ❌ | 管理员判定，基类已有默认实现 |
| `refresh_user(user, handler)` | ❌ | 刷新认证信息（如 token 续期） |
| `validate_username(username)` | ❌ | 用户名规范化校验 |
| `pre_spawn_start(user, spawner)` | ❌ | Spawn 前钩子 |
| `post_spawn_stop(user, spawner)` | ❌ | Stop 后钩子 |

## 2. 最小实现示例

以下是一个最简单的自定义认证器，只实现了必须的 `authenticate()` 方法：

```python
# my_authenticator.py
from jupyterhub.auth import Authenticator
from traitlets import Unicode


class HelloAuthenticator(Authenticator):
    """最简单的自定义认证器：接受特定用户名和密码"""

    # 可配置的密码（通过 traitlets 暴露到配置文件）
    password = Unicode(
        default_value="jupyter123",
        config=True,
        help="允许登录的密码",
    )

    async def authenticate(self, handler, data):
        """验证用户名和密码。

        参数:
            handler: Tornado RequestHandler 对象
            data: 登录表单提交的字典，包含 'username' 和 'password'

        返回:
            - str: 认证成功的用户名
            - dict: 认证成功，包含 name 和可选的 auth_state
            - None: 认证失败
        """
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username:
            return None

        # 简单密码验证
        if password == self.password:
            return username  # 认证成功，返回用户名

        return None  # 认证失败
```

### 在配置文件中使用

```python
# jupyterhub_config.py
import sys
sys.path.insert(0, '/path/to/directory/containing/my_authenticator')

c.JupyterHub.authenticator_class = 'my_authenticator.HelloAuthenticator'
c.HelloAuthenticator.password = 'mysecretpassword'
c.Authenticator.allow_all = True
c.JupyterHub.spawner_class = 'simple'
```

## 3. 使用字典存储用户的简单用户名/密码认证器

下面实现一个更实用的认证器，使用字典存储用户凭据，并支持管理员配置：

```python
# dict_authenticator.py
import hashlib
import secrets
from jupyterhub.auth import Authenticator
from traitlets import Dict, Set, Bool, Unicode


class DictAuthenticator(Authenticator):
    """基于内存字典的用户名/密码认证器。

    用户凭据存储在 Python 字典中，密码使用 SHA-256 哈希存储。
    适用于小型部署、测试环境或用户数量有限的场景。
    """

    # 用户凭据字典：{username: {"password_hash": str, "is_admin": bool}}
    users = Dict(
        default_value={},
        config=True,
        help="用户凭据字典，格式：{username: {'password_hash': '...', 'is_admin': bool}}",
    )

    # 管理员用户名集合（与 users 字典中的 is_admin 标志配合使用）
    admin_users = Set(
        default_value=set(),
        config=True,
        help="管理员用户名集合",
    )

    # 是否自动添加通过认证的新用户到白名单
    allow_all = Bool(
        default_value=False,
        config=True,
        help="允许所有通过密码验证的用户登录",
    )

    @staticmethod
    def _hash_password(password, salt=None):
        """对密码进行 SHA-256 哈希（带盐）。

        注意：生产环境应使用 bcrypt 或 argon2 等专业密码哈希库。
        """
        if salt is None:
            salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256(f"{salt}{password}".encode("utf-8"))
        return f"{salt}${hash_obj.hexdigest()}"

    @staticmethod
    def _verify_password(password, password_hash):
        """验证密码是否匹配哈希值。"""
        salt, expected_hash = password_hash.split("$", 1)
        actual_hash = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
        return secrets.compare_digest(actual_hash, expected_hash)

    def add_user(self, username, password, is_admin=False):
        """添加用户到字典中（可在初始化时调用）。"""
        self.users[username] = {
            "password_hash": self._hash_password(password),
            "is_admin": is_admin,
        }

    async def authenticate(self, handler, data):
        """验证用户名和密码。"""
        username = data.get("username", "").strip().lower()
        password = data.get("password", "")

        if not username or not password:
            return None

        # 检查用户是否存在于字典中
        user_record = self.users.get(username)
        if user_record is None:
            self.log.warning(f"登录失败：用户 '{username}' 不存在")
            return None

        # 验证密码
        if not self._verify_password(password, user_record["password_hash"]):
            self.log.warning(f"登录失败：用户 '{username}' 密码错误")
            return None

        # 认证成功，返回用户名
        self.log.info(f"用户 '{username}' 认证成功")
        return username

    def check_allowed(self, username, authentication=None):
        """检查用户是否被允许登录。"""
        if not self.allow_all:
            # 如果未开启 allow_all，只允许字典中存在的用户
            if username not in self.users:
                # 同时检查基类的 admin_users
                if username not in self.admin_users:
                    return False
        return super().check_allowed(username, authentication)

    def is_admin(self, handler, authentication):
        """判断用户是否为管理员。"""
        username = authentication.get("name", "")

        # 检查字典中的 is_admin 标志
        user_record = self.users.get(username, {})
        if user_record.get("is_admin", False):
            return True

        # 检查 admin_users 集合
        if username in self.admin_users:
            return True

        return super().is_admin(handler, authentication)
```

### 使用示例

```python
# jupyterhub_config.py
import sys
sys.path.insert(0, '/path/to/dict_authenticator')

from dict_authenticator import DictAuthenticator

# 创建认证器实例并添加用户
c.JupyterHub.authenticator_class = DictAuthenticator

# 通过配置添加用户（密码需预先哈希）
# 或者在配置文件中动态创建
auth = DictAuthenticator()
auth.add_user("admin", "admin123", is_admin=True)
auth.add_user("user1", "user123")
auth.add_user("user2", "user456")
c.DictAuthenticator.users = auth.users
c.DictAuthenticator.admin_users = {"admin"}

# 使用 SimpleLocalProcessSpawner 进行测试
c.JupyterHub.spawner_class = 'simple'
```

> **注意**：在实际生产环境中，密码哈希应使用 `bcrypt` 或 `argon2-cffi` 库，而非简单的 SHA-256。详见第 8 节安全注意事项。

## 4. 添加管理员支持

上例中已展示了基本的管理员判定。以下是更完善的管理员支持，包括动态管理员判定和 RBAC 集成：

```python
# admin_authenticator.py
from jupyterhub.auth import Authenticator
from traitlets import Set, Callable


class AdminAwareAuthenticator(Authenticator):
    """支持动态管理员判定的认证器。"""

    # 静态管理员集合
    admin_users = Set(
        default_value=set(),
        config=True,
        help="管理员用户名集合",
    )

    # 管理员组名称集合（用于 LDAP/数据库场景的组级管理员判定）
    admin_groups = Set(
        default_value=set(),
        config=True,
        help="管理员用户组集合",
    )

    def is_admin(self, handler, authentication):
        """判断用户是否为管理员。

        authentication 字典包含:
            - name: 用户名
            - auth_state: 认证状态（如果启用）
            - admin: 已设置的管理员标志
        """
        username = authentication.get("name", "")
        auth_state = authentication.get("auth_state", {}) or {}

        # 1. 检查静态管理员集合
        if username in self.admin_users:
            return True

        # 2. 检查用户所属组（auth_state 中存储的组信息）
        user_groups = set(auth_state.get("groups", []))
        if user_groups & self.admin_groups:
            return True

        # 3. 委托给基类检查
        return super().is_admin(handler, authentication)
```

## 5. 配置 auth_state 存储额外用户信息

auth_state 用于持久化认证过程中获取的敏感信息（如 OAuth token、用户属性等），加密存储在数据库中。

```python
# auth_state_authenticator.py
from jupyterhub.auth import Authenticator


class AuthStateAuthenticator(Authenticator):
    """演示 auth_state 用法的认证器。"""

    async def authenticate(self, handler, data):
        username = data.get("username", "").strip()
        password = data.get("password", "")

        # 假设这里进行了实际的凭据验证
        if not self._verify(username, password):
            return None

        # 模拟从外部系统获取用户信息
        user_info = await self._fetch_user_info(username)

        # 返回字典格式，包含 auth_state
        return {
            "name": username,
            # auth_state 会被加密存储在数据库中
            "auth_state": {
                "user_id": user_info.get("id"),
                "email": user_info.get("email"),
                "full_name": user_info.get("full_name"),
                "groups": user_info.get("groups", []),
                "access_token": user_info.get("access_token"),
                "refresh_token": user_info.get("refresh_token"),
                "token_expires_at": user_info.get("expires_at"),
            },
        }

    async def pre_spawn_start(self, user, spawner):
        """Spawn 前钩子：从 auth_state 中读取信息并设置环境变量。"""
        # 从用户对象中获取 auth_state
        auth_state = await user.get_auth_state()
        if not auth_state:
            return

        # 将 access token 注入单用户服务器环境变量
        spawner.environment["ACCESS_TOKEN"] = auth_state.get("access_token", "")
        spawner.environment["USER_EMAIL"] = auth_state.get("email", "")

    async def refresh_user(self, user, handler=None):
        """刷新认证信息：检查 token 是否过期，过期则刷新。"""
        auth_state = await user.get_auth_state()
        if not auth_state:
            return True  # 无 auth_state，无需刷新

        import time
        expires_at = auth_state.get("token_expires_at", 0)

        # 如果 token 即将过期（5分钟内），刷新 token
        if expires_at and expires_at < time.time() + 300:
            new_token = await self._refresh_access_token(
                auth_state.get("refresh_token")
            )
            if new_token is None:
                return False  # 刷新失败，用户应被注销

            # 更新 auth_state
            auth_state["access_token"] = new_token["access_token"]
            auth_state["token_expires_at"] = new_token["expires_at"]
            return {"auth_state": auth_state}

        return True  # 刷新成功，无更新

    async def _fetch_user_info(self, username):
        """模拟从外部系统获取用户信息。"""
        return {"id": 1, "email": f"{username}@example.com", "groups": ["users"]}

    async def _refresh_access_token(self, refresh_token):
        """模拟刷新 access token。"""
        return None

    def _verify(self, username, password):
        """模拟凭据验证。"""
        return True
```

在配置文件中启用 auth_state：

```python
# jupyterhub_config.py
c.Authenticator.enable_auth_state = True

# auth_state 加密密钥（生产环境必须设置，使用 openssl rand -hex 32 生成）
c.JupyterHub.cookie_secret = b'your-secret-key-at-least-32-bytes-long!'

# 配置 token 刷新策略
c.Authenticator.auth_refresh_age = 300  # 每 5 分钟检查一次
c.Authenticator.refresh_pre_spawn = True  # Spawn 前强制刷新
```

## 6. 注册自定义认证器

### 方式一：直接使用 Python 路径（开发/测试）

将认证器文件放在 Python 路径中，直接在配置文件中指定完整路径：

```python
# jupyterhub_config.py
import sys
sys.path.insert(0, '/path/to/my/authenticator/directory')

c.JupyterHub.authenticator_class = 'my_auth_module.MyCustomAuthenticator'
```

### 方式二：通过 Entry Points 注册（推荐用于分发包）

在 `pyproject.toml` 中声明 entry point：

```toml
[project.entry-points."jupyterhub.authenticators"]
dictauth = "dict_authenticator:DictAuthenticator"
```

在 `setup.py` 中声明（旧格式）：

```python
setup(
    name="jupyterhub-dict-auth",
    ...
    entry_points={
        "jupyterhub.authenticators": [
            "dictauth = dict_authenticator:DictAuthenticator",
        ],
    },
)
```

安装包后即可在配置中使用短名称：

```python
c.JupyterHub.authenticator_class = 'dictauth'
# 或等价的完整类名
c.JupyterHub.authenticator_class = 'dict_authenticator.DictAuthenticator'
```

JupyterHub 内置的认证器短名称参考：

| 短名称 | 类 |
|--------|-----|
| `pam` / `default` | PAMAuthenticator |
| `dummy` | DummyAuthenticator |
| `null` | NullAuthenticator |
| `shared-password` | SharedPasswordAuthenticator |

## 7. 测试自定义认证器

### 7.1 单元测试

```python
# test_my_authenticator.py
import pytest
from tornado.testing import AsyncTestCase
from my_authenticator import HelloAuthenticator


class TestHelloAuthenticator(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.auth = HelloAuthenticator(password="test123")

    async def test_correct_password(self):
        """测试正确密码认证成功。"""
        handler = None  # 测试中可传入 mock handler
        data = {"username": "testuser", "password": "test123"}
        result = await self.auth.authenticate(handler, data)
        assert result == "testuser"

    async def test_wrong_password(self):
        """测试错误密码认证失败。"""
        data = {"username": "testuser", "password": "wrongpass"}
        result = await self.auth.authenticate(None, data)
        assert result is None

    async def test_empty_username(self):
        """测试空用户名认证失败。"""
        data = {"username": "", "password": "test123"}
        result = await self.auth.authenticate(None, data)
        assert result is None

    async def test_is_admin(self):
        """测试管理员判定。"""
        self.auth.admin_users = {"admin"}
        auth_dict = {"name": "admin"}
        assert self.auth.is_admin(None, auth_dict) is True

        auth_dict = {"name": "regular_user"}
        assert self.auth.is_admin(None, auth_dict) is False
```

### 7.2 集成测试

启动 JupyterHub 后，使用 curl 模拟登录请求：

```bash
# 获取登录页面（提取 _xsrf token）
curl -c cookies.txt http://localhost:8000/hub/login

# 提交登录表单
curl -v -b cookies.txt -c cookies.txt \
  -d "username=admin&password=admin123&_xsrf=<xsrf_token>" \
  http://localhost:8000/hub/login

# 验证登录成功（访问 /hub/home 应返回 200）
curl -b cookies.txt http://localhost:8000/hub/home
```

### 7.3 健康检查

```bash
curl http://localhost:8000/hub/health
```

## 8. 进阶：自定义登录表单模板

默认情况下，JupyterHub 使用内置的登录表单。你可以通过自定义 HTML 模板来修改登录页面：

### 8.1 创建自定义模板

创建自定义模板目录和 `login.html` 文件：

```
templates/
└── login.html
```

```html
<!-- templates/login.html -->
{% extends "page.html" %}

{% block login_widget %}
<div class="container">
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card mt-5">
        <div class="card-header">
          <h3 class="text-center">自定义登录</h3>
        </div>
        <div class="card-body">
          {% if login_error %}
          <div class="alert alert-danger">{{ login_error }}</div>
          {% endif %}

          <form method="post" action="{{ login_url }}">
            <div class="mb-3">
              <label for="username_input" class="form-label">用户名</label>
              <input type="text" class="form-control" id="username_input"
                     name="username" placeholder="请输入用户名" required autofocus>
            </div>
            <div class="mb-3">
              <label for="password_input" class="form-label">密码</label>
              <input type="password" class="form-control" id="password_input"
                     name="password" placeholder="请输入密码" required>
            </div>
            <div class="d-grid">
              <button type="submit" class="btn btn-primary">登录</button>
            </div>
          </form>

          <div class="mt-3 text-center text-muted">
            <small>由自定义认证器提供支持</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

### 8.2 配置自定义模板路径

在认证器类中指定自定义模板，或在配置文件中设置：

```python
# 方式一：在认证器类中设置模板路径
class MyCustomAuthenticator(Authenticator):
    # 覆盖默认模板目录
    template_dir = Unicode(
        default_value="/path/to/templates",
        config=True,
        help="自定义模板目录路径",
    )

# 方式二：在 jupyterhub_config.py 中设置全局模板路径
c.JupyterHub.template_paths = ['/path/to/templates']
```

### 8.3 使用 auto_login 跳转到外部认证

对于 OAuth/SSO 等第三方认证场景，可以设置 `auto_login = True` 跳过登录页直接重定向：

```python
class SSOCAuthenticator(Authenticator):
    auto_login = True  # 访问时自动跳转到 SSO 登录
    login_service = "企业 SSO"  # 登录按钮显示文字（当 auto_login=False 时）

    async def authenticate(self, handler, data=None):
        """处理 OAuth 回调。"""
        # 1. 检查是否是回调请求（code 参数）
        code = handler.get_argument("code", None)
        if code is None:
            # 2. 没有 code，重定向到 SSO 授权 URL
            auth_url = self._build_auth_url(handler)
            handler.redirect(auth_url)
            return None

        # 3. 有 code，用 code 换取 token
        token = await self._exchange_code(code)
        user_info = await self._get_user_info(token)

        return {
            "name": user_info["login"],
            "auth_state": {"access_token": token},
        }
```

## 9. 注意事项

### 9.1 密码安全（哈希存储）

**绝不以明文存储密码**。推荐使用专业的密码哈希库：

```bash
pip install bcrypt
# 或
pip install argon2-cffi
```

```python
import bcrypt

# 哈希密码（注册时）
def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt)

# 验证密码（登录时）
def verify_password(password: str, password_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash)
```

安全要点：

- 使用 bcrypt/argon2 等慢哈希算法，**不要使用 SHA-256 等快速哈希**存储密码
- 每个密码使用独立的盐值（bcrypt 自动处理）
- 设置合理的工作因子（bcrypt rounds ≥ 12）
- 不要在日志中输出密码或 token
- auth_state 中存储的敏感信息会被自动加密，但仍需注意 `cookie_secret` 的保护

### 9.2 异步支持

JupyterHub 基于 Tornado 异步框架，所有 I/O 操作必须使用 `async/await`：

```python
async def authenticate(self, handler, data):
    # ✅ 正确：使用异步 HTTP 客户端
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(auth_url, json=data) as resp:
            result = await resp.json()

    # ❌ 错误：使用同步 requests 库会阻塞事件循环
    # import requests
    # resp = requests.post(auth_url, json=data)  # 这会阻塞！
```

要点：

- 使用 `aiohttp` 或 `tornado.httpclient.AsyncHTTPClient` 进行 HTTP 请求
- 使用 `asyncio` 原语进行异步操作
- 数据库操作使用异步驱动（如 `asyncpg` for PostgreSQL）
- 如果必须调用同步阻塞代码，使用 `await asyncio.get_event_loop().run_in_executor(None, sync_func)` 包装

### 9.3 用户名规范化

默认用户名模式为 `r'^[a-z][a-z0-9._-]{2,}$'`（以小写字母开头，3 字符以上）。自定义认证器应处理用户名规范化：

```python
def validate_username(self, username):
    """自定义用户名规范化。"""
    # 转换为小写
    username = username.lower().strip()
    # 从邮箱中提取用户名
    if "@" in username:
        username = username.split("@")[0]
    return super().validate_username(username)
```

### 9.4 错误处理

认证失败时，返回 `None` 并记录日志：

```python
async def authenticate(self, handler, data):
    try:
        return await self._do_authenticate(data)
    except Exception as e:
        self.log.error(f"认证异常：{e}", exc_info=True)
        return None  # 返回 None 表示认证失败
```

## 源码溯源

- [Authenticator 认证系统](../concepts/authenticator.md) — 认证器基类的完整方法参考、配置项和认证流程
- [JupyterHub 认证器体系源码参考](../references/auth-source.md) — Authenticator 基类及内置认证器的 API 参考
