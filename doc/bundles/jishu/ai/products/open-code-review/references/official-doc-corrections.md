---
type: "Wiki Tutorial"
title: "官方文档勘误表（E-01 ~ E-11）"
description: "既有 open-code-review 知识包（2026-09-02 由二手文章迁入）与 Open Code Review 官方文档站 2026-10-21 快照的口径对照与勘误——11 条冲突逐条定位到具体文件行号并给出官方修正值，另含 3 条核对通过项与引用口径边界。"
tags: ["open-code-review", "errata", "official-docs", "ai-code-review"]
sources:
  - id: ocr-docs-cli-reference
    resource: "https://open-codereview.ai/docs/cli-reference/"
    title: "官方文档 · CLI 参考"
  - id: ocr-docs-configuration
    resource: "https://open-codereview.ai/docs/configuration/"
    title: "官方文档 · 配置"
  - id: ocr-docs-architecture
    resource: "https://open-codereview.ai/docs/architecture/"
    title: "官方文档 · 架构"
  - id: ocr-docs-review-rules
    resource: "https://open-codereview.ai/docs/review-rules/"
    title: "官方文档 · 评审规则"
  - id: ocr-docs-home
    resource: "https://open-codereview.ai/"
    title: "Open Code Review 官方文档站首页"
generated: { by: process:seven-concepts, at: 2026-10-21 }
verified: { by: process:seven-concepts-v, at: 2026-10-21 }
---

# 官方文档勘误表（E-01 ~ E-11）

> **背景**：本 bundle 现有 12 篇概念页 + 5 篇参考页于 2026-09-02 从二手渠道迁入，来源为微信文章与 SpecWeave 学习库迁移稿。2026-10-21 按官方文档站 open-codereview.ai 全部 15 个页面重新采集事实后，逐条比对既有数值与官方口径，得到 11 条冲突与 3 条核对通过项。
>
> **处理原则**：本表只记录差异与官方修正值，**不直接改写**既有页面正文——既有页面承载的是二手渠道的叙述脉络，逐段重写会破坏可读性与溯源链。以本表为该 bundle 的口径裁决层：引用既有页面时若涉及本表条目，以本表的「官方口径」列为准。逐条事实出处见[官方文档事实清单](official-doc-facts.md)。

## 一、冲突项

