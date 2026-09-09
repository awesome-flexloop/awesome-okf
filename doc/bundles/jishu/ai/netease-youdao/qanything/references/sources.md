---
type: reference
title: QAnything 信源登记
description: 网易有道 QAnything 开源仓库的固定基线、许可证与关键信源文件清单（R/I 阶段共用）
tags: [qanything, rag, netease-youdao, reference, source]
generated: { by: okf-wiki/0.2, at: 2026-09-09 }
phase: R/I（事实采集与架构洞察）
baseline: v2.0.0 后 HEAD @ 615417a
status: stable
verified: { by: "process:seven-concepts-v-fix", at: "2026-09-09" }
stale_after: 2027-09-09
sources:
  - resource: vendor/netease-youdao/QAnything/
---

# QAnything 信源登记

本知识包基于网易有道开源的 **QAnything**（Question and Answer based on Anything，本地知识库问答/RAG 系统）源码仓库整理而成。事实清单（`facts.md`）与架构洞察（`insights.md`）中的全部 F-qa-xxx 编号事实均溯源至本表登记的固定基线源码。vendor 路径为只读 git submodule，分析期间未作任何修改。

## 上游仓库与固定基线

| 项目 | 值 |
|---|---|
| 上游仓库 | git@github.com:netease-youdao/QAnything.git（GitHub 镜像入口：https://github.com/netease-youdao/QAnything） |
| 最近 tag | v2.0.0 |
| 固定基线 | **v2.0.0 之后 HEAD**（`git describe` 输出 `v2.0.0-69-g615417a`） |
| Pin commit（完整 hash） | `615417a92420d77a2606392a74f5771ca2f31a4b` |
| 基线提交信息 | `docs: keep business contacts in README`（2026-09-03 17:40:04 +0800） |
| 本地路径 | `vendor/netease-youdao/QAnything/`（git submodule，只读） |
| 许可证 | **AGPL-3.0**（GNU Affero General Public License v3，见仓库根 `LICENSE`）——衍生发布与网络服务场景须特别注意其 copyleft 传染性 |

> 版本核对命令：`git -C vendor/netease-youdao/QAnything rev-parse HEAD`

## 关键信源文件清单

以下文件为 facts.md 事实的主要证据来源（路径相对 `vendor/netease-youdao/QAnything/`），按主题分组：

### RAG 内核（core/）

| 文件 | 关键内容 | 关联事实 |
|---|---|---|
| `qanything_kernel/core/local_doc_qa.py` | `LocalDocQA` 编排类：问答主链、rerank 过滤阈值、FAQ 短路、prompt 组装 | F-qa-001~F-qa-009 |
| `qanything_kernel/core/local_file.py` | `LocalFile`：file_id 生成、FAQ/URL/文件三分支入库前处理 | F-qa-026 |
| `qanything_kernel/core/retriever/parent_retriever.py` | `ParentRetriever`/`SelfParentRetriever`：父子切分、双写、混合检索 | F-qa-010~F-qa-012 |
| `qanything_kernel/core/retriever/vectorstore.py` | `VectorStoreMilvusClient`/`SelfMilvus`：kb_id partition key、缓冲落盘 | F-qa-013、F-qa-014 |
| `qanything_kernel/core/retriever/elasticsearchstore.py` | `StoreElasticSearchClient`：BM25 策略、按 file_id 逐条删除 | F-qa-015 |
| `qanything_kernel/core/retriever/docstrore.py` | `MysqlStore`：parent 文档落 MySQL、FAQ 展开 | F-qa-016 |
| `qanything_kernel/core/chains/condense_q_chain.py` | `RewriteQuestionChain`：多轮问题改写链 | F-qa-017 |

### 连接器（connector/）

| 文件 | 关键内容 | 关联事实 |
|---|---|---|
| `qanything_kernel/connector/embedding/embedding_for_online_client.py` | `YouDaoEmbeddings`：本地 embedding 服务客户端、图文行过滤 | F-qa-018 |
| `qanything_kernel/connector/rerank/rerank_for_online_client.py` | `YouDaoRerank`：本地 rerank 服务客户端、分批与排序 | F-qa-019 |
| `qanything_kernel/connector/llm/llm_for_openai_api.py` | `OpenAILLM`：OpenAI 兼容 LLM、token 余量系数 | F-qa-020 |
| `qanything_kernel/connector/llm/base/base.py` | `AnswerResult`/`BaseAnswer`：LLM 抽象层 | F-qa-021 |
| `qanything_kernel/connector/database/mysql/mysql_client.py` | `KnowledgeBaseManager`：57 个方法的数据管理层 | F-qa-022 |
| `qanything_kernel/connector/database/faiss/faiss_client.py` | ⚠️ 遗留死代码（导入不存在的 `FAISS_LOCATION` 等） | F-qa-027 |
| `qanything_kernel/connector/database/milvus/milvus_client.py` | ⚠️ 遗留死代码（导入不存在的 `MILVUS_HOST_ONLINE` 等） | F-qa-027 |

