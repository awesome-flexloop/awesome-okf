---
title: 配置 GitHub OAuth 认证
description: 配置 GitHub OAuth 作为 TLJH 的登录认证方式
type: Example
tags: [example, auth, oauth, github, authentication, jupyterhub, tljh]
sources:
  - id: tljh-configurer
    title: tljh/configurer.py
  - id: tljh-config
    title: tljh/config.py
---

# 配置 GitHub OAuth 认证

本文档演示如何使用 GitHub OAuth 作为 TLJH 的认证方式，让用户使用 GitHub 账户登录。

## 前置条件

- TLJH 已安装并运行
- 服务器有公网 IP 或域名
- 一个 GitHub 账户

## 步骤1：创建 GitHub OAuth App

1. 登录 GitHub，进入 Settings → Developer settings → OAuth Apps → New OAuth App
2. 填写表单：
   - **Application name**：`My JupyterHub`（任意名称）
   - **Homepage URL**：`https://yourdomain.example.com`（你的 JupyterHub 地址）
   - **Authorization callback URL**：`https://yourdomain.example.com/hub/oauth_callback`
3. 点击 "Register application"
4. 记录下 **Client ID** 和 **Client Secret**（点击 "Generate a new client secret"）

> ⚠️ Client Secret 只显示一次，务必保存好。

## 步骤2：安装 oauthenticator（如果尚未安装）

TLJH 的 requirements-hub-env.txt 已包含 oauthenticator ≥17.1.0,<18，通常无需额外安装。如需要手动安装：

```bash
sudo /opt/tljh/hub/bin/pip install oauthenticator
```

## 步骤3：配置 TLJH 使用 GitHub OAuth

```bash
sudo tljh-config set auth.type oauthenticator.github.GitHubOAuthenticator
sudo tljh-config set auth.GitHubOAuthenticator.client_id "你的Client ID"
sudo tljh-config set auth.GitHubOAuthenticator.client_secret "你的Client Secret"
sudo tljh-config set auth.GitHubOAuthenticator.oauth_callback_url "https://yourdomain.example.com/hub/oauth_callback"
```

## 步骤4（可选）：限制特定 GitHub 用户登录

```bash
# 设置允许的 GitHub 用户名白名单
sudo tljh-config add-item auth.GitHubOAuthenticator.allowed_users github-user1
sudo tljh-config add-item auth.GitHubOAuthenticator.allowed_users github-user2
```

## 步骤5（可选）：将 GitHub 组织成员自动设为管理员

```bash
sudo tljh-config set auth.GitHubOAuthenticator.admin_users '["github-admin-user"]'
```

注意：列表值需要通过直接编辑 config.yaml 来设置更复杂的配置。

## 步骤6：重载 Hub 配置

```bash
sudo tljh-config reload hub
```

## 步骤7：测试登录

1. 访问你的 JupyterHub 地址
2. 应该会跳转到 GitHub 授权页面
3. 授权后应重定向回 JupyterHub 并自动登录

## 配置 GitHub 组织访问限制

如果想限制只有特定 GitHub 组织的成员可以登录：

直接编辑 config.yaml：

```bash
sudo nano /opt/tljh/config/config.yaml
```

添加：

```yaml
auth:
  type: oauthenticator.github.GitHubOAuthenticator
  GitHubOAuthenticator:
    client_id: "xxx"
    client_secret: "xxx"
    oauth_callback_url: "https://yourdomain.example.com/hub/oauth_callback"
    allowed_organizations:
      - "your-github-org"
    scope:
      - read:user
```

```bash
sudo tljh-config reload hub
```

## 故障排查

### 登录后显示 403 Forbidden

- 检查 `allowed_users` 或 `allowed_organizations` 配置
- 如果没有设置这些限制，确保 config.yaml 中没有残留的空列表

### Callback URL 不匹配

- GitHub OAuth App 的 Authorization callback URL 必须与 `oauth_callback_url` 配置完全一致
- 包括 http/https 和端口号

### oauthenticator 版本不兼容

检查版本：

```bash
sudo /opt/tljh/hub/bin/pip show oauthenticator
```

确保版本在 ≥17.1.0,<18 范围内。

## 其他 OAuth 提供商

同样的模式适用于其他 OAuth 提供商，只需更改 auth.type 和配置类名：

### Google

```bash
sudo tljh-config set auth.type oauthenticator.google.GoogleOAuthenticator
sudo tljh-config set auth.GoogleOAuthenticator.client_id "xxx"
sudo tljh-config set auth.GoogleOAuthenticator.client_secret "xxx"
```

### Generic OAuth（通用 OIDC）

```bash
sudo tljh-config set auth.type oauthenticator.generic.GenericOAuthenticator
sudo tljh-config set auth.GenericOAuthenticator.client_id "xxx"
sudo tljh-config set auth.GenericOAuthenticator.client_secret "xxx"
sudo tljh-config set auth.GenericOAuthenticator.login_service "My SSO"
sudo tljh-config set auth.GenericOAuthenticator.oauth_callback_url "https://yourdomain/hub/oauth_callback"
sudo tljh-config set auth.GenericOAuthenticator.authorize_url "https://sso.example.com/authorize"
sudo tljh-config set auth.GenericOAuthenticator.token_url "https://sso.example.com/token"
sudo tljh-config set auth.GenericOAuthenticator.userdata_url "https://sso.example.com/userinfo"
```

> ⚠️ 复杂的嵌套配置（如 `token_url`、`authorize_url` 等）可能需要直接编辑 config.yaml。
