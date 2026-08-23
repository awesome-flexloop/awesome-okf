---
type: concept
scope: langchain-mongodb
name: vector-store
version: "0.11.0"
source: https://github.com/langchain-ai/langchain-mongodb
description: MongoDBAtlasVectorSearch 架构——向量存储、搜索管道、索引管理与检索器生态
---

# 向量存储架构

## MongoDBAtlasVectorSearch 概述

`MongoDBAtlasVectorSearch` 是 langchain-mongodb 的核心类，继承自 `langchain_core.vectorstores.VectorStore`。它将文本、元数据和嵌入向量存储在同一个 MongoDB 文档中，通过 Atlas Vector Search 的 HNSW（Hierarchical Navigable Small Worlds）算法执行近似最近邻搜索。

### 文档结构

存储在 MongoDB 中的每个文档具有以下结构：

```javascript
{
  "_id": ObjectId("..."),        // 文档主键（LangChain 中以字符串表示）
  "text": "文档内容文本",         // text_key 字段，默认 "text"
  "embedding": [0.12, ...],     // embedding_key 字段，默认 "embedding"（AutoEmbedding 模式下无此字段）
  // ... 任意元数据字段
}
```

元数据直接作为文档的顶级字段存储，这使得元数据过滤可以利用 MongoDB 的索引能力。

## 两种嵌入模式

### 客户端嵌入模式

传入 `Embeddings` 实例（如 `OpenAIEmbeddings`），文本在 Python 客户端转换为向量后发送给 MongoDB：

```python
from langchain_openai import OpenAIEmbeddings

vectorstore = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=OpenAIEmbeddings(),
    index_name="vector_index",
    embedding_key="embedding",
    relevance_score_fn="cosine",
    dimensions=1536,
)
```

- `embed_documents` 在批量插入时调用
- `embed_query` 在搜索时调用
- 嵌入向量通过网络传输到 MongoDB

### Atlas Auto-Embedding 模式

传入模型名称字符串，嵌入生成完全由 Atlas 服务端管理：

```python
vectorstore = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding="voyage-ai-3-large",  # 字符串触发 AutoEmbeddings
    index_name="vector_index",
    embedding_key=None,             # 必须为 None
    relevance_score_fn=None,        # 必须为 None
    dimensions=-1,                  # 必须为 -1
)
```

AutoEmbedding 模式下：
- 插入时只发送文本，不发送向量
- 查询时 `$vectorSearch` 的 query 字段是文本字符串而非浮点数组
- 嵌入模型由索引定义绑定，不可在运行时切换
- `embed_documents` 和 `embed_query` 调用会抛出 `NotImplementedError`

## 搜索管道构建

所有搜索操作最终构建为 MongoDB 聚合管道，在 `_similarity_search_with_score` 方法中组装：

### 基础相似度搜索管道

```python
pipeline = [
    # 1. 向量搜索阶段
    vector_search_stage(
        query_vector=embedded_query,
        search_field="embedding",
        index_name="vector_index",
        top_k=k,
        filter=pre_filter,
        oversampling_factor=10,
        **kwargs
    ),
    # 2. 提取分数
    {"$set": {"score": {"$meta": "vectorSearchScore"}}},
    # 3. 可选：原生重排序（MongoDB 8.3+）
    # rerank_stage(query, rerank_path, num_docs_to_rerank, model),
    # 4. 默认去除嵌入向量
    {"$project": {"embedding": 0}},
    # 5. rerank 后截断
    # {"$limit": k},
    # 6. 用户自定义后处理管道
    # *post_filter_pipeline,
]
```

### pre_filter 与 post_filter_pipeline

- **pre_filter**：MQL 匹配表达式，在 `$vectorSearch` 阶段执行。利用索引字段缩小搜索范围，减少需要计算相似度的文档数。需要在向量索引定义中将过滤字段声明为 `{"type": "filter"}`。
- **post_filter_pipeline**：搜索完成后的任意聚合阶段列表，可用于投影、分组、排序等复杂后处理。

### oversampling_factor

HNSW 算法在每一步选择 `k × oversampling_factor` 个候选，再精排得到最终 k 个结果。默认值 10 在召回率和延迟之间取得平衡。增大此值可提高召回率但增加计算开销。

### 分数归一化

Atlas Vector Search 的分数已归一化到 [0, 1]，因此 `_select_relevance_score_fn` 返回恒等函数，无需额外转换。分数 1 表示完全相似，0 表示正交（对 cosine/dotProduct）或最远（对 euclidean）。

## MMR（最大边际相关性）搜索

MMR 搜索用于在相似度和结果多样性之间取得平衡。实现分两步：

1. **召回阶段**：以 `fetch_k`（默认 20）调用 `_similarity_search_with_score`，请求包含嵌入向量
2. **重排阶段**：在 Python 端使用 `utils.maximal_marginal_relevance` 计算 MMR

MMR 公式：

```
MMR = argmax_{D_i ∈ R \ S} [λ · Sim(D_i, Q) - (1-λ) · max_{D_j ∈ S} Sim(D_i, D_j)]
```

- `λ = 1`（lambda_mult=1）：纯相关性，等同于普通相似度搜索
- `λ = 0`（lambda_mult=0）：纯多样性，优先选择彼此不同的文档
- 默认 `λ = 0.5`：平衡相关性和多样性

