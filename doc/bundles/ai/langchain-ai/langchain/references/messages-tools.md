---
type: Reference
title: 消息与工具源码信源
description: BaseMessage 体系、AIMessage/ToolCall、ToolMessage、BaseTool/StructuredTool/@tool 的源码溯源
tags: [langchain, messages, tools, source]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: src-msg-base
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/messages/base.py
    title: messages/base.py
  - id: src-msg-ai
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/messages/ai.py
    title: messages/ai.py
  - id: src-msg-tool
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/messages/tool.py
    title: messages/tool.py
  - id: src-msg-content
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/messages/content.py
    title: messages/content.py
  - id: src-tools-base
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/tools/base.py
    title: tools/base.py
  - id: src-tools-structured
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/tools/structured.py
    title: tools/structured.py
  - id: src-tools-convert
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/tools/convert.py
    title: tools/convert.py
---

# 消息与工具源码信源

本信源登记消息类型体系和工具抽象的源码位置。

## 消息基类（messages/base.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `TextAccessor(str)` | 47 | 同时支持属性/方法访问的字符串子类 |
| `TextAccessor.__call__` | 68 | `.text()` 已弃用，2.0.0 移除 |
| `BaseMessage(Serializable)` | 93 | 消息基类 |
| 字段 `content` | 103 | `str \| list[str \| dict]` |
| 字段 `additional_kwargs` | 106 | provider 特定附加数据 |
| 字段 `response_metadata` | 114 | 响应元数据 |
| 字段 `type` | 117 | 消息类型标识 |
| 字段 `name` | 125 | 可选名称 |
| 字段 `id` | 135 | 可选 ID（数字自动转字符串） |
| `is_lc_serializable` | 182 | 返回 `True` |
| `get_lc_namespace` | 191 | `["langchain","schema","messages"]` |
| `content_blocks` 属性 | 200 | 懒解析为 `ContentBlock` 列表 |
| `text` 属性 | 263 | 返回 `TextAccessor` |
| `__add__` | 294 | 消息相加→ChatPromptTemplate |
| `pretty_repr` / `pretty_print` | 309 / 344 | 可读表示 |
| `BaseMessageChunk(BaseMessage)` | 409 | 流式分块基类 |
| `BaseMessageChunk.__add__` | 412 | 抽象合并方法 |

## AI 消息（messages/ai.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `InputTokenDetails(TypedDict)` | 38 | 输入 token 细分 |
| `OutputTokenDetails(TypedDict)` | 74 | 输出 token 细分 |
| `UsageMetadata(TypedDict)` | 104 | token 用量标准结构 |
| `UsageMetadata.input_tokens` | 138 | 输入 token 数 |
| `UsageMetadata.output_tokens` | 141 | 输出 token 数 |
| `UsageMetadata.total_tokens` | 144 | 总 token 数 |
| `AIMessage(BaseMessage)` | 160 | AI 响应消息 |
| 字段 `tool_calls` | 170 | `list[ToolCall]` |
| 字段 `invalid_tool_calls` | 173 | 解析失败的工具调用 |
| 字段 `usage_metadata` | 176 | token 用量 |
| 字段 `type` | 182 | `Literal["ai"] = "ai"` |
| `lc_attributes` | 231 | 含 tool_calls/invalid_tool_calls |
| `content_blocks` | 243 | 支持 provider 翻译器 |
| `AIMessageChunk` | 418 | AI 消息流式分块 |
| `AIMessageChunk.init_tool_calls` | 509 | 补全 tool_calls 字段 |

