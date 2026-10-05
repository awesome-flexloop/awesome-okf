---
type: Concept
title: "知识库 RAG：每库一个 SQLite 与零向量库检索"
description: "Octop 知识库的物理布局、chunks 表结构、float32 全表内存余弦检索、规模硬上限、22 种扩展名解析、search_knowledge 引用契约、Hint 中间件与索引任务。"
tags: [octop, knowledge, rag, sqlite, embeddings, ocr]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: "Octop 源码事实清单 F-316~F-328（并参 F-230）"
---

# 知识库 RAG：每库一个 SQLite 与零向量库检索

Octop 的知识库（RAG）设计刻意"反潮流"：**没有独立向量数据库进程**，每个知识库在文件系统上就是一个目录，向量与原文同库存放在一个 SQLite 侧车文件里，检索时全表读出、在 Python 进程内算余弦相似度。本章拆解这套布局及其规模取舍。

## 物理布局：一库一目录一 SQLite

```
knowledge_dir/
└── {kb_id}/
    ├── index.sqlite                 # 向量索引（chunks 表）
    └── docs/
        └── {doc_id}{suffix}         # 原始文档落盘
```

索引路径逐字为 `PathLayout.from_env().knowledge_dir / kb_id / "index.sqlite"`（F-317），原始文档落盘在 `knowledge_dir/{kb_id}/docs/{doc_id}{suffix}`（F-323）。知识库整体由设置开关门控：`knowledge_bases_enabled` 加上 embedding 三键（backend/model/provider_id），不满足时报错字面 "knowledge feature is disabled" 或 "knowledge embedding prerequisites are not satisfied"（F-323）。

## chunks 表：6 列装下全部索引状态

index.sqlite 初始化时只建一张表加一条索引（F-317）：

```sql
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id  TEXT PRIMARY KEY,       -- 形如 f"{doc_id}:{ordinal}"
    doc_id    TEXT NOT NULL,
    ordinal   INTEGER NOT NULL,
    text      TEXT NOT NULL,
    embedding BLOB NOT NULL,          -- float32 小端打包
    meta_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);
```

写入时一条文档的全部 chunk 在单事务内"先删后插"原子替换（`replace_doc_chunks`），向量用 `struct.pack(f"<{n}f", *vector)` 序列化为 float32 小端字节串（F-318）。命中结果是含 6 个字段的 frozen dataclass `Hit`（chunk_id/doc_id/ordinal/text/score/metadata）（F-318）。

## 检索：全表扫描 + 内存余弦

`KnowledgeIndex.search` 的做法异常直白（F-318）：

```python
rows = conn.execute(
    "SELECT chunk_id, doc_id, ordinal, text, embedding, meta_json FROM chunks"
).fetchall()
# 对每行 struct.unpack 成 float 序列，跳过维度不一致者，
# 进程内计算 query 与 embedding 的余弦，按 score 降序取前 k
```

- 查询向量为零向量直接抛错；命中向量范数为 0 时相似度记 0.0（F-318）。
- 没有 ANN 索引、没有 IVFFlat、没有额外服务——正确性优先，规模靠下面的硬上限兜底。
- 跨库检索只纳入 `status=="ready"` 且非目录的文档，多库结果合并后按 score 降序取前 k，并给输出追加 citation marker（F-320）。

## 规模硬上限与设计取舍

| 限制 | 字面量 | 出处 |
|------|--------|------|
| 每库文档数 | `MAX_DOCS_PER_KB = 100` | F-319 |
| 每拥有者知识库数 | `MAX_BASES_PER_OWNER = 20` | F-319 |
| 单库 max_documents 允许配置上限 | `MAX_KB_MAX_DOCUMENTS = 10_000`（创建时范围 0–10000） | F-319 |
| 默认 top-k | `DEFAULT_RETRIEVAL_K = 8`，工具参数允许 1–20 | F-316、F-325 |
| 索引并发 | `INDEX_CONCURRENCY = 2`（asyncio.Semaphore） | F-324 |
| embedding 批大小 | `_KNOWLEDGE_EMBEDDING_BATCH_LIMIT = 20` | F-321 |
| 预览字符上限 | `_MAX_PREVIEW_CHARS = 200_000` | F-319 |

这组数字解释了"零向量库"为何可行：每库百级文档、chunk 800 字符量级，全表余弦在单进程内仍是毫秒~十毫秒级；代价是单库不适合塞进十万级文档——后者已超出产品定位（自托管、单 wheel、无外部队列/Redis，见 [00-architecture.md](00-architecture.md)）。

可调参数同样有严格区间（F-316）：

