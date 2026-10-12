---
okf_version: "0.2"
type: Reference
title: "Odyssey-3 事实清单（facts）"
description: "Odyssey-3 基础世界模型的编号事实登记 F-001~F-029：文章信息、产品定义、架构、物理基准、世界模型基准、机械臂、Physical AI 目标"
tags: [odyssey3, facts, world-model, physical-ai]
generated:
  by: "wechat-public-okf:R"
  at: "2026-10-12T10:40:00+08:00"
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

# Odyssey-3 事实清单（facts.md）

> **信源**：主信源 `mp-article`（AI前沿杂谈公众号文）+ 独立核验源 `odyssey-meet`/`odyssey-intro`/`natlaw-press`/`aiwiki`/`aicoder`/`itboltwise`。类型字段 `page_fact`=页面客观事实、`author_claim`=信源作者判断/转述、`verified`=经独立权威源核实的厂商声明。断言为客观描述，不混入执行者推断。

## A. 文章与产品发布信息

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|----------|--------|
| F-001 | 文章标题为《输入一句话直接生成一个能走进去的世界：Odyssey-3开放了》，作者账号为「AI前沿杂谈」（原创）。 | page_fact | mp-article | 文首 | collected |
| F-002 | 文章发布于 2026 年 10 月 12 日 05:05。 | page_fact | mp-article | 文首时间 | collected |
| F-003 | 文章称「10 月 8 日，Odyssey 发布 Odyssey-3」。 | author_claim | mp-article | 正文第 4 段 | verified¹ |
| F-004 | Odyssey 于 2026 年 10 月 8 日正式发布 Odyssey-3（Research Preview 已开放）。 | verified | odyssey-meet / natlaw-press | 官方发布页 | verified |

> ¹ F-003 的发布时间（10 月 8 日）经独立核验成立；AI Wiki 记录 Odyssey-3 于 2026 年 9 月 15 日公布研究论文/预告，10 月 8 日为 Research Preview 正式开放，二者不冲突。

## B. 产品定义与交互范式

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|----------|--------|
| F-005 | Odyssey 对 Odyssey-3 的定义是 foundation world model（基础世界模型）。 | verified | odyssey-meet / natlaw-press | 官方发布页 | verified |
| F-006 | 文章称 Odyssey-3「生成一个环境，然后你可以在里面移动、改变方向、加入新的事件，模型继续实时预测」。 | author_claim | mp-article | 「视频播完了，世界还在继续」 | collected |
| F-007 | 文章对比：传统文生视频是"输入一句话→生成一段固定视频"；Odyssey-3 是"输入一个世界→一边生成、一边行动"。 | author_claim | mp-article | 同上 | collected |
| F-008 | 文章称其交互让「AI 生成内容第一次越来越接近游戏引擎，而不只是视频播放器」。 | author_claim | mp-article | 同上 | collected |
| F-009 | 底层架构为自回归扩散 Transformer（autoregressive diffusion transformer）。 | verified | aiwiki / aicoder / mp-article | AI Wiki / AICoder | verified |
| F-010 | Odyssey-3 发布两个档位：Odyssey-3（480p）与 Odyssey-3 Pro（720p）。 | verified | aicoder | AICoder | verified |
| F-011 | 免费浏览器 Research Preview 运行一个更快的 Flash 变体，支持第一/第三人称导航与独立相机视角。 | verified | aicoder / itboltwise | AICoder / itboltwise | verified |

## C. 物理准确性（Physics-IQ Verified）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|----------|--------|
| F-012 | 文章称在 Physics-IQ Verified 的 video-to-video 测试中，Odyssey-3 Pro 拿到 66.1 分，官方称是「目前公开的最高成绩」。 | author_claim | mp-article | 「它开始学物理了」 | verified² |
| F-013 | Odyssey-3 Pro 在 Physics-IQ Verified video-to-video 基准取得 66.1（best-of-8），为公开最高分（new state of the art）；prompt-enhanced 为 63.4。 | verified | odyssey-meet / aicoder | 官方 + AICoder | verified |
| F-014 | Physics-IQ 评测的真实物理现象包括流体动力学、光学、固体力学、磁学、热力学。 | verified | odyssey-meet / aicoder | 官方 + AICoder | verified |
| F-015 | 文章称 480p 档位（base）得分上下文未给出具体 best-of-8 分；官方口径下 480p 模型 best-of-8 为 64.4、prompt-enhanced 为 61.6、base 为 51.8。 | verified | aicoder | AICoder | verified |

