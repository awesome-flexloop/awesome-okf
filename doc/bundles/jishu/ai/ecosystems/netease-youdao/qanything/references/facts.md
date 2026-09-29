---
type: reference
title: QAnything 源码事实清单（R 阶段事实采集）
tags:
  - qanything
  - rag
  - netease-youdao
  - source-code
sources:
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/core/local_doc_qa.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/core/local_file.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/core/retriever/parent_retriever.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/core/retriever/vectorstore.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/core/retriever/elasticsearchstore.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/core/retriever/docstrore.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/core/chains/condense_q_chain.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/configs/model_config.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/connector/embedding/embedding_for_online_client.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/connector/rerank/rerank_for_online_client.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/connector/llm/llm_for_openai_api.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/connector/llm/base/base.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/connector/database/mysql/mysql_client.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/connector/database/faiss/faiss_client.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/connector/database/milvus/milvus_client.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/dependent_server/embedding_server/embedding_server.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/dependent_server/rerank_server/rerank_server.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/dependent_server/ocr_server/ocr_server.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/dependent_server/pdf_parser_server/pdf_parser_server.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/dependent_server/insert_files_serve/insert_files_server.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/qanything_server/sanic_api.py
  - resource: vendor/netease-youdao/QAnything/qanything_kernel/qanything_server/handler.py
  - resource: vendor/netease-youdao/QAnything/docs/API.md
  - resource: vendor/netease-youdao/QAnything/scripts
  - resource: vendor/netease-youdao/QAnything/front_end/package.json
  - resource: vendor/netease-youdao/QAnything/front_end/vite.config.ts
  - resource: vendor/netease-youdao/QAnything/front_end/.env.development
  - resource: vendor/netease-youdao/QAnything/front_end/.env.production
  - resource: vendor/netease-youdao/QAnything/docker-compose-linux.yaml
  - resource: vendor/netease-youdao/QAnything/docker-compose-mac.yaml
  - resource: vendor/netease-youdao/QAnything/docker-compose-win.yaml
  - resource: vendor/netease-youdao/QAnything/README.md
generated:
  by: okf-wiki/0.2
  at: 2026-09-09
  phase: R（事实采集，Task 6）
  baseline: v2.0.0 后 HEAD @ 615417a
verified: { by: "process:seven-concepts-v-fix", at: "2026-09-09" }
stale_after: 2027-09-09
status: stable
---

# QAnything 源码事实清单

> 信源：`vendor/netease-youdao/QAnything/`（git submodule，只读），基线 v2.0.0 后 HEAD @ 615417a。
> 证据位置列为相对 `vendor/netease-youdao/QAnything/` 的路径加符号名。

