---
type: Example
title: JupyterHub 快速入门
description: 在本地环境中快速安装、配置并启动 JupyterHub v6.0.0b2，使用 DummyAuthenticator 进行测试验证
tags: [jupyterhub, example, quickstart, installation, configuration, dummy-authenticator]
sources:
  - id: app-source
    resource: ../references/app-source.md
    title: JupyterHub Application 源码参考
  - id: auth-source
    resource: ../references/auth-source.md
    title: JupyterHub 认证器体系源码参考
generated: { by: reference_agent/source-code-to-okf-wiki, at: "2026-08-22" }
status: stable
stale_after: "2027-08-22"
---

# JupyterHub 快速入门

本示例将指导你在本地环境中快速安装和启动 JupyterHub v6.0.0b2，使用 DummyAuthenticator 进行无密码测试，并验证运行状态。

> **前置知识**：建议先阅读 [JupyterHub 架构概览](../concepts/architecture-overview.md) 了解核心组件和请求流程。

## 1. 环境准备

### 1.1 Python 版本要求

JupyterHub v6.0.0b2 要求 **Python 3.9 或更高版本**。

```bash
# 检查 Python 版本
python3 --version
# 或
python --version
```

推荐使用虚拟环境隔离依赖：

```bash
# 创建虚拟环境
python3 -m venv jupyterhub-env

# 激活虚拟环境（Linux/macOS）
source jupyterhub-env/bin/activate

# 激活虚拟环境（Windows PowerShell）
.\jupyterhub-env\Scripts\Activate.ps1
```

### 1.2 安装 JupyterHub

使用 pip 安装 JupyterHub（含预发布版本）：

```bash
pip install --pre jupyterhub==6.0.0b2
```

> **注意**：`--pre` 参数允许安装预发布版本（beta 版本）。生产环境请使用正式发布版。

### 1.3 安装 Configurable HTTP Proxy

JupyterHub 默认使用 Node.js 的 `configurable-http-proxy` (CHP) 作为前端代理。

```bash
# 全局安装 configurable-http-proxy
npm install -g configurable-http-proxy
```

验证安装：

```bash
configurable-http-proxy --version
```

