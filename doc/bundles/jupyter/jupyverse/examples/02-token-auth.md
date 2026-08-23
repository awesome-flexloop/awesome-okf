---
type: Example
title: "Token 认证配置"
description: "使用 Token 认证模式启动 Jupyverse，配置安全 token，适用于单用户远程访问场景。"
tags: [auth, token, security, remote-access]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: auth
    resource: /concepts/05-auth-system.md
    title: 认证授权系统
  - id: cli
    resource: /concepts/11-cli-and-configuration.md
    title: CLI 与配置
---

# Token 认证配置

本示例演示如何使用 Token 认证启动 Jupyverse，适用于需要安全访问的场景。

## 安装认证插件

```bash
pip install "jupyverse[jupyterlab,auth]"
```

## 启动方式

### 方式1：固定 Token（推荐）

通过 `--set auth.token` 设置固定 token，并禁用其他认证插件：

```bash
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth \
  --set "auth.token=my-secret-token-2024" \
  --host 0.0.0.0
```

浏览器访问时使用：

```
http://your-server:8000/lab?token=my-secret-token-2024
```

### 方式2：自动生成 Token

```bash
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth
```

不指定 token 时，fps-auth 会自动生成一个随机 token。token 会被自动添加为 URL 查询参数（查看启动日志中的 URL）。

### 方式3：测试模式（开发用）

```bash
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth \
  --set "auth.test=true"
```

测试模式自动创建默认用户：
- 邮箱：`admin@jupyter.com`
- 密码：`jupyverse`

同时会创建一个 token 认证用户（token 自动生成）。

## 验证认证

```bash
# 无 token 访问（应返回 403）
curl http://127.0.0.1:8000/api/contents
# → {"detail":"Forbidden"}

# 带 token 访问（查询参数）
curl "http://127.0.0.1:8000/api/contents?token=my-secret-token-2024"
# → 返回根目录内容列表
```

## 使用 Authorization Header

```bash
curl -H "Authorization: Token my-secret-token-2024" \
  http://127.0.0.1:8000/api/contents
```

## Cookie 认证

首次通过 URL 参数 `?token=xxx` 访问后，认证 cookie 会被设置，后续请求无需再携带 token。
