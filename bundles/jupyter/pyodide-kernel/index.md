---
type: OKF
title: JupyterLite Pyodide Kernel 教程
description: jupyterlite-pyodide-kernel 是 JupyterLite 的 Python 内核，基于 Pyodide WebAssembly 在浏览器中运行 CPython。本教程系统讲解其双层架构（构建时Addon+运行时WASM）、双Worker通信模式（Comlink/Coincident）、包管理（piplite三级查找）、IPython兼容层与消息桥接机制。
tags: [pyodide, jupyterlite, kernel, python, wasm, webworker, browser, ipython, piplite, comlink, coincident]
okf_version: "0.2"
version: "0.9.0a1"
source: https://github.com/jupyterlite/pyodide-kernel
source_version: "0.9.0a1"
pyodide_version: "0.29.3"
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
---

# JupyterLite Pyodide Kernel 教程

jupyterlite-pyodide-kernel 是 JupyterLite 的 **Python 内核**，基于 Pyodide（CPython 编译为 WebAssembly）在浏览器中完整运行 Python 解释器。它是 JupyterLite 默认的 Python kernel，让用户无需任何后端服务器即可在浏览器中编写和执行 Python 代码。

本教程基于 jupyterlite-pyodide-kernel v0.9.0a1（适配 Pyodide v0.29.3、JupyterLite >=0.6.0a5）源码深度分析，系统讲解其双层架构设计、Worker 通信机制、浏览器端包管理、IPython 兼容策略和消息桥接机制。

## 📚 快速导航

### [概念文档](concepts/index.md)

#### 入门

- [00-Pyodide Kernel 介绍](concepts/00-introduction.md) — 是什么、核心特性、版本依赖、项目组成
- [01-快速开始](concepts/01-getting-started.md) — 安装、构建站点、基本配置、启动预览

#### 核心概念

- [02-架构总览](concepts/02-architecture-overview.md) — 双层架构、三层执行模型、初始化流程、消息流
- [03-Worker通信模式](concepts/03-worker-communication.md) — Comlink(postMessage) vs Coincident(SharedArrayBuffer)、stdin实现、文件系统差异
- [04-构建时Addon系统](concepts/04-build-addons.md) — PyodideAddon/PipliteAddon/PyodideLockAddon、生命周期钩子
- [05-浏览器端包管理](concepts/05-package-management.md) — piplite三级查找、%pip魔法、loadPackagesFromImports、micropip包装
- [06-Python兼容性层](concepts/06-python-compatibility.md) — Mock/Patch/子类化三层适配、IPython WASM适配、不支持功能
- [07-消息桥接机制](concepts/07-message-bridge.md) — Python↔JS回调绑定、stream/display/comm/stdin消息流

#### 高级主题

- [08-Lockfile定制](concepts/08-lockfile-customization.md) — pyodide-lock.json定制、UvPipCompile、包裁剪优化

### [实践示例](examples/index.md)
- [基本安装与配置](examples/basic-install-config.md) — 从零安装、构建站点、验证内核
- [添加自定义Wheel包](examples/custom-wheels.md) — 本地wheels、pypi目录、纯Python vs WASM wheel、离线部署

### [信源参考](references/index.md)
- [Python Addon源码](references/addon-source.md) — 构建端三个Addon的API参考
- [TypeScript Kernel源码](references/kernel-ts-source.md) — 主线程Kernel、Worker、Comlink/Coincident实现
- [浏览器端Python Kernel源码](references/kernel-py-source.md) — PyodideKernel、Interpreter、Display桥接、Mocks
- [piplite源码](references/piplite-source.md) — 浏览器端包管理器API
- [JupyterLab Extension源码](references/extension-source.md) — 插件注册与Kernel Spec
- [事实清单](facts.md) — 从源码采集的129条零推测事实
- [架构洞察](insights.md) — 5个核心架构洞察四元组与知识地图

## 🚀 快速体验

安装 pyodide-kernel 并构建 JupyterLite 站点：

```bash
# 安装
pip install jupyterlite-pyodide-kernel

# 构建站点（自动使用CDN Pyodide）
jupyter lite build

# 预览
jupyter lite serve
# 访问 http://localhost:8000
```

打开浏览器后，在 Launcher 中选择 "Pyodide" 内核创建 Notebook：

