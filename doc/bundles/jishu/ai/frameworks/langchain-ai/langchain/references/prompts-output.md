---
type: Reference
title: 提示词、模型与输出解析源码信源
description: BasePromptTemplate/PromptTemplate、BaseLanguageModel/BaseChatModel、BaseOutputParser、Generation/ChatGeneration、Document、Embeddings 的源码溯源
tags: [langchain, prompts, language-models, output-parsers, source]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: src-prompts-base
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/prompts/base.py
    title: prompts/base.py
  - id: src-prompts-prompt
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/prompts/prompt.py
    title: prompts/prompt.py
  - id: src-prompts-string
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/prompts/string.py
    title: prompts/string.py
  - id: src-prompts-chat
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/prompts/chat.py
    title: prompts/chat.py
  - id: src-lm-base
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/language_models/base.py
    title: language_models/base.py
  - id: src-lm-chat
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/language_models/chat_models.py
    title: language_models/chat_models.py
  - id: src-parsers
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/output_parsers/base.py
    title: output_parsers/base.py
  - id: src-generation
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/outputs/generation.py
    title: outputs/generation.py
  - id: src-chat-generation
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/outputs/chat_generation.py
    title: outputs/chat_generation.py
  - id: src-documents
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/documents/base.py
    title: documents/base.py
  - id: src-embeddings
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/embeddings/embeddings.py
    title: embeddings/embeddings.py
  - id: src-prompt-values
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/prompt_values.py
    title: prompt_values.py
---

# 提示词、模型与输出解析源码信源

## PromptValue（prompt_values.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `PromptValue(Serializable, ABC)` | 24 | 提示词值抽象基类 |
| `to_string`（抽象） | 46 | 转为字符串 |
| `to_messages`（抽象） | 50 | 转为消息列表 |
| `StringPromptValue(PromptValue)` | 54 | 字符串提示词值 |
| `ChatPromptValue(PromptValue)` | 80 | 聊天提示词值 |
| `ChatPromptValueConcrete` | 152 | 具体聊天提示词值 |

## 提示词模板（prompts/）

| 符号 | 行号 | 说明 |
|---|---|---|
| `BasePromptTemplate(RunnableSerializable[dict, PromptValue], ABC, Generic)` | base.py:38 | 提示词模板基类 |
| 字段 `input_variables` | base.py:43 | 必填变量名列表 |
| 字段 `optional_variables` | base.py:48 | 可选变量 |
| 字段 `input_types` | base.py:55 | 变量类型映射 |
| 字段 `output_parser` | base.py:64 | 输出解析器 |
| 字段 `partial_variables` | base.py:67 | 部分变量 |
| `validate_variable_names` | base.py:81 | 禁止 `stop` 变量名、禁止重叠 |
| `get_lc_namespace` | base.py:109 | `["langchain","schema","prompt_template"]` |
| `OutputType` | base.py:135 | `StringPromptValue \| ChatPromptValueConcrete` |
| `get_input_schema` | base.py:140 | 从 input_variables 构造 |
| `invoke` | base.py:210 | 执行模板返回 PromptValue |
| `format_prompt`（抽象） | base.py:268 | 格式化为 PromptValue |
| `partial` | base.py:289 | 部分应用变量 |
| `format`（抽象） | base.py:317 | 格式化为输出类型 |
| `save` | base.py:387 | 保存到文件 |
| `StringPromptTemplate(BasePromptTemplate[str], ABC)` | string.py:328 | 字符串模板基类 |
| `StringPromptTemplate.format_prompt` | string.py:340 | 返回 StringPromptValue |
| `StringPromptTemplate.format`（抽象） | string.py:364 | 返回 str |
| `PromptTemplate(StringPromptTemplate)` | prompt.py:24 | 具体字符串模板 |
| 字段 `template` | prompt.py:77 | 模板字符串 |
| 字段 `template_format` | prompt.py:80 | `"f-string"`/`"mustache"`/`"jinja2"` |
| 字段 `validate_template` | prompt.py:86 | 是否校验模板 |
| `pre_init_validation` | prompt.py:91 | 模板与变量一致性校验 |
| `PromptTemplate.format` | prompt.py:191 | 返回 str |
| `PromptTemplate.from_examples` | prompt.py:204 | 从示例构造 |
| `PromptTemplate.from_file` | prompt.py:236 | 从文件构造 |
| `PromptTemplate.from_template` | prompt.py:257 | 从模板字符串构造 |
| `MessagesPlaceholder` | chat.py:53 | 消息占位符 |
| `ChatMessagePromptTemplate` | chat.py:354 | 聊天消息模板 |
| `HumanMessagePromptTemplate` | chat.py:668 | 人类消息模板 |
| `AIMessagePromptTemplate` | chat.py:677 | AI 消息模板 |
| `SystemMessagePromptTemplate` | chat.py:686 | 系统消息模板 |
| `ChatPromptTemplate` | chat.py:794 | 聊天提示词模板 |

## 语言模型（language_models/）

