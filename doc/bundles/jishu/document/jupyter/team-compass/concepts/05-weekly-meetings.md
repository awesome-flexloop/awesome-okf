---
type: Concept
title: "周会制度"
description: "Jupyter Server 团队周会的时间、地点、议程管理、会议记录归档，以及会议的组织方式。"
tags: [meetings, weekly-meeting, zoom, hackmd, agenda, meeting-notes]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: "README.md 信源"
  - id: member-guide
    resource: /references/member-guide-source.md
    title: "成员指南信源"
---

## 周会基本信息

Jupyter Server 团队举行每周一次的团队会议，作为同步项目进展、讨论技术方向和协调工作的核心场所。

| 项目 | 详情 |
|------|------|
| **频率** | 每周一次 |
| **日期** | 周四（Thursdays） |
| **时间** | 太平洋时间上午 8:00（[时区转换](https://www.thetimezoneconverter.com/?t=8%3A00%20am&tz=San%20Francisco&)） |
| **平台** | Zoom 视频会议 |
| **会议ID** | 95228013874 |

### 时区换算参考

太平洋时间（PT）与常见时区的换算（夏令时期间）：
- 北京时间（CST, UTC+8）：周四 23:00
- UTC：周四 15:00
- 美东时间（ET）：周四 11:00

## 会议议程管理

### HackMD 协作议程

会议议程使用 [HackMD](https://hackmd.io/Wmz_wjrLRHuUbgWphjwRWw) 进行协作编辑。HackMD 是一个支持多人实时编辑的 Markdown 平台，允许：
- 任何人在会前添加议题
- 会议中实时记录讨论要点
- 异步贡献议程内容（即使不能参会也可以提前添加话题）

### 议程内容通常包括

- 上次会议行动项回顾
- 各项目/PR进展更新
- 需要讨论的技术问题
- 新成员提名
- 社区动态分享

## 会议记录归档

会议记录归档在 GitHub Issue 中：[team-compass#57](https://github.com/jupyter-server/team-compass/issues/57)。

选择 GitHub Issue 作为归档方式的好处：
- **可搜索**：GitHub 的搜索功能方便查找历史讨论
- **可评论**：会后可以补充评论和后续行动
- **公开透明**：任何人都可以查看历史会议记录
- **持久存储**：不依赖第三方平台

会议记录通常置顶在 [team-compass issues 页面](https://github.com/jupyter-server/team-compass/issues)，方便成员快速找到。

## 会议参与方式

### 同步参与

通过 Zoom 链接实时参加，可以：
- 直接发言参与讨论
- 通过视频/音频与其他成员互动
- 屏幕分享演示

### 异步参与

如果无法实时参加，可以：
- 提前在 HackMD 议程中添加话题或问题
- 在会后查看会议记录
- 在相关 GitHub Issue 中跟进讨论

### 对成员的期望

根据[成员指南](04-member-guide.md)，活跃成员应"同步或异步地积极参与团队会议"。这意味着：
- 不强制每次都实时参加
- 但应通过异步方式保持知情和参与
- 会议信息应定期关注

## 周会在团队运作中的角色

周会是 Team Compass 的核心实践之一，与文档仓库的其他部分相辅相成：

```
┌─────────────────────────────────────────────┐
│           团队运作的三大支柱                   │
├─────────────┬───────────────┬───────────────┤
│   周会       │  GitHub Issues │  文档/指南     │
│             │               │               │
│ 同步讨论     │ 异步决策       │  制度规范       │
│ 实时协调     │ 投票/提名      │  知识沉淀       │
│ 方向对齐     │ PR审查         │  新人引导       │
└─────────────┴───────────────┴───────────────┘
```

## 相关概念

- [成员指南与PR合并原则](04-member-guide.md)
- [决策机制](03-decision-making.md)
- [文档构建基础设施](06-doc-infrastructure.md)
