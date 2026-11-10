---
okf_version: "0.2"
type: bundle
title: "2026 AI Agent 框架选型：LangGraph / CrewAI / MAF / Pydantic AI / LlamaIndex"
description: "五框架横向选型——各自范式、2026 版本里程碑、生产就绪维度、token 成本与按主导约束决策的双框架分层策略"
tags: [AI Agent, 框架选型, LangGraph, CrewAI, Microsoft Agent Framework, Pydantic AI, LlamaIndex, MCP, 生产就绪]
generated: { by: "blog-article-to-okf-wiki", at: "2026-11-10T14:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:10:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: dev-article
    resource: https://dev.to/mr_manushukla/2026-ai-agent-frameworks-compared-langgraph-vs-crewai-vs-microsoft-agent-framework-vs-pydantic-ai-4f8k
    title: "2026 AI agent frameworks compared（DEV，2026-07-18）"
  - id: ecorpit-original
    resource: https://ecorpit.com/ai-agent-framework-production-langgraph-crewai-microsoft-pydantic-2026/
    title: "eCorpIT 原文（2026-07-19 更新）"
  - id: langgraph-release
    resource: https://github.com/langchain-ai/langgraph/releases/tag/1.0.0
    title: LangGraph 1.0.0
  - id: maf-blog
    resource: https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/
    title: Microsoft Agent Framework Version 1.0
  - id: pydantic-v2
    resource: https://pydantic.dev/articles/pydantic-ai-v2
    title: Pydantic AI v2
  - id: workflows-pypi
    resource: https://pypi.org/project/llama-index-workflows/1.0.0/
    title: llama-index-workflows 1.0.0
---

# 2026 AI Agent 框架选型

> **⚠️ 信源性质**：本文基于 eCorpIT（印度 AI 开发服务商）的服务型对比文，原文声明“AI 辅助研究 + 编辑复核”，并含服务推销段落。本知识包只保留可核验的版本、能力与选型逻辑；作者观点标 📝，厂商自述标 🏷️。
>
> **⚠️ 已知勘误（1 项）**：原文称 LlamaIndex Workflows 1.0 于 2026-06-22 发布，经 PyPI 核验实际为 **2025-06-25**（至 2026-10 已到 2.26.1）。正文已用正确值，详见 [事实核验报告](references/verification.md)。另有 2 项表述降级（MAF 的 A2A“原生”、五框架“都支持 MCP”）与 1 项用户名单单源（Replit）。

## 这项对比解决什么问题

到 2026 年 7 月，Agent 框架的问题已经不是“哪个最新”，而是“哪个能在生产里活下来”（F-003）。原文选了五个范式代表，主张从**主导约束**出发选型，而不是从 Star 数或功能清单出发（F-005、F-054）。

| 字段 | 值 |
|------|---|
| 原文标题 | 2026 AI agent frameworks compared: LangGraph vs CrewAI vs Microsoft Agent Framework vs Pydantic AI |
| 作者/来源 | Manu Shukla / eCorpIT（DEV 转载 2026-07-18，原文更新 2026-07-19） |
| 信源距离 | 第三方服务商综述（含厂商自述与推销内容） |
| 覆盖框架 | LangGraph、CrewAI、Microsoft Agent Framework、Pydantic AI、LlamaIndex Workflows |
| 状态 | stable（1 项非核心勘误已完整落实） |
| 复核期限 | 2027-01-31（框架版本迭代快） |

## 五框架一览

| 框架 | 2026 里程碑 | 语言 | 核心范式 | 最适合 |
|------|------------|------|---------|--------|
| LangGraph | 1.0 since 2025-10 | Python、JS | 图状态机 + checkpoint | 精确控制、长运行、可审计 |
| CrewAI | 生产可用的角色型多 Agent | Python | 角色 crew | 快速原型、角色型协作 |
| Microsoft Agent Framework | 1.0 on 2026-04-03 | .NET、Python | SK 底座 + AutoGen 图工作流 | 微软/Azure 企业栈 |
| Pydantic AI | V2 on 2026-06-23 | Python | capability + Harness | 类型安全、输出校验 |
| LlamaIndex Workflows | 1.0 实际 2025-06（原文误写 2026-06-22） | Python、TS | 事件驱动 step + 数据层 | 私有数据 RAG |

## 从约束到首选

| 你的主导约束 | 首选 |
|-------------|------|
| 失败恢复、逐步审计、长运行 | LangGraph |
| 两周内验证角色协作 | CrewAI |
| 已标准化在 Azure/.NET | Microsoft Agent Framework |
| 结构化输出必须可信 | Pydantic AI V2 |
| 产品核心是私有文档检索 | LlamaIndex Workflows |

更完整的生产就绪对比、成本结构与“原型层/记录系统层”双框架策略，见 [选型矩阵、生产就绪与成本](concepts/04-selection-and-production-readiness.md)。

## 知识结构

```
agent-framework-selection-2026/
├── concepts/                                  # 5 篇
│   ├── 00-five-frameworks-landscape.md        # 五框架全景与里程碑（含勘误）
│   ├── 01-langgraph-control-and-durability.md # 图状态机与持久执行
│   ├── 02-crewai-speed-and-maf-enterprise-merge.md
│   ├── 03-pydantic-ai-and-llamaindex.md
│   └── 04-selection-and-production-readiness.md
├── references/                                # 2 篇
│   ├── article-source.md                      # F-001~F-081
│   └── verification.md                        # 13 项 P0 核验与勘误
├── index.md
└── log.md
```

## 文档导航

| 文档 | 类型 | 一句话简介 |
|------|------|-----------|
| [五框架全景与 2026 里程碑](concepts/00-five-frameworks-landscape.md) | 概念 | 五种运行时范式、语言与版本时间线；LlamaIndex 年份勘误 |
| [LangGraph：控制与持久化](concepts/01-langgraph-control-and-durability.md) | 概念 | checkpoint/resume、HITL、五家官方客户与“啰嗦换控制” |
| [CrewAI 与 MAF](concepts/02-crewai-speed-and-maf-enterprise-merge.md) | 概念 | 角色协作的速度取舍；SK+AutoGen 合并、双语言对齐、MCP/A2A 边界 |
| [Pydantic AI 与 LlamaIndex](concepts/03-pydantic-ai-and-llamaindex.md) | 概念 | capability/Harness、schema 校验；事件驱动 step 与数据层定位 |
| [选型矩阵与生产就绪](concepts/04-selection-and-production-readiness.md) | 概念 | 约束决策表、token 成本、双框架分层、安全边界 |
| [博文事实清单](references/article-source.md) | 信源 | F-001~F-081 完整登记，观点/自述分层 |
| [事实核验报告](references/verification.md) | 信源 | 7✅/3⚠️/1❌/2🏷️，含勘误与方法 |

## 三条核心结论

1. **选型先问失败代价**：需要恢复与审计时，checkpoint 与状态归属比“多 Agent 功能”更重要（F-018~F-023）。
2. **双框架是分层而非妥协**：原型层求快、记录系统层求稳；迁移与评测 harness 才是主要成本（F-055、F-065~F-067）。
3. **框架不提供默认安全**：提示注入、工具误用、未校验输出仍需独立护栏（F-081）。

## 主题关联

| 关联知识包 | 关系 |
|-----------|------|
| [microsoft-agent-framework](../../microsoft-agent-framework/index.md) | MAF 单框架完整官方文档教程（10 概念 + 5 示例），本文只做横向定位 |
| [langchain-ai/langgraph](../../langchain-ai/langgraph/index.md) | LangGraph 源码/架构细节，本文只讲选型相关机制 |
| [agent-runtime-protocol](../agent-runtime-protocol/index.md) | Thread/Run/Step/Checkpoint 等运行时协议抽象，可与本文持久执行对比 |
| [a2a-mcp-convergence](../a2a-mcp-convergence/index.md) | MCP 与 A2A 的协议分工，补足本文“协议原生”讨论 |
| [agent-knowledge-base](../agent-knowledge-base/index.md) | RAG 与知识库工程，补足 LlamaIndex 数据层场景 |
| [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) | Agent 六大架构模式，本文的选型基线 |

## 核验摘要

- P0 核验：13 项 → 7 项通过、3 项部分通过、1 项失败、2 项自述不可核验
- 已确认勘误：1 项（LlamaIndex Workflows 1.0 年份）
- 表述降级：2 项（MAF A2A“原生”、五框架“都支持 MCP”）
- 单源标注：1 项（Replit 生产用户）
- 核心选型结论未受勘误影响，故 `status: stable`

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
