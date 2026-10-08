---
type: concept
title: "认证体系"
description: "深入理解 cozepy 的四种认证方式——PAT Token、JWT、Web OAuth、PKCE OAuth 和设备码流程，以及同步/异步认证类的选择。"
tags: [auth, token, jwt, oauth, pkce, device-flow, security]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-002
    resource: /references/auth-model.md
    title: "认证体系参考"
  - id: F-cp-001
    resource: /references/coze-client.md
    title: "Coze 客户端入口与基础设施参考"
---

# 认证体系

cozepy 的认证体系设计覆盖了从个人开发到企业级应用的全场景需求。SDK 提供了简单 Token 认证、JWT 服务端认证和三种 OAuth 2.0 授权流程（Web 授权码、PKCE、设备码），每种认证方式都有同步和异步两个版本。理解认证体系是使用 SDK 的第一步——`Coze`/`AsyncCoze` 构造函数的第一个参数就是认证实例。

## 认证继承体系

所有认证类统一在 `Auth` 基类下，分为 `SyncAuth`（同步）和 `AsyncAuth`（异步）两大分支。认证类的职责是为每个 HTTP 请求注入正确的 Authorization 头部。

```
Auth
├── SyncAuth
│   ├── TokenAuth           — PAT/API Token（最简单）
│   ├── JWTAuth             — JWT 服务端认证
│   ├── WebOAuthApp         — Web 授权码流程
│   ├── PKCEOAuthApp        — PKCE 流程（公共客户端）
│   └── DeviceOAuthApp      — 设备码流程（输入受限设备）
│
└── AsyncAuth
    ├── AsyncTokenAuth
    ├── AsyncJWTAuth
    ├── AsyncJWTOAuthApp
    ├── AsyncWebOAuthApp
    ├── AsyncPKCEOAuthApp
    └── AsyncDeviceOAuthApp
```

选择原则很简单：用 `Coze` 就选 `SyncAuth` 子类，用 `AsyncCoze` 就选 `AsyncAuth` 子类。

## TokenAuth：最简单的入门方式

`TokenAuth`（异步版本 `AsyncTokenAuth`）使用个人访问令牌（Personal Access Token, PAT）或 API Token 直接认证，适用于脚本开发、测试、个人工具等场景。

```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

# 中国区
coze = Coze(auth=TokenAuth(token="pat_xxxxxxxxxxxx"), base_url=COZE_CN_BASE_URL)

# 国际区（默认）
coze = Coze(auth=TokenAuth(token="pat_xxxxxxxxxxxx"))
```

获取 PAT 的方式：登录 Coze 平台 → 个人设置 → API 令牌 → 生成新令牌。TokenAuth 的优点是零配置，缺点是 token 绑定个人账号，不适合多用户场景。

## JWTAuth：企业级服务端认证

`JWTAuth`（异步版本 `AsyncJWTAuth`）和 `JWTOAuthApp`/`AsyncJWTOAuthApp` 适用于企业级应用的服务端到服务端认证场景。JWT 认证通过 RSA 签名的 JSON Web Token 进行身份验证，适合后台服务、定时任务等没有用户交互的场景。

与 TokenAuth 不同，JWT 认证不需要预先生成固定的 token，而是使用应用的私钥动态签名生成 JWT，安全性更高。JWT 有过期时间，可以自动刷新。

## OAuth 2.0 授权框架

当你的应用需要代表 Coze 用户访问其资源时（而非使用开发者自己的账号），需要使用 OAuth 2.0 流程。SDK 提供了三种 OAuth 流程，对应不同的应用类型：

### Web OAuth（WebOAuthApp）

适用于**有后端服务器的 Web 应用**。标准授权码流程：

1. 将用户重定向到 Coze 授权页面
2. 用户同意授权后，Coze 回调到你的 redirect_uri，携带 authorization_code
3. 后端用 code 换取 access_token

这是最经典的 OAuth 流程，需要 client_secret 保存在服务端，因此仅适用于有安全后端的应用。

### PKCE OAuth（PKCEOAuthApp）

适用于**公共客户端**——桌面应用、移动端 App、单页应用（SPA）、CLI 工具等无法安全存储 client_secret 的场景。PKCE（Proof Key for Code Exchange，发音"pixy"）通过动态生成的 code_verifier 和 code_challenge 对来防止授权码截获攻击。

PKCE 流程的关键步骤：

