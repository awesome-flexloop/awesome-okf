---
type: Reference
title: "信源清单 S-01~S-14"
description: "14 个信源的 URL、性质、日期与可信度分层；含官方文档在 huggingface/hub-docs 仓库中的源文件定位，便于逐字回源。"
tags: [信源清单, 溯源, 可信度分层, 官方文档]
sources:
  - id: bundles-index
    resource: facts.md
    title: "事实台账 F-001~F-052"
---

# 信源清单 S-01~S-14

> 分层口径：**A** = 一手官方文档 / 官方源码；**B** = 一手官方公告（含厂商自测数据）；**C** = 第三方榜单（经公告转引，本束未直接抓取复核）。所有材料均为公开、无需访问控制的内容。抓取与核对日期：2026-11-17。

## 一手官方材料

| 编号 | source id | 层级 | 材料 | URL | 日期 / 说明 |
|---|---|:---:|---|---|---|
| S-01 | `hf-announcement` | B | Hugging Face × OpenRouter 合作公告 | https://huggingface.co/blog/openrouter | Published 2026-11-16；7 位署名作者；页面显示 39 upvote |
| S-02 | `hf-announcement-src` | A | 公告逐字 Markdown 源文件 | https://github.com/huggingface/blog/blob/main/openrouter.md （raw: https://raw.githubusercontent.com/huggingface/blog/main/openrouter.md） | 用于逐字核对标题、段落、代码块与数字；本束已下载核对 |
| S-03 | `hf-ip-index` | A | Inference Providers 官方文档首页 | https://huggingface.co/docs/inference-providers （源: `huggingface/hub-docs/main/docs/inference-providers/index.md`） | 三种客户端示例、`hf models ls --warm`、策略后缀说明 |
| S-04 | `hf-ip-routing` | A | Routing and Providers | https://huggingface.co/docs/inference-providers/routing （源: `.../routing.md`） | 默认路由三信号、后缀表、供应商开关、Failover |
| S-05 | `hf-ip-pricing` | A | Pricing and Billing | https://huggingface.co/docs/inference-providers/pricing （源: `.../pricing.md`） | 月度 credits 表、`X-HF-Bill-To`、`hf-inference` 历史口径、usage API |
| S-06 | `hf-ip-caching` | A | Prompt Caching | https://huggingface.co/docs/inference-providers/prompt-caching （源: `.../prompt-caching.md`） | `X-HF-Session-Id`、`cached_tokens`、两条缓存 Tips |
| S-07 | `hf-ip-messages` | A | Messages API 官方指南 | https://huggingface.co/docs/inference-providers/guides/messages-api | `/v1/messages` curl、Anthropic SDK `base_url`、Claude Agent SDK 示例 |
| S-08 | `hf-ip-responses` | A | Responses API 官方指南 | https://huggingface.co/docs/inference-providers/guides/responses-api | `/v1/responses` curl 与 SDK 示例 |
| S-09 | `hf-ip-claude-code` | A | Claude Code 接入指南 | https://huggingface.co/docs/inference-providers/integrations/claude-code （源: `.../integrations/claude-code.md`） | 9 个环境变量、`hf-claude` 扩展、模型槽位、`--bill-to` |
| S-10 | `hf-ip-opencode` | A | OpenCode 接入指南 | https://huggingface.co/docs/inference-providers/integrations/opencode （源: `.../integrations/opencode.md`） | 原生支持、`opencode auth login`、`/models`、config 计费头 |
| S-11 | `or-routing-rebuild` | B | How we rebuilt provider routing for better, faster inference | https://openrouter.ai/blog/announcements/how-we-rebuilt-provider-routing/ | Scott Morse，2026-10-28；含 switchback 实验与完整结果表 |
| S-12 | `or-open-vs-closed` | B | Open-Weight vs Closed-Weight Models: What's the Difference? | https://openrouter.ai/blog/insights/open-weight-vs-closed-weight-models/ | OpenRouter，2026-10-31；含份额表、价格表、benchmark 分数与统计口径说明 |
| S-13 | `or-provider-selection` | A | Provider Routing 官方文档 | https://openrouter.ai/docs/guides/routing/provider-selection | `provider` 对象字段、default routing、`:floor` / `:nitro`、区域路由 |
| S-14 | `aa-index` | C | Artificial Analysis Intelligence Index | https://artificialanalysis.ai/leaderboards/models | 公告 F-026 引用的第三方榜单；**本束未直接抓取该榜单复核**，分数按转引登记 |

## 抓取方式与局限

- S-02~S-10 通过 `huggingface/hub-docs` 仓库 raw 文件取得文档源（`.md` / `.mdx`），再与官网渲染页交叉核对；S-01 另有 `huggingface/blog` 仓库 raw 源文件。
- S-11~S-13 为官网页面内容；其中 S-13 原始页面较长，本束只登记与路由机制直接相关的章节，未覆盖全文。
- S-14 只经 S-01 / S-12 转引，未独立核验，故列 C 层；F-026 与 F-046 的分数差异按各自转引口径并列（见 C-02）。

## 未纳入的材料

- 公告内嵌的交互式 setup Space（`huggingface-inference-providers-setup.static.hf.space`）：为 iframe 应用，本束未抓取其运行时内容，只登记公告中列出的五份指南名称（F-019）。
- Codex / Pi / Hermes Agent 三份集成指南：官方源已可达但本束未展开，示例页只做指引，不写具体配置。
- 公告中的四组配图（份额图、智能指数对比图、路由 GIF、页签/用量/设置截图）：图片承载的数据已由正文文字与 S-11 / S-12 覆盖，本束未逐张读图，故**不对图中未见于文字的数值作任何登记**。

## 时点与复核

S-01 发布于 2026-11-16，本束成文于 2026-11-17，两者相差一天。平台文档处于高频修订期；`status: draft` 与 `stale_after: 2027-02-17` 用于提示到期回源。若后续官方把 S-04 / S-11 的策略后缀或计费口径改写，须同时复核 F-014/F-015/F-033/F-038 与 C-03/C-04。
