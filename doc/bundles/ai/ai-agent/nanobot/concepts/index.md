# Concepts

- [00 - nanobot 简介](00-introduction.md) — nanobot 定位、Python Agent 核心与多接口概览
- [01 - 整体架构](01-architecture.md) — 消息总线、nanobot.py 主入口、CLI 分层与网关模式
- [02 - Agent 运行时](02-agent-runtime.md) — AgentLoop、AgentRunner、LLM Provider 抽象与工具调用
- [03 - 消息总线与事件驱动](03-bus-messaging.md) — MessageBus、WebSocket 通道、多聊天复用与认证
- [04 - SDK 类型系统](04-sdk-types.md) — StreamEventType、RunResult、StreamEvent、SessionSnapshot
- [05 - 多接口架构](05-multi-interface.md) — CLI、TUI（Bun+TypeScript）、WebUI（React）三端实现

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-architecture
02-agent-runtime
03-bus-messaging
04-sdk-types
05-multi-interface
```