> ² F-012 的"66.1 且为公开最高"经独立核验成立（best-of-8 口径）。文章未说明该分数为 best-of-8 采样、且存在 prompt-enhanced 63.4 的次要口径，标注此遗漏为 `verification.md` 中的 nuance。

## D. 世界模型基准（WorldMark）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|----------|--------|
| F-016 | 文章称在另一个世界模型基准 WorldMark 中，Odyssey-3 在四个类别中的三个拿到第一。 | author_claim | mp-article | 「它开始学物理了」 | verified³ |
| F-017 | WorldMark 中 Odyssey-3 在四类中取三冠：First-Person Stylized 77.2、Third-Person Real 79.0、Third-Person Stylized 76.3；First-Person Real 80.6 列第三。 | verified | odyssey-meet / itboltwise | 官方 + itboltwise | verified |

> ³ F-016 声称的三/四分类第一经独立核验成立。

## E. 真实机械臂能力

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|----------|--------|
| F-018 | 文章称 Odyssey 已把 Odyssey-3 接到真实机械臂上。 | author_claim | mp-article | 「它开始学物理了」 | verified⁴ |
| F-019 | 文章称「只使用几十小时的机器人演示数据，Odyssey-3 就能完成操作任务，而且出现训练演示里没有的恢复动作」。 | author_claim | mp-article | 「它开始学物理了」 | verified⁵ |
| F-020 | 恢复动作示例一：机械臂抓空以后会重新调整夹爪（reorienting a gripper after a missed grasp）。 | verified | odyssey-meet / odyssey-intro | 官方 | verified |
| F-021 | 恢复动作示例二：物体掉到不常见位置会重新找回来（retrieving a dropped object in an unusual position）。 | verified | odyssey-meet / odyssey-intro | 官方 | verified |
| F-022 | 文章的观点：如果模型知道「下一秒世界会怎样变化」，就能反过来决定机器人下一步该怎么动——这才是世界模型真正值钱的地方。 | author_rhetoric | mp-article | 「它开始学物理了」 | collected |

> ⁴ 机械臂接入事实经官方确认。⁵ "tens of hours of robot demonstrations"及"recovery behaviors absent from the training demonstrations"经 odyssey-meet/odyssey-intro 原文核实成立。

## F. Physical AI 领域目标

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|----------|--------|
| F-023 | 文章称 Odyssey 官方列出目标涵盖机器人、人形机器人、自动驾驶汽车、无人机及其他自主系统。 | author_claim | mp-article | 「目标不是游戏，是整个Physical AI」 | verified⁶ |
| F-024 | Odyssey 官方表述 Odyssey-3 为"single learned intelligence operating across many different physical and virtual systems"，可驱动机器人、汽车、无人机、AI 训练与视频游戏。 | verified | odyssey-intro | 官方博客 | verified |
| F-025 | 额外核验：Odyssey-3 仅用 20 小时模拟驾驶数据即可在印度街道闭环自动驾驶、实时生成驾驶轨迹（文章未提及，作为信源补充事实登记）。 | verified | odyssey-intro | 官方博客 | verified |
| F-026 | 文章称训练机器人最贵的是现实世界数据「不可能让一台机器人真的摔十万次、撞十万次」。 | author_rhetoric | mp-article | 「目标不是游戏，是整个Physical AI」 | collected |
| F-027 | 文章称 Google DeepMind、NVIDIA、World Labs、Odyssey 等公司都在往世界模型方向投入。 | author_claim | mp-article | 同上 | collected |
| F-028 | 文章的行业判断：视频生成卷到终点可能不是"生成更真的视频"，而是"让模型理解世界为什么会这样动"。 | author_rhetoric | mp-article | 同上 | collected |

## G. 方法领域定位与展望

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|----------|--------|
| F-029 | 文章的领域定位：从"生成内容"到"生成环境"——AI 把世界生成出来，人和 Agent 直接进去行动；Odyssey-3 离"无限生成一个稳定世界"还有距离。 | author_rhetoric | mp-article | 全文结尾 | collected |