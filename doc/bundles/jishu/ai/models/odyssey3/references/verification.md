---
okf_version: "0.2"
type: Reference
title: "Odyssey-3 P0 核验记录（verification）"
description: "对公众号文章的 P0 关键声明做独立核验——发布时间、物理基准 66.1、WorldMark 3/4 第一、机械臂恢复动作、Physical AI 目标，逐条给出权威独立源或 single-source 标注"
tags: [odyssey3, verification, p0, world-model, physical-ai]
generated:
  by: "wechat-public-okf:P0"
  at: "2026-10-12T10:50:00+08:00"
status: stable
stale_after: 2027-01-31
sources:
  - id: mp-article
    url: "https://mp.weixin.qq.com/s/Mp-OShUFInPxx58eZind-w"
  - id: odyssey-meet
    url: "https://odyssey.systems/meet-odyssey-3"
  - id: odyssey-intro
    url: "https://odyssey.systems/introducing-odyssey-3"
  - id: natlaw-press
    url: "https://natlawreview.com/press-releases/odyssey-launches-odyssey-3-its-most-powerful-foundation-world-model-built"
  - id: aiwiki
    url: "https://aiwiki.ai/wiki/odyssey_3"
  - id: aicoder
    url: "https://www.aicoder.com/news/news-20261009-odyssey-3-world-model-physics-iq-sota"
  - id: itboltwise
    url: "https://www.it-boltwise.de/odyssey-3-kostenlos-testbares-ki-weltmodell-erzeugt-interaktive-echtwelten.html"
---

# Odyssey-3 P0 核验记录（verification.md）

> 核验方法：对 `mp-article` 中涉及**日期、数量、百分比、排名、官方声明、普遍化陈述**的关键声明，逐一用独立权威 URL 交叉核验；无独立源者标注 `single-source` 或 `single-source/flagged`。**不将源作者（自媒体）声称升级为研究事实**；厂商自宣成绩与独立媒体口径分开呈现。

## 核验结果总表

| # | 声明（对应 F） | 判定 | 独立权威源 | 备注 |
|---|---|------|-----------|------|
| 1 | 2026-10-08 发布 Odyssey-3、Research Preview 开放（F-003/F-004） | ✅ verified | odyssey.systems/meet-odyssey-3、NATLAW Review（Business Wire 新闻稿） | 官方站点明示 "October 8th, 2026 ... research preview is available now" |
| 2 | Physics-IQ Verified video-to-video 66.1、公开最高（F-012/F-013） | ✅ verified（best-of-8 口径） | odyssey.systems/meet-odyssey-3、AICoder | 官方称 "66.1, the highest reported score"；AICoder 细化：Pro 66.1 best-of-8 / 63.4 prompt-enhanced |
| 3 | Physics-IQ 覆盖流体/光学/固体力学/磁学/热力学（F-014） | ✅ verified | odyssey.systems/meet-odyssey-3、AICoder | 官方 "fluid dynamics, optics, solid mechanics, magnetism, thermodynamics" |
| 4 | WorldMark 四类取三第一（F-016/F-017） | ✅ verified | odyssey.systems/meet-odyssey-3、IT Boltwise | 官方分项分数入表；三冠项目与文章一致 |
| 5 | 底层自回归扩散 Transformer（F-009） | ✅ verified | AI Wiki、AICoder | "autoregressive diffusion transformer" |
| 6 | 几十小时机器人演示数据 + 训练外恢复动作（F-018~F-021） | ✅ verified | odyssey.systems/introducing-odyssey-3、AI Wiki、TechTimes | 官方原文 "tens of hours of robot demonstrations ... recovery behaviors absent from the training demonstrations"；示例（missed grasp 重握 / unusual position 取回）逐字对上 |
| 7 | Physical AI 目标：机器人/人形/自动驾驶/无人机/自主系统（F-023/F-024） | ✅ verified | odyssey.systems/introducing-odyssey-3 | 官方 "power robots, drive cars, train AIs, pilot drones, and even play video games" |
| 8 | "单人/单模型跨物理与虚拟系统"（F-024） | ✅ verified | odyssey.systems/introducing-odyssey-3 | 官方原话 "single learned intelligence operating across many different physical and virtual systems" |
| 9 | 行业公司（Google DeepMind/NVIDIA/World Labs/Odyssey）押注世界模型（F-027） | single-source（作者列举） | — | 整组公司参与世界模型为公开方向，但**具体列举系文章作者概括**，未逐一独立核验；判定为作者视角而非可量化 P0 |
| 10 | 480p 档具体分数（F-015） | ✅ verified（补充源） | AICoder | 文章未给 480p 分；补充登记 best-of-8 64.4 / prompt-enhanced 61.6 / base 51.8 |

## 无独立源 / flagged 项

| # | 声明 | 判定 | 说明 |
|---|---|------|------|
| 11 | "视频生成还在卷 10 秒、20 秒"（文章开篇行业判断） | single-source | 自媒体概括，无法独立量化验证；登记为作者语境非规范事实 |
| 12 | "不可能让机器人真摔十万次、撞十万次"（F-026） | single-source | 作者修辞性陈述，非可核验量化声明 |
| 13 | "AI 生成第一次越来越接近游戏引擎"（F-008） | single-source/flagged | 主观评价，无基准数据支撑，仅作作者观点 |

## 口径注意事项（nuance）

1. **66.1 为 best-of-8 口径**：文章只说"66.1、公开最高"，未说明该分数取多次采样之最佳（best-of-8）。官方与 AICoder 均确认此语义；同基准另有 prompt-enhanced 63.4 的次要口径。教程已如实标注。
2. **发布时间双口径**：Reserch Preview **开放**于 2026-10-08（官方发布页）；AI Wiki 记录**技术论文/预告披露**于 2026-09-15。二者不对立，教程以"Research Preview 开放=2026-10-08"为准。
3. **自宣 vs 独立**：Physics-IQ 66.1 与 WorldMark 3/4 均为**厂商自宣成绩**（Odyssey 官方站点）；虽有媒体转引（AICoder/IT Boltwise/Lookonchain 等），但**无第三方独立复测**。教程保留"厂商自宣、独立媒体转引，未经第三方独立复测"的口径。

## 结论

- 主信源文章全部 **13 项关键量化/声明** 经 P0 核验，**9 项 verified、4 项 single-source（其中 2 项为修辞性作者观点、1 项为行业列举概括）**，无源文硬错误。
- 值得注意的改进点：文章**未给 480p 档分数**、**未标注 best-of-8 口径**、**未区分 Research Preview 开放与预告披露两个日期**——这些已在本 bundle 的 concepts 中补足，避免把自媒体简化表述误当完整事实。