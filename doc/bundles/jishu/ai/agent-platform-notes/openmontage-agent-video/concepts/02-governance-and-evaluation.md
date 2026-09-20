---
type: Concept
title: "成本、质量与许可证治理"
description: "建立 OpenMontage 生产任务的成本核算、输出验收、素材授权和 AGPL 合规边界"
tags: [OpenMontage, 评测, 成本, AGPL]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-12-31
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: license, resource: "https://raw.githubusercontent.com/calesthio/OpenMontage/main/LICENSE" }
---

# 成本、质量与许可证治理

“零 API Key”只能描述某条默认路径，不能替代完整预算。[F-013](../references/article-source.md) 一次生产至少要区分本地计算、云模型调用、素材服务、存储和人工审核。

## 交付前检查

| 维度 | 最小检查 |
| --- | --- |
| 事实 | 研究结果是否有来源，脚本是否把猜测写成事实 |
| 素材 | 图片、视频、音乐和字体是否有可用授权 |
| 音画 | 是否存在黑帧、静音、爆音、字幕漂移或错误比例 |
| 成本 | API、重试、渲染、存储和人工时间是否分别记录 |
| 合规 | AGPL 义务、第三方素材条款和模型服务条款是否由负责人确认 |

## 如何避免营销数字污染

文章中的4.3万 Star、50%省时以及工具/技能数量都应写成读取日快照，不应作为永久规模或效果承诺。[F-011、F-015](../references/article-source.md) 真实评估需要固定 commit、输入样本、模型供应商、运行次数、失败样本和完整账单。

## 相关概念

- [流水线、技能与渲染协作](01-pipeline-and-director-skills.md)
- [最小安装与创作请求](../examples/minimal-production-path.md)
