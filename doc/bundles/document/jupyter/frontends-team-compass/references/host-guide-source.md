---
type: Reference
title: "会议主持指南信源"
description: "docs/host-guide.md 的信源登记，包含会议主持职责、开场脚本、录制规范和善后工作。"
tags: [reference, source, host-guide, meetings, facilitation]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:35:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:35:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: host-guide
    resource: https://github.com/jupyterlab/frontends-team-compass/blob/main/docs/host-guide.md
    title: "docs/host-guide.md"
---

# 会议主持指南信源

**原始文件路径**：`docs/host-guide.md`（改编自 Jupyter 通用 Host Guide）

**内容摘要**：

Host Guide 指导任何感兴趣的贡献者主持会议，确保会议积极、友好、包容。

## 主持人职责
- 提醒签到、在聊天中粘贴会议记录链接（可多次粘贴，新加入者看不到之前消息）
- 推进议程：注意时间控制，适时暂停并进入下一议题
- 引导讨论：为参与者和录音朗读聊天内容
- 维持秩序：有人举手时打断让其发言
- 提及并链接 Jupyter Code of Conduct（主持人也受其约束）

## 与会议协助者配合
- 使用 "Project Jupyter" 主持账号登录（需向 security@ipython.org 申请权限）以获得管理权限（移除垃圾信息者、静音、录制等）
- 在 HackMD 上添加当天日期、签到表和议程（每个议程项需有负责人）
- 会议分 on-record（录制）和 off-record（不录制）两部分：通常开始5分钟后开始录制，所有议程完成后停止录制
- off-record 议题通常包括 Issue triage 和发布准备
- 移除未经授权的录制机器人：要求自报身份和是否录制；无回应则移除

## 开场脚本（Sample Script）
- 欢迎语 + 自我介绍
- 说明会议范围（JupyterLab/Notebook/frontends/accessibility）
- 特别欢迎新参与者
- 告知会议将录制并发到 YouTube
- 提及 Code of Conduct
- 录制前询问 off-record 事项

## 会后工作
1. **完善会议记录**：补充、修正、格式化，使未参会者也能理解
2. **发布记录**：将会议记录作为评论发布到 frontends-team-compass 对应 GitHub Issue

**关键事实锚点**：
- F-024: 主持人6项核心职责
- F-025: on-record/off-record 分段，约5分钟后开始录制
- F-026: 会后两项工作（完善记录+发布到GitHub Issue）
