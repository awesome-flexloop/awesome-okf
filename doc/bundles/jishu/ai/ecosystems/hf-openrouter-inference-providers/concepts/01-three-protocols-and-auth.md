---
type: Concept
title: "三种 API 协议与鉴权：同一个 token，三种入口"
description: "梳理 Chat Completions / Responses / Messages 三种协议在 HF 路由上的基址、端点与 SDK 配置，以及 fine-grained token 权限与组织计费头。"
tags: [OpenAI 兼容, Responses API, Anthropic Messages, 鉴权, HF_TOKEN, 组织计费]
sources:
  - id: hf-announcement
    resource: https://huggingface.co/blog/openrouter
    title: "Hugging Face × OpenRouter 官方合作公告（2026-11-16）"
  - id: hf-ip-index
    resource: https://huggingface.co/docs/inference-providers
    title: "Inference Providers 官方文档首页"
  - id: hf-ip-messages
    resource: https://huggingface.co/docs/inference-providers/guides/messages-api
    title: "Messages API 官方指南"
  - id: hf-ip-responses
    resource: https://huggingface.co/docs/inference-providers/guides/responses-api
    title: "Responses API 官方指南"
  - id: hf-ip-pricing
    resource: https://huggingface.co/docs/inference-providers/pricing
    title: "Pricing and Billing 官方文档"
---

# 三种 API 协议与鉴权：同一个 token，三种入口

公告写明路由对**每个聊天模型**都支持 OpenAI 的 Chat Completions 与 Responses API、以及 Anthropic 的 Messages API，「无论背后的供应商是谁」（F-007）。这句话的实际含义是：协议转换发生在 HF 路由内部，客户端只需会说三种协议之一。

## 三种协议对照

| 协议 | HTTP 端点 | OpenAI / Anthropic SDK 的 base URL | 认证方式 |
|---|---|---|---|
| OpenAI Chat Completions | `https://router.huggingface.co/v1/chat/completions` | `https://router.huggingface.co/v1` | `Authorization: Bearer $HF_TOKEN` 或 `api_key=$HF_TOKEN` |
| OpenAI Responses | `https://router.huggingface.co/v1/responses` | `https://router.huggingface.co/v1` | 同上 |
| Anthropic Messages | `https://router.huggingface.co/v1/messages` | `https://router.huggingface.co`（**不带 `/v1`**） | `Authorization: Bearer $HF_TOKEN`；Anthropic SDK 用 `auth_token`；Claude Code 用 `ANTHROPIC_AUTH_TOKEN` |

依据：F-008（OpenAI 兼容基址）、F-009（三个端点）、F-020（Claude Code 的 `ANTHROPIC_BASE_URL` 不带 `/v1`）。

注意 Anthropic 一侧最易踩的坑：**基址不带 `/v1`**，因为 SDK / Claude Code 会自行拼出 `/v1/messages`。若照 OpenAI 习惯写成 `https://router.huggingface.co/v1`，路径会变成 `/v1/v1/messages`。这也解释了为什么 Claude Code 集成指南里写的是裸域名。

## Token 与权限

官方 Messages API 与集成指南给出一致的前置条件（F-010）：

- 一个 **fine-grained** Hugging Face token，带 "Make calls to Inference Providers" 权限（创建链接里对应 `inference.serverless.write` scope）；
- 存到环境变量 `HF_TOKEN`；
- 账户要有 compute credits（PRO / Team / Enterprise 赠送，或按量购买），Free 用户须先购买 credits 或升级（F-028）。

一个 token 同时打通四类服务：Inference Providers（serverless 推理）、Storage Buckets、Jobs（算力）、Inference Endpoints（专属推理）（F-002 语段）。这是「统一入口」的另一层意思——不只是统一供应商，也统一了 HF 站内的计费身份。

## 组织计费头

Team / Enterprise 可以集中计费：每个成员仍用自己的 User Access Token，请求通过 `X-HF-Bill-To: <org-name>` 记到组织账单（F-011）。三个细节值得记住：

- 官方明确要求「显式指定被计费的组织」，否则拿不到组织的赠送额度；
- `huggingface_hub` 的 `InferenceClient(bill_to="my-org-name")`、OpenAI SDK 的 `extra_headers={"X-HF-Bill-To": ...}`、直接 HTTP 的 header 三种写法等价；
- **请求一旦记到组织，供应商启用/禁用设置改用组织的，而不是个人的**；显式请求一个被组织禁用的供应商会报错（F-016、F-029）。

Claude Code 场景还有两条捷径：`hf claude --bill-to your-org-name` / `HF_BILL_TO` 环境变量，或 `ANTHROPIC_CUSTOM_HEADERS="X-HF-Bill-To: your-org-name"`（F-020）。

## 找可用模型

`hf models ls --warm` 列出「至少被一家供应商服务」的模型，加 `--json` 便于脚本与 Agent 消费（F-018）。这一步建议放在写业务代码之前：路由只能把请求送到**确实有人在服务**的模型，模型 id 写错或供应商全部下线时会直接失败，而不是悄悄降级。

## 命名空间的硬边界

HF 路由用 Hub 风格的模型 id，例如 `deepseek-ai/DeepSeek-V4.1-Flash`、`zai-org/GLM-5.3`（F-014）。OpenRouter 自家 API 用另一套，例如 `deepseek/deepseek-v4.1-flash`、`z-ai/glm-5.3-flash`（F-045）。两者不通用；把它们拼在一起是接入期最常见的一类错误，详见 [C-04](../references/conflicts-and-adversarial-review.md)。
