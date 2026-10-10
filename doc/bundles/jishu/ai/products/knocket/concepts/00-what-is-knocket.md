---
okf_version: "0.2"
type: Concept
title: "Knocket 是什么：产品身份与发布事实"
description: "Knocket 的产品定位、腾讯 RTC 归属、三大功能（Web Widget/Contact Page/Mobile Widget）与域名/版本事实（事实层，所有声明带 F 编号）"
tags: [knocket, tencent-rtc, contact-page, ai-business-card, product-profile]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-10T13:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/GstWn_PvN48fikFsvcsjNA
  - id: knocket-official
    url: https://knocket.trtc.io
  - id: trtc-blog
    url: https://trtc.tencentcloud.com
---

# Knocket 是什么：产品身份与发布事实

> 事实层（What / When / Where / Who）。本文只陈述可核验事实与官方页声明，作者观点见 [02-business-card-trend.md](02-business-card-trend.md)。

## 一句话定位

**Knocket** 是腾讯云 **Tencent RTC（实时音视频）** 旗下的一个网页实时通信/接待产品，定位为"会聊天的个人名片/业务接待页"：一个可独立发布的个人或业务页面（Contact Page），内嵌实时聊天（Live Chat）、AI Agent 知识库自动应答与多渠道统一收件（Unified Inbox），并可嵌入自有网站与移动端（F-003、F-031、F-032、F-033）。

官方入口：**https://knocket.trtc.io**（F-031）。

> 名称辨析：官方产品页与 templates 页统一使用 **trtc.io** 域名（knocket.trtc.io）；个别三方报道写 `knocket.ai`，本束以官方 trtc.io 为准（见 [verification.md](../references/verification.md) ③ 口径对照）。

## 归属与发布事实

| 项目 | 值 | 出处 |
|------|-----|------|
| 归属 | 腾讯云 **Tencent RTC**（实时音视频 TRTC）旗下应用 | F-003/F-032 |
| 官方域名 | https://knocket.trtc.io | F-031 |
| 首发时间 | 官方页未标注；媒体口径不一（"近期上线" vs "上线 2 年"）。本束**不采信任何修饰性时间声明**，只陈述"2026-10-10 该域名真实可访问" | F-031，见 verification ① |
| 产品形态 | 闭源商业产品（非开源），以免费无广告方式吸引用户 | F-040 |

## 三大功能（官方产品页）

官方产品页将功能划分为 **3 类**（F-033）：

| 功能 | 官方表述 | 对应博文描述 | 出处 |
|------|---------|-------------|------|
| **Web Widget** | 网页聊天组件（HTML 脚本），可嵌入任意网站 | "把聊天组件装到网站上" | F-034 / F-012 |
| **Contact Page** | 独立个人/业务页，可"发布一个可分享链接" | "给自己做一个独立页面""像个人主页/电子名片" | F-035 / F-004 |
| **Mobile Widget** | 移动端内嵌（如 iOS 应用） | "有 App 也可以接进去" | F-039 / F-012 |

### Contact Page（核心）

- 官方确认可**发布一个可分享链接**，独立承载个人/业务信息（F-035）。
- 可容纳：头像、名字、个人介绍、社交账号、作品、服务项目、价格、案例、客户评价、工作经历、FAQ、预约入口、图片、视频与外链（F-004）。
- 页面内嵌 **Live Chat** 聊天窗口，访客浏览介绍后可直接在页面上聊天，无需翻找微信/邮箱（F-036 / F-006）。

### AI Agent 与自动接待

- 官方支持 **"Upload docs and FAQs"**，让 AI 依据上传的文档与常见问题自动回答常规问题（F-038 / F-008）。
- 需要时**转人工**（F-038 / F-014）。
- "AI 生成页面"（自然语言一键搭页）为博文转述，官方页未逐字确认——见 [verification.md](../references/verification.md) ⚠️（F-013/F-041）。

## 免费与收费口径

- 官方对比页（vs Intercom、Tawk.to 等）声明核心功能 **100% free forever、无广告**（F-040）。
- 产品处于早期、以免费吸引增长，"AI 模型可自行接入"等细节官方对比表未明示（F-042 ⚠️，仅博文单源）。
- 收费边界（超额用量、模型调用计费等）官方页未逐字给出，纳入 `stale_after: 2026-12-31` 复核（F-044）。

## 它替代的既有形态（背景）

- 传统"链接页/电子名片"（Link-in-bio、个人主页）——只有静态介绍，无聊天、无 AI 自动应答（F-004、F-028）。
- 传统客服系统（坐席/工单/排班）——对一天几十个咨询的个人业务过重（F-010，作者观点）。
- Knocket 把"个人介绍页 + 实时聊天 + AI 自动应答 + 多渠道收件"合并到一个可分享链接里（F-007、F-037、F-016）。

## 阅读下一篇

- [01 · 机制原理：Contact Page / Unified Inbox / AI Agent](01-mechanisms-contact-page-inbox.md)——三大机制如何协同实现"会聊天的名片"
- [02 · 业务总入口与 AI 做生意趋势](02-business-card-trend.md)——一人公司/OPC 场景与作者趋势观点（观点层）