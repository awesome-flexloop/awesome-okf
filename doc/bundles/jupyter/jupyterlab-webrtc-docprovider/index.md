---
type: Bundle
title: jupyterlab-webrtc-docprovider
description: JupyterLab P2P实时协作扩展OKF Wiki，基于WebRTC和Yjs CRDT实现无需中心服务器的文档共享
tags: [jupyterlab, webrtc, yjs, crdt, p2p, collaboration, extension, real-time]
bundle:
  id: jupyterlab-webrtc-docprovider
  category: jupyter
  version: "0.2.0"
  source_repo: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider
  license: BSD-3-Clause
  verified_api: true
  status: stable
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:07:00Z", method: "R→I→E→V→C" }
status: stable
stale_after: 2027-08-22
---

# jupyterlab-webrtc-docprovider OKF Wiki

> **Collaborate on Jupyter documents using WebRTC and Yjs** — JupyterLab/JupyterLite 扩展，实现基于 WebRTC P2P 的实时文档协作，无需中心协作服务器。

## 快速导航

| 目录 | 内容 | 文件数 |
|------|------|--------|
| 📚 [概念文档](concepts/index.md) | 架构原理、核心机制、API详解 | 11 |
| 📖 [源码信源](references/index.md) | 源码事实引用、API溯源 | 9 |
| 💡 [使用示例](examples/index.md) | 从入门到部署的教程 | 3 |

## 项目概览

### 是什么

jupyterlab-webrtc-docprovider 是一个 JupyterLab 扩展（也支持 JupyterLite/RetroLab），使用 [y-webrtc](https://github.com/yjs/y-webrtc) 通过 WebRTC DataChannel 在浏览器之间直接同步 Yjs CRDT 文档，实现实时多人协作编辑 Notebook 和文件。

### 核心特性

- 🔀 **P2P 直连**：文档数据通过 WebRTC 直接在浏览器间传输，无需中心服务器中转
- 📝 **CRDT 自动合并**：基于 Yjs 的 CRDT 算法自动处理并发编辑冲突
- 🚀 **零配置可用**：安装后即可用，默认使用公共信令服务器
- 🎨 **多人光标**：不同用户的光标位置和颜色实时可见
- ⚙️ **灵活配置**：URL参数、用户设置、服务器配置三级优先级
- 🔒 **隐私保护**：房间名通过 SHA256 哈希，信令服务器无法知道真实房间名
- 📦 **双端打包**：同时发布 npm 包和 pip 包
- 🔌 **RetroLab兼容**：同时支持JupyterLab底部状态栏和RetroLab工具栏

### 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 扩展框架 | JupyterLab Extension System | >=3.1, <4 |
| CRDT引擎 | Yjs | ^13.5.29 |
| WebRTC传输 | y-webrtc | ^10.2.3 |
| 信令协议 | WebSocket (y-webrtc signaling) | - |
| 本地通信 | BroadcastChannel | - |
| 加密哈希 | sjcl (SHA256) | 1.0.8 |
| 语言 | TypeScript + React(VDom) | - |
| Python打包 | jupyter_packaging | >=0.10,<1 |

## 快速开始

### 安装

```bash
pip install jupyterlab-webrtc-docprovider
```

### 启用协作

```bash
jupyter lab --collaborative
```

### 创建协作会话

```
http://localhost:8888/lab?room=demo&username=Alice
```

将相同 URL（`room` 参数一致）分享给其他人即可开始协作。

更多细节见 [安装与快速开始](concepts/01-getting-started.md) 和 [基本协作使用](examples/basic-collaboration.md)。

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    JupyterLab FrontEnd                  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ Status Bar   │  │ Command Palette│ │ Settings     │ │
│  │ (React/VDom) │  │ & Keybindings │ │ Editor Panel │ │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘ │
│         │                 │                  │         │
│  ┌──────┴─────────────────┴──────────────────┴───────┐ │
│  │              WebRtcManager (核心)                  │ │
│  │   • 三级配置: URL → Settings → Default            │ │
│  │   • 房间ID: SHA256(prefix + room)                  │ │
│  │   • 信号驱动: stateChanged → Provider 创建/销毁    │ │
│  └──────┬─────────────────┬──────────────────┬───────┘ │
│         │                 │                  │         │
│  ┌──────┴───────┐  ┌─────┴──────┐  ┌───────┴────────┐ │
│  │ WebRtcProvider│ │ y-webrtc   │  │ BroadcastChannel│ │
│  │ (per-document)│ │ WebSocket  │  │ (same-browser)  │ │
│  │ extends y-wrtc│ │ Signaling  │  │ 多标签页直连    │ │
│  └──────┬───────┘  └─────┬──────┘  └────────────────┘ │
│         │                 │                            │
│  ┌──────┴───────┐  ┌─────┴──────────────────────┐     │
│  │ Y.Doc (CRDT) │  │ WebRTC DataChannel (P2P)   │     │
│  │ per document │  │ 跨浏览器直连               │     │
│  └──────────────┘  └────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## 4个插件

| 插件 | ID | requires | optional | autoStart | 功能 |
|------|----|----------|----------|-----------|------|
| 核心插件 | `:plugin` | ISettingRegistry, PageConfig, ITranslator | - | yes | 创建WebRtcManager |
| 工厂插件 | `:factory` | IWebRtcManager | IStateDB | yes | 注册文档提供者工厂 |
| 状态栏插件 | `:status` | IWebRtcManager | IStatusBar | yes | 添加状态栏UI |
| RetroLab插件 | `:retro-status` | IWebRtcManager | - | yes | RetroLab工具栏适配 |

## 配置优先级

```
URL参数 (?room=&username=&usercolor=)
    ↓ 短路求值 ||
用户设置 (Settings Editor / overrides.json)
    ↓ 短路求值 ||
服务器配置 (PageConfig / jupyter_server_config.json)
    ↓ 默认
随机值/默认公共信令服务器
```

## 相关项目

- [JupyterLite](https://github.com/jupyterlite/jupyterlite) — 浏览器端Jupyter（本项目的来源）
- [y-webrtc](https://github.com/yjs/y-webrtc) — WebRTC connector for Yjs
- [Yjs](https://github.com/yjs/yjs) — CRDT framework
- [JupyterLab](https://github.com/jupyterlab/jupyterlab) — Jupyter 前端
