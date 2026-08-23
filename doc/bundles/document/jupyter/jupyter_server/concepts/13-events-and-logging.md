---
type: Concept
title: "事件系统与日志"
description: "jupyter_events 结构化事件、事件 Schema 注册、日志配置、Prometheus 指标与可观测性"
tags: [events, logging, jupyter-events, observability, metrics, prometheus, audit]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:05:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: serverapp
    resource: /references/serverapp-source.md
    title: ServerApp 源码信源
---

# 事件系统与日志

Jupyter Server 2.x 集成了 `jupyter_events` 结构化事件系统，提供标准化的事件发射、Schema 验证和审计日志能力。同时支持传统的 Python logging 和 Prometheus 指标。

## 事件系统（jupyter_events）

### 核心概念

| 概念 | 说明 |
|------|------|
| Event（事件） | 结构化 JSON 对象，描述一次系统动作 |
| Schema（事件模式） | JSON Schema 定义事件的字段、类型和版本 |
| Listener（监听器） | 接收并处理事件的对象（日志、文件、API） |
| Emitter（发射器） | 发射事件的组件 |

### 内置事件类型

| 事件 | Schema 文件 | 触发时机 |
|------|-------------|---------|
| 服务器启停 | `serverapp/v1.yaml` | Server 启动/停止 |
| 内核生命周期 | `kernels/v1.yaml` | 内核启动/关闭/重启 |
| 内核状态变化 | `kernels_state/v1.yaml` | 内核状态切换（idle/busy） |
| 会话操作 | `sessions/v1.yaml` | 会话创建/删除 |
| 文件操作 | `contents/v1.yaml` | 文件创建/修改/删除/重命名 |
| 认证事件 | `auth/v1.yaml` | 登录/登录失败/登出 |

### 事件 Schema 示例

```yaml
# event_schemas/org.jupyter.server.contents/v1.yaml
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "/contents"
version: 1
title: "Contents Service Event"
type: object
properties:
  action:
    type: string
    enum: [get, save, rename, delete, new, checkpoint]
  path:
    type: string
  type:
    type: string
    enum: [file, directory, notebook]
  user:
    type: string
required: [action, path, user]
```

### 发射事件

Manager 组件通过 `self.log` 或 event logger 发射事件：

```python
from jupyter_events import EventLogger

class ContentsManager:
    async def save(self, model, path):
        # ... 保存文件 ...
        self.event_logger.emit(
            schema_id="https://schema.jupyter.org/jupyter_server/contents/v1",
            data={
                "action": "save",
                "path": path,
                "type": model.get("type"),
                "user": self.current_user,
            }
        )
```

### 配置事件输出

```python
# jupyter_server_config.py
c.EventLogger.handlers = [
    "logging-short",           # 简短日志格式
    "file:///var/log/jupyter/events.log",  # 文件输出
    # "console-json",          # JSON 控制台输出（开发用）
]

# 也可以添加自定义 handler
from jupyter_events.logger import EventHandler
class MyEventHandler(EventHandler):
    async def emit(self, data, schema_id, version):
        await self.audit_api.post(data)
```

## Python Logging

### 日志配置

Jupyter Server 使用 Python 标准 logging 模块，配置通过 traitlets：

```python
# 设置日志级别
c.ServerApp.log_level = "INFO"     # DEBUG/INFO/WARNING/ERROR/CRITICAL

# 日志文件
c.ServerApp.log_file = "/var/log/jupyter/server.log"

# 日志格式
c.ServerApp.log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```

### 命令行日志级别

```bash
jupyter server --log-level=DEBUG      # 调试模式
jupyter server --debug                 # 等价于 --log-level=DEBUG
jupyter server -vv                     # 详细日志
```

### Logger 层级

```
jupyter_server
├── jupyter_server.serverapp
├── jupyter_server.base
│   └── jupyter_server.base.handlers
├── jupyter_server.services
│   ├── jupyter_server.services.contents
│   ├── jupyter_server.services.kernels
│   ├── jupyter_server.services.sessions
│   └── jupyter_server.services.config
├── jupyter_server.auth
├── jupyter_server.extension
└── jupyter_server.gateway
```

在扩展代码中使用 logger：

```python
import logging
log = logging.getLogger("jupyter_server.extension.my_extension")
log.info("Extension loaded successfully")
```

## 访问日志

Jupyter Server 通过 Tornado 的 log_function 记录 HTTP 访问日志：

```
[I 2024-01-01 12:00:00.000 ServerApp] 200 GET /api/contents?token=... (user@127.0.0.1) 12.34ms
[I 2024-01-01 12:00:01.000 ServerApp] 200 POST /api/kernels?token=... (user@127.0.0.1) 1234.56ms
[W 2024-01-01 12:00:02.000 ServerApp] 403 GET /api/contents/secret?token=... (user@127.0.0.1) 1.23ms
```

格式：`状态码 方法 路径 (用户@IP) 耗时`

## Prometheus 指标

启用 Prometheus 指标端点：

```python
c.ServerApp.prometheus_enabled = True
c.ServerApp.prometheus_port = 8889  # 独立的 metrics 端口（可选）
```

### 核心指标

| 指标名 | 类型 | 说明 |
|--------|------|------|
| `jupyter_server_start_time` | Gauge | 服务器启动时间戳 |
| `jupyter_server_kernel_count` | Gauge | 当前运行内核数 |
| `jupyter_server_terminal_count` | Gauge | 当前运行终端数 |
| `jupyter_server_http_request_duration_seconds` | Histogram | HTTP 请求延迟分布 |
| `jupyter_server_http_requests_total` | Counter | HTTP 请求总数（按方法/状态码） |
| `jupyter_server_kernel_culls_total` | Counter | 回收的空闲内核数 |
| `jupyter_server_ws_connections_active` | Gauge | 活跃 WebSocket 连接数 |

### 访问指标

```bash
# 通过独立端口
curl http://localhost:8889/metrics

# 或通过主服务器（需认证）
curl http://localhost:8888/api/metrics?token=xxx
```

## 可观测性最佳实践

### 开发环境

```python
c.ServerApp.log_level = "DEBUG"
c.EventLogger.handlers = ["console-json"]
c.ServerApp.prometheus_enabled = True
```

### 生产环境

```python
c.ServerApp.log_level = "INFO"
c.ServerApp.log_file = "/var/log/jupyter/server.log"
c.EventLogger.handlers = ["logging-short", "file:///var/log/jupyter/audit.log"]
c.ServerApp.prometheus_enabled = True
c.ServerApp.prometheus_port = 8889  # 独立端口，内部访问
```

### 审计日志

对于合规场景，将文件操作和认证事件发送到审计系统：

```python
c.EventLogger.allowed_schemas = [
    "https://schema.jupyter.org/jupyter_server/auth/*",
    "https://schema.jupyter.org/jupyter_server/contents/*",
]
```

## 日志轮转

对于长时间运行的服务，建议使用系统级日志轮转（logrotate）：

```
# /etc/logrotate.d/jupyter-server
/var/log/jupyter/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload jupyter-server
    endscript
}
```

## 相关概念

- [ServerApp 生命周期](03-serverapp-lifecycle.md) — 启动/关闭事件
- [认证授权系统](05-auth-system.md) — 认证安全事件
- [部署与安全](15-deployment-and-security.md) — 生产环境日志配置
