---
type: Concept
title: "公告与切换边界：换的是路由层，不是 API 层"
description: "逐条还原 2026-11-16 官方公告主张，给出切换前后行为对照表，标出唯一需要改代码的破坏性变更（BYOK）与不经 OpenRouter 的任务范围。"
tags: [公告解读, 迁移, BYOK, 破坏性变更, Inference Providers]
sources:
  - id: hf-announcement
    resource: https://huggingface.co/blog/openrouter
    title: "Hugging Face × OpenRouter 官方合作公告（2026-11-16）"
  - id: hf-ip-routing
    resource: https://huggingface.co/docs/inference-providers/routing
    title: "Routing and Providers 官方文档"
  - id: hf-ip-index
    resource: https://huggingface.co/docs/inference-providers
    title: "Inference Providers 官方文档首页"
---

# 公告与切换边界：换的是路由层，不是 API 层

## 公告说了什么

2026-11-16，Hugging Face 发布《Hugging Face and OpenRouter join forces to make open-weight models easy to run》，署名 7 位作者（celinah、victor、kramp、Wauplin、pierric、coyotte508、julien-c）。公告主张可拆成三句（F-001~F-003、F-006）：

1. Hugging Face Hub 上每个被供应商服务的开放权重模型，都能用 Hugging Face token、经同一个 API 调用；
2. 当天起，Inference Providers **从自研路由切换到 OpenRouter 路由**，语言模型请求按实时价格 / 速度 / 可靠性选供应商，失败在同一次调用内换一家重试；
3. 公告原话是 "Your code stays the same."

公告把它定位为合作「第一步」，后续两项是「把 OpenRouter 账户连到 Hugging Face」与「更多任务经 OpenRouter 路由」。因此本束的所有结论都有一个隐含前提：**这是进行中的迁移，不是终态**。

## 切换前后对照

| 维度 | 切换前（HF 自研路由） | 切换后（OpenRouter 路由） | 依据 |
|---|---|---|---|
| 供应商选择 | 为请求选定一个供应商 | 按实时测量在多家之间挑选 | F-003、F-015 |
| 首次失败 | 返回该供应商的错误 | 同一次调用内在另一供应商重试 | F-003 |
| 策略后缀 | 公告未提及 | `:fastest` / `:cheapest` / `:<provider>` | F-014 |
| pinned 供应商 | — | `:novita` 这类后缀永不被替换 | F-017 |
| 请求地址 / token / SDK | 不变 | 不变 | F-002、F-007、F-008 |
| 自带供应商 API key | 语言模型可用 | **语言模型不可用**；图像 / 视频仍可用 | F-005 |
| 图像 / 视频 / 音频生成 | 走 HF Inference Providers | 完全不变，不经 OpenRouter | F-004 |

## 唯一真正要改的地方：BYOK

公告「Breaking change: custom provider keys」一节写明：语言模型请求现在经 OpenRouter 并记到你的 HF 账户或组织账单上，**因此不能再对语言模型使用自己的供应商 API key**（F-005）。补偿手段有两个：仍可用 `model:provider` 后缀指定供应商，或在设置里关掉不想用的供应商；代码本身不变。

这条容易被"Your code stays the same"盖过去——对绝大多数调用确实不用改，但下面三类用法必须复核：

- 曾把 `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` 之类**供应商密钥**透传给 HF 路由的封装；
- 依赖「某供应商自己的账单 / 自己的配额」做成本核算的脚本（现在改记 HF 账单）；
- 企业侧靠 BYOK 走自有合同价与数据驻留条款的场景（公告未给等价替代，只给供应商开关与 pin）。

图像与视频供应商的自定义 key 继续可用（F-005），所以迁移清单要**按任务类型分叉**，不能一刀切。

## 哪些任务不经过 OpenRouter

图像、视频、音频生成继续直接走 Hugging Face Inference Providers，同一 token、同一 API，并可访问数以万计的 LoRAs（F-004）。这条边界决定了：

- 把「统一路由」理解成「所有推理都换供应商」是错的；
- 只有**聊天 / 语言模型**请求才适用本束讲的 Routing Cost、后缀策略与跨供应商重试；
- 混合应用（既生成文本又生成图）里，两段请求的可观测性与计费口径会分叉。

## 规模语境（厂商口径）

公告给的 OpenRouter 体量是每月 >800 万亿 token、>1000 万用户、600+ 模型、80+ 供应商（F-022）。同一段还引用 open-weight 份额从 2025-10 的 26.8% 升到 2026-09 末的 71.7%、7 月峰值 77.5%（F-023）。这些数字是公告用来解释「为什么值得换路由」的语境材料，**其分母与 OpenRouter 自家文章并不完全一致**，详见 [冲突口径 C-01](../references/conflicts-and-adversarial-review.md)，不要直接当全平台占比引用。

## 本束的解读边界

「换的是路由层」是本束对官方材料的结构化归纳，不是公告原话。判断依据是：三协议端点、基址、token、模型 id 形态在官方文档中保持一致（F-007/F-008/F-014），而选择逻辑、失败行为、计费归属发生了改变（F-003/F-005/F-015）。如果你在迁移中观察到接口层也有变化，应以官方文档为准并回源修订本页。
