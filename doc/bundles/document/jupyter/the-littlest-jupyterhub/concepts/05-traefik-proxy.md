---
title: Traefik 代理与 HTTPS 配置
description: 理解 TLJH 的 Traefik 文件代理架构、路由机制和 HTTPS/Let's Encrypt 配置
type: Explanation
tags: [concept, traefik, proxy, https, lets-encrypt, tls, reverse-proxy, jupyterhub, tljh, devops]
sources:
  - id: tljh-traefik
    title: tljh/traefik.py
  - id: tljh-jupyterhub-config
    title: tljh/jupyterhub_config.py
  - id: tljh-configurer
    title: tljh/configurer.py
---

# Traefik 代理与 HTTPS 配置

TLJH 使用 Traefik 3.x 作为反向代理，采用**文件提供者模式**（File Provider）替代传统的 configurable-http-proxy（CHP）。JupyterHub 将路由规则写入 TOML 文件，Traefik 通过文件监听自动热加载路由。

## 为什么选择 Traefik 文件模式？

传统 JupyterHub 使用 configurable-http-proxy（CHP），通过 REST API 动态添加路由。TLJH 完全移除了 CHP，改用 Traefik 文件提供者模式：

- **少一个运行时组件**：不需要 CHP 进程，Traefik 直接处理所有路由
- **自动 HTTPS**：Traefik 原生支持 Let's Encrypt 自动证书
- **文件监听热更新**：路由写入 TOML 文件后 Traefik 自动加载，无需 API 调用
- **更安全**：Traefik 以严格的安全沙箱运行（ProtectHome=yes, ProtectSystem=strict）

安装时 `ensure_jupyterhub_service` 函数首先调用 `remove_chp()` 停止并卸载 CHP 服务。

## 代理架构

```
用户请求 → :80/:443 → Traefik → JupyterHub (:15001)
                            → jupyter-alice (用户Notebook)
                            → jupyter-bob (用户Notebook)
```

### 关键配置

```python
# jupyterhub_config.py
c.TraefikProxy.should_start = False          # Hub 不启动 Traefik
c.TraefikFileProviderProxy.dynamic_config_file = STATE_DIR/rules/rules.toml
c.JupyterHub.proxy_class = "traefik_file"    # 使用文件代理
c.JupyterHub.hub_port = 15001                # Hub 监听端口
```

- `should_start = False`：Traefik 作为独立 systemd 服务运行，不由 JupyterHub 启动
- `dynamic_config_file`：路由规则写入此 TOML 文件，Traefik watch 此目录
- `proxy_class = "traefik_file"`：使用 jupyterhub-traefik-proxy 的文件模式

### Traefik API

Traefik 暴露一个内部 API 端点（默认 127.0.0.1:8099）供 JupyterHub 查询路由状态。凭证存储在 `/opt/tljh/state/traefik-api.secret`（32字节随机 hex 字符串，安装时生成）。

## Traefik 配置

Traefik 配置分为两部分：

### 静态配置（traefik.toml）

安装时通过 Jinja2 模板渲染到 `/opt/tljh/state/traefik.toml`，包含：

- **API 配置**：启用 dashboard（仅内部访问）
- **日志**：INFO 级别
- **访问日志**：JSON 格式，过滤 5xx 状态码，脱敏 Authorization/Cookie/Set-Cookie/X-Xsrftoken 头
- **入口点**：
  - `http`：监听 http.address:http.port（默认 :80）
  - `https`：监听 https.address:https.port（默认 :443，HTTPS 启用时）
  - `auth_api`：监听 localhost:traefik_api.port（默认 127.0.0.1:8099）
- **证书解析**：Let's Encrypt ACME 配置
- **提供者**：文件提供者，监听 `rules/` 目录，watch=true

### 动态配置（rules/）

`rules/dynamic.toml` 包含 TLS 配置（密码套件、证书等），`rules/rules.toml` 由 JupyterHub 动态写入路由规则。

### 额外配置目录

可在 Traefik 配置目录中放置额外的 `*.toml` 文件，Traefik 会自动合并。

## HTTP 配置

默认 HTTP 监听所有接口的 80 端口：

```bash
# 修改 HTTP 端口
sudo tljh-config set http.port 8080
sudo tljh-config set http.address 127.0.0.1  # 仅本地访问
sudo tljh-config reload proxy
```

