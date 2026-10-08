---
type: example
title: "Reranker 打分与重排序"
description: "基于 RerankerModel 的 compute_score 与 rerank 完成查询-篇章相关性打分与排序：单 pair 标量返回、多 pair 列表返回、rerank 三键返回结构，以及长文本滑窗的 max 合并效果。"
tags: [bcembedding, reranker, example, rerank, compute-score, sliding-window]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-md", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: BCEmbedding 源码事实清单（F-bc 系列）
  - id: concepts
    resource: /concepts/02-reranker-model.md
    title: RerankerModel 与长文本滑窗策略
---

# Reranker 打分与重排序

本演练覆盖 `RerankerModel` 的两个层次：`compute_score`（底层打分）与 `rerank`（高层排序，内含长文本滑窗）。接口行为均忠实于 `BCEmbedding/models/reranker.py`（F-bc-013~020）。

## 前置条件

```bash
pip install BCEmbedding==0.1.5
```

## 场景：初筛后的精排

假设 embedding 召回 10 个候选篇章，用 reranker 精排取前 3。

```python
from BCEmbedding import RerankerModel

# init reranker model（默认加载 bce-reranker-base_v1）
model = RerankerModel(model_name_or_path="maidalun1020/bce-reranker-base_v1")

query = "BCEmbedding 支持长文本重排序吗？"
passages = [
    "RerankerModel 通过应用层滑窗切分支持长 passage 重排序……",
    "今天天气晴朗，适合外出。",
    # ... 更多候选篇章
]
```

## 方法一：`compute_score` 打分

```python
# construct sentence pairs
sentence_pairs = [[query, passage] for passage in passages]

scores = model.compute_score(sentence_pairs)
# scores 为 Python float 列表（sigmoid 后，落在 (0, 1) 区间，F-bc-016）
```

**返回值类型随输入数量变化**（F-bc-016）：

```python
single = model.compute_score([query, passages[0]])
# 仅一个 pair 时返回标量 float，不是列表！

if isinstance(single, float):
    print(f"相关性分数：{single:.4f}")
```

单 pair 的便捷写法 `[query, passage]`（list 首元素为 str）会被自动包装为二元组列表（F-bc-016），无需手工构造。

## 方法二：`rerank` 直接排序

```python
rerank_results = model.rerank(query, passages)

# 三键返回结构（F-bc-017）：
rerank_results['rerank_passages']  # 按分数降序的篇章列表
rerank_results['rerank_scores']    # 与篇章一一对应的分数
rerank_results['rerank_ids']       # 降序排列对应的【原文索引】

top3 = rerank_results['rerank_passages'][:3]
```

注意 `rerank_ids` 是**原文索引**（`np.argsort(merge_scores)[::-1].tolist()`，F-bc-017），用于回查原始列表中的其他字段（如文档 ID、来源元数据）。

## 长文本行为观察

`rerank` 内部先对每条 passage 做 `p[:128000]` **字符级**截断（F-bc-018），再按 `max_length - query长度 - 2` 滑窗切 chunk、逐 chunk 推理、同一 passage 取 **max** 合并（F-bc-019、F-bc-023）。可构造一个"只有中段相关"的长篇章验证该行为：

```python
long_passage = "无关内容……" * 200 + "BCEmbedding 的 RerankerModel 支持超过 512 token 的长 passage 重排序。" + "……无关内容" * 200

res = model.rerank(query, [long_passage])
print(res['rerank_scores'][0])   # 高分来自最相关的那个 chunk 的 max 合并
```

调节滑窗参数（构造时传入，F-bc-015）：

```python
model = RerankerModel(
    model_name_or_path="maidalun1020/bce-reranker-base_v1",
    max_length=512,      # 滑窗窗口的基准长度
    overlap_tokens=80,   # 相邻 chunk 重叠量（实际取 min(80, 可用窗口//4)，F-bc-023）
)
```

## 边界情况处理

```python
# 空 query 或空 passages：返回结构【缺少 rerank_ids 键】（F-bc-018）
res = model.rerank("", passages)
assert res == {'rerank_passages': [], 'rerank_scores': []}

# query 过长：max_length=512 时约 400 token 上限，超出直接断言失败（F-bc-022）
# AssertionError: Your query is too long! Please make sure your query less than 400 tokens!
```

下游解包 `rerank` 返回值时，应先判断 `rerank_ids` 是否存在，再按三键解包。

## 相关概念

- [/concepts/02-reranker-model.md](../concepts/02-reranker-model.md) — 滑窗机制与 device 不对称详解
- [/concepts/04-framework-integrations.md](../concepts/04-framework-integrations.md) — 框架封装如何消费 rerank
- [/examples/langchain-rag-rerank.md](../examples/langchain-rag-rerank.md) — 在 RAG 管线中接入精排
