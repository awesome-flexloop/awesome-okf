---
title: 集成自定义认证
type: example
bundle: jupyter-notebook
chapter: "04"
difficulty: advanced
tags: ["authentication", "security", "backend", "login", "token"]
prerequisites: ["02-server-extension"]
sources: ["F-026"]
related_concepts: ["04-handlers", "07-jupyterhub-integration"]
---

# 04 | 集成自定义认证

本教程展示如何为Jupyter Notebook实现自定义认证机制，包括自定义登录页面、Token验证和API认证。适用于企业部署场景。

## 前置条件

- 已阅读[开发服务端扩展](02-server-extension.md)
- 理解Jupyter Server认证机制
- Python 3.10+

## Jupyter Server认证机制概述

Jupyter Notebook/Jupyter Server默认使用token-based认证：

1. 启动时生成一个随机token
2. URL中必须包含 `?token=xxx` 参数
3. 首次访问时设置cookie，后续请求通过cookie认证
4. 可选设置密码（hash存储）

认证流程：

```
浏览器请求页面
    │
    ├─→ 有有效cookie？ ──是──→ 允许访问
    │
    └─→ 有有效token参数？ ──是──→ 设置cookie → 允许访问
    │
    └─→ 都没有？ ──→ 重定向到 /login
                        │
                        └─→ 用户提交凭证 → 验证 → 设置cookie → 重定向
```

认证由 `IdentityProvider` 类控制，可以替换为自定义实现。

## 方式一：配置文件方式（简单）

### 设置密码

```bash
# 生成密码哈希
python -c "from jupyter_server.auth import passwd; print(passwd('your-password'))"
```

```python
# jupyter_server_config.py
c.ServerApp.password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$...'
c.ServerApp.token = ''  # 禁用token，使用密码登录
c.ServerApp.open_browser = False
```

### 禁用认证（仅开发环境！）

```python
c.ServerApp.token = ''
c.ServerApp.password = ''
c.ServerApp.disable_check_xsrf = True
```

**⚠️ 警告**: 绝不在生产环境禁用认证！

## 方式二：自定义IdentityProvider（推荐）

创建自定义认证提供者，支持多种认证方式（如企业SSO、LDAP、OAuth等）。

### 第一步：创建扩展结构

```
jupyter_custom_auth/
├── pyproject.toml
├── jupyter_custom_auth/
│   ├── __init__.py
│   ├── auth.py           # 自定义IdentityProvider
│   ├── handlers.py       # 自定义登录Handler
│   └── templates/
│       └── login.html    # 自定义登录页面
```

### 第二步：实现自定义IdentityProvider

```python
"""jupyter_custom_auth/auth.py"""
from jupyter_server.auth import IdentityProvider
from jupyter_server.auth.identity import User
from tornado import web
from typing import Optional, Any


class CustomIdentityProvider(IdentityProvider):
    """自定义认证提供者"""

    # 设置登录页面处理类
    login_handler = ...  # 在handlers中定义

    def get_user(self, handler: web.RequestHandler) -> Optional[User]:
        """从请求中获取认证用户"""

        # 1. 检查cookie
        user = self._get_user_from_cookie(handler)
        if user:
            return user

        # 2. 检查token参数（兼容默认行为）
        token_user = super().get_user(handler)
        if token_user:
            return token_user

        # 3. 检查自定义认证头（API调用）
        auth_header = handler.request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            api_token = auth_header[7:]
            if self._validate_api_token(api_token):
                return User(username='api-user', name='API User')

        return None

    def _get_user_from_cookie(self, handler: web.RequestHandler) -> Optional[User]:
        """从自定义cookie中获取用户"""
        # 实现你的cookie验证逻辑
        # 例如：验证JWT token、session ID等
        encrypted_session = handler.get_cookie('jupyter_session')
        if not encrypted_session:
            return None

        try:
            # 解密并验证session
            # session_data = decrypt_and_verify(encrypted_session, secret_key)
            # return User(username=session_data['username'])
            return None  # 实际实现时替换
        except Exception:
            return None

    def _validate_api_token(self, token: str) -> bool:
        """验证API token"""
        # 实现你的API token验证逻辑
        # 例如：查数据库、调用外部认证服务
        valid_tokens = {'my-secret-api-token'}  # 示例：实际应从配置/数据库读取
        return token in valid_tokens

    def validate_security(self, handler: web.RequestHandler, uri: str = '',
                         referer: str = '') -> None:
        """安全验证（CSRF等）"""
        # 可以自定义CSRF逻辑
        super().validate_security(handler, uri, referer)
```

### 第三步：实现登录Handler

