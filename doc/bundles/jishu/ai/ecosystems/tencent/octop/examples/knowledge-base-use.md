---
type: Example
title: "知识库实战：建库、入库与检索调参"
description: "开启实例级知识库功能，创建私有/默认开启知识库，上传 22 类支持文档，用本地 ONNX embedding 建索引，并通过 search_knowledge 工具与引用标记完成检索问答。"
tags: [octop, knowledge, rag, onnx, embedding, citations]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: rag
    resource: /concepts/08-knowledge-rag.md
    title: 知识库与 RAG
  - id: agent
    resource: /concepts/02-agent-runtime.md
    title: Agent 运行时
---

# 知识库实战：建库、入库与检索调参

本示例演示在自托管 Octop 实例上开启知识库（RAG）能力、建库入库、调检索参数，并让 Agent 在对话中引用知识库回答。

## 场景说明

团队希望把产品手册（PDF/DOCX）、运维 FAQ（Markdown）和表格（XLSX）做成私有知识库，由本地 ONNX embedding 生成向量，Agent 对话时按需检索并在回复中附引用标记。

前置条件：管理员账号；以下端点挂在 `/api/knowledge-bases`（router 前缀 `/knowledge-bases`，挂载点 `/api`）。

## 1. 开启功能（实例级开关，默认关闭）

知识库是实例级可选功能：设置键 `knowledge_bases_enabled` 缺失或非 true 时一律视为关闭，此时建库/上传会报 `knowledge feature is disabled`（F-323、F-319）。开启前必须先选定 embedding 模型并满足依赖，否则报 `knowledge embedding prerequisites are not satisfied`。

先查能力状态：

```bash
curl http://127.0.0.1:8088/api/knowledge-bases/capability \
  -H "Authorization: Bearer <jwt-token>"
```

返回中的 `feature_enabled`、`backend`（onnx/remote）、`checks.model_downloaded`、`checks.deps_available` 用于判断缺口。

选本地 ONNX 后端时，安装附加依赖（pyproject 的 `local-embedding` extras）：

```bash
pip install "octop[local-embedding]"
# 等价依赖：fastembed>=0.4 与 huggingface_hub>=0.20
```

预置模型三选一（F-255），先下载再开启：

```bash
# 1) 触发下载（三个预置 id 逐字）
curl -X POST http://127.0.0.1:8088/api/knowledge-bases/onnx-download \
  -H "Authorization: Bearer <jwt-token>" -H "Content-Type: application/json" \
  -d '{"model": "BAAI/bge-small-zh-v1.5"}'
# 另两个：jinaai/jina-embeddings-v2-base-zh、intfloat/multilingual-e5-large

# 2) 轮询进度
curl http://127.0.0.1:8088/api/knowledge-bases/onnx-download-status \
  -H "Authorization: Bearer <jwt-token>"

# 3) 开启功能
curl -X PUT http://127.0.0.1:8088/api/knowledge-bases/feature \
  -H "Authorization: Bearer <jwt-token>" -H "Content-Type: application/json" \
  -d '{"enabled": true, "backend": "onnx", "model": "BAAI/bge-small-zh-v1.5"}'
```

未装 extras 时，下载器会尝试运行时 pip 安装，仅当环境变量 `OCTOP_ALLOW_RUNTIME_PIP` 为 `1/true/yes/on` 之一才放行（F-256）。也可用 `backend: "remote"` 指向已配置的 embedding 供应商。

## 2. 创建知识库

```bash
curl -X POST http://127.0.0.1:8088/api/knowledge-bases \
  -H "Authorization: Bearer <jwt-token>" -H "Content-Type: application/json" \
  -d '{
    "name": "产品手册库",
    "description": "手册、FAQ 与表格",
    "default_open": true,
    "max_documents": 200
  }'
```

字段与限额（F-319、F-323）：

- `default_open` 默认 `false`：true 表示该库对其 owner 的每轮对话默认注入；其他用户仍需在对话时显式勾选
- `max_documents`：单库文档上限，默认 **100**，可设 0（无限）至 10000；每个 owner 最多 **20** 个库
- `shared`：实例级共享可见性

## 3. 入库规则与上传

支持 **22** 个扩展名（F-319）：`.txt .md .markdown .rst .html .htm .json .jsonl .yaml .yml .csv .tsv .pdf .docx .pptx .xls .xlsx .xlsm .png .jpg .jpeg .webp`。图片类上传要求 OCR 已开启。

直接上传文件（multipart，表单字段 `upload` 与可选 `path`）：

