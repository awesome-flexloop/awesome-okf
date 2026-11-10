---
type: Concept
title: 五框架全景与 2026 里程碑
description: LangGraph、CrewAI、Microsoft Agent Framework、Pydantic AI、LlamaIndex Workflows 的定位、语言与 2026 版本时间线（含 LlamaIndex 年份勘误）
tags: [LangGraph, CrewAI, Microsoft Agent Framework, Pydantic AI, LlamaIndex, 框架对比]
generated: { by: "blog-article-to-okf-wiki", at: "2026-11-10T14:50:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: dev-article
    resource: https://dev.to/mr_manushukla/2026-ai-agent-frameworks-compared-langgraph-vs-crewai-vs-microsoft-agent-framework-vs-pydantic-ai-4f8k
---

# 五框架全景与 2026 里程碑

原文的判断很直接：到 2026 年 7 月，“哪个框架最新”已经不是好问题，真正的问题是“哪个能在生产里活下来”（F-003）。它选了五个框架，不是按流行度，而是按运行时范式各取一个代表（F-004、F-014）。

## 一张约束地图，而不是排行榜

| 框架 | 2026 里程碑 | 语言 | 核心范式 | 最适合 |
|------|------------|------|---------|--------|
| LangGraph | 1.0 since 2025-10（F-009、F-069） | Python、JavaScript | 显式图状态机 + checkpoint | 精确控制、可审计、长运行、失败可恢复 |
| CrewAI | 生产可用的角色型多 Agent（F-010） | Python | role/goal/backstory + Crew | 快速搭角色团队、PoC、内部工具 |
| Microsoft Agent Framework | 1.0 on 2026-04-03（F-011、F-070） | .NET、Python | Semantic Kernel 底座 + AutoGen 图工作流 | 微软/Azure/.NET 企业栈 |
| Pydantic AI | V2 on 2026-06-23（F-012、F-071） | Python | capability 组合 + Harness | 类型安全、结构化输出校验 |
| LlamaIndex Workflows | 1.0 实际为 2025-06（F-072；原文误写 2026-06-22） | Python、TypeScript | 事件驱动 step + 数据层 | 对索引私有数据做 RAG/推理 |

> **⚠️ 勘误**：原文把 LlamaIndex Workflows 1.0 写成 2026-06-22 发布。PyPI 显示 `llama-index-workflows 1.0.0` 上传于 2025-06-25，2026-10 最新版已是 2.26.1（F-072）。这意味着它比原文暗示的更成熟，而不是更“新”。

## 五种范式，分别优化什么

1. **LangGraph 优化控制力**：你决定每一次状态转移，代价是写更多连接代码（F-016、F-022）。
2. **CrewAI 优化协作速度**：角色是最小心智模型，代价是复杂分支时杠杆变少（F-024、F-027）。
3. **MAF 优化企业整合**：把两套微软 Agent 技术合并，换 .NET/Python 对齐与 Azure 治理（F-030~F-035）。
4. **Pydantic AI 优化输出可信度**：capability 组合 + schema 校验，换更薄的生态（F-041、F-046）。
5. **LlamaIndex 优化数据邻近性**：检索与工作流同处，换编排上的“不预设立场”（F-050、F-051）。

## 为什么不是“选一个最强的”

原文用两个极端说明约束差异：支付公司要长而可审计的工作流，两人创业公司下周要 Demo（F-015）。这两类需求对“状态、恢复、审计、上线速度”的权重完全不同，因此不存在跨场景的最优解（F-005、F-054）。

更常见的现实是分层：原型层用最快的框架，记录系统层用最稳的框架（F-055、F-065）。这条主线在 [选型与生产就绪](04-selection-and-production-readiness.md) 展开。

## 阅读顺序建议

1. 先看 [LangGraph：控制与持久化](01-langgraph-control-and-durability.md)，理解“状态机 + checkpoint”这条基线。
2. 再看 [CrewAI 与 MAF](02-crewai-speed-and-maf-enterprise-merge.md)，理解“角色协作”和“企业合并”两种相反取舍。
3. 然后看 [Pydantic AI 与 LlamaIndex](03-pydantic-ai-and-llamaindex.md)，理解“类型安全”和“数据层”两条专精路线。
4. 最后用 [选型矩阵](04-selection-and-production-readiness.md) 对照自己的主导约束。

## 信源边界

原文是 eCorpIT 的服务型内容，含自述与推销段落，且声明使用 AI 辅助研究（F-006、F-007）。本知识包只保留可核验的版本、能力与选型逻辑；服务推销、区域报价与未具名案例不计入事实层。完整核验见 [事实核验报告](../references/verification.md)。
