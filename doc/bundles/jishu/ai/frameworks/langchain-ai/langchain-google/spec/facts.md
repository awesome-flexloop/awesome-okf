---
type: spec
title: "langchain-google 事实清单"
---

# langchain-google 事实清单

## 项目元信息与 Monorepo 结构

F-001: 仓库根目录 `README.md` 表明这是 LangChain 与 Google AI/VertexAI/GenAI 的集成 monorepo，`libs/` 下包含三个独立版本化的 Python 包：`community`、`genai`、`vertexai`，均使用 `uv` 管理依赖、`hatchling` 构建。

F-002: 文件 `libs/genai/pyproject.toml` 第5-13行，包名 `langchain-google-genai`，版本 `4.3.5`，描述 "An integration package connecting Google's genai package and LangChain"，要求 Python `>=3.10.0,<4.0.0`。

F-003: 文件 `libs/genai/pyproject.toml` 第14-19行，运行时依赖为 `langchain-core>=1.6.0,<2.0.0`、`google-genai>=1.65.0,<3.0.0`、`pydantic>=2.0.0,<3.0.0`、`filetype>=1.2.0,<2.0.0`。

F-004: 文件 `libs/vertexai/pyproject.toml` 第5-13行，包名 `langchain-google-vertexai`，版本 `3.2.4`，描述 "An integration package connecting Google VertexAI and LangChain"，要求 Python `>=3.10.0,<4.0.0`。

F-005: 文件 `libs/vertexai/pyproject.toml` 第14-26行，运行时依赖包含 `langchain-core>=1.4.7,<2.0.0`、`google-cloud-aiplatform>=1.97.0,<2.0.0`、`google-cloud-storage>=2.18.0,<4.0.0`、`httpx>=0.28.0`、`httpx-sse>=0.4.0`、`pydantic>=2.9.0`、`validators`、`bottleneck`、`numexpr`、`pyarrow>=19.0.1,<24.0.0`、`google-cloud-vectorsearch>=0.2.0`。

F-006: 文件 `libs/vertexai/pyproject.toml` 第37-42行，可选依赖组 `anthropic` 包含 `anthropic>=0.35.0,<1.0.0`，`mistral` 包含 `langchain-mistralai>=0.2.0,<2.0.0`，`vectorsearch_v2` 包含 `google-cloud-vectorsearch`。

F-007: 文件 `AGENTS.md`（仓库根）明确 "Golden rule: use the current SDK"——必须使用 `google-genai`（`from google import genai`），旧库 `google-generativeai`、`google-ai-generativelanguage` 已废弃；禁止使用 `gemini-1.5-flash`、`gemini-1.5-pro`、`gemini-pro`、`gemini-3-pro-preview`、`gemini-embedding-001` 等过时模型。

## langchain-google-genai 公共 API

F-008: 文件 `libs/genai/langchain_google_genai/__init__.py` 第39-65行，`__all__` 导出：`ChatGoogleGenerativeAI`、`GoogleGenerativeAI`（LLM）、`GoogleGenerativeAIEmbeddings`、`create_context_cache`、`__version__`，以及枚举 `ComputerUse`、`Environment`、`HarmBlockThreshold`、`HarmCategory`、`MediaResolution`、`Modality`。

F-009: 文件 `libs/genai/langchain_google_genai/__init__.py` 第3-14行模块 docstring 声明：自 `langchain-google-genai` 4.0.0 起，包使用统一的 `google-genai` SDK 替代旧的 `google-ai-generativelanguage` SDK，同时支持 Gemini API 和 Vertex AI 中的 Gemini 模型，取代了 `langchain-google-vertexai` 中的 `ChatVertexAI` 等类。

## _BaseGoogleGenerativeAI 基类（_common.py）

F-010: 文件 `libs/genai/langchain_google_genai/_common.py` 第56行，类 `_BaseGoogleGenerativeAI(BaseModel)` 是 `ChatGoogleGenerativeAI` 和 `GoogleGenerativeAI`（LLM）的共享基类。

