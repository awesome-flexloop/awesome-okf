# 示例

BCEmbedding 实战演练，共 3 篇，覆盖向量化、RAG 检索-精排与重排序打分三条主线。

* [Embedding 文本向量化流程](embedding-text-vectorization.md) — 官方封装类与 sentence-transformers 两条向量化路径：模型加载、encode 调用、余弦相似度计算、指令前缀正确用法（应为空）。
* [LangChain 集成接入：检索-精排管线](langchain-rag-rerank.md) — HuggingFaceEmbeddings 向量检索 + BCERerank 上下文压缩，复现检索-精排两段式 RAG 管线，核对版本锁定与 top_n 约定。
* [Reranker 打分与重排序](reranker-scoring-and-sorting.md) — compute_score 与 rerank 两层接口：单 pair 标量返回、多 pair 列表返回、rerank 三键返回结构、长文本滑窗 max 合并效果。

```{toctree}
:hidden:
:maxdepth: 7

embedding-text-vectorization
langchain-rag-rerank
reranker-scoring-and-sorting
```
