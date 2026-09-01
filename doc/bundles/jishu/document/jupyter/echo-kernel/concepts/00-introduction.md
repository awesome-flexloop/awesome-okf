---
type: Concept
title: Echo Kernel 简介
description: JupyterLite Echo Kernel 是什么、核心特性、设计目标，以及它作为自定义内核最小示例的教学价值
tags: [introduction, overview, echo-kernel, jupyterlite, kernel]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: meta-source
    resource: /references/plugin-source.md
    title: Echo Kernel 插件注册源码信源
  - id: kernel-src
    resource: /references/kernel-source.md
    title: EchoKernel 类源码信源
---

## Echo Kernel 是什么

Echo Kernel 是 JupyterLite 的一个**最小化示例内核**（echo kernel），它将用户在 Notebook 中输入的代码**原样输出**，不做任何计算或处理。

核心行为：用户输入什么代码，输出区域就显示什么代码——就像"回声"一样。

## 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 极简实现 | 核心TypeScript代码仅约150行，是学习JupyterLite内核开发的最佳起点 |
| 📝 纯文本内核 | 语言类型为 `text`，不执行任何代码，仅回显输入 |
|🔌即插即用 | 作为JupyterLab扩展自动注册，安装后即可在内核选择器中看到"Echo"内核 |
| 🌐 浏览器运行 | 完全在浏览器Web Worker中运行，无需后端服务器 |
| 📦 双语言包 | 同时发布npm包（`@jupyterlite/echo-kernel`）和Python包（`jupyterlite-echo-kernel`） |

## 设计目标

Echo Kernel 的设计目标不是提供一个有用的计算内核，而是：

1. **作为模板**：展示JupyterLite自定义内核的最小必要实现
2. **教学用途**：帮助开发者理解Jupyter内核消息协议和JupyterLite内核API
3. **测试验证**：验证JupyterLite内核注册和消息传递机制是否正常工作
4. **起步脚手架**：开发者可以复制echo-kernel作为起点，替换executeRequest()逻辑来实现自己的内核

## 项目基本信息

| 属性 | 值 |
|------|-----|
| npm包名 | `@jupyterlite/echo-kernel` |
| Python包名 | `jupyterlite-echo-kernel` |
| 版本 | 0.4.0 |
| 许可证 | BSD-3-Clause |
| 兼容JupyterLite | >= 0.6.0（当前基于0.7.0构建） |
| 核心依赖 | `@jupyterlab/application: ^4.5.0`, `@jupyterlite/services: ^0.7.0` |
| Python依赖 | 无运行时依赖 |

## 在JupyterLite内核生态中的位置

JupyterLite支持多种内核类型：

| 内核 | 语言 | 说明 |
|------|------|------|
| **Pyodide Kernel** | Python | CPython编译为WASM，完整科学计算支持 |
| **Xeus Kernel** | C++/多种语言 | 基于Xeus框架的原生内核 |
| **Echo Kernel** | Text（示例） | 最小示例内核，仅回显输入 |
| 自定义内核 | 任意 | 开发者可实现自己的内核 |

Echo Kernel是最简单的内核，只实现了最核心的 `execute_request` 和 `kernel_info_request` 两个消息处理。

## 为什么Echo Kernel很重要

对于想要开发JupyterLite自定义内核的开发者来说，Echo Kernel是最理想的学习材料：

- 它实现了所有必需的接口（10个BaseKernel抽象方法）
- 其中8个方法可以安全地stub（抛出Not implemented）
- executeRequest()的逻辑极其简单（回显输入），易于理解
- 包含了完整的构建配置（TypeScript + hatchling双构建系统）
- 展示了JupyterLab插件注册的标准模式

## 相关概念

- [JupyterLite内核架构](01-kernel-architecture.md)
- [插件注册机制](02-plugin-registration.md)
- [EchoKernel实现详解](03-echokernel-implementation.md)
- [构建与打包](04-build-and-packaging.md)
