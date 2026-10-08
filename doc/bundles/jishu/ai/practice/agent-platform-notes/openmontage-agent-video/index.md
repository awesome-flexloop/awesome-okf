---
okf_version: "0.2"
type: bundle
title: "OpenMontage Agent 视频制作系统"
description: "从微信公众号文章与官方仓库学习 OpenMontage 的流水线契约、Agent 导演模式、渲染工具链、最小安装路径与成本合规边界"
tags: [OpenMontage, Agent, 视频制作, Remotion, HyperFrames, FFmpeg]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-12-31
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/Icq2rjqPi7gfVb-x7cCz8Q" }
  - { id: repo, resource: "https://github.com/calesthio/OpenMontage" }
  - { id: guide, resource: "https://raw.githubusercontent.com/calesthio/OpenMontage/main/AGENT_GUIDE.md" }
  - { id: license, resource: "https://raw.githubusercontent.com/calesthio/OpenMontage/main/LICENSE" }
---

# OpenMontage Agent 视频制作系统

> **证据警示：flagged。** 文章中的 Star/Fork、节省时间和规模数字是时点或单源主张；本包解释官方仓库结构，不代表本次已运行视频生成或证实成片效果。

OpenMontage 把 AI 编程助手放在视频生产控制面，通过流水线 manifest、阶段技能、Python 工具和人工审批，将研究、脚本、素材、剪辑与渲染组织成可复核的生产流程。[F-002、F-006、F-007](references/article-source.md)

## 阅读路径

1. [从提示词到视频生产系统](concepts/00-system-positioning.md)
2. [流水线、技能与渲染协作](concepts/01-pipeline-and-director-skills.md)
3. [成本、质量与许可证治理](concepts/02-governance-and-evaluation.md)
4. [最小安装与创作请求](examples/minimal-production-path.md)
5. [事实登记](references/article-source.md)与[核验报告](references/verification.md)

## 已知边界

- 本包未固定 OpenMontage 的 release tag；复现应固定具体 commit。
- 文章的规模、节省时间和案例效果没有独立评测。
- “零 API Key”路径仍需检查本地算力、素材授权、模型条款和 AGPL 合规。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
