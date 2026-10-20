---
type: Concept
title: SAE 考试流程与结果信号
description: 分层呈现博文发布时描述的考试体验与官方 Skill 的文档规则，不把静态操作说明误写为实测服务行为。
tags: [Kaggle, SAE, 考试流程, 结果信号]
generated: { by: "process:sae-bundle-task-2", at: 2026-10-19T00:00:00Z }
verified: { by: "process:fact-register-crosscheck", at: 2026-10-19T00:00:00Z }
status: stable
stale_after: 2026-12-18
sources:
  - id: kaggle-article
    resource: https://www.kaggle.com/blog/standardized-agent-exams
    title: Kaggle Standardized Agent Exams 博文
  - id: kaggle-sae-skill
    resource: https://www.kaggle.com/static/experimental/sae/SKILL.md
    title: Kaggle SAE 官方静态 Skill
  - id: source-register
    resource: /references/article-source.md
    title: F 编号事实清单
---

# SAE 考试流程与结果信号

## 博文描述的发布时体验

博文描述的高层流程是 Agent 注册、获取考试并自主完成题目，之后获得分数、公开成绩卡和实时排行榜名次（F-006）。博文称注册不需要 Kaggle 账户（F-007），并举 Claude Code、Gemini CLI、Cursor 为接入客户端示例；这些是文章举例，不等同于兼容性测试（F-008）。

上述流程是 2026-04-01 博文的产品描述（F-001、F-006），不是本 bundle 实测的服务行为。当前注册、考试、排行榜和成绩服务可用性仍为 **UNVERIFIED**（F-020）。

## 官方 Skill 写明的规则

以下均为静态 Skill 中的**文档规则或响应示例**，不是本地执行记录或已验证的服务端行为：

1. **注册前确认：** Skill 要求先向用户取得明确参试确认，说明开始考试会启动 30 分钟倒计时，并询问 Agent 名称偏好（F-012）。
2. **注册字段口径：** 博文称注册“只需”名称和描述；Skill 的注册请求示例还列出 `model`、`version`、`agentType`，并将 `description` 标为可选。材料没有判定哪些字段是服务端强制项，故保留差异，不合并成确定字段契约（F-011）。
3. **开始考试：** Skill 示例描述开始考试后返回 16 道题，响应示例含 `timeLimitMinutes: 30`；其约束段写明每次提交限时 30 分钟（F-013）。此处不推断计时器在服务端的具体实现。
4. **答案提交：** Skill 要求将 16 题答案放在一次提交请求中、不跳题；未回答题目计为错误，答案格式不符也可能判错（F-014）。Skill 还写明每个 Agent 对每场考试最多提交 3 次，达到上限时返回 400（F-016）。

本页不提供 API 请求样例或执行步骤；规则仅供理解文档口径，不构成开始考试的授权。

## 结果字段能说明什么

Skill 的提交响应示例列有 `score`、`maxScore`、`percentage`、`passed` 和 `certificateId` 等字段，并描述查询单次结果、Agent 历史和公开 Profile 页面（F-015）。这些是 Skill 的示例/文档描述，不能据此断言当前接口可用或字段必然返回（F-020）。

结果字段本身不能说明分数如何计算、及格阈值是多少、证书具有什么效力或排行榜采用何种统计方法。指定材料未给出这些信息（F-021）；不得从 `passed` 字段、`percentage` 字段或“标准化”名称推导算法或效度。

## 关联阅读

- [SAE 的定位与发布时状态](00-position-and-release-status.md)
- [评测边界与安全约束](02-evaluation-boundaries-and-safety.md)
- [来源事实清单](../references/article-source.md)
- [核验与边界记录](../references/verification.md)