```bash
curl -X POST "http://127.0.0.1:8088/api/knowledge-bases/<kb_id>/documents" \
  -H "Authorization: Bearer <jwt-token>" \
  -F "upload=@manual.pdf" -F "path=guides/manual.pdf"
```

也可直接建 Markdown/纯文本文档（无需上传）：

```bash
curl -X POST "http://127.0.0.1:8088/api/knowledge-bases/<kb_id>/documents/text" \
  -H "Authorization: Bearer <jwt-token>" -H "Content-Type: application/json" \
  -d '{"name": "faq", "format": "md", "content": "# FAQ\n..."}'
```

入库后文档进入异步索引队列：状态机 `processing → ready/failed`，索引并发度为 2（F-324）；只有 `ready` 的非目录文档参与检索（F-320）。向量以 float32 小端存于每个库独立的 `index.sqlite`，检索在 Python 侧算余弦相似度（F-317、F-318）。

## 4. 检索调参

实例级参数与默认值（F-316）：

| 设置键 | 默认 | 范围 |
|--------|------|------|
| `knowledge_chunk_size` | 800 | 100–8000 |
| `knowledge_chunk_overlap` | 120 | 0 且小于 chunk_size |
| `knowledge_retrieval_k` | 8 | 1–20 |
| `knowledge_context_char_budget` | 6000 | 500–50000 |

分块步长为 `size - overlap`（F-322）。改参数后对已有文档重建索引：

```bash
# 单文档
curl -X POST http://127.0.0.1:8088/api/knowledge-bases/<kb_id>/documents/<doc_id>/reindex \
  -H "Authorization: Bearer <jwt-token>"
# 整库
curl -X POST http://127.0.0.1:8088/api/knowledge-bases/<kb_id>/reindex \
  -H "Authorization: Bearer <jwt-token>"
```

## 5. 在 Agent 对话中检索

工具 `search_knowledge` 由系统按「本轮挂载的知识库」注入；无挂载时工具被移除或返回 `No knowledge bases selected for this turn.`（F-325、F-230）。参数为 `query`（聚焦的检索串）与 `k`（1–20，默认 8，F-325）：

```json
{
  "name": "search_knowledge",
  "arguments": {"query": "保修政策 退换货 时限", "k": 8}
}
```

跨库命中按 score 降序取前 k，并在结果文本尾部追加引用标记，标记前缀逐字为 `<!--octop-kb-citations:`，每条引用含 kb_id、kb_name、doc_id、filename、path 五键（F-326）。最终回复呈形如：

```text
……正文……

<!--octop-kb-citations:[{"kb_id":"...","kb_name":"产品手册库","doc_id":"...","filename":"manual.pdf","path":"guides/manual.pdf"}]-->
```

## 排错

| 现象 | 原因与处理 |
|------|-----------|
| 建库报 feature disabled | 未执行 `PUT /feature` 开启；该开关实例级默认关闭 |
| 开启报 prerequisites not satisfied | ONNX 模型未下载完成或未装 `local-embedding` extras；用 `/capability` 看四项 checks，或设置 `OCTOP_ALLOW_RUNTIME_PIP=1` 允许运行时装依赖 |
| 文档卡 processing / 重启后未继续 | 索引是异步 job（并发 2）；服务启动会 `resume_pending` 恢复挂起任务，仍失败可调单文档 `/reindex` |
| 中文 TXT 乱码 | 纯文本编码依次尝试 utf-8-sig、gb18030，最终以 utf-8 `errors="replace"` 兜底（F-322）；源文件建议另存 UTF-8 |
| 图片/扫描 PDF 无文本 | 需开启 OCR：extras 为 `knowledge-ocr`（rapidocr>=3.4,<4、onnxruntime>=1.17、pymupdf>=1.24），图片后缀限 png/jpg/jpeg/webp（F-328）；PDF 抽出空文本时也会回退 OCR |
| Agent 不调用检索 | 本轮没有挂载知识库（勾选库或把库 `default_open` 置 true）；主持人（team）不挂知识库工具 |
| read_file 读不了入库的二进制 | 14 类二进制后缀（pdf/office/zip/图片等）被 read_file 护栏拦截，17 类文本后缀才直读——入库文档请用 preview 接口看抽取文本（F-228） |

## 相关概念

- [/concepts/08-knowledge-rag.md](../concepts/08-knowledge-rag.md)
- [/concepts/02-agent-runtime.md](../concepts/02-agent-runtime.md)