| 编号 | 既有位置 | 既有口径 | 官方口径（2026-10-21） | 判定 | 官方事实编号 |
|------|---------|---------|----------------------|------|-------------|
| **E-01** | `references/cli-reference.md:604`、`references/cli-reference.md:613`、`concepts/02-llm-providers.md:4,15,396,398,413,472,650,902,918`、`references/llm-providers-detail.md:15,102,104,178,273` | 内置 provider **19 个** | 内置 provider **25 个**（含 `chatgpt` 预览版）；官方表逐项列出 25 行 | 硬错误（数量过时） | F-048、F-049 |
| **E-02** | `references/cli-reference.md:611` | provider 清单中含 `azure-openai` | 官方 25 个内置 provider 清单中**无** `azure-openai`；Azure OpenAI 需按自定义 provider 配置 | 硬错误（虚构内置项） | F-049 |
| **E-03** | `concepts/02-llm-providers.md:4,15`、`references/llm-providers-detail.md:15,102` | LLM 集成层实现**三种协议** | 官方 provider 表的 `protocol` 字段取值为 **4 种**：`anthropic`、`anthropic-bedrock`、`openai`、`openai-responses` | 硬错误（漏计 bedrock 协议） | F-048、F-050 |
| **E-04** | `references/cli-reference.md:777`、`references/cli-reference.md:820` | 某文件 diff 超过 `MAX_TOKENS` 的 80%（**默认 58888**）即被丢弃 | `ocr review` 的 `max_tokens` **默认 200000**；**58888 是 `ocr scan` 的取值** | 硬错误（把 scan 的阈值当作 review 默认值） | F-064、F-073、F-018 |
| **E-05** | `references/cli-reference.md:773` | `--max-tools` 默认「模板默认 **30**」；1–9 上调到 10；≥10 覆盖模板默认 | 模板默认 **100**；1–49 先上调到 50；解析后的值只在**大于**模板默认值时生效（只能上调） | 硬错误（默认值与上调区间均错） | F-064、F-065 |
| **E-06** | `references/cli-reference.md:772` | `--timeout` 默认 **10** 分钟 | `--timeout` 默认 **15** 分钟（每子任务时间预算，按 effort 线性缩放为 15 / 30 / 45）；单次请求超时独立设置，默认 300 秒 | 硬错误（默认值错，缺 effort 缩放语义） | F-064、F-066 |
| **E-07** | `concepts/02-llm-providers.md:554`、`references/llm-providers-detail.md:161` | 环境变量 `OCR_LLM_MAX_TOKENS` 语义为「最大**输出** Token」 | `max_tokens` 只约束**提示词**；模型输出上限由 `MAX_COMPLETION_TOKENS`（默认 16384）单独控制；`--max-tokens-budget` 与之相互独立 | 硬错误（提示词 / 输出上限语义颠倒） | F-055 |
| **E-08** | `references/cli-reference.md:816` | 「变更行数低于 `PLAN_MODE_LINE_THRESHOLD`（50）时 plan 阶段自动跳过」 | plan 触发为**双条件**：组内单文件变更行数 ≥ 50，**或** 组内文件数 ≥ 2 且合计变更行数 ≥ 100 | 表述不完整（漏掉分组合计阈值） | F-025 |
| **E-09** | — | — | 官方文档站 `/docs/` 与 `/docs/delegate/` 页尾的「集成」链接指向 `../integrations/agent-skill/` 与 `../integrations/delegate/`，两路径在站点上均返回「页面找不到了」；实际可用路径为 `/docs/agent-skill/` 与 `/docs/delegate/` | 官方站点链接断裂（不影响工具本身） | — |
| **E-10** | — | — | 首页统计区（内部活跃用户、真实任务数、npm 下载量、token 成本占比、AACR-BENCH SEM.F1）由动效计数器渲染，抓取时呈 `0K+` / `0M+` / `0K+` / `0/9` / `0.10%` / `0/9` 占位形态 | 引用风险（这些数值不可作为口径引用） | F-100 |
| **E-11** | `index.md:4,9`、`concepts/01-architecture.md:4,15,93,97,904` | 官方流水线为「**六阶段**」 | 官方架构文档未使用「六阶段」这一划分；其口径为：diff provider → 噪声目录剔除 → 五重门过滤 → 语义分组 → per-group plan → main 循环 → 评论处理五步 → 渲染，另加三道 token 守卫 | 术语口径差异（非事实错误） | F-008 ~ F-036 |

## 二、核对通过项

| 编号 | 核对对象 | 官方口径 | 结论 |
|------|---------|---------|------|
| **OK-01** | `concepts/08-effectiveness.md:66,68`、`concepts/09-limitations.md:23,36,38,39,119,131,133,136` | AACR-BENCH：OCR 最优 F1 **25.10%**、Precision 33.90%、Recall 20.00%；Claude Code 最优 F1 **14.13%**、最高 Recall **28.90%**；Codex v0.140.0 的 GPT-5.5 F1 **8.36%** | 数值与官方首页排行榜逐格一致，既有表述「OCR 精度领先、召回低于 Claude Code」成立 |
| **OK-02** | `concepts/08-effectiveness.md:145,149,153`、`concepts/09-limitations.md:119` | AACR-BENCH 构成：50 个热门开源仓库、200 个真实 PR、10 种编程语言、80+ 资深工程师交叉标注 | 一致 |
| **OK-03** | `references/resources.md:36,42` | AACR-Bench 论文（arXiv 2601.19494）与 GitHub 仓库（alibaba/aacr-bench）为公开资源 | 资源链接可继续引用（本次未复核 arXiv 页面内容） |

## 三、引用口径边界

1. **既有页面不等于官方口径**：本 bundle 12 篇概念页与 5 篇参考页为二手渠道迁入稿，其叙述结构、内部符号名（如 `internal/llm/providers.go`）与部分数值未经官方文档逐项核对。凡涉及数值、参数默认值、provider 清单、阈值常量的引用，须回到本表与[事实清单](official-doc-facts.md)。
2. **官方文档亦非源码**：F-008 ~ F-036 引用的文件名、函数名、常量取自官方架构文档的源码地图章节，本次未拉取仓库源码逐行验证。
3. **首页统计区不可引用**：E-10 涉及的动效计数器数值在无 JS 渲染或无完整渲染时呈占位形态，不具备可复现性。
4. **未覆盖范围**：本次采集覆盖文档站 15 个可达页面（含 `/docs/chatgpt-preview/`）；贡献指南类页面在站点导航中未发现独立入口，未纳入采集范围。