F-011: 文件 `libs/genai/langchain_google_genai/_common.py` 第167-172行，字段 `google_api_key: SecretStr | None`，别名为 `api_key`，默认通过 `secret_from_env(["GOOGLE_API_KEY", "GEMINI_API_KEY"], default=None)` 从环境变量读取，`GOOGLE_API_KEY` 优先。

F-012: 文件 `libs/genai/langchain_google_genai/_common.py` 第221行，字段 `vertexai: bool | None = Field(default=None)`，为 None 时自动检测后端。

F-013: 文件 `libs/genai/langchain_google_genai/_common.py` 第257行，字段 `project: str | None`（Vertex AI only），回退到 `GOOGLE_CLOUD_PROJECT` 环境变量。

F-014: 文件 `libs/genai/langchain_google_genai/_common.py` 第265-267行，字段 `location: str | None`，通过 `from_env("GOOGLE_CLOUD_LOCATION", default=None)` 读取，Vertex AI 默认回退到 `'global'`（embeddings 中为 `'us-central1'`）。

F-015: 文件 `libs/genai/langchain_google_genai/_common.py` 第274行，字段 `base_url: str | dict | None`，别名为 `client_options`，类型接受 `dict` 以向后兼容（仅提取 `api_endpoint` 键）。

F-016: 文件 `libs/genai/langchain_google_genai/_common.py` 第311行，字段 `client_args: dict[str, Any] | None`，传递给底层 HTTP 客户端（如 SOCKS5 代理），同时应用于同步和异步客户端。

F-017: 文件 `libs/genai/langchain_google_genai/_common.py` 第326行，字段 `api_version: str | None`，覆盖请求 URL 中的 API 版本段（google-genai SDK 默认 Vertex AI 用 `v1beta1`、Gemini Developer API 用 `v1beta`）。

F-018: 文件 `libs/genai/langchain_google_genai/_common.py` 第349行，字段 `model: str`（必填）。

F-019: 文件 `libs/genai/langchain_google_genai/_common.py` 第352行，字段 `temperature: float | None = 0.7`；docstring 注明 Gemini 3.0+ 模型若未显式设置，会自动设为 `None`（避免无限循环和推理性能下降）。

F-020: 文件 `libs/genai/langchain_google_genai/_common.py` 第417行，字段 `max_retries: int = Field(default=6, alias="retries")`；docstring 警告：禁用重试应设 `max_retries=1`（而非 0），因为底层 Google SDK 将 0 解释为"使用默认值"（5 次重试）。

F-021: 文件 `libs/genai/langchain_google_genai/_common.py` 第614-647行，方法 `_determine_backend(self) -> Self` 的后端选择优先级：(1) 显式 `vertexai` 参数；(2) `GOOGLE_GENAI_USE_VERTEXAI` 环境变量（true/1/yes → True，false/0/no → False）；(3) `credentials` 参数存在 → Vertex AI；(4) `project` 参数存在 → Vertex AI；(5) 默认 Gemini Developer API（False）。结果存入私有属性 `_use_vertexai`。

F-022: 文件 `libs/genai/langchain_google_genai/_common.py` 第35-53行，模块级函数 `_will_use_vertexai(values: dict[str, Any]) -> bool` 在 "before" 验证阶段预测后端选择，用于 LangSmith gateway 仅应用于 Gemini Developer API 后端（gateway 代理该 API 而非 Vertex AI）。

F-023: 文件 `libs/genai/langchain_google_genai/_common.py` 第649-655行，属性 `lc_secrets` 返回 `{"google_api_key": "GOOGLE_API_KEY", "gemini_api_key": "GEMINI_API_KEY"}`，用于 LangChain 密钥脱敏。

