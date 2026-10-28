---
okf_version: "0.2"
type: Concept
title: "OpenMAIC 与 AgentMore 学习搭子是什么：项目身份与公告事实"
description: "OpenMAIC（清华 THU-MAIC 多智能体互动课堂）的身份/版本/技术栈/合规口径，与智谱清言 AgentMore「学习搭子」的公告元信息（事实层，所有声明带 F 编号）"
tags: [openmaic, agentmore, zhipu, thu-maic, product-profile, ai-education]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-28T14:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: announcement
    url: https://agentmore.chatglm.cn/shareFile/m/6ad704d27f8c85cf468aac82
  - id: openmaic-repo
    url: https://github.com/THU-MAIC/OpenMAIC
  - id: openmaic-demo
    url: https://open.maic.chat
---

# OpenMAIC 与 AgentMore 学习搭子是什么

> 事实层（What / When / Where / Who）。本文只陈述公告口径与官方仓库可核验事实；公告宣传语与厂商自述显式标注，作者/厂商观点与产品事实分层呈现。

## 一句话定位

本次公告讲的是两件事的**衔接**：**智谱清言 AgentMore 的「学习搭子」**（智谱侧产品）引入了**清华 OpenMAIC**（开源的多智能体互动课堂项目）的两项学习方法技能——**费曼学习**与**习题带练**，并把 **8 个 OpenMAIC Skill** 同步上新到 AgentMore「Skill 广场」（F-002、F-012）。

- **OpenMAIC**：全称 **Open Multi-Agent Interactive Classroom**，清华大学 **THU-MAIC** 团队开源的多智能体互动课堂平台（F-026）。
- **AgentMore / 学习搭子**：智谱清言（智谱 / Beijing Knowledge Atlas Technology）旗下 AgentMore 模式中的学习助手（F-041、F-042）。
- 官方仓库：**https://github.com/THU-MAIC/OpenMAIC**（F-025）；Live Demo：**https://open.maic.chat**（F-027）。

## 公告元信息

| 项目 | 值 | 出处 |
|------|-----|------|
| 公告标题 | 《清言 × 清华 OpenMAIC，打造你的专属AI老师》 | F-001 |
| 发布方 | 智谱清言 AgentMore 官方（`agentmore.chatglm.cn` 官方分享域） | F-001 |
| 发布日期 | 分享页**未标注具体日期**；本束只登记采集时点 2026-10-28 | F-001，见 [verification ①](../references/verification.md) |
| 篇幅 | 约 700 字（正文实测） | F-001 |
| 内容性质 | 产品能力上新公告（含对话示例 prompt 与 Skill 名称清单，**无可复现的安装/配置/代码/调用流程**） | F-024 |

## OpenMAIC 是什么（官方仓库核验）

| 项 | 值 | 出处 |
|----|-----|------|
| 全称 | **Open Multi-Agent Interactive Classroom** | F-026 |
| 归属 | 清华大学 **THU-MAIC** 团队开源 | F-026 |
| 仓库 / 演示 | github.com/THU-MAIC/OpenMAIC ｜ open.maic.chat（可获取访问码使用托管模式） | F-025 / F-027 |
| 版本节奏 | **v0.1.0（2026-03-26）→ v0.1.1（2026-04-14）→ v0.2.0（2026-04-20）→ v0.2.1（2026-04-26）** | F-028 |
| 技术栈 | Next.js 16 / React 19 / TypeScript 5 / LangGraph 1.1 / Tailwind CSS 4 | F-029 |
| 核心能力 | 一键生成课堂：two-stage pipeline（Outline→Scenes，含 slides/quizzes/交互模块/PBL） | F-043 |

> 版本口径提示：上表为 README News 的最新 release **v0.2.1（2026-04-26）**；第三方/演示页曾出现更高序号公告，本束以官方仓库 release 为准（见 [verification ①](../references/verification.md)）。

## AgentMore「学习搭子」（智谱侧）

- 第三方测评（36氪）证实智谱清言存在**「学习搭子」**与**「Agentmore 模式」**，构成公告可采信旁证（F-041）。
- 智谱清言由智谱（Beijing Knowledge Atlas Technology）开发（App Store 开发者信息，F-042）。
- ⚠️ **边界**：公告称"本次为学习搭子带来费曼学习、习题带练两项新技能"，该**具体能力与命名**未在 OpenMAIC 仓库或智谱公开文档中逐字找到（F-044），属**公告单源**，正文按"厂商公告披露"呈现。

## 热度与合规口径（务必谨慎采用）

| 项 | 多源观测 | 结论 |
|----|---------|------|
| Star 数 | GitHub API **18,538**（2026-10-28）｜GitHubDaily 报道 **33,000+**（2026-08-28）｜第三方站点自宣 **41.5k**｜过期 HTML 缓存 **16.3k**；公告仅模糊称"Github万星项目" | ⚠️ **多口径互斥**（F-030 / F-003）——本束按"带时点观测"分层登记，**不写成单一权威值** |
| License | `LICENSE` 正文 = **MIT**（Copyright (c) 2026 THU-MAIC）；README 徽章 = **AGPL-3.0**；GitHub API license 字段 = **AGPL-3.0** | ⚠️ **三源互斥**（F-031）——并列登记，采用前须以官方 LICENSE 文件与 releases 自行复核 |

## 核验结论与已知边界

- 公告的**可核验骨架全部成立**：项目真实存在、归属清华 THU-MAIC、Live Demo 在线、课程生成能力确有、官方提供引导式 SOP Skill（F-025~F-029、F-037~F-043、F-046）。
- 本次核对**未发现公告存在硬性事实错误**；争议集中于 Star 数、License 口径与厂商自述的 Skill 上新范围（F-046）。
- 公告**未给出** OpenMAIC 的具体 Star 数（F-003），也未给出课程数/用户数等成效数字。
- 归入 `stale_after: 2026-12-31` 复核：Star 数与观测时点、License 是否统一、AgentMore 学习搭子能力集与 Skill 清单、OpenMAIC 版本号。

## 阅读下一篇

- [01 · 两项新技能：费曼学习与习题带练](01-two-new-study-modes.md)——两套三轮学习法及其示例 prompt
- [02 · 8 个 OpenMAIC Skill 与安装口径](02-eight-openmaic-skills.md)——Skill 清单、与官方目录名的映射及公告单源边界
