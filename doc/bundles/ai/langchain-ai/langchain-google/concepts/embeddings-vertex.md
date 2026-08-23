---
type: concept
scope: langchain-google
name: embeddings-vertex
version: "0.1.0"
source: https://github.com/langchain-ai/langchain-google
description: Google 嵌入模型——GoogleGenerativeAIEmbeddings 双后端、批处理与 task_type，VertexAIEmbeddings 弃用与内部迁移
---

# 嵌入模型与 Vertex AI

langchain-google 提供两个嵌入类，分别位于 genai 和 vertexai 两个包中。理解它们的关系是正确使用 Google 嵌入能力的关键。

## 两个嵌入类的现状

| 类 | 包 | 状态 | 底层 SDK | 后端 |
|---|---|---|---|---|
| `GoogleGenerativeAIEmbeddings` | `langchain-google-genai` | **推荐** | `google-genai` | Gemini API + Vertex AI（双后端） |
| `VertexAIEmbeddings` | `langchain-google-vertexai` | **弃用**（since 3.2.0, removal 4.0.0） | 内部已用 `google-genai` | 仅 Vertex AI |

`VertexAIEmbeddings` 虽然被 `@deprecated` 标记、推荐迁移到 `GoogleGenerativeAIEmbeddings`，但其内部实现**已经切换到 `genai.Client(vertexai=True, ...)`**（`libs/vertexai/.../embeddings.py:85`）。这是迁移过程中的支点策略：先让旧类内部跑在新 SDK 上验证稳定性，再引导用户换类。新代码应直接使用 `GoogleGenerativeAIEmbeddings`。

## GoogleGenerativeAIEmbeddings

### 类定义与字段

`GoogleGenerativeAIEmbeddings(BaseModel, Embeddings)` 位于 `libs/genai/.../embeddings.py:23`，继承 LangChain 的 `Embeddings` 接口（`embed_query`/`embed_documents`）。

核心字段：

| 字段 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `model` | `str` | 必填 | 嵌入模型名，如 `gemini-embedding-2-preview` |
| `task_type` | `str \| None` | `None` | 任务类型，影响嵌入质量（见下表） |
| `google_api_key` | `SecretStr \| None` | 从 `GOOGLE_API_KEY`/`GEMINI_API_KEY` 读取 | API key，别名 `api_key` |
| `vertexai` | `bool \| None` | `None` | 是否用 Vertex AI 后端，None 时自动检测 |
| `project` | `str \| None` | `None` | GCP 项目 ID（Vertex AI），回退 `GOOGLE_CLOUD_PROJECT` |
| `location` | `str \| None` | 从 `GOOGLE_CLOUD_LOCATION` 读取 | GCP 区域（Vertex AI），回退 `us-central1` |
| `output_dimensionality` | `int \| None` | `None` | 输出维度（仅 preview 模型支持 Matryoshka 降维） |
| `base_url` | `str \| None` | `None` | 自定义端点 |
| `api_version` | `str \| None` | `None` | 覆盖 API 版本段 |
| `client_args` | `dict \| None` | `None` | 传给底层 HTTP 客户端（如 SOCKS5 代理） |
| `request_options` | `dict \| None` | `None` | 请求选项（如 `{'timeout': 10}`） |

### 双后端与自动检测

与 `ChatGoogleGenerativeAI` 共享相同的后端检测逻辑（`embeddings.py:222` 的 `_determine_backend` validator）：

1. `vertexai` 参数显式值
2. `GOOGLE_GENAI_USE_VERTEXAI` 环境变量
3. `credentials` 存在 → Vertex AI
4. `project` 存在 → Vertex AI
5. 默认 Gemini Developer API

`_initialize_client` validator（`embeddings.py:248`）创建 `google.genai.Client`：Vertex AI 用 `Client(vertexai=True, project=, location=, credentials=, http_options=)`，Gemini API 用 `Client(api_key=, http_options=)`。HTTP headers 中包含 `user-agent: langchain-google-genai/<version>-GoogleGenerativeAIEmbeddings`。

### task_type：任务感知嵌入

Gemini 嵌入模型针对不同下游任务生成不同质量的嵌入向量，`task_type` 是关键参数：

| task_type | 适用场景 | 默认用于 |
|---|---|---|
| `RETRIEVAL_QUERY` | 检索中的查询 | `embed_query` |
| `RETRIEVAL_DOCUMENT` | 检索中的文档 | `embed_documents` |
| `SEMANTIC_SIMILARITY` | 语义文本相似度（STS） | — |
| `CLASSIFICATION` | 文本分类 | — |
| `CLUSTERING` | 聚类 | — |
| `QUESTION_ANSWERING` | 问答（仅 preview 模型） | — |
| `FACT_VERIFICATION` | 事实验证（仅 preview 模型） | — |
| `CODE_RETRIEVAL_QUERY` | 代码检索（Java/Python） | — |
| `TASK_TYPE_UNSPECIFIED` | 未指定 | — |

`embed_query` 默认使用 `RETRIEVAL_QUERY`，`embed_documents` 默认使用 `RETRIEVAL_DOCUMENT`（`embeddings.py:420,486`）。这一默认值区分至关重要——查询和文档使用不同 task_type 才能获得最佳检索效果。可在构造时设 `task_type`，也可在调用时通过参数覆盖。

### 批处理策略

两个常量控制批处理（`embeddings.py:19-20`）：

- `_MAX_TOKENS_PER_BATCH = 20000`：每批最大 token 数
- `_DEFAULT_BATCH_SIZE = 100`：每批最大文本条数