F-024: 文件 `libs/genai/langchain_google_genai/_common.py` 第673-684行，函数 `get_user_agent(module: str | None = None) -> tuple[str, str]` 返回 `(client_library_version, user_agent)`；当环境变量 `GOOGLE_CLOUD_AGENT_ENGINE_ID` 存在时，追加 `+remote_reasoning_engine` 遥测标签。

## ChatGoogleGenerativeAI（chat_models.py）

F-025: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第1576行，类 `ChatGoogleGenerativeAI(_BaseGoogleGenerativeAI, BaseChatModel)`。

F-026: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第24-51行，从 `google.genai.types` 导入大量类型：`Content`、`Part`、`FunctionCall`、`FunctionDeclaration`、`FunctionResponse`、`GenerateContentConfig`、`GenerateContentResponse`、`GenerationConfig`、`HttpOptions`、`HttpRetryOptions`、`SafetySetting`、`ThinkingConfig`、`ToolCodeExecution`、`ToolConfig`、`VideoMetadata`、`SpeechConfig`、`VoiceConfig`、`PrebuiltVoiceConfig`、`Blob`、`Candidate`、`FileData`、`ImageConfig` 等。

F-027: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第192-198行，字典 `_CLIENT_ERROR_TYPES: dict[int, type[ChatGoogleGenerativeAIError]]` 映射 HTTP 状态码：400→`GoogleInvalidRequestError`、401→`GoogleAuthenticationError`、403→`GooglePermissionDeniedError`、404→`GoogleModelNotFoundError`、429→`GoogleRateLimitError`。

F-028: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第161行，类 `GoogleContextOverflowError(ClientError, ContextOverflowError)`，当错误消息包含 "exceeds the maximum number of tokens allowed" 或 "token limit" 时抛出，使上游中间件（如 `SummarizationMiddleware`）能捕获并回退到上下文压缩。

F-029: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第166-189行，错误类继承体系：`GoogleAuthenticationError`、`GooglePermissionDeniedError`、`GoogleInvalidRequestError`、`GoogleModelNotFoundError`、`GoogleRateLimitError` 均同时继承 `ChatGoogleGenerativeAIError` 和对应的 `langchain_core.exceptions.Model*Error`；`GoogleAPIError(ServerError, ModelAPIError)` 用于服务端错误。

F-030: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第200-235行，函数 `_handle_client_error(e: ClientError, request: dict) -> None`：先检测上下文溢出（抛出 `GoogleContextOverflowError`），否则根据 `e.code` 在 `_CLIENT_ERROR_TYPES` 中查找对应 LangChain 错误类型并抛出，兜底抛出 `ChatGoogleGenerativeAIError`。

F-031: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第254-275行，函数 `_classified_stream(response, request)` 包装流式生成器：由于 `generate_content_stream` 返回的是生成器（请求在迭代时才发出），错误会在消费时才抛出，因此在此处 try/except 分类 `ClientError` 和 `ServerError`；异步版本为 `_aclassified_stream`（第278-300行）。

F-032: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第352-354行，常量 `_FIXED_SAMPLING_AND_NO_PREFILL_MODELS = frozenset({"gemini-3.5-flash-lite", "gemini-3.6-flash"})`，这些模型弃用自定义采样参数且不允许预填充模型轮次；注释说明未来 GA 模型需加入此白名单。

F-033: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第358-364行，函数 `_uses_fixed_sampling_and_disallows_prefill(model_name)` 先 `rsplit("/", 1)[-1]` 去掉前缀，再用 `re.sub(r"-\d{3}$", "", ...)` 去掉版本后缀（如 `-001`），检查是否在白名单中。

F-034: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第2747-2792行，`_initialize_client` model_validator 中的客户端创建逻辑：若 `_use_vertexai` 为 True，先剥离 `model` 的 `models/` 前缀；若传入了 API key 但环境变量未设置，临时设置 `os.environ["GOOGLE_API_KEY"]`（google-genai SDK 在 Vertex AI 模式下通过环境变量读取 API key），在 finally 中清理；调用 `Client(vertexai=True, project=, location=, credentials=, http_options=)`。否则（Gemini Developer API）必须有 API key，调用 `Client(api_key=, http_options=)`，无 key 时抛出 `ValueError`。

