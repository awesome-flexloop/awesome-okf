---
type: concept
scope: langchain-google
name: chat-models
version: "0.1.0"
source: https://github.com/langchain-ai/langchain-google
description: ChatGoogleGenerativeAI 架构——双后端客户端、消息转换、生成流程、工具调用与结构化输出、错误分类
---

# 聊天模型架构

`ChatGoogleGenerativeAI` 是 langchain-google-genai 的核心类，位于 `libs/genai/langchain_google_genai/chat_models.py:1576`，继承 `_BaseGoogleGenerativeAI` 和 `langchain_core.language_models.chat_models.BaseChatModel`。它将 Google Gemini 模型接入 LangChain 的聊天模型协议，同时支持 Gemini Developer API 和 Vertex AI 两个后端。

## 类继承与职责

```
pydantic.BaseModel
    └── _BaseGoogleGenerativeAI          # 鉴权、后端检测、客户端参数
            └── ChatGoogleGenerativeAI   # 消息转换、生成、工具、结构化输出
                    (混入 BaseChatModel)  # LangChain 聊天模型协议
```

- `_BaseGoogleGenerativeAI`（`_common.py:56`）负责：API key/project/credentials/location 字段、`_determine_backend()` 后端选择、`lc_secrets` 密钥声明、`_identifying_params` 标识参数。
- `ChatGoogleGenerativeAI` 负责：消息→`Content`/`Part` 转换、`_prepare_request` 请求构建、`_generate`/`_agenerate`/`_stream` 生成、`bind_tools` 工具绑定、`with_structured_output` 结构化输出、响应→`AIMessage` 转换、错误分类。

## 客户端初始化流程

实例化时通过两个 `model_validator(mode="after")` 完成初始化：

1. **`_determine_backend()`**（继承自 `_common.py:614`）：按五级优先级确定 `_use_vertexai` 布尔值。
2. **`_initialize_client()`**（`chat_models.py:2747` 附近）：
   - 构建 `HttpOptions`（含 `user-agent: langchain-google-genai/<version>-ChatGoogleGenerativeAI`、自定义 headers、client_args、api_version）。
   - 若 Vertex AI：剥离 `model` 的 `models/` 前缀；若程序化传入了 API key 但环境变量未设，临时设 `os.environ["GOOGLE_API_KEY"]` 并在 finally 清理；调用 `Client(vertexai=True, project=, location=, credentials=, http_options=)`。
   - 若 Gemini API：必须有 API key，否则抛 `ValueError`；调用 `Client(api_key=, http_options=)`。
3. **`_set_model_profile()`**（`chat_models.py:2795`）：规范化模型 ID（去 `models/` 前缀和 `-001` 后缀），从 `_PROFILES` 加载默认 `ModelProfile`。

析构时 `__del__`（`chat_models.py:2803`）关闭同步/异步客户端，避免资源泄漏。

## 消息转换：LangChain Message → GenAI Content

LangChain 使用 `HumanMessage`/`SystemMessage`/`AIMessage`/`ToolMessage`，而 GenAI SDK 使用 `Content`（含 `Part` 列表）。转换由 `_convert_to_parts()`（`chat_models.py:463`）等函数完成：

| LangChain 内容 | GenAI Part |
|---|---|
| 纯文本字符串 | `Part(text=...)` |
| `{"type": "text", "text": ...}` | `Part(text=...)`，若含 `extras.signature` 则附加 `thought_signature` |
| 图片（base64/URL/PIL） | `Part(inline_data=...)` 或 `Part(file_data=...)`，由 `ImageBytesLoader` 处理 |
| 工具调用 | `Part(function_call=FunctionCall(...))` |
| 工具返回 | `Part(function_response=FunctionResponse(...))` |
| 代码执行结果 | `Part(code_execution_result=...)` |
| 视频元数据 | 先经 `_validate_video_metadata` 校验起止偏移 |

`_validate_video_metadata()`（`chat_models.py:383`）是一个防御性校验：Gemini API 在视频偏移为负或 `start_offset > end_offset` 时返回不透明的 `500 Internal error`，该函数在客户端提前抛出清晰的 `ValueError`，避免用户调试底层 API 响应。

## 生成流程

### 同步 `_generate`（`chat_models.py:3474`）

```
messages + 参数
    │
    ▼
_prepare_request(messages, stop, tools, functions,
                 safety_settings, tool_config, generation_config,
                 cached_content, tool_choice, **kwargs)
    │  → 构建 {model, contents, config: GenerateContentConfig, ...}
    ▼
self.client.models.generate_content(**request)
    │  异常 → _handle_client_error / _handle_server_error
    ▼
_response_to_result(response)  → ChatResult(generations=[ChatGeneration(...)])
```

`_generate` 的关键字参数（`tools`、`functions`、`safety_settings`、`tool_config`、`generation_config`、`cached_content`、`tool_choice`）允许在调用时覆盖实例默认值，这是 `bind_tools`/`with_structured_output` 等机制的基础。

### 异步 `_agenerate`（`chat_models.py:3516`）

与同步版本结构完全一致，仅将 `self.client.models.generate_content` 替换为 `await self.client.aio.models.generate_content`。

### 流式 `_stream`（`chat_models.py:3560`）

调用 `self.client.models.generate_content_stream(**request)`，返回的生成器通过 `_classified_stream()`（`chat_models.py:254`）包装。这是必要的，因为流式 API 在迭代时才发出请求、才可能抛错，必须在消费点而非调用点分类异常。每个 chunk 通过响应转换函数转为 `ChatGenerationChunk` 并 yield。