## Tool 消息与 ToolCall（messages/tool.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `ToolOutputMixin` | 16 | 工具可直接返回的 mixin |
| `ToolMessage(BaseMessage, ToolOutputMixin)` | 26 | 工具结果消息 |
| 字段 `tool_call_id` | 67 | 关联工具调用 ID |
| 字段 `type` | 70 | `Literal["tool"] = "tool"` |
| 字段 `artifact` | 73 | 不发给模型的执行产物 |
| 字段 `status` | 81 | `Literal["success","error"]` |
| `coerce_args` 验证器 | 92 | content/tool_call_id 类型强制 |
| `ToolMessageChunk` | 174 | 工具消息流式分块 |
| `ToolCall(TypedDict)` | 206 | 工具调用请求 |
| `ToolCall.name` | 225 | 工具名 |
| `ToolCall.args` | 228 | 参数字典 |
| `ToolCall.id` | 231 | 调用 ID |
| `ToolCall.type` | 238 | 可选 `"tool_call"` |
| `tool_call()` 工厂函数 | 242 | 创建并校验 ToolCall |
| `ToolCallChunk(TypedDict)` | 261 | 流式工具调用分块 |

## ContentBlock 类型（messages/content.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `TextContentBlock` | 207 | 文本块 |
| `ToolCall`（content 模块） | 247 | 内容块形式的工具调用 |
| `InvalidToolCall` | 336 | 无效工具调用 |
| `ReasoningContentBlock` | 456 | 推理内容块 |
| `ImageContentBlock` | 498 | 图片块 |
| `DataContentBlock` 别名 | 831 | 图/视/音/文件/纯文本联合 |
| `ToolContentBlock` 别名 | 840 | 工具相关块联合 |
| `ContentBlock` 联合 | 844 | 全部内容块联合 |
| `KNOWN_BLOCK_TYPES` | 855 | 已知块类型集合 |

## 工具抽象（tools/base.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `SchemaAnnotationError(TypeError)` | 89 | schema 注解错误 |
| `ToolException(Exception)` | 371 | 工具执行异常 |
| `BaseTool(RunnableSerializable[...])` | 433 | 工具基类 |
| 字段 `name` | 474 | 唯一工具名 |
| 字段 `description` | 477 | 工具描述 |
| 字段 `args_schema` | 483 | Pydantic 输入 schema |
| 字段 `return_direct` | 495 | 是否直接返回 |
| 字段 `callbacks` | 505 | 回调（exclude） |
| 字段 `tags` / `metadata` | 508 / 518 | 标签/元数据 |
| 字段 `handle_tool_error` | 527 | 异常处理策略 |
| 字段 `handle_validation_error` | 542 | 校验异常处理 |
| 字段 `response_format` | 547 | `"content"` / `"content_and_artifact"` |
| 字段 `extras` | 555 | provider 特定扩展字段 |
| `is_single_input` | 598 | 是否单输入 |
| `args` | 608 | JSON schema 字典 |
| `tool_call_schema` | 677 | 工具调用 schema |
| `get_input_schema` | 741 | 输入 schema |
| `invoke` | 757 | 工具执行入口 |
| `_parse_input` | 778 | 输入解析 |
| `_run`（抽象） | 909 | 同步执行逻辑 |
| `run` | 1009 | 直接调用 |
| `InjectedToolArg` | 1726 | 注入参数标记 |
| `InjectedToolCallId` | 1756 | 注入 tool_call_id |
| `BaseToolkit(BaseModel, ABC)` | 1935 | 工具包基类 |
| `BaseToolkit.get_tools`（抽象） | 1943 | 返回工具列表 |

## StructuredTool 与 @tool（tools/structured.py、tools/convert.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `StructuredTool(BaseTool)` | structured.py:40 | 多输入工具 |
| 字段 `func` | structured.py:50 | 同步函数 |
| 字段 `coroutine` | structured.py:53 | 异步函数 |
| `StructuredTool._run` | structured.py:74 | 调用 self.func |
| `StructuredTool.from_function` | structured.py:133 | 从函数构造 |
| `tool()` 函数 | convert.py:77 | 装饰器/工厂 |
| `tool` overload（无参装饰器） | convert.py:18 | `@tool()` |
| `tool` overload（name+runnable） | convert.py:32 | `tool("name", runnable)` |
| `tool` overload（直接 callable） | convert.py:48 | `@tool` |
| `tool` overload（name 装饰器工厂） | convert.py:63 | `@tool("name")` |

## 相关事实

- F-lc-022 ~ F-lc-032（消息体系）
- F-lc-033 ~ F-lc-040（工具体系）