F-035: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第2795-2801行，model_validator `_set_model_profile`：若 `profile` 为 None，用 `re.sub(r"-\d{3}$", "", model.replace("models/", ""))` 规范化模型 ID，从 `_PROFILES`（来自 `langchain_google_genai.data._profiles`）获取默认 `ModelProfile`。

F-036: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第3474-3514行，方法 `_generate(messages, stop, run_manager, *, tools, functions, safety_settings, tool_config, generation_config, cached_content, tool_choice, **kwargs) -> ChatResult`：先检查 `self.client is not None`，调用 `self._prepare_request(...)` 构建请求，然后 `self.client.models.generate_content(**request)`，捕获 `ClientError`/`ServerError` 并分类，最后 `_response_to_result(response)`。

F-037: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第3516-3558行，异步方法 `_agenerate` 调用 `await self.client.aio.models.generate_content(**request)`，其余逻辑与 `_generate` 一致。

F-038: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第3560行起，方法 `_stream` 调用 `self.client.models.generate_content_stream(**request)` 并通过 `_classified_stream` 包装错误。

F-039: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第3721-3729行，方法 `with_structured_output(schema, method="json_schema", *, include_raw=False, **kwargs) -> Runnable`，`method` 支持 `"function_calling"`、`"json_mode"`（json_schema 的弃用别名）、`"json_schema"`（默认，推荐）；`schema` 接受 Pydantic BaseModel、TypedDict 或 JSON schema dict；流式时发出完全解析的 Pydantic 对象而非增量 JSON 字符串。

F-040: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第3911-3920行，方法 `bind_tools(tools, tool_config=None, *, tool_choice=None, **kwargs) -> Runnable`；`tools` 接受 dict、type（Pydantic）、Callable、BaseTool、GoogleTool；`tool_choice` 支持 `'auto'`（默认）、`'any'`/`'required'`（等价）、`'none'`、函数名、函数名列表、`True`（等同 'any'）。

F-041: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第316-342行，函数 `_merge_http_options(base, override)`：`timeout` 和 `retry_options` 从内部配置派生（除非 override 显式设置），其余 override 字段直接覆盖，`headers` 合并（override 优先）。

## GoogleGenerativeAIEmbeddings（embeddings.py）

F-042: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第19-20行，常量 `_MAX_TOKENS_PER_BATCH = 20000`、`_DEFAULT_BATCH_SIZE = 100`。

F-043: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第23行，类 `GoogleGenerativeAIEmbeddings(BaseModel, Embeddings)`。

F-044: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第26-32行 docstring 警告：`gemini-embedding-2-preview` 原生支持多模态（文本、图片、视频、音频、PDF），但 LangChain `Embeddings` 接口（`embed_query`/`embed_documents`）目前仅接受文本；多模态嵌入需直接使用 Google GenAI SDK。

F-045: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第115-133行，字段 `task_type: str | None`，有效值包括 `RETRIEVAL_QUERY`、`RETRIEVAL_DOCUMENT`、`SEMANTIC_SIMILARITY`、`CLASSIFICATION`、`CLUSTERING`、`QUESTION_ANSWERING`、`FACT_VERIFICATION`、`CODE_RETRIEVAL_QUERY`、`TASK_TYPE_UNSPECIFIED`。

F-046: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第211行，字段 `output_dimensionality: int | None`，设置后所有 embed 调用使用该维度，除非显式覆盖。

F-047: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第248-310行，model_validator `_initialize_client`：构建 `HttpOptions`（含 user-agent header），Vertex AI 模式调用 `Client(vertexai=True, project=, location=, credentials=, http_options=)`，Gemini API 模式调用 `Client(api_key=, http_options=)`；与 ChatModel 相同的 API key 环境变量临时设置/清理逻辑。

