---
type: Reference
title: 事实核验报告
description: 2026 五框架对比文 13 项 P0 声明核验（8 通过 3 部分 1 失败 1 自述），含 LlamaIndex 1.0 年份勘误、A2A 表述降级、Replit 单源
tags: [核验, P0, 勘误, LangGraph, CrewAI, MAF, Pydantic AI, LlamaIndex]
generated: { by: "blog-article-to-okf-wiki", at: "2026-11-10T14:50:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: langgraph-release
    resource: https://github.com/langchain-ai/langgraph/releases/tag/1.0.0
    title: LangGraph 1.0.0 release
  - id: maf-blog
    resource: https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/
    title: Microsoft Agent Framework Version 1.0
  - id: maf-learn
    resource: https://learn.microsoft.com/en-us/agent-framework/overview/
    title: Microsoft Agent Framework Overview
  - id: pydantic-v2
    resource: https://pydantic.dev/articles/pydantic-ai-v2
    title: Pydantic AI v2: capable agentic loops
  - id: pydantic-docs
    resource: https://pydantic.dev/docs/ai/overview/
    title: Pydantic AI documentation
  - id: workflows-pypi
    resource: https://pypi.org/project/llama-index-workflows/1.0.0/
    title: llama-index-workflows 1.0.0 on PyPI
  - id: llamaindex-docs
    resource: https://developers.llamaindex.ai/python/llamaagents/workflows/
    title: LlamaIndex Workflows documentation
  - id: langgraph-customers
    resource: https://www.langchain.com/built-with-langgraph
    title: Built with LangGraph
---

# 事实核验报告

> 核验对象：DEV/eCorpIT《2026 AI agent frameworks compared》。
> 核验日期：2026-11-10。
> 结果：**8 项通过（✅）、3 项部分通过（⚠️）、1 项失败（❌）、1 项自述不可核验（🏷️）**。

## 1. 核验结论总览

| # | 声明 | 结论 | 对应事实 |
|---|------|------|---------|
| 1 | LangGraph 1.0 于 2025 年 10 月发布 | ✅ 通过 | F-009 / F-069 |
| 2 | LangGraph 生产用户含 Uber/Klarna/LinkedIn/Replit/Elastic/AppFolio | ⚠️ 部分通过（5/6） | F-021 / F-075 |
| 3 | MAF 1.0 于 2026-04-03 发布，合并 SK 与 AutoGen | ✅ 通过 | F-011 / F-030 / F-070 |
| 4 | MAF 支持六个模型提供方 | ✅ 通过 | F-037 / F-073 |
| 5 | MAF 的 MCP 与 A2A 在 1.0 原生支持 | ⚠️ 部分通过（A2A 待补齐） | F-036 / F-074 |
| 6 | Pydantic AI V2 于 2026-06-23 稳定 | ✅ 通过 | F-012 / F-040 / F-071 |
| 7 | Pydantic AI V2 的 capability/Harness 能力 | ✅ 通过 | F-041~F-044 / F-077 |
| 8 | LlamaIndex Workflows 1.0 于 2026-06-22 发布 | ❌ 失败（年份错误） | F-013 / F-048 / F-072 |
| 9 | LlamaIndex Workflows 技术特征（事件驱动/async-first/step） | ✅ 通过 | F-048 / F-076 |
| 10 | 五个框架现在都支持 MCP | ⚠️ 部分通过（未逐框架核验） | F-058 |
| 11 | 前沿模型每 100 万输入 token 1~5 美元 | 🏷️ 不可独立核验 | F-061 / F-080 |
| 12 | CrewAI 团队“不到一周上线” | 🏷️ 作者/厂商自述 | F-026 / F-080 |
| 13 | 印度 DPDP Act 2023 适用于 Agent 日志与检索数据 | ✅ 通过（法案存在） | F-068 |

## 2. 通过项详情

### ✅ LangGraph 1.0 日期（F-009 / F-069）
- 博文：1.0 since October 2025。
- 核验：GitHub `langchain-ai/langgraph` 的 `1.0.0` release `published_at` 为 2025-10-17；与“2025 年 10 月”一致。
- 结论：通过。

### ✅ MAF 1.0 日期与合并（F-011 / F-030 / F-070）
- 博文：shipped April 3, 2026，合并 Semantic Kernel 与 AutoGen。
- 核验：微软官方博客标题日明确写 “April 3rd, 2026”，并说明同时面向 .NET 与 Python；GitHub `python-1.0.0` 与 `dotnet-1.0.0` 标签发布于 2026-04-02 UTC（时区差异导致显示为 4 月 2 日）。
- 结论：通过，日期采用微软公告口径。

### ✅ MAF 六个模型提供方（F-037 / F-073）
- 博文：Azure OpenAI、OpenAI、Anthropic Claude、Amazon Bedrock、Google Gemini、Ollama。
- 核验：1.0 公告列出 Microsoft Foundry、Azure OpenAI、OpenAI、Anthropic Claude、Amazon Bedrock、Google Gemini、Ollama；博文把 Foundry 作为平台而非“模型提供方”，六个模型连接器一致。
- 结论：通过。

### ✅ Pydantic AI V2 日期与能力（F-012 / F-040~F-044 / F-071 / F-077）
- 博文：2026-06-23 stable，harness-first，capability 打包工具/指令/钩子/设置，Harness 提供记忆、护栏、沙箱执行，集成 MCP 与 HITL 审批。
- 核验：GitHub `v2.0.0` 与官方文章日期均为 2026-06-23；官方文档确认 capability 原语与 Harness 的记忆/护栏/子 Agent/规划/压缩/持久化能力；沙箱执行由 Monty 等组件承担。
- 结论：通过。补充：官方文档把“sandboxed code execution”表述为 Harness 生态能力，博文概括为 Harness 预置能力，属合理简化。

### ✅ LlamaIndex Workflows 技术特征（F-048 / F-076）
- 博文：轻量、事件驱动、async-first、step-based，Python + TypeScript。
- 核验：官方文档首段即定义为 “event-driven, step-based way to control the execution flow”；包元数据为 async-first；官方文档另有状态序列化/恢复、可观测性页面；TypeScript 包独立存在。
- 结论：技术特征通过；发布日期另见勘误。

### ✅ 印度 DPDP Act 2023（F-068）
- 博文：Agent 日志与检索到的客户数据属于个人数据，受 DPDP Act 2023 管辖。
- 核验：印度《Digital Personal Data Protection Act, 2023》已生效，适用于数字化个人数据处理的场景。
- 结论：法案存在与适用方向通过；具体合规义务需法律意见，博文不构成法律建议（F-008）。

## 3. 部分通过项

### ⚠️ LangGraph 生产用户（F-021 / F-075）
- 博文：Uber、Klarna、LinkedIn、Replit、Elastic、AppFolio。
- 核验：LangChain 官方 “Built with LangGraph” 页面列出 LinkedIn、Uber、Klarna、Elastic、AppFolio 五家，并给出案例链接；页面未列 Replit。
- 结论：5/6 官方确认；Replit 仅博文单源，正文标注“另有 Replit 未在官方客户页列出”。

### ⚠️ MAF 的 A2A 原生支持（F-036 / F-074）
- 博文：“MCP plus A2A are native at 1.0, not bolt-ons”。
- 核验：1.0 公告写 “A2A (Agent-to-Agent) protocol (A2A 1.0 support coming soon) support enables cross-runtime agent collaboration”；即 A2A 集成存在，但 A2A 1.0 规范支持仍在补齐。
- 结论：降级为“MCP 原生；A2A 已有集成，1.0 时规范支持仍在 coming soon”。

### ⚠️ 五框架均支持 MCP（F-058）
- 博文：every one of these frameworks now speaks MCP。
- 核验：MAF 与 Pydantic AI 官方文档明确；LangGraph 有 MCP 适配文档；LlamaIndex 有 MCP 集成；CrewAI 有 MCP 支持。但本次未逐框架回官方文档逐条取证，且“支持程度”（客户端/服务端/工具发现）差异未展开。
- 结论：方向正确，表述降级为“均宣称/提供 MCP 集成，深度需按框架查文档”。

## 4. 失败项与勘误

### ❌ LlamaIndex Workflows 1.0 发布日期（F-013 / F-048 / F-072）
- 博文：1.0 was announced on June 22, 2026。
- 核验：PyPI `llama-index-workflows` 的 `1.0.0` 上传时间为 **2025-06-25**；截至 2026-10-21 最新版为 **2.26.1**。LlamaIndex 官方博客中 Workflows 最早随 LlamaIndex 0.11 于 2024-08-22 引入。
- 判定：**年份错误**，正确表述应为“Workflows 1.0 于 2025 年 6 月发布，至 2026 年已迭代到 2.x”。
- 影响：不改变“LlamaIndex 适合数据层 RAG”的选型结论；但会低估其成熟度（原文暗示“刚稳定”，实际已稳定约一年半）。
- 处置：正文使用正确值，并标注“原文写 2026-06-22，经 PyPI 核验为年份错误”；bundle 维持 `stable`（非核心结论失败，勘误完整）。

## 5. 不可核验项（自述/区间）

### 🏷️ “不到一周上线”（F-026）
- 属团队反馈的二手转述，无客户名、无项目细节、无独立出处。正文标注“作者/厂商自述”，不作为选型硬指标。

### 🏷️ 每 100 万输入 token 1~5 美元（F-061）
- 2026 年中期前沿模型价格确实落在该宽区间，但不同模型、缓存命中、批处理、输入/输出计价差异极大，无法用单一区间做预算。正文保留区间并提示“按目标模型现价核算”。

### 🏷️ “一行代码切换模型”（F-038）
- 厂商宣传语；实际切换涉及认证、模型能力差异、工具调用格式与评测回归。正文明确标注“宣传性表述”。

## 6. 核验方法与边界

- 版本日期优先用 GitHub Releases `published_at` 与 PyPI `upload_time`，其次用官方公告。
- 能力声明优先用官方文档首屏定义；未逐页深挖实现细节。
- 用户名单只用官方客户页；未出现者标“单源”。
- 价格不引第三方聚合站作为唯一证据；保留原文区间并标注不可精算。
- 核验截止 2026-11-10；框架迭代快，`stale_after` 前需复查。
