# 概念文档

本目录包含 jupyter_server_terminals 的核心概念文档，按学习路径从入门到进阶排列。

## 入门

* [jupyter_server_terminals 简介](00-introduction.md) — 什么是 jupyter_server_terminals、与 terminado 的关系、核心能力、在 Jupyter 生态中的位置。
* [5分钟快速上手](01-getting-started.md) — 安装、启用、验证、REST API 快速体验、基本配置。

## 核心架构

* [TerminalsExtensionApp 扩展应用](02-extension-app.md) — 扩展生命周期（settings/handlers 初始化、清理关闭）、Shell 配置流程、环境变量传递。
* [TerminalManager 终端管理器](03-terminal-manager.md) — 终端 CRUD 操作、REST 数据模型、闲置终端自动清理（Culler）、Prometheus 指标、活动追踪。

## 通信与接口

* [REST API 处理器](04-rest-api.md) — TerminalRootHandler/TerminalHandler 路由、认证装饰器、cwd 路径解析、HTTP 方法语义。
* [WebSocket 处理器](05-websocket.md) — TermSocket 多继承结构、WebSocket 握手与认证、消息协议（stdin/stdout）、活动时间戳更新。

## 配置与平台

* [Shell 配置与平台差异](06-shell-configuration.md) — Shell 确定优先级链、平台默认 Shell（PowerShell/Bash）、Login Shell 模式、环境变量、跨平台注意事项。

```{toctree}
:hidden:

00-introduction
01-getting-started
02-extension-app
03-terminal-manager
04-rest-api
05-websocket
06-shell-configuration
```
