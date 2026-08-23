---
type: reference
scope: langchain-google
name: api
version: "0.1.0"
source: https://github.com/langchain-ai/langchain-google
description: langchain-google 核心 API 参考——ChatGoogleGenerativeAI、GoogleGenerativeAIEmbeddings、双后端配置与 VertexAI 弃用类
---

# API 参考

本文档覆盖 `langchain-google-genai` 4.3.5 的核心公共 API，以及 `langchain-google-vertexai` 3.2.4 中仍有使用价值的类。所有路径基于仓库 `libs/` 目录。

## ChatGoogleGenerativeAI

**模块**：`langchain_google_genai.chat_models`
**继承**：`_BaseGoogleGenerativeAI` → `pydantic.BaseModel`，混入 `BaseChatModel`
**定义位置**：`libs/genai/langchain_google_genai/chat_models.py:1576`

### 构造函数

```python
ChatGoogleGenerativeAI(
    model: str,
    *,
    # 鉴权与后端
    api_key: str | SecretStr | None = None,           # 别名 google_api_key
    vertexai: bool | None = None,
    project: str | None = None,
    location: str | None = None,
    credentials: Any = None,
    # HTTP 客户端
    base_url: str | dict | None = None,               # 别名 client_options
    api_version: str | None = None,
    additional_headers: dict[str, str] | None = None,
    client_args: dict[str, Any] | None = None,
    # 生成参数
    temperature: float | None = 0.7,
    top_p: float | None = None,
    top_k: int | None = None,
    max_tokens: int | None = None,                    # 别名 max_output_tokens
    candidate_count: int = 1,                         # 别名 n
    frequency_penalty: float | None = None,
    presence_penalty: float | None = None,
    stop: list[str] | None = None,
    # 重试
    retries: int = 6,                                 # 别名 max_retries
    # 其他
    safety_settings: dict | None = None,
    cached_content: str | None = None,
    thinking_budget: int | None = None,
    transport: str | None = None,
    **kwargs: Any,
)
```

**关键参数说明：**

| 参数 | 说明 |
|---|---|
| `model` | 模型名，如 `gemini-3.5-flash`、`gemini-3.1-pro-preview`。Vertex AI 模式下自动剥离 `models/` 前缀。 |
| `vertexai` | `True` 强制 Vertex AI 后端；`False` 强制 Gemini API；`None`（默认）自动检测。 |
| `api_key` | API key。Gemini API 必填；Vertex AI 可选（无 key 时用 ADC）。也可通过 `GOOGLE_API_KEY`/`GEMINI_API_KEY` 环境变量。 |
| `project` | GCP 项目 ID（Vertex AI）。存在即推断为 Vertex AI 后端。回退 `GOOGLE_CLOUD_PROJECT`。 |
| `location` | GCP 区域。回退 `GOOGLE_CLOUD_LOCATION`，Vertex AI 默认 `global`（chat）/`us-central1`（embeddings）。 |
| `credentials` | `google.auth.credentials.Credentials` 对象。存在即强制 Vertex AI 后端。 |
| `temperature` | 采样温度 [0, 2]。Gemini 3.0+ 未显式设置时自动置 None。 |
| `max_tokens` | 最大输出 token 数。别名 `max_output_tokens`。 |
| `retries` | 最大重试次数，默认 6。禁用重试用 1 而非 0。 |
| `thinking_budget` | 思考 token 预算。0 禁用思考，-1 动态思考。 |

### 核心方法

#### invoke / stream / batch（继承自 BaseChatModel）

```python
model.invoke(input: LanguageModelInput, *, config: RunnableConfig | None = None, **kwargs) -> AIMessage
model.stream(input, *, config=None, **kwargs) -> Iterator[AIMessageChunk]
model.batch(inputs: list[LanguageModelInput], *, config=None, **kwargs) -> list[AIMessage]
await model.ainvoke(...)
await model.astream(...)
```

#### _generate（内部，可被子类或高级用户调用）

```python
_generate(
    messages: list[BaseMessage],
    stop: list[str] | None = None,
    run_manager: CallbackManagerForLLMRun | None = None,
    *,
    tools: Sequence[_ToolDict | GoogleTool] | None = None,
    functions: Sequence[_FunctionDeclarationType] | None = None,
    safety_settings: SafetySettingDict | None = None,
    tool_config: dict | ToolConfig | None = None,
    generation_config: dict[str, Any] | None = None,
    cached_content: str | None = None,
    tool_choice: _ToolChoiceType | bool | None = None,
    **kwargs: Any,
) -> ChatResult
```

定义位置：`chat_models.py:3474`。异步版本 `_agenerate` 在 `chat_models.py:3516`，流式版本 `_stream` 在 `chat_models.py:3560`。

#### bind_tools

