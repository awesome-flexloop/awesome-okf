---
type: Example
title: "三协议最小可运行示例"
description: "Chat Completions / Responses / Messages 三种协议的 curl 与 SDK 最小请求，逐字取自官方文档，并说明响应里读缓存命中与计费归属的位置。"
tags: [快速开始, curl, OpenAI SDK, Anthropic SDK, Responses API, 提示词缓存]
sources:
  - id: hf-ip-index
    resource: https://huggingface.co/docs/inference-providers
    title: "Inference Providers 官方文档首页（Python / JS / curl 示例）"
  - id: hf-ip-responses
    resource: https://huggingface.co/docs/inference-providers/guides/responses-api
    title: "Responses API 官方指南"
  - id: hf-ip-messages
    resource: https://huggingface.co/docs/inference-providers/guides/messages-api
    title: "Messages API 官方指南"
  - id: hf-ip-caching
    resource: https://huggingface.co/docs/inference-providers/prompt-caching
    title: "Prompt Caching 官方文档"
  - id: hf-ip-pricing
    resource: https://huggingface.co/docs/inference-providers/pricing
    title: "Pricing and Billing 官方文档"
---

# 三协议最小可运行示例

> **运行前**：以下代码块均逐字或近似逐字取自官方文档，**本库未用真实 `HF_TOKEN` 实跑**。需要 fine-grained token（`inference.serverless.write` 权限）与可用 credits（F-010、F-028）。模型 id 请先按 `hf models ls --warm` 核对（F-018）。

## ① 准备

```bash
export HF_TOKEN="hf_..."   # fine-grained，含 "Make calls to Inference Providers" 权限
```

## ② Chat Completions（最通用）

官方首页的 `requests` 版（F-008、F-009）：

```python
import os
import requests

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
payload = {
    "messages": [{"role": "user", "content": "How many 'G's in 'huggingface'?"}],
    "model": "deepseek-ai/DeepSeek-V4.1-Flash:fastest",
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.json()["choices"][0]["message"])
```

等价的 OpenAI SDK 版（官方文档原文）：

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)
completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4.1-Flash:fastest",
    messages=[{"role": "user", "content": "How many 'G's in 'huggingface'?"}],
)
print(completion.choices[0].message)
```

`huggingface_hub` 的 `InferenceClient()` 会自动处理供应商选择与路由，无需手工指定基址（F-008 附）。

## ③ Responses API

官方 Responses 指南的 curl 形态（F-009）：

```bash
curl https://router.huggingface.co/v1/responses \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-ai/DeepSeek-V4.1-Flash", "input": "Say hello in one sentence."}'
```

OpenAI SDK 同样把 `base_url` 指到 `https://router.huggingface.co/v1`，改调 `client.responses.create(...)`（官方指南 F-009 附）。

## ④ Anthropic Messages API

官方 Messages 指南的 curl（F-009）：

```bash
curl https://router.huggingface.co/v1/messages \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-ai/DeepSeek-V4.1-Flash", "max_tokens": 128,
       "messages": [{"role": "user", "content": "Say hello in one sentence."}]}'
```

Python SDK（官方文档）：

```python
import os
from anthropic import Anthropic

client = Anthropic(
    base_url="https://router.huggingface.co",   # 注意：不带 /v1
    auth_token=os.environ["HF_TOKEN"],
)
message = client.messages.create(
    model="deepseek-ai/DeepSeek-V4.1-Flash",
    max_tokens=128,
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)
print(message.content)
```

## ⑤ 多轮会话：加缓存粘滞头

官方文档的 Prompt Caching 示例（F-012）：

```bash
curl https://router.huggingface.co/v1/chat/completions \
    -H "Authorization: Bearer $HF_TOKEN" \
    -H "X-HF-Session-Id: 3f8c2a1e-6b4d-4e2a-9c1f-7d5b0e8a4c21" \
    -H "Content-Type: application/json" \
    -d '{ "model": "deepseek-ai/DeepSeek-V4.1-Flash", "messages": [...] }'
```

`X-HF-Session-Id` 必须是**每会话一个稳定 UUID**，其他值被忽略。命中缓存时响应形如（官方文档原文）：

```json
"usage": {
  "prompt_tokens": 12000,
  "completion_tokens": 300,
  "prompt_tokens_details": { "cached_tokens": 11500 }
}
```

配套写法：把 system prompt 与 tools 放最前、变量放最后；不要在 system prompt 顶部放时间戳或随机 id（F-013）。Python / JS 的 HF 官方客户端会自动处理缓存，无需额外配置。

## ⑥ 记到组织账单

```python
from huggingface_hub import InferenceClient

client = InferenceClient(bill_to="my-org-name")
completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3-0324",
    messages=[{"role": "user", "content": "How many 'G's in 'huggingface'?"}],
)
```

OpenAI SDK 用 `extra_headers={"X-HF-Bill-To": "my-org-name"}`，直接 HTTP 用同名 header（F-011）。

## 验收清单

- [ ] 三种协议各能拿到一次 2xx 响应；
- [ ] 能说出本次请求用的是哪个模型 id、是否带后缀；
- [ ] 能在响应里找到 `usage`（多轮时找 `cached_tokens`）；
- [ ] 能说出这笔费用记在个人还是组织账单（有没有 `X-HF-Bill-To`）；
- [ ] 明确知道：这些代码本库未实跑，异常时先回官方文档核对端点与模型可用性。
