---
type: Index
title: 概念文档索引
description: JavaScript Kernel 核心概念文档
tags: [concepts, index]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
---

# 概念文档

- [00-简介](00-introduction.md) — JavaScript Kernel 是什么、核心特性、双运行时模式（IFrame/Worker）、技术栈
- [01-快速开始](01-getting-started.md) — 安装、创建第一个 Notebook、基础表达式、模式选择、Console 输出
- [02-内核架构](02-kernel-architecture.md) — JavaScriptKernel 类、IRuntimeBackend 接口、请求处理流程、启动扩展生命周期
- [03-执行模型](03-execution-model.md) — AST 解析、三重代码转换、Magic Imports、异步函数包装、MIME 富输出、代码补全、错误处理
- [04-运行时后端](04-runtime-backends.md) — IFrameRuntimeBackend 和 WorkerRuntimeBackend 实现、Comlink RPC 通信、初始化流程、资源清理
- [05-Widget 系统](05-widget-system.md) — 内置 ipywidgets 兼容层、Widget/DOMWidget 基类、55+ 控件清单、事件系统、jslink 双向绑定
- [06-Comm 协议](06-comm-protocol.md) — 自定义双向通信通道、CommManager、Comm 类、Widget 通信、Buffer 支持
- [07-富媒体输出系统](07-display-system.md) — display() 函数、DisplayHelper、MIME bundle 类型、display_id 动态更新、自定义输出方法
- [08-启动扩展机制](08-startup-extensions.md) — IJavaScriptKernelStartupRegistry Token、前端插件预加载模块、registerCommTarget
- [09-常见问题与限制](09-faq-limitations.md) — 模式选择、Magic Imports 问题、DOM 限制、调试技巧、与 IPython 差异

```{toctree}
:hidden:

00-introduction
01-getting-started
02-kernel-architecture
03-execution-model
04-runtime-backends
05-widget-system
06-comm-protocol
07-display-system
08-startup-extensions
09-faq-limitations
```
