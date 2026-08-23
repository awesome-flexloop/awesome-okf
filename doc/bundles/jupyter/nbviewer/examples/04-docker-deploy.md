---
type: Example
title: Docker部署示例
description: nbviewer的Docker部署方案，包括单容器部署、docker-compose带Memcached、Nginx反向代理和生产环境配置
tags:
  - jupyter
  - nbviewer
  - docker
  - deployment
  - example
  - production
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/Dockerfile
  - ../../../../../external/libs/jupyter/nbviewer/docker-compose.yml
---

# Docker部署示例

本文档提供nbviewer的Docker部署方案，从快速测试到生产环境。

## 快速测试（单容器）

```bash
# 使用官方镜像
docker run -p 8080:8080 jupyter/nbviewer

# 访问 http://localhost:8080
```

默认配置下：
- 监听8080端口
- 使用内存缓存（仅10条，不适合生产）
- 无GitHub API认证（60次/小时限制）

## docker-compose部署（含Memcached）

创建`docker-compose.yml`：

```yaml
version: '2'

services:
  nbviewer:
    image: jupyter/nbviewer
    ports:
      - "8080:8080"
    environment:
      # GitHub API认证（可选但强烈推荐）
      - GITHUB_API_TOKEN=${GITHUB_API_TOKEN}
      # Memcached连接（通过容器链接自动发现）
      - MEMCACHE_SERVERS=cache:11211
    links:
      - cache
    depends_on:
      - cache
    restart: always
    command: >
      python -m nbviewer
      --port=8080
      --host=0.0.0.0
      --processes=4
      --rate-limit=100
      --cache-expiry-max=7200
      --cache-expiry-min=600

  cache:
    image: memcached:1.6
    command: memcached -m 256  # 256MB内存
    restart: always
```

启动：
```bash
# 设置GitHub Token（可选）
export GITHUB_API_TOKEN=ghp_xxxxx

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f nbviewer
```

## 自定义配置文件挂载

将配置文件挂载到容器中：

```yaml
version: '2'

services:
  nbviewer:
    image: jupyter/nbviewer
    ports:
      - "8080:8080"
    volumes:
      - ./nbviewer_config.py:/etc/nbviewer/nbviewer_config.py
      - ./custom_templates:/etc/nbviewer/templates
      - ./custom_static:/etc/nbviewer/static
    environment:
      - MEMCACHE_SERVERS=cache:11211
    links:
      - cache
    command: >
      python -m nbviewer
      --config-file=/etc/nbviewer/nbviewer_config.py
      --port=8080
      --host=0.0.0.0
      --template-path=/etc/nbviewer/templates
      --static-path=/etc/nbviewer/static

  cache:
    image: memcached:1.6
    command: memcached -m 512
    restart: always
```

## 本地文件服务（Docker）

挂载本地Notebook目录：

```yaml
version: '2'

services:
  nbviewer:
    image: jupyter/nbviewer
    ports:
      - "8080:8080"
    volumes:
      - ./notebooks:/notebooks
    environment:
      - MEMCACHE_SERVERS=cache:11211
    links:
      - cache
    command: >
      python -m nbviewer
      --port=8080
      --host=0.0.0.0
      --localfiles=/notebooks
      --localfile-any-user
      --no-cache  # 开发环境禁用缓存

  cache:
    image: memcached:1.6
    restart: always
```

## Nginx反向代理配置

生产环境建议使用Nginx作为反向代理：

### docker-compose.yml（含Nginx）

```yaml
version: '2'

services:
  nbviewer:
    image: jupyter/nbviewer
    expose:
      - "8080"
    environment:
      - GITHUB_API_TOKEN=${GITHUB_API_TOKEN}
      - MEMCACHE_SERVERS=cache:11211
    links:
      - cache
    restart: always
    command: >
      python -m nbviewer
      --port=8080
      --host=0.0.0.0
      --processes=4
      --base-url=/

  cache:
    image: memcached:1.6
    command: memcached -m 512
    restart: always

  nginx:
    image: nginx:1.20
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - nbviewer
    restart: always
```

### nginx.conf

```nginx
upstream nbviewer {
    server nbviewer:8080;
}

server {
    listen 80;
    server_name nbviewer.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name nbviewer.example.com;

    ssl_certificate /etc/nginx/ssl/nbviewer.crt;
    ssl_certificate_key /etc/nginx/ssl/nbviewer.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;

    # Gzip压缩
    gzip on;
    gzip_types text/html text/css application/javascript application/json;
    gzip_min_length 1000;

    location /static/ {
        proxy_pass http://nbviewer;
        proxy_cache_valid 200 7d;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }

    location / {
        proxy_pass http://nbviewer;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 10s;
        proxy_read_timeout 60s;
        proxy_send_timeout 30s;

        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

## 环境变量参考

| 环境变量 | 说明 | 示例 |
|----------|------|------|
| `GITHUB_API_TOKEN` | GitHub Personal Access Token | `ghp_xxxxx` |
| `GITHUB_OAUTH_KEY` | GitHub OAuth Client ID | `Iv1.xxxxx` |
| `GITHUB_OAUTH_SECRET` | GitHub OAuth Client Secret | |
| `GITHUB_API_URL` | GitHub Enterprise API URL | `https://github.mycompany.com/api/v3/` |
| `MEMCACHE_SERVERS` | Memcached地址 | `cache:11211` |
| `MEMCACHIER_SERVERS` | MemCachier地址 | |
| `MEMCACHIER_USERNAME` | MemCachier用户名 | |
| `MEMCACHIER_PASSWORD` | MemCachier密码 | |
| `GOOGLE_ANALYTICS_ID` | Google Analytics ID | `UA-xxxxx` |
| `JUPYTERHUB_SERVICE_PREFIX` | JupyterHub服务前缀 | `/nbviewer/` |
| `JUPYTERHUB_SERVICE_URL` | JupyterHub服务URL | |

## 生产环境检查清单

- [ ] 配置GitHub API认证（GITHUB_API_TOKEN）
- [ ] 使用Memcached而非内存缓存
- [ ] 配置Nginx反向代理（SSL终止、gzip、缓存静态资源）
- [ ] 设置适当的进程数（CPU核心数-1）
- [ ] 调整限流参数（rate_limit/rate_limit_interval）
- [ ] 配置日志收集（Docker日志驱动或挂载日志目录）
- [ ] 设置容器重启策略（restart: always）
- [ ] 配置监控（StatsD + Grafana）
- [ ] 不要启用--localfiles除非必要
- [ ] 不要在公网启用--no-check-certificate

## 健康检查

```bash
# 简单健康检查
curl -f http://localhost:8080/faq || exit 1

# Docker HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8080/faq || exit 1
```

## 相关文档

- [部署指南](/concepts/13-deployment.md)：完整部署文档
- [基本配置示例](/examples/01-basic-config.md)：配置文件示例
- [速率限制与安全机制](/concepts/11-rate-limit-security.md)：安全配置
