---
okf_version: "0.2"
type: bundle
title: "Odyssey-3 基础世界模型（Foundation World Model）"
description: "Odyssey-3 深度教程——从生成视频到生成可走进的世界：基础世界模型定义、自回归扩散 Transformer、物理准确性（Physics-IQ 66.1 / WorldMark 3冠）、几十小时数据控真实机械臂与训练外恢复行为、Physical AI 宏大目标与生成式训练场"
sources:
  - id: mp-article
    resource: "https://mp.weixin.qq.com/s/Mp-OShUFInPxx58eZind-w"
    title: "输入一句话直接生成一个能走进去的世界：Odyssey-3开放了"
    author: "AI前沿杂谈"
  - id: odyssey-meet
    resource: "https://odyssey.systems/meet-odyssey-3"
    title: "Meet Odyssey-3: Our Most Powerful Foundation World Model"
    author: "Odyssey"
  - id: odyssey-intro
    resource: "https://odyssey.systems/introducing-odyssey-3"
    title: "Introducing Odyssey-3: A General-Purpose Physical Intelligence"
    author: "Oliver Cameron & Jeff Hawke (Odyssey)"
  - id: natlaw-press
    resource: "https://natlawreview.com/press-releases/odyssey-launches-odyssey-3-its-most-powerful-foundation-world-model-built"
    title: "Odyssey Launches Odyssey-3, Its Most Powerful Foundation World Model"
    author: "Business Wire via NATLAW Review"
  - id: aiwiki
    resource: "https://aiwiki.ai/wiki/odyssey_3"
    title: "Odyssey-3 | AI Wiki"
    author: "AI Wiki"
  - id: aicoder
    resource: "https://www.aicoder.com/news/news-20261009-odyssey-3-world-model-physics-iq-sota"
    title: "Odyssey launches Odyssey-3 world model: new SOTA 66.1 on Physics-IQ"
    author: "AICoder"
  - id: itboltwise
    resource: "https://www.it-boltwise.de/odyssey-3-kostenlos-testbares-ki-weltmodell-erzeugt-interaktive-echtwelten.html"
    title: "Odyssey-3: KI-Weltmodell erzeugt interaktive Echtwelten"
    author: "IT Boltwise"
generated:
  by: "wechat-public-okf"
  at: "2026-10-12T11:45:00+08:00"
status: draft
stale_after: 2027-01-31
---

# Odyssey-3 基础世界模型（Foundation World Model）

> 基于 AI 前沿杂谈公众号文《输入一句话直接生成一个能走进去的世界：Odyssey-3开放了》深度转化，并经 Odyssey 官方站点、商业新闻稿、AI Wiki、AICoder、IT Boltwise 独立核验。主信源为自媒体综述，所有转述的量化声明均经 P0 独立核验后才判为 verified；厂商自宣成绩与独立复测口径明确分离。

## 一句话

Odyssey-3 是 AI 公司 Odyssey 于 2026 年 10 月 8 日发布的基础世界模型——它不是"生成一段播完的视频"，而是**生成一个可以走进去、被操作、并实时响应反馈的环境**，最终目标是支撑 Physical AI（机器人、人形、自动驾驶、无人机）。

## 内容导航

### 概念教程（concepts）

- [Odyssey-3 概览：从生成视频到生成可走进的世界](concepts/00-overview.md)
- [它开始学"物理"了：物理基准与现代机械臂](concepts/01-physics-and-robot.md)
- [目标不是游戏，是整个 Physical AI](concepts/02-physical-ai-goals.md)
- [从"生成内容"到"生成环境"：边界与展望](concepts/03-generating-environments.md)

### 参考资料（references）

- [Odyssey-3 参考资料索引](references/index.md)
- [信源登记（source-manifest）](references/source-manifest.md)
- [事实清单（facts）](references/facts.md)
- [P0 核验记录（verification）](references/verification.md)
- [知识地图（knowledge-map）](references/knowledge-map.md)

## 关键数字速览

| 指标 | 数值 | 口径 |
|------|------|------|
| 发布时间 | 2026-10-08（Research Preview 开放） | 官方 |
| 底层架构 | 自回归扩散 Transformer | 官方 |
| Physics-IQ Verified（video-to-video） | Pro 66.1（best-of-8），新 SOTA | 厂商自宣 |
| WorldMark | 四类中三冠 | 厂商自宣 |
| 机械臂演示数据 | 几十小时 | 官方 |
| 机械臂训练外恢复 | 抓空重握 / 异常位置取回 | 官方 |
| 自动驾驶演示数据 | 20 小时模拟数据闭环驾驶 | 官方 |

> ⚠️ 物理基准与 WorldMark 分数为**厂商自宣、独立媒体转引、未经第三方独立复测**；教程按"自宣 vs 复测"分级呈现，消费时请保留此区分。

## 主要史实

- Odyssey 是一家成立于 2023 年的 AI 研究公司，创始人为 Oliver Cameron 与 Jeff Hawke（AI Wiki）。
- Odyssey-3 于 2026-09-15 公布技术预告/论文，2026-10-08 Research Preview 正式开放（verification.md 双口径）。

```{toctree}
:maxdepth: 2

concepts/index
references/index
log
```