```python
bind_tools(
    tools: Sequence[dict[str, Any] | type | Callable | BaseTool | GoogleTool],
    tool_config: dict | ToolConfig | None = None,
    *,
    tool_choice: _ToolChoiceType | bool | None = None,
    **kwargs: Any,
) -> Runnable[LanguageModelInput, AIMessage]
```

定义位置：`chat_models.py:3911`。

- `tools`：Pydantic 类、Callable、BaseTool、dict 或原生 `GoogleTool`。Union 参数自动转 `anyOf` schema。
- `tool_choice`：`'auto'`（默认）、`'any'`/`'required'`、`'none'`、函数名、函数名列表、`True`。
- `tool_config`：额外配置，如 `retrieval_config`（Google Maps 接地的经纬度）。

#### with_structured_output

```python
with_structured_output(
    schema: dict | type[BaseModel],
    method: Literal["function_calling", "json_mode", "json_schema"] = "json_schema",
    *,
    include_raw: bool = False,
    **kwargs: Any,
) -> Runnable[LanguageModelInput, dict | BaseModel]
```

定义位置：`chat_models.py:3721`。

- `method="json_schema"`（默认推荐）：原生 JSON schema，支持流式输出完整 Pydantic 对象。
- `method="function_calling"`：工具调用实现，可靠性较低。
- `method="json_mode"`：已弃用，等同 `json_schema`。
- `include_raw=True` 时返回 `{"raw": AIMessage, "parsed": T | None, "parsing_error": Exception | None}`。

### 异常类型

| 异常 | 触发条件 | 父类（LangChain 协议） |
|---|---|---|
| `GoogleContextOverflowError` | 输入超过 token 限制 | `ContextOverflowError` |
| `GoogleAuthenticationError` | HTTP 401 | `ModelAuthenticationError` |
| `GooglePermissionDeniedError` | HTTP 403 | `ModelPermissionDeniedError` |
| `GoogleInvalidRequestError` | HTTP 400 | `ModelInvalidRequestError` |
| `GoogleModelNotFoundError` | HTTP 404 | `ModelNotFoundError` |
| `GoogleRateLimitError` | HTTP 429 | `ModelRateLimitError` |
| `GoogleAPIError` | HTTP 5xx | `ModelAPIError` |
| `ChatGoogleGenerativeAIError` | 通用错误（所有上述的基类） | — |

均定义于 `chat_models.py:153-198`。

## GoogleGenerativeAIEmbeddings

**模块**：`langchain_google_genai.embeddings`
**继承**：`pydantic.BaseModel` + `langchain_core.embeddings.Embeddings`
**定义位置**：`libs/genai/langchain_google_genai/embeddings.py:23`

### 构造函数

```python
GoogleGenerativeAIEmbeddings(
    model: str,
    *,
    task_type: str | None = None,
    api_key: str | SecretStr | None = None,
    vertexai: bool | None = None,
    project: str | None = None,
    location: str | None = None,
    credentials: Any = None,
    base_url: str | None = None,
    api_version: str | None = None,
    additional_headers: dict[str, str] | None = None,
    client_args: dict[str, Any] | None = None,
    request_options: dict | None = None,
    output_dimensionality: int | None = None,
)
```

### 方法

```python
embed_query(
    text: str,
    *,
    task_type: str | None = None,
    title: str | None = None,
    output_dimensionality: int | None = None,
) -> list[float]
```

默认 `task_type="RETRIEVAL_QUERY"`。定义位置：`embeddings.py:464`。

```python
embed_documents(
    texts: list[str],
    *,
    batch_size: int = 100,
    task_type: str | None = None,
    titles: list[str] | None = None,
    output_dimensionality: int | None = None,
) -> list[list[float]]
```

默认 `task_type="RETRIEVAL_DOCUMENT"`。内部按每批最多 100 条、20000 token 自动切批。定义位置：`embeddings.py:391`。

异步版本：`aembed_query`（`embeddings.py:582`）、`aembed_documents`（`embeddings.py:512`）。

### task_type 枚举

`RETRIEVAL_QUERY`、`RETRIEVAL_DOCUMENT`、`SEMANTIC_SIMILARITY`、`CLASSIFICATION`、`CLUSTERING`、`QUESTION_ANSWERING`、`FACT_VERIFICATION`、`CODE_RETRIEVAL_QUERY`、`TASK_TYPE_UNSPECIFIED`。

## GoogleGenerativeAI（LLM 文本补全）

**模块**：`langchain_google_genai.llms`
与 `ChatGoogleGenerativeAI` 共享 `_BaseGoogleGenerativeAI`，用于文本补全场景（非聊天）。实际 Gemini 模型推荐使用 Chat 类。

## VertexAI 弃用类

以下类标记 `@deprecated(since="3.2.0", removal="4.0.0")`，新代码应使用 genai 包对应类。此处列出以帮助现有代码迁移。

