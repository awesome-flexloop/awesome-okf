---
type: Concept
title: Zvec Embedding 与 Reranker 函数体系
description: 7 种开箱即用 Embedding 函数与 4 种 Reranker、协议基类与框架基类的自定义扩展路径
tags: [zvec, embedding, reranker, splade, bm25, rrf, cross-encoder]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-source
    resource: /references/source-code.md
    title: alibaba/zvec 源码信源
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# Zvec Embedding 与 Reranker 函数体系

Zvec 的 Python SDK 内置完整的 Embedding 与 Reranker 函数系统（`python/zvec/extension/`，16 个模块文件）：开箱即用的本地/API 实现覆盖主流路径，协议基类支持自定义扩展。当前仅支持**文本模态** Embedding。

## Embedding 函数（7 种）

| 类型 | 实现 | 模型与说明 |
|---|---|---|
| 本地稠密 | `DefaultLocalDenseEmbedding` | Sentence Transformers `all-MiniLM-L6-v2`（384 维，~80MB）；中文可切 ModelScope `iic/nlp_gte_sentence-embedding_chinese-small` |
| 本地稀疏 | `DefaultLocalSparseEmbedding` | SPLADE `naver/splade-cocondenser-ensembledistil`（~100MB），`encoding_type="query"/"document"` |
| BM25 | `BM25EmbeddingFunction` | DashText SDK 本地 BM25 编码，无需 API 密钥；内置中文/英文编码器或自定义语料训练（`b`/`k1` 参数） |
| Qwen 稠密 | `QwenDenseEmbedding` | Dashscope API（`text-embedding-v4`），维度必填 |
| Qwen 稀疏 | `QwenSparseEmbedding` | Dashscope API |
| OpenAI 稠密 | `OpenAIDenseEmbedding` | OpenAI API（`text-embedding-4`），维度必填 |
| Jina 稠密 | `JinaDenseEmbedding` | Jina v5 系列（`v5-text-small` 677M/1024 维、`v5-text-nano` 239M/768 维）；支持任务特定任务类型与 Matryoshka 降维（32–1024）。经 `from zvec.extension import JinaDenseEmbedding` 导入（仅 extension 子包导出，未入顶层 `zvec` 命名空间） |

```python
from zvec.extension import DefaultLocalDenseEmbedding, BM25EmbeddingFunction

emb = DefaultLocalDenseEmbedding()                    # 国际默认
emb_cn = DefaultLocalDenseEmbedding(model_source="modelscope")  # 中国大陆推荐 ModelScope
vec = emb.embed("Hello, world!")                      # 384 维

bm25 = BM25EmbeddingFunction(language="zh", encoding_type="query")
sparse = bm25.embed("深度学习神经网络")                # {维度索引: 权重}
```

Jina 任务类型：`retrieval.query` / `retrieval.passage` / `text-matching` / `classification` / `separation`。大陆用户可设 `HF_ENDPOINT=https://hf-mirror.com` 稳定下载。

## Reranker（4 种）

| 类型 | 实现 | 说明 |
|---|---|---|
| 本地重排 | `DefaultLocalReRanker` | Cross-Encoder `cross-encoder/ms-marco-MiniLM-L6-v2`（~80MB），单路结果精排 |
| Qwen 重排 | `QwenReRanker` | Dashscope API（`gte-rerank-v2`） |
| RRF 融合 | `RrfReRanker` | 倒数排名融合，仅用排名位置无需评分（`rank_constant=60`） |
| 加权融合 | `WeightedReRanker` | 加权融合多路有评分结果（`weights=[0.7, 0.3]`） |

`DefaultLocalReRanker` 与 `QwenReRanker` 面向单路结果的语义精排（构造时传 `query` 与 `rerank_field`）；`RrfReRanker`/`WeightedReRanker` 专为多向量融合设计（见[混合检索](06-hybrid-retrieval.md)）。

## 自定义扩展

两级扩展点：

- **协议基类**：`DenseEmbeddingFunction[T]` / `SparseEmbeddingFunction[T]`——实现 `embed(input) -> 向量`、`dimension`、`extra_params` 与 `__call__` 即可从零自定义。
- **框架基类**：`SentenceTransformerFunctionBase`（换任意 ST 模型）、`QwenFunctionBase`（Dashscope 定制）、`OpenAIFunctionBase`——复用基类的模型加载/API 调用，仅覆写 encode 逻辑。

Reranker 自定义：继承 `ReRanker`（`RerankFunction` 的导出名），实现 `topn` 属性与 `rerank(documents, rerank_field, ...)`。

```python
from zvec.extension import DenseEmbeddingFunction
from zvec.common.constants import TEXT, DenseVectorType

class MyDenseEmbedding(DenseEmbeddingFunction[TEXT]):
    @property
    def dimension(self) -> int: ...
    def embed(self, input: str) -> DenseVectorType: ...
    def __call__(self, input: str) -> DenseVectorType:
        return self.embed(input)
```

## 工程注意事项

模型首次使用自动下载（需网络）；本地模型耗内存，用后调 `clear_cache()` 释放；API 函数注意配额与速率限制；Embedding 与 Reranker 函数线程安全，可在多线程环境使用。

## 相关概念

- [混合检索](06-hybrid-retrieval.md)：融合 Reranker 的使用场景
- [总览](00-overview.md)：产品矩阵
- [混合检索实战](/examples/01-hybrid-search.md)
