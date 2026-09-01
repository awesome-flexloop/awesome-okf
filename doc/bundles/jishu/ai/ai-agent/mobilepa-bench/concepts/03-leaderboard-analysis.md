---
type: Concept
title: "榜单解读：v1.5 加权总分与 13 模型"
description: "leaderboard_data.js v1.5 数据出处（paper_v5 Table 1）、Overall 加权公式（0.5/0.2/0.2/0.1）、13 模型分数、Cost/1K 口径（仅可见输出 token）与解读纪律。"
tags: [MobilePA-Bench, leaderboard, 权重公式, 模型榜单, Cost]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobilepa-facts
    resource: /references/facts.md
    title: MobilePA-Bench 与网站事实台账
  - id: mobilepa-sources
    resource: /references/source-registry.md
    title: 信源登记
---

# 榜单解读：v1.5 加权总分与 13 模型

> **事实基础**：本文所有数据与引文均标注 F 编号，完整事实清单见本束 `references/facts.md` A 部分。本文榜单数据出处文件为 `github-pages/static/js/leaderboard_data.js`，版本 v1.5。

MobilePA-Bench 站点 leaderboard 收录 **13 个模型**，总分不是简单平均，而是**四维加权**公式（Tool Use 独占一半权重）。本篇先交代数据出处与版本，再给出分数表与成本口径，最后总结解读纪律。

## 1. 数据出处与权重公式

榜单数据文件 `leaderboard_data.js` 头部注释逐字声明了版本、出处与公式（F-011）：

```javascript
// MobilePA-Bench v1.5 leaderboard data (from paper_v5 Table 1, tab:main_results)
// Overall = 0.5*Tool + 0.2*Memory + 0.2*Skills + 0.1*SubAgent
// info: org used only for optional grouping/badges
```

页面 Leaderboard 章节副标题同式表述（F-013）：

```text
Overall = 50% Tool Use + 20% Memory + 20% Skills + 10% Sub-agent.
```

三条关键信息：①数据版本为 **v1.5**，出自论文 **paper_v5 Table 1（tab:main_results）**；②权重为 **0.5 / 0.2 / 0.2 / 0.1**（Tool / Memory / Skills / SubAgent）；③org 字段仅用于可选分组与徽章，不参与计算（F-011）。页面另注明 "Best value per column is highlighted"（每列最优值高亮，F-013）。

## 2. 13 模型分数表

`LEADERBOARD_DATA` 数组 13 条，每条字段为 model/org/overall/basic/subagent/memory/skills/costPer1k，**列名 basic 对应 Tool Use 维度**（F-012）。按 overall 降序：

| 排名 | 模型 | 机构 | Overall |
|---|---|---|---|
| 1 | Claude-Opus-5 | Anthropic | **75.52**（basic/Tool Use 83.85） |
| 2 | Claude-Fable-5 | Anthropic | 75.31 |
| 3 | Kimi-K3 | Moonshot | 73.01 |
| 4 | Qwen-3.8-Max | Alibaba | 72.51 |
| 5 | Gemini-3.6-Flash | Google | 71.21 |
| 6 | Gemini-3.1-Pro | — | 71.18 |
| 7 | GLM-5.2 | Zhipu | 67.71 |
| 8 | Claude-Opus-4.8 | — | 65.52 |
| 9 | Qwen-3.7-Max | — | 64.71 |
| 10 | Seed-2.1-Pro | ByteDance | 63.65 |
| 11 | GPT-5.6-Sol | OpenAI | 62.68 |
| 12 | GPT-5.5 | — | 61.44 |
| 13 | Kimi-2.6 | — | 55.63 |

数据出处：`github-pages/static/js/leaderboard_data.js`（v1.5，from paper_v5 Table 1）（F-011、F-012）。

> **登记范围说明**：本束台账（F-012）逐字登记了 13 个模型的 org 与 overall，以及榜首 Claude-Opus-5 的 basic 83.85；其余各模型的 subagent/memory/skills/costPer1k 明细分数存于数据文件每条记录，引用时请回查该文件，本束不转录未登记数值。
>
> 另一个值得注意的点：**榜首 Claude-Opus-5（75.52）与次席 Claude-Fable-5（75.31）仅差 0.21**（F-012）——第一名之争远小于维度间的结构性分化。

## 3. Cost/1K 口径

页面口径说明原文（F-014）：

```text
All capability values are percentages (%). Overall is reported only for models
with complete coverage of all four dimensions.

Cost/1K Tasks is estimated from visible output tokens only; input, cached, and
hidden reasoning tokens are excluded.
```

两条纪律：①**Overall 只对四维覆盖完整的模型报告**；②**Cost/1K Tasks 仅按可见输出 token 估算，input、cached 与 hidden reasoning tokens 均被排除**（F-014）。跨模型比较成本时必须带上这个脚注，否则会系统性误读成本优势。

## 4. 榜单解读纪律

综合 F-011~F-014 与维度分布（F-018），引用本榜单时遵循四条纪律：

1. **注明数据出处文件与版本**：`leaderboard_data.js` v1.5（from paper_v5 Table 1），禁止跨信源混拼表格（F-011）。
2. **按维度拆列解读**：引用名次时同时给出四维分——Tool Use 权重 50% 会让总分掩盖 Memory/Skills 维度的模型分化（F-011/F-013、F-018）。
3. **核对 Overall 的适用前提**：只有四维覆盖完整的模型才有 Overall（F-014）。
4. **Cost 引用必带口径脚注**：仅可见输出 token（F-014）。

各维度的 checker 属性差异（Behavior judge 与确定性 checker）见 [02-verification-policy.md](02-verification-policy.md)，它决定了不同维度分数的方差语义。

## 相关概念

- [01-capability-dimensions.md](01-capability-dimensions.md)——四维定义与任务分布（权重的物理来源）
- [02-verification-policy.md](02-verification-policy.md)——checker 类型与分数方差属性
- [00-benchmark-overview.md](00-benchmark-overview.md)——基准性质与私有评测通道
- [../qwen-ui-agent/index.md](../../qwen-ui-agent/index.md)——Qwen-UI-Agent 技术评测束（其中 MobileWorld 82.1% 等分数与本榜单分属不同基准，不可混用）
