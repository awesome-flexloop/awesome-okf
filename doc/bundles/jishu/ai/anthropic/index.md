---
okf_version: "0.2"
type: index
title: "Anthropic 生态中文 Wiki"
description: "Anthropic官方生态中文文档——Python SDK深度源码解析、Claude Code CLI、官方Cookbooks、提示词工程教程、Skills库、金融服务Agents、系统提示词发布史，覆盖Claude AI开发全栈。"
tags: [anthropic, claude, python-sdk, claude-code, prompt-engineering, skills, agents, llm, system-prompts]
sources:
  - name: anthropic-sdk-python
    path: "external/libs/anthropics/anthropic-sdk-python"
  - name: claude-code
    path: "external/libs/anthropics/claude-code"
  - name: claude-cookbooks
    path: "external/libs/anthropics/claude-cookbooks"
  - name: prompt-eng-interactive-tutorial
    path: "external/libs/anthropics/prompt-eng-interactive-tutorial"
  - name: skills
    path: "external/libs/anthropics/skills"
  - name: financial-services
    path: "external/libs/anthropics/financial-services"
generated:
  by: "process:source-code-to-okf-wiki R→I→E→V"
  at: "2026-08-27"
status: stable
stale_after: 2027-08-27
---

# Anthropic 生态中文 Wiki

