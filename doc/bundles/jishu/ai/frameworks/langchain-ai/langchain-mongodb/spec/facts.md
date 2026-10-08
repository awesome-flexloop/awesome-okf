---
type: spec
scope: langchain-mongodb
name: facts
version: "0.11.0"
source: https://github.com/langchain-ai/langchain-mongodb
description: langchain-mongodb 源码事实验证清单
---

# langchain-mongodb 事实清单

## 项目元信息

F-001: 文件 `libs/langchain-mongodb/pyproject.toml` 第7-11行，项目名称为 `langchain-mongodb`，版本 `0.11.0`，描述为 "An integration package connecting MongoDB and LangChain"，要求 Python >= 3.11，构建后端为 hatchling (>1.24)。

F-002: 文件 `libs/langchain-mongodb/pyproject.toml` 第12-21行，运行时依赖包括：`langchain-core>=1.2.5`、`langchain>=1.0`、`langchain-classic>=1.0`、`pymongo>=4.6.1`、`langchain-text-splitters>=1.0`、`numpy>=1.26`、`lark<2.0.0,>=1.1.9`、`pymongo-search-utils>=0.3.0`。

F-003: 文件 `libs/langchain-mongodb/pyproject.toml` 第48-52行，可选依赖组 `viz` 包含 `networkx>=3.0` 和 `holoviews>=1.19`，用于 GraphRAG 可视化。

## 公共 API（langchain_mongodb/__init__.py）

F-004: 文件 `langchain_mongodb/__init__.py` 第11-19行，从子模块导入四个公共类：`MongoDBAtlasSemanticCache`（来自 cache）、`MongoDBCache`（来自 cache）、`MongoDBChatMessageHistory`（来自 chat_message_histories）、`MongoDBAtlasVectorSearch`（来自 vectorstores）。`__all__` 列表恰好包含这四个类名。

## MongoDBAtlasVectorSearch（vectorstores.py）

F-005: 文件 `langchain_mongodb/vectorstores.py` 第58行，类 `MongoDBAtlasVectorSearch` 继承自 `langchain_core.vectorstores.VectorStore`。模块文档字符串说明其基于 HNSW（Hierarchical Navigable Small Worlds）算法执行向量搜索。

F-006: 文件 `langchain_mongodb/vectorstores.py` 第55行，常量 `DEFAULT_INSERT_BATCH_SIZE = 100`，作为文档批量插入的默认批次大小。

F-007: 文件 `langchain_mongodb/vectorstores.py` 第214-248行，`__init__` 方法有两个 `@overload` 签名：一个用于 `AutoEmbeddings`（embedding_key/relevance_score_fn/dimensions 必须为 None/None/-1），一个用于常规 `Embeddings`（embedding_key 默认 "embedding"，relevance_score_fn 默认 "cosine"，dimensions 默认 -1）。

F-008: 文件 `langchain_mongodb/vectorstores.py` 第252-330行，`__init__` 实现接受参数：`collection`、`embedding`（Embeddings 或 str，字符串会自动创建 AutoEmbeddings）、`index_name="vector_index"`、`text_key="text"`（支持 str 或 List[str]，取第一个）、`embedding_key="embedding"`、`relevance_score_fn="cosine"`（支持 'euclidean'、'cosine'、'dotProduct'）、`dimensions=-1`、`auto_create_index=None`、`auto_index_timeout=15`、`vector_index_options=None`。

F-009: 文件 `langchain_mongodb/vectorstores.py` 第296-308行，AutoEmbeddings 模式下有三项校验：embedding_key 必须为 None，dimensions 必须为 -1，relevance_score_fn 必须为 None，否则抛出 `pymongo.errors.ConfigurationError`。

F-010: 文件 `langchain_mongodb/vectorstores.py` 第313-330行，自动建索引逻辑：`auto_create_index=False` 时跳过；`auto_create_index=None` 且 `dimensions==-1` 且非 AutoEmbedding 时跳过；若同名索引已存在则跳过；否则调用 `self.create_vector_search_index(dimensions, wait_until_complete=auto_index_timeout, ...)`。

