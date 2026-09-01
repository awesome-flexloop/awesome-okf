---
type: example
scope: langchain-google
name: basic-usage
version: "0.1.0"
source: https://github.com/langchain-ai/langchain-google
description: langchain-google 基础使用示例——聊天、流式、工具调用、结构化输出、嵌入与 Vertex AI 配置
---

# 基础使用示例

本示例演示 `langchain-google-genai` 的核心使用流程。推荐所有新代码使用 `ChatGoogleGenerativeAI` 和 `GoogleGenerativeAIEmbeddings`，它们同时支持 Gemini Developer API 和 Vertex AI。

## 前置条件

```bash
pip install langchain-google-genai
```

设置 API key（Gemini Developer API）：

```bash
export GOOGLE_API_KEY="your-api-key"
```

## 最小聊天示例

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

messages = [
    SystemMessage(content="你是一个简洁的助手。"),
    HumanMessage(content="用一句话解释什么是 RAG。"),
]

response = llm.invoke(messages)
print(response.content)
# RAG（检索增强生成）是一种先从外部知识库检索相关文档、再让语言模型基于检索结果生成答案的技术。

print(response.response_metadata["model_name"])  # gemini-3.5-flash
print(response.usage_metadata)
# {'input_tokens': 18, 'output_tokens': 42, 'total_tokens': 60}
```

## 流式输出

```python
for chunk in llm.stream("写一首关于编程的短诗"):
    print(chunk.content, end="", flush=True)
```

异步流式：

```python
async for chunk in llm.astream("写一首关于编程的短诗"):
    print(chunk.content, end="", flush=True)
```

## 切换到 Vertex AI 后端

同一套 API，仅改参数即可切换到 Vertex AI（适合生产环境）：

```python
# 方式 1：显式参数（使用 ADC 凭证）
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    project="my-gcp-project",
    location="us-central1",
    vertexai=True,
)

# 方式 2：环境变量驱动（无需改代码）
# export GOOGLE_GENAI_USE_VERTEXAI=true
# export GOOGLE_CLOUD_PROJECT=my-gcp-project
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")
```

Vertex AI 鉴权支持：
- **ADC（推荐）**：`gcloud auth application-default login`
- **服务账号**：传入 `credentials=service_account.Credentials.from_service_account_file(...)`
- **API key**：`vertexai=True` + `project` + `api_key`

注意：Vertex AI 模式下若程序化传入 API key，代码会临时设置 `GOOGLE_API_KEY` 环境变量并在客户端创建后清理。

## 工具调用（Function Calling）

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """获取指定城市的当前天气。"""
    # 实际中调用天气 API
    return f"{city} 今天晴，25°C。"


llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")
llm_with_tools = llm.bind_tools([get_weather])

response = llm_with_tools.invoke("北京今天天气怎么样？")

if response.tool_calls:
    for call in response.tool_calls:
        print(f"调用工具: {call['name']}, 参数: {call['args']}")
        # 调用工具并将结果返回给模型
        result = get_weather.invoke(call["args"])
        print(f"工具结果: {result}")
```

控制工具使用方式：

```python
# 强制必须调用工具
llm.bind_tools([get_weather], tool_choice="required")

# 禁止调用工具
llm.bind_tools([get_weather], tool_choice="none")

# 强制调用指定工具
llm.bind_tools([get_weather], tool_choice="get_weather")
```

### Google Search 接地

```python
from google.genai.types import Tool

llm_with_search = llm.bind_tools(
    [{"google_search": {}}],
    tool_choice="required",
)
response = llm_with_search.invoke("今天的科技新闻有哪些？")
```

## 结构化输出

使用 Pydantic 模型约束输出结构（默认 `json_schema` 方法，支持流式输出完整对象）：

```python
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI


class Person(BaseModel):
    name: str = Field(description="人名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")


llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
structured_llm = llm.with_structured_output(Person)

result = structured_llm.invoke("介绍一下张三，他是一名30岁的工程师。")
print(result)
# Person(name='张三', age=30, occupation='工程师')
```

流式获取已解析对象：

