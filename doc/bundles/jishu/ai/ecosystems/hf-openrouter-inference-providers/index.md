---
okf_version: "0.2"
type: bundle
title: "Hugging Face Inference Providers × OpenRouter 统一路由教程"
description: "2026-11-16 Hugging Face 将 Inference Providers 语言模型路由整体切换到 OpenRouter——同一 HF token 与同一 API 不变，变化在路由层。本束以官方公告为入口，用 Inference Providers 与 OpenRouter 官方文档补齐三种 API 协议、鉴权、路由策略、会话缓存、计费与可观测性，形成可上手教程，并逐条登记两家官方口径的冲突。"
tags: [Hugging Face, OpenRouter, Inference Providers, LLM 网关, 统一路由, OpenAI 兼容, Anthropic Messages, 提示词缓存, BYOK, 计费, 教程]
status: draft
stale_after: 2027-02-17
generated: { by: "reference_agent/workbuddy", at: 2026-11-17 }
verified:
  - { by: "process:seven-concepts-v", at: 2026-11-17 }
sources:
  - id: hf-announcement
    resource: https://huggingface.co/blog/openrouter
    title: "Hugging Face and OpenRouter join forces to make open-weight models easy to run（Hugging Face 官方公告，2026-11-16）"
    author: "team:huggingface（celinah / victor / kramp / Wauplin / pierric / coyotte508 / julien-c）"
    last_modified: 2026-11-16
  - id: hf-announcement-src
    resource: https://github.com/huggingface/blog/blob/main/openrouter.md
    title: "公告逐字源文件 openrouter.md（huggingface/blog）"
  - id: hf-ip-index
    resource: https://huggingface.co/docs/inference-providers
    title: "Inference Providers 官方文档首页（快速开始与多语言示例）"
  - id: hf-ip-routing
    resource: https://huggingface.co/docs/inference-providers/routing
    title: "Routing and Providers 官方文档"
  - id: hf-ip-pricing
    resource: https://huggingface.co/docs/inference-providers/pricing
    title: "Pricing and Billing 官方文档"
  - id: hf-ip-caching
    resource: https://huggingface.co/docs/inference-providers/prompt-caching
    title: "Prompt Caching 官方文档"
  - id: hf-ip-messages
    resource: https://huggingface.co/docs/inference-providers/guides/messages-api
    title: "Messages API 官方指南"
  - id: hf-ip-responses
    resource: https://huggingface.co/docs/inference-providers/guides/responses-api
    title: "Responses API 官方指南"
  - id: hf-ip-claude-code
    resource: https://huggingface.co/docs/inference-providers/integrations/claude-code
    title: "Claude Code 接入官方指南"
  - id: hf-ip-opencode
    resource: https://huggingface.co/docs/inference-providers/integrations/opencode
    title: "OpenCode 接入官方指南"
  - id: or-routing-rebuild
    resource: https://openrouter.ai/blog/announcements/how-we-rebuilt-provider-routing/
    title: "How we rebuilt provider routing for better, faster inference（Scott Morse，2026-10-28）"
  - id: or-open-vs-closed
    resource: https://openrouter.ai/blog/insights/open-weight-vs-closed-weight-models/
    title: "Open-Weight vs Closed-Weight Models: What's the Difference?（OpenRouter，2026-10-31）"
  - id: or-provider-selection
    resource: https://openrouter.ai/docs/guides/routing/provider-selection
    title: "Provider Routing 官方文档（provider 对象字段与排序变体）"
  - id: aa-index
    resource: https://artificialanalysis.ai/leaderboards/models
    title: "Artificial Analysis Intelligence Index（公告引用的第三方能力榜单）"
---

# Hugging Face Inference Providers × OpenRouter 统一路由教程

> **本束性质**：以 Hugging Face 2026-11-16 官方合作公告为入口，用 Hugging Face Inference Providers 官方文档与 OpenRouter 官方文档补齐「怎么用」的操作教程，**不是公告的中文译本，也不是任何一方的官方中文文档**。
>
> **事实截点**：2026-11-17。公告发布于 2026-11-16，属于平台规则高频变动期；`status: draft`，`stale_after: 2027-02-17`，到期前须回官方文档复核。

## 一句话结论

这次变更替换的是**路由层，不是 API 层**：请求仍打 `https://router.huggingface.co/v1`、仍用同一个 Hugging Face token、仍写同一个模型 id，但语言模型请求背后由 OpenRouter 依据实时测量挑选供应商，并在首次失败时于同一次调用内换一家重试。真正需要你改代码的地方只有一个——**语言模型不再接受自带供应商 API key（BYOK）**。