F-011: 文件 `langchain_mongodb/vectorstores.py` 第348-374行，类方法 `from_connection_string(connection_string, namespace, embedding, **kwargs)`，通过 `MongoClient(connection_string, driver=DRIVER_METADATA)` 创建客户端，按 "." 分割 namespace 为 db_name 和 collection_name，返回 cls 实例。

F-012: 文件 `langchain_mongodb/vectorstores.py` 第380-458行，`add_texts` 方法支持按 `batch_size`（默认100）分批，并监控累积字节大小，当 `size >= 47_000_000` 时提前切批（规避 MongoDB 16MB BSON 限制的安全阈值）。每批调用 `bulk_embed_and_insert_texts`。

F-013: 文件 `langchain_mongodb/vectorstores.py` 第493-512行，`bulk_embed_and_insert_texts` 委托给 `pymongo_search_utils.bulk_embed_and_insert_texts`，传入 embedding_func、collection、text_key、embedding_key（AutoEmbedding 时为空字符串）、ids、autoembedding 标志。

F-014: 文件 `langchain_mongodb/vectorstores.py` 第514-551行，`add_documents` 方法将 Document 列表转换为 (texts, metadatas) 元组，按 batch_size 分批调用 `bulk_embed_and_insert_texts`。若未提供 ids，则使用 `doc.id or str(ObjectId())` 生成。

F-015: 文件 `langchain_mongodb/vectorstores.py` 第553-598行，`similarity_search_with_score` 方法：非 AutoEmbedding 时先调用 `embedding.embed_query(query)`，然后调用内部 `_similarity_search_with_score`，传入 `rerank_query=query` 以支持原生重排序。

F-016: 文件 `langchain_mongodb/vectorstores.py` 第600-646行，`similarity_search` 方法委托给 `similarity_search_with_score`，可选地通过 `include_scores=True` 将 score 写入 document.metadata["score"]。

F-017: 文件 `langchain_mongodb/vectorstores.py` 第648-685行，`max_marginal_relevance_search` 方法支持 MMR 搜索，参数 `fetch_k=20`（先取回的候选数）、`lambda_mult=0.5`（相关性与多样性权衡，0=最大多样性，1=最小多样性）。

F-018: 文件 `langchain_mongodb/vectorstores.py` 第764-814行，`max_marginal_relevance_search_by_vector` 先以 `fetch_k` 调用 `_similarity_search_with_score`（include_embeddings=True），再用 `utils.maximal_marginal_relevance` 在 numpy 中计算 MMR 索引，返回去重后的 k 个文档。

F-019: 文件 `langchain_mongodb/vectorstores.py` 第841-944行，核心方法 `_similarity_search_with_score`：构建 MongoDB 聚合管道，根据是否 AutoEmbedding 选择 `autoembedding_vector_search_stage` 或 `vector_search_stage`，追加 `$set` score 阶段；若指定 `rerank_path`，追加 `rerank_stage`（需 MongoDB 8.3+）；默认 `$project` 去掉 embedding 字段；支持 `post_filter_pipeline` 后处理。结果中缺失 text_key 的文档会被跳过，若集合非空但无匹配则发出 warning。

F-020: 文件 `langchain_mongodb/vectorstores.py` 第946-1007行，`create_vector_search_index` 方法：先尝试 `create_collection`（捕获 CollectionInvalid），根据是否 AutoEmbedding 决定 path（text_key vs embedding_key）和 dimensions（-1 vs 推断），委托给 `create_vector_search_index` 或 `update_vector_search_index`。

F-021: 文件 `langchain_mongodb/vectorstores.py` 第732-747行，`delete` 方法将字符串 id 通过 `str_to_oid` 转换为 ObjectId，使用 `$in` 查询调用 `delete_many`，返回 `.acknowledged`。

F-022: 文件 `langchain_mongodb/vectorstores.py` 第344-346行，`_select_relevance_score_fn` 返回恒等函数 `lambda score: score`，因为 Atlas Vector Search 分数已归一化到 [0,1]。

## 索引管理（index.py）

F-023: 文件 `langchain_mongodb/index.py` 第8-13行，从 `pymongo_search_utils` 重新导出四个函数：`create_fulltext_search_index`、`create_vector_search_index`、`drop_vector_search_index`、`update_vector_search_index`。

