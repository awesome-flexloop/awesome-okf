# JupyterLite 核心概念

本文档目录包含 JupyterLite 的核心概念文档，从架构原理到具体实现机制。

## 概念文档列表

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [JupyterLite简介](00-introduction.md) | 是什么、核心特性、与传统Jupyter的区别、技术栈 |
| 01 | [整体架构](01-architecture-overview.md) | 三层线程模型、关键数据流、核心设计决策 |
| 02 | [内核系统](02-kernel-system.md) | BaseKernel基类、消息路由、LiteKernelClient、mock-socket桥接 |
| 03 | [内容管理与文件系统](03-contents-and-filesystem.md) | BrowserStorageDrive、DriveFS、Emscripten FS桥接、格式转换 |
| 04 | [Service Worker桥接](04-service-worker-bridge.md) | Service Worker双重角色、同步XHR桥接机制、离线缓存 |
| 05 | [浏览器存储](05-browser-storage.md) | LocalForage三store设计、检查点系统、服务器文件分层 |
| 06 | [Python构建系统](06-build-system.md) | LiteManager、Doit任务框架、Addon插件体系 |
| 07 | [内核类型](07-kernel-types.md) | Pyodide vs Xeus内核、文件系统挂载、JS互操作 |
| 08 | [扩展架构](08-extension-architecture.md) | JupyterLab插件系统、Token/Provider、内核扩展点、Content Provider |

## 推荐学习路径

1. **入门**：[00-简介](00-introduction.md) → [01-整体架构](01-architecture-overview.md)
2. **理解核心机制**：[02-内核系统](02-kernel-system.md) → [03-内容管理与文件系统](03-contents-and-filesystem.md) → [04-Service Worker桥接](04-service-worker-bridge.md)
3. **存储与持久化**：[05-浏览器存储](05-browser-storage.md)
4. **构建与部署**：[06-Python构建系统](06-build-system.md)
5. **扩展开发**：[07-内核类型](07-kernel-types.md) → [08-扩展架构](08-extension-architecture.md)

```{toctree}
:maxdepth: 7

00-introduction
01-architecture-overview
02-kernel-system
03-contents-and-filesystem
04-service-worker-bridge
05-browser-storage
06-build-system
07-kernel-types
08-extension-architecture
```