## 一、RAG 内核

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-qa-001 | 核心问答编排类 `LocalDocQA` 定义于 `local_doc_qa.py`，构造函数签名为 `LocalDocQA(port)`，实例方法 `init_cfg()` 完成向量库客户端、检索器（ParentRetriever）、embedding/rerank 客户端与 MySQL 管理器初始化 | `qanything_kernel/core/local_doc_qa.py::LocalDocQA` |
| F-qa-002 | `get_knowledge_based_answer()` 为问答主编排方法，其生成器依次产出：改写后问题（condense_question）、检索文档、rerank 结果、prompt、按 SSE `data: ` 前缀封装的 LLM 增量输出，结束帧为 `[DONE]` | `qanything_kernel/core/local_doc_qa.py::LocalDocQA.get_knowledge_based_answer` |
| F-qa-003 | rerank 过滤规则：rerank 分数 < 0.28 的文档被剔除；相邻文档 rerank 分数相对差大于 0.5 时截断（后续文档不再保留） | `qanything_kernel/core/local_doc_qa.py::LocalDocQA.get_knowledge_based_answer` |
| F-qa-004 | FAQ 优先匹配：当某文档为 FAQ 且（query 与 question 完全匹配，或 `calculate_relevance_optimized` 得分 ≥ 0.9）时直接返回答案，跳过 LLM 生成 | `qanything_kernel/core/local_doc_qa.py::LocalDocQA.get_knowledge_based_answer` |
| F-qa-005 | rerank 触发条件为 `num_tokens_rerank(query) <= 300`；rerank 完成后按 `top_k` 截断 | `qanything_kernel/core/local_doc_qa.py::LocalDocQA.get_knowledge_based_answer` |
| F-qa-006 | `reprocess_source_documents()` 按 token 预算裁切文档内容，使拼接后的上下文不超过 LLM 上下文长度预算 | `qanything_kernel/core/local_doc_qa.py::LocalDocQA.reprocess_source_documents` |
| F-qa-007 | `generate_prompt()` 对模板执行 `{{context}}`、`{{question}}` 占位符替换，检索文档以 `<reference>` 标签包裹后拼入提示词 | `qanything_kernel/core/local_doc_qa.py::LocalDocQA.generate_prompt` |
| F-qa-008 | `calculate_relevance_optimized()` 使用 `scipy.spatial.cKDTree` 检索 query 嵌入的近邻，以 0.5/0.5 加权几何平均融合向量相似度与字符串重合度 | `qanything_kernel/core/local_doc_qa.py::LocalDocQA.calculate_relevance_optimized` |
| F-qa-009 | `get_rerank_results()` 支持按 doc_ids（从 MySQL 取文档内容）或 doc_strs（直接传字符串）两种方式调用 rerank 服务，返回分数 ≥ 0.28 的结果 | `qanything_kernel/core/local_doc_qa.py::LocalDocQA.get_rerank_results` |
| F-qa-010 | `ParentRetriever(vectorstore_client, mysql_client, es_client)` 默认切分参数：parent chunk 800、child chunk 400，parent 块 chunk_overlap=0、child 块 chunk_overlap 为 child 尺寸的 1/4（默认 100）；`insert_documents()` 按请求传入的 chunk_size 动态重建 RecursiveCharacterTextSplitter | `qanything_kernel/core/retriever/parent_retriever.py::ParentRetriever` |
| F-qa-011 | `SelfParentRetriever(ParentDocumentRetriever)` 的 `aadd_documents()` 执行 parent/child 两级切分，child 文档页内容前加 `[headers]` 前缀元数据，随后向 Milvus 与 Elasticsearch 双写向量/文本索引，并以 `MysqlStore` 作为 parent docstore | `qanything_kernel/core/retriever/parent_retriever.py::SelfParentRetriever.aadd_documents` |
| F-qa-012 | `ParentRetriever.get_retrieved_documents()` 以 Milvus similarity 检索（expr 为 `kb_id in [...]`）；`hybrid_search=True` 时再以 Elasticsearch `terms` filter 合并 ES 结果并去重，文档元数据标记 `retrieval_source` 为 `'milvus'` 或 `'es'` | `qanything_kernel/core/retriever/parent_retriever.py::ParentRetriever.get_retrieved_documents` |
| F-qa-013 | `VectorStoreMilvusClient` 构造 `SelfMilvus`，参数：embedding_function 为 `YouDaoEmbeddings()`、collection_name 取 `MILVUS_COLLECTION_NAME`、partition_key_field 为 `"kb_id"`、auto_id=True、search_params 为 `{"params": {"ef": 64}}` | `qanything_kernel/core/retriever/vectorstore.py::VectorStoreMilvusClient` |
| F-qa-014 | `SelfMilvus(Milvus)` 带缓冲落盘参数 flush_interval=600 秒、flush_threshold=10000；`_create_collection()` 创建 num_partitions=64 的分区集合 | `qanything_kernel/core/retriever/vectorstore.py::SelfMilvus` |
| F-qa-015 | `StoreElasticSearchClient` 包装 LangChain `ElasticsearchStore`，strategy 为 `ElasticsearchStore.BM25RetrievalStrategy()`，es_url 取 `ES_URL`，index_name 取 `ES_INDEX_NAME`；`delete_files()` 以 `file_id + '_' + i` 为 doc_id 逐条删除 | `qanything_kernel/core/retriever/elasticsearchstore.py::StoreElasticSearchClient` |
| F-qa-016 | `MysqlStore(InMemoryStore)` 的 `mset()` 将 `doc.to_json()` 写入 MySQL 的 Document 表；`mget()` 对 FAQ 类型条目展开为 `question：answer` 形式，并写本地 json 缓存文件 | `qanything_kernel/core/retriever/docstrore.py::MysqlStore` |
| F-qa-017 | `RewriteQuestionChain` 以 `ChatOpenAI(temperature=0, top_p=0.01, seed=1234)` 为改写模型，用中文系统提示词将多轮 history+question 改写为独立问题，链式表达式为 `condense_q_prompt \| chat_model \| StrOutputParser()` | `qanything_kernel/core/chains/condense_q_chain.py::RewriteQuestionChain` |
| F-qa-018 | `YouDaoEmbeddings(Embeddings)` 的 model_version 为 `'local_v20240725'`，请求 `http://{LOCAL_EMBED_SERVICE_URL}/embedding`；`aembed_documents` 经 aiohttp 批量提交；`_process_query` 过滤页内容中的 `![figure]`、`![equation]` 行 | `qanything_kernel/connector/embedding/embedding_for_online_client.py::YouDaoEmbeddings` |
| F-qa-019 | `YouDaoRerank` 请求 `http://{LOCAL_RERANK_SERVICE_URL}/rerank`，`arerank_documents()` 按 `LOCAL_RERANK_BATCH` 分批，分数四舍五入保留 2 位小数并降序排序 | `qanything_kernel/connector/rerank/rerank_for_online_client.py::YouDaoRerank` |
| F-qa-020 | `OpenAILLM` 构造函数参数为 `(model, max_token, api_base, api_key, api_context_length, top_p, temperature)`，类常量 `offcut_token=50`；token 统计经 tiktoken（编码 `cl100k_base` 回退）并乘 1.2/1.1 余量系数；调用入口为 `client.chat.completions.create` | `qanything_kernel/connector/llm/llm_for_openai_api.py::OpenAILLM` |
| F-qa-021 | LLM 抽象层定义 `AnswerResult` 数据类（含 history、llm_output、prompt、total_tokens 等字段）与抽象基类 `BaseAnswer(ABC)` | `qanything_kernel/connector/llm/base/base.py::AnswerResult / BaseAnswer` |
| F-qa-022 | `KnowledgeBaseManager` 位于 MySQL connector，构造函数签名为 `__init__(pool_size=8)`，提供 `add_file`、`add_document`、`add_faq`、`add_qalog`、`get_qalog_by_filter`、`new_qanything_bot` 等方法（共 57 个方法定义，经 Grep `def ` 计数） | `qanything_kernel/connector/database/mysql/mysql_client.py::KnowledgeBaseManager` |
| F-qa-023 | `model_config.py` 关键常量：`VECTOR_SEARCH_TOP_K=30`、`VECTOR_SEARCH_SCORE_THRESHOLD=0.3`、`MILVUS_PORT=19540`、`MILVUS_COLLECTION_NAME='qanything_collection_240625'`、`ES_URL=http://{GATEWAY_IP}:9210/`、`ES_TOP_K=30`、`ES_INDEX_NAME='qanything_es_index_240625'`、`MYSQL_PORT_LOCAL=3316`、`MYSQL_PASSWORD_LOCAL='123456'`、`MYSQL_DATABASE_LOCAL='qanything'`、`MAX_CHARS=1000000` | `qanything_kernel/configs/model_config.py` |
| F-qa-024 | `model_config.py` 定义本地推理服务地址常量：`LOCAL_OCR_SERVICE_URL="localhost:7001"`、`LOCAL_PDF_PARSER_SERVICE_URL="localhost:9009"`、`LOCAL_RERANK_SERVICE_URL="localhost:8001"`、`LOCAL_EMBED_SERVICE_URL="localhost:9001"`；`LOCAL_RERANK_MAX_LENGTH=512`、`LOCAL_EMBED_MAX_LENGTH=512` | `qanything_kernel/configs/model_config.py` |
| F-qa-025 | `model_config.py` 定义切分常量：`DEFAULT_CHILD_CHUNK_SIZE=400`、`DEFAULT_PARENT_CHUNK_SIZE=800`、`SEPARATORS=["\n\n", "\n", "。", "，", ",", ".", ""]`；并定义 SYSTEM、INSTRUCTIONS、PROMPT_TEMPLATE、CUSTOM_PROMPT_TEMPLATE、SIMPLE_PROMPT_TEMPLATE 五组提示词模板与 BOT_DESC/BOT_IMAGE/BOT_PROMPT/BOT_WELCOME 默认 Bot 配置 | `qanything_kernel/configs/model_config.py` |
| F-qa-026 | `LocalFile(user_id, kb_id, file, file_name)` 以 `uuid.uuid4().hex` 生成 file_id；入参为 dict 时按 FAQ 处理、为 str 时按 URL 处理、为 File 时写入 `UPLOAD_ROOT_PATH/user_id/kb_id/file_id/` 目录 | `qanything_kernel/core/local_file.py::LocalFile` |
| F-qa-027 | 存疑事实（遗留代码）：`connector/database/faiss/faiss_client.py` 导入 `FAISS_LOCATION`、`FAISS_CACHE_SIZE`，`connector/database/milvus/milvus_client.py` 导入 `MILVUS_HOST_ONLINE`、`CHUNK_SIZE`，这四个名称均不存在于 `model_config.py`；Grep 全仓验证这两个模块无其他文件 import | `qanything_kernel/connector/database/faiss/faiss_client.py`、`qanything_kernel/connector/database/milvus/milvus_client.py` |

