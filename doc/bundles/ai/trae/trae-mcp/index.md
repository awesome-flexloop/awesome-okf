---
type: Index
title: TRAE MCP 工具服务器
description: trae-mcp 是 TRAE 生态的 MCP（Model Context Protocol）工具服务器集合，涵盖 MCP 架构、配置方法、CloudBase MCP 集成和 MCP 开发指南。
tags: [trae-mcp, trae, mcp, model-context-protocol, tools, server]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# trae-mcp 文档

trae-mcp 是 TRAE IDE 的社区维护 MCP（Model Context Protocol）服务器集合，采用 MIT 许可证。MCP 是 Anthropic 推出的开放标准协议，用于标准化 AI 模型与外部系统的连接方式。

## 核心概念

| 文档 | 说明 |
|------|------|
| [MCP 简介](/concepts/00-introduction.md) | MCP 是什么、三种能力比喻（资源/工具/提示）、与 SKILL 的区别 |
| [MCP 三层模型](/concepts/01-mcp-architecture.md) | Transport 层（stdio/SSE）、Protocol 层（JSON-RPC）、Capability 层（Tools/Resources/Prompts） |
| [MCP 配置格式](/concepts/02-mcp-configuration.md) | JSON 配置结构、server 配置、transport 选择 |
| [CloudBase MCP](/concepts/03-cloudbase-mcp.md) | 腾讯云开发 MCP 服务器、npm 包、7 类云资源能力、7 步工作流 |
| [MCP 与 Skill 的本质区别](/concepts/04-mcp-vs-skill.md) | 工具服务器 vs 提示词包、调用方式对比、何时用 MCP 何时用 Skill |
| [MCP 开发入门](/concepts/05-mcp-development.md) | SDK 选择、服务器骨架、Tool 注册、三层排错法 |

## 示例

| 文档 | 说明 |
|------|------|
| [配置 MCP 服务器示例](/examples/configure-mcp.md) | 在 TRAE 中添加本地 MCP 和 CloudBase MCP 的配置步骤 |
| [CloudBase MCP 使用示例](/examples/use-cloudbase-mcp.md) | CloudBase MCP 配置、登录、7 步工作流使用方式 |
| [构建简单 MCP 服务器示例](/examples/build-simple-mcp.md) | MCP 服务器开发基本流程、Tool 注册、SKILL.md 编写 |

## 参考

| 文档 | 说明 |
|------|------|
| [MCP 协议文档与 CloudBase MCP 索引](/references/mcp-source.md) | MCP 官方文档、CloudBase 文档/源码/插件链接、仓库目录索引 |

```{toctree}
:hidden:
:maxdepth: 7

concepts/00-introduction
concepts/01-mcp-architecture
concepts/02-mcp-configuration
concepts/03-cloudbase-mcp
concepts/04-mcp-vs-skill
concepts/05-mcp-development
examples/build-simple-mcp
examples/configure-mcp
examples/use-cloudbase-mcp
references/mcp-source
spec/facts
spec/insights
```
