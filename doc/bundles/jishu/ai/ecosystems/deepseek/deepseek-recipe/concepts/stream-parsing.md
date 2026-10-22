---
type: concept
scope: deepseek-recipe
name: 流式输出解析
version: "0.2.0"
source: deepseek-recipe/src/stream/
description: InferenceChunk 协议中立推理流、StreamProcessor 与跨 chunk KMP 增量状态机、工具参数流式转换
sources:
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践
---

# 流式输出解析

推理后端按 token 粒度返回 chunk——一个 UTF-8 码点、DSML 标签或工具调用参数都可能被拆到多个 chunk 中。recipe 的 `StreamProcessor` 在内存中维护跨 chunk 状态机，正确解码输出并**尽早**解析出结构以降低返回时延。

---

## 一、协议中立的推理流：InferenceChunk

`src/stream/inference.rs` 定义四个变体：

| 变体 | 载荷 | 说明 |
|---|---|---|
| `Ready` | system_fingerprint, prompt_usage | 流开始信号 |
| `Text` | content, token_count | 文本 chunk（后端无 tokenizer 时使用） |
| `Tokens` | token_ids, logprobs | token ID chunk（附加 tokenizer 后可解码；0.2.0 起替代旧 `Token` 单token变体） |
| `Finish` | finish_reason | 流结束（Stop/StopSequence/EndOfStream 等 6 种） |

`OutputChunk`（`stream/mod.rs`）是解析后的中间产物：`Start / Content / Reasoning / ToolCallBegin / ToolCallNamed / ToolCallArgumentsDelta / Finish`，保证 Start 首发一次、Finish 收尾一次。

## 二、StreamProcessor

`src/stream/processor.rs`：

```rust
// Rust：消费推理流，产出协议 chunk 流
let processor = StreamProcessor::new(generator, converted.parsing_options)
    .with_tokenizer(tokenizer);              // 可选：解码 token chunk
let mut chunks = processor.into_protocol_stream(inference);
```

```python
# Python：push/finish/close 三段式
processor = StreamProcessor(generator, converted.parsing_options, tokenizer)
chunks = []
for chunk in (InferenceChunk.tokens(token_ids), InferenceChunk.finish(InferenceFinishReason.Stop)):
    chunks.extend(processor.push(chunk))
chunks.extend(processor.finish())
processor.close()
```

- `generator` 来自各协议的 `chunk_generator`（如 `ChatCompletionRequest::chunk_generator(&converted, "id-1", model)`）；
- token 输入下 processor 增量解码 token IDs，多 token 字符未完整时先缓冲；产生文本的 token IDs 计入 completion token；
- 思考模式下，processor 用附加 tokenizer 编码已输出的 reasoning 内容统计 usage 中的 `reasoning_tokens`（文本 chunk 与 token chunk 均如此）；未附加 tokenizer 时 Chat Completions 的 usage 不含 `completion_tokens_details`，Responses 的 `reasoning_tokens` 为 0。

## 三、跨 chunk 解析状态机

知乎报告描述的机制在 `src/stream/output_parser.rs` 落地：

- **跨 chunk 解析**：解码遇到不完整 UTF-8 码点时先缓冲相关 token，待后续 token 补齐状态后交给解析器；
- **KMP 增量匹配**：解析器按思考、正文和工具参数等阶段维护状态，用 **KMP 算法**（`kmp_table`/`kmp_next`）增量匹配分隔标记；chunk 末尾只有标记的一部分时保留匹配进度，下个 chunk 到达继续增量识别；已确定的内容随解析进度输出，无需反复扫描之前的文本；
- **输出侧防注入**：`ChunkKind`（Text/PlainTokens/SpecialToken）区分——token 输入下 ` ` 与 DSML 标记只匹配**解码出的 special token**，普通 token 拼出的同文本是内容。

## 四、工具参数流式转换

- **工具名解析完成后即可返回**，后续根据 DSML 参数边界直接生成 JSON 片段；
- 字符串值逐段做 JSON 转义；数组、对象等非字符串值按原始 JSON 文本输出，**无需构造完整参数对象**——省去反复解析与序列化开销；
- 参数较长时也能在生成过程中逐段返回，缩短首个参数片段的等待时间。

## 五、logprobs 透传

转换后的请求设置了 `InferenceOptions::logprobs` 时，调用方为每个 token ID 提供一个 `InferenceTokenLogprob`：解码出的文本会带上其 token 的 log probability，由 Chat Completions 与 Responses 输出。数量不一致的 `Tokens` chunk 以 `StreamError::LogprobCountMismatch` 结束流。

## 六、Stop sequence

stop sequence 的匹配同样走 KMP 增量路径：标记部分出现在 chunk 末尾时保留进度，下个 chunk 继续识别；命中后以 `FinishReason::StopSequence` 结束流（对应协议的 stop_reason 语义）。
