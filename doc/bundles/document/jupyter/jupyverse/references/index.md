---
type: Index
title: "信源索引"
description: "Jupyverse 源码信源文件索引，记录从源码中提取的原始事实。"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
---

# 信源索引

本目录包含从 Jupyverse 源码中提取的原始信源文件，作为 OKF Wiki 文档的可追溯来源。

## 核心入口与配置

| 文件 | 来源 | 说明 |
|------|------|------|
| [readme-source.md](readme-source.md) | `README.md` | 项目概览、安装、基本用法 |
| [pyproject-source.md](pyproject-source.md) | `pyproject.toml` | 版本(0.14.15)、依赖、可选特性组、entry points |
| [cli-source.md](cli-source.md) | `api/api/src/jupyverse_api/cli.py` | CLI 参数、插件发现、配置收集 |
| [app-source.md](app-source.md) | `api/api/src/jupyverse_api/app/__init__.py` | App 类(FastAPI包装)、Router基类、路径冲突检测 |
| [main-module-source.md](main-module-source.md) | `src/jupyverse/__init__.py` | JupyverseModule 生命周期、CORS、服务器启动 |
| [frontend-source.md](frontend-source.md) | `plugins/frontend/src/fps_frontend/main.py` | FrontendConfig、前端基础配置 |

## API 抽象层

| 文件 | 来源 | 说明 |
|------|------|------|
| [auth-api-source.md](auth-api-source.md) | `api/auth/src/jupyverse_auth/__init__.py` | Auth ABC、User 模型、权限模型 |
| [contents-api-source.md](contents-api-source.md) | `api/contents/src/jupyverse_contents/__init__.py` | Contents ABC、Content/Checkpoint 模型、REST端点、ResourceLock |
| [kernels-api-source.md](kernels-api-source.md) | `api/kernels/src/jupyverse_kernels/__init__.py` | Kernels ABC、Kernel/Session/KernelSpec 模型、REST端点、WebSocket通道 |
| [kernel-api-source.md](kernel-api-source.md) | `api/kernel/src/jupyverse_kernel/__init__.py` | Kernel ABC、KernelFactory、ZMQ通道内存流 |
| [lab-api-source.md](lab-api-source.md) | `api/lab/src/jupyverse_lab/__init__.py` | Lab ABC、LabHooks、PageConfig、静态资源挂载 |
| [yjs-api-source.md](yjs-api-source.md) | `api/yjs/src/jupyverse_yjs/__init__.py` | Yjs ABC、协作WebSocket端点、会话管理 |
| [yrooms-api-source.md](yrooms-api-source.md) | `api/yrooms/src/jupyverse_yrooms/__init__.py` | YRooms/YRoom 抽象、文档持久化钩子 |
| [terminals-api-source.md](terminals-api-source.md) | `api/terminals/src/jupyverse_terminals/__init__.py` | Terminals ABC、终端模型、WebSocket协议 |

## 插件实现层

| 文件 | 来源 | 说明 |
|------|------|------|
| [noauth-source.md](noauth-source.md) | `plugins/noauth/src/fps_noauth/main.py` | NoAuth 实现（最简单的认证后端） |
| [fps-kernels-source.md](fps-kernels-source.md) | `plugins/kernels/src/fps_kernels/main.py` | KernelsModule 实现、内核生命周期管理、会话管理 |

```{toctree}
:hidden:
:maxdepth: 7

app-source
auth-api-source
cli-source
contents-api-source
fps-kernels-source
frontend-source
kernel-api-source
kernels-api-source
lab-api-source
main-module-source
noauth-source
pyproject-source
readme-source
terminals-api-source
yjs-api-source
yrooms-api-source
```
