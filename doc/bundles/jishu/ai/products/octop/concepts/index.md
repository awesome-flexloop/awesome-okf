---
okf_version: "0.2"
type: category
title: "Octop 概念教程"
description: "Octop 从『单次对话工具』到『长期工作的多 Agent 助手平台』的设计与使用——身份定位、单进程架构与 Harness 组件、多 Agent 专家与长期记忆、工具调用与多渠道接入"
---

# Octop 概念教程

按从「是什么」到「怎么用」再到「关键子特性」的路径组织：

| 文档 | 内容 |
|------|------|
| [00 · 项目身份与定位](00-what-is-octop.md) | 是什么、官方自述、MIT 许可事实、热度（带时点）、解决的问题 |
| [01 · 单进程架构与 Harness 组件](01-architecture-and-harness.md) | 单 Python 进程、Harness 四组件、HarnessProcessor、SQLite/PostgreSQL 选型、降低自托管复杂度 |
| [02 · 多 Agent 专家与长期记忆](02-multi-agent-and-memory.md) | 多 Agent 专家团队、专家共享、RAG 知识库、Octop Memory 层级记忆、用户隔离 |
| [03 · 工具调用与多渠道接入](03-tools-and-channels.md) | Browser AI+、Terminal AI+、远程桌面、ACP 双向集成、多渠道（IM/HTTP/SSE/WebSocket）、定时任务 |
| [04 · 安装与快速上手](04-install-and-run.md) | 安装命令、初始化、启动、登录、配置模型服务商 |

```{toctree}
:maxdepth: 2
:hidden:

00-what-is-octop
01-architecture-and-harness
02-multi-agent-and-memory
03-tools-and-channels
04-install-and-run
```