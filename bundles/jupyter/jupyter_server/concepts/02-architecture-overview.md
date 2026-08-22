---
type: Concept
title: "架构总览"
description: "Jupyter Server 分层架构：Tornado Web 层、Handler 处理层、Manager 服务层、Extension 插件层与 Kernel 通信层"
tags: [architecture, layers, tornado, handlers, services, design]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: serverapp
    resource: /references/serverapp-source.md
    title: serverapp.py 源码信源
  - id: handlers
    resource: /references/handlers-source.md
    title: base/handlers.py 源码信源
---

# 架构总览

Jupyter Server 采用**分层架构**设计，基于 Tornado 异步 Web 框架构建。从外到内可分为五层：网络层 → Handler 处理层 → 服务管理层 → 扩展层 → 内核通信层。

## 五层架构

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Network (Tornado HTTPServer)                      │
│  HTTP/HTTPS, WebSocket, Unix Socket, SSL/TLS                │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Handler Pipeline                                  │
│  AuthenticatedHandler → JupyterHandler → APIHandler         │
│  认证/授权检查、CORS、模板渲染、JSON序列化                    │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Core Services（Manager 层）                        │
│  ┌──────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐  │
│  │ Contents │ │ Kernels   │ │ Sessions  │ │ Config      │  │
│  │ Manager  │ │ Manager   │ │ Manager   │ │ Manager     │  │
│  └──────────┘ └───────────┘ └───────────┘ └─────────────┘  │
│  ┌──────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐  │
│  │ Kernelspec│ │ Terminals│ │ Events    │ │ Nbconvert   │  │
│  │ Manager  │ │ Manager   │ │ Logger    │ │ Service     │  │
│  └──────────┘ └───────────┘ └───────────┘ └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Extension System                                  │
│  ExtensionApp + ExtensionManager + ExtensionPoint           │
│  JupyterLab / Notebook / 自定义扩展插入此层                   │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Auth System                                       │
│  IdentityProvider（认证）+ Authorizer（授权）                │
│  PasswordIdentityProvider / 自定义认证                        │
├─────────────────────────────────────────────────────────────┤
│  Layer 0: Kernel Communication (jupyter_client + ZMQ)       │
│  Shell / IOPub / Stdin / Control / HB 五通道                 │
└─────────────────────────────────────────────────────────────┘
```

## Layer 5: 网络层（Tornado HTTPServer）

最外层由 Tornado 的 `HTTPServer` 提供，支持：
- **HTTP/HTTPS**：REST API 通信
- **WebSocket**：内核实时通信
- **Unix Socket**：本地 IPC 通信（非 Windows）
- **SSL/TLS**：加密传输
- **端口自动重试**：默认端口 8888 被占用时自动递增（最多 50 次）

入口类是 `ServerWebApplication(web.Application)`，继承自 Tornado 的 Application，负责注册所有 URL 路由和设置。

## Layer 4: Handler 处理层

Handler 是处理 HTTP 请求的核心，采用**三层继承体系**：

```
web.RequestHandler (Tornado)
└── AuthenticatedHandler          # 认证基类：CORS、Cookie、安全头
    └── JupyterHandler            # 核心基类：Manager访问、模板渲染、事件日志
        ├── APIHandler            # REST API基类：JSON序列化、错误处理
        ├── Template404           # 404页面
        ├── FileFindHandler       # 静态文件查找
        ├── MainHandler           # 根路径重定向
        └── PrometheusMetricsHandler  # Prometheus指标端点
