---
type: Concept
title: "CLI 与配置"
description: "Jupyverse 提供命令行选项控制服务器行为，支持插件选择、网络配置和 CORS 设置，所有模块配置通过 --set 语法或 FPS 自动生成的 CLI 选项覆盖。"
tags: [cli, configuration, command-line, options, settings, config]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: cli
    resource: /references/cli-source.md
    title: CLI 入口信源
  - id: main
    resource: /references/main-module-source.md
    title: JupyverseModule 主模块信源
  - id: pyproject
    resource: /references/pyproject-source.md
    title: pyproject.toml 信源
---

# CLI 与配置

Jupyverse 的 CLI 基于 FPS 和 rich-click 构建，提供核心服务器选项和灵活的配置覆盖机制。

## CLI 概览

### 基本用法

```bash
jupyverse [OPTIONS]
```

### 获取帮助

```bash
jupyverse --help          # 查看基本选项
jupyverse --help-all      # 查看所有模块的完整配置选项（含插件配置）
```

### 查看配置

```bash
jupyverse --show-config   # 显示实际生效的配置
```

## 核心 CLI 选项

以下是 `jupyverse` 命令直接支持的选项：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--host` | str | `"127.0.0.1"` | 监听地址 |
| `--port` | int | `8000` | 监听端口 |
| `--open-browser` | flag | `False` | 启动后自动打开浏览器 |
| `--debug` | flag | `False` | 启用调试模式（DEBUG 日志级别） |
| `--backend` | str | `"asyncio"` | 事件循环后端（asyncio/trio） |
| `--allow-origin` | str（多次） | - | 允许的 CORS 源 |
| `--query-param` | str（多次） | - | 默认 URL 查询参数（key=value） |
| `--set` | str（多次） | - | 设置任意配置项（点分语法） |
| `--disable` | str（多次） | - | 禁用指定插件 |
| `--websocket-permessage-deflate` | flag | `False` | 启用 WebSocket 压缩 |
| `--timeout` | float | None | 启动超时（秒） |
| `--stop-timeout` | float | `1` | 停止超时（秒） |
| `--show-config` | flag | `False` | 显示实际配置 |
| `--help-all` | flag | `False` | 显示所有配置描述 |

### 监听地址示例

```bash
# 仅本机访问（默认，端口 8000）
jupyverse

# 允许局域网访问
jupyverse --host 0.0.0.0

# 自定义端口
jupyverse --host 0.0.0.0 --port 9999

# 启动后自动打开浏览器
jupyverse --open-browser
```

### 工作目录

Jupyverse 以**当前工作目录**（执行 `jupyverse` 命令的目录）作为文件服务根目录。切换工作目录即可指定 Notebook 位置：

```bash
cd ~/notebooks
jupyverse
```

## 插件管理

### --disable 选项

`--disable` 用于排除不需要的插件（插件名对应 entry point 名称）：

```bash
# 使用 NoAuth 模式（禁用所有其他认证插件）
jupyverse --disable auth --disable auth_fief --disable auth_jupyterhub
```

常见的可禁用插件包括：`auth`、`auth_fief`、`auth_jupyterhub`、`noauth`、`jupyterlab`、`notebook`、`lab`、`retrolab` 等。具体可用插件取决于安装的包。

查看所有已安装插件：

```bash
jupyverse --help-all
```

## 模块配置与 --set 语法

除核心 CLI 选项外，所有模块配置（包括插件配置）通过 `--set` 设置。FPS 也会为每个模块的配置字段自动生成 CLI 选项（通过 `--help-all` 查看）。

### --set 基本语法

```bash
jupyverse --set "模块名.配置项=值"
```

### 常用 --set 配置示例

```bash
# 启用协作模式
jupyverse --set "frontend.collaborative=true"

# 设置 Token 认证的 token 值
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth \
  --set "auth.token=my-secret-token"

# 测试模式（自动创建 admin 用户）
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth \
  --set "auth.test=true"

# 设置默认内核
jupyverse --set "kernels.default_kernel=python3"

# 启用外部内核
jupyverse --set "kernels.allow_external_kernels=true"

# 配置终端 shell（Unix）
jupyverse --set "terminals.name=zsh"

# 多个配置项组合
jupyverse --host 0.0.0.0 --port 8888 \
  --disable auth_fief --disable auth_jupyterhub --disable noauth \
  --set "auth.token=my-token" \
  --set "frontend.collaborative=true"
```

### 值类型自动转换

`--set` 值会自动转换类型：
- `"true"`/`"false"` → 布尔值
- 数字字符串 → 整数/浮点数
- JSON 格式 → 解析为字典/列表
- 其他 → 字符串

### 查看所有可用配置

```bash
jupyverse --help-all
```

这会显示所有模块（包括插件）的配置项、类型和默认值。

## JupyverseConfig（主模块配置）

主模块的默认配置项：

```python
class JupyverseConfig(Config):
    start_server: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    websocket_permessage_deflate: bool = False
    allow_origins: list[str] = []
    open_browser: bool = False
    query_params: dict[str, str] = {}
    debug: bool = False
    openapi_url: str | None = "/openapi.json"
    routes_url: str | None = None
```

其中 `host`、`port`、`open_browser`、`debug`、`allow_origins`、`websocket_permessage_deflate` 有对应的 CLI 选项直接设置。

## 认证模块配置（fps-auth）

安装 `fps-auth` 插件后，可通过 `--set auth.*` 配置：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `auth.mode` | str | `"token"` | 认证模式：token/user |
| `auth.token` | str | 自动生成 | Token 值 |
| `auth.test` | bool | `False` | 测试模式（创建 admin 用户） |
| `auth.cookie_secure` | bool | `False` | Cookie Secure 标志 |
| `auth.client_id` | str | `""` | OAuth 客户端 ID |
| `auth.client_secret` | str | `""` | OAuth 客户端密钥 |
| `auth.redirect_uri` | str | `""` | OAuth 回调 URI |
| `auth.global_email` | str | `"guest@jupyter.com"` | 全局用户邮箱 |

## 配置优先级

配置项的优先级（高到低）：
1. CLI 参数（`--host`、`--port` 等直接选项）
2. `--set` 参数
3. FPS 自动生成的模块 CLI 选项
4. 代码默认值

## 典型启动命令

```bash
# 最简启动（默认端口 8000，自动选择认证插件）
jupyverse

# 开发环境（无认证，所有接口）
jupyverse --host 0.0.0.0 \
  --disable auth --disable auth_fief --disable auth_jupyterhub

# 协作模式（无认证）
jupyverse --host 0.0.0.0 \
  --disable auth --disable auth_fief --disable auth_jupyterhub \
  --set "frontend.collaborative=true"

# Token 认证模式
jupyverse --host 0.0.0.0 --port 8888 \
  --disable auth_fief --disable auth_jupyterhub --disable noauth \
  --set "auth.token=my-secure-token" \
  --allow-origin "https://my-jupyter.example.com"

# 测试模式
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth \
  --set "auth.test=true"
```

## 相关概念

- [安装与启动](01-getting-started.md) — 基本安装和启动步骤
- [FPS 模块系统](03-fps-module-system.md) — CLI 如何通过 entry points 发现插件
- [架构总览](02-architecture-overview.md) — 插件配置如何传递到各模块
