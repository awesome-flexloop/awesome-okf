---
type: concept
title: "00 - Cockle 简介"
description: Cockle 是什么——浏览器内 bash-like shell 的核心特性、技术栈和适用场景
tags: [introduction, overview, shell, browser, wasm]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: pkg
    resource: /references/shell-api.md
    title: package.json
---

## 什么是 Cockle

Cockle（@jupyterlite/cockle v1.8.0-a0）是一个**运行在浏览器中的 bash-like shell（类 Bash Shell）**，采用 BSD-3-Clause 开源许可证发布 [F-001]。它的定位是在 Web 环境中提供一个完整的命令行交互体验，而无需任何后端服务器或本地安装。

与传统的 Shell（如 Bash、Zsh）不同，Cockle 完全运行在浏览器的沙箱环境中，通过 Web Worker（Web 工作线程）隔离执行，使用 WebAssembly（WASM）技术将经典 Unix 工具编译为浏览器可执行的二进制格式。它不是简单的命令模拟器——而是真正的命令执行环境，拥有独立的虚拟文件系统、进程管道、I/O 重定向和完整的命令解析管线。

传统 Shell 的执行模型依赖操作系统内核提供进程管理、文件系统和系统调用；Cockle 则将这些能力完全映射到浏览器平台：

| 能力 | 传统 Shell | Cockle |
|------|-----------|--------|
| **执行环境** | 操作系统进程 | Web Worker 线程 |
| **文件系统** | 操作系统 FS | Emscripten MEMFS/DriveFS |
| **二进制程序** | ELF/PE 可执行文件 | WebAssembly 模块 |
| **进程间通信** | 操作系统管道（pipe） | 内存中 Pipe 对象 |
| **终端交互** | TTY 设备 | 回调驱动的 IInput/IOutput |
| **系统调用** | 内核 syscall | Emscripten 虚拟系统调用 |

Cockle 是 JupyterLite（Jupyter 的浏览器版本）终端扩展的核心组件 [F-002]，为 JupyterLite 提供了交互式命令行能力，用户可以在浏览器中直接运行 `ls`、`cat`、`grep`、`vim` 等熟悉的 Unix 命令。

## 核心特性

### 四类命令支持

Cockle 支持四种不同类型的命令 [F-003]，覆盖了从内置操作到外部扩展的全部需求：

1. **Builtin TypeScript（内置 TypeScript 命令）**：直接在 Shell 核心中用 TypeScript 实现的内建命令，如 `cd`、`alias`、`exit`、`export`、`history` 等，启动即可用，无需额外下载。
2. **WebAssembly（Emscripten-forge 编译的 WASM 命令）**：通过 Emscripten 编译器将 C/C++ 程序编译为 WASM 模块，在浏览器中以接近原生速度执行。
3. **JavaScript（.js 模块命令）**：纯 JavaScript 编写的命令模块，不含 WASM 二进制，通过动态 `import()` 加载。
4. **External（主线程外部命令）**：运行在浏览器主线程 UI 线程上的命令，通过 ExternalEnvironment 桥接，适合需要操作 DOM 或调用主线程 API 的场景。

### 丰富的 WASM 工具链

Cockle 通过 Emscripten-forge 渠道预编译了大量经典 Unix 工具 [F-004]：

- **coreutils 核心工具集**：`cat`、`cp`、`echo`、`ls`、`mkdir`、`mv`、`rm`、`touch`、`uname`、`wc`
- **版本控制**：`git`（通过 git2cpp 编译）
- **文本处理**：`grep`、`sed`、`less`、`uniq`、`tree`
- **编辑器**：`vim`、`nano`
- **脚本语言**：`lua`

从 v1.4.0 版本开始，Cockle 升级到 Emscripten 4.0.9，并使用 prefix.dev 渠道的 emscripten-forge-4x 包 [F-005]，提供更好的兼容性和性能。

### 管道与 I/O 重定向

Cockle 实现了类 Bash 的管道（`|`）和 I/O 重定向（`>`、`>>`、`<`、`2>`、`2>>`）[F-175][F-176]。命令可以通过管道链式连接，前一个命令的输出直接作为后一个命令的输入，所有数据在内存中流转，无需操作系统介入。重定向支持覆盖写入、追加写入、标准错误重定向等常见模式。

### Tab 自动补全

内置 Tab 补全（Tab Completion）机制 [F-290]，在用户按下 Tab 键时自动补全文件名、命令名和路径。补全逻辑支持文件系统遍历、别名展开和外部命令提供的自定义补全函数。

### 颜色主题支持

Cockle 支持暗色/亮色主题切换，通过 `themeChange(isDark?)` 方法通知主题变更 [F-113]。终端输出可以包含 ANSI 颜色转义序列，在彩色模式（`color: true`）下正确渲染。

### 双 Worker 通信模式

Cockle 提供两种 Worker 通信模式以适应不同的浏览器安全策略 [F-006]：

- **Comlink 模式**（默认端口 4500）：基于 Comlink 库实现的 RPC 通信，不需要 CORS 头，但仅支持 Service Worker 方式的标准输入（stdin）。
- **Coincident 模式**（默认端口 4501）：基于 Coincident 库实现，需要 CORS 头（COOP/COEP），支持 SharedArrayBuffer（SAB）+ Service Worker 双模式的同步 stdin [F-007]。

