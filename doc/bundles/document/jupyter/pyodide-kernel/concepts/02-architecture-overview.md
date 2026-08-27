---
type: Concept
title: 架构总览
description: pyodide-kernel 的双层架构设计——构建时 Python Addon + 运行时三层执行模型
tags: [architecture, runtime, build, worker, wasm]
prerequisites: ["00-introduction", "01-getting-started"]
objectives: ["理解双层架构的设计意图", "掌握运行时三层执行模型", "理解消息流从前端到Python解释器的路径"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: kernel-ts
    resource: /references/kernel-ts-source.md
    title: kernel.ts
  - id: worker-ts
    resource: /references/kernel-ts-source.md
    title: worker.ts
  - id: kernel-py
    resource: /references/kernel-py-source.md
    title: kernel.py
---

# 架构总览

## 为什么采用双层架构

浏览器中运行 Python 需要解决两个根本问题：
1. **资源准备**：Pyodide WASM 文件、Python 包、扩展需要在构建阶段下载并组织好
2. **运行时执行**：浏览器中不能阻塞主线程，需要 Web Worker 隔离 + 进程间通信

pyodide-kernel 通过"构建时 Python Addon + 运行时 JS/Python WASM"双层架构分别解决这两个问题。

## 双层架构

### 第一层：构建时（Python/Node.js）

构建阶段在服务器或开发者机器上运行，由三个 JupyterLite Addon 完成资源准备：

| Addon | 职责 | 产出 |
|-------|------|------|
| `PyodideAddon` | 下载/复制 Pyodide 发行版 | `static/pyodide/pyodide.mjs`、配置中的 `pyodideUrl` |
| `PipliteAddon` | 下载/索引 wheel 包 | `pypi/all.json` 索引、`static/pypi/*.whl` |
| `PyodideLockAddon` | 定制 pyodide-lock.json | 定制的 `pyodide-lock.json`（可选） |

构建产物是纯静态文件，可以部署到任何静态文件服务器（GitHub Pages、CDN 等）。

### 第二层：运行时（浏览器）

运行时在用户浏览器中执行，采用三层模型：

```
┌─────────────────────────────────────────────────┐
│  浏览器主线程 (UI Thread)                        │
│  ┌───────────────────────────────────────────┐  │
│  │  JupyterLab / Notebook 前端               │  │
│  │  ┌─────────────────────────────────────┐  │  │
│  │  │  PyodideKernel (TypeScript)         │  │  │
│  │  │  - 实现 IKernel 接口                │  │  │
│  │  │  - Worker 生命周期管理              │  │  │
│  │  │  - 消息序列化/反序列化             │  │  │
│  │  └─────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────┘  │
├─────────────────────────────────────────────────┤
│  Web Worker 线程                                │
│  ┌───────────────────────────────────────────┐  │
│  │  PyodideRemoteKernel (TypeScript)        │  │
│  │  - 加载 pyodide.mjs                      │  │
│  │  - 调用 loadPyodide()                    │  │
│  │  - 加载 piplite 包管理器                │  │
│  │  - 挂载文件系统                          │  │
│  │  - 绑定 Python ↔ JS 回调               │  │
│  └───────────────────────────────────────────┘  │
├─────────────────────────────────────────────────┤
│  WebAssembly 环境 (Worker 内部)                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Pyodide WASM CPython 运行时             │  │
│  │  ┌─────────────────────────────────────┐  │  │
│  │  │  pyodide_kernel (Python)            │  │  │
│  │  │  - PyodideKernel（执行/补全/内省） │  │  │
│  │  │  - Interpreter（IPython 子类）    │  │  │
│  │  │  - LiteStream / DisplayPublisher   │  │  │
│  │  │  - Comm 通信                        │  │  │
│  │  │  - Mocks / Patches                 │  │  │
│  │  │  - piplite（包管理器）            │  │  │
│  │  └─────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 初始化流程

用户打开 Notebook 后，kernel 初始化按以下顺序执行：

### 主线程初始化（kernel.ts）

```
1. PyodideKernel 构造函数
   ↓
2. initWorker() — 根据 crossOriginIsolated 选择 Worker 类型
   ├─ false → new Worker(comlink.worker.ts) + Comlink.wrap()
   └─ true  → new Worker(coincident.worker.ts) + coincident.proxy()
   ↓
3. this.remote.initialize(options) → 发送初始化消息到 Worker
   ↓
4. 等待 this.ready Promise
```

### Worker 初始化（worker.ts）

Worker 端的 `initialize()` 方法按五个步骤执行（F-330）：

```
1. initRuntime(options)
   ├─ importModule(pyodideUrl) — 动态 import pyodide.mjs
   └─ loadPyodide({ indexUrl, stdin, stdout, stderr, ... })
      ↓
2. initFilesystem(options)
   └─ mountDrive 时挂载 Emscripten DriveFS
      ↓
3. initPackageManager(options)
   ├─ pyodide.pyimport("micropip")
   ├─ pipliteWheelUrl → pyodide.runPythonAsync("import piplite")
   ├─ set piplite_urls
   └─ set disable_pypi_fallback
      ↓
4. initKernel(options)
   ├─ pyodide.runPythonAsync("import ipykernel, comm, jedi")
   ├─ loadPackage("pyodide-kernel")
   └─ pyodide.pyimport("pyodide_kernel")
      ↓
5. initGlobals(options)
   ├─ 从 pyodide.globals 获取 kernel_instance
   ├─ 获取 stdout_stream/stderr_stream（LiteStream）
   ├─ 获取 interpreter（Interpreter 实例）
   └─ 绑定所有回调函数
```

### Python 端初始化（__init__.py）

`import pyodide_kernel` 时在 WASM 中执行（F-108）：

```
1. apply_mocks() — mock termios/fcntl/resource/tornado/pexpect
2. apply_patches() — 设置 matplotlib backend 等
3. 创建 LiteStream（stdout/stderr）
4. LitePythonShellApp.initialize() → 创建 IPython 环境
5. sys.stdout = stdout_stream, sys.stderr = stderr_stream
```

## 代码执行消息流

执行 `execute_request` 时的消息路径：

```
JupyterLab 前端
  │  send("execute_request", { code: "print('hello')" })
  ▼
PyodideKernel.executeRequest()  [主线程]
  │  this.remote.execute(content, parentHeader)
  ▼ (postMessage / proxy)
PyodideRemoteKernel.execute()  [Worker]
  │  kernel.run(code)  [JS → Python 调用]
  ▼
PyodideKernel.run()  [WASM Python]
  │  1. lite_transform_manager.transform_cell(code)
  │     → %pip install → piplite.install()
  │  2. pyodide_js.loadPackagesFromImports(code)
  │  3. interpreter.run_cell(code)
  │     → sys.stdout.write("hello\n")
  │        → stdout_stream.write("hello\n")
  │           → publish_stream_callback("stdout", "hello\n")
  ▼
publish_stream_callback  [Worker JS]
  │  this._parent.send_response({ type: "stream", name: "stdout", text: "hello\n" })
  ▼ (postMessage / proxy)
PyodideKernel._processWorkerMessage()  [主线程]
  │  case "stream": this.stream(...)
  ▼
BaseKernel.stream() → 前端 IOPub 消息
  │
  ▼
JupyterLab 前端显示输出
```

## 两种运行模式对比

### Comlink 模式（非跨源隔离）

```
主线程 ←→ [Comlink.postMessage] ←→ Worker ←→ Pyodide WASM
```

- Worker 类型：`new Worker(comlink.worker.ts)`
- stdin：同步 XMLHttpRequest → Service Worker
- 文件系统：Emscripten MEMFS（内存中，刷新丢失）
- 兼容性：所有现代浏览器
- 限制：Firefox 隐私模式下 DriveFS 不同步（F-078）

### Coincident 模式（跨源隔离）

```
主线程 ←→ [SharedArrayBuffer + Atomics] ←→ Worker ←→ Pyodide WASM
```

- Worker 类型：`new Worker(coincident.worker.ts)`
- stdin：SharedBufferContentsAPI 同步调用
- 文件系统：SharedBufferContentsAPI 提供同步文件系统（F-075）
- 性能：减少 postMessage 序列化开销
- 要求：COOP/COEP HTTP 头

## 关键设计决策

### 为什么用 Worker 而不是主线程直接运行？

1. **不阻塞 UI**：Python 代码执行可能耗时，在 Worker 中运行不阻塞主线程渲染
2. **隔离性**：Pyodide 占用大量内存（WASM 堆），Worker 有独立内存空间
3. **通信规范**：Jupyter kernel 天然是进程隔离模型，Worker 模拟了这种隔离

### 为什么 Python 端内核代码在浏览器中而不是预先编译？

`py/pyodide-kernel/` 中的 Python 代码作为 wheel 包在运行时由 Pyodide 动态 import。这意味着：
1. 可以通过 `%pip install` 安装新的 Python 包
2. 内核逻辑本身也是可替换的
3. 开发时无需重新编译 TypeScript，只需重新打包 wheel

## 下一步

- [Worker 通信模式](03-worker-communication.md) — 深入了解 Comlink vs Coincident
- [构建时 Addon 系统](04-build-addons.md) — 三个 Addon 的详细工作机制
- [消息桥接机制](07-message-bridge.md) — Python↔JS↔前端的消息传递细节

## 源码参考

- [TypeScript Kernel 源码](../references/kernel-ts-source.md)
- [浏览器端 Python Kernel 源码](../references/kernel-py-source.md)