F-024: 文件 `langchain_mongodb/index.py` 第18-42行，内部函数 `_vector_search_index_definition(dimensions, path, similarity, filters, vector_index_options, **kwargs)` 构建索引定义：fields 列表包含一个 vector 字段（numDimensions/path/similarity/type），filters 列表中的每个字段追加为 `{"type": "filter", "path": field}`。

F-025: 文件 `langchain_mongodb/index.py` 第45-59行，`_is_index_ready(collection, index_name)` 遍历 `collection.list_search_indexes(index_name)`，检查 status == "READY"。

F-026: 文件 `langchain_mongodb/index.py` 第62-80行，`_wait_for_predicate(predicate, err, timeout=120, interval=0.5)` 使用 monotonic 时钟轮询，超时抛出 TimeoutError。

## MongoDBRecordManager（indexes.py）

F-027: 文件 `langchain_mongodb/indexes.py` 第17行，类 `MongoDBRecordManager` 继承自 `langchain_core.indexing.base.RecordManager`，用于 LangChain indexing API 跟踪文档写入状态。

F-028: 文件 `langchain_mongodb/indexes.py` 第20-39行，`__init__(collection)` 将 namespace 设为 `f"{db.name}.{collection.name}"`，调用父类构造，存储 collection 引用，并追加客户端元数据。

F-029: 文件 `langchain_mongodb/indexes.py` 第74-93行，`update(keys, *, group_ids, time_at_least)` 对每个 (key, group_id) 执行 `find_one_and_update`，upsert 设置 group_id 和 updated_at（来自 `get_time()`）。

F-030: 文件 `langchain_mongodb/indexes.py` 第108-124行，`get_time()` 优先通过 `database.command("hostInfo")` 获取服务器高精度时间（system.currentTime），失败时回退到 `ping` 命令的 operationTime（低精度），并发出一次性 warning。

F-031: 文件 `langchain_mongodb/indexes.py` 第131-139行，`exists(keys)` 使用 `$in` 查询返回布尔列表，保持输入顺序。

F-032: 文件 `langchain_mongodb/indexes.py` 第146-168行，`list_keys(*, before, after, group_ids, limit)` 支持按 updated_at 时间范围、group_ids 过滤，可选 limit。

F-033: 文件 `langchain_mongodb/indexes.py` 第187-191行，`delete_keys(keys)` 使用 `delete_many` 按 namespace + key $in 删除。所有异步方法通过 `run_in_executor` 包装同步方法。

## 缓存（cache.py）

F-034: 文件 `langchain_mongodb/cache.py` 第23行，类 `MongoDBCache` 继承自 `langchain_core.caches.BaseCache`，实现精确匹配的 LLM 缓存。

F-035: 文件 `langchain_mongodb/cache.py` 第29-31行，`MongoDBCache` 定义三个字段常量：`PROMPT = "prompt"`、`LLM = "llm"`、`RETURN_VAL = "return_val"`。

F-036: 文件 `langchain_mongodb/cache.py` 第33-60行，`MongoDBCache.__init__(connection_string, collection_name="default", database_name="default", **kwargs)`：创建 MongoClient，若集合不存在则创建并在 `[prompt, llm]` 上建复合索引。

F-037: 文件 `langchain_mongodb/cache.py` 第76-82行，`MongoDBCache.lookup(prompt, llm_string)` 通过 `find_one` 精确匹配 prompt 和 llm 字段，反序列化 return_val。

F-038: 文件 `langchain_mongodb/cache.py` 第84-90行，`MongoDBCache.update(prompt, llm_string, return_val)` 使用 `update_one` upsert，将 Generation 列表通过 `_dumps_generations` 序列化为 JSON 字符串。

F-039: 文件 `langchain_mongodb/cache.py` 第108行，类 `MongoDBAtlasSemanticCache` 同时继承 `BaseCache` 和 `MongoDBAtlasVectorSearch`（多继承），实现语义缓存。

F-040: 文件 `langchain_mongodb/cache.py` 第114-115行，`MongoDBAtlasSemanticCache` 定义 `LLM = "llm_string"` 和 `RETURN_VAL = "return_val"` 字段名。

