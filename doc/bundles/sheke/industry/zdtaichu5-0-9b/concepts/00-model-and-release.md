---
okf_version: "0.2"
type: Concept
title: "ZDTaichu5.0-9B 的模型定位与发布事实"
description: "从官方资料和微信公众号文章中拆解 ZDTaichu5.0-9B 的输入模态、架构组成和目标任务。"
tags: [ZDTaichu5.0-9B, 多模态, 空间推理, 具身智能]
generated: { by: "process:seven-concepts-e", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: flagged
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: official-blog
    url: https://taichu-ai.github.io/ZDTaichu5.0-9B/
  - id: github
    url: https://github.com/Taichu-AI/ZDTaichu5.0-9B
---

# 模型定位与发布事实

ZDTaichu5.0-9B 是紫东太初发布的 9B 级多模态基础模型，目标覆盖通用视觉理解、空间推理、工具调用和具身智能研究（F-002、F-003、F-019）。它接收文本、单张或多张图像以及视频，官方页面还强调任意分辨率视觉输入（F-004、F-019）。

模型由 Qwen3.5-9B 语言骨干和 C-RADIOv4-H 视觉编码器组合而成（F-009、F-020）。官方 Hugging Face 页面将其标注为 image-text-to-text、spatial-reasoning、agent 和 video-understanding 等类型（F-022）。

这组定位意味着它处在通用视觉语言模型与机器人感知/规划系统之间：模型负责理解视觉环境、空间关系和任务指令；真正的运动控制、安全策略和设备执行仍需外围系统提供（F-016）。

> **可信度边界**：文章中的基准排名、具体分数和“超过闭源模型”描述，均应按发布方报告值阅读，不能替代独立评测（F-005～F-008、F-023～F-024）。
