---
type: Concept
title: "从提示词到视频生产系统"
description: "理解 OpenMontage 如何把 AI 编程助手、流水线、工具注册表和质量检查组合成视频生产系统"
tags: [OpenMontage, Agent, 视频生产]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-12-31
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: repo, resource: "https://github.com/calesthio/OpenMontage" }
---

# 从提示词到视频生产系统

OpenMontage 的重点不是再提供一个“输入提示词、输出短片”的模型，而是把视频工作拆成可读、可暂停、可复核的生产阶段。[F-002、F-006](../references/article-source.md)

## 四个角色

| 角色 | 负责什么 |
| --- | --- |
| AI 编程助手 | 读取规则、选择流水线、调用工具并推进状态 |
| Pipeline Manifest | 声明阶段顺序、输入输出和生产约束 |
| Director Skill | 说明某个阶段如何执行以及什么算完成 |
| 人类制片人 | 提供目标，确认创意分叉，检查最终交付 |

这形成了“Agent 导演、仓库片场、工具团队、人工审批”的控制面。它的可审计性来自普通的 Markdown、YAML、JSON 和媒体文件，而不是不可见的编排服务。

## 为什么不是“一次生成”

视频成片通常需要研究、脚本、节奏、素材、声音、字幕、合成和渲染检查。把这些步骤写入仓库，可以让一次失败定位在具体阶段，也可以从状态文件继续，而不是从头重复整次生成。

## 证据边界

官方仓库支持上述结构；微信文章的热度、节省时间和案例效果不构成独立基准。[F-011、F-015](../references/article-source.md)

## 相关概念

- [流水线与导演技能](01-pipeline-and-director-skills.md)
- [成本、质量与许可证](02-governance-and-evaluation.md)