## 二、依赖服务（dependent_server）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-qa-028 | embedding 服务为 Sanic 应用 `"embedding_server"`，路由 `POST /embedding`（入参 `texts`），监听 9001 端口，启动参数 `--use_gpu`、`--workers`（默认 1），推理后端为 `EmbeddingOnnxBackend(use_cpu=not args.use_gpu)` | `qanything_kernel/dependent_server/embedding_server/embedding_server.py` |
| F-qa-029 | rerank 服务为 Sanic 应用 `"rerank_server"`，路由 `POST /rerank`（入参 `query`、`passages`），监听 8001 端口，后端为 `RerankOnnxBackend` | `qanything_kernel/dependent_server/rerank_server/rerank_server.py` |
| F-qa-030 | OCR 服务为 Sanic 应用 `"OCRService"`，路由 `POST /ocr`（入参 `img64`，base64 图像），监听 7001 端口；核心类 `OCRQAnything` 组合 `TextDetector`（DBPostProcess，box_thresh=0.5）与 `TextRecognizer`（CTCLabelDecode，字典文件 ocr.res），`drop_score=0.5` | `qanything_kernel/dependent_server/ocr_server/ocr_server.py::OCRQAnything / TextDetector / TextRecognizer` |
| F-qa-031 | PDF 解析服务为 Sanic 应用 `"pdf_parser_server"`，路由 `POST /pdfparser`（入参 `filename`、`save_dir`），监听 9009 端口，后端 `PdfLoader` 按 `--use_gpu` 选择 torch device | `qanything_kernel/dependent_server/pdf_parser_server/pdf_parser_server.py` |
| F-qa-032 | 文件入库服务 `insert_files_server.py` 为 Sanic 应用 `"InsertFileService"`，启动参数 `--port`（默认 8110）、`--workers`（默认 4）；后台任务 `check_and_process()` 轮询 MySQL `File` 表中 `status='gray'` 且 `MOD(id, INSERT_WORKERS)=worker_id` 的记录，置为 `yellow` 后处理 | `qanything_kernel/dependent_server/insert_files_serve/insert_files_server.py` |
| F-qa-033 | `process_data()` 中 `split_file_to_docs` 与 milvus insert 各以 300 秒超时执行；`content_length > MAX_CHARS` 或等于 0 时置 status='red'；入库完成后经 `update_file_upload_infos` 记录 time_record | `qanything_kernel/dependent_server/insert_files_serve/insert_files_server.py::process_data` |