Worker 类型会根据 `crossOriginIsolated` 属性自动检测 [F-142]——当页面设置了正确的跨域隔离头时自动启用 Coincident 模式以获得最佳性能，否则降级到 Comlink 模式。

## 技术栈

Cockle 的技术栈构建在现代化的前端生态之上：

### 核心语言与编译目标

- **TypeScript**：Shell 核心、命令解析器、IO 系统、Worker 桥接层全部使用 TypeScript 编写，提供类型安全和良好的开发体验。
- **WebAssembly (WASM)**：Unix 工具通过 Emscripten 编译为 WASM，在 Worker 线程中实例化执行，与 TypeScript 核心通过 Emscripten 的 FS 和函数表互操作。

### Worker 通信库

- **Comlink ^4.4.2**：Google 开源的 Worker RPC 库，提供基于 Proxy 的透明 Worker 通信 [F-008]。
- **Coincident ^4.1.1**：支持 SharedArrayBuffer 和 Atomics 的 Worker 通信库，提供同步 I/O 能力 [F-008]。

### 框架依赖

- **Lumino**：Jupyter 生态的基础工具库，Cockle 依赖 `@lumino/coreutils`（工具函数）、`@lumino/disposable`（资源生命周期管理）、`@lumino/signaling`（信号机制）[F-008]。Cockle 的 `IShell` 接口继承自 Lumino 的 `IObservableDisposable`，使用 Lumino 的信号系统实现事件通知。

### 其他依赖

- **deepmerge-ts**：深度合并工具，用于配置合并。
- **zod**：TypeScript 优先的 schema 验证库，用于配置验证。
- **rimraf**：跨平台文件删除工具（构建时使用）。

## 适用场景

### JupyterLite 终端扩展

Cockle 最主要的应用场景是作为 JupyterLite 的终端扩展后端 [F-002]。在 JupyterLite 中，用户打开终端标签页时，Cockle 在 Web Worker 中启动，提供完整的命令行交互体验，与 Jupyter 的文件浏览器和内核系统集成。

### 浏览器端 IDE

任何浏览器端的集成开发环境（IDE）都可以集成 Cockle 作为内置终端，提供命令行工具链支持。开发者可以在浏览器中直接编辑文件、运行代码、使用 Git 版本控制，而无需本地安装任何工具。

### 在线命令行工具与教学平台

Cockle 非常适合用于命令行教学平台、在线 Linux 体验站、交互式教程等场景。学生可以在浏览器中安全地练习 Shell 命令，无需配置虚拟机或担心影响本地系统。WASM 工具集提供了真实的 Unix 命令体验，而非模拟环境。

### 嵌入式命令行面板

Web 应用可以嵌入 Cockle 作为调试面板或管理控制台，供高级用户执行诊断命令、查看文件系统状态、运行维护脚本。External Command 机制允许应用注册自定义命令与 Cockle 交互。

## 与其他方案对比

### vs xterm.js + wasm-shell 方案

xterm.js 是一个优秀的终端模拟器（前端 UI 组件），但它本身不提供 Shell 执行能力——它只是渲染终端输出和捕获键盘输入。常见的组合是 xterm.js + 一个 WASM 编译的 Bash（如 bash-wasm），但这种方案存在几个问题：

| 特性 | xterm.js + bash-wasm | Cockle |
|------|---------------------|--------|
| **Shell 逻辑** | 完整 Bash WASM（体积大） | TypeScript 实现解析/执行，WASM 仅用于单命令 |
| **外部命令扩展** | 需要额外桥接 | 原生支持 External Command 和 JS Command |
| **Worker 模式** | 通常仅单模式 | Comlink/Coincident 双模式自动选择 |
| **包体积** | Bash WASM 通常数 MB | 核心更小，命令按需惰性加载 |
| **Jupyter 集成** | 需要自行适配 | 原生 Lumino 信号/生命周期，JupyterLite 官方组件 |

Cockle 的设计哲学是"Shell 逻辑用 TypeScript，单命令用 WASM"，这使得核心更轻量，扩展更灵活，而不是将整个 Bash 编译为 WASM。

### vs websh / jQuery Terminal

websh、jQuery Terminal 等项目主要提供终端 UI 和简单的命令注册框架，通常不包含真实的文件系统、管道、WASM 命令执行能力。它们更适合做自定义命令的 REPL 界面，而不是 Unix Shell 环境。

### vs 其他浏览器 Shell

| 特性 | Cockle | wasm-shell | browser-shell |
|------|--------|-----------|---------------|
| **真实文件系统** | ✅ MEMFS/DriveFS | ✅ MEMFS | ⚠️ 模拟 |
| **管道/重定向** | ✅ 完整支持 | ⚠️ 有限 | ❌ |
| **WASM 命令集** | ✅ coreutils/git/vim等 | ⚠️ 少量 | ❌ |
| **Tab 补全** | ✅ | ⚠️ | ⚠️ |
| **Worker 隔离** | ✅ Comlink/Coincident | ⚠️ 单模式 | ❌ |
| **外部命令桥接** | ✅ ExternalCommand API | ❌ | ⚠️ |
| **Jupyter 生态** | ✅ 原生集成 | ❌ | ❌ |

Cockle 的独特优势在于：它是唯一一个同时提供完整 Shell 语义（管道、重定向、通配符、别名）、丰富 WASM 工具链、双模式 Worker 通信和主线程命令桥接的浏览器 Shell 方案，且深度集成于 Jupyter 生态。

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [命令系统](/concepts/03-command-system.md)
