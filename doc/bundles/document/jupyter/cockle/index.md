---
type: OKF
title: Cockle 教程
description: Cockle（@jupyterlite/cockle v1.8.0-a0）浏览器内 bash-like Shell 的完整教程——架构解析、命令系统、WASM命令、Worker通信和集成实践
tags: [cockle, jupyterlite, shell, browser, wasm, terminal, web-worker]
version: 1.8.0-a0
source: https://github.com/jupyterlite/cockle
demo: https://jupyterlite.github.io/cockle
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# Cockle 浏览器 Shell 教程

Cockle 是一个运行在浏览器中的类 bash Shell（Shell），通过 TypeScript 实现核心 Shell 逻辑，并使用 WebAssembly（WASM）运行通过 Emscripten 编译的 Unix 命令（如 ls、cat、git、vim 等）。它是 JupyterLite 终端扩展的底层引擎。

Cockle 将所有命令执行隔离在 Web Worker 中，支持 SharedArrayBuffer（SAB）或 Service Worker（SW）两种同步 stdin 方案，让 WASM 程序可以在浏览器中实现真正的阻塞式输入输出。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-简介](concepts/00-introduction.md) — Cockle 是什么、核心特性、技术栈、适用场景
- [01-快速开始](concepts/01-getting-started.md) — 安装、前置条件、创建第一个 Shell
- [02-架构总览](concepts/02-architecture-overview.md) — 三层架构、数据流、初始化序列
- [03-命令系统](concepts/03-command-system.md) — ICommandRunner 接口、四种命令类型、惰性加载
- [04-命令解析管线](concepts/04-parsing-pipeline.md) — Tokenizer、Parser、别名展开、AST、重定向
- [05-IO 系统](concepts/05-io-system.md) — IInput/IOutput 接口、终端/文件/管道 IO
- [06-文件系统](concepts/06-filesystem.md) — MEMFS、PROXYFS、DriveFS 浏览器持久化
- [07-缓冲 IO 系统](concepts/07-buffered-io.md) — SAB 零延迟 stdin、Service Worker stdin
- [08-内置命令详解](concepts/08-builtin-commands.md) — 12 个内置命令用法
- [09-外部命令](concepts/09-external-commands.md) — 主线程命令注册、IRunContext、Tab 补全
- [10-WASM 与 JS 命令](concepts/10-wasm-js-commands.md) — cockle-config.json、Emscripten-forge 包
- [11-Worker 通信机制](concepts/11-worker-communication.md) — Comlink vs Coincident、跨域部署

### [实践示例](examples/index.md)
- [01-创建基本 Shell](examples/01-basic-shell.md) — 完整的 Shell 创建和命令执行示例
- [02-使用命令](examples/02-using-commands.md) — 管道、重定向、别名、环境变量
- [03-注册外部命令](examples/03-external-command.md) — 自定义主线程命令和浏览器 API 集成
- [04-自定义命令配置](examples/04-custom-config.md) — cockle-config.json 配置 WASM/JS 命令包
- [05-Tab 补全与交互增强](examples/05-tab-completion.md) — 自定义补全、状态监听、尺寸同步、主题切换

### [信源参考](references/index.md)
- [Shell API 参考](references/shell-api.md) — IShell、Shell、IOptions 完整 API
- [命令系统源码参考](references/command-source.md) — CommandRegistry、ICommandRunner 等 API
- [解析器源码参考](references/parser-source.md) — Tokenizer、Parser、AST 节点
- [IO 系统源码参考](references/io-source.md) — IInput/IOutput 接口族
- [内置命令源码参考](references/builtin-source.md) — 12 个内置命令类结构
- [Worker 通信参考](references/worker-source.md) — BaseShellWorker 及子类 API
- [缓冲 IO 参考](references/buffered-io-source.md) — SAB 和 SW 缓冲 IO 实现 API
- [配置与环境参考](references/config-source.md) — Environment、Aliases、cockle-config.json 格式
- [事实清单](facts.md) — 从源码采集的 334 条零推测事实
- [架构洞察](insights.md) — 5 个核心洞察四元组与知识地图

## 🚀 快速开始

```bash
npm install @jupyterlite/cockle
```

创建最简单的 Shell：

