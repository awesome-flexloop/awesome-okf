---
type: concept
title: "RerankerModel 与长文本滑窗策略"
description: "RerankerModel 的 compute_score/rerank 接口、128000 字符硬截断、query <400 token 断言、应用层滑窗切分与 max 合并机制，以及与 EmbeddingModel 的 device 支持不对称问题。"
tags: [bcembedding, reranker, rerankermodel, sliding-window, long-context, cross-encoder]
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

# RerankerModel 与长文本滑窗策略

`RerankerModel`（`BCEmbedding/models/reranker.py`）是一个 cross-encoder：把 query 与 passage 拼接后过同一个分类头，输出相关性分数。它对外提供两个层次的方法——底层打分的 `compute_score` 与高层排序的 `rerank`——README 宣称的"长 passage 支持"（F-bc-028）完全由 `rerank` 内部的应用层滑窗算法实现，而非模型架构改造。

## 构造签名

```python
RerankerModel(
    model_name_or_path='maidalun1020/bce-reranker-base_v1',
    use_fp16=False,
    device=None,
    **kwargs
)
```

构造器以 `AutoTokenizer` 与 `AutoModelForSequenceClassification.from_pretrained` 加载（F-bc-013）。构造末尾还读取两个供长文本预处理使用的参数（F-bc-015）：

- `self.max_length = kwargs.get('max_length', 512)`
- `self.overlap_tokens = kwargs.get('overlap_tokens', 80)`

即滑窗行为可通过构造时的 `max_length`/`overlap_tokens` 关键字参数调节。

### device 分支：与 EmbeddingModel 不对称

RerankerModel 的 device 分支仅含 `cpu`、`cuda:N`、`cuda`，**没有 `xpu` 分支**；非法取值抛 `ValueError("Please input valid device: 'cpu', 'cuda', 'cuda:0', '0' !")`（F-bc-014）。而 EmbeddingModel 支持 `'xpu'`（经 `intel_extension_for_pytorch` 优化，F-bc-007）。两个本应平权的模型类在硬件适配层出现了单边能力——这是复制粘贴式重复代码必然漂移的典型反例：若在 Intel XPU 环境按 Embedding 的用法配置 Reranker，会在构造期直接抛 `ValueError`。

## compute_score：底层打分

```python
compute_score(sentence_pairs, batch_size=256, max_length=512, enable_tqdm=True)
```

行为要点（F-bc-016）：

- 断言 `sentence_pairs` 为 list；首元素为 str 时自动包装为二元组列表（如 `['query', 'passage']` → `[['query', 'passage']]`）；
- 按 batch 分词（截断至 `max_length=512`）后推理，对 `logits.view(-1,).float()` 施加 `torch.sigmoid`，返回 Python float 列表；
- **仅一个 pair 时返回标量 float**（`len(scores_collection)==1` 时直接返回 `scores_collection[0]`），多 pair 时返回 list——返回值类型随输入数量变化，调用方需自行判断；
- `num_gpus>1` 时 `batch_size` 乘以 `num_gpus`（F-bc-020）。

分数经 sigmoid 后落在 `(0, 1)` 区间，可解释为相关性概率，但库内并未提供概率校准，跨 query 比较绝对值时需谨慎。

## rerank：高层排序与长文本机制

```python
rerank(query, passages, batch_size=256)
```

返回字典，键为 `'rerank_passages'`、`'rerank_scores'`、`'rerank_ids'`；`rerank_ids` 为分数降序排列的原文索引（`np.argsort(merge_scores)[::-1].tolist()`）（F-bc-017）。其内部流程分四步：

### 1. 输入过滤与硬截断

先过滤 passages：仅保留非空 str 且截断为 `p[:128000]`（F-bc-018）。注意这是**字符级**切片而非 token 级。若 `query` 为 `None`/空串或 passages 为空，直接返回 `{'rerank_passages': [], 'rerank_scores': []}`——注意此时**没有 `rerank_ids` 键**（F-bc-018），调用方按固定三键解包会在这里出错。

