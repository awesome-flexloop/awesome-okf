---
type: Concept
title: 部署指南
description: nbviewer生产部署方案、Docker部署、进程/线程池配置、反向代理、Memcached缓存和环境变量参考
tags:
  - jupyter
  - nbviewer
  - deployment
  - docker
  - nginx
  - production
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/app.py
  - ../../../../../external/libs/jupyter/nbviewer/Dockerfile
  - ../../../../../external/libs/jupyter/nbviewer/docker-compose.yml
---

# 部署指南

本文档详细说明 nbviewer 的部署方案，包括 Docker 部署、生产环境配置、反向代理、缓存配置和性能调优。

## 快速开始

### pip 安装

```bash
pip install nbviewer
python -m nbviewer --port=5000
```

访问 http://localhost:5000 即可使用。

### Docker 部署

nbviewer 官方提供 Docker 镜像，支持 docker-compose 一键部署：

```bash
# 单容器运行
docker run -p 8080:8080 jupyter/nbviewer

# 使用docker-compose（含Memcached）
docker-compose up
```

docker-compose.yml 通常包含两个服务：
1. **nbviewer**：主应用服务，暴露8080端口
2. **memcached**：缓存服务，通过容器链接（`NBCACHE_PORT`环境变量）自动发现

## 运行模式

### 线程模式（默认）

```bash
python -m nbviewer --threads=4
```

- 使用 `ThreadPoolExecutor` 执行 nbconvert 渲染
- Exporter 实例在主线程创建，线程间共享（通过线程池传递）
- 内存占用较低（Exporter 单例）
- 受 GIL 限制，CPU 密集型渲染不能真正并行
- 适合 I/O 密集场景或低流量部署

### 进程模式

```bash
python -m nbviewer --processes=4
```

- 使用 `ProcessPoolExecutor` 执行渲染
- Exporter 类（而非实例）传递给子进程，在子进程中首次使用时延迟实例化
- 绕过 GIL，真正多核并行渲染
- 内存占用较高（每个子进程独立加载Exporter和nbconvert）
- 适合高流量、多核服务器部署

> **注意**：进程模式下 Exporter 必须可 pickle（nbconvert 标准 Exporter 都满足）。自定义 Exporter 如果包含不可序列化的资源（如打开的文件句柄、网络连接），进程模式会失败。

## 核心配置参数

### 网络配置

| 参数 | CLI选项 | 默认值 | 说明 |
|------|---------|--------|------|
| host | `--host` | `0.0.0.0` | 监听地址 |
| port | `--port` | `5000` | 监听端口 |
| base_url | `--base-url` | `/` | URL前缀（反向代理子路径部署时使用） |
| sslcert | `--sslcert` | 无 | SSL证书路径 |
| sslkey | `--sslkey` | 无 | SSL私钥路径 |

### 缓存配置

| 参数 | CLI选项 | 默认值 | 说明 |
|------|---------|--------|------|
| no_cache | `--no-cache` | False | 禁用缓存（开发调试） |
| cache_expiry_min | `--cache-expiry-min` | 600 | 缓存最短TTL（秒，10分钟） |
| cache_expiry_max | `--cache-expiry-max` | 7200 | 缓存最长TTL（秒，2小时） |
| mc_threads | `--mc-threads` | 1 | Memcached客户端线程数 |

### 渲染配置

| 参数 | CLI选项 | 默认值 | 说明 |
|------|---------|--------|------|
| threads | `--threads` | 1 | 渲染线程数 |
| processes | `--processes` | 0 | 渲染进程数（0表示使用线程） |
| render_timeout | `--render-timeout` | 15 | 慢渲染超时（秒） |
| default_format | `--default-format` | html | 默认输出格式 |
| localfiles | `--localfiles` | "" | 本地文件根目录（安全风险） |

### 限流配置

| 参数 | CLI选项 | 默认值 | 说明 |
|------|---------|--------|------|
| rate_limit | `--rate-limit` | 60 | 限流阈值（每窗口请求数） |
| rate_limit_interval | `--rate-limit-interval` | 600 | 限流窗口（秒，10分钟） |

### GitHub API配置

| 参数 | 环境变量 | 说明 |
|------|----------|------|
| GITHUB_API_TOKEN | 环境变量 | GitHub Personal Access Token |
| GITHUB_OAUTH_KEY | 环境变量 | GitHub OAuth App Client ID |
| GITHUB_OAUTH_SECRET | 环境变量 | GitHub OAuth App Client Secret |
| GITHUB_API_URL | 环境变量 | GitHub Enterprise API URL |