## HTTPS 配置

TLJH 支持两种 HTTPS 方式：Let's Encrypt 自动证书和手动证书。

### 方式1：Let's Encrypt

```bash
sudo tljh-config set https.enabled true
sudo tljh-config set https.letsencrypt.email you@example.com
sudo tljh-config add-item https.letsencrypt.domains yourdomain.example.com
sudo tljh-config reload proxy
```

Let's Encrypt 配置说明：
- `email`：证书到期通知邮箱（必须是有效的邮箱格式）
- `domains`：域名列表（DNS 必须已指向服务器 IP）
- `staging`：设为 true 使用 Let's Encrypt 测试环境（避免触发速率限制）
- 证书存储在 `/opt/tljh/state/acme.json`（权限 0o600）
- TLS 挑战（tlsChallenge）用于域名验证
- 启用 HTTPS 后，HTTP（80端口）自动重定向到 HTTPS（443端口）

验证域名 DNS 已正确解析后再启用 Let's Encrypt，否则证书颁发会失败。

### 方式2：手动 TLS 证书

```bash
sudo tljh-config set https.enabled true
sudo tljh-config set https.tls.key /path/to/private.key
sudo tljh-config set https.tls.cert /path/to/certificate.crt
sudo tljh-config reload proxy
```

- `key`：私钥文件路径
- `cert`：证书文件路径（可为包含完整链的 bundle）

## TLS 安全配置

动态配置中设置了安全的 TLS 默认值：

- **最低版本**：TLS 1.2
- **密码套件**：现代化安全密码套件列表
- **自动证书**：Let's Encrypt 自动管理证书续期

## Traefik 二进制管理

- **版本**：Traefik 3.6.5（固定版本）
- **安装位置**：`/opt/tljh/hub/bin/traefik`
- **下载**：首次安装时从 GitHub releases 下载，支持 linux_amd64 和 linux_arm64
- **校验**：SHA256 校验和验证，下载损坏自动重试（@backoff.expo, max_tries=2）
- **权限**：chmod 0o755
- **版本检查**：已存在时通过 `traefik version` 检查版本，不匹配则重新下载

## Traefik 服务安全

traefik.service 使用 systemd 安全沙箱：

- `ProtectHome=yes`：无法访问用户主目录
- `ProtectSystem=strict`：文件系统只读
- `ReadWritePaths`：仅可写 `state/rules` 和 `state/acme.json`
- `Restart=always`：崩溃自动重启

## 重载代理

修改网络相关配置（端口、HTTPS、证书等）后需要 reload proxy：

```bash
sudo tljh-config reload proxy
```

proxy reload 会：
1. 重新渲染 Traefik 静态和动态配置模板
2. 合并 extra_config_dir 中的 TOML 文件
3. HTTPS 启用时校验证书配置（tls.cert+key 或 letsencrypt.email+domains 必须配对）
4. 创建 acme.json（权限 0o600）
5. 重启 traefik.service

## 验证代理状态

```bash
# 检查 Traefik 服务状态
sudo systemctl status traefik

# 检查 Traefik 配置
sudo cat /opt/tljh/state/traefik.toml

# 检查路由规则
sudo cat /opt/tljh/state/rules/rules.toml

# 测试 HTTP 响应
curl -I http://localhost

# HTTPS 测试
curl -I https://yourdomain.example.com
```

## 常见问题

### Let's Encrypt 证书申请失败

检查：
1. DNS 是否已解析到服务器（`nslookup yourdomain.example.com`）
2. 80 和 443 端口是否对外开放（防火墙/安全组）
3. 邮箱地址格式是否正确
4. 可先设置 `https.letsencrypt.staging true` 测试，避免触发速率限制

### 修改 HTTPS 配置后无法访问

检查 Traefik 日志：
```bash
sudo journalctl -u traefik -n 50
```

### 如何同时使用 HTTP 和 HTTPS

TLJH 设计为 HTTPS 启用后自动将 HTTP 重定向到 HTTPS。如果需要同时提供两者（不推荐），需在 jupyterhub_config.d 中自定义 Traefik 配置。

## 下一步

- [配置系统](03-config-system.md)：所有配置选项
- [HTTPS 配置示例](../examples/04-https-letsencrypt.md)：Let's Encrypt 完整配置步骤
- [插件系统](06-plugin-system.md)：通过插件扩展 TLJH
