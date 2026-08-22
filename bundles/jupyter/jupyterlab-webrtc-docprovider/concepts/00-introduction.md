---
type: Concept
title: 项目介绍
description: jupyterlab-webrtc-docprovider是基于WebRTC和Yjs的JupyterLab实时协作扩展，为Notebook和编辑器提供P2P文档同步能力
tags: [webrtc, collaboration, yjs, p2p, jupyterlab, jupyterlite, real-time]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README.md - Project documentation
  - id: pkg
    resource: /references/python-source.md
    title: Python packaging source
---

## 什么是 jupyterlab-webrtc-docprovider

**jupyterlab-webrtc-docprovider**（npm 包名 `@jupyterlite/webrtc-docprovider`，Python 包名 `jupyterlab-webrtc-docprovider`）是一个 JupyterLab 扩展，为 JupyterLab 和 JupyterLite 提供基于 WebRTC 的点对点（P2P）实时文档协作能力。

### 核心特性

- **P2P 实时协作**：基于 WebRTC 协议，文档数据直接在浏览器之间传输，不经过中心服务器
- **Yjs CRDT 引擎**：使用 Yjs（y-webrtc）作为冲突无关数据类型（CRDT）引擎，保证多用户并发编辑的数据一致性
- **信令服务器发现**：通过公共或私有信令服务器（Signaling Server）协助 peer 发现和连接建立
- **BroadcastChannel 本地发现**：同一浏览器内的标签页可通过 BroadcastChannel 直接发现彼此，无需信令服务器
- **多平台支持**：支持 JupyterLab 3.1+、RetroLab 0.3+、JupyterLite（beta）
- **零服务端依赖**：除信令服务器外，不需要部署额外的协作后端服务

### 与内置协作的区别

JupyterLab 内置的协作模式（`collaborative: true`）默认使用纯 WebSocket 方案，文档变更通过 Jupyter Server 中转。而 jupyterlab-webrtc-docprovider 使用 WebRTC 协议：

| 特性 | 内置 WebSocket 协作 | WebRTC DocProvider |
|------|---------------------|---------------------|
| 数据路径 | 客户端 ↔ 服务器 ↔ 客户端 | 客户端 ↔ 客户端（P2P） |
| 服务器要求 | 需要 Jupyter Server 中转 | 仅需要信令服务器协助建立连接 |
| 离线/Lite 支持 | 不支持（依赖 Server） | 支持 JupyterLite 静态部署 |
| 延迟 | 取决于服务器位置 | 直连，通常更低延迟 |
| 扩展性 | 服务器负载随用户数增长 | P2P 网状网络，天然分布式 |

### 技术栈

- **前端框架**：TypeScript + Lumino（JupyterLab 组件模型）
- **协作引擎**：Yjs v13 + y-webrtc ^10.2.0
- **加密库**：sjcl ^1.0.8（Stanford JavaScript Crypto Library，用于 SHA256 房间 ID 哈希）
- **WebRTC 补丁**：vendored SimplePeerExtended（修复大消息分块传输）
- **UI 框架**：React（通过 JupyterLab VDomRenderer）

### 版本信息

- 当前版本：0.1.2
- 许可证：BSD-3-Clause
- Python 要求：>= 3.7
- JupyterLab 要求：>= 3.1, <4

## 相关概念

- [安装与快速开始](/concepts/01-getting-started.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [WebRtcManager 配置管理](/concepts/03-webrtc-manager.md)
