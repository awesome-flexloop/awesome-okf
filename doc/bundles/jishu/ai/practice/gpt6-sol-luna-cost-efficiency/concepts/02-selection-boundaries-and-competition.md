---
type: Concept
title: "选型边界与 DeepSeek 竞争对照"
description: "梳理 GPT-6 Sol/Luna 与 DeepSeek V4.1 Flash 的证据边界、适用性和竞争判断。"
tags: [model-selection, deepseek, openai, benchmark, evidence]
generated: { by: "reference_agent/trae", at: "2026-09-23T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T12:00:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: openai
    resource: https://openai.com/index/introducing-gpt-6-sol-and-luna/
  - id: deepseek
    resource: https://api-docs.deepseek.com/quick_start/pricing
---

# 选型边界与 DeepSeek 竞争对照

## 已核实的竞争变化

文章的主判断是：Luna 的普通输入/输出价格进入 DeepSeek V4.1 Flash 的竞争区间，头部模型的价格优势不再由单一厂商独占（F-023）。这一判断可作为市场观察，但具体价格必须按同一币种、同一峰谷时段、同一缓存状态和同一任务口径重算。

DeepSeek 官方资料确认 V4.1-Flash 具备 1M 上下文、原生多模态和峰谷/缓存差异化计价（F-010、F-011）。因此，“谁更便宜”至少有三种答案：缓存命中时谁更便宜、普通请求谁更便宜、完成同一任务谁更便宜。

## benchmark 的正确用法

文章转述了 AutomationBench、Agents’ Last Exam、DeepSWE 和 OSWorld 的多个分数与成本差异（F-013—F-016）。这些数字应被当作发布方在特定配置下的结果，而不是跨平台、跨推理强度、跨提示词的普遍排名。

第三方 Three.js 实测和 Artificial Analysis 摘要也只能说明某些工作负载下的观察（F-024、F-025）。选型时应复现自己的任务集，并保留模型版本、推理档位、工具、上下文和价格日期。

## 决策边界

1. 需要最高能力上限且任务价值高：先评估 Astra。
2. 需要专业工作、编程和 Agent 迭代，且预算敏感：优先把 Sol 纳入对照。
3. 需要高吞吐、低单次成本和可接受误差：把 Luna 作为默认候选。
4. 需要极低缓存命中成本、国产生态或特定部署路径：同时评估 DeepSeek V4.1 Flash。
5. 任何结论都必须以自有任务的“每任务成本 + 成功率”复核。
