---
okf_version: "0.2"
type: Log
title: "jupyter_server 知识包更新日志"
---

# jupyter_server 知识包更新日志

## 2026-08-22 — 初始版本

**版本**: v0.1.0
**源码版本**: jupyter_server v2.21.0.dev0
**源码路径**: `external/libs/jupyter/jupyter_server/`

### 新增内容

#### 源码信源（11 篇）
- `references/serverapp-source.md` — ServerApp 主应用类、ServerWebApplication、子命令应用
- `references/handlers-source.md` — AuthenticatedHandler、JupyterHandler、APIHandler 继承体系
- `references/auth-source.md` — IdentityProvider、PasswordIdentityProvider、Authorizer、User 模型
- `references/contents-source.md` — ContentsManager、FileContentsManager、Checkpoints
- `references/kernels-source.md` — MappingKernelManager、KernelWebsocketHandler、KernelSpec
- `references/extension-source.md` — ExtensionApp、ExtensionManager、扩展发现机制
- `references/gateway-source.md` — GatewayClient、GatewayKernelManager、远程内核代理
- `references/websocket-base-source.md` — WebSocketHandler 基类、ZMQ 频道桥接
- `references/services-source.md` — SessionManager、TerminalManager、ConfigManager、NbconvertHandler
- `references/config-source.md` — traitlets 配置、JSONConfigManager、递归合并
- `references/index.md` — 信源索引

#### 核心概念（16 篇）
- `concepts/00-introduction.md` — Jupyter Server 定位、版本、依赖
- `concepts/01-getting-started.md` — 安装、启动、命令行选项、基本配置
- `concepts/02-architecture-overview.md` — 五层架构（网络/Handler/服务/扩展/认证）
- `concepts/03-serverapp-lifecycle.md` — ServerApp 初始化→启动→请求处理→关闭
- `concepts/04-handler-hierarchy.md` — Handler 三层继承、装饰器、错误处理
- `concepts/05-auth-system.md` — 认证授权分离、Token/密码认证、自定义安全后端
- `concepts/06-config-management.md` — traitlets+JSON 双轨配置、优先级、核心配置项
- `concepts/07-contents-service.md` — 文件/Notebook CRUD、Checkpoints、大文件上传
- `concepts/08-kernel-management.md` — 多内核管理、生命周期、空闲回收、KernelSpec
- `concepts/09-sessions-service.md` — Session 映射、多前端共享、终端管理
- `concepts/10-extension-system.md` — ExtensionApp、entry points、Handler 注册、JupyterLab 范例
- `concepts/11-websocket-communication.md` — ZMQ↔WS 桥接、消息协议、心跳保活
- `concepts/12-gateway-client.md` — Gateway 代理、K8s/YARN 分布式内核
- `concepts/13-events-and-logging.md` — jupyter_events、logging、Prometheus 指标
- `concepts/14-async-programming.md` — anyio 抽象、async Handler、to_thread 桥接
- `concepts/15-deployment-and-security.md` — 生产部署、Nginx、HTTPS、Docker、systemd
- `concepts/index.md` — 概念索引

#### 示例代码（3 篇）
- `examples/01-basic-api-usage.md` — curl/Python requests REST API 完整示例
- `examples/02-simple-extension.md` — 从零创建 ExtensionApp 扩展
- `examples/03-websocket-kernel.md` — Python/JavaScript WebSocket 内核通信客户端
- `examples/index.md` — 示例索引

#### 导航文件
- `index.md` — 知识包首页（bundle 类型）

#### 组索引更新
- 更新 `../index.md`（jupyter 组索引），新增"服务层：后端核心服务"分类，收录 jupyter_server 和 jupyter-core

### 验证结果
- ✅ 核心类名 Grep 验证（18个核心类均在源码中确认存在）
- ✅ 所有 Markdown 文件 frontmatter 完整性检查（31个文件均通过）
- ✅ 内部 Markdown 链接验证（无断链）
- ✅ frontmatter sources 引用路径验证（所有信源路径有效）
