---
type: Concept
title: "04 计费与限速：按次计费与账号级 QPS"
description: Search/Fetch 按成功请求次数计费（每千次 5 元，不按 token/条数）、成功才计费规则、Harness/Claude Code/Codex 2026-11-01 起收费、账号级 QPS（Search 100 / Fetch 25）与 Fetch 域名级限制。
tags: [DeepSeek, 计费, 限速, QPS, 成本]
generated: { by: reference_agent/glm-5.3-flash, at: 2026-10-19T00:00:00Z }
status: draft
stale_after: 2027-04-19
sources:
  - id: deepseek-search-guide
    resource: https://api-docs.deepseek.com/zh-cn/guides/search/
    title: DeepSeek API 文档——网页搜索与抓取
    last_modified: 2026-10-19
---
# 04 计费与限速：按次计费与账号级 QPS

## 4.1 计费规则

Search 和 Fetch **按请求次数计费**，不按 token 或返回结果条数计费：

| API | 计费单位 | 价格 |
|-----|---------|------|
| Search | 每 1,000 次成功请求 | 5 元 |
| Fetch | 每 1,000 次成功请求 | 5 元 |

### 成功才计费

只有返回 HTTP 200 且产生结果的请求才会计费：

- Search 的 `results` 必须非空；
- Fetch 必须返回网页正文。

请求失败、搜索无结果或超时**不计费**。

### count 不影响价格

`count` 只控制返回的结果条数，不影响单次请求的价格——`count: 1` 与 `count: 50` 单次成本相同。

### 悬浮工具调用收费时间表

当前用户在 DeepSeek Harness / Claude Code / Codex 中使用 DeepSeek API 时，已经会通过 Server 端工具调用访问到 Search/Fetch 接口，这部分调用目前未计费，并将于**北京时间 2026-11-01 00:00 起**按次收取调用费用。

## 4.2 限速规则

对每个账号，Search 和 Fetch **分别独立限速，互不占用额度**：

| API | QPS 限制 |
|-----|---------|
| Search | 100 |
| Fetch | 25 |

### 限速粒度

- QPS（每秒请求数）限制按**账号粒度**计算，与使用哪个 API Key 无关；
- 与模型并发限制相互独立；
- 超过账号级 QPS 限制的请求会收到 HTTP 429 错误码；
- 除账号级限制外，**Fetch 还针对目标域名有 QPS 限制**，超过该限制也会收到 HTTP 429。

## 4.3 容量规划速查

| 维度 | 数值 | 推论 |
|------|------|------|
| 单次请求成本 | 0.005 元 | 成本 ≈ 成功请求数 × 0.005 元 |
| Search 吞吐上限 | 100 QPS | 单账号每日理论上限约 864 万次成功搜索 |
| Fetch 吞吐上限 | 25 QPS（账号级） | 批量抓取任务按此水位设计并发 |
| Fetch 域名级限制 | 官方未公布具体数值 | 抓取同一站点时 429 可能先于账号级水位出现，需按域名分桶退避 |

> 计费与限速均可能调整，以官方文档实时显示为准。
