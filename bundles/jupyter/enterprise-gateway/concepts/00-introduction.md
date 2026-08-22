---
okf_version: "0.2"
type: "concept"
title: "Enterprise Gateway 简介"
description: "什么是Enterprise Gateway、解决什么问题、核心能力、支持的部署平台、在Jupyter生态中的位置"
tags: [introduction, overview, jupyter, enterprise-gateway, remote-kernel]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/README.md"
    title: "README.md"
  - id: app-entry
    resource: "/references/app-entry-source.md"
    title: "主应用入口源码"
---

# Enterprise Gateway 简介

## 什么是 Enterprise Gateway

Jupyter Enterprise Gateway（简称EG）是一个 **Jupyter Kernel 远程管理网关**，它扩展了 Jupyter Server/Kernel Gateway 的能力，使 Jupyter Notebook 能够在 **分布式计算集群和容器编排平台** 上远程启动和管理内核进程 [F-001]。

简单来说，EG 解决的核心问题是：**当多用户通过 Notebook 服务器执行代码时，内核进程不应该只运行在 Notebook 服务器所在的机器上，而应该被调度到远端计算资源上执行。**

Jupyter 原生的内核管理机制（MappingKernelManager）只能在本地启动内核进程。EG 通过引入 ProcessProxy 抽象层，将内核启动代理到各种远程计算平台 [F-087]。

## 核心能力

1. **远程内核启动**：在内核规范（kernelspec）中声明进程代理类型，EG自动将内核进程调度到YARN集群、Kubernetes集群、Docker容器、SSH远程主机等平台 [F-088,F-089]
2. **多租户资源隔离**：支持按用户限制内核数量，禁止root等未授权用户启动内核，支持用户模拟（impersonation）[F-041,F-111]
3. **加密通信通道**：远程内核的ZMQ连接信息通过RSA+AES加密通道安全回传，防止端口信息泄露 [F-098,F-099]
4. **高可用部署**：支持standalone（启动时恢复）和replication（访问时懒加载恢复）两种HA模式，配合持久化会话管理 [F-044,F-027,F-028]
5. **负载均衡**：支持多主机间的round-robin和least-connection负载均衡算法 [F-078]
6. **动态配置热更新**：无需重启即可动态调整关键配置参数 [F-023]
7. **完整兼容Jupyter生态**：通过动态Mixin替换Handler而非重写，与Jupyter Server API完全兼容 [F-137]

## 支持的部署平台 [F-007]

| 平台 | ProcessProxy类 | 适用场景 |
|------|---------------|---------|
| 本地进程 | LocalProcessProxy | 开发调试、单机部署 |
| SSH分布式 | DistributedProcessProxy | 多服务器SSH轮询 |
| Apache Hadoop YARN | YarnClusterProcessProxy | 大数据Spark/Hadoop集群 |
| IBM Spectrum Conductor | ConductorClusterProcessProxy | IBM企业级计算平台 |
| Kubernetes | KubernetesProcessProxy | 容器化部署 |
| Kubernetes CRD | CustomResourceProcessProxy | 自定义资源类型 |
| Spark Operator | SparkOperatorProcessProxy | Spark on K8s Operator模式 |
| Docker Swarm | DockerSwarmProcessProxy | Docker Swarm集群 |
| Docker Engine | DockerProcessProxy | 单节点Docker容器 |

## 支持的内核语言 [F-006]

EG 内置支持三种内核语言的启动脚本（kernel-launchers）：
- **Python**（基于 ipykernel）
- **R**（基于 IRkernel）
- **Scala**（基于 Apache Toree）

每种语言在不同部署平台上都有对应的launcher脚本，负责在远端启动内核并回传连接信息。

## 在 Jupyter 生态中的位置

```
用户浏览器
    ↓ HTTP/WebSocket
JupyterHub / Notebook Server
    ↓ HTTP/WebSocket（/api/kernels）
Enterprise Gateway ←── 本项目（内核网关层）
    ↓ SSH/YARN API/K8s API/Docker API
远程计算资源（YARN/K8s/Docker/SSH主机）
    ↓ 启动内核进程
Python/R/Scala Kernel (ipykernel/IRkernel/Toree)
```

EG 位于 Notebook 服务器和计算资源之间，作为**内核网关**转发内核管理请求。它**不**管理多用户Notebook部署（该功能由JupyterHub承担）[F-009]。

EG 提供了与 Jupyter Kernel Gateway 的 jupyter-websocket 模式功能对等的能力，外加远程内核支持 [F-010]。

## 项目信息

| 属性 | 值 |
|------|-----|
| 包名 | enterprise_gateway |
| 版本 | 3.4.0.dev0 [F-001] |
| CLI命令 | `jupyter enterprisegateway` [F-004] |
| 许可证 | Modified BSD License [F-008] |
| 维护者 | Jupyter Development Team |
| 默认端口 | 8888 [F-032] |
| 源码路径 | `external/libs/jupyter/enterprise_gateway/` |

## 快速了解

建议按以下路径学习：
1. [5分钟快速上手](01-getting-started.md) — 安装、启动、创建内核
2. [架构总览](02-architecture-overview.md) — 理解核心组件和数据流
3. [ProcessProxy进程代理](04-process-proxy.md) — 理解最核心的抽象层
