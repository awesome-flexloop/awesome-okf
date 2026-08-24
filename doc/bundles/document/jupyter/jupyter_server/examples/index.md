---
type: Index
title: "示例文档索引"
description: "Jupyter Server 实战示例索引，包含 API 调用、扩展开发、WebSocket 通信三个完整示例"
tags: [examples, index, tutorial]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:10:00Z" }
status: stable
stale_after: 2027-02-22
sources: []
---

# 示例文档索引

本目录提供 Jupyter Server 的实战示例，覆盖 REST API 使用、扩展开发和 WebSocket 内核通信三大场景。

## 示例列表

| 序号 | 示例 | 难度 | 核心内容 |
|------|------|------|---------|
| 01 | [基础 API 使用](01-basic-api-usage.md) | ⭐ 入门 | curl/Python requests 调用 Contents/Kernels/Sessions REST API，文件管理、内核启动 |
| 02 | [编写简单扩展](02-simple-extension.md) | ⭐⭐ 中级 | 创建 ExtensionApp、注册 API Handler、HTML 页面、配置项、entry points 打包 |
| 03 | [WebSocket 内核通信](03-websocket-kernel.md) | ⭐⭐⭐ 进阶 | Python/JavaScript WebSocket 客户端、Jupyter 消息协议、代码执行、实时输出接收 |

## 前置条件

所有示例需要一个运行中的 Jupyter Server：

```bash
# 启动开发服务器
pip install jupyter-server
jupyter server --ServerApp.token=mytoken --port=8888 --no-browser
```

## 示例与概念对应

| 示例 | 相关概念文档 |
|------|-------------|
| 基础 API 使用 | [内容管理服务](../concepts/07-contents-service.md)、[内核管理](../concepts/08-kernel-management.md)、[会话管理](../concepts/09-sessions-service.md) |
| 编写简单扩展 | [扩展系统](../concepts/10-extension-system.md)、[Handler 继承体系](../concepts/04-handler-hierarchy.md) |
| WebSocket 内核通信 | [WebSocket 通信](../concepts/11-websocket-communication.md)、[内核管理](../concepts/08-kernel-management.md)、[异步编程模型](../concepts/14-async-programming.md) |

```{toctree}
:hidden:

01-basic-api-usage
02-simple-extension
03-websocket-kernel
```
