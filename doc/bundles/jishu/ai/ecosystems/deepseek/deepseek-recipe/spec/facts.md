---
type: spec
title: "deepseek-recipe 源码事实清单（R-Phase）"
---

# deepseek-recipe 源码事实清单（R-Phase）

> 源码路径：SpecWeave 工作树内镜像 `external/libs/ai/deepseek-ai/deepseek-recipe`（上游 https://github.com/deepseek-ai/deepseek-recipe ）
> 收集日期：2026-10-22
> 版本：0.2.0（Cargo.toml），edition 2024，resolver 3，MIT

---

## F-001：工作区结构

- 文件：Cargo.toml:2-12
- 8 个 workspace members：六大库 crate（deepseek-recipe / -core / -encoding / -image / -macros / -python）+ encoding-decoding-demo + server-rs；server-py 非 Rust member（纯 Python）

## F-002：协议层组织

- 文件：src/protocol/openai/{chat_completion,responses}/、src/protocol/anthropic/messages/（各含 request/convert.rs、schema.rs 与 response/）
- 导出：openai/mod.rs:1-2（ChatCompletionRequest、ResponsesRequest）；anthropic/mod.rs:3-4（MessagesRequest、MessagesResponse、MessagesStreamEvent）

## F-003：核心契约与配置

- 文件：src/request/mod.rs、src/request/options.rs
- ProtocolRequest trait（mod.rs:239-258）：convert + chunk_generator；ConversationRequest（mod.rs:145-153）聚合 conversation/inference_options/parsing_options/model_version/stream/response_options
- ConversionOptions（options.rs:101-148）：default_thinking_mode 默认 true；reasoning_content_behavior 默认 FillEmpty；responses_web_search 默认 Drop、messages_web_search 默认 Reject；model_versions_by_name 默认两版本；max_tokens_upper_bound 默认 393216
- resolve_max_tokens（mod.rs:207-235）：未指定默认非思考 8192/思考 65536/思考 max effort 131072（mod.rs:158-166），压到剩余上下文且至少 1；超限 400 错误文案与 DeepSeek API 一致
- ModelVersion（options.rs:61-93）：仅 V4.1 支持图片与对话中 system 消息；resolve_top_p 按版本/思考/工具解析

## F-004：编码层

- 文件：deepseek-recipe-encoding/src/lib.rs、src/v4/{dsv4.rs,dsv41.rs}、src/tokenizer.rs、src/v4/mod.rs
- PromptEncoding trait（lib.rs:57-91）：encode + render_conversation → RenderedPrompt{prompt, special_ranges, image_sources}（lib.rs:34-43）
- V4 vs V4.1 差异：V4 不发 System token、系统消息 hoist 到 BOS 后空行拼接（dsv4.rs:30-36）、effort 为两大段长文本（dsv4.rs:17-26）；V4.1 工具提示/response format 追加到首条 system（无则插入空 system，dsv41.rs:34-37）、effort 渲染为 50/75/100（dsv41.rs:21-30）、DSML 标签带空格（dsv41.rs:17-19）
- PromptTokenizer（tokenizer.rs:41-118）：无 added vocabulary 的 plain tokenizer + special ID 表；encode_ids 按区间编码 + encode_batch_fast 批量并行
- 防注入（v4/mod.rs:24-33）：仅 8 个 grounding token（Ref/Box/Point/Polygon 及闭合，Aho-Corasick）在 assistant/reasoning 内容升格为显式 special token；消息文本拼出的 special token 拼写一律按普通字符编码（lib.rs:8-15）

## F-005：流式解析

- 文件：src/stream/{inference.rs,mod.rs,processor.rs,output_parser.rs}
- InferenceChunk 四变体（inference.rs:29-54）：Ready/Text/Tokens/Finish；FinishReason 6 种（inference.rs:76-89）
- OutputChunk（mod.rs:66-96）：Start/Content/Reasoning/ToolCallBegin/ToolCallNamed/ToolCallArgumentsDelta/Finish
- StreamProcessor（processor.rs:19-79）：new(generator, parsing_options) + with_tokenizer + into_protocol_stream（0.2 从 process 改名，CHANGELOG.md:196）
- KMP 增量匹配（output_parser.rs:680-800）：kmp_table/kmp_next 逐字节增量；ChunkKind（output_parser.rs:77-94）区分 Text/PlainTokens/SpecialToken 实现输出侧防注入

## F-006：图片管线

