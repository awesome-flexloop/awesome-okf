---
okf_version: "0.2"
type: Concept
title: "概念文档索引"
description: "《从 Token 到 Agent》知识包概念层文档导航。"
tags: ["索引", "概念层", "导航"]
generated: 2026-09-09
verified: 2026-09-09
status: verified
stale_after: "2027-09-09"
sources: []
---

# 概念文档索引

## 概览

本知识包概念层共 8 篇文档，覆盖从 Token 到 Agent 的九层认知架构。

## 文档列表

### 总览

| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [概念全景与总结](00-overview.md) | 概念关系速查表、核心论点、学习路径、端到端旅程 |

### 各层详解

| 编号 | 文档 | 层级 | 核心内容 |
|------|------|------|----------|
| 01 | [Token（词元）](01-token.md) | 基础层 | 分词原理、中英文估算、计费与性能影响 |
| 02 | [Context 与 Context Window](02-context.md) | 记忆层 | Context 组成、容量定义、溢出行为 |
| 03 | [Prompt（提示词）](03-prompt.md) | 指令层 | 两种类型、Prompt Engineering 本质 |
| 04 | [Tool（工具）](04-tool.md) | 执行层 | Tool 类型、工作流程、JSON 定义格式 |
| 05 | [MCP（模型上下文协议）](05-mcp.md) | 协议层 | 三种原语、vs 直接 API、生态价值 |
| 06 | [Skill（技能）](06-skill.md) | 封装层 | 组成结构、渐进式加载、vs Tool/Agent |
| 07 | [Agent（智能体）](07-agent.md) | 系统层 | 四大能力、工作循环、SubAgent 模式 |
| 08 | [LLM（大语言模型）](08-llm.md) | 引擎层 | 代表性模型、架构位置、层间关系 |

## 阅读建议

1. 先读 [00 概念全景与总结](00-overview.md) 建立整体认知
2. 按 01→08 顺序逐层深入理解各概念
3. 结合 [references/insights.md](../references/insights.md) 深化理解核心论点

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-token
02-context
03-prompt
04-tool
05-mcp
06-skill
07-agent
08-llm
```
