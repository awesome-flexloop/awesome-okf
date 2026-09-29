---
type: Log
title: 生成日志
description: "mobilepa-bench 束生成日志——source-code-to-okf-wiki R→I→E 链路、两份 facts 适配与 WEB-A 改编号说明、无 examples 决策依据、11 文件清单与自检记录"
tags: [日志, 方法论, source-code-to-okf-wiki, 网站资产]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
---

# 生成日志

## 方法论链路

按 `source-code-to-okf-wiki` 工作流 R→I→E 执行（本束为 I 阶段知识地图指定的束 3，E 阶段落位）：

| 阶段 | 内容 | 产出 | 状态 |
|------|------|------|------|
| R | 事实采集：`facts-mobilepa-bench.md`（F-001~F-032）+ `facts-websites.md` A 部分（F-001~F-024） | 两份事实清单 | ✅（既有） |
| I | 洞察提炼与三束知识地图（本束为"束 3：mobilepa-bench，5 篇 concepts，无 examples + 5 篇 references"） | `insights.md` mobilepa-bench 章节 | ✅（既有） |
| E | 信源先行成文：references/ 先于 concepts/ 生成，各级 index 最后写 | 本束 11 文件 | ✅ |

## 信源

| 编号 | 来源 | 说明 |
|------|------|------|
| S1 | `external/libs/tools/Tongyi-MAI/MobilePA-Bench` | README/LICENSE/github-pages 静态站（index.html、js 数据文件、vendor）/.github CI；arXiv:2608.23035；私有评测入口 116.62.42.171 |
| S2 | `external/libs/tools/Tongyi-MAI/Qwen-UI-Agent` | README/package.json/next.config.ts/app 关键文件/db/CI workflow；网站 https://tongyi-mai.github.io/Qwen-UI-Agent/ |

关键性质结论（已写入 [references/source-registry.md](references/source-registry.md) 与根 index）：**两仓均为网站/论文资产，非实现代码仓**。MobilePA-Bench 仓库根不存在任何基准任务数据、评测 harness 或实现代码（F-001）；Qwen-UI-Agent 仓 README 原文 "Website source only — this is not the Qwen-UI-Agent implementation repository."（WEB-A-01），实现指向 Tongyi-MAI/MAI-UI（WEB-A-02）。

## 事实适配与改编号说明

- **A 部分**（MobilePA-Bench）：F-001 ~ F-032 编号原样沿用 `facts-mobilepa-bench.md`，数字与引文逐条保留。
- **B 部分**（Qwen-UI-Agent 网站仓）：facts-websites.md 的 A 部分 F-001 ~ F-024 改用 **WEB-A-01 ~ WEB-A-24** 前缀编号，避免与本束 A 部分 F 编号冲突；每条在 `references/facts.md` 中标注原编号。
- facts-websites.md B 部分（MAI-UI-blog，原 F-025~F-040）属 mai-ui 束登记范围，本束不引用；其中两篇 Notion 博客为重定向 stub，正文一律不引用。

## 无 examples/ 决策依据

