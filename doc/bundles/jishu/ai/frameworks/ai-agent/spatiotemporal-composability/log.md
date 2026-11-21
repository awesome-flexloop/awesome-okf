---
type: Log
title: "生成与复核日志"
description: "本包的生成流程、核验结论、机械门禁结果与到期复核动作"
tags: [spatiotemporal-composability, log, provenance]
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
---

# 生成与复核日志

## 2026-11-21 · 首次生成

**流程**：七概念方法论（`@skill:seven-concepts-cmd`）场景 4「知识沉淀」，链路 `R → I → E → V → A → C`，`depth=deep`。

| 阶段 | 产出 |
|---|---|
| R | arXiv v1 PDF 全文提取（92 页），建立章节地图与形式化定义/定理定位；登记 F-001 – F-072 共 72 条编号事实，双份登记 |
| I | 确定落点 `jishu/ai/frameworks/ai-agent/spatiotemporal-composability/`，与既有 `cordis/` 包做查重与分工判定 |
| E | 新建独立 bundle（不塞进 `cordis/`）；萃取可迁移模式「回程同源」（`maturity: L1`） |
| V | P0 核验 13 项（✅11 / ⚠️1 / ❌0，另 1 项不纳入范围）；四处口径勘误 E-01 – E-04；四视角对抗审查 8 条意见全部采纳 |
| A | 12 篇原子化概念页，每篇 500–5000 字符；形式符号延后至第 04 篇之后 |
| C | 三级 toctree 收录；分组索引与共享计数文件按工作树真值更新；机械门禁复核 |

**落点理由**：既有 `cordis/` 包讲的是框架源码与早期草稿概念引子；本包是论文精读教程，两者互为入口而非重复，故新建独立 bundle 并互链，不改写既有包。

**关键修正**：R/I 阶段检出的两处机械问题已修复——① `sources.md` / `theory-api-mapping.md` 中跨 bundle 相对链接误写 `../../../cordis/...`（会解析到 `frameworks/cordis/`），经逐条路径解析修正为 `../../cordis/...`；② `sources.md` 中「上跳 3 层」的说明同步更正为「上跳 2 层到 `ai-agent/`」。

## 机械门禁结果（已复核）

全包 22 个 `.md`：frontmatter / UTF-8 / LF 行尾全部 PASS；143 条相对链接 0 断链；双份 F 编号 72/72 一致且连续；12 篇概念页 2420–3491 字符；三级 toctree（根 3 / concepts 12 / references 6）零断链；敏感信息 0 处。

仓库门禁：`check-utf8.py`、`check-toctrees.py`、`check-bundles-index.py` 及其 `--self-test` 全部 EXIT=0；`check-asset-baseline.py` 在**干净克隆提交态** EXIT=0（提交前工作区因在途内容报残差 +212699，属预期）；Python 红线 pytest 12 passed。`invoke gates.all` 因本机 `invocations` 元数据缺失无法启动，已改为逐个运行其封装的同一批脚本与自检探针。

提交态自证：子模块提交 `b8bac47f`；干净克隆（`-c core.longpaths=true --local --no-hardlinks`）复跑五门全绿，bundles 对账 752 束五面一致。逐项判据、检出并修复的三处问题见 [P0 核验报告与对抗审查记录](references/verification.md) §5。

## 并发说明

本包生成期间，工作树中另有他方未提交 WIP（`doc/bundles/jishu/ai/products/univer-office-sdk/` 及其索引计数更新）。本任务遵循「他方 WIP 不代改」：共享计数文件的工作区写**目录树真值**，暂存/提交态只带「HEAD + 仅本束增量」，他方改动留在工作区不丢失。

## 到期复核动作（2027-02-28）

1. 检查 arXiv 是否发布 v2+；若发布，比对 §3/§4 定义与定理编号是否变化。
2. 逐条复核受影响的 F 编号条目与 `facts.md` / `paper-source.md` 双份一致性。
3. 复核 `sources.md` 中二手信源时效性；若论文已正式发表，更新信源层级。
4. 复跑双份 F 编号比对、相对链接可达性与三级 toctree 检查。
