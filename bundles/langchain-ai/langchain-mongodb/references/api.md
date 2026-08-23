---
type: reference
scope: langchain-mongodb
name: api
version: "0.11.0"
source: https://github.com/langchain-ai/langchain-mongodb
description: langchain-mongodb 核心 API 参考——类、方法签名与关键参数
---

# langchain-mongodb API 参考

本文档覆盖 `langchain-mongodb` v0.11.0 的核心公共 API。所有类均从顶层包或子模块导入。

## 顶层导出

```python
from langchain_mongodb import (
    MongoDBAtlasVectorSearch,
    MongoDBChatMessageHistory,
    MongoDBCache,
    MongoDBAtlasSemanticCache,
)
```

来源：`langchain_mongodb/__init__.py:11-19`。

---

## MongoDBAtlasVectorSearch

**模块路径**：`langchain_mongodb.vectorstores.MongoDBAtlasVectorSearch`

**继承**：`langchain_core.vectorstores.VectorStore`

基于 MongoDB Atlas Vector Search（HNSW 算法）的向量存储实现。

### 构造函数

```python
MongoDBAtlasVectorSearch(
    collection: Collection[Dict[str, Any]],
    embedding: Embeddings | str,
    index_name: str = "vector_index",
    text_key: str | List[str] = "text",
    *,
    embedding_key: str | None = "embedding",
    relevance_score_fn: str | None = "cosine",
    dimensions: int = -1,
    auto_create_index: bool | None = None,
    auto_index_timeout: int = 15,
    vector_index_options: dict | None = None,
    **kwargs: Any,
)
```

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `collection` | `pymongo.Collection` | 必填 | MongoDB 集合实例 |
| `embedding` | `Embeddings \| str` | 必填 | 嵌入模型；传入字符串时自动创建 `AutoEmbeddings`（服务端嵌入） |
| `index_name` | `str` | `"vector_index"` | Atlas Vector Search 索引名 |
| `text_key` | `str \| List[str]` | `"text"` | 存储文本的字段名；列表时取第一个 |
| `embedding_key` | `str \| None` | `"embedding"` | 嵌入向量字段名；AutoEmbedding 模式必须为 `None` |
| `relevance_score_fn` | `str \| None` | `"cosine"` | 相似度函数：`"cosine"`、`"euclidean"`、`"dotProduct"`；AutoEmbedding 必须为 `None` |
| `dimensions` | `int` | `-1` | 嵌入维度；-1 时自动推断；AutoEmbedding 必须为 `-1` |
| `auto_create_index` | `bool \| None` | `None` | 是否自动创建索引；None 时在 dimensions > -1 或 AutoEmbedding 时自动创建 |
| `auto_index_timeout` | `int` | `15` | 等待索引就绪的超时秒数 |
| `vector_index_options` | `dict \| None` | `None` | 传递给索引定义的额外选项 |

**异常**：AutoEmbedding 模式下若 `embedding_key`、`dimensions`、`relevance_score_fn` 不满足约束，抛出 `pymongo.errors.ConfigurationError`。

### 类方法

#### from_connection_string

```python
@classmethod
from_connection_string(
    connection_string: str,
    namespace: str,
    embedding: Embeddings,
    **kwargs: Any,
) -> MongoDBAtlasVectorSearch
```

从 MongoDB 连接 URI 构造实例。`namespace` 格式为 `"database.collection"`。

#### from_texts

```python
@classmethod
from_texts(
    texts: List[str],
    embedding: Embeddings | str,
    metadatas: Optional[List[Dict]] = None,
    collection: Optional[Collection] = None,
    ids: Optional[List[str]] = None,
    **kwargs: Any,
) -> MongoDBAtlasVectorSearch
```

从原始文本快速构造并写入。必须提供 `collection` 参数，否则抛出 `ValueError`。

### 实例方法

#### add_texts

```python
add_texts(
    texts: Iterable[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    ids: Optional[List[str]] = None,
    batch_size: int = 100,
    **kwargs: Any,
) -> List[str]
```

批量添加文本。自动按 `batch_size` 分批，并在累积字节 ≥ 47MB 时提前切批。返回插入的 ID 列表。

#### add_documents

```python
add_documents(
    documents: List[Document],
    ids: Optional[List[str]] = None,
    batch_size: int = 100,
    **kwargs: Any,
) -> List[str]
```

