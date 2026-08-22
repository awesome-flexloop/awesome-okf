# JupyterLab 源码学习 Wiki

JupyterLab 是 Project Jupyter 的下一代基于 Web 的交互式开发环境，采用 TypeScript + React + Lumino 构建前端，Python（Tornado/Jupyter Server）构建后端。本 Wiki 从源码层面系统讲解 JupyterLab 的架构设计、核心机制和扩展开发。

- **Bundle 版本**：v0.1.0
- **源码版本**：JupyterLab 4.x
- **生成时间**：2026-08-22
- **方法论**：七概念 R→I→E→V→C 五阶段链路 + source-code-to-okf-wiki 工作流

## 快速导航

### 概念文档（按学习路径排序）

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| [00](concepts/00-introduction.md) | 概述与知识地图 | 项目定位、核心特性、架构哲学、章节导航、学习路径 |
| [01](concepts/01-architecture-overview.md) | 整体架构概览 | Monorepo 结构、技术栈、五层架构、前后端通信、核心包依赖链 |
| [02](concepts/02-application-shell.md) | 应用框架与 Shell 布局 | JupyterFrontEnd/JupyterLab 类、LabShell 8 区域、Widget 生命周期、启动流程 |
| [03](concepts/03-plugin-system.md) | 插件系统与依赖注入 | Token、JupyterFrontEndPlugin、激活/停用、DI 机制、通信模式 |
| [04](concepts/04-service-layer.md) | 服务层与后端通信 | ServiceManager、12 个子管理器、REST/WebSocket 通信、Kernel Protocol |
| [05](concepts/05-document-widget-system.md) | 文档注册与 Widget 工厂 | DocumentRegistry、ModelFactory/WidgetFactory、Context、文件类型链 |
| [06](concepts/06-notebook-cells.md) | Notebook 与 Cell 架构 | NotebookPanel/Notebook/Cell 三层结构、Cell 类型、执行流程 |
| [07](concepts/07-extension-ecosystem.md) | 扩展生态系统 | Federated 扩展、Python 扩展管理器、prebuilt/source 扩展、CLI 命令 |
| [08](concepts/08-build-and-modes.md) | 构建系统与运行模式 | Core/Dev/App 三模式、Rspack 构建、jlpm、staging 目录 |
| [09](concepts/09-key-subsystems.md) | 关键子系统 | PageConfig、命令系统、Signal、Disposable、StateDB、Router |

### 实践示例

| 示例 | 标题 | 内容 |
|------|------|------|
| [01](examples/01-minimal-extension.md) | 最小扩展：Hello World 插件 | 创建插件、注册命令、命令面板集成、菜单集成、安装运行 |
| [02](examples/02-custom-file-type.md) | 自定义文件类型：.xyz 查看器 | 注册文件类型、创建 Widget 工厂、自定义 Widget、工具栏配置 |

### 参考资料

| 参考 | 标题 | 内容 |
|------|------|------|
| [01](references/source-code-map.md) | JupyterLab 源码文件地图 | 核心源码文件路径索引、包结构速查表 |

## 三条学习路径

**快速上手（使用者）**：[00](concepts/00-introduction.md) → [01](concepts/01-architecture-overview.md) → [02](concepts/02-application-shell.md)（约 20 分钟）

**扩展开发（前端开发者）**：[00](concepts/00-introduction.md) → [01](concepts/01-architecture-overview.md) → [02](concepts/02-application-shell.md) → [03](concepts/03-plugin-system.md) → [05](concepts/05-document-widget-system.md) → [07](concepts/07-extension-ecosystem.md) → [examples/01](examples/01-minimal-extension.md)（约 50 分钟）

**完整源码（架构师）**：阅读全部 concepts → examples → references（约 80 分钟）

## 更新日志

见 [log.md](log.md)