```python
import sys
print(f"Python {sys.version} on {sys.platform}")

# 内置包自动加载
import numpy as np
arr = np.arange(10)
print(arr.mean())

# 安装额外包
%pip install regex
import regex
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🐍 完整Python 3.12 | Pyodide v0.29.3 提供 CPython 3.12 WASM 运行时 |
| 🔄 双Worker模式 | Comlink（postMessage）/ Coincident（SharedArrayBuffer）自动选择 |
| 📦 三级包管理 | Pyodide内置包 → 本地wheel索引 → PyPI回退 |
| 🧩 IPython兼容 | Mock+Patch+子类化三层策略，InteractiveShell完整运行 |
| 🌐 纯静态部署 | 构建产物为纯静态文件，可部署到任何CDN |
| 🔌 Jupyter协议兼容 | 完整实现execute/complete/inspect/comm等kernel消息 |
| 📁 文件系统同步 | Coincident模式下DriveFS与Jupyter Contents API同步 |
| ⌨️ 同步stdin | input()/getpass()通过同步XHR或Atomics.wait实现 |

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│  构建时（服务器/开发者机器）                              │
│  Python + JupyterLite Addon                             │
│  ├─ PyodideAddon → 下载/复制Pyodide发行版               │
│  ├─ PipliteAddon → 下载wheel + 生成all.json索引         │
│  └─ PyodideLockAddon → 定制pyodide-lock.json            │
│  → 产出：纯静态文件（HTML/JS/WASM/wheels/JSON）          │
└─────────────────────────────────────────────────────────┘
                           │
                    部署到静态服务器
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  运行时（浏览器）                                         │
│                                                          │
│  ┌─ 主线程 ──────────────────────────────────────────┐  │
│  │  JupyterLab / Notebook 前端                        │  │
│  │  └─ PyodideKernel (TypeScript)                    │  │
│  │     ├─ IKernel接口实现                             │  │
│  │     └─ Worker生命周期管理                          │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │ Comlink.postMessage          │
│                         │ 或 Coincident.SharedArrayBuf │
│  ┌─ Web Worker ─────────┴────────────────────────────┐  │
│  │  PyodideRemoteKernel (TypeScript)                  │  │
│  │  ├─ import pyodide.mjs → loadPyodide()            │  │
│  │  ├─ 加载 micropip + piplite                        │  │
│  │  └─ 绑定 Python↔JS 回调                           │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │ Pyodide FFI                   │
│  ┌─ WASM (Worker内部) ──┴────────────────────────────┐  │
│  │  Pyodide CPython 3.12                             │  │
│  │  └─ pyodide_kernel (Python)                        │  │
│  │     ├─ Interpreter(InteractiveShell子类)          │  │
│  │     ├─ LiteStream/LiteDisplay 桥接                │  │
│  │     ├─ Comm通信                                    │  │
│  │     ├─ Mocks/Patches                              │  │
│  │     └─ piplite包管理器                            │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 📖 推荐学习路径

1. **入门了解**：阅读 [00-介绍](concepts/00-introduction.md) 和 [01-快速开始](concepts/01-getting-started.md)，安装并体验 Pyodide Kernel
2. **动手实践**：按 [基本安装与配置](examples/basic-install-config.md) 步骤构建自己的 JupyterLite 站点
3. **理解架构**：学习 [02-架构总览](concepts/02-architecture-overview.md)，建立双层架构和三层执行模型的全局认知
4. **核心机制**：依次阅读 [03-Worker通信](concepts/03-worker-communication.md)、[04-构建Addon](concepts/04-build-addons.md)、[05-包管理](concepts/05-package-management.md)、[06-Python兼容](concepts/06-python-compatibility.md)、[07-消息桥接](concepts/07-message-bridge.md)
5. **实践操作**：跟着 [添加自定义Wheel包](examples/custom-wheels.md) 添加自己的 Python 包
6. **高级优化**：阅读 [08-Lockfile定制](concepts/08-lockfile-customization.md) 优化包加载性能
7. **源码参考**：查阅 [references/](references/index.md) 获取精确的 API 参考，配合 [事实清单](facts.md) 和 [架构洞察](insights.md) 深入理解设计决策

## 🔑 核心设计洞察

### 双层架构
构建时（Python Addon）和运行时（JS/WASM）分离——构建阶段准备静态资源，运行时零服务器依赖。

### 双通信模式
根据 `crossOriginIsolated` 自动选择 Comlink（兼容性优先）或 Coincident（性能优先），对外暴露统一接口。

### 三级包查找
内置包→本地索引→PyPI回退，兼顾离线可用性和生态完整性。%pip 魔法通过代码预转换映射到 piplite.install()。

### 三层IPython适配
先 mock 缺失模块（让import不报错），再 patch 运行时配置（matplotlib backend），最后子类化替换不兼容行为。