配置认证后，GitHub API 速率限制从 60次/小时 提升到 5000次/小时。

### 外部资源配置

| 参数 | CLI选项 | 默认值 | 说明 |
|------|---------|--------|------|
| mathjax_url | `--mathjax-url` | cdnjs MathJax 2.7.1 | MathJax CDN地址 |
| ipywidgets_base_url | `--ipywidgets-base-url` | unpkg.com | ipywidgets JS包CDN |
| jupyter_js_widgets_version | `--jupyter-js-widgets-version` | * | jupyter-js-widgets版本 |
| binder_base_url | `--binder-base-url` | mybinder.org/v2 | Binder服务URL |

### 代理配置

| 参数 | CLI选项 | 默认值 | 说明 |
|------|---------|--------|------|
| proxy_host | `--proxy-host` | 无 | HTTP代理地址 |
| proxy_port | `--proxy-port` | -1 | HTTP代理端口 |
| no_check_certificate | `--no-check-certificate` | False | 禁用SSL证书验证 |

### 监控配置

| 参数 | CLI选项 | 默认值 | 说明 |
|------|---------|--------|------|
| statsd_host | `--statsd-host` | "" | StatsD服务器地址 |
| statsd_port | `--statsd-port` | 8125 | StatsD端口 |
| statsd_prefix | `--statsd-prefix` | nbviewer | StatsD指标前缀 |

### 本地文件配置

| 参数 | CLI Flag | 说明 |
|------|----------|------|
| localfile_any_user | `--localfile-any-user` | 服务非others-readable文件 |
| localfile_follow_symlinks | `--localfile-follow-symlinks` | 跟随符号链接 |

## Memcached环境变量

nbviewer 通过环境变量自动检测和配置 Memcached：

| 环境变量 | 说明 |
|----------|------|
| `MEMCACHIER_SERVERS` | MemCachier服务地址（SASL认证） |
| `MEMCACHIER_USERNAME` | MemCachier用户名 |
| `MEMCACHIER_PASSWORD` | MemCachier密码 |
| `MEMCACHE_SERVERS` | 普通Memcached地址（逗号分隔） |
| `NBCACHE_PORT` | Docker容器链接（如`tcp://172.17.0.2:11211`） |

Docker容器链接是最简单的方式——当memcached容器链接到nbviewer容器时，Docker自动设置`NBCACHE_PORT`环境变量，nbviewer会自动解析并连接。

## 配置文件

生成默认配置文件：

```bash
python -m nbviewer --generate-config
```

这会在当前目录生成 `nbviewer_config.py`，包含所有可配置项和注释。使用配置文件启动：

```bash
python -m nbviewer --config-file=nbviewer_config.py
```

配置文件使用 traitlets 配置语法：

```python
c = get_config()

c.NBViewer.port = 8080
c.NBViewer.processes = 4
c.NBViewer.rate_limit = 100
c.NBViewer.rate_limit_interval = 300
c.NBViewer.cache_expiry_max = 3600
c.NBViewer.mathjax_url = "https://cdn.example.com/mathjax/2.7.1/"
```

## Docker部署

### 官方Dockerfile结构

nbviewer的Dockerfile通常采用多阶段构建：
1. 基础镜像：Python slim
2. 安装系统依赖（libcurl、nodejs等nbconvert需要的包）
3. 安装nbviewer及其依赖
4. 暴露8080端口
5. 入口点：`python -m nbviewer --port=8080 --ip=0.0.0.0`

### docker-compose.yml示例

```yaml
version: '2'
services:
  nbviewer:
    image: jupyter/nbviewer
    ports:
      - "8080:8080"
    environment:
      - GITHUB_API_TOKEN=${GITHUB_API_TOKEN}
      - MEMCACHIER_SERVERS=cache:11211
    links:
      - cache
    restart: always
  
  cache:
    image: memcached:1.5
    restart: always
```

### Docker环境变量

容器中可通过环境变量配置：
- `GITHUB_API_TOKEN`：GitHub认证token
- `JUPYTERHUB_SERVICE_PREFIX`：JupyterHub服务前缀（在JupyterHub中部署时自动设置）
- `JUPYTERHUB_SERVICE_URL`：JupyterHub服务URL（自动设置host/port默认值）
- `NBINDEX_PORT`：Notebook索引服务地址
- `NBVIEWER_STATIC_PATH`：自定义静态文件路径
- `NBVIEWER_TEMPLATE_PATH`：自定义模板路径
- `GOOGLE_ANALYTICS_ID`：Google Analytics ID

## 反向代理配置（Nginx）

