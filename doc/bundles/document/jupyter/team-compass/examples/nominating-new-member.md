---
type: Example
title: "实操：提名一位新团队成员"
description: "按照5步提名流程，演示如何将一位贡献者正式邀请加入 Jupyter Server 团队。"
tags: [example, nomination, new-member, how-to, walkthrough]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: becoming-member
    resource: /references/becoming-member-source.md
    title: "成为团队成员信源"
  - id: member-guide
    resource: /references/member-guide-source.md
    title: "成员指南信源"
---

## 场景假设

假设你是 Jupyter Server 的活跃成员，注意到一位叫 Alex 的贡献者在过去6个月中：
- 持续审查 PR（>20次审查）
- 在 Gitter 和 Discourse 上帮助新手解答问题
- 修复了几个重要 Bug
- 参加了多次团队会议

你认为 Alex 应该被邀请加入团队。以下是完整的操作步骤。

## 步骤1：内部沟通（非正式）

在公开提名之前，先在团队内部非正式地确认共识。

**操作方式**：在团队内部沟通渠道（如私人Gitter频道、会议口头讨论）提到：
> "I've noticed Alex has been contributing consistently for the past 6 months — great PR reviews, helping newcomers, fixing bugs. I'm thinking of nominating them. Any concerns?"

**判断标准**：如果其他活跃成员普遍表示支持或没有反对意见，继续下一步。如果有人提出担忧，先讨论解决。

## 步骤2：私下联系候选人

确认团队有共识后，私下联系 Alex（通过 Gitter DM、邮件等）：

**沟通要点**：
1. 表达对其贡献的认可
2. 询问是否有兴趣加入团队
3. 让其阅读[成员指南](../concepts/04-member-guide.md)了解职责
4. 说明加入后的期望（参加投票、关注仓库等）

**示例消息**：
> "Hi Alex! The team has really appreciated your consistent contributions over the past few months — your reviews and community support have been fantastic. We'd like to nominate you as an official team member. Would you be interested? Being a member comes with some expectations like watching the team-compass repo and participating in votes, but we'd love to have you. Check out the member guide if you'd like to know more."

如果 Alex 同意，继续下一步。如果不感兴趣，尊重其决定，不需要任何正式操作。

## 步骤3：公开提名 Issue

在 [team-compass 仓库](https://github.com/jupyter-server/team-compass/issues) 创建一个新 Issue。

**Issue 标题格式**：`Nomination: [Alex Full Name] (@alex-github) for team membership`

**Issue 内容模板**：

```markdown
I'd like to nominate **Alex Full Name** (@alex-github) for Jupyter Server team membership.

## Why Alex would be a great team member

Alex has been a consistent, positive, and productive member of our community for the past 6 months. Specifically:

- **Code reviews**: Over 20 PRs reviewed, providing thoughtful and constructive feedback
- **Community support**: Regularly helps newcomers on Gitter and Discourse
- **Bug fixes**: Fixed issues in [link to relevant PRs/issues]
- **Meeting participation**: Has attended several weekly team meetings and contributed to discussions

Alex has expressed interest in joining the team and has reviewed the membership guidelines.

This nomination will be open for comments for 7 days. If there are no unresolved objections, Alex will be welcomed as an official team member!
```

## 步骤4：等待7天讨论期

Issue 开放7天期间：
- 其他团队成员可以发表支持意见或提出担忧
- 回应任何问题或疑虑
- 如果有人反对，认真对待并讨论

**支持评论的例子**：
> "+1! Alex's reviews on the WebSocket PRs were incredibly thorough. Would love to have them on the team."

**处理反对意见**：如果有人提出合理的反对意见，不要强行推动。讨论问题、给 Alex 改进的机会、或推迟提名。

## 步骤5：完成加入

7天后，如果没有未解决的反对意见：

1. **确认加入**：在 Issue 中发布欢迎消息
2. **更新成员列表**：提交一个 PR，将 Alex 添加到 `docs/team/contributors-jupyter-server.yaml`：
   ```yaml
   - name: Alex Full Name
     handle: "@alex-github"
     affiliation: "Alex's Organization"
     team: active
     last-check-in: "2026-08"
   ```
3. **更新GitHub权限**：联系有Admin权限的成员将Alex添加到 Jupyter Server GitHub 组织
4. **欢迎**：在会议或Gitter中公开欢迎新成员

## 注意事项

- **不要跳过内部沟通**：直接开公开Issue可能导致尴尬局面
- **7天是约数**：不需要精确到小时，但给足够的讨论时间
- **反对≠否决**：反对意见应该通过讨论解决，不是简单投票
- **不活跃≠退出**：新成员未来如果需要暂停，可以随时转为不活跃状态
- **自助恢复**：未来 Alex 转为不活跃后，可以随时自行重新激活

## 相关概念

- [成为团队成员](../concepts/02-becoming-member.md)
- [团队成员体系](../concepts/01-team-membership.md)
- [成员指南与PR合并原则](../concepts/04-member-guide.md)
