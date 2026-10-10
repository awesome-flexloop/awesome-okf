---
okf_version: "0.2"
type: Concept
title: "Octop 单进程架构与 Harness 组件"
description: "Octop 的单 Python 进程设计、四个 Harness 组件（agent/gateway/memory/browser）、HarnessProcessor 请求流转与 SQLite/PostgreSQL 选型（机制层）"
tags: [octop, architecture, harness, fastapi, single-process, sqlite, langgraph]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-10T09:35:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/kskjE8iQ2AxtI_Skqz5fvg"
  - id: official-home
    url: "https://tencentcloud.github.io/Octop/"
  - id: pypi
    url: "https://pypi.org/project/octop/"
---

# Octop 单进程架构与 Harness 组件

> 机制层（How it works）。本文解释 Octop 的架构设计与其降低自托管复杂度的思路。

## 核心技术栈

| 层 | 技术 | 出处 |
|----|------|------|
| 后端 | Python 3.12+、FastAPI、uvicorn | F-004/F-035 |
| 前端 | React、TypeScript、Vite、Ant Design | F-004/F-035 |
| Agent 运行时 | LangGraph（官方口径） | F-038 |
| 控制平面数据库 | SQLite（默认）/ PostgreSQL（可选） | F-011/F-036 |
| 定时调度 | APScheduler | F-028/F-036 |

## 单进程设计

Octop 的关键架构选择是：**一个 Python 进程**同时承载 Web 控制台、CLI、IM 渠道监听器和定时任务调度器，所有功能共享同一个 SQLite 数据库和同一套配置（F-009/F-010/F-036）。

其取舍在于（官方的核心表述）：

- **无需外部队列或消息代理**。相比把 Web/IM/调度拆成多个微服务（各自带独立队列和存储）的常见架构，Octop 用单进程 + 共享 SQLite 显著降低了个体与小团队的自托管复杂度（F-010/F-036）。
- 保留扩展能力：控制平面数据库可选 PostgreSQL，支持多用户、插件与外部存储（F-011/F-036）。

> 官方把这个取舍描述为「所有功能都运行在同一个进程和数据库中」，这是它适合自托管与小型多用户部署的根因（F-036）。

## Harness 四组件（Octop 的组合件）

Octop 由 4 个「Harness」运行时组件组合进同一个进程（F-003/F-037）：

| 组件 | 官方命名 | 职责 |
|------|---------|------|
| Agent 运行时 | **harness-agent** | 模型路由、工具调用、Skills 管理、对话检查点（模型路由/工具/Skills/会话 checkpointing） |
| 消息网关 | **harness-gateway** | 跨平台即时通信（IM）渠道桥，把多渠道入站消息归一化为单一处理流水线 |
| 长期记忆 | **harness-memory** | 层级召回 + 全文检索；智能体的记忆随其工作空间（workspace）移动 |
| 浏览器自动化 | **harness-browser** | 基于 CDP（Chrome DevTools Protocol）的浏览器自动化 |

> 命名口径：博文称四组件为「Octop Harness / Octop Memory / Octop Browser / Octop Gateway」（F-003）；官方在 Harness stack 中的细粒度命名是 `harness-agent` / `harness-memory` / `harness-browser` / `harness-gateway`（F-037）。两者指同一套组件，本文以官方命名为主。

## 请求流转（HarnessProcessor）

Octop 通过统一的 **HarnessProcessor** 处理来自 Web 控制台、即时通信平台和定时任务的请求（F-009）：

1. 请求经页面、IM 渠道或 HTTP/SSE/WebSocket API 到达服务器（F-036）。
2. HarnessProcessor 按「用户 + 专家」上下文归一化处理（F-036）。
3. 交由对应 Agent（专家）连同其记忆、工具、工作空间执行（F-014/F-036）。

## 为什么这值得注意（选择依据）

- **自托管门槛低**：单进程 + SQLite，一台家庭/团队服务器即可运行，无需编排 Kubernetes、无需外部消息中间件（F-010/F-036）。
- **可控但可扩展**：SQLite→PostgreSQL 平滑升级，满足从小规模到大一点的多用户（F-011/F-036）。
- **组件可单独引入**：官方说明可按需引入 Agent 运行时、长期记忆、浏览器自动化或消息接入能力，不需要装整套系统（F-003/F-037，博文转述）。

## 反模式与边界

- **单进程 ≠ 高性能横向扩展**：单进程模型面向家庭/小团队自托管，超大并发仍受限于单进程吞吐（本文基于官方单进程设计推断，属边界说明）。
- **不要混淆「单进程」与「缺少扩展」**：官方支持 PostgreSQL、插件、外部存储，扩展能力并未因单进程而消失（F-011/F-036）。

## 阅读下一篇

- [02 · 多 Agent 专家与长期记忆](02-multi-agent-and-memory.md)——四个组件之上的业务能力
- [03 · 工具调用与多渠道接入](03-tools-and-channels.md)——Browser/Terminal/远程桌面/ACP 与 IM 多渠道