### 2. 滑窗分块（`reranker_tokenize_preproc`）

`rerank` 调用 `BCEmbedding/models/utils.py` 中的 `reranker_tokenize_preproc(query, passages, tokenizer=None, max_length=512, overlap_tokens=80)`（F-bc-021），返回 `(sentence_pairs, sentence_pairs_pids)` 二元组，后者记录每个 chunk 属于哪条原文 passage。关键约束：

- 函数断言 `tokenizer is not None`（F-bc-021）；
- 先 `tokenizer.encode_plus(query, truncation=False, padding=False)` 得到 query 长度，再计算 `max_passage_inputs_length = max_length - len(query_inputs['input_ids']) - 2`，并断言其 `> 100`，否则报错 `"Your query is too long! Please make sure your query less than 400 tokens!"`（F-bc-022）——即 **query 长度有硬上限**（max_length=512 时约 400 token），超长 query 会直接断言失败；
- 超长 passage 按 `max_passage_inputs_length` 滑窗切分，实际重叠量为 `min(overlap_tokens, max_passage_inputs_length//4)`（F-bc-023）——默认 overlap 80 会被静默压缩到可用窗口的四分之一；
- 每个 chunk 以 `sep_token_id` 与 query 输入拼接（`_merge_inputs`），存在 `token_type_ids` 时追加对应长度全 1 列表（F-bc-023）。

### 3. 批量推理

逐 batch 以 `tokenizer.pad` 补齐后推理，取 sigmoid 得分（F-bc-019）。`num_gpus>1` 时 batch_size 同样乘以 `num_gpus`（F-bc-020）。

### 4. max 合并与排序

同一 passage 的多个 chunk 分数取 `max` 合并回文档级分数，再整体降序排序（F-bc-019）。max 合并意味着"含一个高分片段"的文档会胜过"整体均匀但无峰值"的文档——这是多次前向推理的近似，批量长文档场景的推理成本应按 chunk 数（而非 passage 数）估算。

## 机制总览

```
passages ──> p[:128000] 字符截断 ──> 过滤空串
    │
    ▼
reranker_tokenize_preproc(query, passages, ...)
    │  ├─ query encode（超长则断言失败，<400 token）
    │  ├─ window = 512 - len(query) - 2
    │  └─ 滑窗切 chunk（overlap = min(80, window//4)）
    ▼
batch 推理 → sigmoid 分数（per chunk）
    │
    ▼
同一 passage 多 chunk 取 max 合并
    │
    ▼
np.argsort 降序 → rerank_passages / rerank_scores / rerank_ids
```

## 注意事项

- **长文本能力是应用层算法**：模型权重零改动，仍是 512 token 输入的 cross-encoder；滑窗 + max 合并是 `models/utils.py` 中几十行代码实现的（I 阶段洞察 2）。可将"应用层滑窗 + 分段聚合"作为为短上下文模型外挂长文本能力的通用范式。
- **README 宣称的 "less than 32k tokens" 与 128000 字符截断并存**：截断单位是字符，对中文约等于 token 数，对英文则远小于 token 数，实际可处理的 token 量随文本语言构成变化（F-bc-018）。
- **query 长度约束是硬断言**：超出会直接抛 `AssertionError` 并附带英文提示，不是静默截断（F-bc-022）。
- **空输入返回结构不完整**：query/passages 为空时返回的 dict 缺少 `rerank_ids` 键（F-bc-018），解包前应做防御性判断。

## 相关概念

- [/concepts/01-embedding-model.md](/concepts/01-embedding-model.md) — EmbeddingModel（xpu 支持的对照）
- [/concepts/03-query-instruction.md](/concepts/03-query-instruction.md) — 跨语种检索与 query 长度约束的关系
- [/concepts/04-framework-integrations.md](/concepts/04-framework-integrations.md) — 框架集成层如何消费 rerank
