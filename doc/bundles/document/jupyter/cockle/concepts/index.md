# Cockle 概念文档索引

本目录包含 Cockle 浏览器 Shell 的核心概念文档，建议按编号顺序阅读。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | Cockle 是什么——核心特性、技术栈、适用场景与方案对比 |
| [01-getting-started.md](01-getting-started.md) | 安装 Cockle、创建第一个 Shell 实例、发送命令和接收输出 |

## 核心架构

| 文档 | 说明 |
|------|------|
| [02-architecture-overview.md](02-architecture-overview.md) | 三层 Shell 架构：主线程 Shell → Worker 通信层 → ShellImpl 执行引擎 |
| [03-command-system.md](03-command-system.md) | ICommandRunner 接口、四种命令类型、CommandRegistry 注册与查找、惰性加载 |
| [04-parsing-pipeline.md](04-parsing-pipeline.md) | Tokenizer 词法分析、Parser 语法分析、别名展开、AST 构建、管道与重定向 |
| [05-io-system.md](05-io-system.md) | IInput/IOutput 接口族：终端IO、文件IO、管道、重定向实现 |

## 核心子系统

| 文档 | 说明 |
|------|------|
| [06-filesystem.md](06-filesystem.md) | Emscripten MEMFS 内存文件系统、PROXYFS 代理挂载、DriveFS 浏览器持久存储 |
| [07-buffered-io.md](07-buffered-io.md) | SharedArrayBuffer 零延迟 stdin 与 Service Worker 异步 stdin 的原理与切换 |
| [08-builtin-commands.md](08-builtin-commands.md) | 12 个内置 TypeScript 命令的完整用法详解 |

## 高级主题

| 文档 | 说明 |
|------|------|
| [09-external-commands.md](09-external-commands.md) | 主线程外部命令的注册、IRunContext 接口、Tab 补全和跨线程桥接 |
| [10-wasm-js-commands.md](10-wasm-js-commands.md) | WASM/JS 命令包配置、cockle-config.json 格式、Emscripten-forge 编译要求 |
| [11-worker-communication.md](11-worker-communication.md) | Comlink 与 Coincident 两种 Worker 通信模式的对比和选择策略 |

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-command-system
04-parsing-pipeline
05-io-system
06-filesystem
07-buffered-io
08-builtin-commands
09-external-commands
10-wasm-js-commands
11-worker-communication
```