添加 LangChain Document 列表。未提供 ids 时使用 `doc.id or str(ObjectId())`。

#### similarity_search

```python
similarity_search(
    query: str,
    k: int = 4,
    pre_filter: Optional[Dict[str, Any]] = None,
    post_filter_pipeline: Optional[List[Dict]] = None,
    oversampling_factor: int = 10,
    include_scores: bool = False,
    include_embeddings: bool = False,
    **kwargs: Any,
) -> List[Document]
```

相似度搜索。`pre_filter` 为 MQL 匹配表达式，在向量搜索阶段执行；`post_filter_pipeline` 为搜索后的聚合管道。`oversampling_factor` 控制 HNSW 候选数（k × oversampling_factor）。

#### similarity_search_with_score

```python
similarity_search_with_score(
    query: str,
    k: int = 4,
    pre_filter: Optional[Dict[str, Any]] = None,
    post_filter_pipeline: Optional[List[Dict]] = None,
    oversampling_factor: int = 10,
    include_embeddings: bool = False,
    **kwargs: Any,
) -> List[Tuple[Document, float]]
```

返回文档和归一化到 [0,1] 的相似度分数。

#### max_marginal_relevance_search

```python
max_marginal_relevance_search(
    query: str,
    k: int = 4,
    fetch_k: int = 20,
    lambda_mult: float = 0.5,
    pre_filter: Optional[Dict[str, Any]] = None,
    post_filter_pipeline: Optional[List[Dict]] = None,
    **kwargs: Any,
) -> List[Document]
```

MMR 搜索。`fetch_k` 为候选数，`lambda_mult` 控制相关性（1.0）与多样性（0.0）的权衡。

#### delete

```python
delete(ids: Optional[List[str]] = None, **kwargs: Any) -> Optional[bool]
```

按 ID 删除文档。字符串 ID 自动尝试转换为 ObjectId。

#### create_vector_search_index

```python
create_vector_search_index(
    dimensions: int = -1,
    filters: Optional[List[str]] = None,
    update: bool = False,
    wait_until_complete: Optional[float] = None,
    vector_index_options: dict | None = None,
    **kwargs: Any,
) -> None
```

编程式创建 Atlas Vector Search 索引。`filters` 为需要索引为 filter 类型的字段名列表。

#### as_retriever

继承自 `VectorStore`，支持 `search_type` 为 `"similarity"`（默认）、`"mmr"`、`"similarity_score_threshold"`。

#### close()

关闭底层 MongoClient。

---

## MongoDBChatMessageHistory

**模块路径**：`langchain_mongodb.chat_message_histories.MongoDBChatMessageHistory`

**继承**：`langchain_core.chat_history.BaseChatMessageHistory`

将聊天消息历史持久化到 MongoDB。

### 构造函数

