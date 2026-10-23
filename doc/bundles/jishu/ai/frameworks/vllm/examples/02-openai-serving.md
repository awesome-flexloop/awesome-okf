---
type: Example
title: "示例 02：OpenAI 兼容在线服务（vllm serve）"
description: "用 vllm serve 一键起 OpenAI 兼容服务——启动参数、官方 OpenAI SDK 客户端调用、API key 鉴权、chat 模板与多轮对话，含 Anthropic /v1/messages 兼容验证
tags: [vllm, example, vllm-serve, openai-compatible, api-key, chat-template, client]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-openai
    resource: /references/source-map.md
    title: vllm/entrypoints/openai/ 与 docs/serving/openai_compatible_server.md（本地检出）
---

# 示例 02：OpenAI 兼容在线服务（vllm serve）

`vllm serve <model>` 一条命令起完整的 OpenAI 兼容 API 服务，默认监听 `:8000`（F-064）。这是 vLLM 最高频的用法：任何 OpenAI SDK 改 `base_url` 即可接入。

## 启动服务

```bash
vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
  --port 8000 \
  --max-model-len 8192 \
  --api-key my-secret-key
```

常用启动参数（完整面见 [08 在线服务](../concepts/08-online-serving.md) 与 [07 配置体系](../concepts/07-configuration.md)）：

| 参数 | 作用 |
|------|------|
| `--port` | 服务端口（默认 8000） |
| `--max-model-len` | 上下文上限（默认取模型 config） |
| `--api-key` | 启用 Bearer 鉴权 |
| `--served-model-name` | 对外暴露的模型名（可多个） |
| `--gpu-memory-utilization` | 显存占用比例（默认 0.9） |
| `--enable-prefix-caching` / `--no-enable-prefix-caching` | 前缀缓存开关（默认开） |

## 客户端调用（官方 SDK）

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="my-secret-key",  # 与 --api-key 一致
)

completion = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won in 2020."},
        {"role": "user", "content": "Where was it played?"},
    ],
    temperature=0.7,
    max_tokens=256,
)
print(completion.choices[0].message.content)
```

- chat 模板由服务端按模型 tokenizer 自动应用，客户端只传 messages（F-062）。
- 流式：`stream=True`，逐 chunk 收 `choices[0].delta.content`。
- 补全模式：`client.completions.create(model=..., prompt=...)`（注意 vLLM 的 `/v1/completions` 不支持 `suffix` 参数）。

## Anthropic 兼容验证

```python
import anthropic

client = anthropic.Anthropic(base_url="http://localhost:8000", api_key="my-secret-key")
msg = client.messages.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello"}],
)
print(msg.content)
```

`/v1/messages` 端点让 Claude 生态应用零成本切换（F-063）。

## 运维端点

| 端点 | 用途 |
|------|------|
| `/health` | 存活探针 |
| `/v1/models` | 已加载模型列表 |
| `/tokenize`、`/detokenize` | 分词/还原（调试） |
| `/metrics` | Prometheus 指标（见 [13 进阶主题](../concepts/13-advanced.md)） |

## 鉴权与安全

`--api-key` 启用后，所有 `/v1/*` 端点要求 `Authorization: Bearer <key>`；未带 key 返回 401（F-064 的鉴权面）。生产部署建议前置 Nginx（docs/deployment/nginx.md）做 TLS 与限流。

## 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| 400 chat template not found | 模型无 Instruct 版 chat 模板 | 换 Instruct 模型或传 `--chat-template` |
| 401 unauthorized | key 不匹配 | 对齐 `--api-key` 与客户端 |
| 首请求 30s+ | 模型下载/编译预热 | 正常；加 `--download-dir` 预拉权重 |
| 并发上不去 | 单副本吞吐到顶 | 加 DP（`--data-parallel-size`，见 [12 分布式](../concepts/12-distributed.md)） |

## 相关阅读

- [03 结构化输出](03-structured-output.md)：同一服务上开启 JSON 约束
- [01 离线批量推理](01-offline-inference.md)：不起服务的库模式
- [08 在线服务与 API](../concepts/08-online-serving.md)：API 面全谱与多模态
