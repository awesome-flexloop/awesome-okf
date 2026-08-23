---
type: Concept
title: JupyterLite 整体架构
description: JupyterLite的多层架构设计：主线程、Service Worker、Web Worker内核三者的协作关系
tags: [architecture, thread-model, service-worker, web-worker]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:12:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: meta-source
    resource: /references/metasource.md
    title: JupyterLite 项目元信源
  - id: kernel-source
    resource: /references/kernel-source.md
    title: 内核系统信源
  - id: contents-source
    resource: /references/contents-source.md
    title: 内容管理信源
  - id: app-source
    resource: /references/app-source.md
    title: 应用框架信源
---

## 三层线程模型

JupyterLite 的核心架构建立在浏览器的三个线程上下文之上：

```
┌─────────────────────────────────────────────────────────────────┐
│                     主线程 (Main Thread)                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  JupyterLab UI (React/Lumino Widgets)                     │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │ Notebook    │  │ File Browser │  │ Kernel Manager  │  │  │
│  │  │ Panel       │  │              │  │                 │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘  │  │
│  │                                                           │  │
│  │  @jupyterlab/services (Contents/Session/Kernel API)       │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ BrowserStorageDrive (drive.ts)                       │  │  │
│  │  │   ↕ LocalForage → IndexedDB                          │  │  │
│  │  │ LiteKernelClient (client.ts)                         │  │  │
│  │  │   ↕ mock-socket WebSocket桥接                        │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↕                                  │
│                    Service Worker 拦截                          │
│              POST /api/drive → 同步XHR桥接                      │
│                              ↕                                  │
└─────────────────────────────────────────────────────────────────┘
                               ↕
┌─────────────────────────────────────────────────────────────────┐
│                  Web Worker (内核线程)                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  DriveFS (drivefs.ts) — Emscripten文件系统实现             │  │
│  │  ├─ DriveFSEmscriptenNodeOps (lookup/mknod/readdir)      │  │
│  │  └─ DriveFSEmscriptenStreamOps (open/read/write/close)   │  │
│  │         ↓ 所有文件操作通过同步XHR /api/drive               │  │
│  │                                                           │  │
│  │  ServiceWorkerContentsAPI → 同步XHR → Service Worker     │  │
│  │                                                           │  │
│  │  BaseKernel 实现 (如 PyodideKernel)                       │  │
│  │  ├─ handleMessage() 消息路由                              │  │
│  │  ├─ executeRequest() 代码执行                             │  │
│  │  └─ kernelInfoRequest() 内核信息                          │  │
│  │         ↕                                                 │  │
│  │  Pyodide / Xeus Python (WASM)                             │  │
│  │  import numpy, pandas, matplotlib...                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 关键数据流

### 1. 代码执行流

```
用户在Notebook中按Shift+Enter
    ↓
Notebook面板 → execute_request消息
    ↓
@jupyterlab/services Kernel API
    ↓
LiteKernelClient (主线程)
    ↓
mock-socket WebSocket → Worker线程
    ↓
BaseKernel.handleMessage()
    ↓
executeRequest() → Pyodide执行Python代码
    ↓
stream/display_data/execute_result消息回传
    ↓
mock-socket → 主线程
    ↓
Notebook面板渲染输出
```

### 2. 文件读取流（内核视角）

```
Pyodide内核: open('/drive/notebooks/test.ipynb', 'r')
    ↓
Emscripten FS: 查找文件节点
    ↓
DriveFSEmscriptenNodeOps.lookup() → 路径查找
    ↓
DriveFSEmscriptenStreamOps.open() → 打开文件
    ↓
ServiceWorkerContentsAPI.request({method:'get', path})
    ↓
同步 XMLHttpRequest POST /api/drive
    ↓ (浏览器同步阻塞Worker线程)
Service Worker 拦截 /api/drive 请求
    ↓
转发到主线程 BrowserStorageDrive.get()
    ↓
LocalForage → IndexedDB 读取文件
    ↓
JSON响应返回 → 同步XHR完成
    ↓
DriveFS获得文件内容 → Pyodide继续执行
```

### 3. 文件写入流（内核保存Notebook）

```
Pyodide内核保存Notebook
    ↓
