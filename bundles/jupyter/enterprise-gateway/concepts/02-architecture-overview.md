---
okf_version: "0.2"
type: "concept"
title: "架构总览"
description: "Enterprise Gateway整体架构、核心组件关系图、请求处理流程、三层扩展机制"
tags: [architecture, components, data-flow, overview]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: app-entry
    resource: "/references/app-entry-source.md"
    title: "主应用入口源码"
  - id: process-proxy
    resource: "/references/process-proxy-source.md"
    title: "ProcessProxy源码"
  - id: kernel-manager
    resource: "/references/kernel-manager-source.md"
    title: "内核管理器源码"
  - id: response-manager
    resource: "/references/response-manager-source.md"
    title: "ResponseManager源码"
  - id: handlers
    resource: "/references/handlers-source.md"
    title: "HTTP Handler源码"
---

# 架构总览

## 整体架构图

Enterprise Gateway 的架构可以分为四层：

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP API 层 (Tornado)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ Kernel   │ │KernelSpec│ │ Session  │ │ Swagger/API    │  │
│  │ Handlers │ │ Handlers │ │ Handlers │ │ Version/404    │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───────┬────────┘  │
│       │  Token/CORS/JSONErrors 动态混入 ←───────┘           │
├───────┼─────────────────────────────────────────────────────┤
│       ▼              内核管理层                               │
│  ┌────────────────────────────────────────────┐              │
│  │     RemoteMappingKernelManager             │              │
│  │  ┌──────────────────────────────────────┐  │              │
│  │  │     RemoteKernelManager (per kernel) │  │              │
│  │  │  ┌────────────────────────────────┐  │  │              │
│  │  │  │     ProcessProxy (per kernel)  │  │  │              │
│  │  │  │  Local/SSH/YARN/K8s/Docker...  │  │  │              │
│  │  │  └────────────────────────────────┘  │  │              │
│  │  └──────────────────────────────────────┘  │              │
│  └────────────────────────────────────────────┘              │
├─────────────────────────────────────────────────────────────┤
│              会话与配置层                                     │
│  ┌─────────────┐  ┌──────────────────────┐  ┌────────────┐  │
│  │SessionManager│  │KernelSessionManager  │  │KernelSpec  │  │
│  │(内存)        │  │(File/Webhook持久化)  │  │Cache(监控) │  │
│  └─────────────┘  └──────────────────────┘  └────────────┘  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │     EnterpriseGatewayConfigMixin (50+配置项)         │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│              通信层                                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │     ResponseManager (RSA+AES加密连接信息回传)        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. EnterpriseGatewayApp 主应用 [F-011]

基于 Tornado 的 HTTP 服务器应用，是整个EG的入口。负责：
- 初始化所有核心组件（KernelManager、SessionManager、KernelSpecCache等）[F-015]
- 注册HTTP路由（五类handler拼接）[F-016]
- 启动HTTPServer并监听端口 [F-018]
- 管理生命周期（启动、信号处理、优雅关闭）[F-019,F-020]
- 动态配置热更新 [F-023]

### 2. RemoteMappingKernelManager 内核管理器 [F-105]

管理所有内核实例的映射表，扩展了Jupyter Server的 `AsyncMappingKernelManager`：
- 内核启动前检查资源限额（全局/每用户）[F-111]
- 为每个内核创建 `RemoteKernelManager` 实例
- 内核创建/关闭时维护持久化会话 [F-110,F-117]
- HA模式下支持内核恢复（start_kernel_from_session）[F-114]

### 3. RemoteKernelManager 单内核管理 [F-118]

管理单个内核的完整生命周期：
- 通过ProcessProxy启动/停止/监控内核进程 [F-121,F-124]
- 格式化kernel启动命令（替换模板占位符）[F-123]
- 管理环境变量传递（client_envs/inherited_envs）[F-122]
- 处理SIGINT等内核信号 [F-127]

### 4. ProcessProxy 进程代理 [F-061~F-090]

