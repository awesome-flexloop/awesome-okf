---
type: example
title: "OpenAI 集成：零侵入自动埋点"
description: "使用 openai_wrapper 对 OpenAI Python SDK 进行零侵入自动埋点，自动追踪 Chat Completions 和 Responses API 调用，包含同步、异步、流式、Azure OpenAI 等完整场景。"
tags: [openai, integration, wrapper, auto-instrumentation, streaming, async, azure]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-084
    title: "OpenAI Wrapper"
  - id: examples/openai_chat
    title: "examples/trace/wrapper_openai/sync_openai_chat.py"
---

# OpenAI 集成：零侵入自动埋点

本示例演示如何使用 CozeLoop 的 `openai_wrapper` 对 OpenAI Python SDK 进行零侵入自动埋点。只需一行代码包装客户端，所有后续 Chat Completions 和 Responses API 调用自动被追踪，无需手动创建 Span 或设置标签。

## 前置条件

- Python 3.8+
- 已安装 `cozeloop` 和 `openai`（>=1.0）：
  ```bash
  pip install cozeloop "openai>=1.0"
  ```
- CozeLoop 凭据（Workspace ID + API Token）
- OpenAI API Key

## 基础用法：同步 Chat Completions

```python
import os
import logging
from openai import OpenAI
from cozeloop import new_client
from cozeloop.integration.wrapper import openai_wrapper
from cozeloop.logger import set_log_level
from cozeloop.decorator import observe

# 1. 初始化 CozeLoop 客户端
set_log_level(logging.INFO)
client = new_client()

# 2. 创建 OpenAI 客户端并用 openai_wrapper 包装
openai_client = openai_wrapper(OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
))

# 3. 正常使用——调用自动被追踪
response = openai_client.chat.completions.create(
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "你好，请介绍一下自己。"},
    ],
    model="gpt-4-1106-preview",
    temperature=0.7,
)

print(response.choices[0].message.content)

# 4. 刷新并关闭
client.flush()
client.close()
```

### 自动提取的信息

`openai_wrapper` 自动为每次 `chat.completions.create` 调用创建一个 span_type="model" 的 Span，并自动提取：

| 标签 | 值来源 |
|------|--------|
| `input` | messages 参数序列化为 JSON |
| `output` | 响应的 choices 列表序列化为 JSON |
| `model_provider` | `"openai"`（Azure 为 `"azure"`） |
| `model_name` | model 参数（如 `"gpt-4-1106-preview"`） |
| `input_tokens` | response.usage.prompt_tokens |
| `output_tokens` | response.usage.completion_tokens |
| `call_options` | temperature、max_tokens、top_p、n、stop、frequency_penalty、presence_penalty |
| `start_time_first_resp` | 非流式：finish 时设置；流式：第一个 chunk 到达时设置 |

## 流式调用（Streaming）

流式调用是 LLM 应用的常见模式。`openai_wrapper` 自动处理流式响应：

```python
@observe(name="streaming_chat", span_type="custom")
def chat_stream():
    stream = openai_client.chat.completions.create(
        messages=[
            {"role": "user", "content": "写一首关于春天的短诗"},
        ],
        model="gpt-4",
        stream=True,
        # ⚠️ 重要：流式调用需要设置 include_usage=True，
        # 否则最后一个 chunk 不包含 token 用量统计
        stream_options={"include_usage": True},
    )

    collected_content = []
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            collected_content.append(content)

    print()  # 换行
    return "".join(collected_content)

if __name__ == "__main__":
    set_log_level(logging.INFO)
    client = new_client()
    openai_client = openai_wrapper(OpenAI(api_key=os.environ["OPENAI_API_KEY"]))

    chat_stream()

    client.flush()
    client.close()
```

### 流式 Span 的行为

- Span 在**流开始消费时**创建
- `start_time_first_resp` 在第一个包含 content 的 chunk 到达时自动记录
- Span 在**流被完全消费**（迭代结束）时自动 finish
- 完整响应内容在流结束后聚合并设置到 output 标签
- Token 用量从最后一个 chunk 的 usage 字段提取（需 `stream_options={"include_usage": True}`）

## 异步调用

使用 `AsyncOpenAI` 进行异步调用，同样只需一行包装：

```python
import asyncio
import os
from openai import AsyncOpenAI
from cozeloop import new_client
from cozeloop.integration.wrapper import openai_wrapper

async def async_chat():
    client = new_client()
    async_client = openai_wrapper(AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
    ))

    response = await async_client.chat.completions.create(
        messages=[{"role": "user", "content": "异步调用测试"}],
        model="gpt-4",
    )
    print(response.choices[0].message.content)

    client.flush()
    client.close()

if __name__ == "__main__":
    asyncio.run(async_chat())
```

## Azure OpenAI

`openai_wrapper` 同样支持 Azure OpenAI，自动设置 model_provider 为 "azure"：

