---
type: Concept
title: 双语言分层架构
description: jupyterlite-xeus的Python构建时+TypeScript运行时双语言分层，以及xeus-core/xeus/xeus-extension三层抽象基类设计
tags: [architecture, design, abstraction, layering, python, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: insight-2
    resource: /concepts/02-architecture.md
    title: 洞察I-2 双语言分层
  - id: insight-3
    resource: /concepts/02-architecture.md
    title: 洞察I-3 三层抽象
  - id: kernel-base
    resource: /references/kernel-base-source.md
    title: xeus-core基类参考
  - id: kernel-impl
    resource: /references/kernel-impl-source.md
    title: xeus具体实现参考
---

## 架构全景

jupyterlite-xeus 采用**时态分层**架构——Python 和 TypeScript 各司其职，在不同阶段运行：

```
┌─────────────────────────────────────────────────────┐
│                    构建时 (Build Time)                │
│  ┌───────────────────────────────────────────────┐  │
│  │  Python 端 (jupyterlite_xeus/)                 │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────┐ │  │
│  │  │ XeusAddon   │  │ create_conda │  │ _pip  │ │  │
│  │  │ (post_build)│→ │ _env.py      │  │ .py   │ │  │
│  │  └──────┬──────┘  └──────┬───────┘  └───┬───┘ │  │
│  │         │ 下载micromamba  │ 创建wasm32    │ 处理 │  │
│  │         │ 调度构建流程    │ conda环境     │ pip  │  │
│  │         ↓                ↓              ↓     │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │  empack 打包 → 静态文件输出 (_output/)   │  │  │
│  │  │  - WASM 内核二进制 (.js/.wasm/.data)     │  │  │
│  │  │  - conda包 tar.gz (kernel_packages/)     │  │  │
│  │  │  - kernels.json / kernel.json            │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                          ↓ 部署到静态文件服务器
┌─────────────────────────────────────────────────────┐
│                   运行时 (Runtime - Browser)         │
│  ┌───────────────────────────────────────────────┐  │
│  │  主线程 (Main Thread)                         │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │ xeus-extension (JupyterLab插件)         │  │  │
│  │  │ - kernelPlugin: 注册内核规格            │  │  │
│  │  │ - 加载kernel.json/kernels.json          │  │  │
│  │  └────────────────┬────────────────────────┘  │  │
│  │                   ↓ 创建                       │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │ WebWorkerKernel (xeus包)                │  │  │
│  │  │ - 继承WebWorkerKernelBase               │  │  │
│  │  │ - 创建Worker (coincident/comlink)       │  │  │
│  │  │ - 转发Jupyter消息 ↔ Worker              │  │  │
│  │  └────────────────┬────────────────────────┘  │  │
│  └───────────────────┼───────────────────────────┘  │
│                      ↓ postMessage/SharedArrayBuffer│
│  ┌───────────────────┼───────────────────────────┐  │
│  │  Web Worker       ↓                           │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │ XeusCoincidentKernel / XeusComlinkKernel│  │  │
│  │  │ - 继承EmpackedXeusRemoteKernel          │  │  │
│  │  │ - 加载WASM模块 (createXeusModule)       │  │  │
│  │  │ - 初始化Emscripten FS                   │  │  │
│  │  │ - 挂载DriveFS/SharedBufferContentsAPI   │  │  │
│  │  │ - 调用C++内核(xkernel.start())          │  │  │
│  │  │ - 处理mambajs动态包管理                 │  │  │
│  │  └────────────────┬────────────────────────┘  │  │
│  │                   ↓ Emscripten/Module         │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │ WASM 内核 (C++ xeus编译产物)             │  │  │
│  │  │ - xeus-python / xeus-lua / xeus-r 等    │  │  │
│  │  │ - 执行用户代码、管理解释器状态           │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## 时态分层原则

| 阶段 | 语言 | 职责 | 执行环境 | 产出物 |
|------|------|------|---------|--------|
| **构建时** | Python | conda环境创建、empack打包、内核文件复制、kernels.json生成 | 开发机/CI（有Python+micromamba） | 静态文件目录 |
| **运行时** | TypeScript + WASM | WASM加载、文件系统桥接、消息转发、动态包管理 | 浏览器 | 用户交互体验 |

**关键约束**：构建产物中不包含Python代码（WASM内核内部的Python解释器除外）。这意味着最终部署的站点是纯静态文件——没有CGI、没有WSGI、没有后端Python进程。

## 三层TypeScript抽象

TypeScript端采用严格的三层抽象，每层职责明确：

```
┌─────────────────────────────────────────────────────┐
│ Layer 3: xeus-extension (JupyterLab集成层)           │
│ 文件: packages/xeus-extension/src/index.ts          │
│ 职责: JupyterLab插件注册、kernelSpec提供、日志管理   │
│ 类: kernelPlugin / XeusLogManager / EmpackEnvMeta   │
└──────────────────────┬──────────────────────────────┘
                       ↓ 实例化
┌──────────────────────┴──────────────────────────────┐
│ Layer 2: xeus (具体实现层 - empack + mambajs)        │
│ 文件: packages/xeus/src/kernel.ts, worker.ts        │
│ 职责: 具体的empack打包内核实现、Worker创建、双模式    │
│ 类: WebWorkerKernel / EmpackedXeusRemoteKernel      │
└──────────────────────┬──────────────────────────────┘
                       ↓ 继承
┌──────────────────────┴──────────────────────────────┐
│ Layer 1: xeus-core (抽象基类层)                      │
│ 文件: packages/xeus-core/src/kernel.base.ts等       │
│ 职责: 定义接口契约、通用消息处理逻辑、日志基类        │
│ 类: WebWorkerKernelBase / XeusRemoteKernelBase      │
│     IXeusWorkerKernel / XeusWorkerLoggerBase        │
└─────────────────────────────────────────────────────┘
```

### Layer 1: xeus-core（抽象基类）

定义**与具体通信机制无关**的核心契约：

- [WebWorkerKernelBase](../references/kernel-base-source.md#webworkerkernelbase-类)：主线程内核基类，实现通用的消息转发、Worker生命周期管理，声明抽象方法 `initWorker()` 和 `createRemote()`
- [XeusRemoteKernelBase](../references/kernel-base-source.md#xeusremotekernelbase-类)：Worker端内核基类，实现通用的初始化流程（initialize()），声明8个抽象方法（initializeModule/FileSystem/Interpreter/Stdin/mount/install/uninstall/listInstalledPackages）
- [IXeusWorkerKernel](../references/kernel-base-source.md#ixeusworkerkernel-接口)：Worker端接口，定义所有Worker必须实现的方法签名
- XeusWorkerLoggerBase：基于BroadcastChannel的日志基类

### Layer 2: xeus（empack具体实现）

基于xeus-core抽象层，实现empack+mambajs方案：

- [WebWorkerKernel](../references/kernel-impl-source.md#webworkerkernel-类)：实现 `initWorker()`（根据crossOriginIsolated选择coincident/comlink Worker）和 `createRemote()`（创建coincident或comlink代理）
- [EmpackedXeusRemoteKernel](../references/kernel-impl-source.md#empackedxuesremoterkernel-类)：实现所有8个抽象方法——WASM模块加载、empack环境bootstrap、Python解释器初始化、双模式挂载/stdlib（由子类实现mount/initializeStdin）、mambajs包管理
- XeusCoincidentKernel / XeusComlinkKernel：继承EmpackedXeusRemoteKernel，仅实现差异部分（mount、initializeStdin、storeAsGlobal、callGlobalReceiver）

### Layer 3: xeus-extension（JupyterLab集成）

将内核注册到JupyterLab：

- kernelPlugin：fetch kernels.json/kernel.json → 构造KernelSpec → 注册到IKernelSpecs
- XeusLogManager：管理BroadcastChannel日志通道
- EmpackEnvMetaManager：缓存和提供empack环境元数据

## 扩展点设计

三层抽象使得扩展方式清晰：

| 扩展需求 | 修改层次 | 示例 |
|---------|---------|------|
| 新打包格式（不用empack） | Layer 2：新的RemoteKernel继承XeusRemoteKernelBase | 支持其他WASM包分发方案 |
| 新通信机制 | Layer 2：新的Worker入口类+Kernel子类 | 如未来使用Atomics.wait API |
| 新语言内核 | Layer 3：只需提供正确编译的WASM二进制和kernel.json | xeus-python/xeus-lua都是这样接入的 |
| JupyterLab集成定制 | Layer 3：修改插件注册逻辑 | 自定义内核图标、额外的JupyterLab命令 |

## 设计模式

| 模式 | 应用位置 | 作用 |
|------|---------|------|
| **模板方法** | XeusRemoteKernelBase.initialize() | 定义固定的初始化流程骨架，子类实现各步骤 |
| **抽象工厂** | WebWorkerKernelBase.initWorker()/createRemote() | 子类决定创建哪种Worker和代理 |
| **策略模式** | coincident vs comlink Worker | 运行时根据环境选择通信策略 |
| **代理模式** | coincident/comlink wrap | 主线程通过代理透明调用Worker方法 |

## 与 pyodide-kernel 的对比

jupyterlite-pyodide-kernel 采用单层设计——所有逻辑（Pyodide加载、包管理、文件系统）都硬编码在一个类中。而 xeus 的三层抽象使得：

1. **多内核复用**：xeus-python/xeus-lua/xeus-r 共享同一套TypeScript集成层，只需替换WASM二进制
2. **通信机制可替换**：coincident/comlink是策略选择，不是硬编码
3. **打包格式可替换**：empack是一种实现，不是唯一选择

## 相关API

- [xeus-core 基类API](../references/kernel-base-source.md)
- [xeus empack实现API](../references/kernel-impl-source.md)
- [双Worker模式实现](../references/worker-modes-source.md)
- [扩展注册API](../references/extension-source.md)

## 相关概念

- [双Worker通信模式](03-dual-worker-modes.md)
- [内核生命周期](04-kernel-lifecycle.md)
- [构建系统](05-build-system.md)
