---
type: Concept
title: "成员行为指南与沟通规范"
description: "掌握 Council 成员的日常职责、四种沟通渠道的分工、PR合并指南和开放包容的团队文化规范。"
tags: [jupyter, frontends, member-guide, communication, pr-merge, discourse, zulip]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:37:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:37:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: member-guide
    resource: /references/member-guide-source.md
    title: "成员指南信源"
---

# 成员行为指南与沟通规范

成员指南为 Jupyter Frontends Council 成员提供资源导航、行为准则和操作规范，帮助成员成为高效、愉快的团队参与者。成员资格不应成为负担——许多成员都有其他全职工作，但有几项基本职责需要履行。

## 团队核心资源

| 资源 | 用途 |
|------|------|
| [Team Compass 仓库](https://github.com/jupyterlab/frontends-team-compass) | 团队相关信息中心：开发提示、会议信息、里程碑、路线图 |
| [Team Compass Issues](https://github.com/jupyterlab/frontends-team-compass/issues) | 团队事务讨论：改进团队运作流程、投票事项、会议追踪 |

## 四种沟通渠道与分工

团队明确区分不同沟通渠道的使用场景，帮助贡献者和维护者找到正确的讨论场所：

| 渠道 | 适用场景 | 特点 |
|------|---------|------|
| **GitHub Issues** | 特定仓库的变更讨论（功能请求、Bug 报告） | 异步、可追踪、代码关联 |
| **Discourse 论坛** | 通用讨论、支持问题、灵感交流 | 公开、长文、社区广度 |
| **Zulip** | 实时讨论和支持问题 | 即时、流式、话题线程 |
| **Council 邮件列表** | 成员资格、非公开问题 | 私密、正式、成员专属 |

### 渠道选择原则

- **Bug/功能请求** → 对应仓库的 GitHub Issues
- **"我该怎么做"/"为什么这样设计"** → Discourse 或 Zulip
- **成员提名/权限变更/敏感话题** → 邮件列表
- **快速问答/实时协作** → Zulip

## 成员五项基本职责

### 1. Watch 关键仓库

"Watch" [frontends-team-compass](https://github.com/jupyterlab/frontends-team-compass) 和 [council](https://github.com/jupyterlab/council) 仓库，确保收到团队讨论通知。

### 2. 了解会议动态

通过 Issues 页面置顶的会议记录，随时了解团队最新进展。即使不能参加每次会议，也应浏览会议记录。

### 3. 参与投票

当投票被发起时，GitHub 会自动 ping 你。成员每年应参与至少 **2/3** 的投票。投票是成员的核心权利和义务。

### 4. 请假通知

如果将长期不在（休假、专注其他项目等），请告知团队。这完全没问题——公开 Issue 或私下邮件给任一成员转达均可。知道谁会在场有助于团队协调。

### 5. 促进开放包容讨论

这是最重要的文化职责：

- 在公开空间进行大部分交流，让其他人可以加入
- 如果重要对话发生在离线场合，向团队成员汇报关键结论
- 创建 Issue 时提供充分上下文，让其他人能理解并提供意见
- 经常鼓励反馈和意见输入
- 合并代码时保持耐心——多等一会儿审批总比自行合入好
- 代表社区与外部互动时，保持友好、积极、欢迎的态度

## PR 合并五条原则

拥有合并权既是特权也是责任。以下是合并决策时的指南：

### 原则一：运用最佳判断

团队信任你的判断力。这些指南不是硬性规则，而是帮助思考的框架。

### 原则二：确保代码质量

- 代码组织良好、撰写用心
- 新功能有文档
- 遵循 Python/JavaScript 等语言的最佳实践

### 原则三：确保有测试

新功能和 Bug 修复都应附带测试。很容易觉得某个改动"太小不需要测试"，但请尽量避免这种想法——添加测试通常只需片刻，未来的自己会感谢现在的决定。

### 原则四：留足讨论时间

开放社区的包容性决策过程意味着有时需要放慢脚步，确保他人有机会审阅和发表意见。虽然没有硬性规定，但：

- 可以主动 ping 可能对该问题感兴趣的人
- 如果议题足够复杂或可能引起争议，多给几天讨论时间

### 原则五：不要害怕合并

这与上一条看似矛盾，实则是平衡：大多数变更直接合入即可，不必过度审批。信任判断力，不要让指南拖慢开发速度。

## 帮助他人贡献

作为团队成员，你应该通过以下方式帮助他人贡献：

- 审查代码，提供建设性反馈
- 指导贡献者完善他们的提交
- 最终将合格的贡献合入项目
- 回答社区问题时保持耐心和友好
- 主动欢迎新人参与

## 相关概念

- [决策制定流程](03-decision-making.md) — 共识优先、投票兜底的决策模型
- [Frontends Council 架构](01-team-council.md) — 成员准入、Release Team 和 Admin Team
- [扩展贡献流程](06-extension-contribution.md) — 外部扩展如何纳入 JupyterLab 组织