```

每个请求的处理流程：
1. `prepare()` 方法执行预处理：认证检查、CORS 验证、来源检查
2. 根据 HTTP 方法（GET/POST/PUT/DELETE）调用对应处理方法
3. 调用 Manager 层执行业务逻辑
4. 渲染模板或返回 JSON 响应

## Layer 3: 核心服务层

所有业务逻辑通过 Manager 类提供，每个 Manager 是独立的 traitlets `Configurable`：

| Manager | 职责 | 同步/异步 |
|---------|------|----------|
| `ContentsManager` | 文件/目录/Notebook CRUD、检查点 | 两者都有 |
| `MappingKernelManager` | 内核生命周期管理（启动/关闭/重启） | 两者都有 |
| `SessionManager` | 内核与文件的映射关系 | 同步为主 |
| `KernelSpecManager` | 可用内核规范的发现与管理 | 同步 |
| `ConfigManager` | 前端 JSON 配置管理 | 同步 |
| `TerminalManager` | 终端会话管理 | 委托第三方 |
| `EventLogger` | 结构化事件记录 | 异步 |

**同步/异步双版本设计**：大多数 Manager 提供同步版本（如 `FileContentsManager`）和异步版本（`AsyncFileContentsManager`）。异步版本使用 `anyio.to_thread` 将阻塞 IO 包装到线程池。

## Layer 2: 扩展系统

扩展通过 `ExtensionApp` 基类接入，由 `ExtensionManager` 统一管理：

- **发现机制**：通过 Python entry points 或 `_jupyter_server_extension_points()` 函数发现
- **加载方式**：被 ServerApp 加载 或 独立启动（自动创建内嵌 ServerApp）
- **Handler 合并**：扩展的 URL 路由和静态路径被合并到主应用
- **配置隔离**：每个扩展有独立的 traitlets 配置

## Layer 1: 认证授权层

v2.0 重构后的安全体系，认证与授权分离：

- **IdentityProvider**：回答"你是谁"——处理登录、Token 验证、Cookie 管理、用户模型
- **Authorizer**：回答"你能做什么"——控制对资源的访问权限
- **User 模型**：使用 `@dataclass` 定义的 User 数据类，包含 username、display_name、avatar_url 等字段

默认实现：`PasswordIdentityProvider`（密码+Token）+ `AllowAllAuthorizer`（允许所有认证用户）。

## Layer 0: 内核通信层

通过 `jupyter_client` 库与内核进程通信：

- 使用 ZeroMQ（pyzmq）进行消息传递
- **五个通道**：
  - **Shell**：代码执行请求/回复（请求-响应模式）
  - **IOPub**：广播输出（stdout/stderr/display/状态更新）
  - **Stdin**：标准输入请求（如 `input()` 函数）
  - **Control**：控制命令（中断/重启，比 Shell 优先级高）
  - **Heartbeat**：心跳检测内核存活

`ZMQChannelsWebsocketConnection` 负责将 WebSocket 消息桥接到 ZMQ 通道。

## 请求生命周期

一个典型 API 请求的完整路径：

```
浏览器 → HTTPServer → Router → Handler.prepare()
    → 认证(IdentityProvider.get_user)
    → 授权(Authorizer.is_authorized)
    → Handler.get()/post() → Manager 方法
    → jupyter_client ZMQ / 文件系统 IO
    → JSON/HTML 响应 → 浏览器
```

## 核心设计模式

1. **traitlets 配置模式**：所有组件使用 traitlets 的 `HasTraits`/`Configurable`，支持配置文件和命令行统一配置
2. **Mix-in 组合模式**：通过 Mixin 类（`ExtensionHandlerMixin`、`ExtensionAppJinjaMixin`）组合功能
3. **同步/异步双轨**：每个核心 Manager 都有同步和异步版本，通过 `ensure_async()` 桥接
4. **可插拔架构**：Manager 类均可通过配置替换（自定义 ContentsManager、自定义 IdentityProvider 等）
5. **事件驱动**：基于 jupyter_events 的结构化事件系统，支持审计和监控

## 相关概念

- [ServerApp 生命周期](03-serverapp-lifecycle.md) — 启动流程详细解析
- [Handler 继承体系](04-handler-hierarchy.md) — Handler 层详细设计
- [认证授权系统](05-auth-system.md) — v2.0 安全架构详解
