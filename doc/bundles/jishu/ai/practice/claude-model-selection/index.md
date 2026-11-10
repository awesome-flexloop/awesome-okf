---
okf_version: "0.2"
type: bundle
title: "Claude 模型选型：Fable、Opus、Sonnet 与 Haiku"
description: "基于 claude.dev 官方博文与 Anthropic 模型页核验 Claude 四档模型的定位、价格、effort 调档、混合编排与迁移兼容；含两篇可复现实践。"
tags: [claude, anthropic, model-selection, pricing, effort, subagents, cost]
generated: { by: "lobsterai/main", at: "2026-11-10T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T13:30:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: blog
    resource: https://claude.dev/blog/which-claude-model-should-you-build-with/
  - id: fable-page
    resource: https://www.anthropic.com/claude/fable
  - id: opus-page
    resource: https://www.anthropic.com/claude/opus
  - id: sonnet-page
    resource: https://www.anthropic.com/claude/sonnet
  - id: haiku-page
    resource: https://www.anthropic.com/claude/haiku
  - id: fable-launch
    resource: https://www.anthropic.com/claude-fable-and-mythos-5-2
  - id: cc-model-config
    resource: https://code.claude.com/docs/en/model-config
---

# Claude 模型选型：Fable、Opus、Sonnet 与 Haiku

> **内容性质**：技术选型与方法论教程，含 2 篇可复现实践。核心价格、模型定位、别名解析与 Claude Code 默认 effort 已回到官方模型页与文档核验；benchmark、内部实验与 API 侧细节按“厂商自述 / 博文单源”分层标注。

## 核心结论

多数工作从 **Opus 5.5 的 `medium`** 开始（F-005）。范围明确的日常任务下移 Sonnet 5.5，高频机械劳动下移 Haiku 5.5，最难或最长的任务上移 Fable 5.2（F-007—F-010）。换模型之前先调 effort，因为超过 `high` 后，再升一档的成本可能已经等于换更大的模型（F-011）。

四档模型的 API 列表价是：Haiku `$0.10/$0.50`（≤100K）或 `$0.50/$2.50`（>100K），Sonnet `$2/$10`，Opus `$4/$20`，Fable `$8/$40`（F-026—F-029）。但选型不能只看单价：更难的任务由更大的模型用更少轮数完成时，每任务成本可能反而更低（F-036、F-037）。

## 选型速查

| 场景 | 起始模型 | 起始 effort |
|---|---|---|
| 日常工程、调试、多 PR 功能 | Opus 5.5 | `medium` |
| 范围明确的编码、修 bug | Sonnet 5.5 | `medium` |
| 分类、路由、抽取、日志与搜索子代理 | Haiku 5.5 | `medium` |
| 聊天与交互式会话 | Sonnet 5.5 | `low` 或 `medium` |
| 日常文档、幻灯片、表格 | Sonnet 5.5 | `high`（Claude Code 为 `medium`） |
| 大型重构、迁移、架构规划 | Fable 5.2 | `medium` → `high` |
| 不确定 | Opus 5.5 | `medium` |

完整矩阵与判据见 [按任务选型](concepts/01-task-to-model.md)。

## 阅读路径

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```

1. [四模型阵容与价格](concepts/00-lineup-and-pricing.md)：先把价格、缓存价、上下文与默认 effort 对齐。
2. [按任务选型与 effort 调档](concepts/01-task-to-model.md)：拿到默认答案与上下移动规则。
3. [每完成任务成本](concepts/02-task-economics.md)：理解为什么单价不等于任务成本。
4. [混合模型编排](concepts/03-mixing-models.md)：切换断点、thinking 兼容、子代理、advisor、批量委派。
5. [迁移兼容清单](concepts/04-migration-compatibility.md)：换模型名之前必须测的七类差异。
6. [自测闭环](concepts/05-measurement-loop.md)：把厂商基准换成自己的证据。
7. [用 Haiku 子代理读日志](examples/00-haiku-log-reader-subagent.md)：最小可复现的混合编排。
8. [双模型成本对比实验](examples/01-two-model-cost-comparison.md)：一次完整的自测流程。
9. [信源与核验](references/index.md)：事实编号、勘误与单源边界。

## 已知边界

- 价格与版本为 2026-11-10 快照；模型调价、effort 档位与别名解析都可能变化，`stale_after` 设为 2026-12-31。
- **Sonnet 5.5 缓存读取价存在口径冲突**：博文写 `$0.10`，官方 Sonnet 页只写“最多 90% 缓存节省”，按输入价推算为 `$0.20`。正文同列两者，以实时价目表为准（见 E-1）。
- **API 默认 effort 与 Claude Code 默认 effort 不是同一口径**：Claude Code 侧四模型均为 `medium` 已由官方文档确认；API 侧 Sonnet/Fable 为 `high` 仅有博文单源（见 E-2）。
- platform.claude.com 在核验环境返回区域限制页，preserved thinking、advisor、computer use 工具集等 API 细节为博文单源。
- Terminal-Bench、SWE-bench Pro、43% 开销集中度、90.1%/$2.92 等数字为厂商自述或同站文章转述，未独立复算（见 E-4）。

## 主题关联

- [GPT-6 Sol/Luna 成本效率与 Agent 任务经济性](../gpt6-sol-luna-cost-efficiency/index.md)：同为“模型分工 + 每任务成本”选型束，可对照 OpenAI 侧的价格分层与 DeepSeek 价格口径。
- [Fable5 成本优化](../fable5-cost-optimization/index.md)：Fable 5 世代的定价背景、社区方案与官方优化，是本文 Fable 5.2 价格的前情。
- [上下文优化](../context-optimization/index.md)：上下文压缩与 token 成本，与本文“精简主上下文、便宜子代理做冗长阅读”互补。
- [AI 工程方法论](../ai-engineering-methodology/index.md)：Harness 工程、评测体系与对抗审查，可承接本文的自测闭环。