```python
"""jupyter_custom_auth/handlers.py"""
import json
from jupyter_server.base.handlers import JupyterHandler
from tornado import web
from typing import Any


class CustomLoginHandler(JupyterHandler):
    """自定义登录页面"""

    def get(self) -> None:
        """GET /login - 显示登录页面"""
        # 获取错误消息（如果有）
        error = self.get_argument('error', '')

        # 如果已登录，重定向到next参数
        if self.current_user:
            next_url = self.get_argument('next', '/tree')
            self.redirect(next_url)
            return

        # 渲染登录页面
        html = self.render_template(
            "login.html",
            error=error,
            next_url=self.get_argument('next', '/tree'),
            base_url=self.base_url,
        )
        self.write(html)

    async def post(self) -> None:
        """POST /login - 处理登录提交"""
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        next_url = self.get_argument('next', '/tree')

        # 验证凭证（这里是示例，实际应查数据库或调用认证服务）
        if await self._authenticate(username, password):
            # 认证成功，设置cookie
            self._set_session_cookie(username)
            self.redirect(next_url)
        else:
            # 认证失败，重定向回登录页
            self.redirect(f"/login?error=Invalid+credentials&next={next_url}")

    async def _authenticate(self, username: str, password: str) -> bool:
        """验证用户名密码"""
        # 示例1：简单的硬编码验证（不推荐生产使用）
        # return username == 'admin' and password == 'admin123'

        # 示例2：调用外部认证服务
        # response = await http_client.fetch(
        #     'https://auth.example.com/verify',
        #     method='POST',
        #     body=json.dumps({'username': username, 'password': password})
        # )
        # result = json.loads(response.body)
        # return result.get('success', False)

        # 示例3：LDAP验证
        # import ldap
        # conn = ldap.initialize('ldap://ldap.example.com')
        # try:
        #     conn.simple_bind_s(f'uid={username},ou=users,dc=example,dc=com', password)
        #     return True
        # except ldap.INVALID_CREDENTIALS:
        #     return False

        return False  # 替换为实际认证逻辑

    def _set_session_cookie(self, username: str) -> None:
        """设置认证cookie"""
        # 创建session数据
        session_data = {
            'username': username,
            # 可添加更多信息：角色、过期时间等
        }

        # 示例：使用JWT
        # import jwt
        # token = jwt.encode(session_data, SECRET_KEY, algorithm='HS256')
        # self.set_cookie(
        #     'jupyter_session',
        #     token,
        #     httponly=True,
        #     secure=True,  # HTTPS环境下启用
        #     samesite='Lax',
        #     max_age=86400,  # 24小时
        #     path=self.base_url
        # )
        pass


class LogoutHandler(JupyterHandler):
    """登出Handler"""

    @web.authenticated
    def get(self) -> None:
        """GET /logout - 登出"""
        # 清除cookie
        self.clear_cookie('jupyter_session', path=self.base_url)
        self.redirect('/login')
```

### 第四步：创建登录页面模板