## 三、API 层

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-qa-034 | 主服务为 Sanic 应用 `"QAnything"`，启动参数 `--host`（默认 `0.0.0.0`）、`--port`（默认 8777）、`--workers`（默认 4）；`REQUEST_MAX_SIZE` 设为 128MB，`CORS_ORIGINS="*"`；静态路由 `/qanything/` 映射至 `qanything_kernel/qanything_server/dist/qanything/`（index.html） | `qanything_kernel/qanything_server/sanic_api.py` |
| F-qa-035 | `sanic_api.py` 共注册 28 条路由（经 add_route 调用计数），全部为 GET/POST；其中 `GET /api/docs`、`GET /api/health_check` 两条为 GET，其余 26 条为 POST | `qanything_kernel/qanything_server/sanic_api.py`（第 73–100 行 add_route 调用块） |
| F-qa-036 | 知识库管理路由组：`/api/local_doc_qa/new_knowledge_base`、`list_knowledge_base`、`delete_knowledge_base`、`rename_knowledge_base`、`get_total_status`、`clean_files_by_status`；`new_knowledge_base` 生成的默认 kb_id 形如 `'KB' + uuid.uuid4().hex`，`quick=True` 时追加 `"_QUICK"` 后缀，且 kb_id 必须以 `KB` 开头 | `qanything_kernel/qanything_server/sanic_api.py`、`qanything_kernel/qanything_server/handler.py::new_knowledge_base` |
| F-qa-037 | 文件管理路由组：`upload_files`（multipart `files`）、`upload_weblink`、`upload_faqs`、`list_files`、`delete_files`、`get_doc_completed`、`get_doc`、`get_file_base64`、`update_chunks`；`upload_files` 限制单库文件总数 ≤ 10000，`upload_faqs` 限制单次 ≤ 1000 条且 question ≤ 512 字符、answer ≤ 2048 字符 | `qanything_kernel/qanything_server/handler.py::upload_files / upload_faqs / list_docs` |
| F-qa-038 | 问答路由 `/api/local_doc_qa/local_doc_chat`：入参含 `kb_ids`（≤ 20 个）、`question`、`history`、`streaming`、`rerank`、`hybrid_search`、`networking`、`api_base`、`api_key`、`api_context_length`、`top_p`、`temperature`、`top_k`（≤ 100）、`model`（默认 `gpt-4o-mini`）、`bot_id`；`api_base` 中的 `0.0.0.0`/`127.0.0.1`/`localhost` 被替换为 `GATEWAY_IP` | `qanything_kernel/qanything_server/handler.py::local_doc_chat` |
| F-qa-039 | `local_doc_chat` 流式响应为 `text/event-stream`，帧格式 `data: {json}\n\n`，末帧 `[DONE]` 后携带完整 `response`、`history`、`source_documents`、`retrieval_documents`、`time_record`；非流式返回单条 JSON；问答结果经 `add_qalog` 落 MySQL QALog 表 | `qanything_kernel/qanything_server/handler.py::local_doc_chat` |
| F-qa-040 | Bot 管理路由组：`new_bot`（bot_id 形如 `'BOT' + uuid.uuid4().hex`）、`delete_bot`、`update_bot`、`get_bot_info`；Bot 的 LLM 参数存于 MySQL `llm_setting` JSON 字段，含 `api_base/api_key/api_context_length/top_p/top_k/chunk_size/temperature/model/max_token/rerank/hybrid_search/networking/only_need_search_results` 键 | `qanything_kernel/qanything_server/handler.py::new_bot / update_bot / get_bot_info` |
| F-qa-041 | 用户标识拼接规则：所有 handler 将 `user_id` 与 `user_info` 以 `user_id + '__' + user_info` 拼接后传入数据层；`check_user_id_and_user_info` 校验 user_id 须以字母开头且只含字母数字下划线 | `qanything_kernel/qanything_server/handler.py`（各 handler 函数头部） |
| F-qa-042 | 文件状态机取值：gray（入库排队）、yellow（入库中）、green（成功）、red（失败）；`update_chunks` 在有 yellow 文件时拒绝执行；`local_doc_chat` 仅检索 status='green' 的文件，若无 green 文件则 kb_ids 置空进入纯对话模式 | `qanything_kernel/qanything_server/handler.py::update_chunks / local_doc_chat`、`qanything_kernel/dependent_server/insert_files_serve/insert_files_server.py` |
| F-qa-043 | `docs/API.md` 为接口文档，与 sanic_api.py 注册的路由路径一一对应（如 `http://{your_host}:8777/api/local_doc_qa/*`），并说明 `user_id="zzp"` 时 API 数据与前端页面互通 | `docs/API.md` |

