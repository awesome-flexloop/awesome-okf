---
type: concept
title: "LangChain 与 LlamaIndex 集成：两个 BCERerank"
description: "tools/langchain 与 tools/llama_index 下两个同名 BCERerank 封装的接口约定、top_n 默认值差异（3 vs 5）、延迟导入模式、分数写回约定与版本锁定。"
tags: [bcembedding, langchain, llama-index, integration, rerank, bc-erank]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-md", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: BCEmbedding 源码事实清单（F-bc 系列）
  - id: insights
    resource: /references/insights.md
    title: BCEmbedding 架构洞察与知识地图
---

# LangChain 与 LlamaIndex 集成：两个 BCERerank

`BCEmbedding/tools/` 下按框架分目录提供 Reranker 集成封装：`tools/langchain/bce_rerank.py` 与 `tools/llama_index/bce_rerank.py` 各定义一个同名 `BCERerank` 类。两者类名、内部延迟导入与实例化方式几乎一致，但在默认 `top_n`、基类与分数写回约定上存在框架投射的差异（I 阶段洞察 4）。

## 共同模式：延迟导入

两个 `BCERerank` 均在 `__init__` 内延迟导入 `BCEmbedding.models.RerankerModel` 并实例化为 `_model` 私有属性；导入失败时报错信息要求 `pip install BCEmbedding>=0.1.2`（F-bc-040）。延迟导入的动机是避免在未安装 BCEmbedding 的环境中 import 框架封装模块即失败；版本提示 `>=0.1.2` 也暴露出集成代码曾独立于主包演进（当前主包版本为 0.1.5，F-bc-001）。

## LangChain 版：`BaseDocumentCompressor`

```python
class BCERerank(BaseDocumentCompressor):
    client: str = 'BCEmbedding'
    top_n: int = 3
    model: str = "maidalun1020/bce-reranker-base_v1"
```

- 构造签名：`__init__(top_n=3, model="maidalun1020/bce-reranker-base_v1", device=None, **kwargs)`，`**kwargs` 透传给 `RerankerModel`（F-bc-038）；
- 核心方法 `compress_documents(documents, query, callbacks=None)`：过滤无效文档（空 `page_content`）后调用 `self._model.rerank(query, passages)`，将分数写入 `doc.metadata["relevance_score"]`，无效文档置 0，最终截取前 `top_n` 个（F-bc-038）；
- 分数写回位置：`Document.metadata["relevance_score"]`。

## LlamaIndex 版：`BaseNodePostprocessor`

```python
class BCERerank(BaseNodePostprocessor):
    def __init__(top_n=5, model="maidalun1020/bce-reranker-base_v1", device=None, **kwargs)
```

- 默认 `top_n=5`（F-bc-039）；
- 核心方法 `_postprocess_nodes(nodes, query_bundle=None)`：`query_bundle is None` 时抛 `ValueError("Missing query bundle in extra info.")`（F-bc-039）；
- 分数写回 `node.score`，截取前 `top_n` 个；过程中包装 `CBEventType.RERANKING` 回调事件。

## 关键差异对照

| 维度 | LangChain 版 | LlamaIndex 版 |
|---|---|---|
| 基类 | `BaseDocumentCompressor` | `BaseNodePostprocessor` |
| 默认 `top_n` | **3** | **5** |
| 分数写回 | `doc.metadata["relevance_score"]` | `node.score` |
| 空输入行为 | 空文档列表直接返回 `[]` | 空节点列表直接返回 `[]` |
| 模型实例 | `_model`（pydantic `PrivateAttr`） | `_model`（pydantic `PrivateAttr`） |

**默认 top_n 不一致（3 vs 5）是最具实际影响的差异**：集成层的差异不是模型行为差异，而是框架惯例投射到默认参数上的结果，却足以造成同一 RAG 应用跨框架迁移时召回粒度的静默变化——默认构造不显式传参时用户完全无感知（I 阶段洞察 4）。跨框架迁移或复现 RAG 教程时，应显式指定 `top_n` 并核对框架版本。

## 版本锁定

README 集成示例的版本要求（F-bc-031）：LangChain 为 `langchain==0.1.0`、`langchain-community==0.0.9`、`langchain-core==0.1.7`、`langsmith==0.0.77`；LlamaIndex 为 `llama-index==0.9.42.post2`。这些是 2024 年初的历史版本，当前（较新）框架版本的 API 兼容性需另行验证——例如 LangChain 版源码 `from langchain_core.pydantic_v1 import Extra, root_validator` 依赖 langchain-core 仍提供 pydantic v1 兼容层的版本。

## 注意事项

- 两个封装只消费 `rerank` 的三个返回键中的 `rerank_scores` 与 `rerank_ids`（F-bc-038、F-bc-039）；`rerank` 空输入返回缺 `rerank_ids` 键（F-bc-018），而两个封装在调用前已过滤空文档，恰好绕开了该边角。
- LangChain 版将文档内容中的换行替换为空格（`passage.replace('\n', ' ')`）后再送入 rerank，直接调用 `RerankerModel.rerank` 时无此处理。
- 分数写回后文档/节点的原始顺序保持 rerank 降序，下游按返回序列截断即可，不要再按旧排序假设。

## 相关概念

- [/concepts/02-reranker-model.md](/concepts/02-reranker-model.md) — rerank 接口语义与长文本机制
- [/concepts/00-quickstart.md](/concepts/00-quickstart.md) — 安装与依赖约束
- [/examples/langchain-rag-rerank.md](/examples/langchain-rag-rerank.md) — LangChain 集成演练
