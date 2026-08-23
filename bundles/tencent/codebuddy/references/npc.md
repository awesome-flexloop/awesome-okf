---
type: Reference
title: "CodeBuddy NPC 官网信源"
description: "CodeBuddy NPC 产品官网（codebuddy.cn/npc）的事实登记，记录云端 AI 员工的目标驱动、自主上下文、全流程 PR 与多 NPC 协同能力。"
tags: [codebuddy, npc, cloud-agent, reference, official-site, cnb]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: npc-official
    resource: https://www.codebuddy.cn/npc/
    title: CodeBuddy NPC 产品官网
---

# CodeBuddy NPC 官网信源

本文件登记 CodeBuddy NPC 产品官网（https://www.codebuddy.cn/npc/）的公开事实，对应事实编号 F-039 ~ F-051。

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | npc-official |
| URL | https://www.codebuddy.cn/npc/ |
| 类型 | 产品官网 |
| 抓取日期 | 2026-08-23 |
| 对应事实 | F-039 ~ F-051 |
| 平台入口 | https://cnb.cool/npc/CodeBuddy |

## 产品定位

NPC 定位为研发流程中的 AI 员工（Cloud Agent），基于 CodeBuddy 打造，与 CNB 平台（cnb.cool）深度融合（F-039, F-040）。其核心理念为"给 NPC 定下目标，下班前验收 Ta 的产出"（F-041）。

## 目标驱动范式

NPC 采用目标驱动模式，用户定义 What（做什么）而非 How（怎么做）（F-042）。NPC 自主获取上下文，来源包括（F-043）：

- CNB 仓库
- ISSUE
- 流水线

## 全流程交付

NPC 覆盖从需求到 PR 的完整流程（F-045）：

```
规划 → 编码 → PR → 构建 → 预览环境 → 验收合入
```

## 并行与协同

| 能力 | 说明 | 事实 ID |
|------|------|---------|
| 并行指派 | 多个 NPC 云端并行工作 | F-044 |
| 多 NPC 协同 | NPC Team 按职能分工 | F-046 |

## 自主修复能力

- **构建报错自主修复**：读取日志、查找代码、提交修复，直至门禁通过（F-047）。
- **合并冲突自动解决**（F-048）。

## 可定制性

NPC 支持三方面定制（F-049）：

- 职能（Role）
- SOP（标准作业流程）
- Skill（技能）

## 入口与定价

- 入口：https://cnb.cool/npc/CodeBuddy（F-050）
- 定价：按量收取 Agent 执行 Token 消耗（F-051）

## 事实索引

| 事实 ID | 内容摘要 |
|---------|----------|
| F-039 | 研发流程中的 AI 员工（Cloud Agent），基于 CodeBuddy |
| F-040 | 与 CNB 平台（cnb.cool）深度融合 |
| F-041 | 理念"给 NPC 定下目标，下班前验收 Ta 的产出" |
| F-042 | 目标驱动：定义 What 而非 How |
| F-043 | 自主获取上下文：CNB 仓库/ISSUE/流水线 |
| F-044 | 并行指派：多 NPC 云端并行 |
| F-045 | 全流程：规划→编码→PR→构建→预览环境→验收合入 |
| F-046 | 多 NPC 协同：NPC Team 按职能分工 |
| F-047 | 自主修复构建报错直至门禁通过 |
| F-048 | 自动解决合并冲突 |
| F-049 | 可定制：职能/SOP/Skill |
| F-050 | 入口 https://cnb.cool/npc/CodeBuddy |
| F-051 | 按量收取 Agent 执行 Token 消耗 |

## 相关概念

- [NPC 云端 AI 员工](/concepts/03-npc.md) — NPC 架构与工作模式详解
- [产品矩阵总览](/concepts/00-product-matrix.md) — NPC 在 CodeBuddy 矩阵中的定位
- [CodeBuddy IDE](/concepts/01-ide.md) — NPC 基于 CodeBuddy 核心能力打造
- [CLI](/concepts/02-cli.md) — 本地 Sub-agents 与云端 NPC 的对比