## 四、脚本（scripts/）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-qa-044 | `scripts/` 目录共 12 个条目：9 个 Python 脚本、2 个 Shell 脚本、1 个 jpg 文件（weixiaobao.jpg），经 Glob 计数 | `scripts/` |
| F-qa-045 | `entrypoint.sh` 依次 nohup 启动 6 个进程：rerank_server.py、embedding_server.py、pdf_parser_server.py、ocr_server.py、insert_files_server.py（`--port 8110 --workers 1`）、sanic_api.py（`--port 8777 --workers 1`），并将全部 PID 写入自动生成的 `close.sh`；启动期间轮询 main_server.log 中 `"Starting worker"` 字符串，180 秒超时即报错退出 | `scripts/entrypoint.sh` |
| F-qa-046 | `entrypoint.sh` 以 `ln -s` 为 5 处模型/数据目录创建软链接：embedding_model_configs_v0.0.1（链接进 embedding_server，指向 /root/models/linux_onnx/）、rerank_model_configs_v0.0.1（链接进 rerank_server，指向 /root/models/linux_onnx/）、ocr_models（链接进 ocr_server，指向 /root/models/）、pdf_models→pdf_to_markdown/checkpoints（指向 /root/models/）、nltk_data（链接到仓库根，指向 /root/nltk_data） | `scripts/entrypoint.sh` |
| F-qa-047 | `memory_usage.sh` 对 6 个进程（rerank_server.py、embedding_server.py、ocr_server.py、insert_files_server.py、sanic_api.py、pdf_parser_server.py）统计 RSS 内存；传参 `long` 时进入每 10 秒记录的长期日志模式 | `scripts/memory_usage.sh` |
| F-qa-048 | `local_chat_qa.py` 为单轮问答测试脚本，`sys.argv[1]` 为问题，POST 至 `http://localhost:8777/api/local_doc_qa/local_doc_chat`，请求体含硬编码 kb_ids、`rerank: False` | `scripts/local_chat_qa.py` |
| F-qa-049 | `stream_chat.py` 为流式问答测试脚本，`sys.argv[1]` 为 kb_id，以 `stream=True` 逐行解析 SSE 帧并去掉 `data: ` 前缀后打印 | `scripts/stream_chat.py` |
| F-qa-050 | `upload_files.py`（`sys.argv[1]`=kb_id、`sys.argv[2]`=文件路径）与 `multi_upload_files.py`（`sys.argv[1]`=文件夹、`sys.argv[2]`=kb_id，aiohttp 异步、mode='soft'）为上传测试脚本；`multi_upload_files.py` 按扩展名白名单收集文件：`.md/.txt/.pptx/.jpg/.jpeg/.png/.docx/.xlsx/.eml/.csv/.pdf` 共 11 种 | `scripts/upload_files.py`、`scripts/multi_upload_files.py` |
| F-qa-051 | `multi_local_chat_qa.py` 为并发问答压测脚本，argparse 参数：`-i/--input_file`（默认 `升学百科benchmark_20231120.xlsx`）、`-o/--output_file`、` -c/--concurrency`（默认 10）、`-n/--total_requests`（默认 100）、`--stream` | `scripts/multi_local_chat_qa.py` |
| F-qa-052 | `new_knowledge_base.py`、`list_files.py` 为硬编码请求示例（分别调用 new_knowledge_base 与 list_files 接口）；`test_embed.py` 与 `test_rerank.py` 为 ONNX 推理性能测试脚本，均定义 TEST_DURATION=10、BATCH_SIZES=[1,2,4,8,16]、NUM_THREADS=[1,2,4] 测试矩阵，分别内嵌 `EmbeddingAsyncBackend`、`RerankAsyncBackend` 类 | `scripts/new_knowledge_base.py`、`scripts/list_files.py`、`scripts/test_embed.py`、`scripts/test_rerank.py` |

