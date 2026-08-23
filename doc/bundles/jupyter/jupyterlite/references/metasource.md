---
type: Reference
title: JupyterLite 项目元信源
description: JupyterLite 项目整体信息、源码版本、目录结构与核心模块清单
tags: [meta, source, project, jupyterlite]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyterlite-repo
    resource: https://github.com/jupyterlite/jupyterlite
    title: JupyterLite GitHub Repository
---

## 源码位置

本地检出路径：`d:\spaces\SpecWeave\external\libs\jupyter\jupyterlite`

## 版本信息

| 属性 | 值 |
|------|-----|
| Git Commit | `cf4958fcd20763a61ce4c7eeb1394f3c60e16cb0` |
| Commit Message | Fix outdated content in the extension docs (#2031) |
| 仓库地址 | https://github.com/jupyterlite/jupyterlite |
| 包管理 | npm workspaces (monorepo) + Python pyproject.toml |

## 顶层目录结构

| 目录 | 用途 |
|------|------|
| `app/` | 前端应用（Lab/Notebook/REPL/Consoles/Edit/Tree/Doc）构建配置与静态资源 |
| `packages/` | TypeScript 核心包（services/kernel/contents/application等） |
| `py/` | Python 工具链（jupyterlite-core 构建系统、jupyterlite CLI） |
| `docs/` | 官方文档（Sphinx/MyST） |
| `scripts/` | 构建与发布脚本 |
| `binder/` | Binder 配置 |

## 前端应用（app/）

| 应用 | 路径 | 说明 |
|------|------|------|
| Lab | `app/lab/` | 完整 JupyterLab 体验 |
| Notebook | `app/notebooks/` | Notebook 经典界面 |
| REPL | `app/repl/` | 交互式 REPL 环境 |
| Consoles | `app/consoles/` | 控制台界面 |
| Edit | `app/edit/` | 文本编辑器 |
| Tree | `app/tree/` | 文件浏览器 |
| Doc | `app/doc/` | 文档查看器 |

## TypeScript 包（packages/）

| 包名 | 说明 | 状态 |
|------|------|------|
| `@jupyterlite/services` | 核心服务：内核通信、内容管理、Session、设置、NBConvert | ✅ 主包 |
| `@jupyterlite/kernel` | 内核相关组件（已废弃，shim 重导出自 services） | ⚠️ Deprecated (0.8.0移除) |
| `@jupyterlite/contents` | 内容相关组件（已废弃，shim 重导出自 services） | ⚠️ Deprecated (0.8.0移除) |
| `@jupyterlite/application` | 应用框架基类 | ✅ 核心 |
| `@jupyterlite/application-extension` | 应用扩展点 | ✅ 核心 |
| `@jupyterlite/apputils` | 应用工具函数 | ✅ |
| `@jupyterlite/apputils-extension` | 工具扩展 | ✅ |
| `@jupyterlite/localforage` | LocalForage 封装（IndexedDB存储） | ✅ |
| `@jupyterlite/notebook-application-extension` | Notebook应用扩展 | ✅ |
| `@jupyterlite/repl-extension` | REPL扩展 | ✅ |
| `@jupyterlite/server` | 浏览器端服务器模拟 | ✅ |
| `@jupyterlite/services-extension` | 服务扩展 | ✅ |
| `@jupyterlite/session` | 会话管理 | ✅ |
| `@jupyterlite/settings` | 设置管理 | ✅ |
| `@jupyterlite/types` | TypeScript 类型定义 | ✅ |
| `@jupyterlite/ui-components` | UI 组件库 | ✅ |
| `@jupyterlite/_metapackage` | 元包 | - |

## Python 包（py/）

| 包名 | 路径 | 说明 |
|------|------|------|
| `jupyterlite-core` | `py/jupyterlite-core/` | 核心构建系统（LiteManager + doit任务 + Addon插件体系） |
| `jupyterlite` | `py/jupyterlite/` | CLI 入口与用户接口 |

## @jupyterlite/services 子模块

| 子模块 | 核心导出 |
|--------|----------|
| `contents/` | `DriveFS`, `ContentsAPI`, `ServiceWorkerContentsAPI`, `DriveFSEmscriptenStreamOps`, `DriveFSEmscriptenNodeOps`, `BrowserStorageDrive`, `SiteDrive` |
| `kernel/` | `BaseKernel`, `LiteKernelClient`, `LiteKernelSpecClient`, `KernelSpecs` |
| `session/` | `SessionContext` 等会话管理 |
| `settings/` | 设置存储 |
| `nbconvert/` | Notebook 导出 |

## 关键架构特征

1. **浏览器端全栈**：内核（Pyodide/Xeus Python）运行在 Web Worker 中
2. **Service Worker 桥接**：Worker 内 Emscripten 文件系统通过同步 XHR 请求主线程内容管理器
3. **Emscripten FS 模拟**：实现 Emscripten NodeOps/StreamOps 接口，桥接到 IndexedDB 存储
4. **LocalForage 持久化**：使用 IndexedDB 存储 Notebook 和文件，支持离线
5. **JupyterLab 组件复用**：大量复用 @jupyterlab 包（services、coreutils、lumino等）
6. **Doit 构建系统**：Python 端使用 doit 任务框架 + Addon 插件体系构建静态站点
