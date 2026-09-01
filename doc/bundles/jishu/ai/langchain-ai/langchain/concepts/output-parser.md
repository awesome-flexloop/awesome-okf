---
type: concept
title: 输出解析器
description: BaseOutputParser 将模型输出解析为结构化数据，parse/parse_result/invoke 的协作与 Generation 包装机制
tags: [langchain, output-parser, parsing, base-output-parser]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-po
    resource: /references/prompts-output.md
    title: 提示词、模型与输出解析源码信源
---

# 输出解析器

输出解析器（Output Parser）负责将语言模型的文本或消息输出转换为结构化数据。langchain-core 在 `output_parsers/base.py` 定义了以 `BaseOutputParser` 为根的解析器体系。解析器本身也是 `RunnableSerializable[LanguageModelOutput, T]`（`output_parsers/base.py:140`），因此可以作为 LCEL 链的最后一环，通过 `|` 与模型组合。

## 类层级

```
BaseLLMOutputParser(ABC, Generic[T])                          base.py:34
│   └── parse_result(result, *, partial=False) -> T (抽象)    base.py:38
│
├── BaseGenerationOutputParser(BaseLLMOutputParser[T],
│       RunnableSerializable[Generation, T])                  base.py:74
│       输入为单个 Generation
│
└── BaseOutputParser(BaseLLMOutputParser[T],
        RunnableSerializable[LanguageModelOutput, T])         base.py:140
    ├── parse(text) -> T（抽象）                              base.py:271
    ├── parse_result(result, *, partial=False) -> T           base.py:250
    ├── parse_with_prompt(completion, prompt) -> T            base.py:315
    └── get_format_instructions() -> str                      base.py:334
```

## BaseLLMOutputParser

`BaseLLMOutputParser`（第34行）是最顶层的抽象，定义了唯一的抽象方法：

```python
@abstractmethod
def parse_result(self, result: list[Generation], *, partial: bool = False) -> T:
```

它接收一个 `Generation` 列表（模型可能返回多个候选），解析为目标类型 `T`。`partial=True` 用于流式场景下的增量解析。

## BaseOutputParser

`BaseOutputParser`（第140行）是用户最常继承的基类，输入类型为 `LanguageModelOutput`（即 `str | BaseMessage`）。

### 类型属性

- `InputType`（第177行）返回 `str | AnyMessage`：解析器既接受纯字符串，也接受消息对象。
- `OutputType`（第183行）从类的泛型参数 `T` 推断（通过 Pydantic `__pydantic_generic_metadata__`）。如果无法推断则抛出 `TypeError`，提示 override `OutputType`。

### invoke 方法

`invoke(self, input: str | BaseMessage, config=None, **kwargs) -> T`（第204行）是 Runnable 接口的实现，它将输入统一包装为 Generation 列表后调用 `parse_result`：

```python
if isinstance(input, BaseMessage):
    return self._call_with_config(
        lambda inner: self.parse_result([ChatGeneration(message=inner)]),
        input, config, run_type="parser",
    )
return self._call_with_config(
    lambda inner: self.parse_result([Generation(text=inner)]),
    input, config, run_type="parser",
)
```

关键点：
- 消息输入包装为 `ChatGeneration(message=...)`。
- 字符串输入包装为 `Generation(text=...)`。
- 通过 `_call_with_config` 执行，`run_type="parser"`，自动获得回调、追踪、配置传播。

### parse_result 方法

`parse_result`（第250行）默认实现取列表中**第一个** Generation（最高概率候选），调用 `parse`：

```python
def parse_result(self, result, *, partial=False):
    return self.parse(result[0].text)
```

子类可 override 以访问完整候选列表或 `generation_info`。

### parse 方法

`parse(self, text: str) -> T`（第271行）是抽象方法，子类必须实现——将纯文本解析为目标类型。

### 其他方法

| 方法 | 行号 | 说明 |
|---|---|---|
| `parse_with_prompt(completion, prompt)` | 315 | 带 prompt 的解析，默认委托 `parse_result` |
| `get_format_instructions()` | 334 | 返回告诉模型如何格式化输出的指令字符串，默认返回空串 |
| `_type`（属性） | 339 | 解析器类型标识，默认抛 `NotImplementedError` |
| `ainvoke` | 227 | 异步 invoke，默认在线程池跑同步版本 |

## 内置解析器

`output_parsers/` 目录提供了常用实现：

| 文件 | 类 | 用途 |
|---|---|---|
| `string.py` | `StrOutputParser` | 提取消息文本（最常用） |
| `json.py` | `JsonOutputParser` | 解析 JSON 输出 |
| `pydantic.py` | `PydanticOutputParser` | 解析为 Pydantic 模型 |
| `list.py` | `CommaSeparatedListOutputParser` | 逗号分隔列表 |
| `xml.py` | `XMLOutputParser` | 解析 XML |
| `transform.py` | `BaseTransformOutputParser` | 支持流式增量解析 |
| `openai_tools.py` | `JsonOutputKeyToolsParser` 等 | 解析 OpenAI tool calling |
| `openai_functions.py` | — | 解析 OpenAI function calling |
| `format_instructions.py` | — | 格式指令工具 |

其中 `StrOutputParser` 极其常用——它从 `AIMessage` 中提取 `.text`，是 `prompt | model | StrOutputParser()` 链的标准收尾。

## 解析器在链中的位置

由于解析器是 Runnable，典型的 LCEL 链结构为：

```python
chain = prompt | model | parser
```

1. `prompt` 接收字典，输出 `PromptValue`。
2. `model` 接收 `PromptValue`/消息，输出 `AIMessage`。
3. `parser` 接收 `AIMessage`（或 str），输出结构化类型 `T`。

整条链的输出类型即解析器的泛型 `T`。解析器还可以通过 `get_format_instructions()` 向提示词注入格式要求，通常由用户手动拼入 prompt 或通过 `partial` 注入。

## 自定义解析器

继承 `BaseOutputParser[T]` 并实现 `parse` 即可：

```python
from langchain_core.output_parsers import BaseOutputParser

class BooleanOutputParser(BaseOutputParser[bool]):
    true_val: str = "YES"
    false_val: str = "NO"

    def parse(self, text: str) -> bool:
        cleaned = text.strip().upper()
        if cleaned not in (self.true_val.upper(), self.false_val.upper()):
            raise ValueError(f"Expected {self.true_val} or {self.false_val}, got {cleaned}")
        return cleaned == self.true_val.upper()

    @property
    def _type(self) -> str:
        return "boolean"
```

如需流式增量解析，继承 `BaseTransformOutputParser` 并实现 `parse_result` 处理 `partial=True`。

## 代码示例

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# 1. StrOutputParser —— 提取文本
parser = StrOutputParser()
parser.invoke("hello")           # "hello"
from langchain_core.messages import AIMessage
parser.invoke(AIMessage(content="hi"))  # "hi"

# 2. 在链中使用
chain = prompt | model | StrOutputParser()
text = chain.invoke({"question": "..."})

# 3. JsonOutputParser
json_parser = JsonOutputParser()
data = json_parser.invoke('{"name": "张三", "age": 30}')
# {"name": "张三", "age": 30}

# 4. 解析器也是 Runnable，支持 ainvoke/batch
results = parser.batch(["a", "b", "c"])
```

## 相关概念

- 总览 —— 输出解析器在能力层中的位置
- Runnable 协议 —— BaseOutputParser 是 RunnableSerializable
- 聊天模型 —— 模型输出 AIMessage 给解析器
- 提示词系统 —— output_parser 字段与 get_format_instructions
