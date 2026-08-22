# 核心概念

本章节系统讲解 JupyterLab Desktop v4.6.x 的核心概念，分为入门、核心、进阶三个层次。

## 📘 入门

| 文档 | 简介 |
|------|------|
| [00 - JupyterLab Desktop 简介](00-introduction.md) | 了解 JupyterLab Desktop 是什么、核心特性、技术栈与应用架构总览。 |
| [01 - 架构概览](01-architecture-overview.md) | 理解核心模块组成、模块依赖关系、关键设计模式（Factory/Singleton/双层设置/Signal/IDisposable）与数据流。 |

## 📗 核心

| 文档 | 简介 |
|------|------|
| [02 - 应用入口与生命周期](02-app-entry-lifecycle.md) | 掌握从进程启动到就绪的完整流程：Snap 路径修复、单实例锁、CLI 参数解析、捆绑环境更新、应用启动序列。 |
| [03 - 会话窗口系统](03-session-window-system.md) | 理解 SessionWindow 与 SessionWindowManager、窗口创建/布局/关闭流程、内容视图切换、标题栏与进度视图。 |
| [04 - Jupyter 服务器管理](04-server-management.md) | 深入 JupyterServer 启停机制、启动脚本生成、端口检测、token 生成、自动重启、Factory 预创建与服务器池复用。 |
| [05 - Python 环境管理](05-python-env-management.md) | 掌握环境类型（conda/venv/system/WindowsReg）、Registry 自动发现机制、环境验证、创建与激活流程。 |
| [06 - 设置与配置系统](06-settings-config.md) | UserSettings/WorkspaceSettings 双层设置系统、SettingType 枚举、默认值与覆盖机制、服务器启动参数配置。 |
| [07 - CLI 命令系统](07-cli-system.md) | jlab 命令完整用法、全局选项、env/config/appdata/logs 子命令、环境创建与激活、设置管理。 |

## 📙 进阶

| 文档 | 简介 |
|------|------|
| [08 - 事件与IPC系统](08-event-ipc-system.md) | EventTypeMain/EventTypeRenderer 枚举、EventManager 异步/同步事件处理、IPC 通信机制与安全校验。 |
| [09 - 安全与导航策略](09-security-navigation.md) | 三层导航安全架构、WebContents 声明模式、外部链接处理、WebView 阻止、GetServerInfo origin 校验。 |
| [10 - 多窗口与会话管理](10-multi-window-multisession.md) | 多窗口架构、窗口位置偏移算法、会话持久化与恢复、最近会话列表、远程会话持久化。 |
| [11 - 构建与开发指南](11-build-development.md) | 项目结构、关键依赖版本、开发环境搭建、electron-builder 打包配置、添加新功能指南。 |

---

**导航：**
- [示例文档](../examples/index.md) — 实战操作示例
- [源码信源](../references/index.md) — 源码信源文档
- [返回首页](../index.md)
