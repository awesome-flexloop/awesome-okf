# Pyodide Kernel 概念文档索引

本目录包含 jupyterlite-pyodide-kernel 的核心概念文档，建议按顺序阅读。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | Pyodide Kernel 介绍——是什么、核心特性、版本依赖、项目组成 |
| [01-getting-started.md](01-getting-started.md) | 快速开始——安装方法、构建站点、基本配置、启动预览 |

## 核心概念

| 文档 | 说明 |
|------|------|
| [02-architecture-overview.md](02-architecture-overview.md) | 架构总览——双层架构、三层执行模型、初始化五步流程、消息流路径 |
| [03-worker-communication.md](03-worker-communication.md) | Worker通信模式——Comlink(postMessage) vs Coincident(SharedArrayBuffer)、stdin同步实现、文件系统差异、部署建议 |
| [04-build-addons.md](04-build-addons.md) | 构建时Addon系统——PyodideAddon/PipliteAddon/PyodideLockAddon职责、生命周期钩子、缓存策略 |
| [05-package-management.md](05-package-management.md) | 浏览器端包管理——piplite三级查找策略、%pip魔法拦截、loadPackagesFromImports自动加载、micropip包装关系 |
| [06-python-compatibility.md](06-python-compatibility.md) | Python兼容性层——Mock/Patch/子类化三层适配策略、IPython InteractiveShell适配、LiteStream/LiteDisplay桥接、不支持功能清单 |
| [07-message-bridge.md](07-message-bridge.md) | 消息桥接机制——Python↔JS回调绑定、stream/display/comm/stdin消息类型完整路径、execute_request生命周期 |

## 高级主题

| 文档 | 说明 |
|------|------|
| [08-lockfile-customization.md](08-lockfile-customization.md) | Lockfile定制——pyodide-lock.json结构、PyodideLockAddon配置、UvPipCompile依赖解析、性能优化 |
