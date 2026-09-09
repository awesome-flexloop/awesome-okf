---
type: example
title: "LangChain 集成接入：检索-精排管线"
description: "基于 README 官方 demo 的 LangChain 接入演练：HuggingFaceEmbeddings 向量检索 + BCERerank 上下文压缩，复现检索-精排两段式 RAG 管线，并核对版本锁定与 top_n 约定。"
tags: [bcembedding, langchain, example, rag, rerank, faiss]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-md", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: BCEmbedding 源码事实清单（F-bc 系列）
  - id: concepts
    resource: /concepts/04-framework-integrations.md
    title: LangChain 与 LlamaIndex 集成：两个 BCERerank
---

# LangChain 集成接入：检索-精排管线

本演练复现 README 官方 LangChain demo（F-bc-031、F-bc-038），构建"embedding 初筛 → BCERerank 精排"的两段式 RAG 检索管线。代码骨架忠实于 README Integrations 小节的 Demo 与 `BCEmbedding/tools/langchain/bce_rerank.py` 源码。

## 版本锁定

README 集成示例锁定以下历史版本（F-bc-031）：

```bash
pip install BCEmbedding==0.1.5
pip install langchain==0.1.0
pip install langchain-community==0.0.9
pip install langchain-core==0.1.7
pip install langsmith==0.0.77
```

> 这些是 2024 年初的版本。当前较新的 LangChain 版本 API 已变动（如 `langchain.embeddings` 的导入路径），直接照搬需先验证兼容性；`BCERerank` 源码依赖 `langchain_core.pydantic_v1` 兼容层（F-bc-038），该层在新版 langchain-core 中已移除或迁移。

## 准备语料

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

documents = PyPDFLoader("eval_pdfs/Comp_en_llama2.pdf").load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
texts = text_splitter.split_documents(documents)
```

## 初始化向量模型与精排器

```python
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import DistanceStrategy
from BCEmbedding.tools.langchain import BCERerank

# init embedding model：走 sentence-transformers 加载 BCE 权重
embedding_model_name = 'maidalun1020/bce-embedding-base_v1'
embedding_model_kwargs = {'device': 'cuda:0'}
embedding_encode_kwargs = {'batch_size': 32, 'normalize_embeddings': True, 'show_progress_bar': False}

embed_model = HuggingFaceEmbeddings(
    model_name=embedding_model_name,
    model_kwargs=embedding_model_kwargs,
    encode_kwargs=embedding_encode_kwargs
)

# init reranker：显式指定 top_n，避免依赖默认值
reranker_args = {'model': 'maidalun1020/bce-reranker-base_v1', 'top_n': 5, 'device': 'cuda:1'}
reranker = BCERerank(**reranker_args)
```

两点说明：

- `normalize_embeddings=True` 对应 `EmbeddingModel.encode` 默认的 `normalize_to_unit=True`（F-bc-011），配合 `MAX_INNER_PRODUCT` 距离策略（内积即余弦相似度）；
- `top_n=5` 为**显式指定**。LangChain 版 `BCERerank` 的默认值为 **3**，而 LlamaIndex 版默认为 **5**（F-bc-038、F-bc-039）——不显式传参时，同一 RAG 应用跨框架迁移会发生召回粒度的静默变化（I 阶段洞察 4）。

## 组装检索-精排管线

```python
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever

# example 1. retrieval with embedding and reranker
retriever = FAISS.from_documents(
    texts, embed_model,
    distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
).as_retriever(search_type="similarity", search_kwargs={"score_threshold": 0.3, "k": 10})

compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker, base_retriever=retriever
)

response = compression_retriever.get_relevant_documents("What is Llama 2?")
```

管线数据流：

```
query ──> FAISS 向量检索（k=10，score_threshold=0.3 初筛）
      ──> BCERerank.compress_documents
            ├─ 过滤空 page_content 文档
            ├─ RerankerModel.rerank(query, passages)（内含长文本滑窗，F-bc-019）
            ├─ 分数写入 doc.metadata["relevance_score"]（F-bc-038）
            └─ 截取前 top_n=5 个
```

返回的 `response` 是按相关性降序排列的 `Document` 列表，每个文档的 `metadata["relevance_score"]` 即 sigmoid 相关性分数（F-bc-038）。

## 验证要点

1. **分数写回位置**：精排后从 `doc.metadata["relevance_score"]` 取分，而不是 `doc.score`（后者是 LlamaIndex 版的写回位置，F-bc-039）。
2. **无效文档置 0**：`page_content` 为空的文档不参与 rerank，但会被附加到结果末尾且 `relevance_score=0`（F-bc-038），截断后通常不可见；若 top_n 大于有效文档数，注意结果尾部可能出现零分文档。
3. **换行处理**：`BCERerank` 内部将 `page_content` 的换行替换为空格后再送入 rerank（F-bc-038），直接调用 `RerankerModel.rerank` 时没有此处理，两边分数可能因此有微小差异。
4. **设备分配**：demo 中 embedding 用 `cuda:0`、reranker 用 `cuda:1`，两模型可分居不同卡；`BCERerank` 的 `device` 参数直接透传给 `RerankerModel`（F-bc-038）。

## 常见错误

| 现象 | 原因 | 对策 |
|---|---|---|
| `ImportError: Cannot import 'BCEmbedding' package` | 未安装或版本过旧 | 按报错提示 `pip install BCEmbedding>=0.1.2`（F-bc-040） |
| 精排后文档数与预期不符 | 依赖默认 `top_n=3` | 显式传 `top_n` 并按需核对（F-bc-038） |
| pydantic v1 导入失败 | langchain-core 版本过新 | 回退 README 锁定版本或等待封装适配（F-bc-031） |

## 相关概念

- [/concepts/04-framework-integrations.md](../concepts/04-framework-integrations.md) — 两个 BCERerank 的差异对照
- [/concepts/02-reranker-model.md](../concepts/02-reranker-model.md) — rerank 接口与滑窗机制
- [/examples/reranker-scoring-and-sorting.md](../examples/reranker-scoring-and-sorting.md) — 不依赖框架的精排用法
