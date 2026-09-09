---
type: Section
title: 概念
description: DSH Mobile 产品定位、Kuikly 跨端方案、Host 协议、连接重连与行业演进
generated: { by: "process:blog-article-to-okf-bundle", at: "2026-09-09T00:00:00+08:00" }
---

# 概念导航

按阅读顺序建议：先读 00 定位 → 01 跨端框架 → 02 协议层 → 03 连接层 → 04 行业趋势（可选）。

- [00-dsh-mobile-overview](00-dsh-mobile-overview.md) — 产品定位与架构总览：为什么需要手机接 Agent、为何弃 WebView、远程控制面板定位
- [01-kuikly-cross-platform](01-kuikly-cross-platform.md) — Kuikly 跨端框架与原生桥接：KMP 六平台、组件市场复用、差异下沉、KuiklyUI-AI
- [02-dsh-host-protocol](02-dsh-host-protocol.md) — DSH Host 协议直连：RPC 方法表、session.prompt、events.mux/events.host 两条事件流、快照与宽类型
- [03-connection-and-reconnect](03-connection-and-reconnect.md) — 两种远程连接与断线重连：SSH 隧道、扫码 Relay、世代号、重连状态机
- [04-mobile-agent-control-patterns](04-mobile-agent-control-patterns.md) — 移动端 Agent 控制行业参照与演进：Cursor/Claude Code、手机=决策节点、路线图

```{toctree}
:hidden:
:maxdepth: 2

00-dsh-mobile-overview
01-kuikly-cross-platform
02-dsh-host-protocol
03-connection-and-reconnect
04-mobile-agent-control-patterns
```
