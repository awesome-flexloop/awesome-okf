# 概念文档

本目录包含 p5-kernel 的核心概念文档，按学习路径排列。

## 入门

- [00-p5-kernel 简介](00-introduction.md) — p5-kernel 是什么、核心特性、安装方法、生态位置
- [01-架构概览](01-architecture-overview.md) — 整体架构、继承关系、三层线程模型、关键数据流

## 核心

- [02-P5Kernel 实现详解](02-kernel-implementation.md) — 构造函数、bootstrap、executeRequest 流程、生命周期
- [03-P5Executor 与渲染机制](03-executor-and-rendering.md) — p5.Graphics 自动渲染、P5_DOCS 内置文档、自动生成机制
- [04-%show 魔法命令](04-magic-commands.md) — 语法、参数、iframe srcdoc 生成、代码累积、实时更新

## 扩展

- [05-扩展注册与 CDN 配置](05-extension-registration.md) — JupyterLab 插件、KernelSpec 定义、p5Url 配置
- [06-构建与打包](06-build-and-packaging.md) — TypeScript 构建、p5-docs 生成、hatchling Python 包、双发布