F-041: 文件 `langchain_mongodb/cache.py` 第117-153行，`MongoDBAtlasSemanticCache.__init__` 接受 `connection_string`、`embedding`、`collection_name="default"`、`database_name="default"`、`index_name="default"`、`wait_until_ready=None`、`score_threshold=None`。创建客户端后设置 self.collection，调用 `MongoDBAtlasVectorSearch.__init__`（通过 super()）。

F-042: 文件 `langchain_mongodb/cache.py` 第155-173行，`MongoDBAtlasSemanticCache.lookup` 调用 `similarity_search_with_score(prompt, 1, pre_filter={LLM: {"$eq": llm_string}}, post_filter_pipeline=...)`，若 score_threshold 设置则追加 `$match: {score: {$gte: threshold}}`，从 metadata 取 RETURN_VAL 反序列化。

F-043: 文件 `langchain_mongodb/cache.py` 第175-198行，`MongoDBAtlasSemanticCache.update` 调用 `add_texts([prompt], [{LLM: llm_string, RETURN_VAL: serialized}])`，若 wait_until_ready 设置，轮询 `lookup(prompt, llm_string) == return_val` 直到超时。

F-044: 文件 `langchain_mongodb/cache.py` 第219-239行，`_dumps_generations` 将每个 Generation 通过 `langchain_core.load.dump.dumps` 序列化为字符串，再 json.dumps 为整体。`_loads_generations` 先尝试 `loads(..., allowed_objects="core")`，失败后回退到旧版 `Generation(**dict)` 格式，并对 malformed 数据返回 None 并 warning。

## 聊天历史（chat_message_histories.py）

F-045: 文件 `langchain_mongodb/chat_message_histories.py` 第17-20行，默认常量：`DEFAULT_DBNAME = "chat_history"`、`DEFAULT_COLLECTION_NAME = "message_store"`、`DEFAULT_SESSION_ID_KEY = "SessionId"`、`DEFAULT_HISTORY_KEY = "History"`。

F-046: 文件 `langchain_mongodb/chat_message_histories.py` 第23行，类 `MongoDBChatMessageHistory` 继承自 `langchain_core.chat_history.BaseChatMessageHistory`。

F-047: 文件 `langchain_mongodb/chat_message_histories.py` 第63-132行，`__init__` 接受 `connection_string`（可选）、`session_id`、`database_name`、`collection_name`、`session_id_key`、`history_key`、`create_index=True`、`history_size=None`、`index_kwargs`、`client`（可选）。connection_string 和 client 二选一，同时提供会抛 ValueError；create_index=True 时在 session_id_key 上建索引。

F-048: 文件 `langchain_mongodb/chat_message_histories.py` 第134-160行，`messages` 属性：若 history_size 为 None 则 find 全部；否则计算 skip_count = max(0, total - history_size)，跳过旧消息只取最近 N 条。每条文档的 History 字段是 JSON 字符串，通过 `json.loads` + `messages_from_dict` 反序列化。

F-049: 文件 `langchain_mongodb/chat_message_histories.py` 第166-176行，`add_message(message)` 使用 `insert_one` 插入 `{session_id_key: session_id, history_key: json.dumps(message_to_dict(message))}`，每条消息一个文档。

F-050: 文件 `langchain_mongodb/chat_message_histories.py` 第178-183行，`clear()` 使用 `delete_many({session_id_key: session_id})` 删除会话所有消息。

## 文档存储（docstores.py）

F-051: 文件 `langchain_mongodb/docstores.py` 第19行，类 `MongoDBDocStore` 继承自 `langchain_core.stores.BaseStore`，提供 [str, Document] 键值存储接口。

F-052: 文件 `langchain_mongodb/docstores.py` 第36行，`__init__(collection, text_key="page_content")`，使用 MongoDB 的 `_id` 字段作为键，文档内容存储在 text_key 字段。

F-053: 文件 `langchain_mongodb/docstores.py` 第70-88行，`mget(keys)` 使用 `find({"_id": {"$in": keys}})` 批量获取，构建字典后按输入顺序返回（缺失键返回 None）。

