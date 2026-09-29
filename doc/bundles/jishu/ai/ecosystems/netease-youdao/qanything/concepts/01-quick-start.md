---
type: concept
title: 部署与最小问答闭环
description: 从 docker-compose 启动到 local_doc_chat 首次问答的端到端走查，涵盖六进程就绪判定、文件状态机观察与 SSE 流式响应的验证方法。
tags: [qanything, deployment, quick-start, rag]
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

# 部署与最小问答闭环

本文带领读者从 docker-compose 启动一路走到第一次成功的知识库问答，重点说明两件事：如何确认六进程全部就绪，以及如何观察文件从上传到可检索的完整生命周期。开始前建议先读 [/concepts/00-overview.md](/concepts/00-overview.md) 建立系统全景。

## 启动与就绪判定

三平台分别使用 `docker-compose-linux.yaml`、`docker-compose-mac.yaml`、`docker-compose-win.yaml`。compose 会拉起基础设施（Milvus、Elasticsearch、MySQL、etcd、minio）与主服务 `qanything_local`，后者以 `bash scripts/entrypoint.sh` 启动，并依赖 milvus（healthy）、mysql（started）、elasticsearch（healthy）三个条件就绪（F-qa-059）。

`entrypoint.sh` 依次以 nohup 启动 6 个进程：rerank_server.py、embedding_server.py、pdf_parser_server.py、ocr_server.py、insert_files_server.py（`--port 8110 --workers 1`）、sanic_api.py（`--port 8777 --workers 1`），并把全部 PID 写入自动生成的 `close.sh`（F-qa-045）。就绪判据是轮询 main_server.log 中出现 `"Starting worker"` 字符串，超过 180 秒未出现即报错退出（F-qa-045）——这是日志字符串匹配而非 HTTP 健康探测，排障时应直接看日志而非仅盯容器状态。

启动脚本还会以 `ln -s` 为 5 处模型/数据目录创建软链接（embedding/rerank 模型配置指向 `/root/models/linux_onnx/`、ocr 模型与 pdf_to_markdown/checkpoints 指向 `/root/models/`、nltk_data 指向 `/root/nltk_data`），模型文件缺失时服务将无法就绪（F-qa-046）。`scripts/memory_usage.sh` 可按进程统计这 6 个进程的 RSS 内存，传参 `long` 进入每 10 秒记录的长期日志模式（F-qa-047），是验证资源占用是否达预期的直接工具。

## 前端入口

前端为 Vue 3 项目（package 名 `ai-demo`，版本 2.0.4），开发服务器端口 5052，构建产物输出到 `dist/qanything`；后端将构建产物目录以静态路由 `/qanything/` 挂载（F-qa-053、F-qa-054、F-qa-056）。因此容器部署后浏览器访问 `http://localhost:8777/qanything/` 即可使用 Web 界面；API 数据与前端页面以 `user_id` 隔离互通，例如 API 文档示例中 `user_id="zzp"` 的数据与前端所见一致（F-qa-043）。

## 最小问答闭环

最小闭环只需三步：建知识库 → 传文件 → 提问。仓库 `scripts/` 目录提供了可直接运行的测试脚本（共 12 个条目：9 个 Python、2 个 Shell、1 个 jpg，F-qa-044）：

1. **建库**：`python scripts/new_knowledge_base.py` 向 `POST /api/local_doc_qa/new_knowledge_base` 发送 `{"user_id": "zzp", "kb_name": "kb_test"}`，服务端生成形如 `'KB' + uuid.uuid4().hex` 的 kb_id（F-qa-036、F-qa-052）。
2. **传文件**：`python scripts/upload_files.py <kb_id> <文件路径>` 以 multipart 上传单文件到 `POST /api/local_doc_qa/upload_files`（F-qa-050）；批量上传可用 `multi_upload_files.py <文件夹> <kb_id>`（aiohttp 异步、mode='soft'，按 11 种扩展名白名单收集文件，单请求最多 200MB，F-qa-050）。
3. **提问**：`python scripts/local_chat_qa.py "你的问题"` 以非流式调用 `POST /api/local_doc_qa/local_doc_chat`，请求体含硬编码 kb_ids 与 `rerank: False`，打印 `response` 字段与耗时（F-qa-048）。

`local_doc_chat` 的完整入参面包括 `kb_ids`（≤ 20 个）、`question`、`history`、`streaming`、`rerank`、`hybrid_search`、`model`（默认 `gpt-4o-mini`）、`api_base`、`api_key`、`api_context_length`、`top_p`、`temperature`、`top_k`（≤ 100）等；注意 `api_base` 中的 `0.0.0.0`/`127.0.0.1`/`localhost` 会被替换为 `GATEWAY_IP`（F-qa-038）。

## 观察文件状态机

上传不等于可检索。文件入库由 insert_files_server 后台异步执行，状态机取值（F-qa-042、F-qa-032）：

| 状态 | 含义 |
|---|---|
| gray | 入库排队（写入 MySQL File 表待处理） |
| yellow | 入库中 |
| green | 入库成功，可参与检索 |
| red | 入库失败 |

只有 status='green' 的文件会被 `local_doc_chat` 检索；若请求涉及的知识库没有任何 green 文件，kb_ids 会被置空，问题退化为纯对话模式（不带知识库上下文）（F-qa-042）。因此首次问答若发现"答非所问"，应先查文件状态而非怀疑检索质量——`list_files` 路由与前端文件列表均可观察该状态（F-qa-037）。另外 Milvus 侧有缓冲落盘参数（flush_interval=600 秒或 flush_threshold=10000 条），刚入库文档的向量并非立即可检索（F-qa-014），"上传立即可问"存在时间窗。

## 流式响应的验证

传 `streaming: True` 时响应为 `text/event-stream`：每帧形如 `data: {json}\n\n`，末帧为 `[DONE]`，随后附带完整 `response`、`history`、`source_documents`、`retrieval_documents`、`time_record` 的汇总帧（F-qa-039）。`python scripts/stream_chat.py <kb_id>` 演示了逐行解析 SSE 帧并去掉 `data: ` 前缀的客户端写法（F-qa-049）。问答结果会经 `add_qalog` 落入 MySQL QALog 表，便于事后审计（F-qa-039）。

## 常见踩坑

- **180 秒启动超时**：多半是模型软链接缺失或 GPU 不可用，查 main_server.log（F-qa-045、F-qa-046）。
- **提问无知识库味道**：文件仍是 gray/yellow/red，或知识库无 green 文件触发纯对话回退（F-qa-042）。
- **api_base 连不上本机 LLM**：确认是否踩了 `0.0.0.0`/`127.0.0.1`/`localhost` 被替换为 GATEWAY_IP 的规则（F-qa-038）。
- **compose 镜像版本**：git 基线为 v2.0.0 后 HEAD，但 compose 主镜像 tag 为 v1.5.1，两者不保证一致（F-qa-058）。

## 相关概念

- [00 QAnything 全景](/concepts/00-overview.md)
- [02 LocalDocQA 问答编排链与硬编码阈值](/concepts/02-rag-pipeline.md)
- [06 API 层、Bot 配置与知识库运维](/concepts/06-api-ops.md)
- 示例：[最小问答闭环](/examples/minimal-qa-loop.md)、[API 流式问答调用](/examples/api-streaming-chat.md)
