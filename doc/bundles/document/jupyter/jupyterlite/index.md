---
type: OKF
title: JupyterLite 教程
description: JupyterLite 浏览器端 Jupyter 发行版的系统化教程，涵盖内核系统、内容管理、文件系统桥接、Service Worker、构建系统与扩展架构
tags: [jupyterlite, jupyter, wasm, pyodide, browser, notebook, webworker]
okf_version: "0.2"
version: "0.1.0"
source: https://github.com/jupyterlite/jupyterlite
source_commit: cf4958fcd20763a61ce4c7eeb1394f3c60e16cb0
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:40:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# JupyterLite 教程

JupyterLite 是一个完全运行在浏览器中的 Jupyter 发行版。它将 Python 内核通过 WebAssembly 编译后在 Web Worker 中运行，所有文件存储在浏览器 IndexedDB 中，支持静态部署到任意 Web 服务器。

本教程基于源码深度分析（commit `cf4958fc`），系统讲解 JupyterLite 的核心架构、内核通信、文件系统桥接、浏览器存储、构建系统和扩展机制。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-JupyterLite简介](concepts/00-introduction.md) — 是什么、核心特性、与传统Jupyter的区别
- [01-整体架构](concepts/01-architecture-overview.md) — 三层线程模型、关键数据流、核心设计决策
- [02-内核系统](concepts/02-kernel-system.md) — BaseKernel抽象类、消息路由、LiteKernelClient、mock-socket桥接
- [03-内容管理与文件系统](concepts/03-contents-and-filesystem.md) — BrowserStorageDrive、DriveFS、Emscripten FS桥接
- [04-Service Worker桥接](concepts/04-service-worker-bridge.md) — 离线缓存与同步XHR文件系统桥接
- [05-浏览器存储](concepts/05-browser-storage.md) — LocalForage三store设计、检查点、服务器文件分层
- [06-Python构建系统](concepts/06-build-system.md) — LiteManager、Doit任务框架、Addon插件体系
- [07-内核类型](concepts/07-kernel-types.md) — Pyodide vs Xeus内核、文件系统挂载、JS互操作
- [08-扩展架构](concepts/08-extension-architecture.md) — JupyterLab插件系统、内核扩展点、Content Provider

### [实践示例](examples/index.md)
- [01-快速开始与本地部署](examples/01-quickstart-deploy.md) — 安装CLI、构建站点、本地预览
- [02-站点配置](examples/02-site-configuration.md) — jupyter-lite.json配置详解
- [03-内容管理API使用](examples/03-contents-api-usage.md) — 文件CRUD、检查点、变更监听
- [04-Pyodide内核文件系统](examples/04-pyodide-filesystem.md) — DriveFS挂载、文件读写、JS互操作

### [信源参考](references/index.md)
- [项目元信源](references/metasource.md) — 版本信息、目录结构、包清单
- [内核系统信源](references/kernel-source.md) — BaseKernel、LiteKernelClient API登记
- [内容管理信源](references/contents-source.md) — BrowserStorageDrive、DriveFS API登记
- [构建系统信源](references/build-source.md) — LiteManager、Addon API登记
- [应用框架信源](references/app-source.md) — 应用框架、扩展加载

## 🚀 快速体验

访问 [jupyterlite.github.io/demo](https://jupyterlite.github.io/demo) 即可在线体验 JupyterLite，无需安装任何软件。

本地构建：
```bash
pip install jupyterlite
jupyter lite build --content ./notebooks
jupyter lite serve
# 访问 http://localhost:8000
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🌐 零安装 | 打开浏览器即可使用完整Jupyter环境 |
| 🔌 静态部署 | 部署到GitHub Pages、Vercel、任意CDN |
| 💾 本地持久化 | IndexedDB存储文件，支持离线使用 |
| 🐍 Pyodide内核 | CPython编译为WASM，支持numpy/pandas/matplotlib |
| 📦 JupyterLab兼容 | 复用JupyterLab组件和扩展生态 |
| ⚡ Service Worker | 离线缓存 + 文件系统同步桥接 |
| 🔧 可扩展 | 支持自定义内核、Content Provider、前端扩展 |

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                   主线程 (UI)                             │
│  JupyterLab UI → @jupyterlab/services                    │
│  ├─ LiteKernelClient (mock-socket桥接)                   │
│  └─ BrowserStorageDrive (LocalForage → IndexedDB)        │
└────────────────────────┬────────────────────────────────┘
                         │ POST /api/drive (同步XHR)
                         ↓
              ┌─────────────────────┐
              │   Service Worker    │
              │  (缓存+请求转发)     │
              └─────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                Web Worker (内核)                         │
│  DriveFS (Emscripten NodeOps/StreamOps)                  │
│  └─ ServiceWorkerContentsAPI → 同步XHR                   │
│  PyodideKernel (BaseKernel) → Pyodide WASM               │
└─────────────────────────────────────────────────────────┘
```

## 📖 推荐学习路径

1. **入门了解**：阅读 [00-简介](concepts/00-introduction.md) 和 [01-整体架构](concepts/01-architecture-overview.md)，理解三层线程模型
2. **动手部署**：跟着 [01-快速开始](examples/01-quickstart-deploy.md) 构建第一个站点
3. **理解核心**：学习 [02-内核系统](concepts/02-kernel-system.md) 和 [03-内容管理](concepts/03-contents-and-filesystem.md)
4. **深入桥接**：阅读 [04-Service Worker桥接](concepts/04-service-worker-bridge.md) 理解同步XHR机制
5. **掌握存储**：学习 [05-浏览器存储](concepts/05-browser-storage.md) 理解IndexedDB持久化
6. **构建定制**：阅读 [06-构建系统](concepts/06-build-system.md) 和 [02-配置示例](examples/02-site-configuration.md)
7. **扩展开发**：学习 [07-内核类型](concepts/07-kernel-types.md) 和 [08-扩展架构](concepts/08-extension-architecture.md)