文件内容写入DriveFS流缓冲区
    ↓
DriveFSEmscriptenStreamOps.close()
    ↓ (检测到写模式)
ServiceWorkerContentsAPI.request({method:'put', path, data})
    ↓
同步XHR POST /api/drive
    ↓
Service Worker → 主线程 BrowserStorageDrive.save()
    ↓
LocalForage → IndexedDB 持久化
```

## 核心设计决策

### 为什么用同步XHR？

Web Worker 中无法直接访问 IndexedDB（异步API），而 Emscripten 编译的 CPython（Pyodide）的文件系统操作是**同步**的（POSIX API）。为了桥接这个同步-异步不匹配：

1. **同步XHR阻塞Worker**：Web Worker中允许同步XMLHttpRequest，它会阻塞Worker线程但不会阻塞主线程UI
2. **Service Worker作为中间层**：同步XHR被Service Worker拦截，Service Worker可以通过postMessage与主线程通信
3. **Atomics + SharedArrayBuffer备选**：现代浏览器也支持通过SharedArrayBuffer和Atomics实现更高效的同步，但同步XHR方案兼容性更好

### 为什么用mock-socket模拟WebSocket？

JupyterLab 的内核通信基于 WebSocket 协议（`v1.kernel.websocket.jupyter.org`）。在浏览器端没有真实服务器，因此：

1. 使用 `mock-socket` 库创建一个内存中的 WebSocketServer 和 WebSocketClient 对
2. LiteKernelClient（主线程）持有 WebSocketClient
3. 内核实现（Worker中）通过 Worker 全局 `self` 对象收发消息
4. 消息通过 `serialize/deserialize` 进行Jupyter标准的二进制序列化

### 为什么DriveFS实现Emscripten NodeOps/StreamOps？

Emscripten 提供了可挂载的文件系统（MEMFS、IDBFS、WORKERFS等），但 JupyterLite 需要将文件系统操作路由到 JupyterLab 的 Contents API（而不是直接访问 IndexedDB），因为：

1. JupyterLab 的 ContentsManager 处理了格式转换（json/text/base64）
2. 需要支持检查点（checkpoints）功能
3. 需要支持 content providers（默认内容提供者，如静态站点文件）
4. 文件变更需要触发 fileChanged 信号通知UI更新

## 消息协议复用

JupyterLite 完全复用 Jupyter 的 Jupyter Wire Protocol，包括：

| 通道 | 用途 |
|------|------|
| `shell` | 请求/响应（execute_request, complete_request等） |
| `iopub` | 广播输出（stream, display_data, execute_result, status等） |
| `stdin` | 输入请求（input_request/input_reply） |
| `control` | 控制消息（interrupt等） |

这意味着前端无需修改即可与JupyterLite内核通信，复用了JupyterLab的所有UI组件。

## 存储分层

JupyterLite 的文件存储分为三层：

```
┌─────────────────────────────────────────┐
│  静态站点文件 (Site Drive / _contents)    │ ← 随应用部署，只读
├─────────────────────────────────────────┤
│  浏览器存储 (BrowserStorage / LocalForage)│ ← 用户创建/修改，持久化
├─────────────────────────────────────────┤
│  内存文件系统 (DriveFS / Emscripten FS)   │ ← 内核工作副本，运行时
└─────────────────────────────────────────┘
```

- **Site Drive**：部署时打包的示例Notebook和数据文件，通过 `api/contents/{path}/__all__.json` 索引
- **BrowserStorage Drive**：用户文件在IndexedDB中的持久化存储，读写都走LocalForage
- **DriveFS**：挂载在Pyodide中的虚拟文件系统，运行时将操作转发到BrowserStorage

读取时：优先检查BrowserStorage，不存在则回退到Site Drive
写入时：始终写入BrowserStorage，覆盖Site Drive的同名文件

## 相关概念

- [内核系统](/concepts/02-kernel-system.md)
- [内容管理与文件系统](/concepts/03-contents-and-filesystem.md)
- [Service Worker桥接](/concepts/04-service-worker-bridge.md)
- [浏览器存储](/concepts/05-browser-storage.md)
- [Python构建系统](/concepts/06-build-system.md)
