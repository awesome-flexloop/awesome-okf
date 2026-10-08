---
okf_version: "0.2"
type: bundle
title: "GPT-6 Sol 与 GPT-6 Luna：低成本 Agent 模型选型"
description: "基于 OpenAI 与 DeepSeek 官方资料核验 GPT-6 Sol/Luna 的价格、模型分工、缓存经济性和 Agent 任务选型边界；技术综述/选型分析，非操作教程。"
tags: [openai, gpt-6, sol, luna, deepseek, agent, model-selection, cost]
generated: { by: "reference_agent/trae", at: "2026-09-23T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T12:00:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: blog
    resource: https://mp.weixin.qq.com/s/1190GW6WFZIzZ8YkDD44eg?from=industrynews&color_scheme=light#rd
  - id: openai-release
    resource: https://openai.com/index/introducing-gpt-6-sol-and-luna/
  - id: deepseek-pricing
    resource: https://api-docs.deepseek.com/quick_start/pricing
  - id: deepseek-release
    resource: https://deepseek.com/en/news/deepseek-v4-1-flash/
---

# GPT-6 Sol 与 GPT-6 Luna：低成本 Agent 模型选型

> **内容性质**：技术综述/产品选型分析，非操作教程；本文不设 `examples/`。核心价格与模型分工已回到官方资料核验，benchmark、第三方实测和内部用量数字保留其来源层级。

## 核心结论

OpenAI 的 GPT-6 产品线形成了“能力上限—专业工作—高吞吐低成本”的分层：Astra 负责最复杂任务，Sol 面向专业工作、编程与 Agent 工作流，Luna 面向规模化、重复性和成本敏感任务（F-003、F-007）。Sol 的 API 价格为 `$2/$10`，Luna 为 `$0.10/$0.50`（输入/输出，每百万 token），均约较对应 GPT-5.6 促销价下降 50%（F-004—F-006）。

## 阅读路径

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```

- [产品线与价格机制](concepts/00-model-lineup-and-pricing.md)
- [Agent 任务经济性](concepts/01-agent-task-economics.md)
- [选型边界与竞争对照](concepts/02-selection-boundaries-and-competition.md)
- [信源与核验](references/index.md)

## 已知边界

- 文章中的 benchmark 数字、内部对话错误率、研究人员 token 消耗和第三方实测均不是本知识包独立复算结果。
- DeepSeek 价格受峰谷时段、缓存命中状态和官方调价影响；对照时必须使用当前官方价表。
- “每任务成本”比 token 单价更适合 Agent 经济性分析，但最终结论仍依赖输入长度、缓存比例、推理强度、工具调用和成功率。

## 主题关联

- [GPT-6 Astra 官方使用指南](../gpt6-astra-usage-guide/index.md)：旗舰模型能力、提示词和 API 行为。
- [DeepSeek-V4 免费方案与 API 定价](deepseek-pricing/index.md)：DeepSeek 价格与免费方案背景。
