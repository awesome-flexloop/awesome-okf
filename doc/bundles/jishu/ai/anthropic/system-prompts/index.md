---
okf_version: "0.2"
type: index
title: "Claude 系统提示词发布史"
description: "Anthropic 官方公开的 claude.ai 与移动端核心系统提示词发布史中文 Wiki——18 个模型、30 个日期条目（2024-07 → 2026-09）全覆盖，含公开机制、全景矩阵、四时代逐条目解析与设计思想演进分析。"
tags: [anthropic, claude, system-prompts, release-notes, prompt-engineering, llm]
sources:
  - name: claude-system-prompts-docs
    path: "https://platform.claude.com/docs/en/release-notes/system-prompts/overview"
generated:
  by: "process:seven-concepts R→I→E→V（知识沉淀）"
  at: "2026-09-02"
status: stable
stale_after: 2027-09-02
---

# Claude 系统提示词发布史

Anthropic 自 2024 年 7 月起在官方文档持续公开 claude.ai 网页端与 iOS/Android 移动端使用的**核心系统提示词全文**，并随模型与产品演进定期更新——这是业界少见的透明性实践，也是研究"产品级系统提示词设计"的第一手权威材料。官方明确声明这些提示词**不适用于 Claude API**：API 用户使用自带的 `system` 参数，产品级提示词与开发者提示词完全分离。

本束基于官方发布页（en 版 `.md` 原文端点）于 2026-09-02 的全量快照整理，覆盖 **18 个模型、30 个日期条目**（Opus 3 → Fable 5.1，2024-07-12 → 2026-09-01），所有版本对比均以逐行 diff 实测为准，关键条款保留英文原文逐字摘录并配中文解读。

## 为什么要研究产品级系统提示词

| 视角 | 收获 |
|------|------|
| **提示词工程** | 观察 Anthropic 如何用"模板 + 身份插槽"管理多模型提示词、如何随模型升级做约束减法 |
| **产品演进** | product_information 层是一部 Claude 产品编年史（Claude Code 转正 → 全家桶 → Mythos/Glasswing） |
| **安全合规** | 儿童安全、武器 uplift 累积评估、版权豁免线、政治公正等政策面的章节化索引 |
| **上下文工程** | "上下文工程做减法"（随模型变强删除防御性禁令）趋势在产品级提示词中的实证 |

## 束结构导航

| 分区 | 深度 | 内容 | 适合人群 |
|------|------|------|---------|
| [**concepts**](concepts/index.md) | 🟡结构化整理 | 7 篇：公开机制与政策边界、全景矩阵（18 模型 × 30 条目）、四时代逐条目解析（3.x / 4.0-4.1 / 4.5 / 固定快照）、设计思想演进分析 | 提示词工程师、AI 产品研究者 |
| [**references**](references/index.md) | 🟢信源参考 | 2 篇：信源索引（18 个官方子页 + 采集方法）、条目事实登记表（61 条 F 编号索引） | 复核引文、溯源 |

## 学习路径建议

### 🚀 快速了解路径
1. 读 [00-overview](concepts/00-overview.md) 掌握公开机制与边界（5 分钟）
2. 浏览 [01-lineage-matrix](concepts/01-lineage-matrix.md) 全景矩阵定位感兴趣的模型
3. 跳读对应时代篇的"时代小结"

### 🔬 深度研究路径
1. 按 [01-lineage-matrix](concepts/01-lineage-matrix.md) 矩阵选定研究对象
2. 精读对应时代篇（[02](concepts/02-era-3x.md) / [03](concepts/03-era-4x-launch.md) / [04](concepts/04-era-45.md) / [05](concepts/05-era-fixed-snapshot.md)）的逐条目解析
3. 用 [06-evolution](concepts/06-evolution.md) 建立纵向视角，参考其"实践启示"迁移到自己的提示词工程
4. 引文复核走 [references/entry-registry](references/entry-registry.md) 的 F 编号索引

## 关键发现速览

| 发现 | 一句话 | 详见 |
|------|--------|------|
| **模板 + 身份插槽** | Sonnet 4 与 Opus 4 同日条目仅差 4 处身份插槽，其余逐字相同 | [06-evolution §3](concepts/06-evolution.md) |
| **人格化转折** | Sonnet 3.7（2025-02）首次宣告 "more than a mere tool" | [02-era-3x §6](concepts/02-era-3x.md) |
| **固定快照机制** | 4.6 代起每模型 ID 为单一固定快照，提示词不再演进 | [00-overview §4](concepts/00-overview.md) |
| **约束减法** | 2025-07-31 是禁令清单峰值，此后逐代拆除防御性禁令 | [06-evolution §7](concepts/06-evolution.md) |
| **活文档属性** | 官方页加粗标注执行不严、旧条目就地更新，引用须自行 diff | [06-evolution §8](concepts/06-evolution.md) |

## 文档统计

| 分区 | 概念文档 | 参考文档 | 总文件 |
|------|---------|---------|-------|
| concepts | 7 | 0 | 8 |
| references | 0 | 2 | 3 |
| 根文档（index + log） | — | — | 2 |
| **合计** | **7** | **2** | **13** |

## 版本说明

本文档基于官方发布页 en 版于 2026-09-02 的快照生成（18 个模型子页 `.md` 端点全量采集）。官方页面为"活文档"（旧条目可能就地更新、新模型持续上线——最新为 2026-09-01 的 Claude Fable 5.1），引用时请注意注日期；信源清单与采集方法见 [references/source-index](references/source-index.md)。

```{toctree}
:hidden:

concepts/index
references/index
log
```
