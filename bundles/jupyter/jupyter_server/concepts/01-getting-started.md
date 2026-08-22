---
type: Concept
title: "快速上手"
description: "安装 Jupyter Server、启动服务器、命令行选项、配置文件生成、密码设置与基本 REST API 调用"
tags: [getting-started, installation, cli, configuration, password]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: readme
    resource: /references/serverapp-source.md
    title: serverapp.py 源码信源
  - id: pyproject
    resource: ../../../../../../external/libs/jupyter/jupyter_server/pyproject.toml
    title: pyproject.toml
---

# 快速上手

## 安装

使用 pip 安装 Jupyter Server：

```bash
pip install jupyter_server
```

Jupyter Server 支持 Python ≥ 3.10，可在 Linux、macOS 和 Windows 上运行。

## 启动服务器

最简启动方式：

```bash
jupyter server
```

或使用连字符形式：

```bash
jupyter-server
```

启动后终端会输出类似信息：

```
[I 2024-01-01 12:00:00.000 ServerApp] jupyter_server 2.21.0.dev0 is running at:
[I 2024-01-01 12:00:00.000 ServerApp] http://localhost:8888/tree?token=abc123...
[I 2024-01-01 12:00:00.000 ServerApp]  or http://127.0.0.1:8888/tree?token=abc123...
```

首次启动会生成随机 Token，直接在浏览器中打开带 Token 的 URL 即可访问。

## 常用命令行选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--port` | 指定端口 | `--port=9999` |
| `--ip` | 指定监听 IP | `--ip=0.0.0.0`（允许远程访问） |
| `--no-browser` | 不自动打开浏览器 | `--no-browser` |
| `--root-dir` | 指定根目录 | `--root-dir=/path/to/notebooks` |
| `--base-url` | 设置 URL 前缀 | `--base-url=/jupyter/` |
| `--config` | 指定配置文件 | `--config=my_config.py` |
| `--generate-config` | 生成默认配置文件 | `--generate-config` |
| `--certfile` | SSL 证书文件 | `--certfile=mycert.pem` |
| `--keyfile` | SSL 密钥文件 | `--keyfile=mykey.key` |
| `--allow-root` | 允许 root 用户运行 | `--allow-root` |
| `--PasswordIdentityProvider.token=''` | 禁用 Token 认证（开发用） | |
| `--ServerApp.password=''` | 清空密码 | |

## 子命令

| 子命令 | 说明 |
|--------|------|
| `jupyter server list` | 列出当前运行的 Jupyter Server 实例 |
| `jupyter server stop` | 停止运行中的服务器 |
| `jupyter server password` | 设置/修改登录密码 |
| `jupyter server extension` | 管理服务器扩展（enable/disable/list） |

### 设置密码

```bash
jupyter server password
```

会提示输入并确认密码，密码使用 argon2-cffi 哈希后存储在配置目录中。设置密码后，Token 认证仍然可用，但可以使用密码登录。

## 生成配置文件

```bash
jupyter server --generate-config
```

会在 `~/.jupyter/jupyter_server_config.py` 生成默认配置文件，包含所有可配置项的注释说明。

配置文件使用 Python 语法，例如：

```python
c = get_config()  # noqa
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 9999
c.ServerApp.root_dir = '/home/user/notebooks'
c.ServerApp.open_browser = False
c.ServerApp.token = ''  # 禁用 token（仅开发环境！）
c.PasswordIdentityProvider.hashed_password = 'argon2:$argon2id$v=19$m=...'
```

## REST API 快速调用

Jupyter Server 提供 REST API，主要端点：

```bash
# 获取服务器状态
curl http://localhost:8888/api/status?token=YOUR_TOKEN

# 获取内核列表
curl http://localhost:8888/api/kernels?token=YOUR_TOKEN

# 启动新内核
curl -X POST http://localhost:8888/api/kernels?token=YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{"name": "python3"}'

# 获取目录内容
curl http://localhost:8888/api/contents?token=YOUR_TOKEN

# 获取当前用户信息
curl http://localhost:8888/api/me?token=YOUR_TOKEN
```

所有 API 路径前缀为 `/api/`，认证通过 URL 参数 `?token=` 或请求头 `Authorization: token <TOKEN>` 传递。

## Python API 使用

也可以在 Python 代码中直接启动和控制 Jupyter Server：

```python
from jupyter_server.serverapp import ServerApp

# 创建并初始化服务器实例
server = ServerApp()
server.initialize()

# 启动服务器（阻塞）
server.start()
```

更多程序化用法参见 [ExtensionApp 扩展开发](/concepts/10-extension-system.md)。

## 下一步

- [架构总览](02-architecture-overview.md) — 理解 Jupyter Server 的内部架构
- [ServerApp 生命周期](03-serverapp-lifecycle.md) — 了解服务器启动流程
- [认证授权系统](05-auth-system.md) — 深入安全配置
