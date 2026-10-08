---
type: concept
title: QAnything 全景——六进程 RAG 应用架构
description: 一页看懂 QAnything 系统全景：Vue 前端、Sanic API 主服务、五个本地推理/解析服务进程与 Milvus/Elasticsearch/MySQL 三存储的分工与协作关系。
tags: [qanything, rag, architecture, overview]
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

# QAnything 全景——六进程 RAG 应用架构

QAnything（Question and Answer based on Anything）是网易有道开源的本地知识库问答系统，属于检索增强生成（Retrieval-Augmented Generation，RAG）应用：用户上传文档构建知识库，随后以自然语言提问，系统先从知识库中检索相关片段，再交由大语言模型（LLM）组织回答。本文从系统全景视角拆解它的进程结构、存储分层与请求通路，帮助读者在深入各子系统之前先建立完整心智模型。

## 系统组成总览

一个运行中的 QAnything 实例由 **1 个主 API 进程 + 5 个本地推理/解析服务进程 + 3 个存储服务** 构成（F-qa-045、F-qa-057）：

```
┌─────────────────────────────────────────────────────────┐
│  浏览器前端（Vue 3，构建产物挂载于 /qanything/）           │
├─────────────────────────────────────────────────────────┤
│  主 API 服务 sanic_api.py（Sanic，默认 0.0.0.0:8777）      │
│  ┌──────────────┐  28 条路由：知识库/文件/Bot/问答         │
│  │ LocalDocQA   │  问答编排核心（core/local_doc_qa.py）   │
│  └──────────────┘                                       │
├──────────┬──────────────┬───────────────┬────────────────┤
│ embedding│ rerank       │ OCR           │ PDF 解析       │
│ :9001    │ :8001        │ :7001         │ :9009          │
├──────────┴──────────────┴───────┬───────┴────────────────┤
│  insert_files 文件入库服务 :8110（轮询 MySQL 处理队列）    │
├─────────────────────────────────────────────────────────┤
│  Milvus :19540（向量） Elasticsearch :9210（文本）        │
│  MySQL :3316（结构化：File/Document/QALog/Bot...）        │
└─────────────────────────────────────────────────────────┘
```

主 API 服务是名为 `"QAnything"` 的 Sanic 应用，启动参数 `--host`（默认 `0.0.0.0`）、`--port`（默认 8777）、`--workers`（默认 4），单请求体上限 128MB，CORS 放开到 `*`（F-qa-034）。它将前端构建产物目录 `qanything_kernel/qanything_server/dist/qanything/` 以静态路由 `/qanything/` 直接挂载，因此部署后浏览器入口是 `http://localhost:8777/qanything/`（F-qa-056）。

## 进程组：五个 dependent_server

推理与解析能力被拆分为五个独立的 Sanic 微服务进程，主服务通过 `model_config.py` 中的 localhost URL 常量以 HTTP 调用它们（F-qa-024）：

| 进程 | 端口 | 路由 | 职责 |
|---|---|---|---|
| embedding_server | 9001 | `POST /embedding` | 文本向量化（ONNX 后端） |
| rerank_server | 8001 | `POST /rerank` | 查询-文档相关性重排序（ONNX 后端） |
| ocr_server | 7001 | `POST /ocr` | 图像文字识别（DBNet 检测 + CTC 识别） |
| pdf_parser_server | 9009 | `POST /pdfparser` | PDF 转 Markdown 解析 |
| insert_files_server | 8110 | 无对外业务路由 | 后台轮询 MySQL，执行文件入库流水线 |

这五个服务的接口契约、推理后端与运维要点详见 [/concepts/05-dependent-servers.md](/concepts/05-dependent-servers.md)。需要注意它们是**共享单机生命周期的进程组**：服务间是裸 HTTP + localhost 的紧耦合，进程编排完全依赖 `scripts/entrypoint.sh` 以 nohup 拉起并记录 PID，没有服务发现与进程守护（F-qa-045）。