- 文件：deepseek-recipe-image/src/{lib.rs,opencv.rs,fetcher.rs}
- 默认 feature opencv-preprocess + reqwest-fetch（lib.rs:24-30）；核心 trait ImageFetcher/ImagePreprocessor/ImageResolver
- OpenCvImagePreprocessor（opencv.rs:27-34）：infer 探测类型 → 只读 header 校验 → 低 detail 降采样 → V4.1 token 预算缩放 → padding 色 127 → 透明背景 #FDFDFD → WebP 质量 90（opencv.rs:17-25 常量）
- DestinationFilter（fetcher.rs:26-42）：闭包 Fn(&str, IpAddr)->bool；DNS 解析层 FilteringResolver + 每个重定向目标过滤，最多 5 次重定向（fetcher.rs:16）
- 错误 Display 即 400 响应体（lib.rs:8-13）；ImageByteBudget 配额 + RetryPolicy 重试

## F-007：Python 绑定

- 文件：deepseek-recipe-python/src/lib.rs、python/deepseek_recipe/__init__.py
- #[pymodule] _native 注册约 55 类 + 3 异常（ConversionError/ImageError/CalcResizeError）+ __version__（lib.rs:46-108）；__init__.py:3-60 重导出 + _native.pyi 存根
- Tokenizer 静态构造 from_file/from_str/from_pretrained（tokenizer.rs:28-63）
- pyo3 abi3-py310（Cargo.toml:23）：每平台一个 wheel 跨 CPython 3.10+；maturin 构建；源码构建需 Rust + OpenCV 4.11+（发布 wheel 打包 4.12.0）+ Clang/libclang + CMake

## F-008：服务器示例

- server-rs（Axum）：api_handler<T: ProtocolRequest>（main.rs:22-51），stream=true 走 text/event-stream；三端点 /v1/chat/completions、/v1/responses、/v1/messages；conversion_options() 注册 deepseek-v4-pro/deepseek-flash 别名（lib.rs:64-68）；默认 127.0.0.1:7777（SERVER_ADDR）
- server-py（FastAPI）：uvicorn main:app；PROMPT_ENCODINGS 按 ModelVersion 选 Encoding（main.py:61-64）；create_app(infer=...) 注入自定义后端——回调收 PreparedRequest 产 InferenceChunk 异步迭代器（server-py/README.md:46-55）
- 两者均无鉴权、图片 fetcher 不过滤私网地址，仅限本机回环（两 README Deployment scope 节）

## F-009：Web 演示

- encoding-decoding-demo：cargo run -p encoding-decoding-demo --locked → http://127.0.0.1:7778（DEMO_ADDR）；Render/Parse 两模式；POST /api/render 与 /api/parse（format+body+output+可选 finish_reason，README.md:62-91）；示例输出含 … 推理、两个 DSML 天气工具调用与 EOS；首个 EOS 后内容丢弃；不做 token 编解码、不推理、不拉图片 URL（README.md:94-97）

## F-010：内置 tokenizer

- 文件：static/tokenizers/README.md:8-11、v4/README.md:9-13、v41/README.md:9-12
- v4/ 改自 HF deepseek-ai/DeepSeek-V4-Pro（id 129264/129279 image token 对调）；v41/ 改自 deepseek-ai/DeepSeek-V4-Flash-Vision-Exp（id 129264 重赋值为 image token）
- 各 README 记录 revision、SHA-256、变更；MIT Copyright (c) 2023 DeepSeek；encodings 不自动加载，需调用方加载匹配 tokenizer

## F-011：工具链

- rust-toolchain.toml:3 固定 1.97.1（rustfmt/clippy/rust-src/rust-analyzer）；Python 3.10+（abi3-py310）

## F-012：版本演进

- CHANGELOG.md:11-184（0.2.0，2026-10-20）与 :240-245（0.1.0，2026-09-10）
- 0.2.0 新增：ModelVersion 解析、按版本 temperature/top_p、logprobs、reasoning_tokens、结构化输出 JsonSchema/Regex + OutputConstraint、显式 special token（prompt! 宏 + special_ranges）、prefix 续写、deferred tool loading/tool_search、system 图片、DestinationFilter、response_options、max_tokens 上限 393216、resolve_max_tokens
- 0.2.0 变更：未知 model 名拒绝；校验错误文案对齐 DeepSeek API；StreamTokenizer 新方法（id_to_token/count_tokens/is_special_token）；PromptTokenizer 批量编码
- 0.2.0 移除：InferenceChunk::Token（改 Tokens）、util 模块、StreamDecoder 等；文末附 0.1→0.2 迁移对照表（CHANGELOG.md:186-238）