## 五、前端（front_end/）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-qa-053 | 前端为 Vue 项目：package.json `name: "ai-demo"`、`version: "2.0.4"`、`tagname: "qanything"`；依赖含 vue 3.3、vite ^5.0.11、pinia ^2.1.7、vue-router ^4.0.11、ant-design-vue 4.x、axios、@microsoft/fetch-event-source、markdown-it、@vue-office/docx/excel/pdf、pdfjs-dist | `front_end/package.json` |
| F-qa-054 | `vite.config.ts` 构建输出目录为 `dist/qanything`，base 取环境变量 `VITE_APP_WEB_PREFIX`，压缩选项 `drop_console`、`drop_debugger`；dev server 端口 5052；插件含 unplugin-vue-components（AntDesignVueResolver）、unplugin-auto-import、vite-plugin-svg-icons、rollup-plugin-visualizer、viteImagemin | `front_end/vite.config.ts` |
| F-qa-055 | `.env.development` 与 `.env.production` 内容一致（除 MODE）：`VITE_APP_API_HOST=/api`、`VITE_APP_API_PREFIX=/api`、`VITE_APP_WEB_PREFIX=/qanything` | `front_end/.env.development`、`front_end/.env.production` |
| F-qa-056 | 后端将前端构建产物目录 `qanything_kernel/qanything_server/dist/qanything/` 以静态路由 `/qanything/` 直接挂载，前端经该路径访问（README 给出入口 `http://localhost:8777/qanything/`） | `qanything_kernel/qanything_server/sanic_api.py`（app.static 调用）、`README.md` |

