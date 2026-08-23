---
type: Concept
title: 快速开始
description: nbviewer安装方式、命令行参数、配置文件、环境变量和Docker部署入门
tags:
  - jupyter
  - nbviewer
  - getting-started
  - installation
  - configuration
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/app.py
---

# 快速开始

## 安装

### pip安装

```bash
pip install nbviewer
```

### 源码安装

```bash
git clone https://github.com/jupyter/nbviewer.git
cd nbviewer
pip install -e .
```

## 启动服务

### 最简启动

```bash
python -m nbviewer
```

默认监听 `0.0.0.0:5000`，访问 http://localhost:5000 即可使用。

### 指定端口和地址

```bash
python -m nbviewer --port=8080 --host=127.0.0.1
```

## 命令行参数

### 常用参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--port` | 5000 | 监听端口 |
| `--host` | 0.0.0.0 | 监听地址 |
| `--base-url` | `/` | URL前缀（反向代理时使用） |
| `--localfiles` | "" | 本地文件根目录 |
| `--threads` | 1 | 渲染线程数 |
| `--processes` | 0 | 渲染进程数（>0启用进程模式） |
| `--no-cache` | False | 禁用缓存 |
| `--rate-limit` | 60 | 限流阈值 |
| `--rate-limit-interval` | 600 | 限流窗口（秒） |
| `--render-timeout` | 15 | 慢渲染超时（秒） |
| `--default-format` | html | 默认输出格式 |
| `--config-file` | nbviewer_config.py | 配置文件路径 |
| `--log-level` | INFO | 日志级别 |
| `--debug` | - | 设置DEBUG日志级别 |
| `--proxy-host` | "" | HTTP代理地址 |
| `--proxy-port` | -1 | HTTP代理端口 |
| `--no-check-certificate` | False | 禁用SSL验证 |
| `--statsd-host` | "" | StatsD服务器地址 |
| `--statsd-port` | 8125 | StatsD端口 |
| `--mathjax-url` | cdnjs MathJax | MathJax CDN地址 |
| `--binder-base-url` | mybinder.org | Binder服务URL |
| `--frontpage` | frontpage.json | 首页配置文件路径 |
| `--sslcert` | 无 | SSL证书路径 |
| `--sslkey` | 无 | SSL私钥路径 |

### Flag参数

| Flag | 说明 |
|------|------|
| `--debug` | DEBUG日志级别 |
| `--no-cache` | 禁用缓存 |
| `--no-check-certificate` | 不验证SSL证书 |
| `--localfile-any-user` | 服务非others-readable文件 |
| `--localfile-follow-symlinks` | 跟随符号链接 |
| `--generate-config` | 生成默认配置文件 |
| `-y` / `--yes` | 自动确认覆盖 |

## 配置文件

生成默认配置文件：

```bash
python -m nbviewer --generate-config
```

这会在当前目录生成 `nbviewer_config.py`，包含所有可配置项的默认值和注释。

使用配置文件启动：

```bash
python -m nbviewer --config-file=nbviewer_config.py
```

配置示例：

```python
c = get_config()

c.NBViewer.port = 8080
c.NBViewer.processes = 4
c.NBViewer.rate_limit = 100
c.NBViewer.cache_expiry_max = 3600
c.NBViewer.mathjax_url = "https://cdn.example.com/mathjax/2.7.1/"
c.NBViewer.localfiles = "/path/to/notebooks"
c.NBViewer.localfile_any_user = True
```

## 环境变量

### GitHub API认证

| 环境变量 | 说明 |
|----------|------|
| `GITHUB_API_TOKEN` | Personal Access Token |
| `GITHUB_OAUTH_KEY` | OAuth App Client ID |
| `GITHUB_OAUTH_SECRET` | OAuth App Client Secret |
| `GITHUB_API_URL` | GitHub Enterprise API URL |

配置认证后GitHub API速率限制从60次/小时提升到5000次/小时。

### Memcached配置

| 环境变量 | 说明 |
|----------|------|
| `MEMCACHIER_SERVERS` | MemCachier服务地址 |
| `MEMCACHIER_USERNAME` | MemCachier用户名 |
| `MEMCACHIER_PASSWORD` | MemCachier密码 |
| `MEMCACHE_SERVERS` | Memcached地址（逗号分隔） |
| `NBCACHE_PORT` | Docker容器链接 |

### 其他环境变量

| 环境变量 | 说明 |
|----------|------|
| `GOOGLE_ANALYTICS_ID` | Google Analytics ID |
| `JUPYTERHUB_SERVICE_PREFIX` | JupyterHub服务前缀 |
| `JUPYTERHUB_SERVICE_URL` | JupyterHub服务URL |
| `DEBUG` | 设置DEBUG日志级别 |
| `NBVIEWER_STATIC_PATH` | 自定义静态文件路径 |
| `NBVIEWER_TEMPLATE_PATH` | 自定义模板路径 |

## 本地文件服务

启用本地文件服务（安全风险）：

```bash
python -m nbviewer --localfiles=/path/to/notebooks
```

访问 http://localhost:5000/localfile/ 浏览目录和Notebook。

安全选项：
- `--localfile-any-user`：允许服务没有others-read权限的文件
- `--localfile-follow-symlinks`：跟随符号链接

## Docker部署

```bash
# 单容器
docker run -p 8080:8080 jupyter/nbviewer

# 使用docker-compose（含Memcached）
docker-compose up
```

## 验证安装

启动后访问以下URL验证：
- http://localhost:5000/ — 首页
- http://localhost:5000/faq — FAQ页面
- http://localhost:5000/github/jupyter/notebook/blob/main/docs/source/examples/Notebook/Notebook%20Basics.ipynb — 渲染示例Notebook

## 相关文档

- [架构概览](/concepts/02-architecture-overview.md)：理解系统架构
- [部署指南](/concepts/13-deployment.md)：生产环境部署
- [基本配置示例](/examples/01-basic-config.md)：配置文件示例