```python
MongoDBChatMessageHistory(
    connection_string: Optional[str],
    session_id: str,
    database_name: str = "chat_history",
    collection_name: str = "message_store",
    *,
    session_id_key: str = "SessionId",
    history_key: str = "History",
    create_index: bool = True,
    history_size: Optional[int] = None,
    index_kwargs: Optional[Dict] = None,
    client: Optional[MongoClient] = None,
)
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `connection_string` | 必填 | MongoDB URI；与 `client` 二选一 |
| `session_id` | 必填 | 会话标识 |
| `database_name` | `"chat_history"` | 数据库名 |
| `collection_name` | `"message_store"` | 集合名 |
| `session_id_key` | `"SessionId"` | 会话 ID 字段名 |
| `history_key` | `"History"` | 消息内容字段名（JSON 字符串） |
| `create_index` | `True` | 是否在 session_id_key 上建索引 |
| `history_size` | `None` | 只保留最近 N 条消息；None 为全部 |
| `client` | `None` | 已有的 MongoClient 实例 |

### 属性与方法

- **`messages: List[BaseMessage]`**（property）：检索消息列表。设置 `history_size` 时自动 skip 旧消息。
- **`add_message(message: BaseMessage) -> None`**：追加单条消息。
- **`add_messages(messages: List[BaseMessage])`**：批量追加（继承自基类）。
- **`clear() -> None`**：删除当前会话所有消息。
- **`close() -> None`**：关闭客户端。

每条消息存储为独立文档：`{SessionId: "...", History: "<json>"}`。

---

## MongoDBCache

**模块路径**：`langchain_mongodb.cache.MongoDBCache`

**继承**：`langchain_core.caches.BaseCache`

基于精确匹配（prompt + llm_string）的 LLM 响应缓存。

### 构造函数

```python
MongoDBCache(
    connection_string: str,
    collection_name: str = "default",
    database_name: str = "default",
    **kwargs: Dict[str, Any],
)
```

构造时若集合不存在则自动创建，并在 `[prompt, llm]` 上建复合索引。

### 方法

- **`lookup(prompt: str, llm_string: str) -> Optional[RETURN_VAL_TYPE]`**：精确查找。
- **`update(prompt: str, llm_string: str, return_val: RETURN_VAL_TYPE) -> None`**：upsert 缓存条目。
- **`clear(**kwargs) -> None`**：清除缓存，kwargs 作为删除过滤条件（如 `clear(llm_string="gpt-4")`）。
- **`close() -> None`**。

---

## MongoDBAtlasSemanticCache

**模块路径**：`langchain_mongodb.cache.MongoDBAtlasSemanticCache`

**继承**：`BaseCache`, `MongoDBAtlasVectorSearch`（多继承）

基于向量语义相似度的 LLM 响应缓存。

### 构造函数

```python
MongoDBAtlasSemanticCache(
    connection_string: str,
    embedding: Embeddings,
    collection_name: str = "default",
    database_name: str = "default",
    index_name: str = "default",
    wait_until_ready: Optional[float] = None,
    score_threshold: Optional[float] = None,
    **kwargs: Dict[str, Any],
)
```

| 参数 | 说明 |
|---|---|
| `wait_until_ready` | 写入后等待索引可查询的秒数 |
| `score_threshold` | 相似度阈值；低于此分数的缓存不命中 |

### 方法

- **`lookup(prompt, llm_string)`**：向量搜索 top-1，通过 `pre_filter` 匹配 llm_string，可选 score_threshold 后过滤。
- **`update(prompt, llm_string, return_val, wait_until_ready=None)`**：将 prompt 作为文本、序列化结果作为 metadata 写入 VectorStore。
- **`clear(**kwargs)`**。

---

## MongoDBRecordManager

**模块路径**：`langchain_mongodb.indexes.MongoDBRecordManager`

**继承**：`langchain_core.indexing.base.RecordManager`

用于 LangChain indexing API 的文档写入状态跟踪器。

### 构造函数

```python
MongoDBRecordManager(collection: Collection)
```

namespace 自动设为 `"{database_name}.{collection_name}"`。

### 类方法

```python
@classmethod
from_connection_string(connection_string: str, namespace: str) -> MongoDBRecordManager
```

### 方法

| 方法 | 说明 |
|---|---|
| `create_schema() -> None` | 空实现（MongoDB 无需预定义 schema） |
| `update(keys, *, group_ids=None, time_at_least=None) -> None` | upsert 文档时间戳 |
| `exists(keys) -> List[bool]` | 批量检查 key 是否存在 |
| `list_keys(*, before=None, after=None, group_ids=None, limit=None) -> List[str]` | 按时间范围列出 key |
| `delete_keys(keys) -> None` | 批量删除 |
| `get_time() -> float` | 获取服务器时间戳 |
| 对应 `a*` 异步版本 | 通过 `run_in_executor` 包装 |

---

## MongoDBDocStore

**模块路径**：`langchain_mongodb.docstores.MongoDBDocStore`

**继承**：`langchain_core.stores.BaseStore[str, Document]`

基于 MongoDB 的键值文档存储。使用 `_id` 作为键，`page_content` 字段存储文本。

### 构造函数

```python
MongoDBDocStore(collection: Collection, text_key: str = "page_content")
```

### 方法

- **`mget(keys: Sequence[str]) -> list[Optional[Document]]`**：批量获取，缺失键返回 None。
- **`mset(key_value_pairs, batch_size=100) -> None`**：批量设置。
- **`mdelete(keys) -> None`**：批量删除。
- **`yield_keys(*, prefix=None) -> Iterator[str]`**：前缀匹配迭代键。

---

## 检索器

所有检索器位于 `langchain_mongodb.retrievers`。

### MongoDBAtlasFullTextSearchRetriever

基于 Lucene BM25 的全文检索。

```python
MongoDBAtlasFullTextSearchRetriever(
    *,
    collection: Collection,
    search_index_name: str,
    search_field: str | List[str],
    k: Optional[int] = None,
    filter: Optional[Dict[str, Any]] = None,
    include_scores: bool = True,
    rerank_path: Optional[str | List[str]] = None,
    rerank_model: Optional[str] = None,
    num_docs_to_rerank: Optional[int] = None,
    auto_create_index: bool = True,
    auto_index_timeout: int = 15,
)
```

### MongoDBAtlasHybridSearchRetriever

结合向量搜索和全文搜索，通过 RRF 融合。

```python
MongoDBAtlasHybridSearchRetriever(
    *,
    vectorstore: MongoDBAtlasVectorSearch,
    search_index_name: str,
    k: int = 4,
    oversampling_factor: int = 10,
    pre_filter: Optional[Dict] = None,
    post_filter: Optional[List[Dict]] = None,
    vector_penalty: float = 60.0,
    fulltext_penalty: float = 60.0,
    vector_weight: float = 1.0,
    fulltext_weight: float = 1.0,
    show_embeddings: bool = False,
    rerank_path: Optional[str | List[str]] = None,
    rerank_model: Optional[str] = None,
    num_docs_to_rerank: Optional[int] = None,
    auto_create_index: bool = True,
)
```

### MongoDBAtlasParentDocumentRetriever

父子文档检索，同一集合存储父文档和子块。

```python
@classmethod
from_connection_string(
    connection_string: str,
    embedding_model: Embeddings,
    child_splitter: TextSplitter,
    database_name: str,
    collection_name: str = "document_with_chunks",
    id_key: str = "doc_id",
    auto_create_index: bool = True,
    search_index_name: str = "text_index",
) -> MongoDBAtlasParentDocumentRetriever
```

### MongoDBAtlasSelfQueryRetriever

使用 LLM 从自然语言查询中推导结构化过滤器。

```python
@classmethod
from_llm(
    llm: BaseLanguageModel,
    vectorstore: VectorStore,
    document_contents: str,
    metadata_field_info: Sequence[Union[AttributeInfo, dict]],
    enable_limit: bool = False,
    use_original_query: bool = False,
    **kwargs: Any,
) -> SelfQueryRetriever
```

使用 `MongoDBStructuredQueryTranslator` 将 LangChain StructuredQuery 翻译为 MQL。支持比较器：`eq, ne, gt, gte, lt, lte, in, nin`；运算符：`and, or`。

---

## Agent Toolkit

**模块路径**：`langchain_mongodb.agent_toolkit`

### MongoDBDatabaseToolkit

```python
MongoDBDatabaseToolkit(db: MongoDBDatabase, llm: BaseLanguageModel)
```

`get_tools()` 返回四个工具：
1. `QueryMongoDBDatabaseTool` — 执行 MongoDB 查询
2. `InfoMongoDBDatabaseTool` — 获取集合 schema 和样例行
3. `ListMongoDBDatabaseTool` — 列出所有集合
4. `QueryMongoDBCheckerTool` — 用 LLM 校验查询正确性

系统提示模板：`MONGODB_AGENT_SYSTEM_PROMPT`（从 `langchain_mongodb.agent_toolkit` 导入）。

---

## 索引管理函数

**模块路径**：`langchain_mongodb.index`

```python
from langchain_mongodb.index import (
    create_vector_search_index,
    update_vector_search_index,
    drop_vector_search_index,
    create_fulltext_search_index,
)
```

这些函数重新导出自 `pymongo_search_utils`，用于编程式管理 Atlas Search 索引。

## 管道构建函数

**模块路径**：`langchain_mongodb.pipelines`

```python
from langchain_mongodb.pipelines import (
    vector_search_stage,
    autoembedding_vector_search_stage,
    text_search_stage,
    rerank_stage,
    combine_pipelines,
    reciprocal_rank_stage,
    final_hybrid_stage,
)
```

`rerank_stage(query, path, num_docs_to_rerank, model=None)` 为本库特有实现（需 MongoDB 8.3+），其余重新导出自 `pymongo_search_utils`。