生产环境建议使用 Nginx 作为反向代理：

```nginx
upstream nbviewer {
    server 127.0.0.1:5000;
    # 多实例部署时可添加多个后端
    # server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name nbviewer.example.com;
    
    # 重定向到HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name nbviewer.example.com;
    
    ssl_certificate /etc/ssl/certs/nbviewer.crt;
    ssl_certificate_key /etc/ssl/private/nbviewer.key;
    
    # 上传大小限制（Notebook JSON通常不大，但GitHub API响应可能较大）
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://nbviewer;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置（慢渲染可能需要较长时间）
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
        proxy_send_timeout 30s;
        
        # WebSocket支持（如果需要ipywidgets交互）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态文件可由Nginx直接服务
    location /static/ {
        alias /path/to/nbviewer/static/;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }
}
```

关键配置要点：
1. **`xheaders=True`**：nbviewer 启动时已启用，确保正确解析 `X-Real-IP`/`X-Forwarded-For`
2. **超时设置**：`proxy_read_timeout` 需要大于 `render_timeout`（默认15秒），否则慢渲染页面会被Nginx断开
3. **HTTPS**：建议配置SSL，避免混合内容问题

### 子路径部署

如果nbviewer不在域名根路径下，需要设置 `base_url`：

```bash
python -m nbviewer --base-url="/nbviewer/"
```

Nginx配置对应调整：

```nginx
location /nbviewer/ {
    proxy_pass http://nbviewer;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 性能调优建议

### 1. 启用Memcached

生产环境务必使用Memcached而非内存缓存：
- DummyAsyncCache默认仅10条，多进程时各进程独立缓存，命中率极低
- Memcached支持分布式，多实例nbviewer可共享缓存
- Memcached的TTL过期是精确的，内存缓存依赖访问触发过期

### 2. 进程数配置

进程模式下进程数建议设置为 **CPU核心数 - 1**（留一个核心给事件循环和I/O）。

### 3. 缓存TTL调优

- 高流量公共实例：增大 `cache_expiry_max` 到4-8小时
- 频繁更新的Notebook：减小 `cache_expiry_min` 到5分钟
- 可通过 `max_cache_uris` 设置首页链接使用最大缓存时间

### 4. GitHub API配额

- 务必配置 `GITHUB_API_TOKEN` 或 OAuth凭据
- 未认证限制为60次/小时，认证后为5000次/小时
- 监控日志中的 "GitHub API requests remaining" 警告

### 5. 静态资源CDN

默认使用CDN加载MathJax和ipywidgets资源：
- 内网部署可配置私有CDN或本地静态资源
- `mathjax_url`、`ipywidgets_base_url` 指向内部镜像

### 6. 前置CDN

页面响应包含 `Cache-Control` 头（缓存命中时），可前置CDN（如Cloudflare）进一步减轻源站负载。

## 监控

### StatsD指标

配置 `--statsd-host` 后发送以下指标：

| 指标 | 类型 | 说明 |
|------|------|------|
| `nbviewer.rendering.parsing.time` | timer | JSON解析耗时 |
| `nbviewer.rendering.nbrender.time` | timer | nbconvert渲染耗时 |
| `nbviewer.rendering.nbrender.success` | counter | 渲染成功 |
| `nbviewer.rendering.nbrender.fail` | counter | 渲染失败 |
| `nbviewer.rendering.html.time` | timer | 模板包装耗时 |
| `nbviewer.rendering.waiting` | counter | 慢渲染等待页 |

### 日志级别

- `--log-level=DEBUG`：开发调试，输出详细日志
- 默认INFO：生产环境，记录关键操作
- `--debug` flag：设置DEBUG级别

### 健康检查

简单的健康检查可以请求首页或FAQ页面：

```bash
curl -f http://localhost:5000/faq || exit 1
```

## JupyterHub 部署

nbviewer 可作为 JupyterHub 服务部署：

环境变量自动配置：
- `JUPYTERHUB_SERVICE_URL`：自动设置 host/port 默认值
- `JUPYTERHUB_SERVICE_PREFIX`：自动设置 base_url
- `JUPYTERHUB_API_TOKEN`：Hub API认证
- `JUPYTERHUB_API_URL`：Hub API地址

## 相关文档

- [快速开始指南](/concepts/01-getting-started.md)：基础使用和安装
- [缓存系统](/concepts/07-caching-system.md)：缓存后端详细配置
- [速率限制与安全机制](/concepts/11-rate-limit-security.md)：安全配置建议
- [自定义Provider扩展](/concepts/12-custom-provider.md)：扩展开发
