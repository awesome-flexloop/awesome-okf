---
type: Example
title: "主持一次 Frontends 周会"
description: "从头到尾实操演示如何主持一次 Jupyter Frontends 周会，包含会前准备、开场脚本、议程推进、录制管理和善后工作。"
tags: [example, meeting, host, facilitation, how-to]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:39:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:39:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: host-guide
    resource: /references/host-guide-source.md
    title: "会议主持指南信源"
  - id: readme
    resource: /references/readme-source.md
    title: "README 文档信源"
---

# 主持一次 Frontends 周会

本文以一个完整的 Frontends 团队周会（周三）为例，演示从头到尾的主持流程。

## 场景设定

- **日期**：某个周三
- **时间**：太平洋时间 9:00 AM（北京时间次日 0:00/1:00）
- **平台**：Jupyter Zoom
- **你的角色**：主持人（Host）
- **协助者**：另一位贡献者（Facilitator）

## 第一阶段：会前准备（会议开始前 10 分钟）

### 1. 与协助者确认分工

在 Zulip 或邮件中提前联系一位协助者：

```
你：Hi! I'll host tomorrow's Frontends call. Would you be able to facilitate?
协助者：Sure! I'll handle the Zoom hosting account and HackMD.
你：Great! I'll send the agenda items. Can you log in with the Project Jupyter account?
协助者：Got it.
```

### 2. 准备议程

在 [HackMD](https://hackmd.io/Y7fBMQPSQ1C08SDGI-fwtg) 上创建新的会议记录页面：

```markdown
# Jupyter Frontends Weekly Meeting — 2026-08-26

**Attendees** (add your name):
- Your Name (@yourhandle, Your Affiliation)

**Agenda** (add items with your name):
1. Welcome and newcomers (Host) — 5 min
2. JupyterLab 4.4 release update (@jtpio) — 10 min
3. Accessibility in Notebook 7.3 (@krassowski) — 10 min
4. Open discussion / Q&A — 10 min
5. Action items review (Host) — 5 min
```

## 第二阶段：会议开始（0:00-5:00）

### 3. 开放 Zoom 房间

会议开始前 2-3 分钟进入 Zoom。协助者使用 "Project Jupyter" 账号登录以获得管理权限。

### 4. 开场（0:00-2:00）

> "Hello and welcome to our August 26th Jupyter Frontends call. I'm [Your Name] and I'll be your host today."

> "This is a place for all contributors to connect with each other and the community about JupyterLab, Jupyter Notebook, frontends, and accessibility."

> "A special welcome to all first-time participants! We want all newcomers to feel welcome—we invite you to join in on discussions, introduce yourself, or add items to the agenda. If you'd like to introduce yourself now, feel free to raise your hand or type in chat."

（等待新人自我介绍，如有）

> "Please keep in mind that this call will be recorded and posted to YouTube for the community to view. This call is a part of the Jupyter community, therefore we follow the Jupyter Code of Conduct, which you can read about at jupyter.org/conduct."

### 5. 签到提醒

在聊天中粘贴 HackMD 链接：

> "Please add your name to the attendees list in the meeting notes: [HackMD link]. I'll paste this link a couple times for people joining later."

（2-3分钟后再粘贴一次）

### 6. Off-record 阶段和录制开始（5:00）

> "Before we start the recording, does anyone have anything they'd like to say off the record?"

（等待回应，处理 off-record 事项，通常是简短的社交寒暄）

> "We will now begin recording."

（向协助者打手势开始云录制）

## 第三阶段：推进议程（5:00-50:00）

### 7. 逐项推进议程

对于每个议程项：

1. **邀请负责人发言**：
   > "Next up, Jeremy is going to give us an update on the JupyterLab 4.4 release. Jeremy, go ahead!"

2. **时间管理**：
   - 议程时间过半时：
     > "Thanks Jeremy, we have about 3 minutes left for this topic."
   - 超时：
     > "I want to make sure we cover the remaining items. Can we table this discussion for a GitHub issue or next week's meeting?"

3. **朗读聊天**：
   - 有人在聊天中提问/评论时：
     > "There's a question in chat from Marta: 'Will this affect the extension API?' Let me read that for the recording..."

4. **处理举手**：
   - 看到有人举手时：
     > "I see Isabel has their hand raised. Go ahead Isabel."

### 8. 保持包容性

- 注意讨论中是否有人被忽略
- 如果少数人垄断讨论：
  > "Thanks for that input. Let's hear from others who might have thoughts on this."
- 如果出现争议：
  > "This is a great discussion. Given our time, let's capture the different perspectives in a GitHub issue and continue there."

## 第四阶段：结束录制和 Off-record（50:00-60:00）

### 9. 最后召集

> "Are there any final items before we wrap up the recorded portion?"

（等待回应）

### 10. 行动项回顾

> "Let me quickly review the action items from today:
> - @jtpio will open a PR for the 4.4 release notes by Friday
> - @krassowski will file an issue about the ARIA labels
> - I'll follow up on the documentation update PR"

### 11. 停止录制

> "The recording has ended. Thank you everyone!"

（向协助者示意停止录制）

### 12. Off-record 讨论

录制停止后，可以进行 off-record 讨论，通常包括：
- Issue Triage：快速过一下待分类的 Issue
- 发布准备：讨论尚未公开的发布计划
- 敏感话题：不适合公开记录的讨论

## 第五阶段：会后工作

### 13. 完善会议记录

会议结束后，尽快完善 HackMD 记录：

- ✅ 补充自己笔记中遗漏的要点
- ✅ 修正错别字和格式
- ✅ 加粗标记 Action Items 和负责人
- ✅ 确保每个讨论点有结论或后续行动
- ✅ 格式化为未参会者也能理解的样子

### 14. 发布记录

将完善后的会议记录复制为评论，发布到 [frontends-team-compass Issues](https://github.com/jupyterlab/frontends-team-compass/issues) 中置顶的会议追踪 Issue：

```markdown
## Meeting Notes — August 26, 2026

[Paste formatted notes here]

**Action Items:**
- @jtpio: Open PR for 4.4 release notes (due Aug 29)
- @krassowski: File ARIA labels issue
- @yourname: Follow up on docs update PR
```

### 15. 给自己点赞 🎉

> "Congratulations on hosting your first meeting! Contributions like yours help make the Jupyter community better!"

## 常见问题处理

| 情况 | 处理方式 |
|------|---------|
| 没有人来参加 | 正常，等待 5 分钟后宣布取消，记录在 Issue 中 |
| 讨论跑题 | 温和打断："This is a great topic, but let's get back to the agenda or take it offline." |
| 有人违反 CoC | 私聊提醒；严重时按 Jupyter CoC 事件响应流程处理 |
| Zoom 出现技术问题 | 使用聊天沟通；协助者处理技术问题时主持人继续推进 |
| 议程提前结束 | 开放自由讨论或提前结束，尊重大家的时间 |

## 相关概念

- [双周会议制度](/concepts/02-meetings.md) — 两个周会的时间和定位
- [会议主持指南](/concepts/05-host-guide.md) — 主持人的完整职责规范
- [成员行为指南](/concepts/04-member-guide.md) — 沟通渠道和包容文化
