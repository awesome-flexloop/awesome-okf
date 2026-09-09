---
type: concept
title: API 层、Bot 配置与知识库运维
description: 28 条路由的四大功能组（知识库/文件/Bot/问答）、user_id__user_info 标识拼接、Bot LLM 参数 JSON 配置与 gray→green 文件状态机的运维语义。
tags: [qanything, api, sanic, bot, operations]
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

# API 层、Bot 配置与知识库运维

主服务 `sanic_api.py` 是名为 `"QAnything"` 的 Sanic 应用，共注册 28 条路由——全部为 GET/POST，其中仅 `GET /api/docs` 与 `GET /api/health_check` 两条为 GET，其余 26 条为 POST（F-qa-035）。接口文档 `docs/API.md` 与注册路由一一对应，路径形如 `http://{your_host}:8777/api/local_doc_qa/*`（F-qa-043）。本文按四大功能组梳理这些路由及其背后的运维语义。

## 应用级配置

启动参数 `--host`（默认 `0.0.0.0`）、`--port`（默认 8777）、`--workers`（默认 4）；`REQUEST_MAX_SIZE` 设为 128MB（大文件上传场景），CORS 放开到 `*`；前端构建产物以静态路由 `/qanything/` 挂载（F-qa-034、F-qa-056）。

## 用户标识：user_id + '__' + user_info

所有 handler 将 `user_id` 与 `user_info` 以 `user_id + '__' + user_info` 拼接后传入数据层，`check_user_id_and_user_info` 校验 user_id 须以字母开头且只含字母数字下划线（F-qa-041）。`user_info` 缺省为 `"1234"`。这一拼接既是数据隔离键，也是 API 与前端互通的桥梁：API 文档示例中 `user_id="zzp"` 产生的数据与前端页面所见一致（F-qa-043）。运维含义：直接用 API 灌测试数据会污染同名前端用户的数据面，压测应使用独立 user_id。

## 四大功能组

### 知识库管理组

`/api/local_doc_qa/` 下的 `new_knowledge_base`、`list_knowledge_base`、`delete_knowledge_base`、`rename_knowledge_base`、`get_total_status`、`clean_files_by_status`。`new_knowledge_base` 生成默认 kb_id 形如 `'KB' + uuid.uuid4().hex`，`quick=True` 时追加 `"_QUICK"` 后缀，且 kb_id 必须以 `KB` 开头（F-qa-036）。

### 文件管理组

`upload_files`（multipart `files`）、`upload_weblink`、`upload_faqs`、`list_files`、`delete_files`、`get_doc_completed`、`get_doc`、`get_file_base64`、`update_chunks`。配额约束（F-qa-037）：

- `upload_files`：单库文件总数 ≤ 10000；
- `upload_faqs`：单次 ≤ 1000 条，question ≤ 512 字符、answer ≤ 2048 字符。

`update_chunks` 用于调整文件 chunk 参数，但在有 yellow（入库中）文件时拒绝执行，避免边入库边改切分导致的数据错乱（F-qa-042）。

### Bot 管理组

`new_bot`（bot_id 形如 `'BOT' + uuid.uuid4().hex`）、`delete_bot`、`update_bot`、`get_bot_info`。Bot 的核心价值是把一组知识库 + LLM 参数 + 自定义 prompt 固化为可复用配置：LLM 参数存于 MySQL `llm_setting` JSON 字段，含 `api_base/api_key/api_context_length/top_p/top_k/chunk_size/temperature/model/max_token/rerank/hybrid_search/networking/only_need_search_results` 键（F-qa-040）。调用 `local_doc_chat` 时传入 `bot_id` 即整体套用该配置，无需逐次传参。

### 问答组

核心路由 `POST /api/local_doc_qa/local_doc_chat`，入参面见 [/concepts/01-quick-start.md](/concepts/01-quick-start.md) 与 [/concepts/02-rag-pipeline.md](/concepts/02-rag-pipeline.md)；流式帧格式 `data: {json}\n\n` + 末帧 `[DONE]`，非流式返回单条 JSON，问答结果经 `add_qalog` 落 MySQL QALog 表（F-qa-039）。约束：`kb_ids` ≤ 20 个、`top_k` ≤ 100、`only_need_search_results` 与 `streaming` 不能同时为 True（F-qa-038）。

## 文件状态机的运维语义

gray（入库排队）→ yellow（入库中）→ green（成功）/ red（失败）的状态机是 API 运维的主线（F-qa-042）：

- `local_doc_chat` 仅检索 status='green' 的文件；若请求的知识库无任何 green 文件，kb_ids 被置空，问题退化为纯对话模式——这是"答非所问"类投诉的第一排查点；
- `get_total_status`、`get_doc_completed` 等路由用于批量观测进度；
- `clean_files_by_status` 可按状态清理失败/残留文件；
- red 文件应先查 `content_length > MAX_CHARS`（1000000）或内容为空等入库失败原因（F-qa-033）。

## 配套测试脚本

`scripts/` 目录提供与各路由一一对应的请求示例：`new_knowledge_base.py`、`list_files.py`（硬编码请求示例），`upload_files.py`/`multi_upload_files.py`（单文件/批量上传），`local_chat_qa.py`（单轮问答）、`stream_chat.py`（流式问答），`multi_local_chat_qa.py`（并发压测，argparse 参数 `-i/-o/-c/--concurrency`（默认 10）`-n/--total_requests`（默认 100）`--stream`），`test_embed.py`/`test_rerank.py`（ONNX 推理性能测试，均定义 TEST_DURATION=10、BATCH_SIZES=[1,2,4,8,16]、NUM_THREADS=[1,2,4] 测试矩阵）（F-qa-048~F-qa-052）。

## 相关概念

- [01 部署与最小问答闭环](/concepts/01-quick-start.md)
- [02 LocalDocQA 问答编排链与硬编码阈值](/concepts/02-rag-pipeline.md)
- [05 依赖服务化：五个本地推理/解析进程](/concepts/05-dependent-servers.md)
- 示例：[最小问答闭环](/examples/minimal-qa-loop.md)、[API 流式问答调用](/examples/api-streaming-chat.md)
