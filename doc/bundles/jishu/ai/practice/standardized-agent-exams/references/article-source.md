---
type: Reference
title: Kaggle SAE 来源事实清单
description: 按 F-001–F-022 汇总 Kaggle 博文与官方静态 Skill 的声明，并区分文章时点、文档规则、作者定位和未核实边界。
tags: [Kaggle, SAE, 事实登记, 来源追溯]
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
---

# Kaggle SAE 来源事实清单

## 阅读口径

本清单按唯一事实基准逐项保留 F-001–F-022。`ARTICLE-TIME` 只表示博文在其发表时的说法；`SKILL-RULE` 表示静态 Skill 中写明的操作规则，不代表考试服务已被实测；`SOURCE-MISMATCH` 表示两份材料口径不同；`UNVERIFIED` 表示指定材料和本次只读范围不能确认。两份来源均由 Kaggle 发布，彼此一致不等同独立第三方验证。

## 事实登记

| 编号 | 声明摘要 | 证据状态 | 来源定位 |
|---|---|---|---|
| F-001 | 博文页面标注发布日期为 2026-04-01，作者 Nicholas Kang。 | ARTICLE-TIME；单源 | 博文 “Project Details” |
| F-002 | 博文将 SAE 描述为 experimental MVP，并称其为面向 AI Agent 的轻量、零设置标准化考试。 | ARTICLE-TIME；单源 | 博文标题、副标题、正文首段 |
| F-003 | 博文称首个考试含 16 道题，聚焦 Reasoning 与 Adversarial Safety；Skill 也描述 16 题，题数跨文档一致但并非独立验证。 | ARTICLE-TIME；题数文档一致，维度单源 | 博文 “What’s on the SAE?”；Skill “Step 3: Start Exam” |
| F-004 | 博文把 Reasoning 解释为多步问题处理可靠性，把 Adversarial Safety 解释为负责任地处理棘手或操纵性提示。 | ARTICLE-TIME；单源 | 博文 “What’s on the SAE?” |
| F-005 | 博文面向正在部署 Agent 的开发者，并以免于自建 harness、整理数据集或手工测试流程作为与传统评估设置的对比。 | ARTICLE-TIME；单源 | 博文正文第二段、“A zero-setup exam” |
| F-006 | 博文描述 Agent 注册、获取并自主完成题目，随后获得分数、公开成绩卡和实时排行榜名次。此处是发布时产品描述。 | ARTICLE-TIME；完整流程单源 | 博文 “A zero-setup exam”；Skill “Step 4”–“Step 8” |
| F-007 | 博文称注册不需要 Kaggle 账户；Skill 也如此描述并称通过 HTTP 交互。两份材料来自同一发布方。 | ARTICLE-TIME + SKILL-RULE；文档一致 | 博文 “A zero-setup exam”；Skill 标题说明、“Constraints” |
| F-008 | 博文举 Claude Code、Gemini CLI、Cursor 为客户端示例；示例不等于兼容性测试结果。 | ARTICLE-TIME；单源 | 博文 “Get started in seconds” |
| F-009 | 博文称发布具有实验性质，并邀请读者反馈。 | ARTICLE-TIME；单源 | 博文末段 |
| F-010 | 静态 Skill 自述名称 `kaggle-standardized-agent-exam`、版本 `1.0.0`、API base `https://www.kaggle.com/api/v1`；`reviewedAt` 与 `lastChangedAt` 均为 2026-09-18。 | SKILL-RULE；文件自述，非独立版本历史验证 | Skill frontmatter、文件头注释 |
| F-011 | 博文称注册“只需”名称和描述；Skill 请求示例另含 `model`、`version`、`agentType`，且把 `description` 标为可选。服务端强制字段未知。 | SOURCE-MISMATCH | 博文 “A zero-setup exam”；Skill “Step 2: Register” |
| F-012 | Skill 要求注册前取得用户明确参试确认，说明开始考试会启动 30 分钟倒计时，并询问 Agent 名称偏好。 | SKILL-RULE；未实测 | Skill “Step 2: Register” |
| F-013 | Skill 开始考试示例称返回 16 题，响应示例有 `timeLimitMinutes: 30`；约束段也写明每次提交限时 30 分钟。 | SKILL-RULE；未实测 | Skill “Step 3: Start Exam”、“Constraints” |
| F-014 | Skill 要求一次提交全部 16 题、不跳题；未回答计错。特定格式要求若不满足可能判错。 | SKILL-RULE；未实测 | Skill “Step 3: Start Exam”、“Step 4: Submit Answers” |
| F-015 | Skill 提交响应示例含 `score`、`maxScore`、`percentage`、`passed`、`certificateId` 等字段，并描述结果查询、Agent 历史和公开 Profile 页面。 | SKILL-RULE；示例/文档描述，未实测 | Skill “Step 4”–“Step 7” |
| F-016 | Skill 写明每个 Agent 对每场考试最多提交 3 次；达到上限时返回 400。 | SKILL-RULE；未实测 | Skill “IMPORTANT”、“Constraints” |
| F-017 | Skill 要求 API key 仅发送至 `www.kaggle.com`，只放入 `https://www.kaggle.com/api/v1/*` 请求头；不得分享、记录或输出，并给出本地凭据文件及权限建议。 | SKILL-RULE；未实测 | Skill “CRITICAL SECURITY WARNING” |
| F-018 | Skill 描述 404 时停止所有操作；并说明 401/403、达到提交上限的 400、429 的处理规则。 | SKILL-RULE；未实测 | Skill “IMPORTANT” |
| F-019 | Skill 将删除 Agent 数据描述为不可逆操作，并要求仅在人类明确指示时执行。 | SKILL-RULE；未实测 | Skill “Data Management” |
| F-020 | 截至 2026-10-19，公开 SAE 落地页返回 reCAPTCHA 挑战；未绕过验证，也未请求 SAE API。考试注册、开始、提交、排行榜和成绩服务状态仍未核实；静态 Skill 可读取不证明在线，也不证明下线。 | UNVERIFIED | S3 页面只读访问受阻；S1、S2 |
| F-021 | 指定材料未给出可复核评分算法、维度题目分配、及格阈值、信度/效度研究或排行榜统计方法；不得由字段或“标准化”一词推导。 | UNVERIFIED / NOT SPECIFIED IN S1–S2 | 博文与 Skill 的指定材料范围 |
| F-022 | 博文称 16 题为首个考试；材料没有说明题目是否轮换、后续考试是否固定 16 题或规则生效时间，不能外推为长期不变规则。 | UNVERIFIED | 博文 “What’s on the SAE?”；Skill “Step 3: Start Exam” |

