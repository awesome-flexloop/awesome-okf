---
type: concept
title: 父子切分与 Milvus/ES 混合检索
description: parent 800/child 400 两级切分、"小块召回、大块阅读"的检索增强链路——child 双写向量/文本索引、parent 落 MySQL 回填，以及 hybrid_search 合并去重机制。
tags: [qanything, rag, retrieval, chunking, milvus, elasticsearch]
generated: { by: okf-wiki/0.2, at: 2026-09-09 }
verified: { by: "process:seven-concepts-v", at: 2026-09-09 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: QAnything 源码事实清单（F-qa-001~060）
  - id: insights
    resource: /references/insights.md
    title: QAnything 架构洞察与知识地图
---

# 父子切分与 Milvus/ES 混合检索

RAG 系统的检索质量很大程度上取决于"把文档切成多大块"：chunk 太小，语义不完整，LLM 读到的上下文缺头少尾；chunk 太大，向量表示被稀释，语义命中率下降。QAnything 的解法是**父子切分（parent-child chunking）**：用小块负责向量空间的精确命中，用大块负责给 LLM 提供完整语义，二者各司其职。本文拆解这条"小块召回、大块阅读"链路的完整实现。

## 两级切分参数

`ParentRetriever(vectorstore_client, mysql_client, es_client)` 的默认切分参数（F-qa-010）：

| 参数 | 默认值 | 说明 |
|---|---|---|
| parent chunk | 800 | 送入 LLM 上下文的大块 |
| child chunk | 400 | 参与向量检索的小块 |
| chunk_overlap | parent 为 0；child 为 child 尺寸的 1/4（默认 100） | 相邻块重叠量 |

注意两个细节：其一，parent 块 overlap 为 0，child 块 overlap 固定为 child 尺寸的 1/4（默认 100）——调大 child 会同步增大冗余量；其二，`insert_documents()` 会按请求传入的 chunk_size 动态重建 `RecursiveCharacterTextSplitter`，即切分粒度可在入库时按知识库调整（F-qa-010）。切分分隔符序列为 `SEPARATORS=["\n\n", "\n", "。", "，", ",", ".", ""]`，优先按段落、再按句子、最后硬切，尽量保持语义边界（F-qa-025）。配置常量 `DEFAULT_PARENT_CHUNK_SIZE=800`、`DEFAULT_CHILD_CHUNK_SIZE=400` 定义于 `model_config.py`（F-qa-025）。

## 入库：双写与 parent 落库

`SelfParentRetriever(ParentDocumentRetriever)` 的 `aadd_documents()` 执行两级切分后（F-qa-011）：

1. **child 文档**带 `[headers]` 前缀元数据（章节标题信息随 chunk 入索引），随后向 Milvus 与 Elasticsearch **双写**——向量索引与文本索引各一份；
2. **parent 文档全文**以 `MysqlStore` 作为 parent docstore 落入 MySQL，LangChain 的 `InMemoryStore` 接口背后实际是 MySQL 持久化。

`MysqlStore(InMemoryStore)` 的 `mset()` 将 `doc.to_json()` 写入 MySQL 的 Document 表并写本地 json 缓存；`mget()` 检索后回填 parent 内容，对 FAQ 类型条目展开为 `question：answer` 形式（F-qa-016）。这保证"child 命中 → parent 回填"链路在重启后依然成立。

embedding 输入还经过专门的文本净化：`YouDaoEmbeddings._process_query` 会过滤页内容中的 `![figure]`、`![equation]` 行，避免图文占位符污染向量（F-qa-018）；`YouDaoEmbeddings` 的 model_version 为 `'local_v20240725'`，请求本地 `http://{LOCAL_EMBED_SERVICE_URL}/embedding`，`aembed_documents` 经 aiohttp 批量提交（F-qa-018）。本地 embedding/rerank 服务的输入上限均为 512 token（`LOCAL_EMBED_MAX_LENGTH=512`、`LOCAL_RERANK_MAX_LENGTH=512`），这与 child chunk 400 的取值相互印证——child 上限应受 embedding 模型 max_length 约束（F-qa-024）。

## 检索：child 命中与混合搜索

`ParentRetriever.get_retrieved_documents()` 的检索流程（F-qa-012）：

1. 以 Milvus similarity 检索 child 文档，过滤表达式为 `kb_id in [...]`（按知识库隔离）；
2. `hybrid_search=True` 时，再以 Elasticsearch `terms` filter 检索 ES 索引并合并结果、去重；
3. 文档元数据标记 `retrieval_source` 为 `'milvus'` 或 `'es'`，便于追溯命中来源。

ES 侧由 `StoreElasticSearchClient` 包装 LangChain `ElasticsearchStore`，strategy 为 `ElasticsearchStore.BM25RetrievalStrategy()`，即经典 BM25 关键词检索（F-qa-015）。向量侧 top_k 默认 30（`VECTOR_SEARCH_TOP_K=30`），ES 侧同样为 30（`ES_TOP_K=30`）（F-qa-023）。BM25 与向量相似度互补：前者擅长精确术语、型号、编号，后者擅长语义改写与同义表达。

命中 child 后经 `MysqlStore.mget()` 回填 parent 全文进入上下文，再由编排链的 rerank 与 prompt 组装继续处理（见 [/concepts/02-rag-pipeline.md](/concepts/02-rag-pipeline.md)）。rerank 由 `YouDaoRerank` 请求本地 `http://{LOCAL_RERANK_SERVICE_URL}/rerank` 完成，`arerank_documents()` 按 `LOCAL_RERANK_BATCH` 分批，分数四舍五入保留 2 位小数并降序排序（F-qa-019）。

## 删除的一致性

父子双写意味着删除也必须三处同步。ES 侧 `delete_files()` 以 `file_id + '_' + i` 为 doc_id 逐条删除（F-qa-015）；Milvus 按 file_id 过滤删除；MySQL 侧的 Document/File 记录由 `KnowledgeBaseManager` 清理（F-qa-022）。任何一处遗漏都会造成"删了还能检到"或"回填失败"的孤儿数据。

## 复刻与调参要点

- child/parent 比例 1:2、child overlap=child/4 是起点而非教条，应结合 embedding 模型 max_length（本系统 512）约束 child 上限；
- `[headers]` 前缀与 `![figure]`/`![equation]` 过滤说明 embedding 输入值得专门的净化预处理（F-qa-011、F-qa-018）；
- 入库链路必须保证 child 命中 → parent 回填的双写一致性，删除时同步清理 Milvus/ES/MySQL 三处；
- 混合检索开启后关注去重逻辑与 `retrieval_source` 标记，它是排查"为什么检到这条"的关键线索（F-qa-012）。

## 相关概念

- [02 LocalDocQA 问答编排链与硬编码阈值](/concepts/02-rag-pipeline.md)
- [04 Milvus 分区多租户与三存储分层](/concepts/04-storage-multitenancy.md)
- [05 依赖服务化：五个本地推理/解析进程](/concepts/05-dependent-servers.md)
