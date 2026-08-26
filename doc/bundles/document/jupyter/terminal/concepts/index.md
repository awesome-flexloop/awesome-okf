# JupyterLite Terminal 核心概念

本文档目录包含 JupyterLite Terminal 的核心概念文档，从架构原理到具体实现机制，系统讲解浏览器端终端的工作原理。

## 概念文档列表

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [JupyterLite Terminal简介](00-introduction.md) | 是什么、核心功能、技术栈、shell命令能力、在Jupyter生态中的位置 |
| 01 | [安装与快速开始](01-getting-started.md) | pip安装、jupyter-lite.json配置、构建部署、SAB模式配置、基础使用、常见问题 |
| 02 | [架构概览](02-architecture-overview.md) | 六插件分层架构、整体架构图、核心数据流、双Worker模式、mock-socket关键作用 |
| 03 | [插件系统](03-plugin-system.md) | 6个插件详细职责、激活顺序、依赖注入关系、Token导出、扩展点 |
| 04 | [Shell与Worker机制](04-shell-and-worker.md) | TerminalShell类层级、shell创建流程、Coincident/Comlink双模式详解、Worker构建、shell生命周期 |
| 05 | [无头命令执行](05-headless-exec.md) | HeadlessShellPool设计、4个编程式命令、shell复用vs一次性shell、输出清理、超时机制、错误处理 |
| 06 | [文件系统与Stdin路由](06-drivefs-and-stdin.md) | DriveFS挂载、SAB/SW双模式文件IO路由、ContentsManager注入、交互式命令stdin、文件路径映射 |
| 07 | [主题同步与设置](07-theme-and-settings.md) | 暗色/亮色主题同步两条路径、isAvailable开关、registerAlias/EnvironmentVariable/ExternalCommand全局配置 |
| 08 | [构建系统与扩展开发](08-build-and-extension.md) | TypeScript+Rspack+JupyterBuilder构建流程、Python wheel打包、TerminalAddon WASM复制、开发模式、自定义扩展 |

## 推荐学习路径

### 入门路径（用户）
1. [00-简介](00-introduction.md) → [01-安装与快速开始](01-getting-started.md)
2. 前往[实践示例](/examples/01-basic-terminal-usage.md)体验终端使用

### 深入理解路径（开发者）
1. **理解架构**：[02-架构概览](02-architecture-overview.md) → [03-插件系统](03-plugin-system.md)
2. **核心机制**：[04-Shell与Worker机制](04-shell-and-worker.md) → [06-文件系统与Stdin路由](06-drivefs-and-stdin.md)
3. **编程式API**：[05-无头命令执行](05-headless-exec.md) → [07-主题同步与设置](07-theme-and-settings.md)
4. **构建与扩展**：[08-构建系统与扩展开发](08-build-and-extension.md)
5. **动手实践**：[示例目录](/examples/index.md)中的编程示例

### API速查路径
- 信源文档提供了完整的API签名和源码映射，参见[信源参考](/references/index.md)

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-plugin-system
04-shell-and-worker
05-headless-exec
06-drivefs-and-stdin
07-theme-and-settings
08-build-and-extension
```
