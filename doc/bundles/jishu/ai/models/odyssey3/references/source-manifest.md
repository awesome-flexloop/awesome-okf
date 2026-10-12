---
okf_version: "0.2"
type: Reference
title: "Odyssey-3 信源登记（source-manifest）"
description: "Odyssey-3 首个信源的 URL、归属、公开性预检、访问时点与 P0 独立核验来源清单"
tags: [odyssey3, source-manifest, public-gate, world-model, physical-ai]
generated:
  by: "wechat-public-okf:R"
  at: "2026-10-12T10:30:00+08:00"
status: stable
stale_after: 2027-01-31
sources:
  - id: mp-article
    url: "https://mp.weixin.qq.com/s/Mp-OShUFInPxx58eZind-w"
    title: "输入一句话直接生成一个能走进去的世界：Odyssey-3开放了"
    author: "AI前沿杂谈"
  - id: odyssey-meet
    url: "https://odyssey.systems/meet-odyssey-3"
    title: "Meet Odyssey-3: Our Most Powerful Foundation World Model"
    author: "Odyssey"
  - id: odyssey-intro
    url: "https://odyssey.systems/introducing-odyssey-3"
    title: "Introducing Odyssey-3: A General-Purpose Physical Intelligence"
    author: "Oliver Cameron & Jeff Hawke (Odyssey)"
  - id: natlaw-press
    url: "https://natlawreview.com/press-releases/odyssey-launches-odyssey-3-its-most-powerful-foundation-world-model-built"
    title: "Odyssey Launches Odyssey-3, Its Most Powerful Foundation World Model"
    author: "Business Wire press release via NATLAW Review"
  - id: aiwiki
    url: "https://aiwiki.ai/wiki/odyssey_3"
    title: "Odyssey-3 | AI Wiki"
    author: "AI Wiki"
  - id: aicoder
    url: "https://www.aicoder.com/news/news-20261009-odyssey-3-world-model-physics-iq-sota"
    title: "Odyssey launches Odyssey-3 world model: new SOTA 66.1 on Physics-IQ"
    author: "AICoder"
  - id: itboltwise
    url: "https://www.it-boltwise.de/odyssey-3-kostenlos-testbares-ki-weltmodell-erzeugt-interaktive-echtwelten.html"
    title: "Odyssey-3: KI-Weltmodell erzeugt interaktive Echtwelten"
    author: "IT Boltwise"
---

# Odyssey-3 信源登记（source-manifest）

> 公开性预检：本 bundle 的主信源（`mp-article` 微信公众号文章）与全部独立核验信源（Odyssey 官方站、Business Wire 新闻稿、AI Wiki、AICoder、IT Boltwise）均为**公开内容**，无登录墙、无验证码、无邀请码，可通过公开 URL 直接访问，符合公开内容落地标准。
> 采集/核验通道：WebFetch 解析公开 URL（主信源全文）+ WebSearch 独立检索 P0 声明（2026-10-12）。未复制任何页面全文，仅在 facts.md 中登记可验证的结构事实与作者声明。

## 信源清单

| source_id | 类型 | 标题 / 标识 | URL | 归属 / 作者 | 访问时点 | 公开性 | 一/二手 | 状态 |
|-----------|------|------------|-----|------------|---------|--------|---------|------|
| mp-article | 微信公众号文章（主信源） | 输入一句话直接生成一个能走进去的世界：Odyssey-3开放了 | https://mp.weixin.qq.com/s/Mp-OShUFInPxx58eZind-w | AI前沿杂谈（原创） | 2026-10-12 | ✅ 公开 | 二手（自媒体转述/综述） | collected |
| odyssey-meet | 官方发布页 | Meet Odyssey-3: Our Most Powerful Foundation World Model | https://odyssey.systems/meet-odyssey-3 | Odyssey 官方 | 2026-10-12 | ✅ 公开 | 一手（官方） | collected |
| odyssey-intro | 官方博客 | Introducing Odyssey-3: A General-Purpose Physical Intelligence | https://odyssey.systems/introducing-odyssey-3 | Oliver Cameron / Jeff Hawke（Odyssey） | 2026-10-12 | ✅ 公开 | 一手（官方） | collected |
| natlaw-press | 商业新闻稿 | Odyssey Launches Odyssey-3 ... | https://natlawreview.com/press-releases/... | Business Wire via NATLAW Review | 2026-10-12 | ✅ 公开 | 一手（官方新闻稿转引） | collected |
| aiwiki | 独立 Wiki | Odyssey-3 | https://aiwiki.ai/wiki/odyssey_3 | AI Wiki | 2026-10-12 | ✅ 公开 | 二手（独立资料库） | collected |
| aicoder | 行业媒体 | Odyssey world model: SOTA 66.1 on Physics-IQ | https://www.aicoder.com/news/news-20261009-odyssey-3-... | AICoder | 2026-10-12 | ✅ 公开 | 二手（行业媒体） | collected |
| itboltwise | 海外媒体 | Odyssey-3 erzeugt interaktive Echtwelten | https://www.it-boltwise.de/odyssey-3-... | IT Boltwise | 2026-10-12 | ✅ 公开 | 二手（海外媒体） | collected |

## 拾取口径

- **主信源**：`mp-article` 作为本教程的**叙事对象**与**事实采集起点**（覆盖"视频→世界模型""物理准确性""机械臂""Physical AI"五大部分）。因其为自媒体综述，凡涉及其**转述的厂商量化声明**，均以官方源（odyssey-meet / odyssey-intro / natlaw-press）进行 P0 独立核验后才判为 `verified`。
- **口径取舍**：产品能力、基准分数、机械臂演示等**技术事实**以官方一手源为准；`mp-article` 的**行业叙事与判断性表述**（如"下一场竞争装进现实运行规律"）登记为 `author_claim` / `author_rhetoric`，不作规范事实。
- **动态口径**：基准分数、榜单排名等为**快照时点**数据（2026-10-12），会随后续模型更新而变动；本 bundle 记录原数值并附 `stale_after` 时效边界。

## 未采集项 / 停止规则

- 不保存任何页面全文、HTML 转储；仅登记结构化事实与必要命令（符合版权最小引用原则）。
- 页面内嵌图片文字不经 OCR 采集；以正文文字事实为准。
- 主信源全文已读取；官方源的深度文献（白皮书未公开版、完整实验细节）未纳入本轮，仅采用官方站点公开摘要。