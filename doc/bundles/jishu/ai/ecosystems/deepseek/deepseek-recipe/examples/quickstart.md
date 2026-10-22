---
type: example
scope: deepseek-recipe
name: 快速上手示例
version: "0.2.0"
source: README.zh.md, docs/tokenizer.zh.md
description: deepseek-recipe 最小可用示例——Python 与 Rust 双语言的请求转换与 prompt 渲染
---

# 快速上手

## 一、Python（3.10+）

### 安装

```sh
python3 -m pip install deepseek-recipe
```

### 最小示例：Chat Completions 请求 → V4.1 prompt

```python
from deepseek_recipe import ChatCompletionRequest, ConversionOptions, DeepseekV41Encoding

request = ChatCompletionRequest({
    "model": "DeepSeek-V4.1-Flash",
    "messages": [{"role": "user", "content": "Hello"}],
})
converted = request.convert(ConversionOptions())
rendered = DeepseekV41Encoding().render_conversation(converted.conversation)
print(rendered.prompt)
```

## 二、Rust（1.97.1）

### 安装

```sh
cargo add deepseek-recipe@0.2 deepseek-recipe-encoding@0.2 serde_json@1
```

### 最小示例

```rust
use deepseek_recipe::openai::ChatCompletionRequest;
use deepseek_recipe::request::{ConversionOptions, ProtocolRequest};
use deepseek_recipe_encoding::v4::dsv41::DeepseekV41Encoding;
use serde_json::json;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let request: ChatCompletionRequest = serde_json::from_value(json!({
        "model": "DeepSeek-V4.1-Flash",
        "messages": [{"role": "user", "content": "Hello"}],
    }))?;
    let converted = request.convert(ConversionOptions::default())?;
    let rendered = DeepseekV41Encoding::new().render_conversation(&converted.conversation);
    println!("{}", rendered.prompt);
    Ok(())
}
```

源码构建与图片依赖见官方开发指南（Rust 工具链 + OpenCV 4.11+ + Clang/libclang + CMake，maturin 构建）。

## 三、要点

- **模型名解析**：默认接受 `DeepSeek-V4-Pro` 与 `DeepSeek-V4.1-Flash`；其他名称（如 `deepseek-flash`）用 `ConversionOptions` 的 `with_model_alias` 注册，未注册直接拒绝；
- **渲染结果**：`render_conversation` 返回 prompt 文本 + `special_ranges`（显式 special token 的字节区间）+ `image_sources`——对 prompt 自行分词时必须同样处理 `special_ranges`（见[提示词编码](../concepts/prompt-encoding.md)）；
- **token 编码**：`encode` 需要 `with_tokenizer` 先附加 tokenizer，完整流程见[使用 tokenizer](tokenizer.md)。

## 四、Encoding & Decoding Demo

不开环境也能体验转换效果——仓库根目录运行：

```sh
cargo run -p encoding-decoding-demo --locked
```

打开 <http://127.0.0.1:7778>（`DEMO_ADDR` 可改）：选 API 格式、编辑请求 JSON、渲染 prompt 并高亮 special token（Render 模式）；或编辑完整模型输出、解析为所选协议的完整响应（Parse 模式）。无需 OpenCV/权重/API key。
