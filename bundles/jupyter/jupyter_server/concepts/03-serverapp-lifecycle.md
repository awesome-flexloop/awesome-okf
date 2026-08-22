---
type: Concept
title: "ServerApp 生命周期"
description: "ServerApp 从初始化、配置加载、组件初始化、Web 服务器启动到优雅关闭的完整生命周期"
tags: [lifecycle, serverapp, startup, shutdown, initialization]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: serverapp
    resource: /references/serverapp-source.md
    title: serverapp.py 源码信源
---

# ServerApp 生命周期

`ServerApp` 是 Jupyter Server 的核心编排类，继承自 `jupyter_core.application.JupyterApp`。理解其生命周期对于扩展开发和问题排查至关重要。

## 生命周期概览

```
初始化(initialize)
  ├── 解析命令行参数
  ├── 加载配置文件
  ├── 初始化日志
  ├── init_configurables() → 创建所有 Manager 实例
  ├── init_serverapp() → 服务器核心配置
  ├── init_handlers() → 注册内置 Handlers
  ├── init_webapp() → 创建 ServerWebApplication
  ├── load_extensions() → 加载并链接服务器扩展
  ├── init_signal() → 注册信号处理
  └── write_server_info() → 写入运行信息文件
       │
       ▼
启动(start)
  ├── 绑定端口/套接字
  ├── 启动 IOLoop
  ├── 显示启动 Banner 和 URL
  └── 打开浏览器（可选）
       │
       ▼
运行中(running)
  ├── 处理 HTTP/WebSocket 请求
  ├── 管理内核生命周期
  └── PeriodicCallback（内核回收、指标采集）
       │
       ▼
关闭(stop/cleanup)
  ├── 停止接受新连接
  ├── shutdown kernels → 关闭所有内核
  ├── stop_extensions → 停止扩展
  ├── cleanup_kernels → 清理内核连接
  ├── 删除 server info 文件
  └── 停止 IOLoop
```

## 初始化阶段详解

### 1. 配置加载

JupyterApp 按以下优先级加载配置（高优先级覆盖低优先级）：

1. **命令行参数**（最高优先级）
2. **用户配置文件**：`~/.jupyter/jupyter_server_config.py`
3. **环境变量**：`JUPYTER_SERVER_PORT` 等
4. **代码中的默认值**（最低优先级）

配置文件片段（`jupyter_server_config.d/*.json`）也会被 ExtensionConfigManager 读取并合并。

### 2. init_configurables() — 创建 Manager 实例

按依赖顺序创建核心服务 Manager：

```python
# 核心 Manager 初始化顺序
self.contents_manager = AsyncFileContentsManager(parent=self)
self.kernel_spec_manager = KernelSpecManager(parent=self)
self.kernel_manager = AsyncMappingKernelManager(
    parent=self,
    kernel_spec_manager=self.kernel_spec_manager,
    connection_dir=self.runtime_dir,
)
self.session_manager = SessionManager(
    parent=self,
    kernel_manager=self.kernel_manager,
    contents_manager=self.contents_manager,
)
self.config_manager = ConfigManager(
    parent=self,
    config_dir=os.path.join(self.config_dir, 'serverconfig'),
)
```

每个 Manager 通过 `parent=self` 建立父子关系，可以访问 ServerApp 的配置和日志。

### 3. init_webapp() — 创建 Web 应用

```python
self.web_app = ServerWebApplication(
    handlers=self.handlers,  # 所有 URL 路由
    default_host='',
    settings=settings,       # Tornado 设置
)
```

关键 settings 包括：
- `base_url`: URL 前缀
- `cookie_secret`: Cookie 加密密钥
- `template_path`: Jinja2 模板目录
- `static_path`: 静态文件目录
- `contents_manager`, `kernel_manager` 等 Manager 引用
- `jinja2_env`: Jinja2 模板环境
- `login_url`: 登录页面 URL

### 4. init_handlers() — 注册路由

JUPYTER_SERVICE_HANDLERS 字典定义了内置服务模块：

