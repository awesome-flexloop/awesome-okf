---
type: bundle
okf_version: "0.2"
scope: deepseek-recipe
name: deepseek-recipe Wiki
version: "0.2.0"
source: https://github.com/deepseek-ai/deepseek-recipe
description: deepseek-recipe - DeepSeek 生产级 Token 编解码组件源码中文教程，Rust 工作区 + Python 绑定，与官方 API 处理逻辑完整对齐
sources:
  - id: deepseek-recipe-github
    resource: https://github.com/deepseek-ai/deepseek-recipe
    title: deepseek-recipe 官方仓库（MIT）
  - id: deepseek-announce
    resource: https://mp.weixin.qq.com/s?__biz=Mzk0OTYwNzc3NQ%3D%3D&mid=2247485884&idx=1&sn=d457981abe7db1f1b5d600fc109dc836
    title: DeepSeek 开源推理框架：走向真正普惠的未来（DeepSeek 官方公众号，2026-10-20）
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践（DeepSeek 官方技术报告）
---

# deepseek-recipe

**deepseek-recipe** 是 DeepSeek 2026-10-20 与 [DeepInfer](../deepinfer/index.md) 同步开源的**生产级 Token 编解码组件**（MIT，v0.2.0）。它由一套 Rust 库及对应 Python 绑定组成：把不同格式的 API 请求统一转换为 Conversation 格式，将对话渲染为适用于 DeepSeek 模型的 prompt，通过附加 tokenizer 编码为 token IDs，并把模型输出转换回对应格式的响应——**处理逻辑与 DeepSeek 官方 API 完整对齐**，确保第三方部署获得与官方一致的 API 体验。

> **边界**：recipe 可用于把推理后端接入兼容多种格式的 API 服务；**调用方必须提供模型推理、工具执行和 HTTP 传输**。

---

## 支持范围速览

| 能力域 | 内容 |
|---|---|
| **请求/响应格式** | Messages（Anthropic）、Chat Completions 与 Responses（OpenAI）三协议；流式与完整响应；文本、图片、思考模式、客户端工具调用、`prefix` 续写 |
| **Prompt** | DeepSeek V4 与 V4.1 对话渲染 + 附加 tokenizer 编码为 token IDs |
| **生成参数** | 思考模式、reasoning effort、temperature、top_p、输出上限（`resolve_max_tokens`：非思考 8192 / 思考 65536 / 思考 max effort 131072） |
| **输出解析** | reasoning 内容、工具调用、JSON object 输出、stop sequence；流式 `reasoning_tokens` 计数 |
| **结构化输出** | Chat Completions `response_format`（json_schema/regex）、Responses `text.format`；JSON Schema 校验并写入 prompt；正则透传 |
| **图片** | base64 / URL 传入，OpenCV 预处理（V4.1）；V4 请求图片替换为 `[Unsupported Image]` 文本；`DestinationFilter` SSRF 防护 |
| **工具** | 函数工具；Responses 工具命名空间与 `apply_patch` 自定义工具；V4.1 工具延迟加载与客户端工具搜索 |
| **Log probability** | Chat Completions `logprobs`/`top_logprobs` 与 Responses `top_logprobs` 透传（本库不计算概率） |

---

## 文档导航

### 📘 核心概念 [concepts/](concepts/index.md)

| 文档 | 内容 |
|---|---|
| [概述](concepts/overview.md) | 定位、六大 crate 职责、数据流主线 |
| [协议转换](concepts/protocol-conversion.md) | 三协议统一 Conversation、ConversionOptions、resolve_max_tokens |
| [Prompt 编码](concepts/prompt-encoding.md) | V4/V4.1 渲染差异、special token 防注入、分段并行编码 |
| [流式解析](concepts/stream-parsing.md) | InferenceChunk、跨 chunk KMP 状态机、工具参数流式转换 |
| [图片管线](concepts/image-pipeline.md) | OpenCV 预处理、图片拉取、DestinationFilter |

### 📙 代码示例 [examples/](examples/index.md)

| 示例 | 内容 |
|---|---|
| [快速上手](examples/quickstart.md) | Python/Rust 最小示例：请求转换 → prompt 渲染 |
| [流式响应](examples/streaming.md) | StreamProcessor 消费推理流并产出协议 chunk |
| [使用 tokenizer](examples/tokenizer.md) | encode 编码 / token 流解码 / reasoning_tokens 计数 |
| [服务器示例](examples/servers.md) | server-rs（Axum）/ server-py（FastAPI）/ encoding-decoding-demo |

### 📗 API 参考 [references/](references/index.md)

| 文档 | 内容 |
|---|---|
| [外部资源](references/resources.md) | 官方文档、crate 索引、内置 tokenizer 声明 |

---

## 快速开始

### Python（3.10+）

```sh
python3 -m pip install deepseek-recipe
```

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

### Rust（1.97.1）

```sh
cargo add deepseek-recipe@0.2 deepseek-recipe-encoding@0.2 serde_json@1
```

```rust
use deepseek_recipe::openai::ChatCompletionRequest;
use deepseek_recipe::request::{ConversionOptions, ProtocolRequest};
use deepseek_recipe_encoding::v4::dsv41::DeepseekV41Encoding;
use serde_json::json;

let request: ChatCompletionRequest = serde_json::from_value(json!({
    "model": "DeepSeek-V4.1-Flash",
    "messages": [{"role": "user", "content": "Hello"}],
}))?;
let converted = request.convert(ConversionOptions::default())?;
let rendered = DeepseekV41Encoding::new().render_conversation(&converted.conversation);
println!("{}", rendered.prompt);
```

本库根据请求的 `model` 名解析模型版本，默认接受 `DeepSeek-V4-Pro` 与 `DeepSeek-V4.1-Flash`；其他名称（如 `deepseek-flash`）用 `ConversionOptions::with_model_alias` 注册，未注册的名称直接拒绝。

---

## 相关项目

| 项目 | 关系 |
|---|---|
| [DeepInfer](../deepinfer/index.md) | 姊妹项目——推理引擎核心层；recipe 位于其前后两端做协议↔token 转换，也可接任意自研后端 |
| [DeepSeek API 平台](https://platform.deepseek.com) | 处理逻辑对齐的官方实现（校验错误文案与 DeepSeek API 完全一致） |

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
```
