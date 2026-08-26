# Echo Kernel 核心概念

本文档目录包含 JupyterLite Echo Kernel 的核心概念文档，从架构原理到具体实现机制。

## 概念文档列表

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [Echo Kernel简介](00-introduction.md) | 是什么、核心特性、设计目标、教学价值、项目基本信息 |
| 01 | [JupyterLite内核架构基础](01-kernel-architecture.md) | 主线程-Worker通信模型、BaseKernel模板方法、Jupyter消息协议、KernelSpec |
| 02 | [JupyterLab插件注册机制](02-plugin-registration.md) | Token依赖注入、JupyterFrontEndPlugin结构、IKernelSpecs注册、autoStart机制 |
| 03 | [EchoKernel实现详解](03-echokernel-implementation.md) | kernelInfoRequest、executeRequest核心逻辑、publishExecuteResult、未实现方法分析 |
| 04 | [构建与打包系统](04-build-and-packaging.md) | TypeScript编译、labextension打包、hatchling+hatch-jupyter-builder双构建系统 |

## 推荐学习路径

1. **入门了解**：[00-简介](00-introduction.md) → [01-内核架构基础](01-kernel-architecture.md)
2. **理解注册机制**：[02-插件注册机制](02-plugin-registration.md)
3. **深入实现**：[03-EchoKernel实现详解](03-echokernel-implementation.md)
4. **构建发布**：[04-构建与打包系统](04-build-and-packaging.md)
5. **动手实践**：前往[实践示例](/examples/index.md)跟着教程开发自己的内核

```{toctree}
:maxdepth: 7

00-introduction
01-kernel-architecture
02-plugin-registration
03-echokernel-implementation
04-build-and-packaging
```
