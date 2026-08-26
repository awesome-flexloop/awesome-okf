# 概念文档索引

## 入门

- [00. sphinx-autobuild 简介](00-introduction.md) — 什么是 sphinx-autobuild、设计理念、安装方法、与其他方案对比
- [01. 5分钟快速上手](01-getting-started.md) — 基本命令、autobuild 专有选项、默认忽略目录、Makefile 集成

## 核心架构

- [02. 架构概览](02-architecture-overview.md) — 整体架构图、四大核心组件、请求处理流程、异步任务模型
- [03. CLI 入口与参数解析](03-cli-and-entrypoint.md) — 双解析器策略、Sphinx 参数复用、选项组设计、Make Mode 支持

## 组件详解

- [04. 构建系统](04-builder-system.md) — Builder 类、子进程调用、前后置命令、错误处理、进程隔离设计
- [05. 文件监听与过滤](05-file-watching.md) — watchfiles 异步监听、IgnoreFilter 双模式匹配、默认忽略目录、调试模式
- [06. 服务器与热重载](06-server-and-hotreload.md) — Starlette ASGI 应用、WebSocket 通信、asyncio.Event 信号机制、Lifespan 管理
- [07. 中间件注入机制](07-middleware-injection.md) — JavascriptInjectorMiddleware、ASGI 响应拦截、Content-Length 修正、Cache-Control 处理

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-cli-and-entrypoint
04-builder-system
05-file-watching
06-server-and-hotreload
07-middleware-injection
```
