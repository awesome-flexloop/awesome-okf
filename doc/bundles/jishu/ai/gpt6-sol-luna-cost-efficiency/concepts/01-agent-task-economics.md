---
type: Concept
title: "Agent 任务经济性：从 token 单价到完成成本"
description: "将模型选择从单价比较扩展到任务完成成本、缓存复用和推理强度的组合评估。"
tags: [agent, economics, cost-per-task, caching, evaluation]
generated: { by: "reference_agent/trae", at: "2026-09-23T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T12:00:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: openai
    resource: https://openai.com/index/introducing-gpt-6-sol-and-luna/
  - id: azure
    resource: https://azure.microsoft.com/en-us/blog/gpt-6-astra-sol-and-luna-for-production-agents-in-microsoft-foundry/
---

# Agent 任务经济性：从 token 单价到完成成本

## 为什么要换指标

一个 Agent 任务的成本不是输入 token 单价乘以一次请求。它还包含历史上下文、缓存命中、输出长度、推理强度、工具调用、失败重试和人工接管。OpenAI 与 Microsoft Foundry 的相关资料都强调应观察“每任务成本”以及生产任务的完成效果（F-012）。

可以使用下列非官方估算式建立统一口径：

```text
任务成本 =
输入成本 + 缓存输入成本 + 输出成本
+ 工具/检索成本 + 重试成本 + 人工复核成本
```

这只是分析模板，不是 OpenAI 官方计费公式；落地时应以账单字段和任务日志为准。

## 三类任务

| 任务类型 | 首选候选 | 关键指标 |
|---|---|---|
| 高难度专业工作、复杂编程、长链路 Agent | Astra 或 Sol | 成功率、可合并率、人工接管率、每任务成本 |
| 高频路由、摘要、抽取、批量预处理 | Luna | 吞吐、延迟、单位任务成本、错误率 |
| 长上下文持续协作 | Sol/Luna 先测，必要时升级 Astra | 缓存命中率、上下文复用、上下文窗口、重试次数 |

Sol/Luna 对 Astra 能力的继承是 OpenAI 的产品声明（F-008），不能替代针对自身数据的评测。

## 缓存的经济效应

OpenAI 宣称 GPT-6 的缓存读取可获得 90% 折扣，并允许在保留上下文缓存的情况下调整推理强度或工具（F-019、F-020）。这意味着固定系统提示、代码库索引和历史对话的重复读取可能比一次性的公开单价下降更影响总账单。

## 评测建议

建立至少四个分桶：简单批处理、普通 Agent、长链路编程、人工高价值任务。每个桶记录成功率、平均 token、缓存比例、工具次数、重试次数、人工时长和总费用，再比较模型，而不是只抄录文章的 benchmark 数字（F-013—F-018）。
