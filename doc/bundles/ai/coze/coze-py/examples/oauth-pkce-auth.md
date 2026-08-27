---
type: example
title: "OAuth PKCE 与设备码认证示例"
description: "演示 OAuth 2.0 PKCE 授权流程和设备码（Device Flow）认证的完整实现，包括 code_verifier 生成、授权 URL 构造、轮询 token 和错误处理。"
tags: [oauth, pkce, device-flow, token, auth, authorization]
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

# OAuth PKCE 与设备码认证示例

本示例演示两种 OAuth 2.0 认证流程：PKCE 流程（适用于桌面应用、CLI、SPA 等公共客户端）和设备码流程（适用于输入受限设备如智能电视、CLI 工具）。两种流程都不需要在客户端存储 client_secret，安全性更高。

## 前置准备

1. 在 Coze 开放平台创建 OAuth 应用
2. 获取 client_id（和 redirect_uri，PKCE 流程需要）
3. 对于设备码流程，不需要 redirect_uri
4. 安装 cozepy：`pip install cozepy`

## 完整代码

```python
import os
import sys
import time
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from cozepy import (
    Coze,
    TokenAuth,
    PKCEOAuthApp,
    DeviceOAuthApp,
    CozePKCEAuthError,
    CozePKCEAuthErrorType,
    COZE_CN_BASE_URL,
)
from cozepy.util import gen_s256_code_challenge


# ============================================================
# 示例 1：PKCE 授权流程（带本地回调服务器）
# ============================================================

# 全局变量用于在 HTTP 回调中接收 authorization_code
_received_code = None
_received_state = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP 回调处理器，接收 OAuth 授权码"""

    def do_GET(self):
        global _received_code, _received_state
        query = parse_qs(urlparse(self.path).query)

        if "code" in query:
            _received_code = query["code"][0]
            _received_state = query.get("state", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<html><body><h2>✅ 授权成功！</h2>"
                "<p>你可以关闭此窗口，返回命令行。</p>"
                "</body></html>".encode("utf-8")
            )
        elif "error" in query:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed")
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        """静默 HTTP 服务器日志"""
        pass


def pkce_auth_flow(client_id: str, redirect_port: int = 8080) -> str:
    """
    PKCE OAuth 授权流程完整实现。

    流程：
    1. 生成 code_verifier 和 code_challenge
    2. 构造授权 URL 并打开浏览器
    3. 启动本地 HTTP 服务器等待回调
    4. 用户授权后，从回调获取 code
    5. 使用 code + code_verifier 换取 access_token

    Args:
        client_id: OAuth 应用的 client_id
        redirect_port: 本地回调服务器端口

    Returns:
        access_token 字符串
    """
    global _received_code, _received_state
    _received_code = None
    _received_state = None

    redirect_uri = f"http://localhost:{redirect_port}/callback"

    # Step 1: 生成 PKCE 参数
    # code_verifier: 一个高熵随机字符串
    code_verifier = secrets.token_urlsafe(64)
    # code_challenge: code_verifier 的 SHA256 哈希，Base64URL 编码
    code_challenge = gen_s256_code_challenge(code_verifier)
    # state: 用于防止 CSRF 攻击
    state = secrets.token_urlsafe(16)

    # Step 2: 创建 PKCE OAuth 应用
    oauth_app = PKCEOAuthApp(
        client_id=client_id,
        base_url=COZE_CN_BASE_URL,
    )

    # Step 3: 构造授权 URL
    auth_url = oauth_app.get_oauth_url(
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
        state=state,
        scope="",  # 根据需要添加 scope
    )

    print("=" * 50)
    print("PKCE OAuth 授权流程")
    print("=" * 50)
    print(f"授权 URL: {auth_url}")
    print(f"正在打开浏览器...（如果没有自动打开，请手动复制上面的 URL）")

    # Step 4: 启动本地回调服务器并打开浏览器
    server = HTTPServer(("localhost", redirect_port), OAuthCallbackHandler)
    server.timeout = 120  # 2 分钟超时

    webbrowser.open(auth_url)

    # 等待回调
    print("等待授权回调...")
    while _received_code is None:
        server.handle_request()

    server.server_close()

    # 验证 state（防止 CSRF）
    if _received_state != state:
        raise RuntimeError("State 验证失败，可能存在 CSRF 攻击")

    auth_code = _received_code
    print(f"收到授权码: {auth_code[:20]}...")

    # Step 5: 使用授权码换取 access_token
    oauth_token = oauth_app.get_access_token(
        grant_type="authorization_code",
        code=auth_code,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
    )

    print(f"✅ 获取 access_token 成功！")
    print(f"   Token 类型: {oauth_token.token_type}")
    print(f"   有效期: {oauth_token.expires_in} 秒")
    if oauth_token.refresh_token:
        print(f"   Refresh Token: {oauth_token.refresh_token[:20]}...")

    return oauth_token.access_token


# ============================================================
# 示例 2：设备码授权流程（Device Flow）
# ============================================================

def device_auth_flow(client_id: str, poll_interval: int = 5) -> str:
    """
    设备码 OAuth 授权流程完整实现。

    流程：
    1. 请求设备码
    2. 提示用户访问 URL 并输入用户码
    3. 轮询 token 端点直到授权完成或超时
    4. 处理各种错误（等待、慢下来、拒绝、过期）

    Args:
        client_id: OAuth 应用的 client_id
        poll_interval: 轮询间隔（秒）

    Returns:
        access_token 字符串
    """
    # Step 1: 创建设备码 OAuth 应用
    oauth_app = DeviceOAuthApp(
        client_id=client_id,
        base_url=COZE_CN_BASE_URL,
    )

    print("\n" + "=" * 50)
    print("设备码 OAuth 授权流程")
    print("=" * 50)

    # Step 2: 获取设备码
    device_code = oauth_app.get_device_code(scope="")

    print(f"📱 请在浏览器中访问: {device_code.verification_uri}")
    print(f"🔑 输入用户码: {device_code.user_code}")
    print(f"⏱️  码有效期: {device_code.expires_in} 秒")
    print(f"🔄 轮询间隔: {device_code.interval} 秒")
    print()
    print("等待用户授权（按 Ctrl+C 取消）...")

    # Step 3: 轮询 token 端点
    interval = device_code.interval or poll_interval
    start_time = time.time()

    while True:
        # 检查是否过期
        if time.time() - start_time > device_code.expires_in:
            print("❌ 设备码已过期，请重新运行")
            sys.exit(1)

        time.sleep(interval)

        try:
            oauth_token = oauth_app.get_access_token(
                device_code=device_code.device_code,
            )
            # 如果没有抛异常，说明授权成功
            print(f"✅ 授权成功！")
            print(f"   Access Token: {oauth_token.access_token[:20]}...")
            print(f"   有效期: {oauth_token.expires_in} 秒")
            return oauth_token.access_token

        except CozePKCEAuthError as e:
            if e.error == CozePKCEAuthErrorType.AUTHORIZATION_PENDING:
                # 用户还没授权，继续轮询
                print("   ⏳ 等待用户授权...", end="\r")
                continue

            elif e.error == CozePKCEAuthErrorType.SLOW_DOWN:
                # 请求太频繁，增加间隔
                interval += 5
                print(f"   🐢 请求过快，增加间隔至 {interval} 秒")
                continue

            elif e.error == CozePKCEAuthErrorType.ACCESS_DENIED:
                # 用户拒绝授权
                print("\n❌ 用户拒绝了授权")
                sys.exit(1)

            elif e.error == CozePKCEAuthErrorType.EXPIRED_TOKEN:
                # 设备码过期
                print("\n❌ 设备码已过期，请重新运行")
                sys.exit(1)

            else:
                # 其他错误
                print(f"\n❌ 未知错误: {e}")
                raise


# ============================================================
# 使用 Token 调用 API
# ============================================================

def call_api_with_token(access_token: str, bot_id: str, message: str):
    """使用获取到的 access_token 调用 Coze API"""
    from cozepy import Message, ChatEventType

    coze = Coze(
        auth=TokenAuth(token=access_token),
        base_url=COZE_CN_BASE_URL,
    )

    print(f"\n[API 调用] 发送消息: {message}")
    print("[Bot] ", end="", flush=True)

    for event in coze.chat.stream(
        bot_id=bot_id,
        user_id="oauth_user_001",
        additional_messages=[Message.build_user_question_text(message)],
    ):
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print(event.message.content, end="", flush=True)
        elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
            if event.chat.usage:
                print(f"\n(Token: {event.chat.usage.token_count})")


# ============================================================
# 主函数
# ============================================================

def main():
    # 配置你的 OAuth 应用 client_id
    CLIENT_ID = os.environ.get("COZE_OAUTH_CLIENT_ID", "your_client_id_here")
    BOT_ID = "your_bot_id_here"

    if len(sys.argv) < 2:
        print("用法:")
        print("  python oauth_pkce_auth.py pkce       # PKCE 流程")
        print("  python oauth_pkce_auth.py device     # 设备码流程")
        sys.exit(1)

    flow = sys.argv[1]

    if flow == "pkce":
        access_token = pkce_auth_flow(CLIENT_ID)
    elif flow == "device":
        access_token = device_auth_flow(CLIENT_ID)
    else:
        print(f"未知流程: {flow}")
        sys.exit(1)

    # 使用 token 调用 API
    call_api_with_token(access_token, BOT_ID, "你好，我通过 OAuth 授权登录了！")


if __name__ == "__main__":
    main()
```