F-048: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第321-356行，静态方法 `_prepare_batches(texts, batch_size)` 按当前最大批大小（100 条）和每批最大 token 数（20000）切分文本；当单条文本超过 `_MAX_TOKENS_PER_BATCH` 或累计 token 超限/达到 batch_size 时切批。

F-049: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第391-462行，方法 `embed_documents(texts, *, batch_size=100, task_type=None, titles=None, output_dimensionality=None) -> list[list[float]]`：默认 `effective_task_type` 为 `"RETRIEVAL_DOCUMENT"`；逐批调用 `self.client.models.embed_content(model=, contents=[{"parts":[{"text":...}]}...], config=)`；title 仅在单文本批次时传入；捕获 `ClientError` 包装为 `GoogleGenerativeAIError`。

F-050: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第464-510行，方法 `embed_query(text, *, task_type=None, title=None, output_dimensionality=None) -> list[float]`：默认 `effective_task_type` 为 `"RETRIEVAL_QUERY"`；调用 `self.client.models.embed_content(model=, contents=text, config=)`，返回 `result.embeddings[0].values`。

F-051: 文件 `libs/genai/langchain_google_genai/embeddings.py` 第512-582行，异步方法 `aembed_documents` 和 `aembed_query`，使用 `self.client.aio.models.embed_content`。

## langchain-google-vertexai 公共 API

F-052: 文件 `libs/vertexai/langchain_google_vertexai/__init__.py` 第79-110行，`__all__` 导出：`ChatVertexAI`（标记 Deprecated）、`VertexAI`（Deprecated）、`VertexAIEmbeddings`（Deprecated）、`create_structured_runnable`（Deprecated）、`create_context_cache`、`get_vertex_maas_model`、`VertexAIModelGarden`、`VertexAIImageCaptioning`/`Chat`/`EditorChat`/`GeneratorChat`/`VisualQnAChat`、`VertexPairWiseStringEvaluator`/`VertexStringEvaluator`、`VectorSearchVectorStore`/`Datastore`/`GCS`、`DataStoreDocumentStorage`、`GCSDocumentStorage`、`PydanticFunctionsOutputParser`、以及枚举和类型重导出。

F-053: 文件 `libs/vertexai/langchain_google_vertexai/__init__.py` 第35-41行，从 `google.cloud.aiplatform_v1beta1.types` 重导出 `FunctionCallingConfig`、`FunctionDeclaration`、`Schema`、`ToolConfig`、`Type`。

F-054: 文件 `libs/vertexai/pyproject.toml` 第206-214行 `filterwarnings` 配置忽略以下弃用警告：`ChatVertexAI`、`VertexAI`、`VertexAIEmbeddings`、`create_structured_runnable` 均被标记为弃用，推荐使用 `langchain_google_genai` 中的对应类。

## _VertexAIBase 与 _VertexAICommon（_base.py）

F-055: 文件 `libs/vertexai/langchain_google_vertexai/_base.py` 第57行，常量 `_DEFAULT_LOCATION = "us-central1"`。

F-056: 文件 `libs/vertexai/langchain_google_vertexai/_base.py` 第72行，类 `_VertexAIBase(BaseModel)`。

F-057: 文件 `libs/vertexai/langchain_google_vertexai/_base.py` 第77-131行，`_VertexAIBase` 字段：`project: str | None`、`location: str = "us-central1"`、`request_parallelism: int = 5`、`max_retries: int = 6`、`stop: list[str] | None`（别名 `stop_sequences`）、`model_name: str | None`（别名 `model`）、`full_model_name: str | None`（exclude）、`client_options`、`api_endpoint: str | None`（别名 `base_url`）、`api_transport: str | None`（别名 `transport`，`'grpc'` 或 `'rest'`）、`default_metadata`、`additional_headers`、`client_cert_source`、`credentials`（exclude）、`endpoint_version: Literal["v1","v1beta1"] = "v1beta1"`。

