---
okf_version: "0.2"
type: Concept
title: "它开始学物理了：物理基准与现代机械臂"
description: "Odyssey-3 的物理保真评估——Physics-IQ Verified 66.1、WorldMark 3/4 第一、几十小时演示数据控制机械臂与训练外恢复动作"
tags: [odyssey3, physics-iq, worldmark, robot-arm, benchmark]
generated:
  by: "wechat-public-okf:E"
  at: "2026-10-12T11:25:00+08:00"
status: draft
stale_after: 2027-01-31
sources:
  - id: mp-article
    url: "https://mp.weixin.qq.com/s/Mp-OShUFInPxx58eZind-w"
  - id: odyssey-meet
    url: "https://odyssey.systems/meet-odyssey-3"
  - id: odyssey-intro
    url: "https://odyssey.systems/introducing-odyssey-3"
  - id: aicoder
    url: "https://www.aicoder.com/news/news-20261009-odyssey-3-world-model-physics-iq-sota"
  - id: itboltwise
    url: "https://www.it-boltwise.de/odyssey-3-kostenlos-testbares-ki-weltmodell-erzeugt-interaktive-echtwelten.html"
---

# 它开始学"物理"了：物理基准与现代机械臂

> 本概念对应事实：F-012~F-022。物理准确性是世界模型与视频模型的分水岭（knowledge-map M2）。

## 1. 为什么物理是世界模型的命门

世界模型最怕的不是画面不好看，而是物理规律混乱——杯子掉下突然飞起、液体不流动、物体碰撞后穿过去（F-008 背景）。这类问题在短视频里能"糊弄"，但用来自动驾驶/机器人等**闭环决策**场景就完全不可用。因此 Odyssey-3 把物理准确性列为研究核心。

## 2. Physics-IQ Verified 基准成绩

- 在 Physics-IQ Verified 的 **video-to-video** 测试中，**Odyssey-3 Pro 达到 66.1（best-of-8）**，官方称为公开最高分（F-012/F-013）。
- 得分性质：厂商自宣，独立媒体转引（AICoder），**尚无第三方独立复测**（见 verification 口径注意）。
- 评测覆盖的真实物理现象：**流体动力学、光学、固体力学、磁学、热力学**（F-014）。

## 3. WorldMark 世界模型基准

在 WorldMark 基准中，Odyssey-3 在四个类别中**三冠**（F-016）：

| 类别 | 分数 |
|------|------|
| First-Person Stylized | 77.2（第一） |
| Third-Person Real | 79.0（第一） |
| Third-Person Stylized | 76.3（第一） |
| First-Person Real | 80.6（第三） |

（F-017，来源 odyssey.systems / IT Boltwise。）

## 4. 真实机械臂：几十小时数据 + 训练外恢复

Odyssey 已把 Odyssey-3 接到真实机械臂（F-018）：

- **数据量**：仅使用**几十小时**机器人演示数据（F-019，官方原文 "tens of hours of robot demonstrations"）。
- **能力**：完成多步操作任务，由自然语言指令驱动（如"把麦片倒进碗里"）。
- **关键现象——训练外恢复行为**（F-020/F-021）：
  - 机械臂**抓空后重新调整夹爪**（reorienting a gripper after a missed grasp）；
  - **物体落到了不常见位置会重新找回来**（retrieving a dropped object in an unusual position）。

这些恢复动作**不存在于训练演示数据中**，暗示预训练阶段获得的物理/世界理解产生了真实泛化，而非简单的演示记忆（F-020/F-021 + AI Wiki/TechTimes 佐证）。

## 5. 机制解读

文章的观点（F-022）：如果模型知道"下一秒世界如何变化"，就能反过来决定机器人下一步怎么动——这才是世界模型真正值钱的地方。这与 knowledge-map 的 M3 一致：**世界知识在预训练中学会，真实数据只做本体/任务适配**，从而把昂贵现实采集压缩到几十小时。

## 延伸

- 想理解这些能力服务于什么目标，见 [目标不是游戏，是整个 Physical AI](02-physical-ai-goals.md)。
- 想了解这条路线当前的边界，见 [从"生成内容"到"生成环境"：边界与展望](03-generating-environments.md)。