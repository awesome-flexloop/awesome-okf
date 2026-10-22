---
type: concept
scope: deepseek-recipe
name: 协议转换
version: "0.2.0"
source: deepseek-recipe/src/protocol/, deepseek-recipe/src/request/
description: 三协议统一 Conversation 转换、ConversionOptions 配置项与 resolve_max_tokens 规则
---

# 协议转换

recipe 的第一职责是把三种主流 API 协议的请求归一到同一种 Conversation 格式，共用模型模板与编码逻辑。

---

## 一、协议层组织

`deepseek-recipe/src/protocol/` 下按厂商分列：

| 协议 | 类型 | 导出 |
|---|---|---|
| OpenAI Chat Completions | `protocol/openai/chat_completion/`（request/ + response/） | `ChatCompletionRequest` |
| OpenAI Responses | `protocol/openai/responses/`（request/ + response/） | `ResponsesRequest` |
| Anthropic Messages | `protocol/anthropic/messages/`（request/ + response/） | `MessagesRequest`、`MessagesResponse`、`MessagesStreamEvent` |

每个 request 目录含 `convert.rs`（转换为 Conversation）、`schema.rs`（协议 schema）；`mod.rs` 与 `schema.rs` 共同定义请求/响应类型。

## 二、核心契约：ProtocolRequest

`src/request/mod.rs` 定义两个核心类型：

- **`ProtocolRequest` trait**：`convert(ConversionOptions) -> ConversationRequest` 与 `chunk_generator(request, response_id, model)`——前者归一请求，后者为流式解析生成协议侧 chunk 发生器；
- **`ConversationRequest`**：聚合 `conversation`（归一对话）、`inference_options`（推理选项）、`parsing_options`（解析选项）、`model_version`、`stream`、`response_options`。

## 三、ConversionOptions 配置项

`src/request/options.rs` 的 `ConversionOptions`：

| 配置 | 默认 | 说明 |
|---|---|---|
| `default_thinking_mode` | true | 未显式指定时的思考模式默认值 |
| `reasoning_content_behavior` | FillEmpty | reasoning 内容在多轮间的处理策略 |
| `responses_web_search` / `messages_web_search` | Drop / Reject | web_search 内容的降级策略（两协议不同） |
| `model_versions_by_name` | V4-Pro + V4.1-Flash | 模型名→版本映射；`with_model_alias` 注册别名 |
| `max_tokens_upper_bound` | 393216 | max_tokens 上限 |
| `special_tokens` | — | 自定义 special token 集合 |

## 四、resolve_max_tokens 规则

编码 prompt 之后调用 `ConversationRequest::resolve_max_tokens(prompt_tokens, context_limit)`：

1. 检查 prompt + `max_tokens` 是否超出 `context_limit`，超出返回 400（错误文案与 DeepSeek API 完全一致："This model's maximum context length is …"）；
2. 请求显式指定的 `max_tokens` 保持不变；
3. 未指定时按模式取默认：**非思考 8192 / 思考 65536 / 思考且 max effort 131072**，并降到 prompt 之后剩余的上下文以内（至少 1）。

## 五、结构化输出的转换侧

- Chat Completions 的 `response_format`（`json_schema` 与 `regex` 类型）与 Responses 的 `text.format`（`json_schema` 类型）→ 转换时校验 JSON Schema，渲染时写入 prompt；正则以 `ResponseFormat::Regex` 透传；
- 转换还会选出 `InferenceOptions` 的 `OutputConstraint`：带工具且 tool choice 不为 `none` 的请求是工具调用块，否则是 response format 对应的 JSON、JSON Schema 或正则；
- 是否由后端以约束解码执行，由调用方决定（DeepInfer 的 `so_args` 即对应路径，见[DeepInfer 结构化输出](../../deepinfer/concepts/structured-output.md)）。

## 六、生成参数的版本规则

- `ModelVersion::resolve_top_p`：按版本/思考模式/有无工具解析 top_p；
- 思考模式与 reasoning effort 透传至 `InferenceOptions`；
- `logprobs`/`top_logprobs`（Chat Completions 与 Responses）转换为 `InferenceOptions`，调用方在 `InferenceChunk::Tokens` 中提供后端值；本库不计算概率。
