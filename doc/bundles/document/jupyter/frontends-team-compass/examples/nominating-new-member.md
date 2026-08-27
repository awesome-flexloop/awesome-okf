---
type: Example
title: "提名新 Council 成员"
description: "从现任成员视角，逐步演示如何提名一位新贡献者加入 Frontends Council，包含内部共识、投票、正式邀请的完整流程。"
tags: [example, membership, nomination, council, how-to]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:39:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:39:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: becoming-member
    resource: /references/becoming-member-source.md
    title: "成员准入指南信源"
  - id: member-guide
    resource: /references/member-guide-source.md
    title: "成员指南信源"
---

# 提名新 Council 成员

本文演示一个现任 Council 成员如何提名一位新贡献者加入 Frontends Council 的完整流程。

## 场景设定

- **你的身份**：现任 Frontends Council 成员
- **被提名人**：Alex Chen（@alexchen），过去一年持续贡献 JupyterLab  accessibility 功能，积极参与会议和PR审查
- **时间线**：整个过程通常需要 1-2 周

## 第一步：评估候选人是否合适（自我评估）

在发起正式流程之前，自我评估候选人是否符合基本标准：

### 入选标准 Checklist

- [ ] **持续贡献**：是否持续参与社区至少6个月以上？（Alex：过去一年提交了15+ PR，主要在 accessibility 方向）
- [ ] **积极正面**：在 Issue/PR/会议中的互动是否友好、建设性？（Alex：Code Review 总是给出建设性反馈，帮助新人）
- [ ] **长期意愿**：是否有意向继续投入至少一年？（Alex：在最近会议上多次表达长期参与意愿）
- [ ] **多维度贡献**：贡献不限于代码？（Alex：除了PR，还在会议上做 accessibility 专题分享，帮助回答 Zulip 问题）

> 💡 贡献不限于代码！帮助论坛用户、审查 PR、参与会议、改进文档都是有价值的贡献。

## 第二步：内部私下讨论

在公开之前，先在 Council 内部私下讨论（保护候选人隐私——如果最终未通过，不应对外公开）。

### 在 Council 邮件列表发起讨论

发送邮件到 [jupyterlab-council 邮件列表](https://groups.google.com/u/1/g/jupyterlab-council)：

```
Subject: [NOMINATION] Alex Chen for Frontends Council

Hi all,

I'd like to nominate Alex Chen (@alexchen) for Frontends Council membership.

Contributions summary:
- 15+ PRs over the past year, primarily focused on accessibility improvements
  to JupyterLab (screen reader support, keyboard navigation, ARIA labels)
- Regular participant in weekly Frontends meetings
- Presented accessibility roadmap at two community calls
- Active in helping newcomers on Zulip and in PR reviews
- Affiliated with [University/Company]

Alex has expressed interest in continuing long-term involvement
and taking on more responsibility in the accessibility working group.

Please share your thoughts. I'd like to gauge consensus before
reaching out to Alex formally.

Thanks,
[Your name]
```

### 收集反馈

等待至少 **3-5 天**让所有 Council 成员有时间回应：

- ✅ 如果有明确共识（多数人支持、无人反对）→ 进入第三步
- ⚠️ 如果有分歧或担忧 → 先在内部讨论解决；必要时进行内部投票（保护候选人隐私）
- ❌ 如果共识不足 → 暂缓提名，给候选人更多时间积累贡献

## 第三步：正式联系候选人

获得内部共识后，由你（提名者）或一位资深成员私下联系候选人。

### 通过私信/邮件联系

```
Subject: Invitation to join the Jupyter Frontends Council

Hi Alex,

I'm reaching out on behalf of the Jupyter Frontends Council to
invite you to become a Council member!

Your work on accessibility over the past year has been incredibly
valuable to the project. The Council has discussed your contributions
and would love to have you join us formally.

Before you decide, please review the Membership Guidelines:
https://jupyterlab-team-compass.readthedocs.io/en/latest/team/member-guide.html

Key responsibilities include:
- Watching the team-compass and council repos for updates
- Participating in at least 2/3 of votes (you'll be auto-pinged on GitHub)
- Joining meetings when you can (sync or async participation is fine)
- Helping foster open and inclusive discussions
- Voting in SSC representative elections (annually, January)

There's no requirement to attend every meeting or contribute a set
number of hours—we know everyone has other commitments!

Would this be of interest to you? No pressure either way, and feel
free to ask any questions.

Best,
[Your name]
```

### 回答候选人的问题

候选人可能会问：
- "需要投入多少时间？" → 通常每周 1-3 小时，参与投票和偶尔的会议
- "必须参加所有会议吗？" → 不需要，异步参与（看会议记录、在Issue上投票）即可
- "Release Team/Admin Team 是什么？" → 解释三层体系，Council 是基础层，其他需要额外申请
- "我只是做 accessibility，需要懂所有方向吗？" → 不需要，每个成员有自己的专注领域

## 第四步：候选人接受后的行政流程

如果候选人接受，执行以下操作：

### 4.1 公开欢迎

在 team-compass 仓库开一个 Issue 或在下一次周会上公开宣布和欢迎新成员：

> "We're happy to welcome Alex Chen (@alexchen) to the Frontends Council! Alex has been doing amazing work on JupyterLab accessibility and we're excited to have them join."

### 4.2 GitHub 权限

Admin Team 成员需要：
- 将 @alexchen 添加到 GitHub JupyterLab 组织
- 邀请加入 `jupyterlab` team（基础成员组）

### 4.3 通知成员列表

在 Council 邮件列表发送欢迎邮件，附上新成员的简介和贡献领域。

### 4.4 更新文档

成员列表由 bot 自动管理（council 仓库的 workflow），但可以在下一次成员活跃确认周期前手动确认新成员已加入。

## 第五步：新成员融入

作为提名者，帮助新成员顺利融入：

- ✅ 在下一次周会上介绍新成员
- ✅ 确保他们 Watch 了 team-compass 和 council 仓库
- ✅ 指导他们如何参与投票（第一个投票时主动提醒）
- ✅ 介绍 Council 运作方式和沟通渠道
- ✅ 解答日常问题

## 时间线总结

| 阶段 | 预计时间 | 操作 |
|------|---------|------|
| 自我评估 | 1天 | 确认候选人符合标准 |
| 内部邮件讨论 | 3-5天 | Council 内部私下讨论，收集反馈 |
| 内部投票（如需） | 3-7天 | 共识不足时进行匿名投票 |
| 联系候选人 | 1-3天 | 私信邀请，回答问题，等待回复 |
| 行政流程 | 1天 | GitHub 权限、公开欢迎、邮件通知 |
| 融入指导 | 持续 | 帮助新成员适应 |

**总时长**：约 1-2 周（如果内部共识明确），3-4 周（如需投票）。

## 注意事项

1. **隐私保护**：在候选人正式接受之前，不要在公开场合讨论提名
2. **不施压**：候选人完全可以拒绝，不影响其未来的贡献
3. **不设门槛过高**：不需要"完美"的贡献者，持续的积极参与比数量更重要
4. **多样性考虑**：注意候选人的背景、机构、地域、专长领域的多样性
5. **记录留存**：内部讨论邮件保留在邮件列表存档中，但不需要公开

## 相关概念

- [Frontends Council 架构](../concepts/01-team-council.md) — 三层成员体系和加入流程
- [决策制定流程](../concepts/03-decision-making.md) — 共识与投票机制
- [成员行为指南](../concepts/04-member-guide.md) — 新成员的职责和期望
