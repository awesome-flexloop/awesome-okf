---
type: Concept
title: "AgentGit 的 Session 版本化模型"
description: "从 Git 的代码版本控制转向 Agent Session 与 Context 的保存、分享和继续。"
tags: [AgentGit, Agent Session, Context, Git]
generated: { by: "reference_agent/trae", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: official
    resource: https://agent-git.com/en/
---

# AgentGit 的 Session 版本化模型

## 核心命题

传统 Git 保存的是代码结果；AgentGit 的产品定位是保存、分享和继续 Agent Session（F-016）。文章进一步提出：Agent 与人协作时产生的 prompt、尝试、判断、修正和反馈，也应成为可交接的工作资产（F-006、F-012）。

## 概念映射

文章用 Git 做了一个便于理解的类比：

| Git 里的概念 | AgentGit 文章类比 | 说明 |
|---|---|---|
| repository | Agent repo | 一组相关 Session 的容器 |
| branch | 一条具体 Session | 某项任务的连续工作轨迹 |
| commit | 一轮对话或阶段性保存 | 对上下文演进的记录 |

这张表是作者的解释模型，不是官方数据模型（F-015）。官方可确认的是 Session 的保存、分享、继续，以及多个运行时的导入/恢复能力（F-016、F-017、F-024）。

## 为什么代码不够

文章用胸牌打印 App 的软硬件调试作为案例：打印机设置、底色、字体适配等规则经过多轮尝试后沉淀在 Agent Session 中（F-007）。接手者若只看到仓库代码，还需要重新推断这些决策的来龙去脉（F-008）。

因此，Session 版本化的价值不在于替代代码版本控制，而在于补齐“意图—尝试—决策—结果”的过程层。
