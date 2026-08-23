---
type: Reference
title: "成员指南信源"
description: "docs/team/member-guide.md 的核心内容摘录，包含团队资源、沟通渠道、成员职责和PR合并原则。"
tags: [reference, member-guide, communication, pr-merge, responsibilities]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: member-guide
    resource: https://github.com/jupyter-server/team-compass/blob/main/docs/team/member-guide.md
    title: "docs/team/member-guide.md"
---

## docs/team/member-guide.md 核心内容

### 团队资源

- **Team Compass 仓库**：包含开发技巧、团队会议信息、里程碑和路线图
- **Team Compass Issues**：讨论与团队相关的具体可操作事项
- **Gitter 频道**（jupyter/jupyter_server）：用于多个项目的实时同步对话
- **Discourse 论坛**（discourse.jupyter.org）：通用讨论、支持问题、灵感交流

### 沟通渠道策略

1. **GitHub Issues**：与变更仓库内容相关的具体讨论（功能请求、Bug报告）
2. **Discourse 论坛**：通用讨论、支持问题、互相启发

### 新成员5项职责

1. **"Watch" team-compass 仓库**：接收团队对话通知
2. **了解团队会议**：保持对团队会议的了解，会议记录置顶在 issues 页面
3. **投票**：参与至少2/3的投票，投票时会被自动 @提醒
4. **告知缺席**：如果将长时间不可用，告知团队（可公开或私信某位成员转达）
5. **促进开放包容讨论**：确保社区对话积极包容；尽量在公开空间沟通；离线重要对话后向团队汇报；创建issue时提供充分上下文；鼓励反馈；合并代码要有耐心——等待批准比自行合并更好

### PR合并指南（5项原则）

拥有合并权既是特权也是责任：

1. **运用最佳判断**：团队信任你的判断
2. **确保代码质量**：代码组织良好、文档齐全、遵循Python/JS最佳实践
3. **确保有测试**：新功能和Bug修复都应添加测试，不要认为"太小不需要测试"
4. **确保充分讨论时间**：开放社区需要时间让他人审查和反馈，复杂议题多等几天
5. **不要害怕合并！**：大多数变更可以直接合并，不要让指南成为开发负担
