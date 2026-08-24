---
okf_version: "0.2"
type: bundle
title: "jupyter_server"
description: "Jupyter 后端核心服务：Tornado HTTP 服务器、认证授权、内核管理、内容管理、扩展系统与 REST/WebSocket API。本知识束从源码出发，系统讲解 Jupyter Server v2.21.0.dev0 的架构、API 和实战用法。"
---

# jupyter_server

> Jupyter 生态的后端核心服务：提供 REST API、WebSocket 内核通信、文件管理、认证授权和扩展框架。

`jupyter_server` 是 JupyterLab、Jupyter Notebook Classic、Voilà 等前端应用共同依赖的后端服务。它基于 Tornado 异步框架，提供 Notebook/文件管理、内核生命周期管理、终端会话、扩展插件等核心能力，是所有 Jupyter Web 应用的服务端基石。

## 快速导航

### 📘 核心概念（16 篇）

**入门**
- [简介](concepts/00-introduction.md) — Jupyter Server 在生态中的定位、版本信息、依赖关系与核心能力
- [5分钟快速上手](concepts/01-getting-started.md) — 安装、启动、命令行选项、访问 UI、基本 API 测试

**架构与基础**
- [架构总览](concepts/02-architecture-overview.md) — 五层架构模型（网络层→Handler→服务层→扩展层→认证层）、ZMQ 内核通信通道
- [ServerApp 生命周期](concepts/03-serverapp-lifecycle.md) — 初始化→配置加载→扩展发现→HTTP 启动→请求处理→优雅关闭的完整流程
- [Handler 继承体系](concepts/04-handler-hierarchy.md) — AuthenticatedHandler→JupyterHandler→APIHandler 三层继承、@allow_unauthenticated/@authorized 装饰器、错误处理机制
- [认证授权系统](concepts/05-auth-system.md) — IdentityProvider/Authorizer 分离架构、User 模型、Token+密码双模式、CORS 配置、自定义安全后端
- [配置管理](concepts/06-config-management.md) — traitlets+JSON 双轨配置体系、四级配置文件搜索优先级、递归合并机制、核心配置项速查

**核心服务**
- [内容管理服务](concepts/07-contents-service.md) — ContentsManager 文件/目录/Notebook CRUD、Checkpoints 检查点、大文件分块上传、Notebook 信任机制
- [内核管理](concepts/08-kernel-management.md) — MappingKernelManager 多内核管理、内核生命周期、空闲回收（culling）、KernelSpec 发现、ZMQ 五通道
- [会话管理](concepts/09-sessions-service.md) — Session 关联文件与内核映射、多前端共享内核、Terminal 终端管理、NbConvert 转换服务
- [扩展系统](concepts/10-extension-system.md) — ExtensionApp 基类、ExtensionManager 扩展发现、entry points 注册、Handler/静态资源/配置扩展
- [WebSocket 通信](concepts/11-websocket-communication.md) — WebSocket 基类、ZMQ↔WS 消息桥接、Jupyter 消息协议、心跳保活、Nginx 代理配置
- [网关客户端](concepts/12-gateway-client.md) — GatewayClient 远程内核代理、Enterprise Gateway 集成、K8s/YARN/Docker 分布式执行

**进阶功能**
- [事件系统与日志](concepts/13-events-and-logging.md) — jupyter_events 结构化事件、Schema 注册、Python logging、Prometheus 指标、审计日志
- [异步编程模型](concepts/14-async-programming.md) — anyio 抽象层、async/await Handler、同步/异步双版本 Manager、to_thread 桥接、异步最佳实践与陷阱
- [部署与安全](concepts/15-deployment-and-security.md) — 生产部署指南、Nginx 反向代理、HTTPS 证书、Docker 容器化、systemd 服务配置与安全加固清单

- [概念文档索引](concepts/index.md) — 概念文档总目录

### 💻 示例代码（3 个）

- [基础 API 使用](examples/01-basic-api-usage.md) — curl/Python requests 调用 Contents/Kernels/Sessions REST API，文件管理、内核启动与会话操作完整流程
- [编写简单扩展](examples/02-simple-extension.md) — 从零创建 ExtensionApp 扩展，添加自定义 API 端点、HTML 页面、配置项、entry points 打包
- [WebSocket 内核通信](examples/03-websocket-kernel.md) — Python/JavaScript WebSocket 客户端连接内核、发送 execute_request、实时接收 stdout/result/error 输出
- [示例文档索引](examples/index.md) — 示例总目录

### 📄 源码信源（10 个模块）

- [serverapp.py](references/serverapp-source.md) — ServerApp 主应用类、ServerWebApplication、JupyterPasswordApp/JupyterServerStopApp/JupyterServerListApp 子命令
- [base/handlers.py](references/handlers-source.md) — AuthenticatedHandler、JupyterHandler、APIHandler、FileFindHandler 等核心 Handler
- [base/websocket.py](references/websocket-base-source.md) — WebSocketHandler 基类、认证继承、消息序列化
- [auth/](references/auth-source.md) — IdentityProvider、PasswordIdentityProvider、Authorizer、AllowAllAuthorizer、LoginHandler、User 模型
- [services/contents/](references/contents-source.md) — ContentsManager、FileContentsManager、Checkpoints、ContentsAPIHandler
- [services/kernels/](references/kernels-source.md) — MappingKernelManager、KernelWebsocketHandler、KernelSpecManager
- [services/ 其他模块](references/services-source.md) — SessionManager、TerminalManager、ConfigManager、NbconvertHandler
- [extension/](references/extension-source.md) — ExtensionApp、ExtensionManager、扩展发现与加载
- [gateway/](references/gateway-source.md) — GatewayClient、GatewayKernelManager、GatewayWebSocketHandler
- [配置管理](references/config-source.md) — traitlets 配置、JSONConfigManager、递归合并

- [源码信源索引](references/index.md) — 信源文档总目录

## 版本信息

| 属性 | 值 |
|------|-----|
| 版本 | **v2.21.0.dev0** |
| Python 版本要求 | ≥ 3.10 |
| 构建系统 | Hatchling ≥ 1.18 |
| 核心依赖 | tornado ≥ 6.2.0, traitlets ≥ 5.6.0, jupyter_client ≥ 7.4.4, jupyter_core ≥ 5.7.0, anyio ≥ 3.6.2, argon2-cffi |
| Web 框架 | Tornado ≥ 6.2.0 |
| 异步库 | anyio ≥ 3.6.2 |
| 认证库 | argon2-cffi, pyopenssl |
| 许可证 | BSD-3-Clause |
| CLI 命令 | `jupyter-server` / `jupyter server` |
| 默认端口 | 8888 |
| 源码路径 | `external/libs/jupyter/jupyter_server/` |

---

**推荐阅读顺序：** [简介](concepts/00-introduction.md) → [快速上手](concepts/01-getting-started.md) → [架构总览](concepts/02-architecture-overview.md) → [ServerApp 生命周期](concepts/03-serverapp-lifecycle.md) → [Handler 体系](concepts/04-handler-hierarchy.md) → [认证授权](concepts/05-auth-system.md) → [配置管理](concepts/06-config-management.md) → [内容管理](concepts/07-contents-service.md) → [内核管理](concepts/08-kernel-management.md)

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
