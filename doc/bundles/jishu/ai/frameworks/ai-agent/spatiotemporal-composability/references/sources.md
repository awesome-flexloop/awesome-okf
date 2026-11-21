---
type: Reference
title: "信源登记与版本声明"
description: "本包全部信源 URL、获取方式、信源距离与时效边界"
tags: [spatiotemporal-composability, sources, provenance, arxiv]
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
---

# 信源登记与版本声明

## 1. 权威信源（全部 F 编号的依据）

| ID | 信源 | URL | 用途 |
|---|---|---|---|
| `arxiv-abs` | arXiv 元数据页 | <https://arxiv.org/abs/2608.25512> | 作者、提交时间、页数、分类、DOI、版本历史 |
| `arxiv-pdf` | 论文 v1 全文（92 页） | <https://arxiv.org/pdf/2608.25512v1> | 全部定义、定理、算法、案例与讨论 |
| `cordis-paper-repo` | 论文配套仓库 | <https://github.com/cordiverse/paper> | 由本库 `cordis/` 包登记，本包未直接抓取 |
| `cordis-repo` | Cordis 框架仓库 | <https://github.com/cordiverse/cordis> | 由本库 `cordis/` 包登记，本包未直接抓取 |

## 2. 核验用二手信源（不作事实依据）

| ID | 信源 | URL | 用途 |
|---|---|---|---|
| `besthub-review` | BestHub《DeepSeek Harness Open-Source》 | <https://www.besthub.dev/articles/deepseek-harness-open-source-a-fully-pluggable-ai-agent-framework-backed-by-a-formal-paper-e0d24896ddce> | 提供待核验转述，检出 E-01 / E-02 / E-03 |
| `pith-record` | Pith 论文摘要记录 | <https://pith.science/paper/2608.25512> | 摘要逐句分类交叉确认；该页明确声明未读全文 |
| `hn-mirror` | 预印本说明转载页 | <https://yavchn.parkscomputing.com/story/hn/49285342> | 确认「活跃修订中预印本」的表述与 BibTeX 作者列表 |

## 3. 内部参照（查重与互链，不作事实依据）

| 目标 | 相对路径 | 分工 |
|---|---|---|
| 背景理论章节 | [cordis/references/background-paper.md](../../cordis/references/background-paper.md) | 既有包的**概念引子**（早期草稿口径），本包不复制 |
| 效应与协同效应源码机制 | [cordis/concepts/effects-coeffects.md](../../cordis/concepts/effects-coeffects.md) | 既有包的**源码级**讲解 |
| Cordis 源码信源 | [cordis/references/cordis-sources.md](../../cordis/references/cordis-sources.md) | 既有包的 API / 文件行号索引 |
| Cordis 框架教程入口 | [cordis/index.md](../../cordis/index.md) | 框架总览与示例 |
| DeepSeek Harness 教程 | [deepseek-harness/index.md](../../deepseek-harness/index.md) | 该范式的 Agent 框架落地 |

> 相对路径层级：本文件位于 `spatiotemporal-composability/references/`。上跳 1 层到本 bundle 根，上跳 2 层到分组根 `ai-agent/`，故指向**同组兄弟 bundle** 用 `../../<bundle>/...`；若写 3 层会落到 `frameworks/` 而断链。该层级经逐条路径解析脚本验证。

## 4. 版本与时效

- 本包依据 **arXiv:2608.25512v1**（2026-08-26）。论文为活跃修订中的预印本，后续版本可能改动证明细节与实现描述。
- 既有 `cordis/` 包记录的是更早的草稿口径（2026-08-13、约 88 页），差异已登记为 E-04，不视为错误，也不改写既有包。
- 全包 `stale_after: 2027-02-28`。到期复核动作：检查 arXiv 是否发布 v2+、比对 §3/§4 定义与定理编号是否变化、更新 F 编号受影响条目。
- 本包**不含**可运行示例与部署实测。`examples/` 的取舍依据见根 index 的「骨架说明」。