Anthropic（[anthropic.com](https://www.anthropic.com)）是AI安全公司，Claude系列大模型的开发商。本Wiki覆盖Anthropic官方开源的6大核心项目与官方系统提示词发布史文档，从底层SDK到上层应用生态，为中文开发者提供系统化的Claude开发参考。

## 生态全景

Anthropic开源生态围绕**Claude模型**构建，形成从基础API到垂直行业应用的完整栈：

```
┌─────────────────────────────────────────────────────────┐
│  垂直行业应用层                                          │
│  ┌─────────────────────┐  ┌──────────────────────────┐  │
│  │ financial-services  │  │  Skills（19个官方技能）    │  │
│  │  10个金融Agents     │  │  文档/设计/API/开发工具     │  │
│  │  7个垂直Skills      │  │  /docx /pdf /pptx /xlsx   │  │
│  │  12个数据连接器      │  └──────────────────────────┘  │
│  └─────────────────────┘                                │
├─────────────────────────────────────────────────────────┤
│  开发工具与教程层                                        │
│  ┌──────────────┐  ┌────────────┐  ┌─────────────────┐  │
│  │  claude-code  │  │ cookbooks  │  │prompt-engineering│ │
│  │ CLI Agent框架 │  │ 实战食谱    │  │ 提示词工程教程   │  │
│  │ 插件/Hook/MCP │  │ 30+示例     │  │ 入门→中级→高级  │  │
│  └──────────────┘  └────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  SDK基础层                                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │           anthropic-sdk-python                    │   │
│  │  Stainless生成架构 · 同步/异步双轨 · 多云抽象      │   │
│  │  流式/SSE · Tool Use · Beta Agents/Memory/MCP    │   │
│  │  Middleware洋葱模型 · AWS Bedrock · GCP Vertex   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 子Bundle导航

| 子Bundle | 深度 | 内容 | 适合人群 |
|---------|------|------|---------|
| [**python-sdk**](python-sdk/index.md) | 🔴深度源码 | 24文档（6参考+10概念+6示例），Stainless架构、同步/异步客户端、流式传输、Tool Use、多云适配、Beta Agents/Memory、中间件系统 | SDK开发者、生产环境集成 |
| [**claude-code**](claude-code/index.md) | 🟡结构化整理 | 9文档，CLI Agent框架、插件体系（commands/agents/skills/hooks/MCP）、13个官方插件、SDK开发 | Claude Code用户、插件开发者 |
| [**cookbooks**](cookbooks/index.md) | 🟡结构化整理 | 10文档，30+实战食谱索引，覆盖Agent SDK/Tool Use/Multimodal/Advanced/Third-party/Third-party-API | 快速上手、实战参考 |
| [**prompt-engineering**](prompt-engineering/index.md) | 🟡结构化整理 | 8文档，9章提示词工程教程，入门(结构/清晰/角色)→中级(数据分离/CoT/示例)→高级(防幻觉) | 提示词优化、Prompt工程师 |
| [**official-skills**](official-skills/index.md) | 🟡结构化整理 | 9文档，19个官方Skills分类索引，SKILL.md格式规范，skill-creator元技能，claude-api多语言参考 | Skill开发者、Claude Code高级用户 |
| [**financial-services**](financial-services/index.md) | 🟢行业方案 | 9文档，10个金融Agents、7个垂直Skills、12个MCP数据连接器、双模式部署（Cowork+Managed Agents API） | 金融科技、投研/投行/PE/财富管理 |
| [**system-prompts**](system-prompts/index.md) | 🟡结构化整理 | 13文档，官方系统提示词发布史：18模型×30日期条目（2024-07→2026-09）全景矩阵、四时代逐条目解析、设计思想演进分析 | 提示词工程师、AI产品研究者 |

## 学习路径建议

### 🚀 快速上手路径
1. 先读 [prompt-engineering](prompt-engineering/index.md) 掌握提示词基础
2. 浏览 [cookbooks](cookbooks/index.md) 找到对应场景的示例
3. 用 [claude-code](claude-code/index.md) 开始交互式开发

### 🔧 生产集成路径
1. 精读 [python-sdk](python-sdk/index.md) 的概念篇（00-09）
2. 参考 [python-sdk/examples](python-sdk/examples/index.md) 的6个示例
3. 学习中间件和错误处理确保生产稳定
4. 多云部署参考 Bedrock/Vertex 适配器

### 🏗️ Agent/插件开发路径
1. 了解 [claude-code](claude-code/index.md) 插件体系
2. 学习 [official-skills](official-skills/index.md) 的SKILL.md格式
3. 使用 [skill-creator](official-skills/concepts/02-skill-creator.md) 创建自定义Skill
4. 参考 [financial-services](financial-services/index.md) 的行业Agent模式

### 🏦 金融行业路径
1. 了解 [financial-services/concepts/00-overview](financial-services/concepts/00-overview.md) 双模式架构
2. 根据业务选择对应Agent或Vertical
3. 配置MCP数据连接器连接内部系统

## 生态关键特性

| 特性 | 说明 | 文档位置 |
|------|------|---------|
| **同步/异步双轨** | Anthropic/AsyncAnthropic完全对称API | [python-sdk/concepts/01-client-init](python-sdk/concepts/01-client-init.md) |
| **Stainless代码生成** | 核心代码自动生成+lib/手动扩展 | [python-sdk/references/source](python-sdk/references/source.md) |
| **流式SSE传输** | Stream/AsyncStream事件驱动 | [python-sdk/concepts/03-streaming](python-sdk/concepts/03-streaming.md) |
| **Tool Use** | Function Calling工具调用范式 | [python-sdk/concepts/04-tool-use](python-sdk/concepts/04-tool-use.md) |
| **多云抽象** | AWS Bedrock + GCP Vertex统一接口 | [python-sdk/concepts/07-multi-cloud](python-sdk/concepts/07-multi-cloud.md) |
| **Beta Agents** | Managed Agents持久化会话 | [python-sdk/concepts/08-beta-agents](python-sdk/concepts/08-beta-agents.md) |
| **Skills扩展** | 可复用能力包+触发式加载 | [official-skills/concepts/00-overview](official-skills/concepts/00-overview.md) |
| **MCP集成** | 模型上下文协议数据连接器 | [python-sdk/concepts/08-beta-agents](python-sdk/concepts/08-beta-agents.md)#mcp支持 |
| **中间件洋葱模型** | 请求/响应拦截与自定义逻辑 | [python-sdk/concepts/09-middleware-extended](python-sdk/concepts/09-middleware-extended.md) |

## 文档统计

| 子Bundle | 概念文档 | 示例/食谱 | 参考文档 | 总文件 |
|---------|---------|----------|---------|-------|
| python-sdk | 10 | 6 | 6 | 24 |
| claude-code | 2 | 1 | 1 | 9 |
| cookbooks | 5 | 0 | 1 | 10 |
| prompt-engineering | 5 | 0 | 0 | 8 |
| official-skills | 4 | 0 | 1 | 9 |
| financial-services | 4 | 0 | 1 | 9 |
| system-prompts | 7 | 0 | 2 | 13 |
| **合计** | **37** | **7** | **12** | **82** |

## 版本说明

本文档基于以下官方仓库版本生成（2026-08-27）：
- anthropic-sdk-python: 最新main分支（含Beta Agents/Memory/Sessions/MCP/Vaults）
- claude-code: 含插件系统、MCP服务器支持
- claude-cookbooks: 含Agent SDK、Computer Use、PDF提取等新食谱
- skills: 含19个官方Skills（含theme-factory、slack-gif-creator等）
- financial-services: 含10个Agents、7个verticals、12个MCP连接器
- prompt-eng-interactive-tutorial: 9章交互式教程
- system-prompts: 官方系统提示词发布页（platform.claude.com），2026-09-02 快照（18模型×30条目）

```{toctree}
:hidden:

python-sdk/index
claude-code/index
cookbooks/index
prompt-engineering/index
official-skills/index
financial-services/index
system-prompts/index
log
```