```python
for obj in structured_llm.stream("介绍李四，28岁设计师"):
    print(obj)  # Person(name=..., age=..., occupation=...)
```

若需要原始响应和解析错误信息：

```python
structured_llm_raw = llm.with_structured_output(Person, include_raw=True)
output = structured_llm_raw.invoke("...")
print(output["raw"])       # AIMessage
print(output["parsed"])    # Person | None
print(output["parsing_error"])  # Exception | None
```

## 嵌入模型

### 基本用法

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

# 单个查询（默认 task_type=RETRIEVAL_QUERY）
vector = embeddings.embed_query("什么是向量数据库？")
print(f"维度: {len(vector)}")

# 批量文档（默认 task_type=RETRIEVAL_DOCUMENT，每批最多 100 条/20000 token）
docs = ["向量数据库存储高维向量。", "相似度搜索用于检索。", "RAG 结合检索与生成。"]
vectors = embeddings.embed_documents(docs)
print(f"文档数: {len(vectors)}, 维度: {len(vectors[0])}")
```

### RAG 中的正确用法

查询和文档使用不同的 `task_type` 以获得最佳检索效果（默认已正确区分）：

```python
# 文档入库：RETRIEVAL_DOCUMENT
doc_vectors = embeddings.embed_documents(documents)

# 查询检索：RETRIEVAL_QUERY
query_vector = embeddings.embed_query(user_question)
```

如需指定其他任务类型：

```python
# 语义相似度任务
embeddings.embed_query(text, task_type="SEMANTIC_SIMILARITY")

# 聚类任务
embeddings.embed_documents(texts, task_type="CLUSTERING")
```

### Vertex AI 嵌入后端

```python
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    project="my-gcp-project",
    vertexai=True,
)
```

### 维度缩减

preview 模型支持 Matryoshka 降维：

```python
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    output_dimensionality=512,  # 截断为 512 维
)
```

### 异步批量嵌入

```python
vectors = await embeddings.aembed_documents(large_doc_list)
query_vec = await embeddings.aembed_query("查询")
```

## 安全设置

```python
from langchain_google_genai import HarmCategory, HarmBlockThreshold

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    },
)
```

## 思考预算（Thinking Models）

Gemini 2.5+ 支持思考过程，可通过 `thinking_budget` 控制：

```python
# 禁用思考（降低延迟）
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", thinking_budget=0)

# 动态思考（模型自行决定）
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", thinking_budget=-1)
```

## 错误处理

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAIError,
    GoogleRateLimitError,
    GoogleContextOverflowError,
)

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", max_retries=1)

try:
    llm.invoke("...")
except GoogleContextOverflowError:
    # 上下文过长，可触发摘要压缩中间件
    ...
except GoogleRateLimitError:
    # 限流，自行处理退避
    ...
except ChatGoogleGenerativeAIError as e:
    # 其他 Google 错误（400/401/403/404/5xx）
    ...
```

注意：禁用 SDK 重试用 `max_retries=1`（不是 0）。SDK 的 429 重试使用固定指数退避，不遵循服务器返回的 `retry_delay`（上游 issue #1875）。

## LCEL 组合

ChatModel 是 Runnable，可与 LangChain 表达式语言组合：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是 {role} 专家。"),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()

answer = chain.invoke({"role": "Python", "question": "什么是装饰器？"})
```

## 注意事项

1. **模型选择**：避免使用已弃用的 `gemini-1.5-flash`、`gemini-1.5-pro`、`gemini-pro` 等；推荐 `gemini-3.5-flash`、`gemini-3.1-pro-preview`。
2. **temperature 自动行为**：Gemini 3.0+ 未显式设置 temperature 时自动为 None，不要依赖默认 0.7。
3. **嵌入仅文本**：LangChain `Embeddings` 接口仅接受文本；多模态嵌入需直接使用 `google-genai` SDK。
4. **批大小**：嵌入自动分批（100 条/20000 token），无需手动分批。
5. **Vertex AI 模型名**：自动剥离 `models/` 前缀，传 `"gemini-3.5-flash"` 即可。

## 相关文档

- API 参考
- 聊天模型架构
- 嵌入模型与 Vertex AI
- 总览
