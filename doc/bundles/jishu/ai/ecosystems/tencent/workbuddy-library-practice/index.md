---
okf_version: "0.2"
type: bundle
title: "WorkBuddy 资料库协作与工作台实践"
description: "从 11 个 WorkBuddy 空间页面中整理资料复用、人机共编、团队知识回存、工作台设计与专家案例边界；含 6 篇概念、46 条事实及来源核验。"
tags: [WorkBuddy, 腾讯, 资料库, Agent, 人机协作, 团队知识, 工作台, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-19" }
status: draft
stale_after: "2026-12-31"
sources:
  - { id: source-ledger, resource: "references/article-source.md", title: "11 个来源与 F-001–F-046 事实登记" }
  - { id: source-verification, resource: "references/verification.md", title: "来源核验、官方交叉参照与证据边界" }
  - { id: official-workbuddy, resource: "../workbuddy-official-docs/index.md", title: "WorkBuddy 官方站点与四区文档" }
  - { id: workbuddy-mvp, resource: "../workbuddy-one-sentence-mvp/index.md", title: "WorkBuddy 一句话做 MVP" }
  - { id: tencent-buddy-family, resource: "../tencent-buddy-family/index.md", title: "腾讯 Buddy 家族产品观察" }
---

# WorkBuddy 资料库协作与工作台实践

> 本包将 13 个输入链接去重为 11 个页面来源，整理出资料接续、人机共编、内容载体分工、团队知识循环、工作台组合与专家案例边界六个主题。它是对作者实践材料的归纳，不是 WorkBuddy 官方操作手册或独立效果评测。

## 阅读路径

| 顺序 | 概念页 | 适合的问题 |
| --- | --- | --- |
| 00 | [让资料成为人与 Agent 可接续的工作成果](concepts/00-shared-agent-workspace.md) | 怎样让已完成的资料支持后续任务和团队协作？ |
| 01 | [内容、数据与呈现：三种载体如何分工](concepts/01-content-data-presentation.md) | 说明、结构化数据与页面展示如何分层组织？ |
| 02 | [人机共编：把修改建议放进可审阅的闭环](concepts/02-human-ai-review-loop.md) | 怎样区分 Agent 建议、人工审阅与内容写回？ |
| 03 | [团队共享上下文与知识回存循环](concepts/03-team-knowledge-cycle.md) | 怎样组织共享资料、任务调用与新成果回存？ |
| 04 | [工作台组合：先区分展示页面与持续使用的工具](concepts/04-workbench-composition.md) | 当前需要展示页，还是持续更新的工作台？ |
| 05 | [专家案例拆解：沉淀判断流程，也设计能力边界](concepts/05-expert-case-boundaries.md) | 如何理解案例中的流程、角色分工与风险测试？ |

## 与相关知识包的分工

- [WorkBuddy 官方站点与四区文档](../workbuddy-official-docs/index.md)是产品能力、权限和操作流程的参照。本包不复制官方步骤；具体功能以该包及官方最新文档为准。
- [WorkBuddy 一句话做 MVP](../workbuddy-one-sentence-mvp/index.md)聚焦单次产品叙事、软文证据与能力判读；本包关注资料复用、协作组织和工作台案例。
- [腾讯 Buddy 系列产品观察](../tencent-buddy-family/index.md)描述 Buddy 产品矩阵与生态关系；本包聚焦 WorkBuddy 资料库实践，不扩展为品牌或市场判断。

## 已知边界

- 来源页面托管于 WorkBuddy 域名，但作者身份、发布关系和官方背书未独立核实；作者框架与产品事实分层呈现。
- 本包 46 条编号事实是来源页面内容及采集边界登记，不代表每条产品声明均已独立验证。产品能力与操作以官方知识包为准。
- S10 的“3.4 万个家庭”等数字未核实，不作为用户规模、服务效果或因果证据。
- S11 四个看板的数据为页面声明的虚构演示数据；主工作台正文未取得，不从目录或子页面推断其功能。
- 候选材料未同时满足可照做步骤和复现信息充分两项条件，因此不创建 `examples/`。

来源清单、去重关系与事实台账见[来源与事实登记](references/article-source.md)；交叉核验及判定依据见[核验与证据边界](references/verification.md)。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
