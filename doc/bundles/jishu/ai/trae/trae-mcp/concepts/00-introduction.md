---
type: Concept
title: MCP 简介
description: MCP（Model Context Protocol）是 Anthropic 推出的开放标准协议，为 AI 模型提供操作工具、读取数据和连接服务三种核心能力，在 TRAE 中作为 Agent 可调用的工具服务器。
tags: [trae-mcp, trae, mcp, introduction, model-context-protocol]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# MCP 简介

## 什么是 MCP

MCP 全称为 **Model Context Protocol**（模型上下文协议），是 Anthropic 推出的开放标准协议，用于标准化 AI 模型与外部系统的连接方式。在 TRAE IDE 生态中，trae-mcp 仓库是社区维护的 MCP 服务器集合，采用 MIT 许可证。

MCP 的核心定位可以用一个比喻来理解：MCP 是 AI 模型的"感官"和"四肢"，赋予 AI 与外部世界交互的能力。

## MCP 的三种能力

MCP 为 AI 模型提供三种核心能力：

1. **操作工具**：执行命令行、发送消息、管理代码仓库——这是 AI 的"手"，能主动改变外部状态
2. **读取数据**：访问本地文件、查询数据库、阅读文档——这是 AI 的"眼睛"，能获取外部信息
3. **连接服务**：与 Slack、GitHub、Google Drive 等外部平台交互——这是 AI 的"触手"，能连接互联网服务

在 TRAE 中，配置的 MCP 服务器作为 agent 可调用的 **Tools**，agent 可根据任务需求自动选择并执行这些工具。

## MCP 与 Skill 的区别

MCP 和 SKILL 是 TRAE Agent 能力扩展的两种根本不同机制：

| 维度 | MCP | SKILL |
|------|-----|-------|
| **本质** | 可调用的工具服务器（Tool Server） | 提示词指令包（Prompt Package） |
| **接口** | 程序化 API 接口，Agent 通过函数调用使用 | 自然语言工作流指令，指导 Agent 思考和行动 |
| **返回** | 结构化数据 | 不提供可执行接口 |
| **比喻** | 扩展 Agent 的"手"（能做什么操作） | 扩展 Agent 的"脑"（知道怎么做、何时做） |

trae-mcp 仓库中存在两者混淆的案例：`git-commit-generator` 目录下无任何 MCP 服务器代码，完全是从 trae-skills 复制的 Skill 内容。实际上 trae-mcp 仓库的定位更接近"MCP 服务器的配置与文档索引"，而非"MCP 服务器源码仓库"——MCP 服务器的实际代码通常以 npm 包/Python 包/独立可执行文件形式分发。

> ⚠️ README 中明确说明：项目主要托管 MCP Servers（Tools），Skills（SOPs）在 TRAE Agent Skills 仓库。

## 相关链接

- [MCP 三层模型](01-mcp-architecture.md)
- [MCP 配置格式](02-mcp-configuration.md)
- [MCP 与 Skill 的本质区别](04-mcp-vs-skill.md)
- [配置 MCP 服务器示例](../examples/configure-mcp.md)
- [MCP 协议文档与 CloudBase MCP 索引](../references/mcp-source.md)
