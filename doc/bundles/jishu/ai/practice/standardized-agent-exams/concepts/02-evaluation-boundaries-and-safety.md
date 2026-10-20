---
type: Concept
title: SAE 评测边界与安全约束
description: 汇总 Skill 的授权、密钥、时限和提交规则，并界定现有材料不足以支持的可用性、评分与测量效度结论。
tags: [Kaggle, SAE, 安全边界, 评测效度]
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

# SAE 评测边界与安全约束

## 先区分文档规则与实测行为

本 bundle 记录的报名、计时、提交、密钥和错误处理要求来自 Kaggle 官方静态 Skill，均应理解为**文档规则**，并非本任务实测的服务行为（F-012–F-019）。本任务没有调用 SAE API、注册 Agent、开始考试、提交答案或处理凭据；当前服务状态仍为 **UNVERIFIED**（F-020）。

## 授权、计时与提交边界

- **明确同意：** Skill 要求在注册前向用户取得明确参试确认，并说明开始考试将启动 30 分钟倒计时；还要求询问 Agent 名称偏好（F-012）。这不是可由 Agent 默认为用户接受的授权。
- **限时考试：** Skill 的开始考试示例包含 16 道题和 30 分钟时限描述；具体计时与服务端执行方式未在本任务中验证（F-013）。
- **提交限制：** Skill 规定一次提交全部 16 题，不跳题；未回答计为错误，并提示答案须遵循题目格式（F-014）。Skill 另写明每个 Agent 对每场考试最多提交 3 次，达到上限返回 400（F-016）。这些是静态规则，不是实测结果。
- **不可逆数据操作：** Skill 将删除 Agent 数据描述为不可逆，并要求仅在人类明确指示时操作（F-019）。本文不提供删除或考试操作步骤。

## API key 的域名和存储约束

Skill 将 API key 的允许去向限定为 `www.kaggle.com`，且仅用于 `https://www.kaggle.com/api/v1/*` 请求头；不得分享、记录或输出给用户。Skill 还给出本地凭据文件及权限设置建议（F-017）。本 bundle 不包含密钥、凭据样例或请求代码；上述限制是对 Skill 安全文本的转述，不表示已发送任何凭据。

Skill 对错误响应也规定了不同处理方式：404 时停止操作；对 401/403、提交次数已满的 400 和 429 分别说明重试、停止或等待边界（F-018）。这些属于静态错误处理规则；不能据此判断当前考试端点的状态（F-018、F-020）。

## 评测结论的证据边界

博文描述了 Reasoning 与 Adversarial Safety 两个维度（F-003、F-004），Skill 示例展示了若干结果字段（F-015）。但指定材料没有给出可复核的评分算法、维度题目分配、及格阈值、信度/效度研究或排行榜统计方法（F-021）。因此本 bundle 不推断分数含义、测量效度、跨 Agent 可比性或证书效力（F-021）。

材料也未说明题目是否轮换、后续考试是否固定为 16 题或规则的长期生效范围（F-022）。博文所称首个考试的题数不应外推为所有未来考试的永久规则（F-003、F-022）。

## 已知边界

- “experimental MVP”是博文在 2026-04-01 所表达的发布时状态，不等于当前可用性结论（F-001、F-002、F-020）。
- 博文称考试后有分数、公开成绩卡和实时排行榜；该表述限于文章发布语境，不证明当前服务运行（F-006、F-020、AN-04）。
- 博文与 Skill 关于注册字段的表述不同，且没有证据裁定服务端强制字段（F-011）。
- 作者称 SAE 可作为 “quick first baseline” 是产品定位语句，不是测量效度证据（AI-01、F-021）。

## 相关内容

- [SAE 的定位与发布时状态](00-position-and-release-status.md)
- [考试流程与结果信号](01-exam-flow-and-result-signals.md)
- [核验与边界记录](../references/verification.md)
