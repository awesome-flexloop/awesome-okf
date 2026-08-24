---
type: Index
title: jupyterlite-xeus 教程
description: jupyterlite-xeus v5.0.0 完整教程——从快速入门到自定义内核开发，系统讲解浏览器端xeus WASM内核的架构、机制与实践
tags: [jupyterlite, xeus, wasm, kernel, jupyter, webassembly, browser]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-repo
    resource: /index.md
    title: https://github.com/jupyterlite/xeus v5.0.0
---

# jupyterlite-xeus 教程

> 版本：v5.0.0 | 源码：[jupyterlite/xeus](https://github.com/jupyterlite/xeus) | 许可证：BSD-3-Clause

jupyterlite-xeus 是 JupyterLite 的 xeus 内核集成，将基于 C++ xeus 框架的 Jupyter 内核编译为 WebAssembly，在浏览器内运行支持 Python/Lua/R/C++ 等多语言的交互式计算环境——无需后端服务器，纯静态部署即可使用。

## 🚀 快速开始

| 主题 | 说明 |
|------|------|
| [jupyterlite-xeus 是什么](concepts/00-introduction.md) | 项目定位、核心能力、支持的内核语言 |
| [快速开始](concepts/01-getting-started.md) | 安装→构建→预览→部署的完整入门流程 |
| [基础部署示例](examples/basic-deploy.md) | 15分钟搭建第一个xeus JupyterLite站点 |

## 🏗️ 核心概念

| 主题 | 难度 | 说明 |
|------|------|------|
| [双语言分层架构](concepts/02-architecture.md) | ⭐⭐ | Python构建时+TS运行时的时态分层、三层抽象基类设计 |
| [双Worker通信模式](concepts/03-dual-worker-modes.md) | ⭐⭐ | coincident（SharedArrayBuffer同步）vs comlink（postMessage异步）的自适应切换机制 |
| [内核生命周期](concepts/04-kernel-lifecycle.md) | ⭐⭐⭐ | 从插件激活→Worker创建→WASM加载→消息循环的完整生命周期 |
| [构建系统详解](concepts/05-build-system.md) | ⭐⭐ | micromamba环境创建、empack打包、产物目录结构 |
| [浏览器内包管理](concepts/06-package-management.md) | ⭐⭐⭐ | mambajs+empack实现%conda/%pip动态安装、限制与最佳实践 |
| [文件系统桥接](concepts/07-filesystem-bridge.md) | ⭐⭐⭐ | Emscripten MEMFS、DriveFS/SharedBufferContentsAPI、三层FS架构 |
| [JupyterLab扩展注册](concepts/08-extension-registration.md) | ⭐⭐ | Token DI、kernelPlugin注册、日志与环境元数据服务 |
| [自定义xeus内核集成](concepts/09-custom-kernel.md) | ⭐⭐⭐ | 扩展基类、实现抽象方法、新通信机制适配 |

## 💡 实战示例

| 示例 | 难度 | 场景 |
|------|------|------|
| [基础部署](examples/basic-deploy.md) | ⭐ | 最小可用站点部署到GitHub Pages/Nginx |
| [自定义Conda环境](examples/custom-env.md) | ⭐⭐ | 预装数据科学包、添加Notebook和数据文件 |
| [生产环境部署](examples/advanced-deploy.md) | ⭐⭐⭐ | COOP/COEP配置、CDN加速、Service Worker、PWA离线 |

## 📖 API 信源参考

每个核心模块的源码级API参考文档，包含类/方法签名、参数说明和源码定位：

| 信源 | 覆盖模块 |
|------|---------|
| [项目元数据](references/metasource.md) | 包信息、依赖版本、支持平台 |
| [xeus-core基类API](references/kernel-base-source.md) | WebWorkerKernelBase、XeusRemoteKernelBase、IXeusWorkerKernel、XeusWorkerLoggerBase |
| [empack内核实现API](references/kernel-impl-source.md) | WebWorkerKernel、EmpackedXeusRemoteKernel、IEmpackXeusWorkerKernel、动态包管理方法 |
| [双Worker模式实现](references/worker-modes-source.md) | XeusCoincidentKernel、XeusComlinkKernel、mount/initializeStdin差异 |
| [JupyterLab扩展注册](references/extension-source.md) | kernelPlugin、XeusLogManager、EmpackEnvMetaManager、Token定义 |
| [Python构建端XeusAddon](references/python-addon-source.md) | post_build流程、copy_xpython_static、pack_prefix、输出目录结构 |
| [Conda环境与pip处理](references/conda-env-source.md) | create_conda_environment、install_pip_packages、纯Python包验证 |

## 🗺️ 学习路径

### 路径1：用户/部署者（不需要理解源码）

```
00-introduction → 01-getting-started → examples/basic-deploy
                                              ↓
                                    examples/custom-env
                                              ↓
                                    examples/advanced-deploy
```

### 路径2：开发者（理解原理）

```
00-introduction → 01-getting-started
        ↓
02-architecture → 03-dual-worker-modes → 04-kernel-lifecycle
        ↓                                    ↓
05-build-system                    06-package-management
        ↓                                    ↓
07-filesystem-bridge ←───────────── 08-extension-registration
```

### 路径3：扩展开发者（自定义内核）

```
先完成路径2
    ↓
09-custom-kernel → 阅读references/下所有API文档
    ↓
参考xeus包的实现结构创建自己的包
```

## 🔑 核心设计洞察

1. **双Worker自适应**：根据`crossOriginIsolated`自动选择coincident（SAB同步，高性能，需COOP/COEP）或comlink（postMessage异步，兼容性好），文件系统和stdin在两种模式下实现完全不同。

2. **时态分层**：Python仅在`jupyter lite build`构建时运行（conda环境创建+empack打包），运行时完全是TypeScript+WASM——最终产物是纯静态文件。

3. **三层抽象**：xeus-core（抽象基类）→ xeus（empack具体实现）→ xeus-extension（JupyterLab集成），使得新语言内核、新打包格式、新通信机制都能独立扩展。

4. **浏览器内包管理**：mambajs在浏览器内运行libsolv依赖求解器，下载预编译WASM conda包到Emscripten MEMFS，支持%conda/%pip但pip仅支持纯Python包。

5. **三层文件系统**：MEMFS（内核+预装包）→ DriveFS/SAB（JupyterLite Contents API桥接）→ 打包挂载（构建时只读快照），工作目录优先`/files`然后`/drive`。

## 📁 Bundle 结构

```
xeus/
├── index.md                    # 本文件
├── facts.md                    # R阶段事实清单（137条零推测事实）
├── insights.md                 # I阶段架构洞察（5条核心洞察+知识地图）
├── concepts/                   # 概念文档（10篇）
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-architecture.md
│   ├── 03-dual-worker-modes.md
│   ├── 04-kernel-lifecycle.md
│   ├── 05-build-system.md
│   ├── 06-package-management.md
│   ├── 07-filesystem-bridge.md
│   ├── 08-extension-registration.md
│   └── 09-custom-kernel.md
├── examples/                   # 示例文档（3篇）
│   ├── index.md
│   ├── basic-deploy.md
│   ├── custom-env.md
│   └── advanced-deploy.md
└── references/                 # API信源参考（7篇）
    ├── index.md
    ├── metasource.md
    ├── kernel-base-source.md
    ├── kernel-impl-source.md
    ├── worker-modes-source.md
    ├── extension-source.md
    ├── python-addon-source.md
    └── conda-env-source.md
```

## 相关Bundle

- [fps](../fps/index.md) — JupyterLite的FastAPI插件系统（JupyterLite核心插件框架）

```{toctree}
:hidden:

examples/index
references/index
concepts/00-introduction
concepts/01-getting-started
concepts/02-architecture
concepts/03-dual-worker-modes
concepts/04-kernel-lifecycle
concepts/05-build-system
concepts/06-package-management
concepts/07-filesystem-bridge
concepts/08-extension-registration
concepts/09-custom-kernel
facts
insights
log
```
