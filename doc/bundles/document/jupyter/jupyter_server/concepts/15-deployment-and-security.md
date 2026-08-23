---
type: Concept
title: "部署与安全"
description: "生产部署指南、反向代理配置、HTTPS 证书、Docker 容器化、系统服务配置与安全加固"
tags: [deployment, security, production, docker, nginx, https, systemd, reverse-proxy]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:05:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: auth
    resource: /references/auth-source.md
    title: 认证授权源码信源
---

# 部署与安全

本文档提供 Jupyter Server 生产环境部署的完整指南，包括安全加固、反向代理配置、HTTPS、容器化和服务管理。

## 部署架构推荐

### 单机部署（个人/小团队）

```
用户浏览器
    │
    ▼
Nginx (反向代理 + HTTPS + 静态资源缓存)
    │
    ▼
Jupyter Server (localhost:8888)
    │
    ├── Kernels (本地进程)
    └── Contents (本地文件系统)
```

### 企业级部署（分布式）

```
用户浏览器
    │
    ▼
Nginx/Ingress (负载均衡 + HTTPS)
    │
    ▼
Jupyter Server/JupyterHub (多用户)
    │
    ▼
Enterprise Gateway
    │
    ├── K8s Pod: Python Kernel
    ├── K8s Pod: R Kernel
    └── K8s Pod: Spark Kernel
```

## 安全加固清单

### ✅ 必须配置

| 项目 | 配置 | 说明 |
|------|------|------|
| 密码认证 | `PasswordIdentityProvider.hashed_password` | 设置强密码 |
| Token 认证 | `IdentityProvider.token` | 使用随机 Token |
| HTTPS | `certfile`/`keyfile` | 加密传输 |
| 允许远程 | `allow_remote_access=True` | 远程访问时显式启用 |
| XSRF 保护 | `disable_check_xsrf=False` | 保持开启（默认） |
| Cookie Secret | `cookie_secret` | 使用固定值（重启后 Cookie 有效） |

### ✅ 推荐配置

| 项目 | 配置 | 说明 |
|------|------|------|
| CORS 限制 | `allow_origin` | 指定允许的域名 |
| 空闲内核回收 | `cull_idle_timeout=3600` | 1小时回收空闲内核 |
| 最大请求体 | `max_body_size` | 限制上传大小 |
| 审计日志 | `EventLogger.handlers` | 记录操作审计 |
| 进程用户 | 非 root 用户 | 使用普通用户运行 |
| 防火墙 | 限制 8888 端口 | 只允许本机/代理访问 |

### ❌ 禁止配置

| 项目 | 禁止值 | 原因 |
|------|--------|------|
| 空 Token | `token=''` | 禁用认证，任何人可访问 |
| 开放 CORS | `allow_origin='*'` | 跨站请求伪造风险 |
| 无密码公网 | `password=''` + 公网 | 任意代码执行漏洞 |
| root 运行 | `--allow-root` | 容器外极度危险 |
| 禁用 XSRF | `disable_check_xsrf=True` | CSRF 攻击风险 |

## HTTPS 配置

### 方式 1：自签名证书（开发/测试）

```bash
# 生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout jupyter.key -out jupyter.crt

# 启动
jupyter server \
  --certfile=jupyter.crt \
  --keyfile=jupyter.key \
  --ip=0.0.0.0
```

### 方式 2：Let's Encrypt（生产推荐）

```bash
# 使用 certbot 获取证书
sudo certbot certonly --standalone -d jupyter.example.com

# 证书位于 /etc/letsencrypt/live/jupyter.example.com/
jupyter server \
  --certfile=/etc/letsencrypt/live/jupyter.example.com/fullchain.pem \
  --keyfile=/etc/letsencrypt/live/jupyter.example.com/privkey.pem \
  --ip=0.0.0.0
```

### 方式 3：反向代理终止 HTTPS（推荐生产）

Jupyter Server 监听 localhost，由 Nginx 处理 HTTPS：见下方 Nginx 配置。

## Nginx 反向代理配置

```nginx
# /etc/nginx/sites-available/jupyter
server {
    listen 443 ssl http2;
    server_name jupyter.example.com;

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/jupyter.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jupyter.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 日志
    access_log /var/log/nginx/jupyter_access.log;
    error_log /var/log/nginx/jupyter_error.log;

    # 最大请求体（Notebook 上传）
    client_max_body_size 512M;

    location / {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 长超时（WebSocket/内核执行）
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;

        # 缓冲
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # 静态资源缓存
    location /static/ {
        proxy_pass http://127.0.0.1:8888;
        proxy_cache_valid 200 1h;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }
}

# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name jupyter.example.com;
    return 301 https://$server_name$request_uri;
}
```

### base_url 配置

如果 Jupyter Server 不在根路径，需要设置 `base_url`：

```python
c.ServerApp.base_url = '/jupyter/'
```

Nginx 配置对应调整：

```nginx
location /jupyter/ {
    proxy_pass http://127.0.0.1:8888/jupyter/;
    # ... 其他配置相同
}
```

## systemd 服务配置

```ini
# /etc/systemd/system/jupyter-server.service
[Unit]
Description=Jupyter Server
After=network.target

[Service]
Type=simple
User=jupyter
Group=jupyter
WorkingDirectory=/home/jupyter/notebooks
Environment=PATH=/home/jupyter/.local/bin:/usr/bin:/bin
ExecStart=/home/jupyter/.local/bin/jupyter-server \
  --config=/etc/jupyter/jupyter_server_config.py \
  --no-browser
Restart=always
RestartSec=10

# 安全加固
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/jupyter/notebooks
CapabilityBoundingSet=
AmbientCapabilities=

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动
sudo systemctl daemon-reload
sudo systemctl enable --now jupyter-server
sudo systemctl status jupyter-server
```

