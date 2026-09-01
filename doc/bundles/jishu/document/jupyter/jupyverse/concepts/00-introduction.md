---
type: Concept
title: "Jupyverse 简介"
description: "Jupyverse 是基于 FPS（FastAPI Plugin System）的模块化 Jupyter 服务器实现，采用 API-Plugin 双层分离架构，支持可插拔的认证、内核、协作等功能。"
tags: [introduction, overview, jupyter, server, fps, modular]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 信源
  - id: pyproject
    resource: /references/pyproject-source.md
    title: pyproject.toml 信源
---

# Jupyverse 简介

Jupyverse 是一组基于 [FPS](https://github.com/jupyter-server/fps)（FastAPI Plugin System）模块实现的 Jupyter 服务器。它采用**模块化插件架构**，将传统 Jupyter Server 的单体后端拆解为可独立替换的插件组件。

## 定位与特性

Jupyverse 是 Jupyter 生态中的**下一代后端服务器**，相比经典的 Jupyter Server / Notebook Server，它具有以下核心特性：

- **完全模块化**：认证、文件服务、内核管理、终端、协作编辑等均为独立插件，可按需组合
- **FastAPI 驱动**：基于现代 Python 异步 Web 框架 FastAPI，自动生成 OpenAPI 文档
- **多认证后端**：内置 Fief、JupyterHub、Token、NoAuth 等多种认证方式
- **实时协作**：基于 Yjs CRDT 的实时光文档协作，支持多用户同时编辑 Notebook
- **灵活部署**：支持单用户、多用户（JupyterHub 集成）、微服务模式
- **双事件循环**：支持 asyncio 和 trio 两种异步后端

## 版本与依赖

| 属性 | 值 |
|------|-----|
| 当前版本 | **0.14.15** |
| Python 版本 | ≥ 3.10（支持 3.10 ~ 3.14） |
| 构建系统 | uv_build |
| Web 框架 | FastAPI + anycorn (ASGI) |
| CLI 框架 | rich-click |
| 核心框架 | FPS ≥ 0.6.3 |
| 日志 | structlog（结构化日志） |
| 许可证 | BSD-3-Clause |

## 与 Jupyter Server 的关系

```
┌─────────────────────────────────────────────────┐
│          JupyterLab / Notebook 前端              │
└────────────────────┬────────────────────────────┘
                     │ HTTP / WebSocket
┌────────────────────▼────────────────────────────┐
│                  Jupyverse                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Contents │ │ Kernels  │ │ Yjs (Collab)     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │   Auth   │ │ Terminals│ │ Lab (Frontend)   │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│         每个功能都是独立的 FPS 插件               │
└────────────────────┬────────────────────────────┘
                     │ ZMQ / Subprocess
┌────────────────────▼────────────────────────────┐
│     Jupyter Kernel（IPython / IR / IJulia...）   │
└─────────────────────────────────────────────────┘
```

与传统 Jupyter Server 不同，Jupyverse 不将所有功能内置在一个进程中，而是通过 FPS 插件系统让每个功能成为独立的、可替换的模块。

## 可选功能组

通过 pip extras 可以按需安装功能组合：

| Extra | 功能 | 包含组件 |
|-------|------|---------|
| `jupyterlab` | JupyterLab 前端 | fps-jupyterlab |
| `notebook` | Notebook 7 前端 | fps-notebook |
| `auth` | 用户认证 | fps-auth + fps-login |
| `collaboration` | 实时协作 | fps-yjs + fps-yrooms + fps-ystore-sqlite + fps-file-id |
| `resource-usage` | 资源监控 | fps-resource-usage |
| `webdav` | WebDAV 文件访问 | fps-webdav |
| `jupyterlab-git` | Git 集成 | fps-jupyterlab-git |
| `jupyterlab-lsp` | 语言服务 | fps-jupyterlab-lsp |

## 相关概念

- [快速上手](01-getting-started.md) — 安装、启动 Jupyverse
- [架构总览](02-architecture-overview.md) — 深入理解双层分离架构
- [FPS 模块系统](03-fps-module-system.md) — FPS 依赖注入与生命周期
