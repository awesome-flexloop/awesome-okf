---
type: Concept
title: "Jupyter Server 简介"
description: "Jupyter Server 是 Jupyter Web 应用的后端核心，提供核心服务、REST API 和 WebSocket 端点，为 Notebook、JupyterLab、Voilà 等前端提供支持。"
tags: [introduction, overview, jupyter, backend, server]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: readme
    resource: ../../../../../../external/libs/jupyter/jupyter_server/README.md
    title: Jupyter Server README
  - id: pyproject
    resource: ../../../../../../external/libs/jupyter/jupyter_server/pyproject.toml
    title: pyproject.toml
  - id: init
    resource: /references/serverapp-source.md
    title: serverapp.py 源码信源
---

# Jupyter Server 简介

Jupyter Server 是 Jupyter 生态系统的**后端核心引擎**，为 Jupyter Notebook、JupyterLab、Voilà 等 Web 应用提供核心服务、REST API 和 WebSocket 通信端点。它是从经典的 Jupyter Notebook 服务器中分离出来的纯后端组件，专注于内核管理、文件服务、认证授权等基础设施能力。

## 定位与作用

Jupyter Server 在 Jupyter 技术栈中扮演**服务端中枢**角色：

- **内核管理**：启动、监控、关闭 Jupyter 内核（IPython 等），管理内核生命周期
- **文件服务**：提供 Notebook 和普通文件的 CRUD REST API
- **WebSocket 通信**：通过 ZMQ 桥接前端与内核之间的实时消息通道
- **认证授权**：可插拔的身份提供者（IdentityProvider）和授权器（Authorizer）
- **扩展机制**：支持服务器端扩展（Server Extension）和前端扩展加载
- **会话管理**：维护 Notebook 文件与内核实例之间的映射关系

## 版本信息

| 属性 | 值 |
|------|-----|
| 当前开发版本 | **2.21.0.dev0** |
| Python 版本要求 | ≥ 3.10 |
| 构建系统 | Hatchling ≥ 1.11 |
| Web 框架 | Tornado ≥ 6.2.0 |
| 配置框架 | traitlets ≥ 5.6.0 |
| 核心依赖 | jupyter_client, jupyter_core, nbformat, nbconvert, pyzmq, jinja2, anyio |
| 许可证 | BSD-3-Clause |
| CLI 命令 | `jupyter server`, `jupyter-server` |

## 核心依赖关系

```
jupyter_server
├── jupyter_core (≥4.12)     # 基础应用基类 JupyterApp、路径管理
├── jupyter_client (≥7.4.4)  # 内核管理 KernelManager、ZMQ 通信
├── nbformat (≥5.3.0)        # Notebook 文件格式
├── nbconvert (≥6.4.4)       # Notebook 格式转换
├── tornado (≥6.2.0)         # 异步 Web 框架
├── traitlets (≥5.6.0)       # 配置系统与类型化属性
├── pyzmq (≥24)              # ZeroMQ 消息通信
├── jinja2 (≥3.0.3)          # HTML 模板引擎
├── anyio (≥3.1.0)           # 异步 IO 抽象层
├── terminado (≥0.8.3)       # 终端 WebSocket 支持
├── argon2-cffi (≥21.1)      # 密码哈希
├── prometheus_client (≥0.9) # 监控指标
└── jupyter_events (≥0.11.0) # 结构化事件系统
```

## 与其他 Jupyter 项目的关系

```
┌─────────────────────────────────────────────┐
│  前端应用（JupyterLab / Notebook / Voilà）   │
└──────────────────┬──────────────────────────┘
                   │ HTTP / WebSocket
┌──────────────────▼──────────────────────────┐
│              Jupyter Server                 │  ◀── 本知识束
│  ┌─────────┐ ┌────────┐ ┌────────────────┐  │
│  │ Contents│ │ Kernels│ │ Extensions     │  │
│  │ Manager │ │ Manager│ │ (ExtensionApp) │  │
│  └─────────┘ └────────┘ └────────────────┘  │
│  ┌──────────────────────────────────────┐   │
│  │ Auth (IdentityProvider + Authorizer) │   │
│  └──────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │ ZMQ
┌──────────────────▼──────────────────────────┐
│  Jupyter Kernel（IPython / IR / IJulia...） │
└─────────────────────────────────────────────┘
```

Jupyter Server 本身**不包含任何前端 UI**，它只提供 API 和 WebSocket 端点。前端应用（如 JupyterLab）通过这些 API 与后端交互。

## 什么是 Server Extension？

Jupyter Server 的扩展机制允许开发者以插件形式添加：
- 新的 REST API 端点
- 自定义页面和模板
- 静态资源（JS/CSS）
- 新的认证方式
- 自定义内容管理器

JupyterLab、Jupyter Notebook v7+ 等都是以 Extension 形式运行在 Jupyter Server 之上的。

## 相关概念

- [快速上手](01-getting-started.md) — 安装、启动服务器、基本配置
- [架构总览](02-architecture-overview.md) — 深入理解 Jupyter Server 的分层架构
- [ServerApp 生命周期](03-serverapp-lifecycle.md) — 服务器从启动到关闭的完整流程