## 工具调用（bind_tools）

`bind_tools()`（`chat_models.py:3911`）将工具定义绑定到模型，返回一个新的 `Runnable`：

```python
model.bind_tools(
    tools,                          # dict / Pydantic 类 / Callable / BaseTool / GoogleTool
    tool_config=None,               # 额外配置，如 retrieval_config（Google Maps/Search 接地）
    *,
    tool_choice=None,               # 'auto'/'any'/'required'/'none'/函数名/函数名列表/True
    **kwargs,
)
```

工具转换由 `_function_utils.py` 中的 `convert_to_genai_function_declarations()` 完成，支持：
- Pydantic BaseModel → JSON schema → `FunctionDeclaration`
- Callable（从签名和 docstring 提取 schema）
- BaseTool（LangChain 工具）
- Union 类型参数 → `anyOf` schema

`tool_choice` 通过 `_tool_choice_to_tool_config()` 转为 GenAI 的 `ToolConfig(function_calling_config=FunctionCallingConfig(mode=...))`。Google 原生的接地工具（Google Search、Google Maps）也通过 `tools=[{"google_search": {}}]` 或 `tools=[{"google_maps": {}}]` 传入，`tool_config` 可携带 `retrieval_config`（如经纬度）。

## 结构化输出（with_structured_output）

`with_structured_output()`（`chat_models.py:3721`）返回约束输出符合 schema 的 `Runnable`：

```python
model.with_structured_output(
    schema,                     # Pydantic BaseModel / TypedDict / JSON schema dict
    method="json_schema",       # "json_schema"(推荐) / "json_mode"(弃用别名) / "function_calling"
    *,
    include_raw=False,          # True 时返回 {raw, parsed, parsing_error}
    **kwargs,
)
```

- **`json_schema`**（默认）：使用 Gemini 原生 `response_json_schema` 支持，可靠性高，流式时发出完全解析的 Pydantic 对象（非增量 JSON 字符串）。
- **`function_calling`**：通过工具调用实现结构化输出，可靠性较低，不推荐新代码使用。
- **`json_mode`**：`json_schema` 的弃用别名。

实现上组合了 `JsonOutputParser`/`PydanticOutputParser`/`PydanticToolsParser`（来自 langchain_core）与模型绑定，形成 LCEL 管道。

## 错误分类体系

`ChatGoogleGenerativeAI` 将 `google.genai.errors.ClientError`/`ServerError` 映射到 LangChain 跨厂商异常体系（`langchain_core.exceptions`）：

| HTTP | 异常类 | 父类 | 中间件意义 |
|---|---|---|---|
| 400 | `GoogleInvalidRequestError` | `ModelInvalidRequestError` | 不可重试 |
| 401 | `GoogleAuthenticationError` | `ModelAuthenticationError` | 凭证问题 |
| 403 | `GooglePermissionDeniedError` | `ModelPermissionDeniedError` | 权限问题 |
| 404 | `GoogleModelNotFoundError` | `ModelNotFoundError` | 模型名错误 |
| 429 | `GoogleRateLimitError` | `ModelRateLimitError` | 可重试（限流） |
| 5xx | `GoogleAPIError` | `ModelAPIError` | 服务端可重试 |
| 上下文溢出 | `GoogleContextOverflowError` | `ContextOverflowError` | 触发上下文压缩回退 |

所有错误类同时继承 `ChatGoogleGenerativeAIError`，保证 `except ChatGoogleGenerativeAIError` 的旧代码仍能捕获（向后兼容）。`GoogleContextOverflowError` 通过错误消息字符串匹配（"exceeds the maximum number of tokens allowed" / "token limit"）而非状态码识别，使 `SummarizationMiddleware` 能专门处理。

详见 [深度洞察 §3](/langchain-ai/langchain-google/spec/insights)。

## 模型行为差异处理

代码中包含若干针对特定模型版本的特殊处理：

- **Gemini 3.0+ temperature**：`_BaseGoogleGenerativeAI` docstring 注明，未显式设置 temperature 时自动置 `None`（而非默认 0.7），避免无限循环和推理性能下降。
- **固定采样模型白名单**：`_FIXED_SAMPLING_AND_NO_PREFILL_MODELS = frozenset({"gemini-3.5-flash-lite", "gemini-3.6-flash"})`（`chat_models.py:352`），这些模型弃用 `temperature/top_k/top_p` 且不允许预填充模型轮次。由于 Gemini 版本号非单调（`gemini-3.5-flash` 不受影响但 `-lite` 受影响），只能维护显式白名单。
- **thinking_budget**：支持配置思考预算（0 禁用，-1 动态），通过 `GenerateContentConfig.thinking_config` 传递。

## 与 ChatVertexAI 的关系

`ChatVertexAI`（`libs/vertexai/.../chat_models.py:1008`）是旧实现，基于 `google.cloud.aiplatform` 的 gapic/proto 客户端（`PredictionServiceClient.generate_content`，gRPC/REST），同时导入 v1 和 v1beta1 两套 proto 类型。它已标记弃用，推荐迁移到 `ChatGoogleGenerativeAI`。两者在 LangChain 协议层面接口一致，但底层 SDK 和错误处理不同——新代码应统一使用 genai 包。

## 进一步阅读

- [总览](/langchain-ai/langchain-google/concepts/overview)
- [嵌入模型与 Vertex AI](/langchain-ai/langchain-google/concepts/embeddings-vertex)
- [API 参考](/langchain-ai/langchain-google/references/api)
- [基础使用示例](/langchain-ai/langchain-google/examples/basic-usage)
