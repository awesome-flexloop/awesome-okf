---
type: Concept
title: 架构总览
description: jupyterlite-lsp 的整体架构设计、Mock-Socket 桥接原理、数据流与组件关系
tags: [architecture, mock-socket, bridge, data-flow]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: core
    resource: /references/core-plugin-source.md
    title: 核心LSP包源码引用
  - id: hacks
    resource: /references/hacks-source.md
    title: Monkey-patch 源码引用
  - id: yaml
    resource: /references/yaml-plugin-source.md
    title: YAML语言服务器包源码引用
---

## 架构全景

jupyterlite-lsp 的核心设计思想是**浏览器内全栈 LSP**——利用浏览器 API（Web Worker、Service Worker）和 mock-socket 库，在没有后端进程的情况下完整模拟 jupyter-lsp 的通信层。

```
┌─────────────────────────────────────────────────────────┐
│                    浏览器（JupyterLite）                   │
│                                                         │
│  ┌──────────────┐    ┌───────────────────────────────┐  │
│  │ jupyterlab-  │    │  jupyterlite-lsp 扩展          │  │
│  │ lsp 前端     │    │                               │  │
│  │              │    │  ┌─────────┐  ┌────────────┐  │  │
│  │ REST /lsp/*  │───▶│  │ routes  │  │  Language  │  │  │
│  │ WS /lsp/ws/*│    │  │ Plugin  │  │  Servers   │  │  │
│  └──────┬───────┘    │  └─────────┘  └─────┬──────┘  │  │
│         │            │                     │         │  │
│         │ Monkey-    │  ┌─────────┐  ┌─────▼──────┐  │  │
│         │ patched    │  │  hacks  │  │  Session   │  │  │
│         │ WebSocket  │  │ Plugin  │  │  (mock-    │  │  │
│         │            │  └─────────┘  │   socket)  │  │  │
│         │            │               └─────┬──────┘  │  │
│         │            │                     │         │  │
│         │            │              ┌──────▼──────┐  │  │
│         │            │              │ IJSONRPC-   │  │  │
│         │            │              │ Language-   │  │  │
│         │            │              │ Server      │  │  │
│         │            │              └──────┬──────┘  │  │
│         │            │                     │         │  │
│         │            │         ┌───────────┼───────┐ │  │
│         │            │         │           │       │ │  │
│         │            │    ┌────▼───┐  ┌────▼───┐   │ │  │
│         │            │    │ YAML   │  │ (未来  │   │ │  │
│         │            │    │ Server │  │ 添加的 │   │ │  │
│         │            │    │(Worker)│  │ 服务器)│   │ │  │
│         │            │    └────────┘  └────────┘   │ │  │
│         │            └───────────────────────────────┘ │  │
│         │                                              │  │
│    ┌────▼────┐  mock-socket WebSocketServer             │  │
│    │ window. │  (浏览器内虚拟 WS 服务端)                  │  │
│    │MockWebSocket│                                       │  │
│    └─────────┘                                          │  │
└─────────────────────────────────────────────────────────┘
```

## 三大桥接层

整个架构由三层桥接构成：

### 1. REST 桥接（Service Worker 层）

jupyterlab-lsp 前端通过 `ServerConnection.makeSettings()` 创建的 fetch 客户端发送 REST 请求（如获取 `/lsp/status`）。hacksPlugin 中的 `hackServerConnection()` 将 fetch 替换为 `app.fetch.bind(app)`，即 JupyterLiteServer 的 Service Worker fetch 处理函数。routesPlugin 注册 `/lsp/status` GET 路由，返回 LanguageServers.status() 的 JSON 结果。

### 2. WebSocket 桥接（mock-socket 层）

这是最关键的桥接层。传统架构中，前端通过 `new WebSocket('ws://.../lsp/ws/<id>')` 连接后端的 jupyter-lsp 进程。在 jupyterlite-lsp 中：

- 构建时，dodo.py 的 task_hack 将 jupyterlab-lsp 打包产物中的 `new WebSocket(...)` 字符串替换为 `new window.MockWebSocket(...)`
- 运行时，每个 Session 在 `initServer()` 中创建一个 mock-socket 的 `WebSocketServer`，监听 URL `${WS_BASE_URL}lsp/ws/${id}`
- 当前端创建 `new window.MockWebSocket(url)` 时，连接直接在浏览器内存中路由到对应的 WebSocketServer
- 没有任何真实的网络请求

WS_BASE_URL 由 `PageConfig.getBaseUrl().replace(/^http/, 'ws')` 生成。

### 3. 语言服务器桥接（Web Worker 层）

语言服务器运行在 Web Worker 中（避免阻塞主线程）。JSONLanguageServer 类实现了 IJSONRPCLanguageServer 接口，将 Worker 的消息 API 适配为 AsyncGenerator 模式：

- **写方向**：`write(msg)` → `worker.postMessage(msg)` → Worker 内的语言服务器
- **读方向**：Worker `onmessage` → `wait-queue` 入队 → `read()` AsyncGenerator `yield` → Session 通过 `socket.send()` 发给前端

## 数据流（一条 LSP 消息的旅程）

以"悬停提示"（textDocument/hover）为例：

1. 用户在编辑器中悬停，jupyterlab-lsp 前端构造 LSP 请求消息
2. 前端通过 MockWebSocket 发送消息
3. mock-socket 将消息路由到 Session 的 `onMessage` 回调
4. Session 调用 `langServer.write(msg)` → `worker.postMessage(msg)`
5. yaml-language-server（Worker 中）处理请求，生成响应
6. Worker 发送响应消息到主线程
7. `onWorkerMessage` 将消息放入 WaitQueue
8. `read()` AsyncGenerator yield 消息
9. Session 的 read 循环中 `socket.send(msg)` 通过 mock-socket 发回前端
10. jupyterlab-lsp 前端接收响应，显示悬停提示

整个过程中，消息从主线程→Worker→主线程，没有跨网络传输。

## 三插件启动顺序

三个 JupyterLiteServerPlugin 都设置了 `autoStart: true`，启动顺序为：

1. **hacksPlugin**（`${NS}:hacks`）：最先执行 Monkey-patch，为后续插件提供环境基础
2. **serverPlugin**（`${NS}:plugin`）：创建 LanguageServers 实例，提供 ILanguageServers Token
3. **routesPlugin**（`${NS}:routes`）：依赖 ILanguageServers，注册 REST 路由

语言服务器包（如 lsp-yaml）的插件依赖 ILanguageServers Token，在核心三插件之后启动，调用 `addLanguageServer()` 注册具体语言服务器。

## 扩展点架构

添加新语言服务器只需：

1. 创建一个新的 npm 包（如 `@jupyterlite/lsp-python`）
2. 定义一个 JupyterLiteServerPlugin，依赖 ILanguageServers
3. 在 activate 中调用 `lsp.addLanguageServer(id, { spec, createNewServer })`
4. createNewServer 返回实现 IJSONRPCLanguageServer 接口的对象（通常包装一个运行语言服务器的 Web Worker）

核心包不需要修改。这是典型的微内核+插件架构。

## 相关概念

- [项目介绍](00-introduction.md)
- [三插件体系](03-plugin-system.md)
- [IJSONRPCLanguageServer 接口](04-language-server-interface.md)
- [Mock-Socket 桥接机制](05-mock-socket-bridge.md)
- [添加自定义语言服务器示例](../examples/add-custom-language-server.md)