## 六、部署

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-qa-057 | 三平台 compose 文件服务组成一致：elasticsearch 8.13.2（端口映射 9210:9200，单节点、xpack.security 关闭）、etcd v3.5.5、minio（minioadmin/minioadmin）、milvus v2.4.8 standalone（19540:19530）、mysql 8.4（3316:3306，root 密码 123456）、qanything_local | `docker-compose-linux.yaml`、`docker-compose-mac.yaml`、`docker-compose-win.yaml` |
| F-qa-058 | 三平台差异仅在 QAnything 主镜像名：`xixihahaliu01/qanything-linux:v1.5.1`、`xixihahaliu01/qanything-mac:v1.5.1`、`xixihahaliu01/qanything-win:v1.5.1`；linux 版主容器使用 `network_mode: "host"`，mac/win 版以 ports 映射 | `docker-compose-linux.yaml`、`docker-compose-mac.yaml`、`docker-compose-win.yaml` |
| F-qa-059 | `qanything_local` 服务以 `bash scripts/entrypoint.sh` 启动，挂载仓库根目录到 `/workspace/QAnything/`，环境变量 `GPUID`（默认 0）、`USER_IP`、`Gateway_IP`，并依赖 milvus（healthy）、mysql（started）、elasticsearch（healthy）三个条件 | `docker-compose-linux.yaml` |
| F-qa-060 | compose 数据卷默认落盘于 `${DOCKER_VOLUME_DIRECTORY:-.}/volumes/` 下的 es/etcd/minio/mysql/milvus 子目录；Milvus standalone 依赖 etcd 与 minio（ETCD_ENDPOINTS、MINIO_ADDRESS 环境变量） | `docker-compose-linux.yaml` |

## 附：存疑与未覆盖事项

- F-qa-027 已列出的两个遗留模块（`connector/database/faiss/faiss_client.py`、`connector/database/milvus/milvus_client.py`）存在对 `model_config.py` 中不存在名称的导入，且无任何模块引用它们；RAG 主链路实际使用 `core/retriever/vectorstore.py` 与 `core/retriever/elasticsearchstore.py`。
- `qanything_kernel/core/tools/`、`qanything_kernel/utils/` 下的部分工具函数（如 `general_utils.py` 的 `safe_get`、`check_user_id_and_user_info`）仅在 handler 中被调用，本清单未逐一展开其内部实现。
- `pdf_parser_server/pdf_to_markdown/` 目录（PdfLoader 的模型代码）与 `front_end/src/` 组件层未深入阅读，仅记录了入口与配置级事实。