## 运行方式

### PKCE 流程

```bash
export COZE_OAUTH_CLIENT_ID="your_client_id"
# 修改代码中的 BOT_ID
python oauth_pkce_auth.py pkce
```

运行后会自动打开浏览器，用户在浏览器中完成授权后，本地 HTTP 服务器接收回调，自动换取 token。

### 设备码流程

```bash
export COZE_OAUTH_CLIENT_ID="your_client_id"
python oauth_pkce_auth.py device
```

运行后在终端显示 URL 和用户码，用户在其他设备（手机/电脑）的浏览器中打开 URL、输入用户码、点击授权，CLI 自动轮询获取 token。

## 代码解析

### PKCE 核心安全参数

| 参数 | 生成方式 | 何时发送 | 作用 |
|------|---------|---------|------|
| `code_verifier` | `secrets.token_urlsafe(64)` | 仅在换取 token 时发送 | 客户端持有的密钥 |
| `code_challenge` | `gen_s256_code_challenge(verifier)` | 授权 URL 中携带 | 服务端存储的挑战值 |
| `state` | `secrets.token_urlsafe(16)` | 授权 URL 和回调中携带 | 防止 CSRF 攻击 |

PKCE 的安全原理：即使授权码被截获，没有 code_verifier 也无法换取 token，因为 code_verifier 只在客户端保存，不经过浏览器。