## 存储分层：三库各司其职

QAnything 将数据按访问模式分配到三种存储中：

- **Milvus**（向量库，容器端口 19540）：存储 child chunk 的 embedding，承担语义相似度检索；
- **Elasticsearch**（文本索引，容器端口映射 9210:9200）：存储文档文本，承担 BM25 关键词检索，`hybrid_search` 开启时与 Milvus 结果合并去重；
- **MySQL**（结构化数据，容器端口映射 3316:3306）：管理文件元数据与状态机、parent 文档全文、FAQ 内容、问答日志（QALog）与 Bot 配置，由 `KnowledgeBaseManager` 统一访问（57 个方法，F-qa-022）。

三库的职责划分与多租户隔离设计详见 [/concepts/04-storage-multitenancy.md](/concepts/04-storage-multitenancy.md)。

## 一次问答请求的通路

以一次典型的知识库问答为例，请求的完整通路是（F-qa-002、F-qa-038）：

1. 前端或脚本向 `POST /api/local_doc_qa/local_doc_chat` 发起请求；
2. handler 校验用户标识、组装 LLM 参数，调用 `LocalDocQA.get_knowledge_based_answer()`；
3. 若带多轮 history，先经 `RewriteQuestionChain` 将问题改写为独立问句（F-qa-017）；
4. 向 embedding 服务（9001）获取查询向量，经 ParentRetriever 从 Milvus/ES 检索 child 文档，并从 MySQL 回填 parent 全文；
5. 查询 token 数不超过 300 时调用 rerank 服务（8001）精排并过滤；
6. 检索文档以 `<reference>` 标签包裹拼入 prompt 模板，调用 LLM 生成回答；
7. 以 SSE（Server-Sent Events）逐帧返回增量输出，末帧 `[DONE]` 后附完整 `response`、`source_documents` 等字段（F-qa-039）。

这条链路的逐帧拆解与其中散布的硬编码阈值，是 [/concepts/02-rag-pipeline.md](/concepts/02-rag-pipeline.md) 的主题。

## 部署形态

三个 docker-compose 文件（linux/mac/win）的基础设施服务组成一致：Elasticsearch 8.13.2、etcd v3.5.5、minio、Milvus v2.4.8 standalone、MySQL 8.4 与 `qanything_local` 主服务；差异仅在主镜像名（三平台分别为 `xixihahaliu01/qanything-{linux,mac,win}:v1.5.1`）与网络模式（linux 用 host 网络，mac/win 用端口映射）（F-qa-057、F-qa-058）。compose 数据卷默认落盘于 `${DOCKER_VOLUME_DIRECTORY:-.}/volumes/` 下各服务子目录（F-qa-060）。

> ⚠️ 注意版本口径：git 基线为 v2.0.0 之后的 HEAD，但 compose 主镜像 tag 仍为 v1.5.1、前端版本为 2.0.4，三者不一致。版本错位现象及其成因见 [/concepts/07-evolution-traces.md](/concepts/07-evolution-traces.md)。

## 学习路径建议

- 想尽快跑起来并调用 API：读 [/concepts/01-quick-start.md](/concepts/01-quick-start.md) 与 [/concepts/06-api-ops.md](/concepts/06-api-ops.md)；
- 想理解问答行为与调参：读 [/concepts/02-rag-pipeline.md](/concepts/02-rag-pipeline.md)；
- 想做二次开发或架构借鉴：沿 02 → 03 → 04 → 05 → 07 完整走一遍。

## 相关概念

- [01 部署与最小问答闭环](/concepts/01-quick-start.md)
- [02 LocalDocQA 问答编排链与硬编码阈值](/concepts/02-rag-pipeline.md)
- [05 依赖服务化：五个本地推理/解析进程](/concepts/05-dependent-servers.md)
- [06 API 层、Bot 配置与知识库运维](/concepts/06-api-ops.md)
