---
okf_version: "0.2"
type: Concept
title: "模型规格与发布状态"
description: "从原文拆解 Ling 3.1 Flash 的参数规模、架构走向与尚未开源的发布状态。"
tags: [Ling3.1Flash, MoE, 蚂蚁集团, 大模型]
generated: { by: "process:seven-concepts:i-e", at: "2026-10-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-10T00:00:00Z" }
status: flagged
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
---

# 模型规格与发布状态

> 本篇为评测快报的整理；所有规格数字当前为**文章单源口径**，见[核验报告](/references/verification.md)。

## 核心规格（F-005、F-006）

| 项目 | 数值 | 来源 |
|---|---|---|
| 架构 | MoE（混合专家） | F-005 |
| 总参数 | 560B | F-005 |
| 激活参数 | 25B | F-005 |
| 上一代（3.0 Flash）参数 | 124B | F-006 |
| 规模倍数 | 约 4.5 倍 | F-006 |

这是“Flash”前缀下远超上一代的体量：激活参数仅 25B，说明大多数专家在线下被稀疏激活，属 MoE 常见设计，用于在推理时控制计算成本。

## 发布状态（F-008）

截至发文，权重未开放，官方声称“很快会放出”。这直接决定了文章的可复现性：在权重开放前，任何人都无法独立重跑测试。

> **阅读动作**：把这些数字标记为“文章转述”，待官方参数页发布后再回填核实，不要把 560B/25B 当作已确认的最终官方指标。