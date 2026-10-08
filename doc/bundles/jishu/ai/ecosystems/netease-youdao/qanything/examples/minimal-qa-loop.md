---
type: example
title: 最小问答闭环——建库、传文件、提问
description: 以仓库自带测试脚本为线索，走通"新建知识库 → 上传文件 → 等待入库 → 非流式问答"的最小闭环，并说明每步背后的接口与状态机语义。
tags: [qanything, example, api, quick-start]
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

# 最小问答闭环——建库、传文件、提问

本例演示 QAnything 的最小使用闭环：新建知识库 → 上传文件 → 等待入库 → 提问。全部请求均指向主服务 `http://localhost:8777`（Sanic 应用，默认端口 8777，F-qa-034），示例代码忠实于仓库 `scripts/` 目录下的真实测试脚本。

## 前置条件

按 [/concepts/01-quick-start.md](/concepts/01-quick-start.md) 完成部署，确认 `entrypoint.sh` 拉起的 6 个进程全部就绪（日志中出现 `"Starting worker"`，180 秒超时即失败，F-qa-045）。接口路径与 `docs/API.md` 一一对应（F-qa-043）。

## 第一步：新建知识库

`POST /api/local_doc_qa/new_knowledge_base` 只需 `user_id` 与 `kb_name`（F-qa-036）。仓库脚本 `scripts/new_knowledge_base.py` 是可直接运行的最小示例：

```python
import requests
import json

url = "http://0.0.0.0:8777/api/local_doc_qa/new_knowledge_base"
headers = {"Content-Type": "application/json"}
data = {"user_id": "zzp", "kb_name": "kb_test"}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.text)
```

服务端生成形如 `'KB' + uuid.uuid4().hex` 的 kb_id（F-qa-036）。注意 `user_id` 须以字母开头且只含字母数字下划线，数据层实际以 `user_id + '__' + user_info`（user_info 缺省 `"1234"`）为隔离键（F-qa-041）；`user_id="zzp"` 的数据与前端页面互通（F-qa-043）。

## 第二步：上传文件

`POST /api/local_doc_qa/upload_files` 为 multipart 表单，字段含 `user_id`、`kb_id` 与文件列表 `files`（F-qa-037）。`scripts/upload_files.py` 的单文件上传写法（`sys.argv[1]`=kb_id，`sys.argv[2]`=文件路径）：

```python
import requests
import sys

kb_id = sys.argv[1]
url = "http://0.0.0.0:8777/api/local_doc_qa/upload_files"
data = {"user_id": "zzp", "kb_id": kb_id}

files = [("files", open(sys.argv[2], "rb"))]
response = requests.post(url, files=files, data=data)
print(response.text)
```

运行：`python scripts/upload_files.py KBxxxxxxxx your_doc.pdf`。

上传是**登记而非入库完成**：服务端以 `LocalFile(user_id, kb_id, file, file_name)` 生成 file_id（`uuid.uuid4().hex`），文件写入 `UPLOAD_ROOT_PATH/user_id/kb_id/file_id/` 目录，并在 MySQL File 表登记 status='gray'，随后由 insert_files_server 异步处理（F-qa-026、F-qa-032）。单库文件总数上限 10000（F-qa-037）。

## 第三步：等待入库（状态机）

入库状态沿 gray（排队）→ yellow（入库中）→ green（成功）/ red（失败）迁移（F-qa-042）。用 `list_files` 路由轮询，直至目标文件为 green 再提问；若 `content_length > 1000000` 或内容为空会被判 red（F-qa-033）。只有 green 文件参与检索，若知识库无任何 green 文件，`local_doc_chat` 会置空 kb_ids 退化为纯对话模式（F-qa-042）。

## 第四步：提问

`scripts/local_chat_qa.py` 演示非流式单轮问答（`sys.argv[1]` 为问题），请求体忠实还原如下（F-qa-048）：

```python
import requests, time

def send_request(ques):
    url = 'http://localhost:8777/api/local_doc_qa/local_doc_chat'
    headers = {'content-type': 'application/json'}
    data = {
        "user_id": "liujx_265",
        "kb_ids": ["KBf652e9e379c546f1894597dcabdc8e47"],
        "question": ques,
        "rerank": False,
        "history": []
    }
    start = time.time()
    response = requests.post(url=url, headers=headers, json=data, timeout=60)
    res = response.json()
    print(res['response'])

send_request("这份文档的主要结论是什么？")
```

要点（F-qa-038、F-qa-039）：

- `kb_ids` 一次最多 20 个；生产调用通常显式传 `api_base`/`api_key`/`api_context_length`/`top_p`/`temperature`/`top_k`（≤ 100）/`model`（默认 `gpt-4o-mini`），本脚本省略即走服务默认或环境配置；
- `api_base` 中的 `0.0.0.0`/`127.0.0.1`/`localhost` 会被替换为 `GATEWAY_IP`（F-qa-038）；
- 非流式返回单条 JSON，`response` 为答案，`source_documents`/`retrieval_documents`/`time_record` 供溯源与耗时分析；问答结果经 `add_qalog` 落 MySQL QALog 表（F-qa-039）。

## 验证清单

1. 建库返回 kb_id 以 `KB` 开头（F-qa-036）；
2. 提问前 `list_files` 确认文件为 green（F-qa-042）；
3. 答案附带 `source_documents` 引用片段，说明走的是知识库问答而非纯对话回退（F-qa-039、F-qa-042）。

## 相关概念

- [01 部署与最小问答闭环](/concepts/01-quick-start.md)
- [06 API 层、Bot 配置与知识库运维](/concepts/06-api-ops.md)
- [05 依赖服务化：五个本地推理/解析进程](/concepts/05-dependent-servers.md)
- 示例：[知识库上传与检索流程](/examples/kb-upload-and-retrieval.md)、[API 流式问答调用](/examples/api-streaming-chat.md)