## 作者定位与分析编号

以下编号是事实基准对作者定位或分析边界的标识，不应改写成独立测量结论：

- **AI-01**：作者把两个维度称为 Agent 核心能力的 “quick first baseline”；这不证明测验充分代表 Agent 能力。
- **AI-02**：作者将 SAE 放入推进 “rigorous, trustworthy evaluation” 的目标叙述；这是目标/定位，不是方法学验证。
- **AI-03**：作者使用 “zero-setup / autonomous” 体验表述；不应解释为无需凭据或授权。
- **AN-01**：两份 Kaggle 文档相符仅是文档间一致性核对，不是独立复现。
- **AN-02**：注册字段差异按 F-011 原样保留，不判定服务端强制字段。
- **AN-03**：产品结构描述不足以证明覆盖面、题目质量、跨 Agent 可比性或分数统计意义。
- **AN-04**：博文的实时排行榜描述属于 2026-04-01 发布语境；2026-10-19 公开 SAE 落地页被 reCAPTCHA 挑战拦截，且未请求 API，因此不是当前实时状态证据。

## 来源登记

| ID | 来源 | 日期与用途 |
|---|---|---|
| S1 | [Kaggle：Standardized Agent Exams: Zero-setup evaluation for your AI agents](https://www.kaggle.com/blog/standardized-agent-exams) | 页面标注 2026-04-01；用于博文发布时主张。 |
| S2 | [Kaggle 官方 SAE 静态 Skill](https://www.kaggle.com/static/experimental/sae/SKILL.md) | 文件自述版本 1.0.0，`reviewedAt` 与 `lastChangedAt` 为 2026-09-18；用于文档操作规则。 |
| S3 | [Kaggle SAE 公开落地页](https://www.kaggle.com/experimental/sae) | 2026-10-19 返回 reCAPTCHA 挑战；仅记录访问限制，不作为服务在线/下线证据。 |

本清单未纳入评论区、个人成绩或外部转载。产品规则核验仍限于 S1 与 S2；S3 仅用于记录公开落地页访问受阻。事实基准记录的来源读取日期为 2026-10-19；本任务没有调用 SAE API 或验证实时服务。
