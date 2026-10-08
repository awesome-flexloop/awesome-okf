---
type: concept
title: 提示词系统
description: BasePromptTemplate、PromptTemplate、ChatPromptTemplate 与 PromptValue 的模板格式化、变量校验和部分应用机制
tags: [langchain, prompts, prompt-template, chat-prompt]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-po
    resource: /references/prompts-output.md
    title: 提示词、模型与输出解析源码信源
---

# 提示词系统

提示词模板（Prompt Template）负责将用户变量格式化为模型可接受的输入。langchain-core 在 `prompts/` 目录定义了以 `BasePromptTemplate` 为根的模板体系。所有提示词模板都是 `RunnableSerializable[dict[str, Any], PromptValue]`（`prompts/base.py:38`），即输入字典、输出 `PromptValue`，因此天然支持 `invoke`/`ainvoke`/`batch`/`stream` 和管道组合。

## 继承体系

```
BasePromptTemplate(RunnableSerializable[dict, PromptValue], ABC, Generic)  base.py:38
├── StringPromptTemplate(BasePromptTemplate[str], ABC)                    string.py:328
│   └── PromptTemplate(StringPromptTemplate)                              prompt.py:24
└── BaseChatPromptTemplate / ChatPromptTemplate                          chat.py:794
    ├── SystemMessagePromptTemplate                                      chat.py:686
    ├── HumanMessagePromptTemplate                                       chat.py:668
    ├── AIMessagePromptTemplate                                          chat.py:677
    ├── ChatMessagePromptTemplate                                        chat.py:354
    └── MessagesPlaceholder                                              chat.py:53
```

## BasePromptTemplate

`BasePromptTemplate`（`prompts/base.py:38`）是泛型抽象基类，`Generic[FormatOutputType]` 表示 `format` 方法的返回类型（字符串模板为 `str`）。

### 核心字段

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `input_variables` | `list[str]` | 43 | 必填变量名列表 |
| `optional_variables` | `list[str]` | 48 | 可选变量（自动推断） |
| `input_types` | `dict[str, Any]` | 55 | 变量类型映射，默认全为 str |
| `output_parser` | `BaseOutputParser \| None` | 64 | 关联的输出解析器 |
| `partial_variables` | `Mapping[str, Any]` | 67 | 部分应用的变量 |
| `metadata` | `dict \| None` | 74 | 追踪元数据 |
| `tags` | `list[str] \| None` | 77 | 追踪标签 |

### 变量名校验

`validate_variable_names`（第81行，`@model_validator(mode="after")`）强制：
- `input_variables` 和 `partial_variables` 都**不能**包含名为 `"stop"` 的变量（内部保留）。
- `input_variables` 与 `partial_variables` 不能有重叠。

违反时抛出带 `ErrorCode.INVALID_PROMPT_INPUT` 的 `ValueError`。

### 核心方法

| 方法 | 行号 | 说明 |
|---|---|---|
| `get_input_schema(config)` | 140 | 从 input_variables/optional_variables 构造 Pydantic 模型 `PromptInput` |
| `invoke(input, config)` | 210 | 执行模板，返回 `PromptValue` |
| `format_prompt(**kwargs)`（抽象） | 268 | 格式化为 `PromptValue` |
| `partial(**kwargs)` | 289 | 部分应用变量，返回新模板 |
| `format(**kwargs)`（抽象） | 317 | 格式化为 `FormatOutputType` |
| `save(file_path)` | 387 | 保存到文件 |

`OutputType` 属性（第135行）返回 `StringPromptValue | ChatPromptValueConcrete`。`get_lc_namespace` 返回 `["langchain", "schema", "prompt_template"]`，`is_lc_serializable` 返回 `True`。

## StringPromptTemplate 与 PromptTemplate

`StringPromptTemplate`（`prompts/string.py:328`）是字符串输出模板的抽象基类：
- `format_prompt(**kwargs)`（第340行）调用 `format` 后包装为 `StringPromptValue`。
- `format(**kwargs) -> str` 是抽象方法（第364行）。

`PromptTemplate`（`prompts/prompt.py:24`）是最常用的具体实现：

