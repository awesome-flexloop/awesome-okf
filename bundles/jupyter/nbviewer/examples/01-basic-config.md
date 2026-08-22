---
type: Example
title: 基本配置示例
description: nbviewer常用配置文件示例，包括端口、缓存、限流、GitHub认证和CDN资源配置
tags:
  - jupyter
  - nbviewer
  - configuration
  - example
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/app.py
---

# 基本配置示例

本文档提供nbviewer常用配置文件示例。

## 最小配置

```python
# nbviewer_config.py
c = get_config()

c.NBViewer.port = 8080
c.NBViewer.host = "0.0.0.0"
```

启动：
```bash
python -m nbviewer --config-file=nbviewer_config.py
```

## 开发环境配置

```python
# nbviewer_config.py - 开发环境
c = get_config()

# 网络
c.NBViewer.port = 5000
c.NBViewer.host = "127.0.0.1"

# 调试
c.Application.log_level = "DEBUG"
c.NBViewer.no_cache = True

# 本地文件（开发时方便查看本地Notebook）
c.NBViewer.localfiles = "/home/user/notebooks"
c.NBViewer.localfile_any_user = True
c.NBViewer.localfile_follow_symlinks = True

# 单线程便于调试
c.NBViewer.threads = 1
```

## 生产环境基础配置

```python
# nbviewer_config.py - 生产环境基础
c = get_config()

# 网络
c.NBViewer.port = 8080
c.NBViewer.host = "0.0.0.0"
c.NBViewer.base_url = "/"

# 性能：进程模式，4核渲染
c.NBViewer.processes = 4

# 缓存TTL
c.NBViewer.cache_expiry_min = 600    # 最短10分钟
c.NBViewer.cache_expiry_max = 7200   # 最长2小时

# 限流
c.NBViewer.rate_limit = 100
c.NBViewer.rate_limit_interval = 600  # 10分钟

# 慢渲染超时
c.NBViewer.render_timeout = 30  # 30秒

# 日志
c.Application.log_level = "INFO"
```

## GitHub API认证配置

```python
# nbviewer_config.py - 含GitHub认证
import os

c = get_config()

# 方式一：Personal Access Token
# 环境变量: export GITHUB_API_TOKEN=ghp_xxxxx
# 无需在配置文件中设置，自动从环境变量读取

# 方式二：OAuth App
# 环境变量: export GITHUB_OAUTH_KEY=xxx
#           export GITHUB_OAUTH_SECRET=xxx

c.NBViewer.port = 8080
c.NBViewer.processes = 4
```

也可直接在配置文件中设置（不推荐，注意不要提交到版本控制）：

```python
c.NBViewer.port = 8080
# 直接设置（不安全，仅用于测试）
# import os
# os.environ["GITHUB_API_TOKEN"] = "ghp_xxxxx"
```

## CDN资源配置

```python
# nbviewer_config.py - 自定义CDN
c = get_config()

c.NBViewer.mathjax_url = "https://cdn.example.com/mathjax/2.7.1/"
c.NBViewer.ipywidgets_base_url = "https://cdn.example.com/npm/"
c.NBViewer.binder_base_url = "https://binder.example.com/v2"

# 版本锁定
c.NBViewer.jupyter_js_widgets_version = "2.1.0"
c.NBViewer.jupyter_widgets_html_manager_version = "0.20.0"
```

## 反向代理子路径配置

当nbviewer部署在反向代理子路径下（如`https://example.com/nbviewer/`）：

```python
# nbviewer_config.py - 子路径部署
c = get_config()

c.NBViewer.port = 8080
c.NBViewer.base_url = "/nbviewer/"

# Nginx配置参考：
# location /nbviewer/ {
#     proxy_pass http://127.0.0.1:8080/nbviewer/;
#     proxy_set_header Host $host;
#     proxy_set_header X-Real-IP $remote_addr;
#     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#     proxy_set_header X-Forwarded-Proto $scheme;
# }
```

## SSL配置

```python
# nbviewer_config.py - 直接SSL（生产建议用Nginx终止SSL）
c = get_config()

c.NBViewer.port = 443
c.NBViewer.sslcert = "/etc/ssl/certs/nbviewer.crt"
c.NBViewer.sslkey = "/etc/ssl/private/nbviewer.key"
```

## 代理配置

企业内网环境通过代理访问外部：

```python
# nbviewer_config.py - 代理
c = get_config()

c.NBViewer.proxy_host = "proxy.example.com"
c.NBViewer.proxy_port = 8080
c.NBViewer.no_check_certificate = True  # 自签名证书环境
```

## StatsD监控配置

```python
# nbviewer_config.py - StatsD监控
c = get_config()

c.NBViewer.statsd_host = "localhost"
c.NBViewer.statsd_port = 8125
c.NBViewer.statsd_prefix = "nbviewer.prod"
```

## 自定义首页

```python
# nbviewer_config.py - 自定义首页
c = get_config()

c.NBViewer.frontpage = "/etc/nbviewer/frontpage.json"
```

frontpage.json格式：
```json
{
  "title": "My Notebook Viewer",
  "subtitle": "内部Notebook查看服务",
  "show_input": true,
  "sections": [
    {
      "header": "示例Notebook",
      "links": [
        {
          "text": "Notebook基础",
          "target": "github/jupyter/notebook/blob/main/docs/source/examples/Notebook/Notebook%20Basics.ipynb"
        }
      ]
    }
  ]
}
```

## 自定义模板和静态资源

```python
# nbviewer_config.py - 自定义模板和静态资源
c = get_config()

# 自定义模板（覆盖默认模板）
c.NBViewer.template_path = "/etc/nbviewer/templates"

# 自定义静态资源（CSS覆盖等）
c.NBViewer.static_path = "/etc/nbviewer/static"
c.NBViewer.static_url_prefix = "/static/"
```

## 完整生产配置参考

```python
# nbviewer_config.py - 完整生产配置
import os

c = get_config()

# === 网络 ===
c.NBViewer.port = 8080
c.NBViewer.host = "127.0.0.1"  # 只监听本地，通过Nginx代理
c.NBViewer.base_url = "/"

# === 性能 ===
c.NBViewer.processes = 4
c.NBViewer.render_timeout = 30
c.NBViewer.cache_expiry_min = 600
c.NBViewer.cache_expiry_max = 7200

# === 限流 ===
c.NBViewer.rate_limit = 100
c.NBViewer.rate_limit_interval = 600

# === 安全 ===
c.NBViewer.content_security_policy = "connect-src 'none';"

# === CDN资源 ===
c.NBViewer.mathjax_url = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/"
c.NBViewer.ipywidgets_base_url = "https://unpkg.com/"
c.NBViewer.binder_base_url = "https://mybinder.org/v2"

# === 监控 ===
c.NBViewer.statsd_host = os.environ.get("STATSD_HOST", "")
c.NBViewer.statsd_port = 8125
c.NBViewer.statsd_prefix = "nbviewer"

# === 日志 ===
c.Application.log_level = "INFO"
```

## 相关文档

- [快速开始](/concepts/01-getting-started.md)：完整CLI参数列表
- [部署指南](/concepts/13-deployment.md)：Docker和Nginx部署
- [应用类与traitlets配置](/concepts/03-app-and-traitlets.md)：配置机制详解
- [Docker部署示例](/examples/04-docker-deploy.md)：容器化部署
