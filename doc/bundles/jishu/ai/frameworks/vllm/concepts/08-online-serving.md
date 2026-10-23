---
type: Concept
title: "在线服务与 API：OpenAI 兼容面及扩展"
description: "vllm serve 的完整 API 面——OpenAI 兼容（Completions/Chat/Responses/Embeddings/Audio）、Anthropic Messages、自定义 Pooling/Score/Classification/Decisions 端点、chat 模板机制、鉴权、流式与多模态、开发模式与 LoRA 动态加载端点"
tags: [vllm, online-serving, openai-compatible, anthropic-api, chat-template, api, streaming]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: website-serving
    url: https://docs.vllm.ai/en/latest/serving/online_serving/
    title: Online Serving（官网文档，2026-10-14 更新）
  - id: local-openai
    resource: /references/source-map.md
    title: vllm/entrypoints/openai/（本地检出）
---

# 在线服务与 API：OpenAI 兼容面及扩展

`vllm serve <model>` 起的不是「一个 API」，而是**一组接口族**：OpenAI 兼容面（迁移零成本）+ Anthropic 面（Claude 生态）+ vLLM 自定义面（池化/评分/决策等模型任务）+ 运维面（健康检查/分词/LoRA 管理）（F-062）。

## OpenAI 兼容端点

| 端点 | 适用模型 | 备注 |
|------|---------|------|
| `/v1/completions` | 文本生成 | 不支持 `suffix` 参数 |
| `/v1/chat/completions` | 带 chat 模板的文本生成 | `user` 参数被忽略；`parallel_tool_calls` 控制并行工具调用 |
| `/v1/chat/completions/batch` | 同上 | 批量变体 |
| `/v1/responses`（含 `/{id}`、`/{id}/cancel`） | 文本生成 | Responses API |
| `/v1/decisions` | 文本生成 | 谓词/选择/评分三类 typed 问题 |
| `/v1/embeddings` | embedding 模型 | |
| `/v1/audio/transcriptions`、`/v1/audio/translations` | ASR 模型 | |

## Anthropic 兼容端点

`/v1/messages`、`/v1/messages/count_tokens`——Claude 生态应用可低成本切换到开源模型（F-063）。源码位置 `vllm/entrypoints/anthropic/`（F-002）。

## vLLM 自定义端点

| 端点 | 用途 |
|------|------|
| `/classify` | 分类模型 |
| `/score`、`/v1/score` | 打分模型（cross-encoder/bi-encoder/late-interaction） |
| `/pooling` | 全部池化模型 |
| `/generative_scoring` | 对指定 `label_token_ids` 算下一 token 概率 |

另有 scale-out 面（`--enable-scale-out` 开启）：token-in/token-out `/inference/v1/generate`、renderer/derenderer 预处理端点（把请求渲染成 token ids 再推理，适配自定义前端）（F-062）。

## 运维与管理端点

- 基础：`/health`、`/v1/models`、`/version`、`/load`（F-066）；
- 分词：`/tokenize`、`/detokenize`、`/tokenizer_info`（含 chat 模板与配置）（F-066）；
- LoRA 动态加载/卸载：`/v1/load_lora_adapter`、`/v1/unload_lora_adapter`（**仅限本地开发**）（F-067）；
- 剖析：`/start_profile`、`/stop_profile`（F-066）。

## chat 模板：对话能力的开关

Chat 端点要求模型的 tokenizer 配置里带 chat 模板（Jinja2）。没有模板的 Instruct 模型，聊天请求会直接报错；补救：`vllm serve <model> --chat-template ./path.jinja`（文件路径或内联字符串）（F-065）。

多模态消息用 OpenAI 新版 content 段格式（`[{"type": "text", "text": ...}]`）。vLLM 自动探测模板期望的 content 格式（`string` 或 `openai` 列表），探测不符时用 `--chat-template-content-format` 覆盖（F-065）。

## 鉴权与安全边界

- `--api-key` 可传多个 key（任一中即通过，便于轮换），或环境变量 `VLLM_API_KEY`（F-064）；
- 多模态本地文件读取需显式开 `--allowed-local-media-path`（有安全风险，仅可信环境）；`--allowed-media-domains` 限制可拉取的媒体域名（F-013）；
- 不要把无鉴权服务暴露公网。

## 开发模式端点

`VLLM_SERVER_DEV_MODE=1` 开启（**生产禁用**，F-068）：缓存管理 `/reset_prefix_cache`、`/reset_mm_cache`、`/reset_encoder_cache`；RL 权重迁移 `/init_weight_transfer_engine`、`/update_weights` 系列；sleep 模式 `/sleep`、`/wake_up`；`/collective_rpc`（极端危险，可执行任意 RPC）。

## 部署变体

- **Ray Serve LLM**：把 vLLM 引擎包装成可自动扩缩、负载均衡、带背压的生产级服务，OpenAI 兼容 API + Python API，单 GPU 到多节点无需改代码（F-062）；
- **gRPC 服务**：`vllm/entrypoints/grpc_server.py`，非 HTTP 场景（F-002）；
- **批处理**：`vllm run-batch` 走 OpenAI Batch 语义（F-130）。

## 延伸阅读

- [01 快速开始](01-quickstart.md)：serve 的最小验证
- [09 模型支持](09-model-support.md)：哪些模型能serve、任务类型如何映射端点
- [13 进阶主题](13-advanced.md)：生产栈、多 API server 与 PD 分离服务化
