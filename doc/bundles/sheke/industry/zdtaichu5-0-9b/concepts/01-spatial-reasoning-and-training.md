---
okf_version: "0.2"
type: Concept
title: "空间推理能力与训练管线"
description: "解释文章所述空间具身能力、数据生产和自适应循环推理，并区分官方报告与作者解读。"
tags: [空间推理, 训练管线, GRPO, recurrent reasoning]
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

# 空间推理能力与训练管线

文章把空间具身能力描述为三类能力的组合：识别物体与空间关系、在多视角之间转换参照系，以及据此判断下一步操作（F-003、F-005、F-015）。这比“图中有什么”的静态识别多了一层状态更新和行动规划。

源文称训练经过预训练、监督微调、高质量退火和 GRPO 强化学习，总数据量约 1.28T tokens；强化学习阶段把答案、空间坐标和输出格式转成可自动校验的奖励信号（F-010、F-011）。这些描述应理解为发布方训练方案说明，而不是独立审计过的训练报告。

文章还介绍自适应循环推理：模型对每个 token 估计把握度，遇到视角转换或物体关系判断等难题时，在内部增加计算轮次（F-013）。官方 GitHub 确认仓库包含 `recurrent_reasoning/` 目录（F-014、F-021），但目录存在本身不能证明该机制在所有任务上都带来稳定收益。

从方法论角度看，这条路线把更多计算预算分配给高不确定性片段，而不是让所有 token 使用同一推理深度。可迁移的评估问题是：额外计算是否提高空间判断正确率、延迟增加多少、以及是否会改变工具调用的稳定性。