```python
from openai import AzureOpenAI
from cozeloop.integration.wrapper import openai_wrapper

azure_client = openai_wrapper(AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
))

response = azure_client.chat.completions.create(
    messages=[{"role": "user", "content": "你好"}],
    model="gpt-4-deployment",  # Azure deployment name
)
print(response.choices[0].message.content)
```

异步 Azure 客户端同理，使用 `AsyncAzureOpenAI`。

## Responses API

OpenAI 新的 Responses API 也被支持：

```python
response = openai_client.responses.create(
    model="gpt-4o",
    input="解释什么是可观测性",
)
print(response.output_text)
```

## 与 @observe 装饰器组合使用

`openai_wrapper` 创建的 Span 与 `@observe` 创建的 Span 自动在同一上下文中建立父子关系：

```python
from cozeloop.decorator import observe

@observe(name="retriever", span_type="retriever")
def retrieve(question):
    """模拟知识检索"""
    return ["北京是中国的首都。", "北京有着悠久的历史。"]

@observe(name="rag_pipeline", span_type="chain")
def rag(question):
    # retrieve() 的 span 自动成为 rag_pipeline 的子 span
    docs = retrieve(question)
    context = "\n".join(docs)

    # openai_wrapper 创建的 span 自动成为 rag_pipeline 的子 span
    response = openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": f"根据以下信息回答问题：\n{context}"},
            {"role": "user", "content": question},
        ],
        model="gpt-4",
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    set_log_level(logging.INFO)
    client = new_client()
    openai_client = openai_wrapper(OpenAI(api_key=os.environ["OPENAI_API_KEY"]))

    answer = rag("北京是哪个国家的首都？")
    print(answer)

    client.flush()
    client.close()
```

生成的 Trace 树结构：

```
rag_pipeline (chain)
├── retriever (retriever)
└── chat_completions (model)   ← openai_wrapper 自动创建
```

## RAG 完整示例（含流式）

```python
import os
import logging
from openai import OpenAI
from cozeloop import new_client
from cozeloop.decorator import observe
from cozeloop.integration.wrapper import openai_wrapper
from cozeloop.logger import set_log_level

@observe
def retriever(question):
    """模拟向量检索"""
    return [
        "CozeLoop 是扣子平台的可观测性 SDK。",
        "它支持 Trace 上报、Prompt Hub 和 PTaaS。",
        "CozeLoop Python SDK 使用 httpx 作为 HTTP 客户端。",
    ]

@observe
def rag(question):
    docs = retriever()
    system_msg = "请根据以下参考资料回答问题：\n\n" + "\n".join(docs)

    stream = openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": question},
        ],
        model=os.environ.get("OPENAI_MODEL_NAME", "gpt-4"),
        stream=True,
        extra_body={"stream_options": {"include_usage": True}},
    )

    print("回答：", end="", flush=True)
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()

if __name__ == "__main__":
    set_log_level(logging.INFO)
    client = new_client()
    openai_client = openai_wrapper(OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
    ))

    rag("CozeLoop 是什么？")
    client.flush()
    client.close()
```

## 注意事项

1. **包装顺序**：必须在创建 OpenAI 客户端**之后**、**使用之前**调用 `openai_wrapper()`。包装后，原客户端的所有 chat.completions.create 调用会被 monkey-patch。

2. **stream_options**：流式调用务必设置 `stream_options={"include_usage": True"}`（或 `extra_body={"stream_options": {"include_usage": True}}`），否则无法获取 token 用量。

3. **不支持的方法**：`openai_wrapper` 仅包装 `chat.completions.create` 和 `responses.create`。其他 API（如 Embeddings、Fine-tuning、Files）不会被自动追踪。

4. **自定义 HTTP 客户端**：包装后的客户端仍然可以使用自定义的 httpx 客户端（如代理配置）：
   ```python
   import httpx
   custom_http = httpx.Client(proxies="http://proxy:8080")
   openai_client = openai_wrapper(OpenAI(
       api_key="key",
       http_client=custom_http,
   ))
   ```

5. **与手动 Span 共存**：可以在 openai_wrapper 的 Span 上通过 context 获取当前 span 并添加自定义标签：
   ```python
   from cozeloop import get_span_from_context

   response = openai_client.chat.completions.create(...)
   current_span = get_span_from_context()
   current_span.set_tags({"custom_metric": 42})
   ```
   注意：openai_wrapper 的 span 在非流式调用中在 create() 返回时已 finish，此时设置标签不会被上报。建议通过父 span（如 @observe 包装的函数）设置自定义标签。

## 下一步

- 学习 [@observe 装饰器和自定义 Span 追踪](custom-span-tracing.md)处理更复杂的场景
- 了解 [LLM 埋点模式](../concepts/02-llm-instrumentation.md)对比三种埋点方式
- 查看 [框架集成参考](../references/integrations.md)了解 LangChain 等更多框架的集成方式
