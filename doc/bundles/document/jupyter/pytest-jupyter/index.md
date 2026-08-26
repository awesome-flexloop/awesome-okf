---
okf_version: "0.2"
type: bundle
title: "pytest-jupyter"
description: "Jupyter 官方 pytest 测试插件集：通过分层插件架构提供环境隔离、内核管理、ServerApp生命周期、HTTP/WebSocket测试客户端等完整的Jupyter测试基础设施。本知识包从源码出发，系统讲解 pytest-jupyter v0.12.0 的架构、API和实战用法。"
---

# pytest-jupyter

> Jupyter 生态的 pytest 测试插件集：为 Jupyter 库和扩展提供开箱即用的测试基础设施。

`pytest-jupyter` 是 Jupyter 官方维护的 pytest 插件集合，通过 pytest fixtures 自动化管理 Jupyter 测试环境的完整生命周期——从临时目录隔离、asyncio 事件循环，到内核启动、Jupyter Server 实例启停和 HTTP/WebSocket 测试客户端。它采用分层插件设计（Core → Client/ Tornado → Server），让使用者按需引入测试能力。

## 快速导航

### 📘 核心概念（9 篇）

**入门**
- [简介](concepts/00-introduction.md) — pytest-jupyter 定位、三层插件架构、核心能力、项目信息
- [5分钟快速上手](concepts/01-getting-started.md) — 安装、conftest配置、第一个测试、常见问题

**架构**
- [架构总览](concepts/02-architecture-overview.md) — 模块结构、插件加载机制、fixture依赖DAG、异步测试架构、设计哲学
- [Fixture工厂模式](concepts/08-fixture-factories.md) — 工厂fixture设计模式、闭包机制、资源追踪、自定义工厂模板

**核心**
- [Core插件详解](concepts/03-core-plugin.md) — 环境隔离(jp_environ)、asyncio事件循环、异步测试pytest钩子、临时目录fixtures
- [Client插件详解](concepts/04-client-plugin.md) — 内核启动工厂(jp_start_kernel)、ZMQ上下文管理、资源自动清理
- [Server插件详解](concepts/05-server-plugin.md) — ServerApp生命周期、jp_fetch/jp_ws_fetch HTTP客户端、认证测试、自动清理
- [Tornado异步测试支持](concepts/06-tornasync-plugin.md) — 内嵌pytest-tornasync、IOLoop桥接、HTTP服务器/客户端、端口管理

**进阶**
- [Echo测试内核](concepts/07-echo-kernel.md) — EchoKernel实现原理、do_execute方法、stdin处理、扩展方式
- [概念文档索引](concepts/index.md) — 概念文档总目录

### 💻 示例代码（4 个）

- [Core插件基础测试](examples/01-basic-core-test.md) — 环境隔离验证、async测试函数、临时目录使用
- [内核测试](examples/02-kernel-testing.md) — echo/Python内核启动、消息通信、多内核、直接实例化
- [Server API测试](examples/03-server-api-test.md) — REST API、kernel生命周期、WebSocket通道、认证授权
- [自定义Server配置](examples/04-custom-server-config.md) — 覆盖fixtures、配置扩展、自定义base URL/根目录/token
- [示例文档索引](examples/index.md) — 示例总目录

### 📄 源码信源（7 个文件）

- [入口与版本](references/init-source.md) — __init__.py、_version.py、pyproject.toml
- [工具函数](references/utils-source.md) — mkdir工具函数
- [Core插件](references/jupyter-core-source.md) — 异步钩子、事件循环、环境隔离、临时目录fixtures
- [Echo内核](references/echo-kernel-source.md) — EchoKernel、EchoKernelApp、do_execute
- [Client插件](references/jupyter-client-source.md) — ZMQ上下文、内核启动工厂、资源清理
- [Tornado异步测试](references/pytest-tornasync-source.md) — IOLoop、HTTP服务器/客户端、AsyncHTTPServerClient
- [Server插件](references/jupyter-server-source.md) — ServerApp生命周期、HTTP/WebSocket工厂、认证授权
- [源码信源索引](references/index.md) — 信源文档总目录

## 版本信息

| 属性 | 值 |
|------|-----|
| 版本 | **v0.12.0.dev0**（开发版） |
| Python 版本要求 | ≥ 3.10 |
| 构建系统 | Hatchling ≥ 1.10.0 |
| 核心依赖 | `pytest>=7.0`, `jupyter_core>=5.7` |
| client extra依赖 | `jupyter_client>=7.4.0`, `nbformat>=5.3`, `ipykernel>=6.14` |
| server extra依赖 | `jupyter_server>=1.21`（含client全部依赖） |
| 许可证 | BSD-3-Clause |
| 源码仓库 | https://github.com/jupyter-server/pytest-jupyter |
| 源码路径 | `external/libs/jupyter/pytest-jupyter/` |
| 开发状态 | Beta |

## 插件层级关系

```
┌──────────────────────────────────────────────────────┐
│         jupyter_server 插件（最完整）                  │
│  ServerApp / HTTP+WebSocket / Auth / Notebook        │
│  ─ 包含: client + tornasync + core 全部fixtures       │
├──────────────────────────────────────────────────────┤
│    jupyter_client / pytest_tornasync 插件              │
│  Kernel管理 / Tornado HTTP层                          │
│  ─ 包含: core 全部fixtures                            │
├──────────────────────────────────────────────────────┤
│         jupyter_core 插件（基础层）                    │
│  环境隔离 / asyncio事件循环 / 异步测试钩子 / 临时目录    │
└──────────────────────────────────────────────────────┘
```

---

**推荐阅读顺序：** [简介](concepts/00-introduction.md) → [快速上手](concepts/01-getting-started.md) → [架构总览](concepts/02-architecture-overview.md) → [Core插件](concepts/03-core-plugin.md) → [Server插件](concepts/05-server-plugin.md) → [Fixture工厂模式](concepts/08-fixture-factories.md)

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
