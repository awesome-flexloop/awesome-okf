---
type: Concept
title: 内核类型
description: JupyterLite支持的内核类型：Pyodide（WASM CPython）与Xeus内核家族的架构差异
tags: [kernel, pyodide, xeus, wasm, webassembly, python]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:26:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: meta-source
    resource: /references/metasource.md
    title: JupyterLite 项目元信源
  - id: kernel-source
    resource: /references/kernel-source.md
    title: 内核系统信源
---

## JupyterLite 内核家族

JupyterLite 支持多种在浏览器中运行的内核，它们都通过继承 `BaseKernel` 抽象类来实现Jupyter消息协议。主要有两大内核家族：**Pyodide** 和 **Xeus**。

## Pyodide 内核

Pyodide 是 CPython 编译为 WebAssembly 的版本，是 JupyterLite 的默认 Python 内核。

### 技术特点

| 特性 | 说明 |
|------|------|
| 基础 | CPython 3.x 通过 Emscripten 编译为 WASM |
| 包管理 | 支持预编译的WASM包（numpy/pandas/matplotlib等）、micropip安装纯Python包 |
| 文件系统 | 通过 Emscripten MEMFS/IDBFS + DriveFS 桥接浏览器存储 |
| JS互操作 | `from js import ...` 直接访问浏览器DOM和Web API |
| 启动方式 | 在 Web Worker 中加载 Pyodide WASM 模块 |

### 启动流程

1. LiteKernelClient.startNew() 被调用
2. 创建新的 Web Worker，加载 Pyodide 内核脚本
3. Worker 中初始化 Pyodide（加载WASM、初始化文件系统）
4. DriveFS 挂载到 Emscripten 文件系统（`/drive/` 挂载点）
5. 内核向主线程发送 `kernel_info_reply` 表示就绪
6. 通过 mock-socket WebSocket 与主线程通信

### 文件系统挂载

Pyodide 内核使用 DriveFS 将浏览器存储挂载到 Emscripten 文件系统：

```
/pyodide/           — Pyodide运行时文件
/drive/             — JupyterLite内容驱动器（挂载DriveFS）
  └── notebooks/    — 对应 BrowserStorage:notebooks/
/drive/pyodide/     — Pyodide包安装目录
```

内核中执行 `open('/drive/notebooks/test.ipynb')` 会通过 DriveFS → ServiceWorkerContentsAPI → 同步XHR → BrowserStorageDrive → IndexedDB 链路读取文件。

### JavaScript 互操作

Pyodide 的独特优势是可以直接与浏览器JavaScript交互：

```python
from js import document, fetch, console
# 操作DOM
document.getElementById("output").innerHTML = "<h1>Hello from Python!</h1>"
# 发起网络请求
response = await fetch("https://api.example.com/data")
data = await response.json()
# 调用JS库
import js
js.eval("alert('Hello!')")
```

这使得Pyodide内核可以创建丰富的交互式可视化，直接操作网页DOM。

## Xeus 内核

Xeus 是一个 C++ 实现的 Jupyter 内核框架，支持多种编程语言内核。

### Xeus 特点

| 特性 | 说明 |
|------|------|
| 基础 | C++ 库，原生实现Jupyter协议 |
| 语言支持 | xeus-python（C++实现的Python内核）、xeus-lua、xeus-sqlite等 |
| WASM编译 | 通过 Emscripten 将 C++ 内核编译为 WASM |
| 性能 | 某些场景下比Pyodide启动更快 |

### xeus-python

xeus-python 是基于 Xeus 框架的 Python 内核，它不像 Pyodide 那样携带完整的 CPython WASM 运行时，而是有自己的Python实现路径。在JupyterLite中，xeus-python也是一个可选内核。

## 内核注册

内核通过 KernelSpecs 注册到 JupyterLite：

```typescript
// 内核规格信息
interface ISpecModel {
  name: string;           // 内核标识名（如'python'）
  display_name: string;   // 显示名（如'Python (Pyodide)'）
  language: string;       // 语言（如'python'）
  argv: string[];         // 启动命令（在JupyterLite中通常为空，WASM内核不需要）
  resources: {};          // 资源（logo等）
  metadata?: {};          // 元数据
}
```

每个内核注册时提供：
1. **spec**：内核规格信息（显示在Launcher和Kernel选择菜单中）
2. **create**：工厂函数，创建BaseKernel实例

## FALLBACK_KERNEL

当请求的内核不可用时，JupyterLite 使用 `FALLBACK_KERNEL` 常量指定的默认内核（通常是 Pyodide Python 内核）。LiteKernelClient.startNew() 中：

```typescript
const kernelName = name ?? FALLBACK_KERNEL;
const factory = this._kernelspecs.factories.get(kernelName);
if (!factory) {
  throw Error(`No factory for kernel ${kernelName}`);
}
```

## 内核与主线程的通信模型

无论是Pyodide还是Xeus内核，都运行在独立的Web Worker中：

```
┌─────────────── 主线程 ───────────────┐     ┌─────── Worker (内核) ────────┐
│                                      │     │                              │
│  LiteKernelClient                    │     │  PyodideKernel / XeusKernel  │
│  ├─ mock-socket WebSocketClient ─────┼─────┼─→ Worker消息监听             │
│  │  (serialize/deserialize)          │     │  ├─ BaseKernel.handleMessage  │
│  │                                   │     │  └─ Pyodide/Xeus执行         │
│  BrowserStorageDrive                 │     │  DriveFS                     │
│  └─ LocalForage (IndexedDB)          │     │  └─ Emscripten FS            │
│                                      │     │                              │
└───────────────↕──────────────────────┘     └──────────────────────────────┘
                │ Service Worker拦截
                ↓
         POST /api/drive (同步XHR)
```

## 相关概念

- [内核系统](/concepts/02-kernel-system.md)
- [内容管理与文件系统](/concepts/03-contents-and-filesystem.md)
- [Service Worker桥接](/concepts/04-service-worker-bridge.md)
- [扩展架构](/concepts/08-extension-architecture.md)
