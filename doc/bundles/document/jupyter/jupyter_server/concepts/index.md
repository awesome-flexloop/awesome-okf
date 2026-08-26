---
type: Index
title: "概念文档索引"
description: "Jupyter Server 核心概念文档索引，从入门到进阶共 16 篇"
tags: [concepts, index, documentation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:10:00Z" }
status: stable
stale_after: 2027-02-22
sources: []
---

# 概念文档索引

Jupyter Server 核心概念文档共 16 篇，按学习路径分为四个阶段。

## 🟢 入门阶段（00-01）

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [简介](00-introduction.md) | Jupyter Server 在生态中的定位、版本信息、依赖关系、与其他项目的关系 |
| 01 | [快速上手](01-getting-started.md) | 安装、启动、命令行选项、基本配置、访问服务器、测试 API |

## 🟡 架构与基础（02-06）

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 02 | [架构总览](02-architecture-overview.md) | 五层架构：网络层/Handler/服务层/扩展层/认证层，ZMQ 内核通信 |
| 03 | [ServerApp 生命周期](03-serverapp-lifecycle.md) | ServerApp 初始化→配置加载→扩展加载→HTTP 服务器启动→请求处理→关闭 |
| 04 | [Handler 继承体系](04-handler-hierarchy.md) — AuthenticatedHandler→JupyterHandler→APIHandler、装饰器、错误处理 |
| 05 | [认证授权系统](05-auth-system.md) | IdentityProvider/Authorizer 分离、User 模型、Token/密码认证、CORS、自定义安全后端 |
| 06 | [配置管理](06-config-management.md) | traitlets+JSON 双轨配置、配置文件位置与优先级、递归合并、命令行配置 |

## 🔵 核心服务（07-12）

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 07 | [内容管理服务](07-contents-service.md) | ContentsManager、Checkpoints、文件/目录/Notebook CRUD、大文件上传、Notebook 信任 |
| 08 | [内核管理](08-kernel-management.md) | MappingKernelManager、内核生命周期、空闲回收、KernelSpec、ZMQ 五通道 |
| 09 | [会话管理](09-sessions-service.md) | Session 关联文件与内核、多前端共享内核、终端管理、NbConvert 服务 |
| 10 | [扩展系统](10-extension-system.md) | ExtensionApp、ExtensionManager、entry points 发现、Handler 注册、静态资源、JupyterLab 范例 |
| 11 | [WebSocket 通信](11-websocket-communication.md) | WS 基类、ZMQ↔WS 桥接、消息协议、子协议、心跳保活、Nginx 代理配置 |
| 12 | [网关客户端](12-gateway-client.md) | GatewayClient、远程内核代理、K8s/YARN/Docker 分布式执行、WebSocket 代理转发 |

## 🟣 进阶功能（13-15）

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 13 | [事件系统与日志](13-events-and-logging.md) | jupyter_events 结构化事件、Schema 注册、Python logging、Prometheus 指标、审计日志 |
| 14 | [异步编程模型](14-async-programming.md) | anyio 抽象、async Handler、同步/异步双版本 Manager、to_thread 桥接、异步陷阱 |
| 15 | [部署与安全](15-deployment-and-security.md) | 生产部署、Nginx 反向代理、HTTPS、Docker、systemd、安全加固、JupyterHub 多用户 |

## 推荐阅读路径

```
入门阶段 ──→ 架构与基础 ──→ 核心服务 ──→ 进阶功能
  00-01         02-06          07-12        13-15
    │             │              │            │
    ▼             ▼              ▼            ▼
  安装启动    理解架构原理    掌握各服务    生产实战
```

快速入门：00 → 01 → 02
理解原理：03 → 04 → 05 → 06
核心开发：07 → 08 → 09 → 10
高级主题：11 → 12 → 13 → 14 → 15

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-serverapp-lifecycle
04-handler-hierarchy
05-auth-system
06-config-management
07-contents-service
08-kernel-management
09-sessions-service
10-extension-system
11-websocket-communication
12-gateway-client
13-events-and-logging
14-async-programming
15-deployment-and-security
```
