---
okf_version: "0.2"
type: Concept
title: "机制原理：Contact Page / Unified Inbox / AI Agent 知识库"
description: "Knocket 三大机制如何协同实现「会聊天的名片」——独立页面、实时聊天、多渠道统一收件与 AI 知识库自动应答/转人工（机制层，声明带 F 编号）"
tags: [knocket, contact-page, unified-inbox, ai-agent, live-chat, knowledge-base]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-10T13:05:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/GstWn_PvN48fikFsvcsjNA
  - id: knocket-official
    url: https://knocket.trtc.io
  - id: knocket-templates
    url: https://knocket.trtc.io/templates/html-live-chat
---

# 机制原理：Contact Page / Unified Inbox / AI Agent 知识库

> 机制层（How）。本文拆解 Knocket 的核心机制，说明"会聊天的名片/业务总入口"是如何实现的。产品事实来自官方页，作者使用观感归观点层。

## 机制一：Contact Page——独立可分享的个人业务页

Contact Page 是 Knocket 的枢纽，官方确认可**发布一个可分享链接**（F-035）。它的作用是先把"你是谁、你能提供什么、怎么联系你"一次讲清楚（F-004、F-025）：

- **承载力**：头像、名字、介绍、社交账号，及作品、服务项目、价格、案例、客户评价、工作经历、FAQ、预约入口、图片、视频和外链（F-004）。
- **分发**：该链接可被放到公众号菜单、文章底部、小红书主页、个人简介、邮件签名、线下活动二维码等任意有流量的位置（F-011）。
- **开头接住"联系你"需求**：作者观察强调，个人业务最常被问到的问题是"怎么联系你"，Contact Page 把这个入口前置——先展示，再对话（F-022、F-023）。

## 机制二：页面内嵌 Live Chat——访客直接聊

- 官方在 Contact Page 内嵌 **Live Chat** 聊天窗口（F-036）。
- 访客看完介绍后如有疑问，无需翻找微信/邮箱，直接在页面上聊（F-006）。
- 该组件也可作为 **Web Widget**（HTML 脚本）嵌入独立网站（F-034），或经 **Mobile Widget** 内嵌到移动端 App（F-039）——对应"有官网/有 App 也能接进去"。

## 机制三：Unified Inbox——多渠道消息统一归还

- 官方 **Unified Inbox（统一收件箱）** 聚合多个渠道的消息：Live Chat、Telegram、Email（产品页图片另含 WhatsApp、Instagram）；templates 页文字明确写 "Unified inbox (Live Chat, Telegram, and Email)"（F-037）。
- 效果：无论访客从页面聊天、Telegram 还是邮件进来，消息都汇总到同一个收件箱，避免"消息散落"（F-012、F-037）。

## 机制四：AI Agent + 知识库——自动应答与转人工

- 官方支持 **"Upload docs and FAQs"**：把 FAQ、网站内容、产品资料、服务说明上传，让 AI 依据这些内容自动回答常规问题（F-038 / F-008）。
- 需要时**转人工**（F-038）。
- **定位逻辑**（作者观点，F-010）：这对日咨询量几十、不需要坐席/工单/排班的个人业务足够；AI 先接高频重复问题，复杂问题再找本人（F-009）。
- "AI 生成页面"（自然语言一键搭页）为博文转述，官方页未逐字确认，标"仅博文单源"（F-013/F-041）。

## 三机制协同图

```
                      流量入口（公众号/小红书/网站/邮件签名/线下二维码…）
                                      │
                          ┌───────────▼───────────┐
                          │     Contact Page       │  ← 独立可分享链接（F-035）
                          │  个人业务总入口（你是谁/能提供什么/怎么联系）│
                          └───────────┬───────────┘
                      页面内嵌 Live Chat │           Web Widget（嵌入网站）
                          ┌───────────▼───────────┐   Mobile Widget（移动端）
                          │   AI Agent + 知识库     │
                          │   FAQ/文档自动回答 → 需时转人工 │
                          └───────────┬───────────┘
                          ┌───────────▼───────────┐
                          │     Unified Inbox      │  ← 聚合 Live Chat/Telegram/Email(WhatsApp/Ins)（F-037）
                          └───────────────────────┘
```

## 各机制对应事实速查

| 机制 | 官方表述 | 博文对应 | F（官方/博文） |
|------|---------|---------|---------------|
| Contact Page 独立链接 | publish a shareable link | 独立页面/电子名片 | F-035 / F-004 |
| 页面 Live Chat | Contact Page 内嵌聊天 | 页面里直接聊 | F-036 / F-006 |
| Web/移动 Widget | HTML 脚本 / iOS 内嵌 | 装到网站 / App 接进去 | F-034/F-039 / F-012 |
| Unified Inbox | 聚合 Live Chat/Telegram/Email | 消息统一收回来 | F-037 / F-012 |
| AI 自动应答 | Upload docs and FAQs / 转人工 | FAQ 自动回答 + 人工接管 | F-038 / F-008、F-014 |
| AI 生成页面 | 官方未逐字确认（单源） | 一句话搭页面 | ⚠️ F-041 / F-013 |

## 阅读下一篇

- [02 · 业务总入口与 AI 做生意趋势](02-business-card-trend.md)——为什么这类产品正当时（一人公司/OPC 场景与趋势观点）