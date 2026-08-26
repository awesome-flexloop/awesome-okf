# 核心概念索引

本目录包含 Enterprise Gateway 的 12 个核心概念文档，按学习路径排列。

## 入门篇

* [Enterprise Gateway 简介](00-introduction.md) — 什么是EG、解决什么问题、核心能力、支持平台、在Jupyter生态中的位置。
* [5分钟快速上手](01-getting-started.md) — 安装、本地启动、API验证、创建内核、Token认证的最小示例。
* [架构总览](02-architecture-overview.md) — 四层架构图、七大核心组件关系、创建内核完整请求流、三层扩展机制。

## 核心篇

* [应用入口与配置体系](03-app-and-config.md) — EnterpriseGatewayApp初始化流程、50+配置项分类详解（网络/认证/CORS/SSL/限制/环境变量/HA）、动态配置热更新。
* [ProcessProxy进程代理体系](04-process-proxy.md) — 核心抽象层、三层继承体系、9种ProcessProxy实现、SSH隧道机制、自定义扩展方法。
* [远程内核管理](05-kernel-management.md) — RemoteMappingKernelManager限额与并发控制、RemoteKernelManager生命周期、pending计数、HA内核恢复。
* [加密通信机制](06-response-manager.md) — ResponseManager RSA+AES混合加密、TCP回传通道、Response事件机制、KernelChannel枚举、launcher通信协议。
* [HTTP API体系](07-http-api-handlers.md) — 动态Mixin替换机制、三类Mixin详解、完整API端点列表、WebSocket代理。

## 进阶篇

* [会话管理与持久化](08-session-management.md) — SessionManager内存会话、FileKernelSessionManager文件持久化、WebhookKernelSessionManager外部存储、HA会话恢复。
* [内核启动流程详解](09-kernel-launch-flow.md) — 从POST /api/kernels到内核就绪的11阶段完整时序、launcher职责、SSH隧道建立。
* [部署模式与Kernel Launcher](10-deployment-modes.md) — Python/R/Scala Launcher职责、Docker/K8s/YARN部署模式、kernelspec配置、Docker镜像、Helm部署。
* [安全认证与高可用](11-security-and-ha.md) — Token认证、CORS配置、SSL/TLS双向认证、用户授权与模拟、负载均衡算法、standalone/replication HA模式。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-app-and-config
04-process-proxy
05-kernel-management
06-response-manager
07-http-api-handlers
08-session-management
09-kernel-launch-flow
10-deployment-modes
11-security-and-ha
```
