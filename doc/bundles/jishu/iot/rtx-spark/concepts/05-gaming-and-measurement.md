---
type: Concept
title: 游戏支持与帧率指标
description: 区分原生渲染、超分辨率、多帧生成和神经渲染，限定 1440p 与加速倍数声明
tags: [DLSS 5, 游戏, 帧率, RTX Spark]
source: ../references/article-source.md
sources:
  - id: facts
    resource: ../references/article-source.md
  - id: cn
    resource: https://blogs.nvidia.cn/blog/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/
  - id: en
    resource: https://nvidianews.nvidia.com/news/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/
  - id: specs
    resource: https://www.nvidia.com/en-us/products/rtx-spark/
  - id: surface
    resource: https://www.microsoft.com/en-us/surface/devices/surface-laptop-ultra
status: stable
stale_after: 2026-12-31
---

# 游戏支持与帧率指标

上市稿摘要称 RTX Spark 可在 1440p 下超过 100 FPS，正文称首发支持数百款游戏（[F-053](../references/article-source.md)）。本包没有获取该摘要对应的完整游戏测试集、预设、DLSS 开关、具体整机与供电条件，因此只能将其引用为厂商声明。

FPS指每秒显示帧数，1440p通常指垂直1440像素的画面规格。中文稿另称相对“当前最常见的Windows SoC”游戏至高9倍（F-062），但未给足基线型号及测试设置；它不能与后文模型2倍、DLSS帧率1.4倍混成一个比较结论。

## 技术名称

| 名称 | 阅读时关注 | 不能混用的指标 |
|---|---|---|
| 光线追踪 | 光照效果及相关计算负载 | 开启与关闭光追的帧率 |
| 超分辨率 | 输入渲染分辨率、输出分辨率、画质档 | 输出 1440p 不等于原生 1440p 渲染 |
| 帧生成 | 真实渲染帧与生成帧的组成 | 显示帧率不等于输入响应更新率 |
| DLSS 5 神经渲染 | 发布稿描述的光照与材质增强 | 某个 AI 模型吞吐不等于整帧吞吐 |
| Reflex | 延迟与响应指标 | 平均 FPS 不能替代端到端延迟 |

平台技术名称见 F-015；NBA 2K27 神经渲染声明见 F-056。中列和右列是**通用测量解释**，不是本文获取的特定游戏 benchmark。

## 两个倍数

发布稿说新 AI 模型运行速度为原来的 2 倍，DLSS 5 帧率最高为原来的 1.4 倍（F-057）。它们分属模型处理与整体帧率指标，不能合并为“游戏帧率翻倍”。

**教学解释**：当某个加速环节只占总帧时间的一部分，缩短这一环节不代表所有其他环节同样缩短。新闻稿未提供足够的时间拆分，因此本文不从两个倍数反推 GPU 利用率或帧时间构成。

## 游戏名单

| 稿件 | 列举的标题 | 用途 |
|---|---|---|
| 中文 | 明日方舟终末地、赛博朋克2077、原神、战争机器事变日、堡垒之夜、漫威争锋、异环、永劫无间、NBA 2K27、燕云十六声、鸣潮 | 中国稿首发支持举例，F-054 |
| 英文 | Cyberpunk 2077、Fortnite、Gears of War E-Day、Marvel Rivals、World of Warcraft、NBA 2K27 | 全球稿首发支持举例，F-055 |

两份名单是举例而非完整兼容数据库；名单不同不能直接判定某游戏在另一地区不可用。Visual Concepts 制作人的合作引语仍来自 NVIDIA 稿件，未独立回读 2K 公告（F-058）。

联网服务、反作弊、驱动、外设、mod 与特定版本都属于后续兼容验收对象。本包未验证这些项目，也不以“Windows 支持”推定所有 x86 游戏可原生执行。

## 测量条件

Surface 页面提醒性能随游戏、资源和配置变化（F-061）。若测试目标是替换现有游戏电脑，**本包建议**固定同一游戏版本、场景、显示与画质设置，分别记录：

1. 关闭帧生成时的平均帧率与低帧表现。
2. 开启超分辨率和帧生成时的显示帧率与画面缺陷。
3. 同一输入操作下的响应延迟。
4. 插电与离电条件下的持续性能、温度与电量变化。
5. 登录、联网、反作弊与必要外设是否可正常使用。

这些是拟采用的测量项，不是已完成的测试。游戏需求可以纳入[任务优先评估](06-evaluation-and-insights.md)，与本地 AI 的内存需求分别判定。

最低记录方法是保留同一场景的逐帧耗时日志，并声明“低帧表现”采用的统计口径；均值可能掩盖短暂卡顿，不能代替帧时间分布。响应延迟指从输入操作到屏幕反馈的时间，若没有相应测量工具只能记主观观察，不填写伪精确毫秒数。这是教学建议，不是本包实测报告。