## Docker 部署

### Dockerfile

```dockerfile
FROM python:3.11-slim

RUN pip install --no-cache-dir jupyter-server ipykernel

# 创建非 root 用户
RUN useradd -m -s /bin/bash jupyter
USER jupyter
WORKDIR /home/jupyter

# 创建工作目录
RUN mkdir notebooks
WORKDIR /home/jupyter/notebooks

# 生成默认配置
RUN jupyter server --generate-config

EXPOSE 8888

CMD ["jupyter-server", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  jupyter:
    build: .
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jupyter/notebooks
      - jupyter-config:/home/jupyter/.jupyter
    environment:
      - JUPYTER_TOKEN=${JUPYTER_TOKEN:-changeme}
    restart: unless-stopped
    user: "1000:1000"

volumes:
  jupyter-config:
```

### 运行

```bash
JUPYTER_TOKEN=my-secret-token docker-compose up -d
```

## JupyterHub 多用户部署

对于多用户场景，使用 JupyterHub 管理用户认证和内核隔离：

```
JupyterHub (端口 8000)
├── PAM/OAuth/GitHub 认证
├── 每个用户一个 Jupyter Server 实例
├── Docker/K8s 容器隔离
└── 资源配额管理
```

安装：
```bash
pip install jupyterhub
jupyterhub
```

## 生产配置文件示例

```python
# /etc/jupyter/jupyter_server_config.py
c = get_config()  # noqa

# 网络配置
c.ServerApp.ip = '127.0.0.1'  # 只监听本机（Nginx 代理）
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_remote_access = True
c.ServerApp.base_url = '/'

# HTTPS（Nginx 终止时不需要）
# c.ServerApp.certfile = '/etc/ssl/jupyter.crt'
# c.ServerApp.keyfile = '/etc/ssl/jupyter.key'

# 认证配置
c.PasswordIdentityProvider.hashed_password = 'argon2:...'
c.IdentityProvider.token = ''  # 禁用 Token（使用密码 + Cookie）
c.IdentityProvider.cookie_secret_file = '/etc/jupyter/cookie_secret'

# CORS（Nginx 代理，只允许本域名）
c.ServerApp.allow_origin = 'https://jupyter.example.com'
c.ServerApp.allow_credentials = True
c.ServerApp.disable_check_xsrf = False

# 安全限制
c.ServerApp.max_body_size = 100 * 1024 * 1024  # 100MB
c.ContentsManager.allow_hidden = False  # 禁止访问隐藏文件

# 内核管理
c.MappingKernelManager.cull_idle_timeout = 3600  # 1小时回收
c.MappingKernelManager.cull_interval = 300
c.MappingKernelManager.cull_connected = True

# 目录限制
c.ServerApp.root_dir = '/home/jupyter/notebooks'

# 日志
c.ServerApp.log_level = 'INFO'
c.ServerApp.log_file = '/var/log/jupyter/server.log'

# 事件审计
c.EventLogger.handlers = [
    'logging-short',
    'file:///var/log/jupyter/audit.log',
]

# 禁用功能（按需）
c.ServerApp.terminals_enabled = True  # 设为 False 禁用终端
c.ServerApp.quit_button = False       # 隐藏退出按钮
```

## 认证集成

### OAuth2/OpenID Connect

使用 `oauthenticator` 扩展实现企业 SSO：

```python
# 与 JupyterHub 配合使用 OAuthenticator
from oauthenticator.github import GitHubOAuthenticator
c.JupyterHub.authenticator_class = GitHubOAuthenticator
```

### LDAP/Active Directory

```python
# 使用 ldapauthenticator
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address = 'ldap://ldap.example.com'
c.LDAPAuthenticator.bind_dn_template = 'cn={username},ou=users,dc=example,dc=com'
```

## 监控与健康检查

### 健康检查端点

Jupyter Server 本身没有专门的 health endpoint，但可以使用：

```bash
# 检查 API 是否响应
curl -f http://localhost:8888/api/status?token=xxx

# 检查 JupyterLab 扩展
curl -f http://localhost:8888/lab
```

### 系统监控

```python
# 启用 Prometheus 指标
c.ServerApp.prometheus_enabled = True
```

配合 Prometheus + Grafana 监控内核数量、请求延迟、内存使用等。

## 故障排查

### 常见问题

| 问题 | 排查方向 |
|------|---------|
| 无法连接 | 防火墙、端口绑定、Nginx 代理配置 |
| WebSocket 断开 | Nginx 超时配置（`proxy_read_timeout`） |
| 认证失败 | Token/密码、Cookie 域名、XSRF |
| 内核启动失败 | Python 环境、内核安装、权限 |
| 文件访问被拒 | root_dir 配置、文件权限、hidden 文件 |
| 内存泄漏 | 内核回收配置、未关闭的连接 |

### 诊断模式

```bash
# 启动调试模式
jupyter server --debug

# 检查配置是否生效
jupyter server --show-config

# 验证扩展加载
jupyter server extension list
```

## 相关概念

- [认证授权系统](05-auth-system.md) — 认证机制详解
- [配置管理](06-config-management.md) — 所有配置选项
- [事件系统与日志](13-events-and-logging.md) — 审计日志配置
- [快速上手](01-getting-started.md) — 基本启动命令
