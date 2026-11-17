---
type: Concept
title: Pydantic AI 与 LlamaIndex Workflows
description: capability/Harness 带来的类型安全路线，与事件驱动 step 框架在私有数据检索场景的定位
tags: [Pydantic AI, LlamaIndex, Workflows, capability, Harness, RAG, 类型安全]
generated: { by: "blog-article-to-okf-wiki", at: "2026-11-10T14:50:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: pydantic-v2
    resource: https://pydantic.dev/articles/pydantic-ai-v2
  - id: llamaindex-docs
    resource: https://developers.llamaindex.ai/python/llamaagents/workflows/
---

# Pydantic AI 与 LlamaIndex Workflows

这两个框架不抢“全能编排”的位置，而是各守一个专精：Pydantic AI 守“输出可信”，LlamaIndex 守“数据邻近”。

## Pydantic AI V2：把 Agent 拆成可组合的 capability

V2 于 2026 年 6 月 23 日稳定，核心变化是 **harness-first**（F-040）。它只引入一个中心概念：**capability**——把工具、指令、生命周期钩子、模型设置打包成一个可复用单元（F-041）。Agent 不再手工逐项接线，而是由 capability 组装（F-042）。

这带来两个直接后果：

1. **横切能力可以复用**：记忆、护栏、审批这类“每个 Agent 都要一点”的东西，变成可插拔单元，而不是复制粘贴。
2. **校验成为结构的一部分**：Pydantic schema 在步骤之间拦截畸形输出，让错误在进入下游系统前暴露（F-045）。

一等方包 **Harness** 提供记忆、护栏、沙箱代码执行等预置能力（F-043），并集成 MCP 与 human-in-the-loop 工具审批（F-044）。官方文档进一步列出记忆、护栏、子 Agent、规划、上下文压缩、持久化与 coding agent 等 capability；沙箱执行由 Monty 等组件承担（F-077）。

### 边界

Pydantic AI 只支持 Python（F-046）。作为 V2，它比 LangGraph 作为 1.0 更年轻，示例生态更薄（F-046）。它也不试图解决“多 Agent 图编排”的全部问题——那仍是 LangGraph/MAF 的领域。

### 什么时候选它

当你的痛点是“模型输出不可预测、未校验”，而不是“编排太复杂”时，类型安全路径很快回本（F-047）。典型场景：结构化抽取、表单填充、跨系统传参、需要编译器与 schema 双重兜底的业务流程。

## LlamaIndex Workflows：事件驱动的数据层

先把日期纠正：原文称 Workflows 1.0 于 2026-06-22 发布，但 PyPI 显示 1.0.0 上传于 **2025-06-25**，2026-10 最新版为 **2.26.1**（F-072）。所以它不是“刚稳定的新框架”，而是已经迭代一年多的成熟包。

它的模型很小：应用被拆成 step，每个 step 接收一个事件、做一件事、返回另一个事件；返回的事件触发下一个能接收它的 step（F-048、F-076）。分支是普通 `if`，循环是返回更早 step 能处理的事件，并发是返回事件列表。官方文档强调 async-first，并提供状态序列化/恢复与可观测性（F-076）。

### 定位：检索与工作流同处

LlamaIndex 的血统是数据层（F-050）。当 Agent 的主要工作是对索引私有数据做推理时，检索与工作流放在同一个框架里，比“检索一个工具 + 编排另一个框架”少一层缝合（F-052）。

它有意对编排保持不预设立场（F-051）：

1. 想要轻量事件核心的人，会觉得它干净。
2. 想要开箱多 Agent 模式的人，会觉得它缺电池。

因此原文的建议是：RAG over 自有文档是产品中心时选它；否则把检索框架与独立编排层组合，保持边界清晰（F-052、F-053）。

## 两条路线的对照

| 维度 | Pydantic AI V2 | LlamaIndex Workflows |
|------|----------------|----------------------|
| 中心抽象 | capability | step + event |
| 最强处 | 类型安全、结构化输出、校验 | 检索与工作流同处、数据层 |
| 语言 | Python（F-046） | Python、TypeScript（F-049） |
| 编排立场 | 提供 Agent 循环与 Harness，但不做重图编排 | 有意不预设，轻事件核心 |
| 适合 | 输出必须可信的业务流程 | 私有文档 RAG 为中心的产品 |
| 主要代价 | 生态较薄、仅 Python | 多 Agent 模式需自建 |

## 与本站其他知识包的关系

- Pydantic 生态与校验思路可对照 [microsoft-agent-framework](../../../microsoft-agent-framework/index.md) 中的类型安全章节。
- RAG 与检索工程见 [agent-knowledge-base](../../agent-knowledge-base/index.md)。
- 事件驱动编排可与 [agent-runtime-protocol](../../agent-runtime-protocol/index.md) 的 Run/Step 模型对照。
