---
okf_version: "0.2"
type: Reference
title: "原文事实清单：ZDTaichu5.0-9B"
description: "登记微信公众号文章中的模型发布事实、能力声明、训练方案、作者判断及其来源层级。"
tags: [ZDTaichu5.0-9B, 紫东太初, 具身智能, 多模态模型]
generated: { by: "reference_agent/blog-article-to-okf-wiki", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: flagged
stale_after: "2026-12-31"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/YOW4mB8Dg6loiKDfzF_NHQ?from=industrynews&color_scheme=light#rd
  - id: official-blog
    url: https://taichu-ai.github.io/ZDTaichu5.0-9B/
---

# 原文事实清单

> 提取方式：浏览器读取微信公众号页面 `#js_content`。F-001～F-018 来自原文；F-019～F-024 为官方来源核验或 V 阶段裁决。

| 编号 | 原文事实或表述 | 分类 |
|---|---|---|
| F-001 | 标题为《只有 9B，一个令人惊艳的国产模型，开源了！》，作者“小 G”，公众号 GitHubDaily，发布日期为 2026-09-22。 | 文章元信息 |
| F-002 | 紫东太初团队开源 ZDTaichu5.0-9B。 | 发布事实 |
| F-003 | 模型面向物理世界，强调空间具身能力。 | 能力定位 |
| F-004 | 模型参数量为 9B，支持单图、多图、长视频和任意分辨率图像。 | 能力声明 |
| F-005 | 文章称模型在 ViewSpatial、MMSI-Bench、MindCube-tiny 等基准上表现突出。 | 厂商/文章转述 |
| F-006 | 文章称九项国际空间理解基准中有八项位于同参数开源模型组第一。 | 厂商/文章转述 |
| F-007 | 文章列出 MindCube-tiny 78.27、ViewSpatial 62.50、CV-Bench 86.82 等分数。 | 厂商/文章转述 |
| F-008 | 文章列出 AI2D、WeMath、OCRBench、IFEval、LiveCodeBench v6、TAU2-Bench 的通用能力分数。 | 厂商/文章转述 |
| F-009 | 模型使用 Qwen3.5-9B 语言骨干和 C-RADIOv4-H 视觉编码器。 | 架构事实 |
| F-010 | 训练包括预训练、监督微调、高质量退火和 GRPO 强化学习，数据总量约 1.28T tokens。 | 训练事实 |
| F-011 | 奖励信号可自动校验答案、空间坐标和输出格式。 | 训练事实 |
| F-012 | 数据生产管线方案随项目公开。 | 开放性声明 |
| F-013 | 自适应循环推理会在低把握 token 上增加内部计算轮次。 | 机制声明 |
| F-014 | 仓库包含 `recurrent_reasoning/` 目录。 | 仓库事实 |
| F-015 | 文章介绍机器人收纳剪刀、科研自动化和智能制造场景。 | 演示转述 |
| F-016 | 模型负责高层规划，底层运动控制和设备安全逻辑仍由硬件控制系统承担。 | 边界事实 |
| F-017 | 作者认为小型空间具身模型可能在部署成本和响应速度上更有优势。 | 作者观点 |
| F-018 | 文章附有 GitHub、技术 Blog、Hugging Face 和 ModelScope 地址。 | 文章元信息 |
| F-019 | 官方 Blog 确认 9B 多模态基础模型定位及文本、图像、视频输入。 | 官方核验 |
| F-020 | 官方 Blog 确认 Qwen3.5-9B 与 C-RADIOv4-H 组合。 | 官方核验 |
| F-021 | 官方 GitHub 确认 `recurrent_reasoning/` 目录存在。 | 官方核验 |
| F-022 | 官方 Hugging Face 页面列出 spatial-reasoning、agent、video-understanding 等标签。 | 官方核验 |
| F-023 | 官方页面提供基准结果与定性演示，但结果仍属于发布方报告。 | 核验边界 |
| F-024 | 未找到独立复现实验，基准排名和真实场景效果不能升级为独立验证结论。 | V 阶段裁决 |