F-054: 文件 `langchain_mongodb/docstores.py` 第90-111行，`mset(key_value_pairs, batch_size=100)` 分批调用 `insert_many`，每批将 Document 转为 `{"_id": key, text_key: text, **metadata}`。

F-055: 文件 `langchain_mongodb/docstores.py` 第121-136行，`yield_keys(*, prefix=None)` 支持前缀匹配（使用 `$regex: f"^{prefix}"`），yield 每个文档的 _id。

## 管道组件（pipelines.py）

F-056: 文件 `langchain_mongodb/pipelines.py` 第12-18行，从 `pymongo_search_utils` 重新导出：`autoembedding_vector_search_stage`、`combine_pipelines`、`final_hybrid_stage`、`reciprocal_rank_stage`、`vector_search_stage`。

F-057: 文件 `langchain_mongodb/pipelines.py` 第21-54行，`rerank_stage(query, path, num_docs_to_rerank, model=None)` 返回 `[$rerank, $set]` 两阶段管道。$rerank spec 包含 query.text、path、numDocsToRerank（最大1000），可选 Voyage AI model（如 "rerank-2.5"）。注释说明需 MongoDB 8.3+ 且在 Atlas Project Settings 启用 Native Reranking。

F-058: 文件 `langchain_mongodb/pipelines.py` 第57-94行，`text_search_stage(query, search_field, index_name, limit, filter, include_scores=True)` 返回 `[$search, $match?, $set score?, $limit?]` 管道，使用 Lucene 标准（BM25）分析器的全文搜索。

## AutoEmbeddings（embeddings.py）

F-059: 文件 `langchain_mongodb/embeddings.py` 第6行，类 `AutoEmbeddings` 继承自 `langchain_core.embeddings.Embeddings`，启用 MongoDB 服务端自动嵌入。

F-060: 文件 `langchain_mongodb/embeddings.py` 第7-16行，`__init__(model)` 仅存储模型名称。`embed_documents` 和 `embed_query` 均抛出 `NotImplementedError`，因为所有嵌入由 MongoDB Atlas 服务端管理。

## 检索器（retrievers/）

F-061: 文件 `langchain_mongodb/retrievers/__init__.py` 第7-23行，导出五个检索器：`MongoDBAtlasFullTextSearchRetriever`、`MongoDBGraphRAGRetriever`、`MongoDBAtlasHybridSearchRetriever`、`MongoDBAtlasParentDocumentRetriever`、`MongoDBAtlasSelfQueryRetriever`。

F-062: 文件 `langchain_mongodb/retrievers/full_text_search.py` 第15行，`MongoDBAtlasFullTextSearchRetriever` 继承 `BaseRetriever`，使用 BM25 全文搜索。构造时若 auto_create_index=True 且索引不存在，自动创建全文搜索索引。

F-063: 文件 `langchain_mongodb/retrievers/hybrid_search.py` 第24行，`MongoDBAtlasHybridSearchRetriever` 结合向量搜索和全文搜索，通过 RRF（Reciprocal Rank Fusion）算法融合分数。默认 `vector_penalty=60.0`、`fulltext_penalty=60.0`、`vector_weight=1.0`、`fulltext_weight=1.0`、k=4、oversampling_factor=10。

F-064: 文件 `langchain_mongodb/retrievers/hybrid_search.py` 第213-238行，混合搜索管道分别构建 vector_pipeline 和 text_pipeline，各追加 `reciprocal_rank_stage`，通过 `combine_pipelines` 合并，最后用 `final_hybrid_stage` 求和排序。

F-065: 文件 `langchain_mongodb/retrievers/parent_document.py` 第35行，`MongoDBAtlasParentDocumentRetriever` 继承 `langchain_classic.retrievers.parent_document_retriever.ParentDocumentRetriever`，在同一 Collection 中存储父文档和子文档块，仅对子块计算嵌入。

F-066: 文件 `langchain_mongodb/retrievers/parent_document.py` 第149-173行，父文档检索管道：$vectorSearch → $set score → $project embedding → $lookup 自连接（localField=doc_id, foreignField=_id, 子管道 $match 排除有 metadata.doc_id 的子文档）→ $unwind → $group 去重 → $replaceRoot。