| 符号 | 行号 | 说明 |
|---|---|---|
| `LanguageModelInput` 类型别名 | base.py:140 | `PromptValue \| str \| Sequence[MessageLikeRepresentation]` |
| `LanguageModelOutput` | base.py:143 | `BaseMessage \| str` |
| `BaseLanguageModel(RunnableSerializable, ABC)` | base.py:181 | 语言模型基类 |
| 字段 `cache` | base.py:190 | 缓存配置 |
| 字段 `verbose` | base.py:201 | 详细模式 |
| 字段 `callbacks`/`tags`/`metadata` | base.py:204/207/210 | 追踪配置 |
| `model_post_init` | base.py:222 | 注入 lc_versions |
| `_add_version` | base.py:253 | 累积包版本到 metadata |
| `generate_prompt`（抽象） | base.py:318 | 从 PromptValue 生成 |
| `with_structured_output` | base.py:405 | 结构化输出 |
| `get_num_tokens` | base.py:448 | token 计数 |
| `BaseChatModel(BaseLanguageModel[AIMessage], ABC)` | chat_models.py:284 | 聊天模型基类 |
| 字段 `rate_limiter` | chat_models.py:334 | 限流器 |
| 字段 `disable_streaming` | chat_models.py:337 | 禁用流式 |
| 字段 `output_version` | chat_models.py:355 | 输出格式版本 |
| `OutputType` | chat_models.py:457 | `AIMessage` |
| `invoke` | chat_models.py:475 | 同步调用返回 AIMessage |
| `stream` | chat_models.py:727 | 流式输出 |
| `generate` | chat_models.py:1592 | 批量生成 |
| `generate_prompt` | chat_models.py:1869 | 从 PromptValue 生成 |
| `_generate`（抽象） | chat_models.py:2209 | 核心生成逻辑 |
| `_stream` | chat_models.py:2255 | 核心流式逻辑 |
| `_llm_type`（抽象属性） | chat_models.py:2331 | 模型类型标识 |
| `bind` | chat_models.py:2355 | 返回 `_ChatModelBinding` |
| `bind_tools` | chat_models.py:2366 | 绑定工具（基类 NotImplementedError） |
| `with_structured_output` | chat_models.py:2385 | 结构化输出 |
| `_ChatModelBinding` | chat_models.py:2568 | 聊天模型绑定包装 |
| `SimpleChatModel(BaseChatModel)` | chat_models.py:2657 | 简化模型基类 |
| `SimpleChatModel._call`（抽象） | chat_models.py:2679 | 只需实现字符串入字符串出 |

## 输出解析器（output_parsers/base.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `BaseLLMOutputParser(ABC, Generic[T])` | 34 | LLM 输出解析器基类 |
| `parse_result`（抽象） | 38 | 从 Generation 列表解析 |
| `BaseGenerationOutputParser(...)` | 74 | 单 Generation 解析器 |
| `BaseOutputParser(BaseLLMOutputParser[T], RunnableSerializable)` | 140 | 输出解析器主基类 |
| `InputType` | 177 | `str \| AnyMessage` |
| `OutputType` | 183 | 从泛型推断 `type[T]` |
| `invoke` | 204 | 包装为 Generation 调用 parse_result |
| `parse_result` | 250 | 取首个 Generation 调用 parse |
| `parse`（抽象） | 271 | 从字符串解析 |
| `parse_with_prompt` | 315 | 带 prompt 的解析 |
| `get_format_instructions` | 334 | 格式指令（默认空串） |
| `_type` | 339 | 解析器类型标识 |

## Generation 输出（outputs/）

| 符号 | 行号 | 说明 |
|---|---|---|
| `Generation(Serializable)` | generation.py:11 | 文本生成结果 |
| 字段 `text` | generation.py:25 | 生成文本 |
| 字段 `generation_info` | generation.py:28 | provider 原始响应 |
| 字段 `type` | generation.py:34 | `"Generation"` |
| `GenerationChunk(Generation)` | generation.py:55 | 可拼接分块 |
| `ChatGeneration(Generation)` | chat_generation.py:17 | 聊天生成结果 |
| 字段 `message` | chat_generation.py:37 | `BaseMessage` |
| 字段 `type` | chat_generation.py:41 | `"ChatGeneration"` |
| `set_text` 验证器 | chat_generation.py:45 | 从 message 同步 text |
| `ChatGenerationChunk(ChatGeneration)` | chat_generation.py:87 | 聊天分块 |
| `merge_chat_generation_chunks` | chat_generation.py:140 | 合并分块列表 |

## Document 与 Embeddings

| 符号 | 行号 | 说明 |
|---|---|---|
| `BaseMedia(Serializable)` | documents/base.py:34 | 媒体基类 |
| `Blob(BaseMedia)` | documents/base.py:59 | 二进制大对象 |
| `Blob.as_string`/`as_bytes`/`as_bytes_io` | 158/176/195 | 读取方式 |
| `Blob.from_path`/`from_data` | 214/251 | 工厂方法 |
| `Document(BaseMedia)` | documents/base.py:288 | 文本文档 |
| 字段 `page_content` | documents/base.py:306 | 文本内容 |
| 字段 `type` | documents/base.py:309 | `"Document"` |
| `Document.__init__` | documents/base.py:311 | page_content 位置参数 |
| `is_lc_serializable` | documents/base.py:318 | `True` |
| `get_lc_namespace` | documents/base.py:323 | `["langchain","schema","document"]` |
| `Embeddings(ABC)` | embeddings/embeddings.py:8 | 嵌入模型接口 |
| `embed_documents`（抽象） | embeddings.py:37 | 批量文档嵌入 |
| `embed_query`（抽象） | embeddings.py:48 | 查询嵌入 |
| `aembed_documents` | embeddings.py:58 | 异步（默认线程池） |
| `aembed_query` | embeddings.py:69 | 异步查询 |

## 相关事实

- F-lc-041 ~ F-lc-045（Prompts）
- F-lc-046 ~ F-lc-050（Language Models）
- F-lc-056 ~ F-lc-058（Output Parsers）
- F-lc-059、F-lc-060（Documents）
- F-lc-066（Embeddings）
- F-lc-067、F-lc-068（Generation）
- F-lc-069（PromptValue）