F-058: 文件 `libs/vertexai/langchain_google_vertexai/_base.py` 第139-162行，model_validator(mode="before") `validate_params_base`：将 `model` 重命名为 `model_name`；`api_transport` 从 `initializer.global_config._api_transport` 获取；`location` 从 `initializer.global_config.location` 获取；根据 location 构造 `api_endpoint`（`global` 时无前缀，否则 `{location}-aiplatform.googleapis.com`）；通过 `_get_client_options` 构建 client_options；`additional_headers` 转为 `default_metadata` 元组。

F-059: 文件 `libs/vertexai/langchain_google_vertexai/_base.py` 第164-171行，model_validator(mode="after") `validate_project`：若 `project is None`，先尝试 `credentials.project_id`，否则从 `initializer.global_config.project` 获取。

F-060: 文件 `libs/vertexai/langchain_google_vertexai/_base.py` 第173-201行，属性 `prediction_client` 和 `async_prediction_client`：懒加载，根据 `endpoint_version`（v1/v1beta1）通过 `_get_prediction_client`/`_get_async_prediction_client` 创建 `PredictionServiceClient`/`PredictionServiceAsyncClient`，传入 credentials、client_options、transport、user_agent。

F-061: 文件 `libs/vertexai/langchain_google_vertexai/_base.py` 第216行，类 `_VertexAICommon(_VertexAIBase)`。

F-062: 文件 `libs/vertexai/langchain_google_vertexai/_base.py` 第222-315行，`_VertexAICommon` 增加的模型参数字段：`temperature`、`frequency_penalty`、`presence_penalty`、`max_output_tokens`（别名 `max_tokens`）、`top_p`、`top_k`、`n: int = 1`、`seed`、`streaming: bool = False`、`safety_settings`、`tuned_model_name`、`response_modalities`、`thinking_budget: int | None`（0 禁用思考，-1 动态思考）、`include_thoughts`、`audio_timestamp`、`timeout: float | httpx.Timeout | None`。

## ChatVertexAI（chat_models.py）

F-063: 文件 `libs/vertexai/langchain_google_vertexai/chat_models.py` 第1008行，类 `ChatVertexAI(_VertexAICommon, BaseChatModel)`；模块 docstring 第1-4行说明这是 "Wrapper around Google VertexAI chat-based models"，支持 v1 和 v1beta1 端点。

F-064: 文件 `libs/vertexai/langchain_google_vertexai/chat_models.py` 第80-90行，同时从 `vertexai.generative_models` 导入 `Candidate as VertexCandidate`、`Tool as VertexTool`、`ToolConfig`、`SafetySettingsType`、`GenerationConfigType`、`GenerationResponse`、`_convert_schema_dict_to_gapic`；代码注释标注 "TODO: migrate to google-genai since this is deprecated"。

F-065: 文件 `libs/vertexai/langchain_google_vertexai/chat_models.py` 第94-123行，同时从 `google.cloud.aiplatform_v1.types` 和 `google.cloud.aiplatform_v1beta1.types` 导入两套 proto 类型（`Content`、`Part`、`FunctionCall`、`GenerateContentRequest`、`GenerationConfig`、`SafetySetting`、`Tool`、`ToolConfig` 等），v1beta1 额外包含 `Blob`、`CodeExecutionResult`、`ExecutableCode`、`FileData`、`VideoMetadata`、`HarmCategory`。

F-066: 文件 `libs/vertexai/langchain_google_vertexai/chat_models.py` 第2403-2422行，方法 `_generate_gemini(messages, stop, run_manager, **kwargs) -> ChatResult`：调用 `self._prepare_request_gemini(...)` 构建请求，通过 `_completion_with_retry(self.prediction_client.generate_content, max_retries=, run_manager=, wait_exponential_kwargs=, request=, metadata=, timeout=, **kwargs)` 执行，返回 `self._gemini_response_to_chat_result(response)`。

