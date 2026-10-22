---
type: reference
scope: deepseek-recipe
name: Python 绑定 API 清单
version: "0.2.0"
source: deepseek-recipe-python/src/lib.rs, python/deepseek_recipe/__init__.py
description: deepseek_recipe Python 包导出类、异常与构造方法速查
---

# Python 绑定 API 清单

Python 包以 `deepseek_recipe` 导入（`pip install deepseek-recipe`，Python 3.10+，cp310-abi3 稳定 ABI——一个 wheel 跨所有 CPython 3.10+）。`#[pymodule] _native` 注册约 55 个类 + 3 个异常类 + `__version__`，`python/deepseek_recipe/__init__.py` 重新导出全部名称（另有 `_native.pyi` 类型存根）。

## 一、请求与转换

| 类 | 用途 |
|---|---|
| `ChatCompletionRequest` / `ResponsesRequest` / `MessagesRequest` | 三协议请求（dict 构造 + `.convert(ConversionOptions)`） |
| `ConversionOptions` | 转换配置（模型别名注册、思考模式默认等） |
| `ModelVersion` | 模型版本（V4-Pro / V4.1-Flash） |
| `ConversationRequest` | 归一请求（`resolve_max_tokens`） |
| `InferenceOptions` / `OutputConstraint` | 推理选项与输出约束 |

## 二、编码与分词

| 类 | 用途 |
|---|---|
| `DeepseekV4Encoding` / `DeepseekV41Encoding` | 两代 prompt 渲染与编码（`render_conversation` / `encode`；`with_tokenizer` 附加 tokenizer） |
| `Tokenizer` | tokenizer 封装：`from_file` / `from_str` / `from_pretrained`（HF Hub，可指定 revision/token） |

## 三、流式处理

| 类 | 用途 |
|---|---|
| `StreamProcessor` | `(generator, parsing_options, tokenizer?)` 构造；`push(chunk)` / `finish()` / `close()` |
| `InferenceChunk` | `InferenceChunk.tokens(ids)` / `.text(s)` / `.finish(reason)` / `.ready(...)` 工厂方法 |
| `InferenceFinishReason` | Stop / StopSequence / EndOfStream 等枚举 |
| `ParsingOptions` | 解析配置 |

## 四、图片

| 类 | 用途 |
|---|---|
| `OpenCvImagePreprocessor` | OpenCV 预处理 |
| `ReqwestImageFetcher` | 图片拉取（`with_destination_filter` 安装 SSRF 防护） |
| `ImageResolver` | fetch + preprocess 组合 |

## 五、协议响应类型

三协议的 `*ChunkGenerator` / `*Response` / `*StreamEvent`（Chat Completions、Responses、Messages 各一组），以及消息/工具类型：`Message` / `UserMessage` / `AssistantMessage` / `ToolCall` / `ToolDefinition` 等。

## 六、异常

| 异常 | 触发 |
|---|---|
| `ConversionError` | 转换/校验失败（含 `resolve_max_tokens` 超限；文案与 DeepSeek API 一致） |
| `ImageError` | 图片拉取/处理失败（Display 即 400 响应体） |
| `CalcResizeError` | 图片尺寸计算失败 |

## 七、行为约定

- 未附加 tokenizer 时：`encode` 抛 `RuntimeError`；`tokens` chunk 使 processor 抛 `RuntimeError` 并关闭；
- `encode` 失败抛 `RuntimeError`（Rust 侧 `EncodingError`）；`resolve_max_tokens` 超限抛 `ConversionError`；
- chunk 的 `to_json()` 输出协议 JSON；processor 处理完 `finish()` 后应调用 `close()` 释放资源。
