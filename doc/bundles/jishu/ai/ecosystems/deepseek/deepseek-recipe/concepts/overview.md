---
type: concept
scope: deepseek-recipe
name: deepseek-recipe 概述
version: "0.2.0"
source: README.zh.md, Cargo.toml, CHANGELOG.md
description: deepseek-recipe 组件定位、Cargo 工作区六大 crate 职责与请求到响应的数据流主线
sources:
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践
---

# deepseek-recipe 概述

deepseek-recipe 解决的是推理服务中一个长期被低估的环节：**API 协议与 token 序列之间的双向转换**。在生产规模下，这个环节面临三重工程难题——多协议适配的爆炸、超长上下文的 tokenize 延迟、用户文本中 special token 的注入风险——recipe 把它们统一收口，并以 Rust 实现换取高效处理，同时提供 Python 绑定降低接入门槛。

---

## 一、数据流主线

```
ChatCompletionRequest / ResponsesRequest / MessagesRequest
        │  convert(ConversionOptions)
        ▼
ConversationRequest（conversation + inference_options + parsing_options + model_version）
        │  DeepseekV4/V41Encoding::render_conversation   ──→ RenderedPrompt（prompt + special_ranges + image_sources）
        │  DeepseekV4/V41Encoding::encode                 ──→ token IDs（需 with_tokenizer 附加 tokenizer）
        ▼
   推理后端（调用方提供）
        │  InferenceChunk 流（Ready / Text / Tokens / Finish）
        ▼
StreamProcessor + 各协议 chunk_generator
        │
        ▼
Chat Completions / Responses / Messages 协议响应（SSE 或 JSON）
```

**职责边界**：recipe 全程不提供模型推理、工具执行与 HTTP 传输——它是可组合的"编解码中间件"。

## 二、Cargo 工作区结构

根 `Cargo.toml` 定义 8 个 workspace members，`version = "0.2.0"`、`edition = "2024"`、`resolver = "3"`、MIT 协议。

| Crate | 职责 |
| --- | --- |
| `deepseek-recipe` | 协议转换与模型输出解析（主库） |
| `deepseek-recipe-core` | 共享的对话、消息、图片与工具类型 |
| `deepseek-recipe-encoding` | DeepSeek V4 与 V4.1 的 prompt 渲染与 token 编码 |
| `deepseek-recipe-image` | 图片拉取与预处理 |
| `deepseek-recipe-macros` | `prompt!` 模板宏与 `UntaggedDeserialize` derive（proc-macro） |
| `deepseek-recipe-python` | Python bindings（PyO3 cdylib，lib 名 `_native`） |
| `encoding-decoding-demo` | Web 演示（渲染 prompt + 解析输出，见[服务器示例](../examples/servers.md)） |
| `server-rs` | Axum mock API 服务器示例 |

另有 `server-py/`（纯 Python FastAPI mock 示例，非 Rust member）。

## 三、生产定位（源自知乎技术报告）

- **API 多协议适配**：Chat Completions API、Responses API 和 Messages API 的请求转成同一种对话格式，共用模型模板和编码逻辑，按模型版本生成 prompt 和 token 序列；
- **性能**：请求转换、prompt 编码和输出解析都由 Rust 实现，以实现高效处理，同时支持 Python 绑定调用；
- **Tokenizer 加速**：通过 special token 分段和并行策略，避免 special token 注入的同时，降低长文本 tokenize 的处理时延（详见[提示词编码](prompt-encoding.md)）。

## 四、模型版本解析

`ModelVersion` 目前两个取值：`DeepseekV4Pro` 与 `DeepseekV41Flash`：

- 根据请求 `model` 名解析，默认接受 `DeepSeek-V4-Pro` 与 `DeepSeek-V4.1-Flash`；别名经 `ConversionOptions::with_model_alias` 注册（如 `deepseek-flash`）；**未知名称直接拒绝**（0.2.0 变更）；
- 仅 V4.1 支持图片输入与对话中 system 消息；V4 请求中的每张图片被替换为文本 `[Unsupported Image]`；
- temperature/top_p 按版本/思考模式/有无工具解析。

## 五、版本演进要点

| 版本 | 日期 | 要点 |
|---|---|---|
| 0.1.0 | 2026-09-10 | 初始发布：三协议转换、V4/V4.1 渲染、图片管线、流式解析、Python 包 |
| 0.2.0 | 2026-10-20 | 破坏性 API 变更：`ModelVersion` 解析、logprobs、`reasoning_tokens`、结构化输出（JsonSchema/Regex + OutputConstraint）、显式 special token 体系（`prompt!` 宏 + `special_ranges`）、`prefix` 续写、deferred tool loading / tool_search、system 图片、`DestinationFilter`、`resolve_max_tokens`（上限 393216）；移除 `InferenceChunk::Token`（改 `Tokens`）等 |

## 六、语言与工具链要求

- **Rust**：`rust-toolchain.toml` 固定 1.97.1（rustfmt/clippy/rust-src/rust-analyzer 组件）；
- **Python**：3.10+（pyo3 `abi3-py310` 稳定 ABI，每平台一个 wheel 跑所有 CPython 3.10+）；
- **源码构建**：Rust 工具链 + OpenCV 4.11+（发布 wheel 打包 OpenCV 4.12.0）+ Clang/libclang + CMake，经 maturin 构建。
