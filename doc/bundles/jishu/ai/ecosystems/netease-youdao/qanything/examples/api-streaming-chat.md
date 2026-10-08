---
type: example
title: API 流式问答调用——SSE 帧解析与 LLM 参数透传
description: 以 stream_chat.py 为例演练流式问答客户端：local_doc_chat 的 streaming 模式、SSE 帧格式（data: 前缀 + [DONE] 末帧）、增量解析与 LLM 参数透传的最佳实践。
tags: [qanything, example, api, sse, streaming]
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

# API 流式问答调用——SSE 帧解析与 LLM 参数透传

本例基于 `scripts/stream_chat.py` 演练 `local_doc_chat` 的流式调用：服务端按 SSE 逐帧推送生成器的中间产物，客户端需正确解析 `data: ` 前缀、`[DONE]` 末帧与汇总帧。适合对接自研前端、客服机器人等需要逐字渲染回答的场景。

## 帧格式回顾

`local_doc_chat` 流式响应为 `text/event-stream`（F-qa-039）：

- 每帧格式 `data: {json}\n\n`；生成器依次产出改写后问题、检索文档、rerank 结果、prompt、LLM 增量输出（F-qa-002）；
- 末帧为 `[DONE]`，随后附带完整 `response`、`history`、`source_documents`、`retrieval_documents`、`time_record` 的汇总数据（F-qa-039）。

## 最小流式客户端

`stream_chat.py`（`sys.argv[1]` 为 kb_id）的解析写法（F-qa-049）：

```python
import json, requests, sys

kb_id = sys.argv[1]

def stream_requests(data_raw):
    url = 'http://0.0.0.0:8777/api/local_doc_qa/local_doc_chat'
    response = requests.post(url, json=data_raw, timeout=60, stream=True)
    for line in response.iter_lines(decode_unicode=False, delimiter=b"\n\n"):
        if line:
            yield line

data_raw = {
    "kb_ids": [kb_id],
    "question": "韦小宝身份证号？",
    "user_id": "zzp",
    "streaming": True,
    "history": []
}
for chunk in stream_requests(data_raw):
    chunkstr = chunk.decode("utf-8")[6:]      # 去掉 "data: " 前缀
    chunkjs = json.loads(chunkstr)
    print(chunkjs)
```

`iter_lines(delimiter=b"\n\n")` 以空行切分 SSE 事件、`[6:]` 去掉 `data: ` 前缀，是解析该接口帧的最小逻辑（F-qa-049）。

## 生产可用的健壮版本

真实接入需补全三处：LLM 参数透传、`[DONE]` 终止判定与增量渲染：

```python
import json, requests

def chat_stream(question, kb_ids, history=None):
    url = 'http://localhost:8777/api/local_doc_qa/local_doc_chat'
    payload = {
        "user_id": "zzp",
        "kb_ids": kb_ids,                  # ≤ 20 个
        "question": question,
        "history": history or [],
        "streaming": True,
        "rerank": True,
        "hybrid_search": True,
        "api_base": "http://192.168.1.10:11434/v1",   # 外部 LLM；0.0.0.0/127.0.0.1/localhost 会被替换为 GATEWAY_IP
        "api_key": "ollama",
        "api_context_length": 4096,
        "top_p": 0.99,
        "temperature": 0.5,
        "top_k": 30,                       # ≤ 100
        "model": "gpt-4o-mini",            # 缺省默认值
    }
    response = requests.post(url, json=payload, timeout=60, stream=True)
    for line in response.iter_lines(decode_unicode=True, delimiter="\n\n"):
        if not line:
            continue
        frame = line[len("data: "):]
        if frame == "[DONE]":
            break
        yield json.loads(frame)
```

参数要点（F-qa-038）：

- `api_base`/`api_key`/`api_context_length`/`top_p`/`temperature`/`top_k` 为必填校验项，缺失返回参数错误；`top_p=1.0` 会被强制改为 0.99；
- `top_k` 上限 100；`kb_ids` 上限 20；
- `only_need_search_results`（仅返回检索结果）与 `streaming` 不能同时为 True（F-qa-038）；
- 若改用 `bot_id` 提问，则 LLM 参数整体来自 MySQL `llm_setting` JSON 配置，请求体中的同名参数不生效（F-qa-040）。

## 帧内容的消费建议

生成器各阶段帧的字段类型不同（改写问题、检索文档、rerank 结果、prompt、增量 token，F-qa-002），客户端应按帧内容分流处理：文档类帧用于展示"引用来源"面板，增量帧用于打字机渲染，直到 `[DONE]` 后读取汇总帧中的 `source_documents` 与 `time_record` 做溯源展示与耗时上报。问答日志已服务端落库（`add_qalog` 写 QALog 表，F-qa-039），客户端无需重复记录全量历史。

## 相关概念

- [02 LocalDocQA 问答编排链与硬编码阈值](/concepts/02-rag-pipeline.md)
- [06 API 层、Bot 配置与知识库运维](/concepts/06-api-ops.md)
- [01 部署与最小问答闭环](/concepts/01-quick-start.md)
- 示例：[最小问答闭环](/examples/minimal-qa-loop.md)