```typescript
import { Shell } from '@jupyterlite/cockle';

const shell = new Shell({
  baseUrl: '/',
  wasmBaseUrl: '/cockle-assets/',
  outputCallback: (output: string) => {
    terminal.write(output);
  },
  browsingContextId: 'my-shell'
});

await shell.start();
await shell.input('ls -la\n');
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🖥️ 四类命令 | Builtin TypeScript、WebAssembly（Emscripten-forge）、JavaScript 模块、主线程外部命令 |
| 🔧 WASM 工具链 | coreutils、git、grep、vim、nano、less、sed、tree、lua 等 Unix 命令 |
| 🔗 管道与重定向 | 支持 `\|` 管道、`>`/`>>`/`2>`/`2>>`/`<` 五种重定向 |
| 📁 虚拟文件系统 | Emscripten MEMFS + PROXYFS 代理挂载，支持浏览器持久存储 |
| ⚡ 双 Worker 模式 | Comlink（无需跨域头）和 Coincident（SAB 零延迟 stdin）自动选择 |
| 📡 双 stdin 方案 | SharedArrayBuffer（Atomics 同步）和 Service Worker（fetch 拦截）自动检测 |
| 🎨 彩色终端 | 支持 ANSI 颜色、Tab 补全、命令历史、深色/浅色主题 |
| 🔌 可扩展 | 外部命令 API 支持自定义主线程命令、Tab 补全、DOM/浏览器 API 集成 |

## 📖 推荐学习路径

1. **入门了解**：阅读 [00-简介](concepts/00-introduction.md) 和 [01-快速开始](concepts/01-getting-started.md)
2. **动手实践**：跟着 [01-创建基本 Shell](examples/01-basic-shell.md) 跑通第一个示例
3. **理解架构**：学习 [02-架构总览](concepts/02-architecture-overview.md) 理解三层结构
4. **掌握核心**：深入 [03-命令系统](concepts/03-command-system.md)、[04-解析管线](concepts/04-parsing-pipeline.md)、[05-IO 系统](concepts/05-io-system.md)
5. **子系统深入**：学习 [06-文件系统](concepts/06-filesystem.md)、[07-缓冲 IO](concepts/07-buffered-io.md)、[08-内置命令](concepts/08-builtin-commands.md)
6. **高级扩展**：掌握 [09-外部命令](concepts/09-external-commands.md)、[10-WASM/JS 命令](concepts/10-wasm-js-commands.md)、[11-Worker 通信](concepts/11-worker-communication.md)

## 📊 架构概览

```
┌──────────────────────────────────────────────────────────┐
│                    浏览器主线程                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Shell extends BaseShell                           │  │
│  │  - outputCallback / input()                        │  │
│  │  - Worker 生命周期管理                              │  │
│  │  - External Command 桥接 (callExternalCommand)      │  │
│  │  - SharedArrayBuffer / Service Worker IO (Main)    │  │
│  └───────────┬────────────────────────┬───────────────┘  │
│              │ Comlink.postMessage    │ Coincident.proxy │
│              │ (序列化)               │ (直接属性赋值)    │
├──────────────┼────────────────────────┼──────────────────┤
│              ▼                        ▼                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Web Worker 线程                                    │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │  BaseShellWorker                             │  │  │
│  │  │  - 回调桥接 → ShellImpl                      │  │  │
│  │  │  - WorkerIO 创建 (SAB/SW)                    │  │  │
│  │  └──────────────────┬───────────────────────────┘  │  │
│  │                     ▼                              │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │  ShellImpl (核心执行引擎)                      │  │  │
│  │  │  - Tokenizer + Parser → AST                  │  │  │
│  │  │  - CommandRegistry → ICommandRunner          │  │  │
│  │  │  - Builtin/WASM/JS 命令执行                   │  │  │
│  │  │  - Pipe / Redirect IO 组装                    │  │  │
│  │  │  - Emscripten FS (MEMFS + PROXYFS)           │  │  │
│  │  │  - Tab 补全 / 历史记录 / 别名                  │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## 🔗 外部资源

- **GitHub 仓库**：[jupyterlite/cockle](https://github.com/jupyterlite/cockle)
- **在线 Demo**：[jupyterlite.github.io/cockle](https://jupyterlite.github.io/cockle)
- **JupyterLite 终端**：[jupyterlite/terminal](https://github.com/jupyterlite/terminal)
- **Emscripten-forge**：[prefix.dev 频道](https://prefix.dev/channels/emscripten-forge)
- **Comlink**：[GoogleChromeLabs/comlink](https://github.com/GoogleChromeLabs/comlink)
- **Coincident**：[WebReflection/coincident](https://github.com/WebReflection/coincident)

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