F-067: 文件 `libs/vertexai/langchain_google_vertexai/chat_models.py` 第2424-2444行，异步方法 `_agenerate_gemini` 调用 `self.async_prediction_client.generate_content`，通过 `_acompletion_with_retry` 包装。

F-068: 文件 `libs/vertexai/langchain_google_vertexai/chat_models.py` 第2446-2462行，方法 `get_num_tokens(text) -> int` 调用 `self.prediction_client.count_tokens({"endpoint": self.full_model_name, "model": self.full_model_name, "contents": contents})`。

F-069: 文件 `libs/vertexai/langchain_google_vertexai/chat_models.py` 第2658行，方法 `with_structured_output(...)`；第2905行，方法 `bind_tools(...)`——接口与 genai 包对应方法类似，但底层走 gapic/proto 路径。

## VertexAIEmbeddings（embeddings.py）

F-070: 文件 `libs/vertexai/langchain_google_vertexai/embeddings.py` 第30-39行，类 `VertexAIEmbeddings(BaseModel, Embeddings)` 被 `@typing_deprecated` 和 `@deprecated(since="3.2.0", removal="4.0.0", alternative_import="langchain_google_genai.GoogleGenerativeAIEmbeddings")` 双重装饰，标记为弃用。

F-071: 文件 `libs/vertexai/langchain_google_vertexai/embeddings.py` 第18-27行，类型别名 `EmbeddingTaskTypes` 为 Literal，包含 `RETRIEVAL_QUERY`、`RETRIEVAL_DOCUMENT`、`SEMANTIC_SIMILARITY`、`CLASSIFICATION`、`CLUSTERING`、`QUESTION_ANSWERING`、`FACT_VERIFICATION`、`CODE_RETRIEVAL_QUERY`。

F-072: 文件 `libs/vertexai/langchain_google_vertexai/embeddings.py` 第79-91行，model_validator `validate_environment`：要求 `model_name` 必须提供，否则抛出 `ValueError`；创建 `genai.Client(vertexai=True, project=, location=, credentials=)`——即弃用的 VertexAIEmbeddings 内部已迁移到统一的 `google-genai` SDK。

F-073: 文件 `libs/vertexai/langchain_google_vertexai/embeddings.py` 第93-120行，方法 `_get_embeddings_with_retry(texts, embeddings_type, dimensions, title)`：通过 `create_retry_decorator(max_retries=self.max_retries)` 创建重试装饰器，调用 `self.client.models.embed_content(model=, contents=texts, config=EmbedContentConfig(task_type=, output_dimensionality=, title=))`，返回 `[e.values for e in embeddings.embeddings]`。

F-074: 文件 `libs/vertexai/langchain_google_vertexai/embeddings.py` 第122行起，方法 `embed(texts, embeddings_task_type=None, dimensions=None, title=None) -> list[list[float]]` 是核心嵌入方法，docstring 说明 `QUESTION_ANSWERING`、`FACT_VERIFICATION` 仅 preview 模型支持，`dimensions` 仅 preview 模型支持。

## VertexAI 其他集成

F-075: 文件 `libs/vertexai/langchain_google_vertexai/__init__.py` 第12-21行模块 docstring 列出支持的集成：(1) Imagen 视觉模型（`VertexAIImageCaptioning` 等）；(2) Vertex Model Garden 第三方 MaaS 模型（Mistral、Llama、Anthropic，通过 `model_garden_maas`）；(3) Model Garden 自部署端点（`VertexAIModelGarden`）；(4) Vector Search（`VectorSearchVectorStore` 系列）；(5) Evaluators（`VertexPairWiseStringEvaluator`、`VertexStringEvaluator`）。