创建 `templates/login.html`（可以使用Jinja2模板继承或独立HTML）：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login - Jupyter Notebook</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            width: 360px;
        }
        .logo {
            text-align: center;
            margin-bottom: 24px;
            font-size: 24px;
            color: #f37726;
        }
        .form-group {
            margin-bottom: 16px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            color: #333;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        input:focus {
            outline: none;
            border-color: #f37726;
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 16px;
            font-size: 14px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #f37726;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            margin-top: 8px;
        }
        button:hover {
            background: #e5671a;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🪐 Jupyter Notebook</div>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="{{ base_url }}login">
            <input type="hidden" name="next" value="{{ next_url }}">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Sign In</button>
        </form>
    </div>
</body>
</html>
```

### 第五步：扩展入口

```python
"""jupyter_custom_auth/__init__.py"""
from ._version import __version__


def _jupyter_server_extension_points():
    return [{"module": "jupyter_custom_auth"}]


def _load_jupyter_server_extension(server_app):
    """加载扩展，替换认证提供者"""
    from .auth import CustomIdentityProvider
    from .handlers import CustomLoginHandler, LogoutHandler

    # 替换IdentityProvider
    server_app.identity_provider = CustomIdentityProvider(
        parent=server_app,
        log=server_app.log
    )

    # 注册自定义login/logout路由
    web_app = server_app.web_app
    base_url = web_app.settings.get("base_url", "/").rstrip("/")

    # 注意：需要移除默认的login handler，然后添加自定义的
    # 这里通过添加到handlers来覆盖
    web_app.add_handlers(".*$", [
        (base_url + "/login", CustomLoginHandler),
        (base_url + "/logout", LogoutHandler),
    ])

    # 添加模板目录
    import os
    from pathlib import Path
    template_dir = str(Path(__file__).parent / "templates")
    env = web_app.settings.get("jinja2_env")
    if env:
        env.loader.searchpath.append(template_dir)

    server_app.log.info("Custom auth extension loaded!")
```

### 第六步：配置pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "jupyter-custom-auth"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "jupyter_server>=2.0",
]

[project.entry-points."jupyter_server.extensions"]
custom-auth = "jupyter_custom_auth"
```

### 第七步：安装和启用

```bash
pip install -e .

# 禁用默认token认证
jupyter notebook --ServerApp.token='' \
    --ServerApp.password='' \
    --ServerApp.disable_check_xsrf=False
```

## 方式三：OAuth/SSO集成

对于企业场景，通常需要集成OAuth2/OIDC认证：

```python
class OAuthIdentityProvider(IdentityProvider):
    """OAuth2/OIDC认证提供者"""

    login_handler = OAuthLoginHandler

    def get_user(self, handler):
        # 1. 检查是否有OAuth回调code
        code = handler.get_argument('code', None)
        if code:
            return self._handle_oauth_callback(handler, code)

        # 2. 检查session cookie
        user = self._get_user_from_cookie(handler)
        if user:
            return user

        # 3. 重定向到OAuth授权页面
        if not handler.request.path.endswith('/oauth/callback'):
            self._redirect_to_oauth(handler)
            return None

        return None

    def _redirect_to_oauth(self, handler):
        """重定向到OAuth授权端点"""
        auth_url = (
            f"https://auth.example.com/authorize?"
            f"client_id={CLIENT_ID}&"
            f"redirect_uri={handler.base_url}oauth/callback&"
            f"response_type=code&"
            f"state={generate_state()}"
        )
        handler.redirect(auth_url)

    async def _handle_oauth_callback(self, handler, code):
        """处理OAuth回调，交换token获取用户信息"""
        # 用code交换access_token
        # 用access_token获取用户信息
        # 设置session cookie
        # 返回User对象
        pass
```

## 安全最佳实践

### 1. Cookie安全设置

```python
self.set_cookie(
    'jupyter_session',
    token,
    httponly=True,       # 阻止JavaScript访问cookie
    secure=True,         # HTTPS环境下必须启用
    samesite='Lax',      # 防止CSRF
    max_age=86400,       # 过期时间
    path=self.base_url   # 限定cookie路径
)
```

### 2. HTTPS强制

在生产环境中始终使用HTTPS：

```python
c.ServerApp.certfile = '/path/to/cert.pem'
c.ServerApp.keyfile = '/path/to/key.pem'
```

### 3. 密码存储

永远不要明文存储密码：

```python
# 使用argon2或bcrypt哈希
from jupyter_server.auth import passwd
hashed = passwd('password', algorithm='argon2')
```

### 4. CORS配置

```python
c.ServerApp.allow_origin = 'https://your-domain.com'
c.ServerApp.allow_credentials = True
```

### 5. 认证日志

记录所有认证事件：

```python
self.log.info(f"User {username} logged in from {handler.request.remote_ip}")
self.log.warning(f"Failed login attempt for {username} from {handler.request.remote_ip}")
```

## API认证

对于REST API调用，推荐使用Bearer Token认证：

```python
# 在get_user中添加
auth_header = handler.request.headers.get('Authorization', '')
if auth_header.startswith('Bearer '):
    token = auth_header[7:]
    if self._validate_api_token(token):
        return User(username='api')

# 前端API调用
fetch('/api/contents', {
    headers: {
        'Authorization': 'Bearer ' + apiToken
    },
    credentials: 'include'
});
```

生成API Token可以通过：
- 配置文件中的静态token
- 数据库存储的用户token
- JWT token（包含用户信息和过期时间）

## 与JupyterHub配合

如果在JupyterHub下运行，**不要自定义Notebook端的认证**。JupyterHub负责认证，Notebook只需要：

1. 检测到 `hub_prefix` 设置（自动完成，F-026）
2. token在page_config中被清空（安全措施，F-026）
3. 认证由Hub统一管理

自定义认证应该在JupyterHub层面实现（自定义Authenticator）。

## 测试自定义认证

```bash
# 使用curl测试登录
curl -c cookies.txt -X POST http://localhost:8888/login \
    -d "username=admin&password=admin123&next=/tree"

# 使用cookie访问API
curl -b cookies.txt http://localhost:8888/api/contents

# 使用API Token访问
curl -H "Authorization: Bearer my-secret-api-token" \
    http://localhost:8888/api/kernels
```

## 常见问题

### Q: 自定义登录页面不生效？

检查：
1. 扩展是否正确加载（查看启动日志）
2. IdentityProvider是否正确替换了server_app.identity_provider
3. 模板目录是否正确添加到Jinja2 loader
4. 路由是否覆盖了默认的/login

### Q: 登录后无限重定向？

通常是因为cookie设置不正确（如path、domain不匹配），或者 `get_user()` 始终返回None导致循环重定向到/login。

### Q: WebSocket连接失败？

WebSocket连接也需要认证。确保cookie对WebSocket连接生效，或者在WebSocket URL中包含token参数。

### Q: API请求返回403？

检查：
1. CSRF token是否正确（对于POST/PUT/DELETE请求）
2. `X-XSRFToken` 头是否设置
3. API Token是否有效

## 参考资源

- [Jupyter Server Security](https://jupyter-server.readthedocs.io/en/latest/operators/security.html)
- [JupyterHub Authenticators](https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html)
- [tornado.web.authenticated](https://www.tornadoweb.org/en/stable/web.html#tornado.web.authenticated)
