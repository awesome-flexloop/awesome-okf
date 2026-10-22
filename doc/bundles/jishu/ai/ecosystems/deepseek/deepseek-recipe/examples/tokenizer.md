---
type: example
scope: deepseek-recipe
name: 使用 tokenizer 示例
version: "0.2.0"
source: docs/tokenizer.zh.md, static/tokenizers/README.md
description: 对话编码为 token IDs、token 流解码与 reasoning_tokens 计数——Rust 与 Python 双语言
---

# 使用 tokenizer

`PromptEncoding` 与 `StreamProcessor` **不会自动加载 tokenizer**：未附加时 `encode` 返回 `EncodingError::MissingTokenizer`，`Tokens` chunk 以 `StreamError::MissingTokenizer` 结束流。须先用 `with_tokenizer` 传入再调用相应方法。

## 一、tokenizer 来源

| 来源 | 说明 |
|---|---|
| 仓库 `static/tokenizers/` | 内置 V4（改自 DeepSeek-V4-Pro）与 V4.1（改自 DeepSeek-V4-Flash-Vision-Exp）tokenizer 副本，从对应目录加载 `tokenizer.json` 即可；各目录 README 记录 revision、SHA-256 与 image token 变更 |
| Hugging Face Hub | `Tokenizer.from_pretrained`（Python）/ 自行加载；added vocabulary 必须包含渲染写入的每个 special token 的拼写，否则 `encode` 返回 `EncodingError::Encode` |

## 二、编码：对话 → token IDs

### Python

```python
from deepseek_recipe import (
    ChatCompletionRequest, ConversionOptions, DeepseekV41Encoding, Tokenizer,
)

request = ChatCompletionRequest({
    "model": "DeepSeek-V4.1-Flash",
    "messages": [{"role": "user", "content": "Hello"}],
})
converted = request.convert(ConversionOptions())

tokenizer = Tokenizer.from_file("static/tokenizers/v41/tokenizer.json")
encoding = DeepseekV41Encoding().with_tokenizer(tokenizer)
print(encoding.encode(converted.conversation))
```

`Tokenizer.from_str` 直接加载文件内容；未附加 tokenizer 或编码失败时 `encode` 抛出 `RuntimeError`。

### Rust

```rust
use tokenizers::Tokenizer;
use deepseek_recipe_encoding::{PromptEncoding, PromptTokenizer};
use deepseek_recipe_encoding::v4::dsv41::DeepseekV41Encoding;

let tokenizer = Tokenizer::from_file("static/tokenizers/v41/tokenizer.json")?;
let encoding = DeepseekV41Encoding::new()
    .with_tokenizer(PromptTokenizer::new(&tokenizer));
let token_ids = encoding.encode(&converted.conversation)?;
```

`PromptTokenizer` 为 `Tokenizer` 另存一份不含 added vocabulary 的副本；`encode` 先渲染对话再分词——special 区间按 special token ID 编码、区间间纯文本批量编码（`tokenizers` crate 依 `TOKENIZERS_PARALLELISM` 并行）。

## 三、编码后：resolve_max_tokens

```python
max_tokens = converted.conversation.resolve_max_tokens(
    prompt_tokens, context_limit
)
```

- `prompt_tokens` = 编码 token 数 + `MultiModalData::image_token_adjustment`（图片超出占位符的 token 数）；
- `context_limit` = 模型上下文可容纳 token 数；
- 显式指定的 `max_tokens` 不变；未指定取默认（非思考 8192 / 思考 65536 / 思考 max effort 131072）并降到剩余上下文内；
- prompt + `max_tokens` 超过 `context_limit` 时：Rust 返回 `ConversionError`，Python 抛出 `ConversionError`。

## 四、解码：token IDs → 协议响应

后端产生 token IDs 时，把同一个 tokenizer 附加到 stream processor 即可解码：

```python
processor = StreamProcessor(generator, converted.parsing_options, tokenizer)
for chunk in (InferenceChunk.tokens(token_ids), InferenceChunk.finish(InferenceFinishReason.Stop)):
    chunks.extend(processor.push(chunk))
```

- processor 增量解码 token IDs，多 token 字符未完整时先缓冲；产生文本的 token IDs 计入 completion token；
- 每个 special token 单独解码成一段并带标记——输出解析器只把 token 形式的标记当作标记，普通 token 拼出的同文本是内容；
- 思考模式下 processor 用该 tokenizer 编码 reasoning 内容统计 usage 的 `reasoning_tokens`；
- `InferenceChunk.tokens` 携带后端一次输出的全部 token IDs，processor 一起解码；logprobs 数量与 token 数不一致时以 `StreamError::LogprobCountMismatch` 结束流。

## 五、路径提示

tokenizer 路径相对于**工作目录**：在仓库根目录运行时可直接用 `static/tokenizers/v41/tokenizer.json`；在其他目录运行请改用绝对路径或你自己的 `tokenizer.json`（Rust 示例同理，`cargo run --manifest-path` 跨目录运行时尤其注意）。
