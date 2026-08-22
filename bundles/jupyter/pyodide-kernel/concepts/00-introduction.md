---
type: Concept
title: Pyodide Kernel 介绍
description: jupyterlite-pyodide-kernel 是什么，它在 JupyterLite 生态中的位置，以及核心特性
tags: [introduction, overview, pyodide, jupyterlite]
prerequisites: []
objectives: ["理解 pyodide-kernel 的定位和作用", "了解项目核心组成", "掌握版本和依赖关系"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: pyproject
    resource: /references/addon-source.md
    title: pyproject.toml
---

# Pyodide Kernel 介绍

## 为什么需要 Pyodide Kernel？

JupyterLite 是 Jupyter 的浏览器版本，不需要后端服务器就能运行 Notebook。但标准的 IPython kernel 需要真正的 CPython 进程，无法在浏览器中直接运行。

Pyodide 是 CPython 编译到 WebAssembly 的版本，可以在浏览器中执行 Python 代码。jupyterlite-pyodide-kernel 将两者连接起来：它实现了 Jupyter 的内核协议，通过 Web Worker 运行 Pyodide 解释器，让用户在浏览器中获得完整的 Python 编程体验。

## 是什么

jupyterlite-pyodide-kernel 是一个 Python kernel for JupyterLite，基于 Pyodide 运行。它由两部分组成：

1. **Python 包（构建端）**：`jupyterlite-pyodide-kernel`，作为 JupyterLite 的 Addon 插件，在构建阶段准备 Pyodide 发行版和 wheel 包资源
2. **TypeScript 包 + Python 包（运行端）**：`@jupyterlite/pyodide-kernel`，在浏览器中通过 Web Worker 运行 Pyodide 解释器，实现完整的 Jupyter kernel 协议

### 版本信息

- Python 包版本：`0.9.0a1`（基于 pyproject.toml F-001）
- 目标 Pyodide 版本：`0.29.3`（F-014）
- 目标 JupyterLite 版本：`>=0.6.0a5,<0.7`（F-009）
- Python 要求：`>=3.12`（F-002）
- License：BSD-3-Clause（F-006）
- Repository：`https://github.com/jupyterlite/pyodide-kernel`（F-005）

### 核心依赖

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| jupyterlite-core | `>=0.6.0a5,<0.7` | JupyterLite 核心框架（F-009） |
| pyodide-cli | `>=0.2.2` | Pyodide 命令行工具（F-010） |
| pyodide-lock | `>=0.1.3` | Lockfile 定制工具（F-011） |
| @jupyterlab/services | `^7.1.2` | JupyterLab 服务通信（F-061） |
| @jupyterlite/kernel | `^0.6.0-alpha.5` | JupyterLite 内核基类（F-062） |
| comlink | `^4.4.2` | Worker 通信库（postMessage 模式）（F-063） |
| coincident | `^2.3.1` | SharedArrayBuffer 通信库（F-064） |

## 核心特性

### 完整的 Jupyter Kernel 协议支持

PyodideKernel 实现了所有标准的 kernel 消息处理方法（F-048）：
- `execute_request` — 代码执行
- `complete_request` — 代码补全
- `inspect_request` — 对象内省
- `is_complete_request` — 代码完整性检查
- `comm_info/open/msg/close` — Comm 通信（Widget 支持）
- `kernel_info_request` — 内核信息
- `input_reply` — 标准输入响应

### 双 Worker 通信模式

根据浏览器是否支持跨源隔离（`crossOriginIsolated`），自动选择两种通信模式（F-050/F-051）：

| 模式 | 通信机制 | 特性 |
|------|---------|------|
| Comlink | postMessage | 兼容性好，stdin 通过同步 XHR，文件系统不同步 |
| Coincident | SharedArrayBuffer + Atomics | 性能更好，支持同步文件系统和同步 stdin |

### 浏览器端包管理

通过 piplite（micropip 的包装）提供三级包查找（F-111）：
1. Pyodide 内置包（pyodide-lock.json 预加载）
2. 本地 wheel 索引（all.json，含用户自定义 wheels 和 federated extension wheels）
3. PyPI 回退（可禁用）

### IPython 兼容层

通过 mock + patch + 子类化三层策略，让 IPython InteractiveShell 在 Pyodide WASM 环境中运行（F-104/F-105/F-088）。

## 项目组成

```
jupyterlite-pyodide-kernel/
├── jupyterlite_pyodide_kernel/    # Python 构建端
│   ├── addons/
│   │   ├── pyodide.py             # Pyodide 发行版管理 Addon
│   │   ├── piplite.py             # piplite wheel 管理 Addon
│   │   └── lock.py                # Lockfile 定制 Addon
│   └── constants.py               # 核心常量
├── packages/
│   ├── pyodide-kernel/            # TypeScript + Python 运行端
│   │   ├── src/                   # TypeScript Kernel 源码
│   │   │   ├── kernel.ts          # 主线程 Kernel
│   │   │   ├── worker.ts          # Worker 抽象基类
│   │   │   ├── comlink.worker.ts  # Comlink Worker 实现
│   │   │   └── coincident.worker.ts # Coincident Worker 实现
│   │   └── py/
│   │       ├── pyodide-kernel/    # 浏览器端 Python Kernel
│   │       └── piplite/           # 浏览器端包管理器
│   └── pyodide-kernel-extension/  # JupyterLab 扩展
└── pyproject.toml
```

## 下一步

- [快速开始](/concepts/01-getting-started.md) — 安装和基本配置
- [架构总览](/concepts/02-architecture-overview.md) — 理解整体架构设计

## 源码参考

- [Python Addon 源码](/references/addon-source.md)
- [JupyterLab Extension 源码](/references/extension-source.md)
