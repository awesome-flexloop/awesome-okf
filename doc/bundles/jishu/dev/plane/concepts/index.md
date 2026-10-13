---
okf_version: "0.2"
type: Concept
title: "Plane 概念地图"
description: "Plane 知识包概念层导航——定位与许可、三套版本、三层工作模型、视图文档统计、部署运维、选型边界"
---

# 概念地图

| # | 篇目 | 层 | 回答的问题 |
|---|------|----|-----------|
| [00](00-overview-and-positioning.md) | 定位、起源与技术栈 | 发布事实层 | Plane 是什么、多大、用什么写的、什么许可证 |
| [01](01-editions-and-licensing.md) | 三套自托管版本与许可边界 | 结构层 | Community / Commercial / Airgapped 怎么选、AGPL 边界在哪 |
| [02](02-work-model-three-scales.md) | Work Items / Cycles / Modules | 结构层 | 单件事、这两周、整条线分别由谁管 |
| [03](03-views-pages-analytics.md) | 视图、文档、统计与需求入口 | 结构层 | 五视图、Pages/Wiki、统计面板、Intake、集成与 AI |
| [04](04-deployment-and-operations.md) | 部署架构与运维要点 | 架构层 | 怎么装、改哪些环境键、内置组件是什么、生产要注意什么 |
| [05](05-selection-and-boundaries.md) | 选型矩阵与适用边界 | 边界层 | 谁该用、谁要付钱、与同类怎么比、什么不能信 |

## 学习路径

- **只想知道值不值得看**：00 → 05
- **要自己部署**：00 → 01 → 04 → [examples/](../examples/index.md)
- **要推行给团队**：00 → 02 → 03 → 05
- **任何数字要引用前**：先读 [references/verification.md](../references/verification.md)

```{toctree}
:hidden:
:maxdepth: 2

00-overview-and-positioning
01-editions-and-licensing
02-work-model-three-scales
03-views-pages-analytics
04-deployment-and-operations
05-selection-and-boundaries
```
