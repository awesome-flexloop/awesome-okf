---
type: Bundle
title: "Jupyverse"
description: "模块化 Jupyter 服务器的 OKF Wiki 教程。Jupyverse 基于 FPS（FastAPI Plugin System）构建，采用 API-Plugin 双层分离架构，支持可插拔认证、实时协作、内核管理和前端扩展。"
version: "0.14.15"
tags: [jupyverse, jupyter, fastapi, fps, plugin, notebook, kernel, collaboration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: Jupyverse README
  - id: pyproject
    resource: /references/pyproject-source.md
    title: Jupyverse pyproject.toml
source_repo: https://github.com/jupyter-server/jupyverse
python_requires: ">=3.10,<3.15"
license: "BSD-3-Clause"
---

# Jupyverse

**Jupyverse 是一个模块化的 Jupyter 服务器实现**，基于 [FPS](https://github.com/jupyter-server/fps)（FastAPI Plugin System）构建，采用创新的 API-Plugin 双层分离架构，提供可组合的 Jupyter 后端服务。

## 核心特性

- **🔌 模块化架构**：所有功能通过 FPS 插件提供，可按需组合、替换和扩展
- **🔐 可插拔认证**：支持 Token、Fief OAuth、JupyterHub、NoAuth 四种认证后端
- **👥 实时协作**：基于 Yjs/CRDT 的多用户实时编辑，支持光标感知和文档持久化
- **⚡ FastAPI 驱动**：基于 FastAPI + anycorn，原生异步高性能
- **🧩 Jupyter 兼容**：兼容 Jupyter Server API，支持 JupyterLab、RetroLab 前端
- **📦 轻量内核**：支持子进程内核和外部内核，可扩展 Web Worker 等内核类型

## 快速开始

```bash
# 安装（含 JupyterLab + 无认证模式）
pip install "jupyverse[jupyterlab,noauth]"

# 启动服务器
jupyverse

# 打开浏览器访问
# http://127.0.0.1:8000/lab
```

更详细的安装和配置指南见：[安装与启动](concepts/01-getting-started.md)

## 文档导航

### 📚 概念文档（Concepts）

系统讲解 Jupyverse 的架构、核心机制和各模块设计：

| 章节 | 文档 |
|------|------|
| 入门 | [简介](concepts/00-introduction.md) · [安装与启动](concepts/01-getting-started.md) |
| 架构 | [架构总览](concepts/02-architecture-overview.md) · [FPS模块系统](concepts/03-fps-module-system.md) · [App与Router](concepts/04-app-and-router.md) |
| 服务 | [认证授权](concepts/05-auth-system.md) · [文件服务](concepts/06-contents-service.md) · [内核管理](concepts/07-kernel-management.md) · [Lab前端](concepts/08-lab-frontend.md) · [协作编辑](concepts/09-collaboration-yjs.md) · [终端服务](concepts/10-terminals.md) |
| 扩展 | [CLI与配置](concepts/11-cli-and-configuration.md) · [插件开发](concepts/12-plugin-development.md) |

### 🚀 实践示例（Examples）

可直接操作的实践指南：

| 示例 | 场景 |
|------|------|
| [基本服务器启动](examples/01-basic-startup.md) | 快速启动 Jupyverse |
| [Token认证配置](examples/02-token-auth.md) | 安全认证部署 |
| [实时协作编辑](examples/03-collaboration.md) | 多用户实时协作 |
| [REST API使用](examples/04-rest-api-usage.md) | HTTP API 操作指南 |
| [自定义插件开发](examples/05-custom-plugin.md) | 开发 FPS 插件 |

### 📋 源码信源（References）

从 Jupyverse 源码中提取的原始事实文件，提供文档的可追溯来源：

- [信源索引](references/index.md) — 完整的信源文件列表

## 版本信息

| 项目 | 值 |
|------|-----|
| Jupyverse 版本 | 0.14.15 |
| Python 版本 | 3.10 - 3.14 |
| FPS 版本 | ≥0.6.3 |
| 核心依赖 | FastAPI, anycorn, structlog, rich-click |
| 源码仓库 | <https://github.com/jupyter-server/jupyverse> |

## 架构概览

```
┌─────────────────────────────────────────────────┐
│                  Jupyverse                       │
│  ┌─────────────┐  ┌──────────────────────────┐  │
│  │ JupyverseMod│  │      FPS Module System    │  │
│  │  (根模块)   │  │  prepare → start → stop   │  │
│  └──────┬──────┘  └──────────────────────────┘  │
│         │                                        │
│  ┌──────┴─────────────────────────────────────┐ │
│  │            API 抽象层 (api/)                │ │
│  │  App · Auth · Contents · Kernels · Kernel  │ │
│  │  Lab · Yjs · YRooms · Terminals · Config   │ │
│  └──────────────────┬─────────────────────────┘ │
│                     │ 依赖注入                    │
│  ┌──────────────────┴─────────────────────────┐ │
│  │          Plugin 实现层 (plugins/)           │ │
│  │  fps-auth · fps-noauth · fps-contents      │ │
│  │  fps-kernels · fps-lab · fps-yjs · ...     │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
         ↑ anycorn (ASGI Server)
         │ HTTP/WebSocket
    ┌────┴────┐
    │ Browser │
    └─────────┘
```

## 可选依赖功能组

安装时通过 extras 选择功能组合：

| extras | 安装内容 |
|--------|---------|
| `jupyverse[jupyterlab]` | JupyterLab 前端 |
| `jupyverse[jupyterlab,noauth]` | JupyterLab + 无认证（推荐新手） |
| `jupyverse[jupyterlab,auth]` | JupyterLab + Token 认证 |
| `jupyverse[jupyterlab,yjs,noauth]` | JupyterLab + 协作 + 无认证 |
| `jupyverse[retrolab]` | RetroLab 前端 |
| `jupyverse[nbclassic]` | Notebook Classic 前端 |
| `jupyverse[test]` | 测试依赖（pytest, httpx 等） |
