---
type: concept
title: Milvus 分区多租户与三存储分层
description: 单集合 + kb_id partition key 的多租户隔离设计、64 分区与缓冲落盘参数的工程含义，以及 Milvus（向量）/Elasticsearch（文本）/MySQL（结构化）三层存储的职责划分与一致性维护。
tags: [qanything, milvus, elasticsearch, mysql, multitenancy, storage]
generated: { by: okf-wiki/0.2, at: 2026-09-09 }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
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

# Milvus 分区多租户与三存储分层

QAnything 的多用户、多知识库场景建立在三层存储之上。本文先讲 Milvus 侧最具特色的"单集合 + partition key"多租户设计，再梳理三层存储的职责划分与跨库一致性的工程要点。

## 单集合 + kb_id 分区：逻辑隔离而非物理隔离

常见的多租户向量库做法是"每租户一个 collection"。QAnything 反其道而行：`VectorStoreMilvusClient` 以 `partition_key_field="kb_id"` 构建**单一集合**（`MILVUS_COLLECTION_NAME='qanything_collection_240625'`），所有知识库共用这一个 collection（F-qa-013）。构造参数细节：

- embedding_function 为 `YouDaoEmbeddings()`；
- partition_key_field 为 `"kb_id"`，auto_id=True；
- search_params 为 `{"params": {"ef": 64}}`（HNSW 检索精度参数）；
- `_create_collection()` 创建 num_partitions=64 的分区集合（F-qa-014）。

kb_id 由服务端生成，形如 `'KB' + uuid.uuid4().hex`，`quick=True` 时追加 `"_QUICK"` 后缀（F-qa-036）。检索时以 `kb_id in [...]` 表达式过滤（F-qa-012），知识库的删除与隔离不删集合结构，而是按 partition key 过滤。

两个反直觉的工程含义值得强调：

1. **分区是哈希路由，不是"一个知识库一个分区"**。分区数固定 64，知识库数量远超 64 时多个 kb_id 共享物理分区，隔离是逻辑级的而非物理级的。若业务要求物理级租户隔离，需改造为分 collection 方案。
2. **入库不等于立即可检索**。`SelfMilvus(Milvus)` 带缓冲落盘参数 flush_interval=600 秒、flush_threshold=10000（F-qa-014），向量写入先驻留缓冲区。排查"文件已入库但检索不到"时，应先检查 flush 缓冲窗口与文件状态机（gray/yellow/green/red），而非向量库配置。

## 三存储分层

| 存储 | 部署形态 | 职责 | 关键事实 |
|---|---|---|---|
| Milvus 2.4.8 standalone | 容器 19540:19530，依赖 etcd + minio | child chunk 向量，语义相似度检索 | F-qa-013、F-qa-014、F-qa-057 |
| Elasticsearch 8.13.2 | 容器 9210:9200 映射，单节点，xpack.security 关闭 | 文档文本 BM25 关键词检索，hybrid_search 合并 | F-qa-015、F-qa-057 |
| MySQL 8.4 | 容器 3316:3306，root 密码 123456 | 文件元数据/状态机、parent 全文、FAQ、QALog、Bot 配置 | F-qa-016、F-qa-022、F-qa-057 |

ES 侧由 `StoreElasticSearchClient` 包装 LangChain `ElasticsearchStore`，strategy 为 `ElasticsearchStore.BM25RetrievalStrategy()`，es_url 取 `ES_URL`（`http://{GATEWAY_IP}:9210/`），index_name 取 `ES_INDEX_NAME='qanything_es_index_240625'`（F-qa-015、F-qa-023）。MySQL 侧的数据访问统一收敛在 `KnowledgeBaseManager`（构造函数签名 `__init__(pool_size=8)`，提供 add_file、add_document、add_faq、add_qalog、get_qalog_by_filter、new_qanything_bot 等方法，共 57 个方法定义），连接参数 MYSQL_PORT_LOCAL=3316、MYSQL_PASSWORD_LOCAL='123456'、MYSQL_DATABASE_LOCAL='qanything'（F-qa-022、F-qa-023）。

MySQL 中还有一类容易被忽视的角色：`MysqlStore(InMemoryStore)` 作为 parent docstore，`mset()` 把 `doc.to_json()` 写入 Document 表，`mget()` 检索后回填 parent 全文并对 FAQ 条目展开为 `question：answer` 形式（F-qa-016）。也就是说，MySQL 不仅是"元数据库"，还是检索链路上 parent 内容的权威来源（详见 [/concepts/03-retrieval.md](/concepts/03-retrieval.md)）。

## 一致性维护

三库双写（向量 + 文本）+ 一库（结构化）的架构决定了任何数据变更都必须考虑跨库一致性：

- **删除文件**：ES 以 `file_id + '_' + i` 为 doc_id 逐条删除（F-qa-015），Milvus 按 file_id 过滤删除，MySQL 清 File/Document 记录，三处缺一即产生孤儿数据；
- **删除知识库**：按 kb_id 过滤三库记录，不触碰集合结构本身；
- **入库时序**：insert_files_server 完成后才置 green 状态，问答仅检索 green 文件，用状态机挡住"半成品"数据进入检索链路（F-qa-042）。

## 容量与性能关注点

- 64 分区是固定上限，知识库规模增长后需关注哈希不均带来的尾部延迟；
- `MAX_CHARS=1000000`：单文件内容长度上限，超限或内容为空直接置 red 失败（F-qa-023、F-qa-033）；
- compose 数据卷落盘于 `${DOCKER_VOLUME_DIRECTORY:-.}/volumes/` 下 es/etcd/minio/mysql/milvus 子目录，扩容与备份以此目录为边界（F-qa-060）；
- Milvus standalone 依赖 etcd 与 minio（ETCD_ENDPOINTS、MINIO_ADDRESS 环境变量）， compose 中 minio 使用默认凭据 minioadmin/minioadmin（F-qa-057、F-qa-060）——生产部署必须修改默认口令。

## 相关概念

- [03 父子切分与 Milvus/ES 混合检索](/concepts/03-retrieval.md)
- [05 依赖服务化：五个本地推理/解析进程](/concepts/05-dependent-servers.md)
- [07 演进痕迹：死代码、失效导入与版本错位](/concepts/07-evolution-traces.md)