本束**不设 examples/**，依据为事实清单而非省事：

1. 仓库不存在可运行的评测代码与数据（F-001：仓库根仅 README/LICENSE/.gitignore/github-pages/ 与 .github/，"不存在任何基准任务数据、评测 harness、模型或智能体实现代码目录"）；
2. 站点案例与 replay 数据是**展示型 JS 数组**（F-020/F-023），不是可复现的操作序列；
3. 唯一的"运行"形态是提交 endpoint 的私有评测（F-008/F-009：HTTPS、OpenAI-compatible、tool-calling endpoint，3 个工作日返回、每账户每 7 天 1 次），已作为 00 篇 §5 的实操说明呈现。

## 文件清单（11 个）

| # | 文件 | 类型 | 事实编号 |
|---|------|------|---------|
| 1 | index.md | 根索引 | F-001~F-023、WEB-A 系列（总览） |
| 2 | log.md | 本文件 | — |
| 3 | concepts/index.md | 概念目录索引 | — |
| 4 | concepts/00-benchmark-overview.md | 基准概览 | F-001~F-010、F-028~F-031 |
| 5 | concepts/01-capability-dimensions.md | 四能力维度与任务分布 | F-003~F-005、F-016~F-020、F-022、F-032 |
| 6 | concepts/02-verification-policy.md | 固定验证策略与六类 checker | F-003、F-007、F-021~F-023、F-032 |
| 7 | concepts/03-leaderboard-analysis.md | 榜单解读 | F-011~F-014、F-018、F-021 |
| 8 | concepts/04-qwenuiagent-website.md | Qwen-UI-Agent 网站技术栈简析 | WEB-A-01~WEB-A-24 |
| 9 | references/index.md | 信源目录索引 | — |
| 10 | references/facts.md | 事实台账（A+B 两部分） | F-001~F-032 + WEB-A-01~WEB-A-24 |
| 11 | references/source-registry.md | 信源登记 | 全部事实的文件级映射 |

## 自检记录（E 阶段质量门）

### ① toctree 与实际文件一致

- [x] 根 index toctree：concepts/index、references/index、log —— 三者均存在
- [x] concepts/index toctree：00-benchmark-overview、01-capability-dimensions、02-verification-policy、03-leaderboard-analysis、04-qwenuiagent-website —— 五篇均存在
- [x] references/index toctree：facts、source-registry —— 两篇均存在
- [x] 本束无 examples/，各级 toctree 均未引用 examples

### ② 无 `../` 束内链接

- [x] 束内正文链接均为相对路径：根 index 用 `concepts/…`、`references/…`、`log.md`；concepts 互链用同目录 `00-…md` ~ `04-…md`
- [x] `../` 仅出现在跨束互链场景（`../mai-ui/index.md`、`../mobile-world/index.md`、`../qwen-ui-agent/index.md`）；references → concepts/log 的两处束内引用已改为纯文本路径，不含超链接
- [x] 无 `file:///` 链接；官方外链仅限 facts 已登记项（arxiv.org/abs/2608.23035、116.62.42.171、video-mme.github.io、tongyi-mai.github.io/Qwen-UI-Agent/、github.com/Tongyi-MAI/MobilePA-Bench、github.com/Tongyi-MAI/Qwen-UI-Agent、github.com/Tongyi-MAI/MAI-UI）
- [x] 未虚构未登记的 URL（如未登记的项目页公网地址，已在 source-registry 显式说明以仓库内文件为准）

### ③ frontmatter 齐全

- [x] 根 index：okf_version "0.2"、type: bundle、title/description/tags/generated/verified/status/stale_after/sources 齐全
- [x] 5 篇 concepts：type: Concept + 任务给定模板字段（含 sources 指向 /references/facts.md 与 /references/source-registry.md）齐全
- [x] references/facts.md、source-registry.md：type: Reference 齐全
- [x] concepts/index.md、references/index.md：无 frontmatter、含 toctree（符合规范）
- [x] log.md：type: Log（沿用模板束惯例）

### ④ 数字一致性抽查

- [x] 1,705/212/13/89（F-004）在 00/01/根 index 一致
- [x] 权重公式 0.5/0.2/0.2/0.1（F-011）与 50%/20%/20%/10%（F-013）在 03 篇逐字呈现
- [x] 任务分布 1,040/376/200/89（F-018）在 01 篇与 03 篇引用一致
- [x] 13 模型 overall 分数与机构（F-012）逐条核对；未转录台账未登记的四维明细
- [x] N=15/T=15（F-017）、3 个工作日/每 7 天 1 次（F-009）、portal IP（F-008/F-010）均与台账一致
- [x] WEB-A 数字：next 16.2.6/react 19.2.6/node >=22.13.0（WEB-A-04/05）、82.1/92.2 等（WEB-A-15）、409 任务/104 App（WEB-A-16）均与台账一致

## 备注

- 本束为 Tongyi-MAI 三束（mai-ui / mobile-world / mobilepa-bench）中知识地图指定的束 3；跨束互链的 mai-ui 与 mobile-world 束由并行的 E 阶段任务落位，链接按知识地图蓝图预先写入（`../<bundle>/index.md`）。
- 与既有 qwen-ui-agent 束的关系为单向链接（本束 → 既有束），不回写只读引用的既有 bundle。
- 04 篇引用的 MobileWorld 82.1%/92.2% 等分数已在 04 篇内显式标注"与 MobilePA-Bench 榜单分属不同基准，不可混用"，落实数据口径纪律。
- stale_after 设为 2026-12-31：榜单 v1.5 快照与网站 "Coming soon" 状态均可能随版本更新改变。
