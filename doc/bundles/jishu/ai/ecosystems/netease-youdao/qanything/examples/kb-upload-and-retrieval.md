---
type: example
title: 知识库上传与检索流程——批量入库到命中回填
description: 以 multi_upload_files.py 为例演练批量上传（扩展名白名单、200MB 分批、aiohttp 并发），并拆解后端入库流水线与"child 命中、parent 回填"的检索链路。
tags: [qanything, example, upload, ingestion, retrieval]
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

# 知识库上传与检索流程——批量入库到命中回填

本例以 `scripts/multi_upload_files.py` 为主线，演练"整目录批量上传 → 异步入库 → 检索命中回填"的完整数据通路，帮助理解上传接口的吞吐设计参数与检索链路上父子文档的协作方式。

## 批量上传客户端

`multi_upload_files.py`（`sys.argv[1]`=文件夹，`sys.argv[2]`=kb_id）的核心逻辑（F-qa-050）：

```python
import os, sys, aiohttp, asyncio

file_folder = sys.argv[1]
kb_id = sys.argv[2]
support_end = ('.md', '.txt', '.pptx', '.jpg', '.jpeg', '.png',
               '.docx', '.xlsx', '.eml', '.csv', '.pdf')   # 11 种扩展名白名单

files = []
for root, dirs, file_names in os.walk(file_folder):
    for file_name in file_names:
        if file_name.endswith(support_end):
            files.append(os.path.join(root, file_name))

async def send_request(round_, files):
    url = 'http://0.0.0.0:8777/api/local_doc_qa/upload_files'
    data = aiohttp.FormData()
    data.add_field('user_id', 'default')
    data.add_field('kb_id', kb_id)
    data.add_field('mode', 'soft')
    for file_path in files:
        data.add_field('files', open(file_path, 'rb'))
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
        async with session.post(url, data=data) as response:
            print(f"round_:{round_}, 状态码: {response.status}")
```

编排策略是**按体积分批 + 信号量限流**（F-qa-050）：

```python
# 一次请求最多发送 200MB 的文件；最多 4 个并发请求
await create_tasks_by_size_limit(files, 200)   # 内部 Semaphore(4)
```

三个设计要点：

1. **白名单收集**：仅 `.md/.txt/.pptx/.jpg/.jpeg/.png/.docx/.xlsx/.eml/.csv/.pdf` 11 种扩展名入库（F-qa-050）；图片类文件依赖 OCR 服务（7001 端口）提取文本（F-qa-030）；
2. **体积分批**：单请求累计不超过 200MB，避免触及 `REQUEST_MAX_SIZE=128MB` 级别的服务端限制与内存峰值（F-qa-034）；
3. **超时与重试边界**：aiohttp 总超时 300 秒；`mode='soft'` 为服务端去重/容错模式参数。

运行：`python scripts/multi_upload_files.py ./docs_folder KBxxxxxxxx`。

## 服务端入库流水线

上传接口返回后，数据沿以下链路异步入库（F-qa-026、F-qa-032、F-qa-033）：

```
upload_files handler
  → LocalFile 生成 file_id（uuid4.hex），文件落盘 UPLOAD_ROOT_PATH/user_id/kb_id/file_id/
  → MySQL File 表登记 status='gray'
insert_files_server（轮询 MOD(id, INSERT_WORKERS)=worker_id 的 gray 记录）
  → status='yellow'
  → pdf_parser（9009）/ OCR（7001）解析文本（PDF 与图片类）
  → split_file_to_docs：父子两级切分（parent 800 / child 400，parent overlap 0、child overlap 100）
       [300 秒超时]
  → child 双写 Milvus（向量）+ Elasticsearch（BM25 文本），带 [headers] 前缀
  → parent 全文落 MySQL Document 表（MysqlStore）
       [milvus insert 300 秒超时]
  → status='green'，记录 time_record
异常或 content_length > MAX_CHARS(1000000)/为 0 → status='red'
```

入库完成后，Milvus 侧还有缓冲落盘窗口（flush_interval=600 秒或 flush_threshold=10000 条），极端情况下向量检索可能短暂滞后于 green 状态（F-qa-014）。

## 检索：child 命中、parent 回填

提问时（`local_doc_chat`，F-qa-012、F-qa-016）：

1. 查询向量化后经 `ParentRetriever.get_retrieved_documents()` 以 `kb_id in [...]` 表达式在 Milvus 做 similarity 检索，命中 **child chunk**（向量检索 top_k 默认 30，F-qa-023）；
2. `hybrid_search=True` 时再以 Elasticsearch `terms` filter 检索 BM25 结果并合并去重，元数据标记 `retrieval_source` 为 `'milvus'` 或 `'es'`（F-qa-012）；
3. `MysqlStore.mget()` 按 child → parent 关联回填 **parent 全文**（FAQ 条目展开为 `question：answer`），进入 prompt 组装（F-qa-016）。

这就解释了检索结果里"命中的片段比预期长"的现象：LLM 读到的是 800 字的 parent，而命中定位靠的是 400 字的 child（切分参数见 F-qa-010、F-qa-025）。

## 排障对照表

| 现象 | 排查点 | 事实编号 |
|---|---|---|
| 文件上传后长期 gray | insert_files_server 是否存活、MySQL 连接 | F-qa-032、F-qa-045 |
| 状态 red | 内容超 MAX_CHARS(1000000) 或为空 | F-qa-033 |
| green 了但检索不到 | Milvus 缓冲落盘窗口（600s/10000 条） | F-qa-014 |
| 图片内容问答为空 | OCR 服务（7001）就绪与 drop_score | F-qa-030 |
| 命中片段过长/过短 | parent/child 切分参数与 update_chunks | F-qa-010、F-qa-042 |

## 相关概念

- [03 父子切分与 Milvus/ES 混合检索](/concepts/03-retrieval.md)
- [04 Milvus 分区多租户与三存储分层](/concepts/04-storage-multitenancy.md)
- [05 依赖服务化：五个本地推理/解析进程](/concepts/05-dependent-servers.md)
- 示例：[最小问答闭环](/examples/minimal-qa-loop.md)
