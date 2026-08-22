---
type: Concept
title: "双周会议制度"
description: "掌握 Jupyter Frontends 团队的两个周会（周三 Frontends 会 + 周二 Triage 会）的时间、形式、记录归档方式和主持流程。"
tags: [jupyter, frontends, meetings, triage, weekly-meeting, hackmd, zoom]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:36:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:36:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: "README 文档信源"
  - id: host-guide
    resource: /references/host-guide-source.md
    title: "会议主持指南信源"
---

# 双周会议制度

Jupyter Frontends 团队保持**两个固定周会**的节奏，分别在周二和周三进行。所有会议对社区开放，任何人都可以参加。

## 两个周会

### Frontends 团队周会（周三）

| 属性 | 值 |
|------|-----|
| **时间** | 每周三，太平洋时间 9:00 AM（北京时间次日 0:00/1:00，夏令时切换） |
| **地点** | [Jupyter Zoom 房间](https://zoom.us/j/95228013874) |
| **记录平台** | [HackMD](https://hackmd.io/Y7fBMQPSQ1C08SDGI-fwtg) |
| **主题** | JupyterLab/Notebook 前端方向讨论、路线图、架构决策、社区动态 |

### Triage 周会（周二）

| 属性 | 值 |
|------|-----|
| **时间** | 每周二，太平洋时间 9:00 AM |
| **地点** | 同一 Jupyter Zoom 房间 |
| **记录平台** | [HackMD](https://hackmd.io/HaQ3S_nPSbqaRtk9rj59iA) |
| **主题** | Issue 分类、Bug 评审、PR 初审、待处理事项 |

Triage 会聚焦于**操作性工作**：审核标记为 "Needs Triage" 的 JupyterLab Issue 和 Jupyter Notebook Issue，决定优先级、指派负责人、标记标签。

## 会议记录归档流程

两次会议采用统一的记录归档流程：

```
HackMD 实时协作记录
       │
       ▼
会议结束后完善格式
       │
       ▼
发布为 GitHub Issue 评论
（在 frontends-team-compass 仓库的对应 Issue 中）
```

1. **实时记录**：会议中在 HackMD 上协作编辑
2. **会后完善**：主持人或协助者补充、修正、格式化记录，确保未参会者也能理解
3. **发布归档**：将记录作为评论添加到 frontends-team-compass 仓库中对应的 Issue 上（通常是置顶的会议追踪 Issue）

最新的会议记录 Issue 始终**置顶**在 [frontends-team-compass Issues 页面](https://github.com/jupyterlab/frontends-team-compass/issues)。

## 会议录制规范

Frontends 周会（周三）采用 **on-record / off-record 分段录制**：

| 阶段 | 时间 | 录制 | 内容 |
|------|------|------|------|
| Off-record | 开场约5分钟 | ❌ 不录制 | 社交寒暄、非正式讨论 |
| On-record | 正式议程 | ✅ 录制（云端录制） | 正式讨论、决策、演示 |
| Off-record | 议程结束后 | ❌ 不录制 | Issue Triage、发布准备等敏感话题 |

主持人在开始/停止录制前会明确告知："We will now begin recording" / "The recording has ended"。录制视频发布到 YouTube 供社区观看。

## 主持开放制度

任何感兴趣的贡献者都可以主持会议（不限于 Council 成员）。主持人的核心职责在[会议主持指南](05-host-guide.md)中详述，包括：

- 提醒签到和粘贴会议链接
- 推进议程、控制时间
- 朗读聊天内容（为录音和参与者）
- 维持秩序、确保每个人都有发言机会
- 提及 Code of Conduct

主持人通常与一位**会议协助者**（meeting facilitator）搭档，由协助者负责使用 "Project Jupyter" 主持账号管理会议（移除骚扰者、控制静音、启动/停止录制等）。

## 行为准则

所有会议参与者均受 [Project Jupyter Code of Conduct](https://jupyter.org/governance/conduct/code_of_conduct.html) 约束，主持人也不例外。会议应保持：

- **积极友好**的氛围
- **欢迎多元背景**的参与者
- **特别鼓励新人**参与讨论、自我介绍或仅旁听
- **禁止私自录制**：未经授权的录制机器人会被要求自报身份，无回应则移除

## 相关概念

- [会议主持指南](05-host-guide.md) — 主持人的详细职责、开场脚本和会后工作
- [Frontends Council 架构](01-team-council.md) — Council 成员体系与 SSC 代表
- [沟通渠道与协作规范](04-member-guide.md) — 日常沟通渠道分工
