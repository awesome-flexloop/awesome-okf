---
okf_version: "0.2"
type: bundle
title: "Codex Agent 工作流实践：如何成为 Token Billionaire"
description: "天地大观 2026年5月博客——从月耗 2-3 亿 token 跃升至 243 亿的 Codex Agent 工作流全记录：并行模式、大闭环、对抗提升、Spec/Plan 工程、Review 左移与质量保障体系"
tags: [codex, agent-workflow, token-economy, ai-coding, parallel-computing, tdd, ddd, adr]
generated:
  by: "agent:agnes"
  at: "2026-09-09T04:30:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-09-09T04:35:00+08:00"
status: stable
stale_after: "2026-11-21"
sources:
  - id: blog
    resource: /references/article-source.md
    url: https://zhuanlan.zhihu.com/p/2040748661567710711
  - id: verification
    resource: /references/verification.md
  - id: official-codex-pricing
    url: https://openai.com/index/introducing-codex-max/
---

# Codex Agent 工作流实践：如何成为 Token Billionaire

> **状态：`stable`** — 经 P0 核验，F-001/F-002 用量数字标注"仅博文单源"，F-008/F-009 转述标注"据博文转述"，均不构成核心声明错误。
>
> **⚠️ 个人实践数据**：本文涉及的 token 用量（243 亿/月）与费用（$12,213）为作者 ccusage 个人统计，非公开市场数据，不可直接推广为行业基准。
>
> **本文性质**：非操作教程，无 `examples/` 目录。

## 内容导航

- [概览：四大杠杆与核心数据](concepts/00-overview.md)
- [并行工作流：多 Session 与 Sub-Agent 协同](concepts/01-parallel-workflow.md)
- [大闭环：让 Agent 持续工作数小时而不迷失](concepts/02-large-closed-loop.md)
- [对抗提升：Review Fix Loop 与 Best-of-N](concepts/03-adversarial-improvement.md)
- [真实需求驱动：Feature Flag 与 AI Native 流程](concepts/04-real-demand-driven.md)
- [Review 挑战：多轮耗时、Scope 膨胀、无用测试](concepts/05-review-challenges.md)
- [Spec 与 Plan 工程：垂直切片与开发自闭环](concepts/06-spec-and-plan.md)
- [质量保障：技术债控制、DDD+ADR、Skill 开发原则](concepts/07-quality-assurance.md)
- [参考与附件](references/index.md)

```{toctree}
:maxdepth: 2

concepts/index
references/index
log
```

## 主题关联

- 与 [`planning-with-files`](../../planning-with-files/index.md) 互补：后者讲 3-File Pattern 文件系统外存，本篇讲 Spec+Plan 文档组合与垂直切片
- 与 [`context-optimization`](../../context-optimization/index.md) 互补：后者讲 Token 优化技术，本篇讲上下文管理的工作流策略
- 与 [`token-economy-explosion`](../../token-economy-explosion/index.md) 关联：本篇为个人视角 token 消耗实践，上篇为宏观 Token 经济规模分析

## 已知边界

- 所有用量数据为单一作者个人统计，不代表行业平均水平
- OpenAI / Anthropic 相关分享为博文转述，未找到直接官方出处
- slock.ai、Superpowers、Skills For Real Engineers 等外部资源有效性未独立验证
- 部分 skill（review-change-loop、babysit-mr 等）为作者私有实现，未开源

```{toctree}
:hidden:
:maxdepth: 2

concepts/00-overview
concepts/01-parallel-workflow
concepts/02-large-closed-loop
concepts/03-adversarial-improvement
concepts/04-real-demand-driven
concepts/05-review-challenges
concepts/06-spec-and-plan
concepts/07-quality-assurance
references/index
log
```
