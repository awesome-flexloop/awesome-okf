---
type: Bundle
title: Jupyter Real-Time Collaboration (jupyter-collaboration)
description: Jupyter实时协作系统的完整教程，涵盖架构原理、CRDT同步、WebSocket协议、Awareness感知、文件持久化、Fork分叉和时间线等核心概念
version: 5.0.0
okf_version: "0.2"
source:
  type: source-code
  repository: https://github.com/jupyterlab/jupyter-collaboration
  local_path: external/libs/jupyter/jupyter-collaboration
  version_tag: v5.0.0
tags: [jupyter, rtc, crdt, yjs, collaboration, websocket, realtime]
category: jupyter/real-time-collaboration
generated: { by: source-code-to-okf-wiki/agent, at: "2026-04-21T00:00:00Z" }
status: stable
---

# Jupyter Real-Time Collaboration (jupyter-collaboration)

Jupyter Real-Time Collaboration（jupyter-collaboration）是Jupyter生态系统的官方实时协作扩展，基于Yjs CRDT实现多用户同时编辑Jupyter Notebooks和文件。

## 核心能力

- **多用户实时编辑**：多个用户同时编辑同一Notebook/文件，光标位置实时可见
- **CRDT自动合并**：基于Yjs的CRDT算法，无需手动解决合并冲突
- **持久化存储**：SQLite YStore保存CRDT更新历史，支持版本回溯
- **外带变更检测**：检测文件在协作外的修改并自动同步
- **文档分叉（Fork）**：创建实验分支，可选择性合并回主文档
- **时间线导航**：浏览历史版本、Undo/Redo、恢复误删内容
- **共享链接**：通过链接邀请访客协作者
- **全局Awareness**：跨文档的在线用户状态追踪

## 快速开始

```bash
pip install jupyter-collaboration
jupyter lab
```

打开两个浏览器窗口访问同一Notebook即可体验实时协作。

详细配置参见 [examples/01-setup-config.md](examples/01-setup-config.md)。

## 文档结构

### 📚 Concepts（核心概念）

从入门到深入的概念讲解：

| 编号 | 文档 | 内容 |
|---|---|---|
| 00 | [简介](concepts/00-introduction.md) | 功能概览、技术栈、核心特性 |
| 01 | [架构概览](concepts/01-architecture-overview.md) | 前后端架构、数据流、组件关系 |
| 02 | [YDocExtension配置](concepts/02-ydoc-extension.md) | 后端扩展配置项、路由、默认设置 |
| 03 | [文档房间](concepts/03-document-room.md) | DocumentRoom生命周期、保存机制、共享文档模型 |
| 04 | [YStore持久化](concepts/04-ystore-persistence.md) | CRDT更新存储、SQLite/TempFile实现 |
| 05 | [WebSocket协议](concepts/05-websocket-protocol.md) | 消息类型、连接流程、会话兼容、REST API |
| 06 | [Awareness协议](concepts/06-awareness-protocol.md) | 用户感知、双层Awareness、光标与状态 |
| 07 | [文件加载](concepts/07-file-loading.md) | FileLoader、轮询检测、外带变更、并发保护 |
| 08 | [Fork与时间线](concepts/08-fork-timeline.md) | 文档分叉、版本历史、Undo/Redo |
| 09 | [前端Provider](concepts/09-frontend-provider.md) | WebSocketProvider、RtcContentProvider、Token注入 |

### 💡 Examples（实战示例）

| 编号 | 文档 | 场景 |
|---|---|---|
| 01 | [安装配置](examples/01-setup-config.md) | 安装、配置项、部署场景、故障排查 |
| 02 | [自定义文档类型](examples/02-custom-document-type.md) | 为自定义文件类型添加协作支持 |
| 03 | [协作事件与扩展](examples/03-collaboration-events.md) | 事件监听、审计日志、通知扩展 |
| 04 | [Fork和时间线用法](examples/04-fork-timeline-usage.md) | REST API、客户端示例、恢复误删内容 |

### 📖 References（源码参考）

源码信源登记文档，记录源码分析的事实依据：

- [references/index.md](references/index.md) — 信源索引
- [references/app-source.md](references/app-source.md) — YDocExtension入口
- [references/handlers-source.md](references/handlers-source.md) — WebSocket/REST处理器
- [references/rooms-source.md](references/rooms-source.md) — 文档房间
- [references/stores-source.md](references/stores-source.md) — 持久化存储
- [references/loaders-source.md](references/loaders-source.md) — 文件加载
- [references/websocketserver-source.md](references/websocketserver-source.md) — WebSocket服务器
- [references/yprovider-source.md](references/yprovider-source.md) — 前端Provider
- [references/tokens-source.md](references/tokens-source.md) — 依赖注入Token

## 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| CRDT引擎 | [Yjs](https://github.com/yjs/yjs) / pycrdt | 前端/后端CRDT实现 |
| 通信协议 | WebSocket + y-websocket协议 | 实时同步 |
| 后端框架 | Jupyter Server Extension (Tornado) | HTTP/WebSocket服务 |
| 持久化 | SQLite / 临时文件 | CRDT更新存储 |
| 前端框架 | JupyterLab + Lumino | UI与插件系统 |
| 事件系统 | Jupyter Events | 事件发射与监听 |

## 相关资源

- [jupyter-collaboration GitHub](https://github.com/jupyterlab/jupyter-collaboration)
- [Yjs文档](https://docs.yjs.dev/)
- [pycrdt](https://github.com/jupyter-server/pycrdt)
- [Jupyter Server文档](https://jupyter-server.readthedocs.io/)

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
