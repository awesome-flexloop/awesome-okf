---
type: Reference
title: "serverapp.py 源码信源"
description: "ServerApp 主应用类源码分析：Tornado Web 服务器启动、配置、Handler 注册与生命周期管理"
tags: [serverapp, tornado, application, lifecycle, entrypoint]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: serverapp-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/serverapp.py
    title: jupyter_server/serverapp.py
---

# serverapp.py 源码信源

## 文件概述

`serverapp.py` 是 Jupyter Server 的入口文件，定义了核心的 `ServerApp` 类。该类继承自 `jupyter_core.application.JupyterApp`，基于 Tornado Web 框架构建后端服务器。

## 核心类

### `ServerWebApplication(web.Application)` (L240)

Tornado Web Application 的子类，负责：
- 初始化 Tornado 设置（cookie_secret、template_path、static_path 等）
- 注册 URL 路由规则
- 管理 Handler 类映射

### `JupyterPasswordApp(JupyterApp)` (L596)

密码设置命令行工具，对应 `jupyter server password` 子命令：
- 使用 `argon2-cffi` 进行密码哈希
- 密码存储在 `jupyter_config_dir/jupyter_server_config.json`
- 提供 `set_password()` 方法写入哈希密码

### `JupyterServerStopApp(JupyterApp)` (L684)

停止运行中的 Jupyter Server：
- 读取 PID 文件和端口信息
- 发送 Shutdown 请求或信号终止进程

### `JupyterServerListApp(JupyterApp)` (L753)

列出当前运行的 Jupyter Server 实例：
- 扫描 runtime 目录中的 server info 文件
- 显示 URL、端口、根目录、PID 等信息

### `ServerApp(JupyterApp)` (L870)

**核心主应用类**，主要 traitlets 配置项：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `ip` | Unicode | 'localhost' | 监听 IP 地址 |
| `port` | Integer | 8888 | 监听端口 |
| `port_retries` | Integer | 50 | 端口冲突重试次数 |
| `base_url` | Unicode | '/' | 基础 URL 前缀 |
| `root_dir` | Unicode | cwd | 笔记本根目录 |
| `default_url` | Unicode | '/tree' | 默认重定向 URL |
| `token` | Unicode | 随机生成 | 认证 Token |
| `password` | Unicode | '' | 哈希后的密码 |
| `disable_check_xsrf` | Bool | False | 禁用 XSRF 检查 |
| `allow_origin` | Union | '' | 允许的跨域来源 |
| `allow_credentials` | Bool | False | CORS 凭证允许 |
| `max_body_size` | Integer | 512*1024*1024 | 请求体大小上限 (512MB) |
| `max_buffer_size` | Integer | 512*1024*1024 | 缓冲区大小上限 |
| `cookie_secret` | Bytes | 随机生成 | Cookie 加密密钥 |
| `login_handler_class` | Type | LoginFormHandler | 登录 Handler 类 |
| `identity_provider_class` | Type | PasswordIdentityProvider | 身份提供者类 |
| `authorizer_class` | Type | AllowAllAuthorizer | 授权器类 |
| `contents_manager_class` | Type | AsyncFileContentsManager | 内容管理器类 |
| `kernel_manager_class` | Type | AsyncMappingKernelManager | 内核管理器类 |
| `session_manager_class` | Type | SessionManager | 会话管理器类 |
| `terminals_enabled` | Bool | True | 是否启用终端 |
| `nbconvert_enabled` | Bool | True | 是否启用 nbconvert |
| `allow_remote_access` | Bool | False | 是否允许远程访问 |
| `autoreload` | Bool | False | 文件修改自动重载 |
| `open_browser` | Bool | True | 启动时自动打开浏览器 |
| `webbrowser_open_new` | Integer | 2 | 浏览器打开方式 |
| `custom_display_url` | Unicode | '' | 自定义显示 URL |
| `jinja_template_vars` | Dict | {} | Jinja2 模板变量 |
| `extra_template_paths` | List | [] | 额外模板路径 |
| `extra_static_paths` | List | [] | 额外静态文件路径 |
| `static_url_prefix` | Unicode | '/static/' | 静态文件 URL 前缀 |
| `jinja_environment_options` | Dict | {} | Jinja2 环境选项 |
| `get_secure_cookie_kwargs` | Dict | {} | 安全 Cookie 参数 |
| `serverapp_class` | Type | None | 备用 ServerApp 类 |
| `event_logger` | Instance | EventLogger | Jupyter 事件记录器 |

**核心方法**：

| 方法 | 说明 |
|------|------|
| `init_serverapp()` | 初始化服务器核心组件 |
| `init_configurables()` | 初始化各 Manager（Contents/Kernel/Session 等） |
| `init_webapp()` | 创建 ServerWebApplication 实例 |
| `init_handlers()` | 注册核心 Handler 路由 |
| `add_extension_handlers()` | 添加扩展 Handler |
| `start()` | 启动服务器主循环 |
| `stop()` | 优雅停止服务器 |
| `cleanup_kernels()` | 清理运行中的内核 |
| `write_server_info()` | 写入服务器信息文件 |
| `load_server_extensions()` | 加载服务器扩展 |
| `init_signal()` | 初始化信号处理 |
| `init_terminals()` | 初始化终端服务 |
| `init_mime_overrides()` | 初始化 MIME 类型覆盖 |

**JUPYTER_SERVICE_HANDLERS 字典** (L184-209)：

注册了内置服务的 Handler 模块：
- `api`: `jupyter_server.services.api.handlers`
- `config`: `jupyter_server.services.config.handlers`
- `contents`: `jupyter_server.services.contents.handlers`
- `files`: `jupyter_server.files.handlers`
- `kernels`: `jupyter_server.services.kernels.handlers`
- `kernelspecs`: `jupyter_server.kernelspecs.handlers` + `jupyter_server.services.kernelspecs.handlers`
- `nbconvert`: `jupyter_server.nbconvert.handlers` + `jupyter_server.services.nbconvert.handlers`

## 常量

- `DEFAULT_STATIC_FILES_PATH`: 静态文件目录
- `DEFAULT_TEMPLATE_PATH_LIST`: 模板路径列表
- `DEFAULT_JUPYTER_SERVER_PORT = 8888`: 默认端口
- `MIN_TORNADO = (6, 1, 0)`: 最低 Tornado 版本要求

## 入口点

CLI 入口：`jupyter-server = "jupyter_server.serverapp:main"`
