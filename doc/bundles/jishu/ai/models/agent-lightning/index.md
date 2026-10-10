---
okf_version: "0.2"
type: bundle
title: "微软 Agent Lightning v1.0：把真实 Agent 接进强化学习"
description: "产品发布资讯/技术综述（非操作教程）——微软开源 Agent Lightning v1.0 面向 AI Agent 的强化学习框架，约 3,500 行训练控制层，Harnessed Agentic RL 范式、rollout/样本拆分/Collocated Async RL 机制，Qwen3.5-9B 在 SWE-bench Verified 从 41.8% 到 56.4%。"
tags: [agent-lightning, agentic-rl, harness, rl, 微软开源, harnessed-agentic-rl]
generated: { by: "reference_agent/deepseek-v4", at: "2026-10-10" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-10" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/j9m0xBbqGrFl5WVeKHq1kg"
  - id: official-blog
    url: "https://www.microsoft.com/en-us/research/blog/agent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses/"
  - id: arxiv
    url: "https://arxiv.org/abs/2608.17528"
  - id: github
    url: "https://github.com/microsoft/agent-lightning"
---

# 微软 Agent Lightning v1.0：把真实 Agent 接进强化学习

> **产品发布资讯/技术综述，非操作教程** [F-004]。本束由 [AINLP 公众号博文](https://mp.weixin.qq.com/s/j9m0xBbqGrFl5WVeKHq1kg)（作者 NLPerNLPer，2026-10-09）经 OKF v0.2 七阶段工作流转化，关键成效数字经微软官方来源核验通过。

微软开源 **Agent Lightning v1.0**，一套面向 AI Agent 的强化学习框架——给已经搭好 Agent、希望继续训练底层模型的开发者使用，保留现有工具调用、上下文管理和任务执行流程，用实际任务执行记录与结果反馈训练模型 [F-001][F-002][F-003]。框架约 3,500 行代码实现训练控制层 [F-044]，通过 agent harness 让部署侧流程直接参与 RL 训练。

## 核心要点速览

| 维度 | 内容 |
|------|------|
| **发布方** | 微软（微软亚洲研究院）[F-012] |
| **定位** | 把真实 Agent 接进强化学习的训练框架 [F-001] |
| **核心概念** | agent harness——执行与上下文编排的外层程序 [F-005] |
| **训练范式** | Harnessed Agentic RL（分离式架构 + LLM endpoint proxy）[F-014][F-047] |
| **标杆结果** | Qwen3.5-9B 在 SWE-bench Verified：41.8%→56.4%（+14.6pp，约 6,000 样本）[F-009][F-010][F-011] |
| **异步加速** | Collocated Async RL 约 2 倍端到端加速（官方实验）[F-041] |
| **代码规模** | 约 3,500 行训练控制层 [F-044] |
| **开源形式** | MIT license，GitHub + arXiv 2608.17528 [F-049][F-050][F-051] |

## 已知边界与可信度

- **成效数字均为微软官方实验口径**（约 6,000 样本、约 2 倍加速、约 3,500 行），带"约"限定词，非普适性能承诺——详见 [references/verification.md](references/verification.md)。
- **F-046 硬件型号（A100/B200）仅博文单源，待复核**，stale_after 前建议复核。
- **多数机制细节（rollout/样本拆分/奖励统计）为博文叙述**，辅以官方概念核验，引用时提示甄别。
- 本束 **无 examples**（产品发布资讯/技术综述，无可复现操作流程）。
- **状态**：stable（全部关键数字官方核验通过，无勘误、无 flagged 触发）。

## 内容导航

- [概念文档](concepts/index.md) — Agent Lightning 概览、Harnessed Agentic RL 范式、实验结果与生态
- [信源参考](references/index.md) — 博文事实清单 + P0 核验报告

## 主题关联

本束与 [AReaL 自演进 Agent 强化学习基础设施](../areal/index.md) 属同一"Agent 强化学习基础设施"主题簇，两者互为对照：Agent Lightning v1.0 主打轻量化训练控制层（harness 直接参与训练），AReaL 2.0 主打自演进式 Agent RL（Agent-compute 微服务架构）。AReaL 2.0 亦采纳了 harnessed agentic RL 范式 [F-048]。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```