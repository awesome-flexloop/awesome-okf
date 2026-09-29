---
type: Concept
title: "流水线、技能与渲染协作"
description: "拆解 OpenMontage 的七阶段生产骨架、任务流水线和 Remotion/HyperFrames/FFmpeg 协作关系"
tags: [OpenMontage, Pipeline, Remotion, HyperFrames, FFmpeg]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-12-31
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: repo, resource: "https://github.com/calesthio/OpenMontage" }
---

# 流水线、技能与渲染协作

官方 README 给出的共同骨架是：

```text
research -> proposal -> script -> scene_plan -> assets -> edit -> compose
```

每种任务只是在这条骨架上选择不同的素材、声音、剪辑和渲染策略。[F-006、F-009](../references/article-source.md)

## 阶段契约

1. `research` 建立主题事实和素材候选。
2. `proposal` 让人类先确认方向、工具路径和预算。
3. `script` 固化旁白、叙事节奏和声音要求。
4. `scene_plan` 将脚本变成镜头、素材和转场计划。
5. `assets` 获取或生成图像、视频、音乐和字幕素材。
6. `edit` 组织时间线、音画和字幕。
7. `compose` 使用 Remotion、HyperFrames 或其他后端完成合成，再由 FFmpeg 编码和检查。[F-010](../references/article-source.md)

## 任务路径选择

Animated Explainer 适合知识解释，Documentary Montage 适合开放档案和真实素材，Clip Factory 适合长视频切片，Screen Demo 适合产品演示，Localization & Dub 适合字幕、翻译和配音。[F-009](../references/article-source.md)

不要把这些名称当作永远不变的 API。项目主分支持续演进，复现时必须固定 commit 并重新读取 manifest。[核验报告](../references/verification.md)

## 相关概念

- [从提示词到视频生产系统](00-system-positioning.md)
- [成本、质量与许可证](02-governance-and-evaluation.md)
