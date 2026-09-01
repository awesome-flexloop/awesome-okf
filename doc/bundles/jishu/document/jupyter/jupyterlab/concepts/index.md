# 概念文档索引

本目录包含 JupyterLab 源码学习的核心概念文档，按学习路径编号排列（00-09）。

## 学习路径建议

建议按编号顺序阅读：00（概述）→ 01（架构）→ 02（应用框架）→ 03（插件系统）→ ... → 09（子系统）

## 文档列表

| 编号 | 文档 | 主题领域 | 前置阅读 |
|------|------|---------|---------|
| 00 | [00-introduction.md](00-introduction.md) | 概述、特性、架构哲学、导航 | 无 |
| 01 | [01-architecture-overview.md](01-architecture-overview.md) | 架构概览、Monorepo、分层模型 | 00 |
| 02 | [02-application-shell.md](02-application-shell.md) | JupyterFrontEnd、LabShell、启动流程 | 01 |
| 03 | [03-plugin-system.md](03-plugin-system.md) | 插件、Token、DI、激活机制 | 02 |
| 04 | [04-service-layer.md](04-service-layer.md) | ServiceManager、后端通信、Kernel | 01 |
| 05 | [05-document-widget-system.md](05-document-widget-system.md) | DocumentRegistry、WidgetFactory、Context | 03, 04 |
| 06 | [06-notebook-cells.md](06-notebook-cells.md) | Notebook、Cell、NotebookActions | 05 |
| 07 | [07-extension-ecosystem.md](07-extension-ecosystem.md) | Federated 扩展、扩展管理器 | 03 |
| 08 | [08-build-and-modes.md](08-build-and-modes.md) | 构建系统、运行模式、staging | 07 |
| 09 | [09-key-subsystems.md](09-key-subsystems.md) | PageConfig、命令、Signal、StateDB | 02 |

## 返回导航

- [返回首页](../index.md)
- [示例文档](../examples/index.md)
- [参考资料](../references/index.md)

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-architecture-overview
02-application-shell
03-plugin-system
04-service-layer
05-document-widget-system
06-notebook-cells
07-extension-ecosystem
08-build-and-modes
09-key-subsystems
```