### State 验证

回调中必须验证返回的 `state` 与发送的一致，这是防止 CSRF（跨站请求伪造）攻击的关键步骤。

### 设备码轮询与错误处理

设备码流程的核心是轮询 token 端点，四种错误状态的处理：

| 错误 | 处理方式 |
|------|---------|
| `AUTHORIZATION_PENDING` | 继续轮询（正常状态） |
| `SLOW_DOWN` | 增加轮询间隔 5 秒 |
| `ACCESS_DENIED` | 退出，提示用户拒绝 |
| `EXPIRED_TOKEN` | 退出，提示码过期 |

### Token 使用

获取到 `OAuthToken` 后，使用 `access_token` 创建 `TokenAuth` 实例，后续 API 调用与 PAT 方式完全一致。refresh_token 可以在 access_token 过期后换取新的 token，避免重新走授权流程。

## 流程选择

| 场景 | 推荐流程 | 理由 |
|------|---------|------|
| CLI 工具（有浏览器） | PKCE | 本地回调服务器自动接收 code |
| CLI 工具（无浏览器/远程服务器） | Device Flow | 在其他设备上完成授权 |
| 桌面应用 | PKCE | 可注册自定义 URL scheme 作为回调 |
| 移动端 App | PKCE | 系统浏览器授权 + 自定义 scheme 回调 |
| SPA（单页应用） | PKCE | 纯前端，无后端 |
| 智能电视/IoT | Device Flow | 输入受限，用手机扫码/输码 |

## 相关概念

- [认证体系](../concepts/01-auth-system.md) — 四种认证方式的详细对比和选择指南
- [客户端初始化](../concepts/02-client-init.md) — TokenAuth 的使用
- [基础对话示例](basic-chat.md) — 获取 token 后如何调用对话 API
- [认证体系参考](../references/auth-model.md) — OAuth 类和模型的完整 API
