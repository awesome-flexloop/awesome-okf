---
okf_version: "0.2"
type: bundle
title: "Knocket：会聊天的个人名片（腾讯 RTC）"
description: "腾讯云 Tencent RTC 旗下网页实时通信/接待产品——Web Widget/Contact Page/Mobile Widget 三功能、Unified Inbox 多渠道统一收件、AI Agent 知识库自动应答，面向一人公司/OPC 的「个人业务总入口」（源自微信博文经官方产品页核验）"
tags: [knocket, tencent-rtc, contact-page, unified-inbox, ai-agent, ai-business-card, opc, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-10-10T13:20:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T13:55:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/GstWn_PvN48fikFsvcsjNA
  - id: knocket-official
    url: https://knocket.trtc.io
  - id: knocket-templates
    url: https://knocket.trtc.io/templates/html-live-chat
  - id: trtc-blog
    url: https://trtc.tencentcloud.com
---

# Knocket：会聊天的个人名片（腾讯 RTC）

> **类型**：商业分析/产品观察（观点+趋势文，无 examples/——操作可复现性两问皆"否"）
> **信源**：微信公众号「怪哥」博文（2026-10，作者怪哥）→ 2026-10-10 经官方产品页 knocket.trtc.io、templates/html-live-chat 与 TRTC 官方博客交叉核验
> **核验结论**：12 项 P0 声明 **8✅ / 4⚠️ / 0❌**（F 编号行级口径 ✅ 9 / ⚠️ 5 / ❌ 0），无核心产品声明失败；⚠️ 均为官方未逐字确认的转述或归观点层的分析
> **数据时点**：产品事实为 2026-10-10 官方页口径；产品处于早期增长期，功能集可能变化

## 本文概要

[Knocket](https://knocket.trtc.io) 是腾讯云 **Tencent RTC** 旗下的网页实时通信/接待产品。它把"独立个人介绍页（Contact Page）+ 页面内嵌实时聊天（Live Chat）+ AI 知识库自动应答 + 多渠道统一收件（Unified Inbox）"打包成一张可分享链接的**"会聊天的个人名片"**。三大功能——Web Widget（网页聊天组件）、Contact Page（独立链接页）、Mobile Widget（移动端内嵌）——面向自媒体博主、知识付费讲师、咨询顾问、独立开发者与"一人公司"（OPC），官方声明核心功能 **100% free forever、无广告**。

## 阅读路径

**先建立概念（10 分钟）**

1. [Knocket 是什么：产品身份与发布事实](concepts/00-what-is-knocket.md)——定位、腾讯 RTC 归属、三功能、免费口径（带 F 编号）
2. [机制原理：Contact Page / Unified Inbox / AI Agent](concepts/01-mechanisms-contact-page-inbox.md)——独立链接、页面聊天、多渠道收件、知识库自动应答如何协同
3. [业务总入口与 AI 做生意趋势](concepts/02-business-card-trend.md)——一人公司/OPC 场景与作者趋势观点（观点层）

**继续溯源核验**

- [博文事实清单](references/article-source.md)（F-001~F-045 双份登记）
- [P0 权威核验报告](references/verification.md)（勘误四张清单）

## 核心事实速查

| 项 | 值 |
|----|-----|
| 归属 | 腾讯云 **Tencent RTC**（实时音视频）旗下应用 |
| 官方入口 | https://knocket.trtc.io（非 `knocket.ai`，个别三方口径） |
| 三功能 | Web Widget（网页聊天组件）/ Contact Page（独立链接页）/ Mobile Widget（移动端内嵌） |
| 核心机制 | Contact Page 内嵌 Live Chat + AI 知识库自动应答/转人工 + Unified Inbox（聚合 Live Chat/Telegram/Email 等） |
| 免费口径 | 核心功能 **100% free forever、无广告**（vs Intercom/Tawk.to） |
| 适用人群 | 自媒体博主/知识付费讲师/咨询顾问/独立开发者/一人公司（OPC） |

## ⚠️ 阅读前必知的四条口径/边界

1. **首发时间不确**：官方未标首发日期，媒体口径不一（"近期上线" vs "上线 2 年"），本束不采信任何修饰性时间声明。
2. **两条"仅博文单源"**：博文称"AI 可以生成页面"、"AI 模型可以自己接"——官方页未逐字确认，正文标"仅博文单源待核"，不当作官方承诺。
3. **"产品壳/引流"是作者观点**：腾讯 RTC"底层能力→产品壳、先吸引用户再商业化"为博文作者分析，官方未如此声明，归观点层。
4. **域名统一**：`knocket.ai` 为个别三方报道，本束一律用官方 trtc.io 域名。

## 采用提示与已知边界

- **闭源商业产品**：Knocket 非开源，本束核心产品事实以官方产品页为准，博文作第三方观察视角；不提供安装/self-host/API 教程（无 public API 文档）。
- **早期增长期**：产品以免费吸引增长，功能集可能快速变化；`stale_after: 2026-12-31` 前复核免费政策、功能集、归属/域名与"AI 生成页面/模型自接"是否落地。
- **观点与事实分层**：一人公司趋势、腾讯战略为作者观点（V 型），与产品事实（O 型）分开呈现，读者勿将观点当官方承诺。

## 信源与可信度

- 事实清单与逐条核验状态：[references/article-source.md](references/article-source.md)（F-001~F-045）
- P0 核验报告与勘误四张清单：[references/verification.md](references/verification.md)
- 信源距离：第三方产品观察号（怪哥）→ 已升级为官方产品页 + TRTC 官方博客交叉核验；作者观点显式标"作者观点"

## 主题关联

- [todesk-ai](../todesk-ai/index.md)：ToDesk 跨设备 AI 助手（同为"个人/工具型 AI 接待/助理产品生态"相邻话题）
- [octop](../octop/index.md) 与 [ok-platform](../ok-platform/index.md)：腾讯系其他 AI 产品/研发流程知识包（Knocket 为腾讯 RTC 系 AI 接待产品，同属腾讯 AI 生态）
- [uumit-a2a-marketplace](../uumit-a2a-marketplace/index.md)：AI 能力交易/市场化（从"个人 AI 名片/业务入口"延伸至"AI 能力如何被交易分发"）

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```