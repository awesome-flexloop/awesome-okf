---
type: Concept
title: "成员指南与PR合并原则"
description: "Jupyter Server 团队成员的日常操作指南：沟通渠道选择、5项核心职责、PR合并5项原则，以及开放包容的社区文化。"
tags: [member-guide, communication, pr-merge, responsibilities, community, culture]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: member-guide
    resource: /references/member-guide-source.md
    title: "成员指南信源"
  - id: readme
    resource: /references/readme-source.md
    title: "README.md 信源"
---

## 团队资源

成员应熟悉以下核心资源：

| 资源 | 用途 |
|------|------|
| [Team Compass 仓库](https://github.com/jupyter-server/team-compass) | 开发技巧、会议信息、里程碑和路线图 |
| [Team Compass Issues](https://github.com/jupyter-server/team-compass/issues) | 讨论团队相关的具体可操作事项 |
| [Gitter 频道](https://gitter.im/jupyter/jupyter_server) | 多项目实时同步对话 |
| [Discourse 论坛](http://discourse.jupyter.org/) | 通用讨论、支持问题、灵感交流 |

## 沟通渠道策略

团队明确规定了不同沟通渠道的使用场景，帮助贡献者和维护者找到合适的讨论场所：

### GitHub Issues

用于**与变更仓库内容相关的具体讨论**：
- 功能请求（Feature requests）
- Bug 报告
- 具体技术方案讨论

### Discourse 论坛

用于**通用讨论和支持**：
- 使用问题和求助
- 开放性讨论
- 社区灵感交流
- 跨项目话题

### Gitter/实时聊天

用于**短时间尺度的同步对话**。如果对话可能跨越数小时，或涉及多人，应转至 Discourse 或 team-compass 仓库 Issue。

### 沟通原则

- **公开优先**：尽量在公开空间沟通，让其他人可以参与
- **离线汇报**：如果重要对话发生在线下，事后向团队汇报关键结论
- **充分上下文**：创建 Issue 时提供足够上下文，让他人理解并参与
- **鼓励反馈**：经常征求他人意见和输入

## 新成员5项核心职责

团队成员身份不是荣誉头衔，而是带有明确期望的角色。新成员应做到：

### 1. Watch team-compass 仓库

在 GitHub 上 "Watch" team-compass 仓库，接收团队对话的通知。这是团队信息发布的主要渠道。

### 2. 了解团队会议

保持对团队会议的了解。以往会议记录置顶在 [team-compass issues 页面](https://github.com/jupyter-server/team-compass/issues)。

### 3. 参与投票

参与至少**2/3**的团队投票。当投票发起时，你会在 GitHub 上被自动 @提醒。投票权伴随着参与义务。

### 4. 告知长期缺席

如果将长时间不可用（如休假、工作重心转移），告知团队：
- 可以公开说明
- 如果不方便公开，可以私信某位成员转达
- 也可以考虑临时转为[不活跃成员](/concepts/01-team-membership.md)

### 5. 促进开放包容讨论

作为团队成员，你有责任确保社区对话：
- 积极正面
- 包容欢迎新人
- 帮助解答问题
- 引导新贡献者融入社区

## PR合并5项原则

拥有合并权（merge rights）既是**特权**也是**责任**。团队给出了明确但灵活的合并指南：

### 原则1：运用最佳判断

> "As a member of the Jupyter Server team, we trust your judgment, and we ask you to use your best judgment."

团队信任成员的专业判断。这不是推卸责任，而是在共识文化中赋予成员自主权。

### 原则2：确保代码质量

代码应：
- 组织良好、编写周到
- 新功能有文档
- 遵循 Python/JavaScript 等语言的最佳实践

### 原则3：确保有测试

- 新功能**必须**添加测试
- Bug修复**也应**添加测试
- "太小不需要测试"的想法应尽量避免
- 添加测试通常只需要一点时间，未来的自己会感谢现在的决定

### 原则4：确保充分讨论时间

- 开放社区需要时间让他人审查和反馈
- 没有硬性时间规定，但复杂或有争议的变更应多给几天
- 可以主动 @提醒可能感兴趣的人
- 对于大多数变更，直接合并即可

### 原则5：不要害怕合并！

> "Don't be afraid to merge! ... for most changes it is fine to just go ahead and merge. Again, we trust your judgment, and we don't want these guidelines to become a burden that slows down development."

这是对前4条原则的平衡——指南是帮助而非阻碍，信任判断比流程繁琐更重要。

## 社区文化：友善与包容

作为团队成员，你在与他人互动时（线上线下）代表社区。应：
- 保持友好、积极的态度
- 欢迎新人、帮助他人融入
- 耐心回答问题
- 将新贡献者引导至合适的贡献路径

## 相关概念

- [团队成员体系](/concepts/01-team-membership.md)
- [成为团队成员](/concepts/02-becoming-member.md)
- [决策机制](/concepts/03-decision-making.md)
- [周会制度](/concepts/05-weekly-meetings.md)
