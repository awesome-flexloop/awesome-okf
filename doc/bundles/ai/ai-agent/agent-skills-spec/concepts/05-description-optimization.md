---
type: Concept
title: Description 优化：触发机制与防过拟合实验
description: description 作为技能路由函数的优化方法学——触发机制与能力阈值限定、四条写作原则、触发率测量（3 次运行/0.5 阈值）、near-miss 负例设计与 60/40 训练验证切分防过拟合。
tags: [agent-skills, skill-format, description, trigger-optimization, overfitting, evaluation]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: optimizing-mdx
    resource: /references/spec-sources.md
    title: docs/skill-creation/optimizing-descriptions.mdx
  - id: spec-mdx
    resource: /references/spec-sources.md
    title: docs/specification.mdx description 字段约束
---

# Description 优化：触发机制与防过拟合实验

`description` 字段是智能体决定**是否为给定任务加载技能**的首要机制（F-035）。在渐进式披露架构下，它是唯一常驻上下文的技能表面——欠规定（under-specified）意味着该触发时不触发，过宽（over-broad）意味着不该触发时误触发，污染每一次任务的路由决策。官方为此专门提供了一篇优化指南，其方法论直接借用 ML 实验的 train/validation 切分来保护这一个 YAML 字段（F-040）。

## 触发机制与能力阈值限定

一个反直觉的限定（F-035）：智能体通常只在任务需要其自身知识/能力之外的东西时才查询技能。**简单的单步请求（如 "read this PDF"）即使 description 完全匹配也可能不触发**；陌生 API、领域特定工作流、不常见格式等需要专门知识的任务，才是 description 发挥作用的地方。

推论：description 优化的目标函数不是"相关性"，而是"超出基线能力时的可召回性"。

## 写作四原则

1. **祈使式措辞**："Use this skill when..." 而非 "This skill does..."（F-036）。
2. **聚焦用户意图**而非实现机制。
3. **宁可 "pushy"**：显式列出适用场景，包括用户没有直接点名领域的情形（"even if they don't explicitly mention 'CSV' or 'analysis.'"）。
4. **保持简洁**：规范对 description 有 1024 字符硬限制（F-036、F-007）。

## 触发评估查询集

查询集存于 `eval_queries.json`，条目形如（F-037）：

```json
{"query": "I need to analyze this CSV", "should_trigger": true}
```

建议约 **20 条**（8-10 条应触发 + 8-10 条不应触发）。应触发查询沿四个轴变化（F-037）：

| 轴 | 变化范围 |
|---|---|
| 措辞 | formal / casual / typos |
| 显式度 | 直接点名领域 vs 只描述需求 |
| 细节量 | terse vs 带文件路径列名背景的冗长 |
| 复杂度 | 单步 vs 埋在长链中的多步 |

最有价值的应触发用例是"技能帮得上忙但连接不明显"的那类。

## 负例设计：near-miss 优先

不应触发用例中最有价值的是 **near-miss（近失）查询**——与技能共享关键词或概念但实际需要别的东西（F-038）。弱负例（"Write a fibonacci function"、"What's the weather today?"）测不出什么。针对 CSV 分析技能的强负例：

- "I need to update the formulas in my Excel budget spreadsheet"
- "can you write a python script that reads a csv and uploads each row to our postgres database"

## 触发率测量

每个查询跑多次（**3 次为合理起点**）计算 trigger rate（技能被调用的运行占比）（F-039）。判定条件：

- 应触发查询：trigger rate **高于阈值**（**0.5 为合理默认值**）；
- 不应触发查询：trigger rate 低于该阈值。

参考检测脚本用 `claude -p "$query" --output-format json` 输出经 jq 匹配技能是否被调用：

```bash
any(.messages[].content[]; .type == "tool_use" and .name == "Skill" and .input.skill == $skill)
```

文中提示该检测逻辑可替换为各客户端自己的实现（F-039）。

## 防过拟合划分与优化循环

**60/40 切分**（F-040）：训练集约 60%、验证集约 40%，两集都按比例混含正负例；划分随机生成后**跨迭代固定**。只用训练集失败指导修改；验证集结果**不进入**修改过程。

**循环五步**：

1. **双集评估**：对训练集与验证集分别测触发率；
2. **训练集失败定位**：找出未达标查询；
3. **修订 description**：避免照抄失败查询的关键词——那是过拟合，应归纳其一般类别；若干轮无进展则尝试结构性不同的写法；随时检查 1024 字符上限——"descriptions tend to grow during optimization"（description 会在优化中不断变长）；
4. **重复**：至训练集全过或无有意义改进；
5. **按验证通过率选优**：最佳 description **未必是最后一轮**——早轮可能验证通过率高于过拟合的晚轮。

文中称**五轮迭代通常足够**。定稿后再用 5-10 条**从未参与优化的新查询**做诚实泛化检查（F-040）。

## 与 eval 驱动迭代的关系

本文的方法与 [/concepts/04-eval-driven-iteration.md](/concepts/04-eval-driven-iteration.md) 同属实验方法学，但对象不同：eval 驱动迭代针对技能**输出质量**（执行维度），本文针对技能**路由行为**（发现维度）。两者共享"干净对照、证据驱动、防过拟合"的治理姿态。

## 相关概念

- [/concepts/02-frontmatter-fields.md](/concepts/02-frontmatter-fields.md) —— description 字段的格式约束（1024 字符）
- [/concepts/01-progressive-disclosure.md](/concepts/01-progressive-disclosure.md) —— 为什么 description 是路由函数
- [/concepts/04-eval-driven-iteration.md](/concepts/04-eval-driven-iteration.md) —— 执行维度的姊妹方法学
- [/concepts/03-authoring-principles.md](/concepts/03-authoring-principles.md) —— "宁可 pushy" 与写作四原则的来源语境