### 配置（configs/）

| 文件 | 关键内容 | 关联事实 |
|---|---|---|
| `qanything_kernel/configs/model_config.py` | 全部常量：检索 top_k/阈值、切分参数、服务 URL、端口、提示词模板、Bot 默认配置 | F-qa-023~F-qa-025 |

### 依赖服务（dependent_server/）

| 文件 | 关键内容 | 关联事实 |
|---|---|---|
| `qanything_kernel/dependent_server/embedding_server/embedding_server.py` | embedding Sanic 服务，POST /embedding，9001 | F-qa-028 |
| `qanything_kernel/dependent_server/rerank_server/rerank_server.py` | rerank Sanic 服务，POST /rerank，8001 | F-qa-029 |
| `qanything_kernel/dependent_server/ocr_server/ocr_server.py` | OCR 服务，POST /ocr，7001（DBNet 检测 + CTC 识别） | F-qa-030 |
| `qanything_kernel/dependent_server/pdf_parser_server/pdf_parser_server.py` | PDF 解析服务，POST /pdfparser，9009 | F-qa-031 |
| `qanything_kernel/dependent_server/insert_files_serve/insert_files_server.py` | 文件入库服务，MySQL 轮询 gray 记录 | F-qa-032、F-qa-033 |

### API 层（qanything_server/）

| 文件 | 关键内容 | 关联事实 |
|---|---|---|
| `qanything_kernel/qanything_server/sanic_api.py` | 主 Sanic 应用、28 条路由注册、静态挂载 | F-qa-034、F-qa-035 |
| `qanything_kernel/qanything_server/handler.py` | 全部 handler：知识库/文件/Bot 管理、local_doc_chat、状态机 | F-qa-036~F-qa-042 |
| `docs/API.md` | 接口文档，与注册路由一一对应 | F-qa-043 |

### 脚本与前端（scripts/、front_end/）

| 文件 | 关键内容 | 关联事实 |
|---|---|---|
| `scripts/entrypoint.sh` | 六进程启动编排、模型目录软链接 | F-qa-045、F-qa-046 |
| `scripts/memory_usage.sh` | 六进程 RSS 内存统计 | F-qa-047 |
| `scripts/local_chat_qa.py`、`scripts/stream_chat.py`、`scripts/upload_files.py`、`scripts/multi_upload_files.py`、`scripts/multi_local_chat_qa.py` | 上传/单轮/流式/压测测试脚本 | F-qa-048~F-qa-051 |
| `scripts/new_knowledge_base.py`、`scripts/list_files.py`、`scripts/test_embed.py`、`scripts/test_rerank.py` | 硬编码请求示例与 ONNX 性能测试 | F-qa-052 |
| `front_end/package.json`、`front_end/vite.config.ts`、`front_end/.env.*` | Vue 3 前端技术栈与构建配置 | F-qa-053~F-qa-055 |
| `qanything_kernel/qanything_server/dist/qanything/`（构建产物挂载点） | 前端产物静态路由 `/qanything/` | F-qa-056 |

### 部署（compose 文件）

| 文件 | 关键内容 | 关联事实 |
|---|---|---|
| `docker-compose-linux.yaml` / `docker-compose-mac.yaml` / `docker-compose-win.yaml` | 基础设施服务组合（ES 8.13.2、etcd、minio、Milvus 2.4.8、MySQL 8.4）与主镜像 tag v1.5.1 | F-qa-057~F-qa-060 |
| `README.md` | 项目说明与前端入口路径 | F-qa-056 |

## 时效与基线说明

- 基线固定于 2026-09-09 时 submodule 的 HEAD（pin commit `615417a92420d77a2606392a74f5771ca2f31a4b`）。上游仍在活跃演进，后续事实采集须先核对 submodule HEAD 是否漂移。
- 已知版本错位：compose 主镜像 tag 为 v1.5.1、前端版本 2.0.4、git tag v2.0.0，三者不一致（详见 insights.md 洞察五），引用版本号时须注明口径。
- 存疑事实（F-qa-027）已确认为遗留死代码，非笔误；其余未覆盖事项（`core/tools/`、`pdf_to_markdown/` 模型代码、`front_end/src/` 组件层）见 facts.md 附录。
