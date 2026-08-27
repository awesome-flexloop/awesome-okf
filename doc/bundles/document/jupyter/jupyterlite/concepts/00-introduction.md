---
type: Concept
title: JupyterLite 简介
description: JupyterLite 是什么、核心特性、技术栈，以及它与传统 Jupyter 的区别
tags: [introduction, overview, jupyterlite, browser]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: meta-source
    resource: /references/metasource.md
    title: JupyterLite 项目元信源
---

## JupyterLite 是什么

JupyterLite 是一个**完全运行在浏览器中的 Jupyter 发行版**。它不需要后端服务器、不需要安装 Python 环境，打开网页即可使用完整的 JupyterLab 或 Notebook 体验。

核心思想：将 Jupyter 的计算内核（Python内核）通过 WebAssembly (WASM) 编译后在浏览器的 Web Worker 中运行，所有文件存储在浏览器的 IndexedDB 中，整个应用作为静态站点部署。

## 核心特性

| 特性 | 说明 |
|------|------|
| 🌐 零安装 | 打开浏览器即可使用，无需安装Python或Jupyter |
| 🔌 静态部署 | 纯静态文件，可部署到GitHub Pages、Vercel、任意CDN |
| 💾 本地持久化 | 文件和Notebook存储在浏览器IndexedDB中，支持离线 |
| 🐍 Pyodide内核 | CPython编译为WebAssembly，支持大多数科学计算包 |
| 🔬 Xeus内核 | 基于Xeus的替代内核框架，支持C++等语言 |
| 📦 JupyterLab兼容 | 复用JupyterLab组件生态，支持大部分JupyterLab扩展 |
| ⚡ Service Worker | 离线缓存+文件系统桥接 |

## 与传统 Jupyter 的区别

| 维度 | 传统 Jupyter | JupyterLite |
|------|-------------|-------------|
| 运行位置 | 服务器端（本机或远程） | 浏览器内（Web Worker） |
| Python环境 | 系统/conda环境 | Pyodide (WASM CPython) |
| 文件存储 | 服务器文件系统 | IndexedDB（浏览器） |
| 内核通信 | WebSocket → 服务器进程 | mock-socket → Web Worker |
| 文件系统桥接 | 直接文件IO | Emscripten FS → Service Worker → 主线程 |
| 部署方式 | 需要服务器（JupyterHub/Notebook） | 静态文件托管 |
| 网络依赖 | 需要实时连接 | 首次加载后可离线 |

## 技术栈

### 前端
- **TypeScript**：主要开发语言
- **JupyterLab 组件**：`@jupyterlab/services`、`@jupyterlab/coreutils`、`@jupyterlab/nbformat`等
- **Lumino**：JupyterLab底层工具库（Signaling、Widgets、Commands）
- **Rspack**：构建工具（Rust-based Webpack替代）
- **LocalForage**：IndexedDB封装，用于持久化存储
- **mock-socket**：模拟WebSocket，用于主线程-Worker通信

### 后端/内核
- **Pyodide**：CPython 3.x 编译为WebAssembly
- **Xeus**：C++实现的Jupyter内核框架，支持多语言
- **Emscripten**：将C/C++代码编译为WASM的工具链

### 构建工具链
- **Python + doit**：静态站点构建任务框架
- **Traitlets**：Python配置系统（Jupyter生态通用）
- **Addon插件体系**：基于entry_points的可扩展构建流程

## 支持的前端界面

| 界面 | 说明 |
|------|------|
| Lab | 完整JupyterLab体验（启动器、文件浏览器、多面板） |
| Notebook | 经典Notebook界面 |
| REPL | 交互式代码控制台 |
| Consoles | 控制台面板 |
| Edit | 文本编辑器 |
| Tree | 文件浏览器 |
| Doc | 文档查看器 |

## 典型使用场景

1. **教学演示**：无需学生安装环境，分享链接即可运行Notebook
2. **嵌入式文档**：在文档网站中嵌入可执行代码示例
3. **离线计算**：离线环境下的数据探索和计算
4. **静态站点**：作为个人博客/作品集的一部分，展示可交互代码
5. **轻量级原型**：快速验证想法，无需配置开发环境

## 相关概念

- [整体架构](01-architecture-overview.md)
- [内核系统](02-kernel-system.md)
- [内容管理与文件系统](03-contents-and-filesystem.md)
- [Service Worker桥接](04-service-worker-bridge.md)
- [浏览器存储](05-browser-storage.md)
