---
type: Concept
title: "架构总览"
description: "Jupyverse 采用 API-Plugin 双层分离架构，基于 FPS 模块系统实现依赖注入和生命周期管理，所有功能通过可插拔模块组合。"
tags: [architecture, fps, plugin, module, api-plugin-separation, dependency-injection]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-module-source.md
    title: JupyverseModule 主模块信源
  - id: app
    resource: /references/app-source.md
    title: App 类信源
  - id: pyproject
    resource: /references/pyproject-source.md
    title: pyproject.toml 信源
---

# 架构总览

Jupyverse 的架构核心是**API-Plugin 双层分离**和 **FPS 模块系统**，两者共同构成一个高度可组合的 Jupyter 后端。

## 双层分离架构

Jupyverse 的代码分为两个清晰的层次：

```
jupyverse/
├── api/                          # API 抽象层（jupyverse_* 包）
│   ├── api/                      #   核心 API：App、Config、Router、CLI
│   ├── auth/                     #   认证抽象：Auth ABC、User 模型
│   ├── contents/                 #   文件服务抽象：Contents ABC
│   ├── kernels/                  #   内核管理抽象：Kernels ABC、Session 模型
│   ├── kernel/                   #   内核抽象：Kernel ABC、KernelFactory
│   ├── lab/                      #   前端服务抽象：Lab ABC、PageConfig
│   ├── yjs/                      #   协作抽象：Yjs ABC
│   ├── yrooms/                   #   协作房间抽象：YRoom、YRooms
│   ├── terminals/                #   终端抽象：Terminals ABC
│   ├── frontend/                 #   前端配置：FrontendConfig
│   └── ...                       #   其他抽象包
├── plugins/                      # 插件实现层（fps_* 包）
│   ├── auth/                     #   Token 认证实现：fps-auth
│   ├── auth_fief/                #   Fief OAuth 实现：fps-auth-fief
│   ├── auth_jupyterhub/          #   JupyterHub 认证实现：fps-auth-jupyterhub
│   ├── noauth/                   #   无认证实现：fps-noauth
│   ├── contents/                 #   文件服务实现：fps-contents
│   ├── kernels/                  #   内核管理实现：fps-kernels
│   ├── kernel_subprocess/        #   子进程内核实现：fps-kernel-subprocess
│   ├── lab/                      #   JupyterLab 前端实现：fps-lab
│   ├── yjs/                      #   Yjs 协作实现：fps-yjs
│   ├── yrooms/                   #   Yjs 房间实现：fps-yrooms
│   ├── ystore_sqlite/            #   SQLite 文档存储：fps-ystore-sqlite
│   ├── terminals/                #   终端实现：fps-terminals
│   └── ...                       #   其他插件包
└── src/jupyverse/                # 主入口包
```

### API 层的职责

API 层（`api/`）定义**抽象契约**：
- ABC（抽象基类）声明服务接口（如 `Auth`、`Contents`、`Kernels`）
- Pydantic 模型定义数据结构（如 `User`、`Content`、`Session`、`Kernel`）
- Config 类定义配置项
- Router 基类在 `__init__` 中声明 REST API 端点（路由路径、权限要求）

API 层**不包含具体实现逻辑**，它只定义"长什么样"。

### Plugin 层的职责

Plugin 层（`plugins/`）提供**具体实现**：
- 继承 API 层的 ABC，实现所有抽象方法
- 作为 FPS Module，在 `prepare()` 中获取依赖、创建实例、注册服务
- 可以替换同层的其他插件（如用 fps-noauth 替换 fps-auth）

## FPS 模块系统

所有插件都基于 FPS（FastAPI Plugin System）框架，核心机制是：

1. **Module 基类**：所有插件继承 `fps.Module`
2. **生命周期方法**：`prepare()` → `start()` → `stop()`
3. **依赖注入**：`self.get(Type)` 获取依赖，`self.put(instance, Type)` 注册服务
4. **entry points 发现**：通过 `jupyverse.modules` entry point 自动发现插件

```
┌──────────────────────────────────────────────┐
│            JupyverseModule (根模块)           │
│  prepare(): 创建 App、配置 CORS、注册共享服务  │
│  start():  启动 HTTP 服务器                   │
│  stop():   发送关闭信号                       │
├──────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │ FrontendMod │ │ AuthModule  │ │ LabMod │ │
│  │  (注册配置)  │ │ (注册Auth)  │ │(注册Lab)│ │
│  └─────────────┘ └──────┬──────┘ └───┬────┘ │
│                         │             │      │
│  ┌─────────────┐ ┌──────┴──────┐      │      │
│  │ KernelsModule│ │ContentsModule│     │      │
│  │ (依赖Auth)   │ │ (依赖Auth)  │      │      │
│  └──────┬──────┘ └─────────────┘      │      │
│         │                             │      │
│  ┌──────┴──────┐                     │      │
│  │ YjsModule   │ (依赖 Auth+FileId)  │      │
│  └─────────────┘                     │      │
│  插件间通过 self.get() 声明式获取依赖   │      │
└──────────────────────────────────────────────┘
```

## 核心服务依赖关系

```
App (FastAPI 包装器)
 ├── FrontendConfig (基础 URL、协作模式开关)
 ├── Auth (认证抽象，由 fps-auth/fps-noauth 等实现)
 │    └── User (当前用户模型)
 ├── Contents (文件服务抽象，由 fps-contents 实现)
 │    └── FileWatcher (文件监视)
 ├── Kernels (内核管理抽象，由 fps-kernels 实现)
 │    ├── KernelFactory (内核工厂，由 fps-kernel-subprocess 注册)
 │    ├── Yjs (可选，协作支持)
 │    └── Lifespan (生命周期事件)
 ├── Lab (JupyterLab 前端服务，由 fps-lab 实现)
 │    └── PageConfig (页面配置钩子)
 ├── Terminals (终端服务，由 fps-terminals 实现)
 ├── Yjs (协作服务抽象，由 fps-yjs 实现)
 │    └── YRooms (协作房间管理器)
 │         └── YRoom (单个协作房间，管理 CRDT 文档)
 └── Lifespan (关闭信号)
```

## 请求处理流程

一个典型的 API 请求处理流程：

1. HTTP 请求到达 FastAPI/anycorn
2. App 中间件更新 `last_activity` 时间戳
3. Router 中注册的端点匹配请求路径
4. `Depends(auth.current_user(permissions={...}))` 执行认证和权限检查
5. 委托给具体实现类的抽象方法处理业务逻辑
6. 返回 Pydantic 模型序列化为 JSON 响应

## 关键设计原则

| 原则 | 体现 |
|------|------|
| **接口-实现分离** | api/ 定义 ABC，plugins/ 提供实现，可无缝替换 |
| **声明式依赖** | Module.prepare() 中通过 get()/put() 声明和获取依赖 |
| **路径冲突检测** | App 类自动检测重复路由注册，防止插件间路径冲突 |
| **权限即代码** | 每个端点在装饰器中声明所需权限 `{resource: [actions]}` |
| **配置即数据** | 所有配置通过 Pydantic Config 类声明，支持命令行和文件配置 |

## 相关概念

- [FPS 模块系统](03-fps-module-system.md) — 深入理解 Module 生命周期和依赖注入
- [App 与 Router 基础设施](04-app-and-router.md) — FastAPI 包装器和路由注册机制
- [认证授权系统](05-auth-system.md) — Auth 抽象和多后端实现
- [插件开发指南](12-plugin-development.md) — 开发自定义插件
