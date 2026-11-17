---
type: Concept
title: "四模型阵容与价格"
description: "Claude Haiku 5.5、Sonnet 5.5、Opus 5.5、Fable 5.2 的定位、单价、缓存价、上下文与默认 effort 对照。"
tags: [claude, pricing, model-lineup, effort]
generated: { by: "lobsterai/main", at: "2026-11-10T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T13:30:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: fable-page
    resource: https://www.anthropic.com/claude/fable
  - id: opus-page
    resource: https://www.anthropic.com/claude/opus
  - id: sonnet-page
    resource: https://www.anthropic.com/claude/sonnet
  - id: haiku-page
    resource: https://www.anthropic.com/claude/haiku
---

# 四模型阵容与价格

## 阵容：四个通用档位加一个受控档位

当前通用可用（GA）的 Claude 模型有四个：Haiku 5.5、Sonnet 5.5、Opus 5.5、Fable 5.2（F-003）。另有 Mythos 5.2，与 Fable 5.2 同源，但保留更强的网络安全与生物安全护栏，只通过验证计划向相关机构开放（F-004）。

四个档位不是简单的“新旧替代”，而是按任务强度与预算切分的服务层（F-024）：

1. Haiku 5.5 面向高频、成本敏感、延迟敏感的工作。
2. Sonnet 5.5 面向范围明确、可快速迭代的日常工作。
3. Opus 5.5 是复杂编码与知识工作的日常主力。
4. Fable 5.2 面向最有野心、最开放的长期技术项目。

## 对照表

| 项目 | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 | Fable 5.2 |
|---|---|---|---|---|
| 定位 | 高频低成本 | 范围明确的快速任务 | 复杂编码与知识工作日常主力 | 最难的开放式技术工作 |
| 相对延迟 | 最快 | 快 | 中等 | 中等 |
| 输入/输出（每百万 token） | `$0.10/$0.50`（≤100K）<br>`$0.50/$2.50`（>100K） | `$2/$10` | `$4/$20` | `$8/$40` |
| 缓存读取 | `$0.01`（≤100K）<br>`$0.05`（>100K） | `$0.10`（博文口径，见勘误 E-1） | `$0.20` | `$0.20` |
| 上下文窗口 | 1M | 1M | 1M | 1M |
| 最大输出 | 128K | 128K | 128K | 128K |
| Thinking（API） | 自适应，默认开，可关 | 自适应，默认开，`between_tools` | 自适应，始终开 | 自适应，始终开 |
| 默认 effort（API） | `medium` | `high`（Claude Code 为 `medium`） | `medium` | `high`（Claude Code 为 `medium`） |
| Fast mode | 不支持 | 不支持 | 支持 | 支持 |

数据来源：F-024 至 F-035。价格均为 Claude API 列表价，不含批处理折扣、数据驻留溢价与合同价；Fast mode 溢价另计（F-044）。

## 价格表的三个读法

**第一，单价不是任务成本。** Opus 5.5 的单位 token 价是 Fable 5.2 的一半（F-006），但真正要比较的是“完成同一个任务花多少钱”，后者还取决于 token 用量、轮数、缓存命中与成功率（见 [每完成任务成本](02-task-economics.md)）。

**第二，Haiku 是唯一按提示长度分档的模型。** 100K token 以内走低价档，超过 100K 后输入价变 5 倍、输出价变 5 倍（F-026）。短提示场景下它的输入价只有 Sonnet 的二十分之一；长提示场景下优势收窄到约四分之一（F-048）。

**第三，缓存读取是长任务的隐藏主成本。** 每一轮都会重发上下文，但大部分输入按缓存读取计费（F-045）。Opus 与 Fable 的缓存读价都是 `$0.20`，所以长跑场景里两者的差距主要落在未缓存输入与输出上（F-030）。

## 默认 effort 的双口径

博文表格区分了 API 默认值与 Claude Code 默认值：Haiku 与 Opus 在 API 上是 `medium`，Sonnet 与 Fable 在 API 上是 `high`，但后两者在 Claude Code 中降到 `medium`（F-034）。Claude Code 侧的四模型 `medium` 默认已由官方 model-config 文档确认；API 侧档位为博文单源，见 [核验报告](../references/verification.md) 的 E-2。

实践含义：在 Claude Code 里看到的行为不等于 API 默认行为。写服务端代码时显式传 effort，不要依赖默认值。

## Fast mode 的适用边界

Fast mode 只给 Opus 5.5 与 Fable 5.2，用更高单价换最高 2.5 倍输出速度（F-035、F-044）。它适合“人正在等结果”的交互场景，不适合批处理或后台长跑；后者的瓶颈通常是总成本而不是单轮延迟。
