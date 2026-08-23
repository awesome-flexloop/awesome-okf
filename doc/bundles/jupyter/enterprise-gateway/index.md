---
okf_version: "0.2"
title: "enterprise-gateway"
description: "Jupyter Enterprise Gateway：Jupyter内核的远程管理网关，支持YARN/Kubernetes/Docker/SSH等多种部署平台，提供多租户隔离、加密通信、高可用和负载均衡能力。本知识束从源码出发，系统讲解EG的架构、ProcessProxy核心抽象、内核启动流程、配置体系和实战部署。"
---

# Enterprise Gateway

> Jupyter Kernel 远程管理网关。Enterprise Gateway 扩展了 Jupyter Server 的内核管理能力，通过 ProcessProxy 抽象层支持在 YARN 集群、Kubernetes、Docker、SSH 远程主机等多种平台上启动和管理内核进程，提供多租户资源隔离、RSA+AES加密通信、高可用和负载均衡等企业级特性。

## 快速导航

### [核心概念](concepts/index.md)

12篇概念文档，从入门到深入系统讲解 Enterprise Gateway：

- **入门**：[简介](concepts/00-introduction.md) → [5分钟快速上手](concepts/01-getting-started.md) → [架构总览](concepts/02-architecture-overview.md)
- **核心**：[应用入口与配置](concepts/03-app-and-config.md) · [ProcessProxy进程代理](concepts/04-process-proxy.md) · [远程内核管理](concepts/05-kernel-management.md) · [加密通信机制](concepts/06-response-manager.md) · [HTTP API体系](concepts/07-http-api-handlers.md)
- **进阶**：[会话管理与持久化](concepts/08-session-management.md) · [内核启动流程详解](concepts/09-kernel-launch-flow.md) · [部署模式与Kernel Launcher](concepts/10-deployment-modes.md) · [安全认证与高可用](concepts/11-security-and-ha.md)

### [示例代码](examples/index.md)

3个可独立运行的实战示例：

- [本地启动EG并执行代码](examples/01-start-eg-locally.md)
- [编写自定义ProcessProxy](examples/02-custom-process-proxy.md)
- [Kubernetes部署EG](examples/03-kubernetes-deployment.md)

### [源码信源](references/index.md)

7个关键模块的源码解析文档，为概念文档中的溯源引用提供目标。

## 核心特性

| 特性 | 说明 |
|------|------|
| 远程内核启动 | 支持本地/SSH/YARN/K8s/Docker/Docker Swarm/Conductor/CRD/Spark Operator共9种进程代理 |
| 多语言支持 | 内置Python(ipykernel)、R(IRkernel)、Scala(Apache Toree)三种内核启动器 |
| 加密通信 | RSA+AES混合加密的连接信息回传通道，防止ZMQ端口信息泄露 |
| 多租户隔离 | 按用户内核限额、禁止未授权用户、用户模拟（impersonation） |
| 高可用 | standalone（启动恢复）/replication（懒加载恢复）两种HA模式 |
| 负载均衡 | round-robin/least-connection算法，支持多远程主机轮询 |
| 动态配置 | 无需重启即可热更新关键配置参数 |
| Jupyter兼容 | 完全兼容Jupyter Server API，通过Mixin动态扩展Handler |
| 安全认证 | Token认证、CORS跨域、SSL/TLS双向认证、主机名验证 |
| 可扩展 | 自定义ProcessProxy对接任意计算平台，自定义Session持久化后端 |

## 版本信息

| 属性 | 值 |
|------|-----|
| 包名 | enterprise_gateway |
| 当前版本 | 3.4.0.dev0 |
| CLI命令 | `jupyter enterprisegateway` |
| 默认端口 | 8888 |
| 响应端口 | 8877 |
| 许可证 | Modified BSD License |
| 源码路径 | `external/libs/jupyter/enterprise_gateway/` |
