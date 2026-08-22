---
type: Reference
title: "成为团队成员信源"
description: "docs/team/becoming-member.md 的核心内容摘录，包含成员职责、活跃/不活跃状态、提名流程和半年维护机制。"
tags: [reference, membership, nomination, onboarding]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: becoming-member
    resource: https://github.com/jupyter-server/team-compass/blob/main/docs/team/becoming-member.md
    title: "docs/team/becoming-member.md"
---

## docs/team/becoming-member.md 核心内容

### 成员类型

**活跃成员 (Active members)**：
- 必须由当前团队成员提名
- 可被选举为 Jupyter Server 的 SSC 代表
- 在投票时有投票权
- 计入投票法定人数
- 应参与大多数团队投票
- 可以提名新团队成员
- 应同步或异步地积极参与团队会议

**不活跃成员 (Inactive members)**：
- 之前是活跃成员
- 不投票
- 不计入投票法定人数
- 可随时通过公开声明状态变更来"重新激活"

成员可以随时在活跃和不活跃之间自由切换。应通过更新 `contributors-jupyter-server.yaml` 文件的 PR 公开声明状态变更。

### 提名新成员流程

新成员应该已经是社区中持续、积极、有产出的贡献者，表现出长期参与的意愿（至少一年）。贡献不限于代码，可以是论坛帮助、PR 审查、会议参与等。

5步提名流程：
1. **内部沟通**：提名人先与团队成员内部讨论，确保有基本共识
2. **联系候选人**：确认候选人有兴趣，并让其阅读成员指南了解职责
3. **开Issue提名**：在 team-compass 仓库开新 issue，陈述支持理由
4. **7天讨论期**：Issue 保持开放约7天，让团队成员发表意见
5. **无反对则加入**：如果没有未解决的反对意见，新成员正式加入

### 成员维护（半年确认）

每6个月，一位当前活跃成员应在 team-compass 仓库开 issue，询问所有活跃成员是否仍然认为自己活跃。如果不回复，将被视为转为不活跃。不活跃成员可随时通过更改状态回归。
