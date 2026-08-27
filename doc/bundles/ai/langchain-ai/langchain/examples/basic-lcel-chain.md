---
type: example
title: LCEL 基础链
description: 使用 PromptTemplate、FakeListChatModel 与 StrOutputParser 构建第一条 LCEL 链，演示 invoke/batch/stream
tags: [langchain, lcel, chain, prompt, parser]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-core
    resource: /references/core-abstractions.md
    title: 核心抽象源码信源
  - id: ref-po
    resource: /references/prompts-output.md
    title: 提示词、模型与输出解析源码信源
---

# LCEL 基础链

本示例演示如何用 LangChain Expression Language（LCEL）构建最基础的链：提示词 → 模型 → 输出解析器。示例使用 langchain-core 内置的 `FakeListChatModel`（无需 API key），真实场景替换为 partner 包的模型（如 `ChatOpenAI`）。

## 前置条件

- Python ≥ 3.10
- 已安装 `langchain-core`

## 构建链

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.fake_chat_models import FakeListChatModel

# 1. 定义提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，请用简短的中文回答。"),
    ("human", "{question}"),
])

# 2. 准备模型（这里用 FakeListChatModel 模拟，真实场景换成 ChatOpenAI 等）
model = FakeListChatModel(responses=[
    "装饰器是 Python 的语法糖，用于在不修改原函数代码的情况下扩展其功能。",
    "闭包是指能够访问自由变量的函数，即使外部函数已经返回。",
])

# 3. 输出解析器提取文本
parser = StrOutputParser()

# 4. 用 | 组合成链（RunnableSequence）
chain = prompt | model | parser
```

`prompt`、`model`、`parser` 都是 `Runnable`，`|` 构造 `RunnableSequence`，整条链自动支持 `invoke`/`ainvoke`/`batch`/`stream`。

## invoke 单次调用

```python
result = chain.invoke({"role": "Python 专家", "question": "什么是装饰器？"})
print(result)
# 装饰器是 Python 的语法糖，用于在不修改原函数代码的情况下扩展其功能。

result2 = chain.invoke({"role": "Python 专家", "question": "什么是闭包？"})
print(result2)
# 闭包是指能够访问自由变量的函数，即使外部函数已经返回。
```

## batch 批量调用

```python
results = chain.batch([
    {"role": "Python 专家", "question": "什么是装饰器？"},
    {"role": "Python 专家", "question": "什么是闭包？"},
])
for r in results:
    print("-", r)
```

`batch` 默认在线程池中并行执行（`Runnable.batch`，`runnables/base.py:930`）。

## stream 流式输出

```python
for chunk in chain.stream({"role": "Python 专家", "question": "什么是装饰器？"}):
    print(chunk, end="", flush=True)
```

`FakeListChatModel` 实现了 `_stream`（`fake_chat_models.py:95`），会逐字符产出 `AIMessageChunk`，`StrOutputParser` 提取文本块。

## 配置传播

通过 `RunnableConfig` 传入 tags、metadata、callbacks，它们会自动沿链传播：

```python
result = chain.invoke(
    {"role": "Python 专家", "question": "什么是装饰器？"},
    config={
        "tags": ["demo", "basic-chain"],
        "metadata": {"user_id": "u123"},
        "run_name": "python_qa",
        "recursion_limit": 25,
    },
)
```

## 声明式装饰器

链可以叠加 `with_retry`、`with_fallbacks` 等装饰器，每一步返回新的 Runnable，不修改原链：

```python
robust_chain = chain.with_retry(stop_after_attempt=3)
fallback_chain = chain.with_fallbacks([
    ChatPromptTemplate.from_template("出错了，请重试") | model | parser,
])
```

## 异步调用

```python
import asyncio

async def main():
    result = await chain.ainvoke({"role": "Python 专家", "question": "什么是装饰器？"})
    print(result)

    async for chunk in chain.astream({"role": "Python 专家", "question": "什么是装饰器？"}):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

## 要点总结

- 三个 Runnable 通过 `|` 组合为 `RunnableSequence`，类型自动贯通：`dict → PromptValue → AIMessage → str`。
- `StrOutputParser`（`output_parsers/string.py:8`）从 `AIMessage` 提取 `.text`。
- `FakeListChatModel` 继承 `SimpleChatModel`，只需实现 `_call` 返回字符串；它会循环返回 `responses` 列表中的预设回答。
- 真实使用时将 `FakeListChatModel` 替换为 `langchain_openai.ChatOpenAI` 等具体实现，链的其余代码无需改动。

## 相关概念

- Runnable 协议
- 提示词系统
- 聊天模型
- 输出解析器