```python
from cozepy import PKCEOAuthApp
from cozepy.util import gen_s256_code_challenge
import secrets

# 1. 生成 code_verifier 和 code_challenge
code_verifier = secrets.token_urlsafe(32)
code_challenge = gen_s256_code_challenge(code_verifier)

# 2. 构造授权 URL，引导用户访问（携带 code_challenge，不携带 code_verifier）
oauth_app = PKCEOAuthApp(client_id="your_client_id")
auth_url = oauth_app.get_oauth_url(
    redirect_uri="http://localhost:8080/callback",
    code_challenge=code_challenge,
)
# → 引导浏览器访问 auth_url

# 3. 用户授权后，从回调 URL 获取 code
# 4. 使用 code + code_verifier 换取 token
oauth_token = oauth_app.get_access_token(
    grant_type="authorization_code",
    code="received_code",
    redirect_uri="http://localhost:8080/callback",
    code_verifier=code_verifier,  # 只有这一步才发送 code_verifier
)
```

轮询 PKCE token 时可能遇到 `CozePKCEAuthError`，错误类型由 `CozePKCEAuthErrorType` 枚举定义：
- `AUTHORIZATION_PENDING`：用户还没授权，继续轮询
- `SLOW_DOWN`：请求太频繁，增加间隔
- `ACCESS_DENIED`：用户拒绝授权
- `EXPIRED_TOKEN`：设备码过期，需重新发起

### Device OAuth（DeviceOAuthApp）

适用于**输入受限设备**——智能电视、CLI 工具、IoT 设备、游戏主机等场景。用户在这些设备上不方便输入用户名密码，设备码流程允许用户在另一台设备（手机/电脑）上完成授权。

流程如下：

```python
from cozepy import DeviceOAuthApp

oauth_app = DeviceOAuthApp(client_id="your_client_id")

# 1. 获取设备码
device_code = oauth_app.get_device_code(scope="...")
print(f"请访问 {device_code.verification_uri} 并输入代码: {device_code.user_code}")

# 2. 轮询等待用户授权
import time
while True:
    try:
        token = oauth_app.get_access_token(device_code=device_code.device_code)
        print("授权成功！")
        break
    except CozePKCEAuthError as e:
        if e.error == CozePKCEAuthErrorType.AUTHORIZATION_PENDING:
            time.sleep(device_code.interval)
            continue
        elif e.error == CozePKCEAuthErrorType.SLOW_DOWN:
            time.sleep(device_code.interval + 5)
            continue
        else:
            raise
```

用户体验是：CLI 打印一个 URL 和一个用户码 → 用户在电脑/手机浏览器打开 URL → 输入用户码 → 点击授权 → CLI 轮询成功。

## OAuthToken 模型

无论哪种 OAuth 流程，最终都会返回 `OAuthToken` 对象：

| 字段 | 类型 | 说明 |
|------|------|------|
| `access_token` | `str` | 用于 API 调用的访问令牌 |
| `refresh_token` | `str` | 刷新令牌（用于获取新的 access_token） |
| `expires_in` | `int` | access_token 有效期（秒） |
| `token_type` | `str` | 通常为 "Bearer" |
| `scope` | `str` | 授权的权限范围 |

拿到 `OAuthToken` 后，可以将其 `access_token` 传入 `TokenAuth` 来构造客户端：

```python
coze = Coze(auth=TokenAuth(token=oauth_token.access_token), base_url=COZE_CN_BASE_URL)
```

## load_oauth_app_from_config 工厂函数

对于需要根据配置动态选择 OAuth 类型的场景，可以使用 `load_oauth_app_from_config()` 工厂函数，传入配置字典即可自动创建对应的 OAuth 应用实例：

```python
from cozepy import load_oauth_app_from_config

config = {
    "client_id": "xxx",
    "client_secret": "xxx",
    "app_type": "web",  # 或 "pkce" / "device"
    "redirect_uri": "http://localhost:8080/callback",
}
oauth_app = load_oauth_app_from_config(config)
```

## 认证方式选择决策

| 使用场景 | 推荐方式 | 理由 |
|----------|---------|------|
| 个人脚本/快速测试 | `TokenAuth` | 零配置，一行代码搞定 |
| 服务端后台任务 | `JWTAuth` | 无需用户交互，安全性高 |
| Web 应用（有后端） | `WebOAuthApp` | 标准授权码流程，client_secret 安全存储在后端 |
| 桌面应用/CLI/SPA | `PKCEOAuthApp` | 公共客户端，PKCE 防止授权码截获 |
| 智能电视/IoT设备 | `DeviceOAuthApp` | 用户在其他设备上完成授权 |

## 相关概念

- [客户端初始化](02-client-init.md) — 认证实例创建后如何初始化客户端
- [基础对话示例](../examples/basic-chat.md) — 使用 TokenAuth 发起对话的完整示例
- [OAuth PKCE 认证示例](../examples/oauth-pkce-auth.md) — PKCE 和设备码流程的完整可运行示例
- [认证体系参考](../references/auth-model.md) — 所有认证类和模型的完整 API 文档
