---
type: concept
title: 00 · 研究事实卡与边界
description: Apple Health AI Usage Study 的公告时间、主体、形态、合作方与五个 W，以及「不是什么」边界清单
tags: [apple, health-ai, facts-card, boundary, research-study]
generated:
  by: workbuddy/seven-concepts-cmd
  at: "2026-11-17T12:30:00+08:00"
status: stable
stale_after: 2027-05-17
sources:
  - id: apple-newsroom-2026-11-15
    resource: https://www.apple.com/newsroom/2026/11/apple-launches-research-study-to-explore-the-use-of-ai-for-health/
    title: Apple Newsroom 官方公告（2026-11-15 UPDATE）
  - id: iclarified-103551
    resource: https://iclarified.com/103551
    title: Apple Launches Health AI Study With OpenEvidence for U.S. Adults（二手报道）
---

# 00 · 研究事实卡与边界

读厂商公告的第一步不是归纳亮点，而是先把「它是什么」和「它不是什么」分开摆好。本页只登记官方稿可直证的事实，媒体补充一律显式标注。

## 五个 W 事实卡

| 项 | 官方口径 | 事实编号 |
|----|----------|----------|
| **What** | Apple Health AI Usage Study，一项虚拟研究（virtual research study）及配套研究 App | F-002、F-003 |
| **When** | 公告页标注 `UPDATE November 15, 2026`；多家媒体报道发布于 11 月 15 日、跟进于 11 月 16 日 | F-001 |
| **Where** | 美国境内（United States），美国区 App Store | F-003、F-039、F-041 |
| **Who** | Apple 发起，与 OpenEvidence 合作；Apple 健康与健身副总裁 Sumbul Desai 医学博士、UCSF 医学系主任 Robert M. Wachter 医学博士在稿中被引述 | F-006、F-012、F-015 |
| **Why** | 推进对「人们如何与对话式健康 AI 工具交互」的理解，为 Apple 与行业负责任地设计健康 AI 体验提供依据 | F-004、F-005 |

## 研究形态的三层拆解

1. **研究对象**：人与对话式健康 AI 的交互过程，观察维度为信任、回答质量、理解与日常健康行动（F-007～F-010，详见 [01 篇](01-four-measurement-axes.md)）。
2. **研究载体**：一款独立的研究 App，由 Apple 设计研究体验，健康问答能力由 OpenEvidence 提供（F-018、F-019，详见 [02 篇](02-clinical-grounding.md)）。
3. **研究边界**：非诊断、非治疗、不替代专业医疗意见；研究数据不用于训练 AI 模型（F-030、F-034，详见 [03 篇](03-privacy-and-guardrails.md)）。

## 「不是什么」清单（教学重点）

| 常见误读 | 官方稿实际写了什么 |
|----------|--------------------|
| 「Apple 上线了健康聊天机器人」 | 官方稿写的是**研究**与**研究 App**，未宣布 Siri 或「健康」App 新增通用健康聊天功能；多家媒体在报道中特别澄清这一点（S4、S6） |
| 「这是 Apple 自研医疗大模型」 | 官方稿写明医学接地的 AI 技术由 OpenEvidence 提供，Apple 设计的是研究体验（F-018） |
| 「App 可以给出诊断」 | 官方稿脚注与多家媒体一致：不用于诊断或治疗，不替代医疗专业意见（F-034） |
| 「参与者数据会用于改进模型」 | 官方稿明确「study data will not be used to train AI models」（F-030） |
| 「全球用户都能参加」 | 美国境内、21 岁及以上、特定机型与系统版本（F-038～F-040，详见 [04 篇](04-eligibility-and-enrollment.md)） |

> 💡 **为什么先写「不是什么」**：健康类公告最容易被二次传播压缩成一句「Apple 做了 XXX」。把否定边界与肯定事实并排登记，读者后续遇到媒体标题时能有一把自己的校准尺。这正是 [06 篇](06-transferable-pattern.md)「公告四层核验」的第一步。

## 术语对齐

| 术语 | 本束用法 |
|------|----------|
| 临床接地（clinical grounding） | 回答以同行评议临床文献为依据并附可点击引文，见 [02 篇](02-clinical-grounding.md) |
| 理解（comprehension） | 官方列出的观察维度之一，指参与者对回答的理解程度，非模型准确率 |
| 护栏（guardrails） | 检测某些令人担忧的问题并建议就医或转向其他资源的安全机制，见 [03 篇](03-privacy-and-guardrails.md) |
| 锚点束 | OKF 目录树计束规则：目录直挂 `concepts/examples/references` 即计 1 束（本知识库规范，非本研究术语） |

完整逐条事实见 [F-001～F-048 事实清单](../references/facts.md)。
