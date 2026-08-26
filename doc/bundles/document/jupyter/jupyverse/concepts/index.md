---
type: Index
title: "概念文档索引"
description: "Jupyverse 概念文档索引，涵盖入门、架构、核心服务和插件开发的系统讲解。"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
---

# 概念文档索引

本目录包含 Jupyverse 的概念性文档，从入门到进阶系统讲解其架构和核心机制。

## 入门与安装

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [简介](00-introduction.md) | Jupyverse 是什么、定位、核心特性、版本依赖 |
| 01 | [安装与启动](01-getting-started.md) | 安装方式、服务器启动、CLI选项、测试验证 |

## 架构与基础设施

| 序号 | 文档 | 说明 |
|------|------|------|
| 02 | [架构总览](02-architecture-overview.md) | API-Plugin双层分离、FPS模块系统、核心服务依赖关系 |
| 03 | [FPS模块系统与依赖注入](03-fps-module-system.md) | Module生命周期(prepare/start/stop)、get/put依赖注入、entry points插件发现 |
| 04 | [App与Router基础设施](04-app-and-router.md) | FastAPI包装器、路径冲突检测、Router基类路由注册、Config/Singleton |

## 认证与核心服务

| 序号 | 文档 | 说明 |
|------|------|------|
| 05 | [认证授权系统](05-auth-system.md) | Auth ABC、权限模型{resource:[actions]}、四种认证后端、User模型 |
| 06 | [Contents文件服务](06-contents-service.md) | 文件CRUD REST API、Content/Checkpoint模型、ResourceLock并发控制 |
| 07 | [内核管理](07-kernel-management.md) | 内核生命周期、Session/KernelSpec、WebSocket channels、ZMQ通信、KernelFactory |
| 08 | [Lab前端服务](08-lab-frontend.md) | JupyterLab静态资源、PageConfig、LabHooks钩子、主题系统 |
| 09 | [协作编辑Yjs](09-collaboration-yjs.md) | CRDT/pycrdt实时协作、YRoom/YRooms、WebSocket同步、Awareness感知、文档持久化 |
| 10 | [终端服务](10-terminals.md) | 终端REST API、WebSocket协议、PTY子进程管理 |

## 配置与扩展

| 序号 | 文档 | 说明 |
|------|------|------|
| 11 | [CLI与配置](11-cli-and-configuration.md) | 命令行选项、--set语法、配置文件、环境变量、配置优先级 |
| 12 | [插件开发指南](12-plugin-development.md) | 插件目录结构、Module生命周期、路由注册、依赖注入、teardown回调 |

## 阅读建议

- **新用户**：按顺序阅读 00→01→02，然后按需查阅核心服务文档
- **插件开发者**：重点阅读 03→04→05→12，再参考 examples/05-custom-plugin.md
- **部署运维**：重点阅读 01→05→09→11
- **理解架构**：按顺序阅读 02→03→04→05→06→07→08→09

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-fps-module-system
04-app-and-router
05-auth-system
06-contents-service
07-kernel-management
08-lab-frontend
09-collaboration-yjs
10-terminals
11-cli-and-configuration
12-plugin-development
```