## 适用与不适用

| | 说明 |
|---|---|
| **适用于** | 想用一个 token 调多家供应商的开放权重模型；要把现有 OpenAI / Anthropic SDK 或编码 Agent 指到 HF 路由；要理解默认路由背后的取舍并显式选策略；要迁移旧的 Inference Providers 用法 |
| **不适用于** | 图像 / 视频 / 音频生成（不经 OpenRouter，走原有 HF Inference Providers 链路）；自建网关选型评测；模型能力排行榜的独立复核（本束只登记厂商与第三方口径，不做独立测量） |
| **前置条件** | 一个带 `inference.serverless.write`（"Make calls to Inference Providers"）权限的 fine-grained HF token；有计费额度（PRO / Team / Enterprise 赠送，或按量购买 credits）；Python 或 Node 基础 |

## 内容导航

- [公告与切换边界](concepts/00-announcement-and-switch.md)——切换前后对照、破坏性变更 BYOK、哪些任务不经过 OpenRouter
- [三种 API 协议与鉴权](concepts/01-three-protocols-and-auth.md)——Chat Completions / Responses / Messages 的基址、端点、token 权限与组织计费头
- [路由机制与策略后缀](concepts/02-routing-mechanism.md)——默认路由的六项实时信号、`:fastest` / `:cheapest` / `:provider`、故障转移与缓存感知；与 OpenRouter 原生 `provider` 对象对照
- [定价、可观测性与边界](concepts/03-pricing-observability-and-boundaries.md)——无加价计费、月度 credits、Providers / Metrics 两个页签、用量拆分、供应商开关
- [三协议最小可运行示例](examples/01-quickstart-three-protocols.md)——curl / Python / JavaScript 各一份，含响应里怎么看缓存命中
- [编码 Agent 接入](examples/02-coding-agent-setup.md)——Claude Code 与 OpenCode 两套配置，含 `hf-claude` 扩展与 `--bill-to`
- [策略选择与缓存粘滞演练](examples/03-routing-policy-and-cache.md)——`X-HF-Session-Id`、策略对照实验、迁移自查清单
- [事实台账 F-001~F-052](references/facts.md) / [信源清单](references/source-manifest.md) / [冲突口径与对抗审查](references/conflicts-and-adversarial-review.md)

## 已知边界（消费前必读）

1. **未实跑**：本束所有代码示例均逐字取自官方文档，**未经本库用真实 `HF_TOKEN` 运行验证**；模型 id、端点路径、环境变量名以官方文档为准，运行前请回源核对。
2. **口径不合并**：HF 公告与 OpenRouter 自家文章在「最常用模型」「最佳模型分数」「份额分母」上给出不同数字。本束按「多源分账」原则并列登记（见 `references/conflicts-and-adversarial-review.md`），**不合并、不抹平、不裁决谁对**。
3. **厂商自述**：路由收益（-46% capacity errors、+16.9% TTFT、+16.3% throughput）来自 OpenRouter 自己的 switchback 实验；同一实验还测到每千请求成本 +6.0%，公告未提。所有成效数字按厂商口径对待。
4. **命名空间不通用**：HF 侧写 `zai-org/GLM-5.3`、后缀 `:fastest`；OpenRouter 侧写 `z-ai/glm-5.3-flash`、变体 `:floor` / `:nitro`。两套 id 与两套后缀**不可交叉套用**。
5. **时效**：公告自述为合作「第一步」，后续还有账户打通与更多任务接入；页签、供应商开关、额度均可能变更。

## 主题关联

- [💳 DeepSeek-V4 免费方案与 API 定价](../deepseek-pricing/index.md)——同属 `ecosystems` 的官方定价口径束，对照「厂商直连」与「统一路由」两条路径；
- [🚀 国产 Token 出海：低价算力如何碾压全球市场](../../practice/domestic-model-token-export/index.md)——OpenRouter 平台数据的行业解读（该束为博文核验，口径与本束不同，注意区分）；
- [💥 Token 经济大爆发](../../practice/token-economy-explosion/index.md)——Token 调用量的宏观语境；
- [📊 免费大模型 API 汇总](../../learning/free-llm-api-roundup/index.md)——多平台免费额度盘点，含 OpenRouter 通道（时效截点更早）。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
```
