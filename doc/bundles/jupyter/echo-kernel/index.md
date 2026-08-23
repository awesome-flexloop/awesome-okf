---
type: OKF
title: JupyterLite Echo Kernel 教程
description: JupyterLite Echo Kernel最小示例内核的系统化教程，涵盖内核架构、插件注册、BaseKernel实现、构建打包与自定义内核开发
tags: [echo-kernel, jupyterlite, jupyter, kernel, typescript, browser, notebook, extension]
okf_version: "0.2"
version: "0.1.0"
source: https://github.com/jupyterlite/echo-kernel
source_version: "0.4.0"
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:25:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# JupyterLite Echo Kernel 教程

Echo Kernel 是 JupyterLite 的**最小化示例内核**，它将用户输入的代码原样输出（"回声"），核心TypeScript代码仅约150行。它是学习JupyterLite自定义内核开发的最佳起点——实现了所有必需的接口，展示了完整的插件注册和构建配置。

本教程基于 echo-kernel v0.4.0 源码深度分析，系统讲解 JupyterLite 内核架构、插件系统、消息协议、内核实现和构建打包机制。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-Echo Kernel简介](concepts/00-introduction.md) — 是什么、核心特性、设计目标、教学价值
- [01-JupyterLite内核架构基础](concepts/01-kernel-architecture.md) — 主线程-Worker通信、BaseKernel模板方法、消息协议
- [02-JupyterLab插件注册机制](concepts/02-plugin-registration.md) — Token依赖注入、JupyterFrontEndPlugin、autoStart
- [03-EchoKernel实现详解](concepts/03-echokernel-implementation.md) — kernelInfoRequest、executeRequest、publishExecuteResult
- [04-构建与打包系统](concepts/04-build-and-packaging.md) — TypeScript编译、labextension打包、hatchling双构建

### [实践示例](examples/index.md)
- [01-安装与使用Echo Kernel](examples/01-install-and-use.md) — pip安装、站点构建、验证、开发模式
- [02-自定义JupyterLite内核开发教程](examples/02-custom-kernel-tutorial.md) — 从零创建Uppercase Kernel完整教程

### [信源参考](references/index.md)
- [插件注册信源](references/plugin-source.md) — src/index.ts API登记
- [内核类信源](references/kernel-source.md) — src/kernel.ts EchoKernel类API登记
- [Python包信源](references/python-source.md) — __init__.py、pyproject.toml、install.json API登记

## 🚀 快速体验

安装Echo Kernel并集成到JupyterLite站点：

```bash
# 安装Echo Kernel
pip install jupyterlite-echo-kernel

# 构建JupyterLite站点
jupyter lite build

# 预览站点
jupyter lite serve
# 访问 http://localhost:8000
```

打开浏览器后，在Launcher中选择"Echo"内核创建Notebook，输入任意文本按Shift+Enter，输出区域会原样显示输入内容。

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 极简实现 | 核心代码仅约150行TypeScript，最小可用内核示例 |
| 📝 纯文本回显 | 输入什么输出什么，无计算逻辑，专注于展示内核框架 |
| 🔌 即插即用 | pip install后自动注册，内核选择器中可见 |
| 📦 双语言包 | 同时发布npm包和Python包，标准JupyterLab扩展格式 |
| 🏗️ 完整构建 | 展示TypeScript+hatchling双构建系统配置 |
| 📖 教学价值 | 自定义内核开发最佳入门模板 |

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                   主线程 (UI)                             │
│  JupyterLab → @jupyterlab/services                       │
│  └─ LiteKernelClient (mock-socket桥接)                   │
│  └─ IKernelSpecs（内核规格注册服务）                      │
│     └─ @jupyterlite/echo-kernel:kernel 插件              │
│        └─ kernelspecs.register({spec, create})          │
└────────────────────────┬────────────────────────────────┘
                         │ mock-socket
                         ↓
┌────────────────────────┴────────────────────────────────┐
│                Web Worker (内核线程)                      │
│  EchoKernel extends BaseKernel                           │
│  ├─ kernelInfoRequest() → 返回内核元信息                  │
│  └─ executeRequest() → publishExecuteResult({code})     │
└─────────────────────────────────────────────────────────┘
```

## 📖 推荐学习路径

1. **入门了解**：阅读 [00-简介](concepts/00-introduction.md) 和 [01-内核架构](concepts/01-kernel-architecture.md)，理解JupyterLite内核通信模型
2. **理解插件系统**：学习 [02-插件注册机制](concepts/02-plugin-registration.md)，掌握Token依赖注入和内核注册流程
3. **深入实现**：阅读 [03-EchoKernel实现](concepts/03-echokernel-implementation.md)，理解消息处理和结果发布
4. **掌握构建**：学习 [04-构建与打包](concepts/04-build-and-packaging.md)，理解双语言构建系统
5. **动手实践**：跟着 [02-自定义内核教程](examples/02-custom-kernel-tutorial.md) 开发自己的第一个内核
6. **安装体验**：按 [01-安装使用](examples/01-install-and-use.md) 步骤实际安装和体验Echo Kernel

## 🔑 Echo Kernel 教给我们什么

作为最小内核示例，Echo Kernel展示了JupyterLite内核开发的所有关键概念：

1. **BaseKernel模板方法**：继承BaseKernel，只需实现10个抽象方法，其中8个可以stub
2. **消息协议**：`kernel_info_request` 和 `execute_request` 是最小必需消息
3. **输出发布**：通过 `publishExecuteResult()`、`stream()` 等方法向前端发送消息
4. **插件注册**：使用 `JupyterFrontEndPlugin` + `IKernelSpecs.register()` 注册内核
5. **构建配置**：TypeScript编译 + JupyterLab builder + hatchling Python打包的完整配置