F-076: 文件 `libs/vertexai/langchain_google_vertexai/model_garden_maas/__init__.py` 导出 `get_vertex_maas_model`，子模块 `llama.py`、`mistral.py` 提供 `VertexModelGardenLlama`、`VertexModelGardenMistral`。

F-077: 文件 `libs/vertexai/langchain_google_vertexai/_anthropic_parsers.py` 和 `_anthropic_utils.py` 提供 Anthropic 在 Vertex AI 上的特殊解析逻辑；可选依赖 `anthropic>=0.35.0`。

F-078: 文件 `libs/vertexai/langchain_google_vertexai/vectorstores/vectorstores.py` 提供 `VectorSearchVectorStore`，`document_storage.py` 提供 `DataStoreDocumentStorage`、`GCSDocumentStorage`；依赖 `google-cloud-vectorsearch>=0.2.0`。

## langchain-google-community

F-079: 文件 `libs/community/langchain_google_community/__init__.py` 第1-79行，导出大量 Google 服务集成：BigQuery（`BigQueryLoader`、`BigQueryVectorStore`、`VertexFSVectorStore`）、Calendar 工具集、Gmail 工具集、Sheets 工具集、Tasks 工具集、Drive（`GoogleDriveLoader`）、GCS（`GCSDirectoryLoader`、`GCSFileLoader`）、Document AI（`DocAIParser`、`DocAIParsingResults`、`DocumentAIWarehouseRetriever`）、Vision（`CloudVisionLoader`、`CloudVisionParser`）、Speech-to-Text、Text-to-Speech、Translate、Search API、Places API、Geocoding、Vertex AI Search（`VertexAISearchRetriever`、`VertexAIMultiTurnSearchRetriever`、`VertexAISearchSummaryTool`）、Vertex Rank、Check Grounding、Model Armor（`ModelArmorSanitizePromptRunnable`、`ModelArmorSanitizeResponseRunnable`）、BigQuery 回调（`BigQueryCallbackHandler`、`AsyncBigQueryCallbackHandler`）。

F-080: 文件 `libs/community/langchain_google_community/model_armor/` 包含 `_client_utils.py`、`base_runnable.py`、`middleware.py`、`runnable.py`，提供 Google Model Armor 的提示/响应净化中间件。

F-081: 文件 `libs/community/langchain_google_community/bq_storage_vectorstores/` 包含 `_base.py`、`bigquery.py`、`featurestore.py`、`utils.py`，提供基于 BigQuery 和 Vertex Feature Store 的向量存储实现。

## 模型 Profile 与数据

F-082: 文件 `libs/genai/langchain_google_genai/data/_profiles.py` 和 `libs/vertexai/langchain_google_vertexai/data/_profiles.py` 均定义 `_PROFILES` 字典，配合 `profile_augmentations.toml` 提供模型能力元数据；AGENTS.md 说明 profile 通过主 langchain monorepo 的 `langchain-profiles` CLI 生成：`langchain-profiles refresh --provider google --data-dir <data目录>`。

F-083: 文件 `libs/genai/langchain_google_genai/chat_models.py` 第150行，`_MODEL_PROFILES = cast("ModelProfileRegistry", _PROFILES)`，类型为 `langchain_core.language_models.ModelProfileRegistry`。

## 测试与工具链

F-084: 两个包均使用 `pytest`，测试分 `tests/unit_tests/`（无网络调用，`pytest-socket` 禁用网络）和 `tests/integration_tests/`（需要 GCP 凭证）；`asyncio_mode = "auto"`；genai 包 addopts 含 `--benchmark-disable`，vertexai 包含 `--strict-markers --strict-config --durations=5`。

F-085: 文件 `AGENTS.md` 说明 Vertex 集成测试若因 GCP 凭证过期失败，需重新认证：`gcloud auth application-default login`；代码使用 `google.auth` 库，先查 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量，再查系统级认证。
