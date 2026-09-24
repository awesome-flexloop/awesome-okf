---
type: Concept
title: "GPT-6 产品线与价格机制"
description: "解释 Astra、Sol、Luna 的分工，以及 API 单价、缓存和峰谷价格的比较口径。"
tags: [gpt-6, openai, pricing, caching]
generated: { by: "reference_agent/trae", at: "2026-09-23T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T12:00:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: openai
    resource: https://openai.com/index/introducing-gpt-6-sol-and-luna/
---

# GPT-6 产品线与价格机制

## 三层分工

OpenAI 的官方叙述把 GPT-6 家族按任务强度和预算分层：Astra 面向最具挑战性的工作；Sol 是更通用的专业工作模型；Luna 是面向高吞吐量工作的更高性价比模型（F-003、F-007）。

这不是简单的“新模型替代旧模型”，而是把同一能力家族拆成不同的服务档位：需要更深推理和更高成功率的任务使用 Astra 或 Sol，规模化抽取、路由、摘要和批处理更适合先评估 Luna。

## API 价格

| 模型 | 输入（美元/百万 token） | 输出（美元/百万 token） | 相对对应 GPT-5.6 促销价 |
|---|---:|---:|---|
| GPT-6 Sol | 2 | 10 | 约低 50% |
| GPT-6 Luna | 0.10 | 0.50 | 约低 50% |

上述数字来自 OpenAI 发布页（F-004—F-006）。实际账单还会受缓存输入、输出长度、推理强度和处理优先级影响。

## 与 DeepSeek 对照时的口径

文章用 DeepSeek V4.1 Flash 做价格参照（F-009）。DeepSeek 官方价表同时区分缓存命中、缓存未命中、输出 token 和峰谷时段（F-011），因此不能只比较一个“每百万 token 价格”。官方还将模型名、上下文长度和能力列为独立字段，V4.1-Flash 的 API 名称为 `deepseek-flash`、上下文长度为 1M（F-010）。

## 选择原则

价格表只回答“单位 token 花多少钱”。对 Agent 系统，至少还要测量成功率、平均迭代轮数、缓存命中率、工具调用次数和完成一项任务的总成本。
