---
okf_version: "0.2"
type: bundle
title: Kaggle Standardized Agent Exams (SAE)
description: 基于 Kaggle 博文与官方静态 Skill 整理的技术综述/产品案例，非操作教程；区分发布时陈述、文档规则与评测证据边界。
tags: [Kaggle, SAE, Agent评测, 技术综述, 产品案例]
generated: { by: "process:sae-bundle-task-2", at: 2026-10-19T00:00:00Z }
verified: { by: "process:bundle-fact-crosscheck", at: 2026-10-19T00:00:00Z }
status: stable
stale_after: 2026-12-18
sources:
  - id: kaggle-article
    resource: https://www.kaggle.com/blog/standardized-agent-exams
    title: Kaggle Standardized Agent Exams 博文
  - id: kaggle-sae-skill
    resource: https://www.kaggle.com/static/experimental/sae/SKILL.md
    title: Kaggle SAE 官方静态 Skill
  - id: article-source-reference
    resource: /references/article-source.md
    title: Kaggle SAE 来源事实清单
  - id: verification-reference
    resource: /references/verification.md
    title: Kaggle SAE 来源核验与边界记录
---

# Kaggle Standardized Agent Exams (SAE)

> **技术综述/产品案例，非操作教程。** 本 bundle 以 Kaggle 博文和官方静态 Skill 为来源，记录其所述产品定位、考试流程、安全规则及评测证据边界；不提供考试操作步骤。

## 阅读导航

| 篇目 | 内容 |
|---|---|
| [SAE 的定位与发布时状态](concepts/00-position-and-release-status.md) | 博文时点的产品阶段、目标读者、作者定位语句及当前服务状态边界。 |
| [SAE 考试流程与结果信号](concepts/01-exam-flow-and-result-signals.md) | 博文描述的体验、Skill 文档规则、结果字段示例与注册口径差异。 |
| [SAE 评测边界与安全约束](concepts/02-evaluation-boundaries-and-safety.md) | 用户同意、时限、提交次数、API key 域名限制，以及未说明的评分与效度问题。 |
| [Kaggle SAE 来源事实清单](references/article-source.md) | 完整 F-001–F-022、作者定位与分析编号。 |
| [Kaggle SAE 来源核验与边界记录](references/verification.md) | 来源交叉核对、口径差异、只读边界和本地复核记录。 |
| [更新日志](log.md) | 本 bundle 的新增记录。 |

## 时效与已知边界

- Kaggle 博文页面标注发布日期为 2026-04-01、作者 Nicholas Kang；博文将 SAE 称为 experimental MVP（F-001、F-002）。这是**发布时陈述**，不是当前产品状态。
- 官方静态 Skill 自述 `reviewedAt` 与 `lastChangedAt` 均为 2026-09-18（F-010）；这是文件元数据，不是服务状态证明。
- 当前考试注册、开始、提交、排行榜和成绩服务是否可用均为 **UNVERIFIED**；静态 Skill 可读不等于服务在线或下线（F-020）。
- 博文与 Skill 的注册字段表述不一致；bundle 保留差异，不把示例字段合并为服务端契约（F-011）。
- Skill 写明注册前需取得用户明确同意、告知 30 分钟倒计时、每场最多提交 3 次，以及 API key 的 Kaggle 域名限制；这些是**文档规则**，未作为已实测服务行为陈述（F-012、F-013、F-016、F-017）。
- 指定材料没有给出可复核评分算法、及格阈值或信度/效度研究，不从结果字段推断这些信息（F-015、F-021）。
- 不创建 `examples/`：本 bundle 不记录经实测且可复现的考试流程；静态规则文本不足以证明当前操作流程可复现（F-020）。

`status: stable` 仅表示指定来源范围内没有发现被否证的核心声明；它不代表 SAE 服务当前在线或下线。服务状态仍以 **UNVERIFIED** 标记（F-020）。

## 相邻专题分工

- [Agent 评测工程手册](../ai-engineering-methodology/concepts/evaluation/agent-evaluation-wiki/00-overview.md)：覆盖通用评测理论、指标设计、基准构建、工具链选择和持续评测。本 bundle 不重复通用工程建设指南，只记录 SAE 这一具体产品案例。
- [Agent 评测方法论 Wiki](../ai-engineering-methodology/concepts/evaluation/agent-eval-methodology-wiki/01-overview/01-methodology-overview.md)：从方法论视角组织评测认知与实施。本 bundle 不把单一产品的发布描述提升为普遍评测方法或效度结论。

## 来源

- [Kaggle：Standardized Agent Exams: Zero-setup evaluation for your AI agents](https://www.kaggle.com/blog/standardized-agent-exams)（博文页面标注日期见 F-001）。
- [Kaggle 官方 SAE 静态 Skill](https://www.kaggle.com/static/experimental/sae/SKILL.md)（文件自述日期见 F-010）。
- 内部来源登记：[article-source.md](references/article-source.md)、[verification.md](references/verification.md)。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