静态方法 `_prepare_batches(texts, batch_size)`（`embeddings.py:321`）的切分逻辑：
- 遍历文本，用 `_split_by_punctuation` 辅助估算 token
- 当单条文本超过 20000 token 时独立成批（API 会处理长文本）
- 当累计 token 超过 20000 或当前批达到 `batch_size`（100）时切批
- 返回 `list[list[str]]`

`embed_documents` 逐批调用 `self.client.models.embed_content(model=, contents=[{"parts":[{"text":...}]}...], config=)`，将各批结果拼接。`title` 仅在单文本批次时传入（Gemini API 的 title 适用于 RETRIEVAL_DOCUMENT 场景）。

### 维度缩减（Matryoshka）

`output_dimensionality` 参数（构造级）和 `dimensions` 参数（调用级，仅 `VertexAIEmbeddings`）支持截断嵌入维度，利用 Matryoshka 表示学习——短向量仍保留大部分语义信息，可降低存储和检索成本。仅 preview 模型支持。

### 异步支持

`aembed_query`（`embeddings.py:582`）和 `aembed_documents`（`embeddings.py:512`）使用 `self.client.aio.models.embed_content`，与同步版本逻辑对称。

### 文本-only 限制

docstring 明确警告（`embeddings.py:26-32`）：虽然 `gemini-embedding-2-preview` 原生支持多模态（文本、图片、视频、音频、PDF），但 LangChain `Embeddings` 接口仅接受文本。多模态嵌入需直接使用 `google-genai` SDK。

## VertexAIEmbeddings（弃用类）

### 弃用标记

```python
@typing_deprecated("Use GoogleGenerativeAIEmbeddings instead.")
@deprecated(since="3.2.0", removal="4.0.0",
            alternative_import="langchain_google_genai.GoogleGenerativeAIEmbeddings")
class VertexAIEmbeddings(BaseModel, Embeddings):
```

### 与 GoogleGenerativeAIEmbeddings 的差异

| 维度 | VertexAIEmbeddings | GoogleGenerativeAIEmbeddings |
|---|---|---|
| 后端 | 仅 Vertex AI | Gemini API + Vertex AI |
| 客户端 | `genai.Client(vertexai=True, ...)` | 自动选择 |
| 默认 location | `us-central1` | 回退 `us-central1`/`global` |
| 核心方法 | `embed(texts, embeddings_task_type=, dimensions=, title=)` | `embed_query`/`embed_documents`（标准接口） |
| 重试 | `create_retry_decorator`（tenacity 指数退避） | 委托 google-genai SDK 重试 |
| 配置 | `extra="forbid"`（严格禁止额外字段） | 较宽松 |

`VertexAIEmbeddings.embed()`（`embeddings.py:122`）是其核心方法，通过 `_get_embeddings_with_retry`（`embeddings.py:93`）调用 `self.client.models.embed_content`，配置 `EmbedContentConfig(task_type=, output_dimensionality=, title=)`。`embed_query` 和 `embed_documents` 作为标准接口适配方法委托给 `embed`。

### Vertex AI 鉴权

使用 `VertexAIEmbeddings` 或 `GoogleGenerativeAIEmbeddings(vertexai=True)` 时，鉴权由 `google.auth` 库处理，查找顺序：

1. `credentials` 参数传入的 `google.auth.credentials.Credentials` 对象
2. `GOOGLE_APPLICATION_CREDENTIALS` 环境变量（服务账号 JSON 路径）
3. gcloud CLI 凭证（`gcloud auth application-default login`）
4. GCE/GKE/Cloud Run 等环境的元服务器凭证

测试时若 Vertex 集成测试因凭证过期失败，需重新运行 `gcloud auth application-default login`。

## Vertex AI 上的其他嵌入相关能力

### Vector Search

`langchain_google_vertexai.vectorstores` 提供 `VectorSearchVectorStore`、`VectorSearchVectorStoreDatastore`、`VectorSearchVectorStoreGCS`，对接 Vertex AI Vector Search（原 Matching Engine），支持批量索引和近似最近邻搜索。文档存储可对接 Datastore 或 GCS（`DataStoreDocumentStorage`、`GCSDocumentStorage`）。依赖 `google-cloud-vectorsearch>=0.2.0`，v2 功能需安装 `vectorsearch_v2` 可选依赖。

### BigQuery 向量存储

`langchain_google_community` 提供 `BigQueryVectorStore` 和 `VertexFSVectorStore`（基于 BigQuery 和 Vertex Feature Store），适合数据已在 BigQuery 中的场景。

### Community 检索器

`langchain_google_community` 还提供 `VertexAISearchRetriever`、`VertexAIMultiTurnSearchRetriever`（Vertex AI Search 接地搜索）和 `VertexAIRank`（重排序）。

## 使用建议

1. **新项目**：统一使用 `GoogleGenerativeAIEmbeddings`，通过 `vertexai=True` + `project` 访问 Vertex AI 后端。
2. **RAG 场景**：文档入库用默认的 `RETRIEVAL_DOCUMENT`，查询用默认的 `RETRIEVAL_QUERY`，不要混用。
3. **大批量嵌入**：利用内置批处理（每批 100 条/20000 token），无需手动分批；异步用 `aembed_documents`。
4. **降维**：若存储成本敏感且使用 preview 模型，设置 `output_dimensionality` 截断向量。
5. **多模态嵌入**：当前 LangChain 接口不支持，直接用 `google-genai` SDK 的 `client.models.embed_content` 传入多模态 Part。

## 进一步阅读

- [总览](/ai/langchain-ai/langchain-google/concepts/overview)
- [聊天模型架构](/ai/langchain-ai/langchain-google/concepts/chat-models)
- [API 参考](/ai/langchain-ai/langchain-google/references/api)
- [基础使用示例](/ai/langchain-ai/langchain-google/examples/basic-usage)