| 字段 | 类型/默认 | 行号 | 说明 |
|---|---|---|---|
| `template` | `str` | 77 | 模板字符串（必填） |
| `template_format` | `"f-string"` | 80 | 模板语法：`"f-string"`/`"mustache"`/`"jinja2"` |
| `validate_template` | `False` | 86 | 是否校验模板 |

`pre_init_validation`（第91行，`@model_validator(mode="before")`）检查模板与 input_variables 的一致性。`format`（第191行）根据 `template_format` 渲染模板。

工厂方法：
- `from_template(template, **kwargs)`（第257行）：从模板字符串构造。
- `from_file(template_file, ...)`（第236行）：从文件构造。
- `from_examples(examples, suffix, input_variables, ...)`（第204行）：从 few-shot 示例构造。

### 安全提示

`PromptTemplate` 文档明确警告（第33-45行）：不要接受不受信任来源的 Jinja2 模板，可能导致任意 Python 代码执行。推荐使用 `template_format='f-string'`。Jinja2 默认使用沙箱环境，但仅为 best-effort。

## ChatPromptTemplate

`ChatPromptTemplate`（`prompts/chat.py:794`）由一系列消息模板组成，每个消息模板可以是：
- `SystemMessagePromptTemplate`（第686行）
- `HumanMessagePromptTemplate`（第668行）
- `AIMessagePromptTemplate`（第677行）
- `ChatMessagePromptTemplate`（第354行，带任意 role）
- `MessagesPlaceholder`（第53行，消息列表占位符）

`ChatPromptTemplate` 格式化后产生 `ChatPromptValue`，其 `to_messages()` 返回消息列表。常用工厂方法包括 `from_template`、`from_messages`、`from_messages` 接收 `("system", "...")`、`("human", "...")` 等元组列表。

`MessagesPlaceholder`（第53行）用于在特定位置插入整个消息列表（如对话历史），可选 `optional=True`。

## PromptValue

`PromptValue`（`prompt_values.py:24`）是模板格式化的结果，是 `Serializable` 抽象基类：

| 方法 | 行号 | 说明 |
|---|---|---|
| `to_string()`（抽象） | 46 | 转为字符串（给传统 LLM） |
| `to_messages()`（抽象） | 50 | 转为消息列表（给聊天模型） |

具体子类：
- **`StringPromptValue`**（第54行）：持有 `text: str`，`to_string` 返回文本，`to_messages` 返回 `[HumanMessage(content=text)]`。
- **`ChatPromptValue`**（第80行）：持有消息列表，`to_messages` 返回该列表。
- **`ChatPromptValueConcrete`**（第152行）：`ChatPromptValue` 的具体可序列化版本。

`PromptValue` 的价值在于同一模板结果既可喂给传统文本 LLM（`to_string`），也可喂给聊天模型（`to_messages`），是两种模型接口的桥梁。

## partial 部分应用

`partial(**kwargs)`（`prompts/base.py:289`）将部分变量预先填入 `partial_variables`，返回新模板实例。这在某些变量需要延迟获取（如动态日期、回调注入的 user_id）时很有用——模板先部分应用已知变量，调用时只需提供剩余变量。

## 代码示例

```python
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder

# 1. 字符串模板
prompt = PromptTemplate.from_template("讲一个关于 {topic} 的{length}笑话")
prompt.format(topic="程序员", length="短")
# '讲一个关于 程序员 的短笑话'

# 2. 作为 Runnable 调用，返回 PromptValue
pv = prompt.invoke({"topic": "程序员", "length": "短"})
pv.to_string()
pv.to_messages()  # [HumanMessage(content='...')]

# 3. 聊天模板
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{role}专家"),
    ("human", "{question}"),
    MessagesPlaceholder("history", optional=True),
])
chat_prompt.format_messages(role="Python", question="什么是装饰器？")

# 4. partial 部分应用
partial = prompt.partial(length="短")
partial.format(topic="程序员")

# 5. input_schema 自省
schema = prompt.input_schema
schema.model_json_schema()
```

## 相关概念

- 总览 —— 提示词在能力层中的位置
- Runnable 协议 —— BasePromptTemplate 是 RunnableSerializable
- 聊天模型 —— PromptValue 是模型的输入
- 输出解析器 —— output_parser 字段关联解析器
- 消息类型 —— ChatPromptValue 产生消息列表
