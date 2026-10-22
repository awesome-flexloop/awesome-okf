---
type: example
scope: deepseek-recipe
name: 流式响应示例
version: "0.2.0"
source: docs/streaming.zh.md
description: StreamProcessor 消费推理流并产出协议 chunk——Rust 异步流与 Python push/finish/close 三段式
---

# 流式响应示例

## 一、Rust

依赖：`cargo add deepseek-recipe@0.2 serde_json@1 tokio-stream@0.1`（tokio 带 `macros` 与 `rt-multi-thread` feature）。

```rust
use deepseek_recipe::openai::ChatCompletionRequest;
use deepseek_recipe::request::{ConversionOptions, ProtocolRequest};
use deepseek_recipe::stream::{InferenceChunk, InferenceFinishReason, StreamProcessor};
use serde_json::json;
use tokio_stream::{StreamExt, iter};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let request: ChatCompletionRequest = serde_json::from_value(json!({
        "model": "DeepSeek-V4.1-Flash",
        "messages": [{"role": "user", "content": "Hello"}],
    }))?;
    let converted = request.convert(ConversionOptions::default())?;

    // 1. 协议侧 chunk 发生器
    let generator = ChatCompletionRequest::chunk_generator(
        &converted, "id-1".into(), "DeepSeek-V4.1-Flash".into(),
    );

    // 2. mock 推理流（真实后端由调用方提供）
    let inference = iter([
        InferenceChunk::Ready { system_fingerprint: None, prompt_usage: None },
        InferenceChunk::Text { content: "Hello world!".into(), token_count: None },
        InferenceChunk::Finish { finish_reason: InferenceFinishReason::Stop },
    ]);

    // 3. StreamProcessor 转换为协议 chunk 流
    let processor = StreamProcessor::new(generator, converted.parsing_options);
    let mut chunks = std::pin::pin!(processor.into_protocol_stream(inference));
    while let Some(chunk) = chunks.next().await {
        println!("{}", serde_json::to_string(&chunk?)?);
    }
    Ok(())
}
```

## 二、Python

```python
from deepseek_recipe import (
    ChatCompletionRequest, ConversionOptions,
    InferenceChunk, InferenceFinishReason, StreamProcessor,
)

converted = ChatCompletionRequest({
    "model": "DeepSeek-V4.1-Flash",
    "messages": [{"role": "user", "content": "Hello"}],
}).convert(ConversionOptions())
generator = ChatCompletionRequest.chunk_generator(converted, "id-1", "DeepSeek-V4.1-Flash")

processor = StreamProcessor(generator, converted.parsing_options)

chunks = []
for chunk in (
    InferenceChunk.text("Hello world!"),
    InferenceChunk.finish(InferenceFinishReason.Stop),
):
    chunks.extend(processor.push(chunk))
chunks.extend(processor.finish())

for chunk in chunks:
    print(chunk.to_json())
processor.close()
```

## 三、要点

- **推理流与协议流解耦**：`InferenceChunk`（Ready/Text/Tokens/Finish）是协议中立的推理侧输入；`StreamProcessor` 把它转换为所选协议的响应 chunk（SSE 事件或 JSON）；
- **思考模式**：只有为 processor 附加 tokenizer 才会在 usage 中统计 `reasoning_tokens`（tokenizer 用法见[使用 tokenizer](tokenizer.md)）；
- **后端与 HTTP 传输由应用提供**——完整接入形态见[服务器示例](servers.md)。