| 设置键 | 默认 | 允许范围 |
|--------|------|----------|
| knowledge_chunk_size | 800 | 100–8000 |
| knowledge_chunk_overlap | 120 | 0 ≤ overlap < size |
| knowledge_retrieval_k | 8 | 1–20 |
| knowledge_context_char_budget | 6000 | 500–50000 |

## 文档解析：22 种扩展名与编码回退

知识库接受 22 个扩展名（F-319）：`.txt .md .markdown .rst .html .htm .json .jsonl .yaml .yml .csv .tsv .pdf .docx .pptx .xls .xlsx .xlsm .png .jpg .jpeg .webp`。

- 纯文本后缀 7 个；文本编码尝试顺序为 `("utf-8-sig", "gb18030")`，最终再以 utf-8 `errors="replace"` 兜底——对中文老文件友好（F-322）。
| 二进制类型 | 解析路径 |
|------------|----------|
| PDF | pypdf；抽不出文本则回退 OCR（F-322） |
| docx | python-docx，含 altChunk / mc:Fallback 分支（F-322） |
| pptx | python-pptx（F-322） |
| xlsx | openpyxl；xls 走 xlrd（F-322） |
| png/jpg/jpeg/webp | 必须开启 OCR 才允许上传（F-319） |

切窗签名为 `chunk_text(text, *, size=800, overlap=120)`，步进 = size − overlap（F-322、F-316）。

OCR 是独立可选项（F-328）：后端同样只有 onnx/remote 两种；本地额外包固定为 `rapidocr>=3.4,<4`、`onnxruntime>=1.17`、`pymupdf>=1.24`（纯 PDF 只需要 pymupdf），PDF 以 `Matrix(2,2)` 渲染，拒答提示最长 400 字符。embedding 后端默认 onnx，remote 形态向 `{base}/embeddings` 发 POST、timeout 60（F-321）。路径安全由 `normalize_kb_path` 兜底：禁 `..`、归一前导斜杠/反斜杠（F-328）。

## 索引任务：processing → ready/failed

文档入库后由 jobs 模块异步索引：状态机为 processing→ready/failed，支持 reindex_all 全量重建与 resume_pending 断点续跑，全库索引并发信号量为 2（F-324）。知识库创建时可带实例级 `default_open`（service.py 的 create_base 形参默认 False），语义是"拥有者的每轮对话默认注入此库"（F-319、default_open.py）。

## search_knowledge 工具与引用契约

Agent 侧只看到一个工具（F-325）：

```python
SEARCH_KNOWLEDGE_TOOL = "search_knowledge"
# k: int = Field(ge=1, le=20, default=8)
# configurable 取键：user、user_is_admin、knowledge_base_ids、locale
```

没有任何知识库被选入本轮时，工具直接返回字面串 `"No knowledge bases selected for this turn."`（F-325）。默认开放库的合并规则（F-327）：显式选择非 None 时完全采用显式列表；否则只注入**拥有者本人**的 default_open 库再加额外授权 id——别人的默认开放库不会泄漏到你的会话。

检索结果不只要"塞进上下文"，还承担溯源责任，契约是一个 HTML 注释标记（F-326）：

```python
CITATIONS_MARKER_PREFIX = "<!--octop-kb-citations:"
# 追加格式：f"{body}\n\n{prefix}{json}-->"
# KnowledgeCitation 含 5 键：kb_id、kb_name、doc_id、filename、path
```

这样前端/下游可以从回答正文末尾机械地解析出引用清单，而不必让模型自己编造出处。

## KnowledgeSearchHint 中间件：动态改写工具描述

知识库目录不是静态提示词：`KnowledgeSearchHintMiddleware`（定义于 `src/octop/infra/knowledge/hint.py:93`，在 Agent 中间件链中位于第 3 位）在模型调用前工作（F-230、F-327）：

1. 从 `configurable["knowledge_base_catalog"]` 读本轮可见的知识库目录；
2. 目录为空——直接从 request.tools 中**移除** search_knowledge，模型根本看不到这个工具；
3. 目录非空——`model_copy` 改写工具 description，把库名/用途写进去，引导模型按库检索。

每轮的四键 `knowledge_base_ids、knowledge_base_catalog、user_is_admin、locale` 由 `stamp_turn_knowledge_config` 盖到 configurable 上（F-327）。这与推理覆盖中间件写 `octop_reasoning_overrides`（F-226）属于同一类"请求期注入"手法。

## 相关概念

- [/concepts/10-agent-teams.md](10-agent-teams.md) —— Hint 中间件所在的 8 环中间件链
- [/concepts/07-connector-system.md](07-connector-system.md) —— 外部知识源（weknora/notion 等）走连接器而非本地库
- [/concepts/00-architecture.md](00-architecture.md) —— 单进程模型与规模取舍的总背景
