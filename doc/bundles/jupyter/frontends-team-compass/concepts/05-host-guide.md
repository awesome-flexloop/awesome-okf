---
type: Concept
title: "会议主持指南"
description: "学习如何主持 Jupyter Frontends 周会——主持人职责、开场脚本、录制规范、会后工作和反骚扰机制。"
tags: [jupyter, frontends, host-guide, meetings, facilitation, code-of-conduct]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:37:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:37:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: host-guide
    resource: /references/host-guide-source.md
    title: "会议主持指南信源"
---

# 会议主持指南

Jupyter Frontends 鼓励所有感兴趣的贡献者主持周会——不限于 Council 成员。主持会议是参与团队建设的好方式，本指南提供完整的主持流程、脚本模板和注意事项。

## 会议基调

每次会议都应：

- **积极友好**：营造轻松愉快的氛围
- **欢迎多元背景**：特别欢迎新参与者
- **鼓励参与**：新人可以自由发言、自我介绍，也可以选择旁听

## 主持人六项核心职责

主持人负责引导会议流程，具体包括：

### 1. 签到与议程提醒

- 提醒大家签到（在 HackMD 记录上添加自己的名字）
- 将会议记录链接粘贴到聊天中——可以多次粘贴，因为新加入者看不到之前的聊天消息

### 2. 推进议程

- 按照议程逐项讨论
- 进行时间检查：时间紧张时暂停当前议题，推进到下一项
- 确保所有议题都有机会被覆盖

### 3. 引导讨论

- **为参与者和录音朗读聊天内容**——线上会议中聊天信息很容易被忽略
- 帮助澄清问题，确保讨论聚焦
- 邀请沉默的参与者发表意见

### 4. 维持秩序

- 有人举手（Zoom "Raise Hand"）时，及时打断当前讨论让其发言
- 确保每个人都有机会说话，避免少数人垄断讨论
- 礼貌地控制超时发言

### 5. 提及行为准则

- 在开场时链接并提及 Jupyter Code of Conduct
- 强调所有人（包括主持人）都受其约束
- 如遇不当行为，按 CoC 流程处理

### 6. 录制管理

- 与协助者配合控制录制的开始和结束
- 明确告知录制状态变更

## 与会议协助者配合

主持人通常与一位**会议协助者**（meeting facilitator）搭档：

| 角色 | 职责 |
|------|------|
| **主持人** | 引导讨论、控制时间、维持秩序、朗读聊天 |
| **协助者** | 管理Zoom（使用Project Jupyter账号）、管理HackMD记录、处理录制、移除骚扰者 |

### 协助者的技术工作

- 使用 "Project Jupyter" 主持账号登录（获得管理权限：移除骚扰者、静音、录制等）
  - 如需账号权限，向 security@ipython.org 申请
- 在 HackMD 上创建当天的会议记录：添加日期、签到表、议程（每个议程项标注负责人）
- 控制录制的启停
- 移除未经授权的录制机器人

### 反录制机器人机制

根据 Jupyter 社区规定，参与者不得私自录制会议。处理流程：

1. 发现疑似 AI 录制机器人的账号时，要求其自报身份并说明是否在录制
2. 如果该账号无回应，假定其正在录制
3. 将其移出会议

## 开场脚本

以下是标准开场脚本（英文版，会议以英语进行）：

> **Hello and welcome to our [full date] Jupyter Frontends call. I'm [host name] and I'll be your host today.**
> 
> **This is a place for all contributors to connect with each other and the community about JupyterLab, Jupyter Notebook, frontends, and accessibility. A special welcome to all first-time participants! We want all newcomers to feel welcome—we invite you to join in on discussions, introduce yourself, or add items to the agenda.**
> 
> **Please keep in mind that this call will be recorded and posted to YouTube for the community to view. This call is a part of the Jupyter community, therefore we follow the Jupyter Code of Conduct, which you can read about at jupyter.org/conduct.**

### 录制前的 Off-record 提醒

正式录制前：

> **Before we start the recording, does anyone have anything they'd like to say off the record?**
> 
> （等待回应，处理完 off-record 事项后）
> 
> **We will now begin recording.**

议程全部结束后：

> **The recording has ended.**（然后停止录制，开始 off-record 讨论）

## 会后两项工作

恭喜完成主持！🎉 以下是会后需要完成的事项：

### 1. 完善会议记录

回到 HackMD 记录，进行必要的补充、修正和格式化：

- 补充遗漏的关键讨论点
- 修正错别字和格式问题
- 使记录对未参会者也能清晰理解
- 标注行动项（Action Items）和负责人

### 2. 发布会议记录

将当天的会议记录复制为评论，发布到 [frontends-team-compass Issues](https://github.com/jupyterlab/frontends-team-compass/issues) 中对应的会议追踪 Issue（通常是置顶的那个）。

## 主持小技巧

- **多次粘贴会议链接**：Zoom 聊天中后来的人看不到之前的消息，关键链接（HackMD、CoC）可以重复粘贴2-3次
- **主动邀请新人发言**：如果看到陌生名字，温柔地邀请他们自我介绍，但不要强迫
- **时间盒讨论**：每个议题设定时间上限，到时间时总结当前结论并推进
- **记录 Action Items**：讨论中明确的待办事项要在记录中加粗标注负责人
- **保持节奏**：冷场时主动提出下一个议题，不要让沉默持续太久

## 相关概念

- [双周会议制度](02-meetings.md) — 两个周会的时间、形式和归档方式
- [成员行为指南](04-member-guide.md) — 沟通渠道分工和包容文化
- [决策制定流程](03-decision-making.md) — 会议中的共识决策机制
