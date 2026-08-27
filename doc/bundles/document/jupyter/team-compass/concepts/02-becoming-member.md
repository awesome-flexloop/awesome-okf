---
type: Concept
title: "成为团队成员"
description: "新成员加入 Jupyter Server 团队的完整流程：前置条件、5步提名流程、半年维护机制，以及活跃/不活跃状态管理。"
tags: [membership, nomination, onboarding, new-members, team-growth]
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

## 前置条件：什么样的贡献者可以成为成员

成为 Jupyter Server 团队成员不是"申请-审批"模式，而是**认可-邀请**模式。候选人应该已经是社区中：

- **持续的**（consistent）贡献者
- **积极的**（positive）社区参与者
- **有产出的**（productive）贡献者
- 表现出**长期参与意愿**（至少一年）

贡献**不限于代码**，可以包括：
- 在论坛/Issues 中帮助他人
- 审查 Pull Request
- 参与团队会议
- 文档贡献
- 社区建设

这种"持续参与优先于代码量"的理念，与 Jupyter 社区重视多元贡献的价值观一致。

## 5步提名流程

任何新团队成员必须由**当前活跃成员提名和支持（champion）**，流程如下：

### 步骤1：内部共识沟通

提名人先与其他团队成员**内部讨论**，确保对候选人加入有基本共识。这一步是非正式的，避免公开提名后出现反对的尴尬局面。

### 步骤2：联系候选人

如果团队有共识，提名人**私下联系**潜在新成员，询问其是否有兴趣加入。同时让候选人阅读[成员指南](04-member-guide.md)，确保其了解加入后的职责。如果候选人同意，进入下一步。

### 步骤3：公开提名Issue

提名人在 [team-compass 仓库](https://github.com/jupyter-server/team-compass/issues) 开一个新 Issue，内容应包括：
- 明确表示支持新成员
- 讨论为什么该候选人适合加入团队
- 列举其具体贡献

### 步骤4：7天讨论期

提名 Issue 保持开放约**7天**，给团队成员充分时间表达意见和支持。这是一个公开透明的社区讨论过程。

### 步骤5：无反对即加入

如果7天内没有未解决的反对意见，新成员正式加入团队！反对意见需要有充分理由，并通过讨论解决，而非简单投票否决。

## 半年维护机制

为了保持活跃成员列表的准确性，团队实行**半年确认制度**：

1. **触发**：每6个月，一位当前活跃成员在 team-compass 仓库开一个 Issue
2. **询问**：请所有当前活跃成员回复是否仍然认为自己活跃
3. **处理**：如果不回复（或明确表示不活跃），该成员将被视为转为不活跃

这个机制确保成员列表不会因人员流动而变得过时。

## 灵活的状态管理

### 自行暂停

成员可以随时转为不活跃状态，无需解释或批准。典型场景包括：
- 休长假（>2周）
- 工作重心转移
- 个人原因需要减少投入

### 自行恢复

不活跃成员可以在任何时间通过公开声明状态变更（PR 更新 YAML 文件）重新激活，**不需要其他成员提名**。这大大降低了回归门槛。

### 状态变更的公开性

所有状态变更都应通过 Pull Request 更新 `contributors-jupyter-server.yaml` 文件公开记录，保持团队状态的透明度。

## 与 JupyterLab 团队的一致性

README.md 明确指出，向 Jupyter Server GitHub 组织贡献扩展的指南与 JupyterLab 遵循相同的准则，这确保了 Jupyter 生态内团队加入流程的一致性。

## 相关概念

- [团队成员体系](01-team-membership.md)
- [决策机制](03-decision-making.md)
- [成员指南与PR合并原则](04-member-guide.md)
- [实操：提名新成员](../examples/nominating-new-member.md)