> 如果尚未安装 Node.js，请先从 [nodejs.org](https://nodejs.org/) 下载安装。npm 随 Node.js 一起提供。

## 2. 启动 JupyterHub（默认配置）

完成安装后，可以直接使用默认配置启动 JupyterHub：

```bash
jupyterhub
```

首次启动时，JupyterHub 会：

1. 在当前目录创建 SQLite 数据库 `jupyterhub.sqlite`
2. 生成 cookie secret 文件 `jupyterhub_cookie_secret`
3. 启动 Configurable HTTP Proxy（监听端口 8000）
4. 启动 Hub 进程（监听端口 8081）

### 默认访问地址

启动成功后，在浏览器中访问：

```
http://localhost:8000
```

你将被重定向到登录页面 `/hub/login`。

> 默认认证器为 **PAMAuthenticator**，需要使用操作系统的用户名和密码登录。如果在本地没有合适的系统用户用于测试，请继续阅读下一节使用 DummyAuthenticator。

## 3. 使用 DummyAuthenticator 快速测试

DummyAuthenticator 是一个不做任何验证的测试认证器，接受任意用户名和密码，非常适合开发和演示场景。

### 3.1 生成配置文件

```bash
jupyterhub --generate-config
```

此命令会在当前目录生成默认配置文件 `jupyterhub_config.py`。

### 3.2 编辑配置文件

在 `jupyterhub_config.py` 中添加以下配置：

```python
# jupyterhub_config.py

# 使用 DummyAuthenticator（测试用，不验证密码）
c.JupyterHub.authenticator_class = 'dummy'

# 允许所有用户登录（DummyAuthenticator 不做白名单校验）
c.Authenticator.allow_all = True

# 设置管理员用户
c.Authenticator.admin_users = {'admin'}

# 使用 SimpleLocalProcessSpawner（不做用户切换，适合测试）
c.JupyterHub.spawner_class = 'simple'
```

> ⚠️ **安全警告**：DummyAuthenticator 仅用于开发和测试，**严禁在生产环境中使用**。任何人都可以用任意用户名登录。

### 3.3 启动 JupyterHub

```bash
jupyterhub -f jupyterhub_config.py
```

访问 http://localhost:8000，在登录页面输入任意用户名（如 `admin`）和任意密码即可登录。登录后会自动触发 Spawn 流程，启动你的单用户 Jupyter 服务器。

## 4. 基本配置示例

以下是一个更完整的 `jupyterhub_config.py` 配置示例，涵盖常用配置项：

```python
# jupyterhub_config.py — JupyterHub v6.0.0b2 基本配置示例

# ========== 网络配置 ==========
# 公共访问地址（Proxy 监听地址）
c.JupyterHub.bind_url = 'http://:8000'

# Hub 监听 IP 和端口
c.JupyterHub.hub_ip = '127.0.0.1'
c.JupyterHub.hub_port = 8081

# ========== 认证配置 ==========
# 使用 DummyAuthenticator 快速测试
c.JupyterHub.authenticator_class = 'dummy'
c.Authenticator.allow_all = True
c.Authenticator.admin_users = {'admin'}

# ========== Spawner 配置 ==========
# 使用 SimpleLocalProcessSpawner（测试用，无用户切换）
c.JupyterHub.spawner_class = 'simple'

# 单用户服务器启动超时（秒）
c.Spawner.start_timeout = 120

# 默认工作目录
c.Spawner.notebook_dir = '~/notebooks'

# 默认启动 JupyterLab（需已安装 jupyterlab）
c.Spawner.default_url = '/lab'

# ========== 数据库配置 ==========
# 使用 SQLite 数据库
c.JupyterHub.db_url = 'sqlite:///jupyterhub.sqlite'

# ========== 日志配置 ==========
# 设置日志级别
c.JupyterHub.log_level = 'INFO'
```

> 关于各配置项的详细含义，请参考 [JupyterHub Application 源码参考](../references/app-source.md)。

## 5. 验证运行状态

### 5.1 健康检查端点

JupyterHub 提供了健康检查端点，用于监控服务状态：

```bash
# Hub 健康检查（返回 200 表示 Hub 正常运行）
curl http://localhost:8000/hub/health
```

正常响应：

```json
{"status": "ok"}
```

### 5.2 检查进程状态

```bash
# 查看 JupyterHub 和 CHP 进程
ps aux | grep -E "(jupyterhub|configurable-http-proxy)"
```

### 5.3 查看已注册路由

通过 CHP 的 API 查看当前路由表：

```bash
# CHP 默认 API 端口为 8001，auth_token 在启动日志中输出
curl -H "Authorization: token <api_token>" http://localhost:8001/api/routes
```

### 5.4 登录后验证

1. 访问 http://localhost:8000/hub/login
2. 输入用户名 `admin` 和任意密码登录
3. 等待 Spawn 完成，跳转到 JupyterLab 或 Jupyter Notebook 界面
4. 管理员可访问 http://localhost:8000/hub/admin 查看管理面板

## 6. 创建管理员用户

有两种方式设置管理员用户：

### 方式一：通过配置文件

在 `jupyterhub_config.py` 中配置：

```python
c.Authenticator.admin_users = {'admin', 'jupyteradmin'}
```

### 方式二：通过命令行创建

```bash
# 使用 jupyterhub 命令创建管理员（需要数据库已存在）
jupyterhub user create admin --admin
```

管理员登录后可以访问 `/hub/admin` 管理面板，执行以下操作：

- 查看所有用户及其服务器状态
- 启动/停止用户服务器
- 添加/删除用户
- 访问用户服务器（通过"访问服务器"按钮）

## 7. 常见问题排查

### 7.1 configurable-http-proxy 未找到

**症状**：启动时报错 `Error: Could not find configurable-http-proxy`。

**解决方案**：

```bash
# 确认 npm 全局安装路径在 PATH 中
npm config get prefix
# 将 <prefix>/bin 添加到 PATH（Linux/macOS）
export PATH="$(npm config get prefix)/bin:$PATH"

# Windows 用户确保 npm 全局目录在 PATH 中
npm root -g
```

### 7.2 端口被占用

**症状**：启动时报错 `Address already in use`。

**解决方案**：

```bash
# 查找占用端口的进程（Linux/macOS）
lsof -i :8000

# 查找占用端口的进程（Windows）
netstat -ano | findstr :8000

# 或在配置文件中指定其他端口
c.JupyterHub.bind_url = 'http://:8888'
```

### 7.3 Spawn 失败 — 权限错误

**症状**：登录后 Spawn 失败，日志显示权限错误。

**原因**：默认使用 `LocalProcessSpawner` 需要 setuid 权限（root 或特殊配置）。

**解决方案**：使用 `SimpleLocalProcessSpawner` 进行测试：

```python
c.JupyterHub.spawner_class = 'simple'
```

### 7.4 单用户服务器启动超时

**症状**：页面显示"Server failed to start"或超时错误。

**解决方案**：增加启动超时时间：

```python
c.Spawner.start_timeout = 120  # 默认 60 秒，增加到 120 秒
```

### 7.5 数据库被锁定

**症状**：日志中出现 `database is locked` 错误。

**解决方案**：停止所有 JupyterHub 进程后删除旧数据库重新启动：

```bash
# 停止所有 JupyterHub 相关进程
pkill -f jupyterhub
pkill -f configurable-http-proxy

# 删除旧数据库（会丢失用户数据，仅测试环境）
rm jupyterhub.sqlite

# 重新启动
jupyterhub -f jupyterhub_config.py
```

## 下一步

- 了解 [Authenticator 认证系统](../concepts/authenticator.md) 的完整机制
- 学习 [自定义认证器示例](custom-authenticator.md) 扩展认证逻辑
- 了解 [Spawner 机制](../concepts/spawner.md) 自定义服务器启动方式
- 学习 [自定义 Spawner 示例](custom-spawner.md) 适配不同计算后端