F-067: 文件 `langchain_mongodb/retrievers/self_querying.py` 第26行，`MongoDBStructuredQueryTranslator` 继承 `Visitor`，将 LangChain StructuredQuery 翻译为 MongoDB 查询格式。

F-068: 文件 `langchain_mongodb/retrievers/self_querying.py` 第38-50行，支持的比较器：EQ、NE、GT、GTE、LT、LTE、IN、NIN；支持的逻辑运算符：AND、OR。映射到 MongoDB 的 `$eq/$ne/$gt/$gte/$lt/$lte/$in/$nin/$and/$or`。

F-069: 文件 `langchain_mongodb/retrievers/self_querying.py` 第73-90行，`_convert_dict_to_datetime` 处理 LangChain 内部日期格式 `{"date": "YYYY-MM-DD", "type": "date"}` 和 `{"datetime": "...", "type": "datetime"}`，转换为 Python datetime 对象，避免 Atlas 将 "type" 键误判为 GeoJSON。

## Agent Toolkit（agent_toolkit/）

F-070: 文件 `langchain_mongodb/agent_toolkit/toolkit.py` 第21行，`MongoDBDatabaseToolkit` 继承 `BaseToolkit`，包含 `db: MongoDBDatabase` 和 `llm: BaseLanguageModel` 两个字段。

F-071: 文件 `langchain_mongodb/agent_toolkit/toolkit.py` 第87-124行，`get_tools()` 返回四个工具：`QueryMongoDBDatabaseTool`（执行查询）、`InfoMongoDBDatabaseTool`（获取 schema 和样例行）、`ListMongoDBDatabaseTool`（列出集合）、`QueryMongoDBCheckerTool`（LLM 校验查询正确性）。

## 工具函数（utils.py）

F-072: 文件 `langchain_mongodb/utils.py` 第37行，`DRIVER_METADATA = DriverInfo(name="Langchain", version=version("langchain-mongodb"))`，通过 importlib.metadata 获取已安装版本。

F-073: 文件 `langchain_mongodb/utils.py` 第44-74行，`cosine_similarity(X, Y)` 优先使用 `simsimd`（需安装）进行高性能余弦距离计算，回退到 NumPy 实现。

F-074: 文件 `langchain_mongodb/utils.py` 第77-138行，`maximal_marginal_relevance(query_embedding, embedding_list, lambda_mult=0.5, k=4)` 实现 MMR 算法：先选最相似文档，然后迭代选择 `λ*Sim(D_i,Q) - (1-λ)*max Sim(D_i,D_j)` 最大的文档。

F-075: 文件 `langchain_mongodb/utils.py` 第141-164行，`str_to_oid(str_repr)` 尝试将24字符十六进制字符串转为 ObjectId，失败则原样返回字符串。`oid_to_str` 直接 str() 转换。

F-076: 文件 `langchain_mongodb/utils.py` 第181-196行，`make_serializable(obj)` 递归将字典中的 ObjectId 转为字符串、datetime/date 转为 ISO 格式字符串、列表中的 ObjectId/datetime 也逐一转换。

F-077: 文件 `langchain_mongodb/utils.py` 第199-229行，`prepare_query_for_vector_search(query, embedding)` 返回 `(query_input, is_autoembedding)`：AutoEmbeddings 时返回原始字符串（服务端嵌入），否则调用 `embedding.embed_query(query)` 返回向量。

## Monorepo 结构

F-078: 仓库根目录 `libs/` 下包含四个包：`langchain-mongodb`（核心集成）、`langchain-mongodb-deepagents-vfs`（DeepAgents 虚拟文件系统）、`langgraph-checkpoint-mongodb`（LangGraph 检查点持久化）、`langgraph-store-mongodb`（LangGraph 长期记忆存储）。

F-079: 文件 `libs/langchain-mongodb/langchain_mongodb/graphrag/` 目录包含 GraphRAG 实现：`graph.py`、`schema.py`、`prompts.py`、`example_templates.py`，并在 `retrievers/graphrag.py` 中提供 `MongoDBGraphRAGRetriever`。