余弦相似度计算优先使用 `simsimd` 库（高性能 SIMD 实现），未安装时回退到 NumPy。

## 批量写入机制

`add_texts` 和 `add_documents` 实现了智能分批：

- **按文档数分批**：默认每批 100 个文档（`DEFAULT_INSERT_BATCH_SIZE`）
- **按字节大小提前切批**：累积文本和元数据大小达到 47MB 时立即切批

47MB 阈值的设计考虑了：
- MongoDB 单个文档 16MB 限制
- BSON 编码开销（嵌入向量浮点数、字段名）
- 批量插入命令本身的大小限制

实际嵌入计算和插入委托给 `pymongo_search_utils.bulk_embed_and_insert_texts` 函数。

## 索引管理

### 自动创建

构造函数的 `auto_create_index` 参数控制自动建索引行为：

| auto_create_index | dimensions | 行为 |
|---|---|---|
| `False` | 任意 | 不创建索引 |
| `None` | -1 且非 AutoEmbedding | 不创建索引 |
| `None` | > -1 或 AutoEmbedding | 自动创建 |
| `True` | 任意 | 自动创建 |

创建前检查 `collection.list_search_indexes()` 是否已有同名索引，避免重复创建。

### 索引定义

向量搜索索引定义格式：

```python
{
    "fields": [
        {
            "numDimensions": 1536,
            "path": "embedding",
            "similarity": "cosine",  # 或 "euclidean"、"dotProduct"
            "type": "vector",
        },
        # filter 字段
        {"type": "filter", "path": "genre"},
        {"type": "filter", "path": "year"},
    ]
}
```

### 索引就绪等待

`create_vector_search_index` 支持 `wait_until_complete` 参数，通过 `_wait_for_predicate` 轮询 `list_search_indexes` 的 status 字段，直到状态变为 "READY" 或超时。

## 检索器生态

MongoDBAtlasVectorSearch 可通过 `as_retriever()` 转为标准 LangChain Retriever，此外还有五种专用检索器：

| 检索器 | 搜索方式 | 适用场景 |
|---|---|---|
| VectorStore.as_retriever() | 纯向量相似度/MMR | 语义搜索 |
| `MongoDBAtlasFullTextSearchRetriever` | BM25 全文搜索 | 关键词精确匹配 |
| `MongoDBAtlasHybridSearchRetriever` | 向量 + 全文 RRF 融合 | 综合搜索质量 |
| `MongoDBAtlasParentDocumentRetriever` | 子块向量搜索 → 父文档返回 | 需要更宽上下文 |
| `MongoDBAtlasSelfQueryRetriever` | LLM 推导元数据过滤器 | 结构化元数据查询 |

### 混合搜索的 RRF 融合

混合检索器分别执行向量搜索和全文搜索，各自计算 RRF 分数后合并：

```
RRF_score = weight × (1 / (rank + penalty + 1))
```

默认 `vector_penalty=60`、`fulltext_penalty=60`、`vector_weight=1.0`、`fulltext_weight=1.0`。penalty 越大，排名靠前的结果优势越小，融合越均衡。

### 父文档检索的同集合设计

父文档检索器在**同一个 Collection** 中存储父文档和子文档块：
- 子文档：包含 `embedding` 字段和 `metadata.doc_id` 指向父文档
- 父文档：无 `embedding` 字段，无 `metadata.doc_id`

通过 `$lookup` 自连接和 `$match: {"metadata.doc_id": {$exists: false}}` 区分父子，用 `$group` 去重确保同一父文档只返回一次。

## 原生重排序（$rerank）

MongoDB 8.3+ 支持 Atlas 原生重排序，使用 Voyage AI 模型（如 "rerank-2.5"）：

```python
results = vectorstore.similarity_search_with_score(
    query="...",
    k=5,
    rerank_path="text",           # 启用 $rerank
    rerank_model="rerank-2.5",    # 可选，默认最新
    num_docs_to_rerank=20,        # 传给重排器的候选数（≤1000）
)
```

管道中 `$rerank` 阶段在向量搜索之后执行，先用较大候选数召回，再由重排序模型精排，最后 `$limit` 截断到 k。这一能力在 VectorStore、FullTextRetriever、HybridRetriever、ParentDocumentRetriever、SelfQueryRetriever 中均可用。

## ID 处理

LangChain 层面使用字符串 ID，MongoDB 内部使用 ObjectId：

- **写入**：用户提供的字符串 ID 通过 `str_to_oid` 尝试转换为 ObjectId；非 24 字符十六进制字符串则原样存储
- **读取**：MongoDB 返回的 ObjectId 通过 `oid_to_str` 转为字符串
- **自动生成**：未提供 ID 时使用 `str(ObjectId())` 生成

`make_serializable` 递归将结果中的 ObjectId 转为字符串、datetime 转为 ISO 格式，确保 Document 元数据可 JSON 序列化。

## 相关阅读

- [总览](/ai/langchain-ai/langchain-mongodb/concepts/overview)
- [缓存与聊天历史](/ai/langchain-ai/langchain-mongodb/concepts/chat-history-cache)
- [API 参考 — MongoDBAtlasVectorSearch](/ai/langchain-ai/langchain-mongodb/references/api)
- [基础使用示例](/ai/langchain-ai/langchain-mongodb/examples/basic-usage)