**EG最核心的抽象层**，定义了"如何启动和管理内核进程"的统一接口：
- `launch_process()`：启动进程（抽象方法，各平台实现）
- `poll()`/`wait()`：检查进程状态
- `send_signal()`/`kill()`/`terminate()`：向进程发送信号
- `confirm_remote_startup()`：等待远程启动完成

通过三层继承体系实现9种进程代理，支持本地/SSH/YARN/K8s/Docker等部署方式。

### 5. ResponseManager 加密通信 [F-091~F-102]

单例模式，管理远程内核连接信息的加密回传：
- 启动TCP监听端口（默认8877）
- 生成RSA密钥对，公钥随启动命令传给launcher
- launcher用RSA+AES加密ZMQ连接信息回传
- EG解密后通过事件机制通知等待的ProcessProxy

### 6. SessionManager / KernelSessionManager 会话管理 [F-147~F-157]

- `SessionManager`：内存中的session记录
- `KernelSessionManager`：持久化会话抽象，支持文件存储（FileKernelSessionManager）和Webhook（WebhookKernelSessionManager）两种后端
- HA模式下通过持久化会话恢复内核状态

### 7. KernelSpecCache 内核规范缓存 [F-160,F-161]

- 缓存所有kernelspec到内存
- 通过watchdog文件系统监控自动刷新缓存
- 无需重启即可加载新内核

## 请求处理流程：创建内核

客户端 POST `/api/kernels` 请求的完整处理链路：

```
1. MainKernelHandler.post()
   ├─ TokenAuthorizationMixin.prepare()  ← Token认证
   ├─ CORSMixin.set_default_headers()    ← CORS头设置
   └─ 解析请求体（kernelspec name, env）

2. RemoteMappingKernelManager.start_kernel()
   ├─ get_kernel_username()              ← 获取当前用户
   ├─ _enforce_kernel_limits()           ← 检查内核数限额
   ├─ pending_requests.increment()       ← pending计数
   ├─ super().start_kernel()             ← 创建RemoteKernelManager
   │   └─ RemoteKernelManager.start_kernel()
   │       ├─ new_kernel_id()            ← 生成/获取kernel_id
   │       ├─ _get_process_proxy()       ← 创建ProcessProxy实例
   │       ├─ _capture_user_overrides()  ← 捕获环境变量
   │       ├─ _enforce_authorization()   ← 用户授权检查
   │       └─ super().start_kernel()     ← AsyncIOLoopKernelManager
   │           ├─ format_kernel_cmd()    ← 替换命令模板占位符
   │           └─ _launch_kernel()
   │               └─ process_proxy.launch_process()
   │                   ├─ [Local]  本地launch_kernel()
   │                   └─ [Remote] SSH/YARN/K8s/Docker API启动
   │                       └─ launcher脚本启动kernel进程
   │                           └─ 加密回传连接信息
   │                               └─ ResponseManager解密
   ├─ pending_requests.decrement()
   └─ kernel_session_manager.create_session() ← 持久化会话

3. 返回kernel模型（id, name, WebSocket URL）
```

## 三层扩展机制 [I-01洞察5]

EG提供三个粒度的扩展点：

| 扩展粒度 | 配置方式 | 替换什么 |
|---------|---------|---------|
| 系统级 | `kernel_manager_class` | 整个内核管理实现 |
| 会话级 | `kernel_session_manager_class` | 会话持久化后端 |
| 内核级 | kernelspec的`metadata.process_proxy.class_name` | 单个内核类型的进程代理 |

最常用的扩展点是第三层——在kernelspec中声明process_proxy类型，即可让不同内核运行在不同平台上。

## 关键设计决策

1. **动态Mixin替换**：不重写Jupyter Server的Handler，而是通过动态创建子类混入认证/CORS/错误处理逻辑，保持API完全兼容 [F-137]
2. **RSA+AES混合加密**：非对称加密传递对称密钥，对称加密加密数据，兼顾安全和性能 [F-098]
3. **SSH隧道**：远程ZMQ端口通过SSH隧道映射到本地，使WebSocket代理无需感知远程网络拓扑 [F-076]
4. **双环境变量前缀**：同时支持EG_*和KG_*前缀，保持与Kernel Gateway的向后兼容 [F-047]