### ChatVertexAI

**模块**：`langchain_google_vertexai.chat_models`
**定义位置**：`libs/vertexai/langchain_google_vertexai/chat_models.py:1008`

```python
ChatVertexAI(
    model: str,
    *,
    project: str | None = None,
    location: str = "us-central1",
    credentials: Any = None,
    max_retries: int = 6,
    request_parallelism: int = 5,
    endpoint_version: Literal["v1", "v1beta1"] = "v1beta1",
    transport: str | None = None,            # "grpc" 或 "rest"
    temperature: float | None = None,
    max_tokens: int | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
    safety_settings: SafetySettingsType | None = None,
    thinking_budget: int | None = None,
    seed: int | None = None,
    stop: list[str] | None = None,
    **kwargs: Any,
)
```

底层通过 `PredictionServiceClient.generate_content`（gRPC/REST）调用 gapic 客户端，而非 google-genai SDK。迁移到 `ChatGoogleGenerativeAI` 后，`project`/`location`/`credentials` 参数保持兼容。

### VertexAIEmbeddings

**模块**：`langchain_google_vertexai.embeddings`
**定义位置**：`libs/vertexai/langchain_google_vertexai/embeddings.py:39`

```python
VertexAIEmbeddings(
    model: str,                          # 别名 model_name
    *,
    project: str | None = None,
    location: str = "us-central1",
    credentials: Any = None,
    max_retries: int = 6,
    dimensions: int | None = None,       # 默认输出维度
)
```

核心方法：`embed(texts, embeddings_task_type=None, dimensions=None, title=None)`。
内部已使用 `genai.Client(vertexai=True, ...)`，但接口和重试逻辑独立。迁移到 `GoogleGenerativeAIEmbeddings`。

### VertexAI（LLM）

**模块**：`langchain_google_vertexai.llms`
文本补全类，同样弃用。

## Vertex AI 专属能力（未弃用）

以下类仅存在于 vertexai 包，genai 包尚未覆盖：

### Model Garden 第三方模型

```python
from langchain_google_vertexai.model_garden_maas import get_vertex_maas_model
# 返回 VertexModelGardenLlama 或 VertexModelGardenMistral
model = get_vertex_maas_model("meta/llama-3.1-405b-instruct-maas", ...)
```

- `VertexAIModelGarden`（`model_garden.py`）：自部署端点。
- `model_garden_maas/llama.py`：Llama MaaS。
- `model_garden_maas/mistral.py`：Mistral MaaS。
- Anthropic 支持需 `pip install langchain-google-vertexai[anthropic]`，通过 `model_garden.ChatAnthropicVertex`。

### Vector Search

```python
from langchain_google_vertexai import (
    VectorSearchVectorStore,
    VectorSearchVectorStoreDatastore,
    VectorSearchVectorStoreGCS,
    DataStoreDocumentStorage,
    GCSDocumentStorage,
)
```

### Imagen 视觉模型

```python
from langchain_google_vertexai import (
    VertexAIImageCaptioning,
    VertexAIImageCaptioningChat,
    VertexAIImageEditorChat,
    VertexAIImageGeneratorChat,
    VertexAIVisualQnAChat,
)
```

### Evaluators

```python
from langchain_google_vertexai import (
    VertexPairWiseStringEvaluator,   # 成对比较评估
    VertexStringEvaluator,          # 单字符串评估
)
```

### 工具函数

```python
from langchain_google_vertexai import create_context_cache
```

## 环境变量速查

| 变量 | 用途 | 适用包 |
|---|---|---|
| `GOOGLE_API_KEY` | API key（主，优先） | genai |
| `GEMINI_API_KEY` | API key（后备） | genai |
| `GOOGLE_GENAI_USE_VERTEXAI` | 强制 Vertex AI 后端（`true`/`false`） | genai |
| `GOOGLE_CLOUD_PROJECT` | GCP 项目 ID | 两者 |
| `GOOGLE_CLOUD_LOCATION` | GCP 区域 | 两者 |
| `GOOGLE_APPLICATION_CREDENTIALS` | 服务账号 JSON 路径 | vertexai |
| `HTTPS_PROXY` | HTTP/HTTPS 代理 | genai |
| `SSL_CERT_FILE` | 自定义 SSL 证书 | genai |
| `GOOGLE_CLOUD_AGENT_ENGINE_ID` | 设置后追加 `+remote_reasoning_engine` 遥测标签 | genai |

## 进一步阅读

- [聊天模型架构](/ai/langchain-ai/langchain-google/concepts/chat-models)
- [嵌入模型与 Vertex AI](/ai/langchain-ai/langchain-google/concepts/embeddings-vertex)
- [基础使用示例](/ai/langchain-ai/langchain-google/examples/basic-usage)
