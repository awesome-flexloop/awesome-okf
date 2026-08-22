---
type: Concept
title: FPS 简介
description: FPS（Fast Pluggable System）是Jupyter团队开发的模块化、可配置、可插拔、并发应用框架，版本0.6.7，基于anyio异步运行时。
tags: [introduction, overview, jupyter]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:52:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:52:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-module-py
    resource: /references/module-source.md
    title: src/fps/_module.py
  - id: fps-context-py
    resource: /references/context-source.md
    title: src/fps/_context.py
---

## 什么是 FPS

FPS（全称 Fast Pluggable System）是 Jupyter 开发团队维护的一个 Python 框架，用于创建**模块化、可配置、可插拔、并发**的应用程序。它的核心设计理念是让开发者通过组合独立的"模块"（Module）来构建应用，模块之间通过基于类型的异步发布-订阅机制共享服务，无需硬编码依赖关系。

FPS 是 [Jupyverse](https://github.com/jupyter-server/jupyverse) 项目的底层框架——Jupyverse 使用 FPS 将 Jupyter 服务器的各个组件（内核管理、文件服务、认证等）实现为可热替换的插件模块。

## 核心特性

FPS 提供以下核心能力：

1. **模块化架构**：应用由树状结构的 Module 组成，每个模块有自己的配置、生命周期和服务发布/获取接口
2. **三阶段生命周期**：每个模块经历 `prepare`（准备）→ `start`（启动）→ `stop`（停止）三个阶段，框架自动协调模块间的启动顺序
3. **类型驱动的服务共享**：模块通过 `put(value, SomeType)` 发布服务，其他模块通过 `await self.get(SomeType)` 异步获取——基于Python类型系统实现依赖注入，无需接口注册
4. **安全资源管理**：`SharedValue`/`Value` 实现类似Rust借用机制的异步资源共享，支持 `max_borrowers` 并发限制和 `teardown_callback` 生命周期清理
5. **声明式配置**：支持JSON配置文件和CLI参数（`--set`点分路径）两种方式配置任意嵌套模块的参数，配合Pydantic可获得自动类型校验
6. **插件发现**：通过Python entry-points（`fps.modules`组）实现零代码插件注册，第三方包安装后即可被FPS发现和加载
7. **并发运行时**：基于 [anyio](https://anyio.org) 异步框架，支持 asyncio 和 trio 两种事件循环后端
8. **内置Web支持**：提供 `FastAPIModule`（发布FastAPI应用）和 `ServerModule`（基于anycorn的ASGI服务器），可快速构建可插拔Web服务

## 技术栈

- **Python版本**：≥ 3.10（支持3.10-3.14）
- **异步运行时**：anyio ≥ 4.14.0（兼容asyncio和trio）
- **日志**：structlog（结构化日志）
- **可选Web框架**：FastAPI ≥ 0.137.2
- **可选ASGI服务器**：anycorn ≥ 0.19.0
- **可选CLI框架**：click ≥ 8.1.8
- **构建系统**：hatchling

## 框架定位

FPS 不是一个Web框架（尽管它内置了Web支持），而是一个更通用的**应用组装框架**。它解决的核心问题是：如何让多个独立开发的模块（可能来自不同的Python包）在运行时动态组合成一个应用，模块间可以安全地共享资源、协调启动/关闭顺序，而不需要在编码时硬编码依赖关系。

## 相关概念

- [安装与快速开始](/concepts/01-getting-started.md)
- [模块系统](/concepts/02-module-system.md)
- [上下文与共享值](/concepts/03-context-sharing.md)
- [生命周期阶段](/concepts/04-lifecycle-phases.md)