```python
JUPYTER_SERVICE_HANDLERS = {
    "auth": None,  # 由 identity_provider 提供
    "api": ["jupyter_server.services.api.handlers"],
    "config": ["jupyter_server.services.config.handlers"],
    "contents": ["jupyter_server.services.contents.handlers"],
    "files": ["jupyter_server.files.handlers"],
    "kernels": ["jupyter_server.services.kernels.handlers"],
    "kernelspecs": ["jupyter_server.kernelspecs.handlers",
                    "jupyter_server.services.kernelspecs.handlers"],
    "nbconvert": ["jupyter_server.nbconvert.handlers",
                  "jupyter_server.services.nbconvert.handlers"],
}
```

每个模块导出 `default_handlers` 列表，被合并到主路由表中。扩展的 Handlers 在 `add_extension_handlers()` 中追加。

### 5. load_extensions() — 加载扩展

1. 从配置和 entry points 发现扩展
2. 创建 ExtensionPackage 实例
3. 按顺序调用：`link_extension()` → `start_extension()`
4. 扩展的 Handlers 和静态路径被合并到 web_app

## 启动阶段

### 端口绑定

```python
sockets = bind_sockets(self.port, self.ip)
self.http_server = httpserver.HTTPServer(self.web_app)
self.http_server.add_sockets(sockets)
```

如果端口被占用，会从当前端口开始递增重试，最多 `port_retries` 次（默认 50）。

支持 Unix Socket（非 Windows）：
```python
sockets = [bind_unix_socket(self.unix_socket)]
```

### IOLoop 启动

Tornado 的 IOLoop 开始事件循环，监听所有已绑定的 socket。

启动 Banner 显示访问 URL 和 Token，方便用户直接复制到浏览器。

## 运行阶段

### PeriodicCallbacks

服务器运行时，多个 PeriodicCallback 周期性执行：

| 回调 | 默认间隔 | 说明 |
|------|---------|------|
| `cull_kernels` | `cull_interval` (300s) | 回收空闲内核 |
| `last_activity` | 60s | 更新 Prometheus 最后活动指标 |

### 请求处理

运行期间，Tornado IOLoop 持续处理：
- HTTP 请求 → Handler 链
- WebSocket 连接 → ZMQ 桥接
- 内核事件 → IOPub 广播

## 关闭阶段

### 优雅关闭流程

收到 SIGINT/SIGTERM 或调用 `stop()` 时：

1. **停止接受新请求**：关闭 HTTP 服务器监听
2. **关闭 WebSocket 连接**：通知前端连接即将关闭
3. **shutdown_kernels()**：向所有运行中的内核发送 shutdown 请求
4. **shutdown_all_kernels()**：等待内核进程终止（有超时）
5. **stop_extensions()**：调用每个扩展的 `stop_extension()`
6. **清理临时文件**：删除 kernel connection 文件
7. **删除 server info**：从 runtime 目录删除 JSON 信息文件
8. **停止 IOLoop**：`self.io_loop.stop()`

### Server Info 文件

运行时在 `jupyter_runtime_dir/` 写入 `jpserver-<pid>.json`，包含：

```json
{
    "base_url": "/",
    "hostname": "localhost",
    "password": false,
    "pid": 12345,
    "port": 8888,
    "root_dir": "/home/user",
    "secure": false,
    "token": "abc123...",
    "url": "http://localhost:8888/",
    "version": "2.21.0"
}
```

`jupyter server list` 和 `jupyter server stop` 命令读取这些文件来发现和控制运行中的实例。

## 自定义扩展中的生命周期钩子

编写 ExtensionApp 时，可以重写以下生命周期方法：

```python
from jupyter_server.extension.application import ExtensionApp

class MyExtension(ExtensionApp):
    def initialize_settings(self):
        """初始化扩展设置"""
        ...

    def initialize_handlers(self):
        """注册扩展 URL Handlers"""
        self.handlers.append(('/myext/api/(.*)', MyAPIHandler))

    async def _start_jupyter_server_extension(self, serverapp):
        """扩展启动时调用"""
        await super()._start_jupyter_server_extension(serverapp)
        # 自定义启动逻辑

    def _stop_jupyter_server_extension(self):
        """扩展停止时调用"""
        # 清理资源
        ...
```

## 相关概念

- [架构总览](02-architecture-overview.md) — 理解各层在生命周期中的角色
- [Handler 继承体系](04-handler-hierarchy.md) — 请求处理链详解
- [扩展系统](10-extension-system.md) — ExtensionApp 开发指南
