---
type: concept
title: "评测体系与 monkey-patch 模式"
description: "c_mteb 评测模块的任务族导入结构、AbsTaskReranking.evaluate 的 monkey-patch 劫持、ModChineseRerankingEvaluator 的 duck-typing 双路径（cross/bi-encoder），以及 YDDRESModel 适配层。"
tags: [bcembedding, evaluation, mteb, monkey-patch, cross-encoder, bi-encoder]
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

# 评测体系与 monkey-patch 模式

`BCEmbedding/evaluation/c_mteb/` 是本库自带的 MTEB 定制评测模块，覆盖跨语种检索（Retrieval）与重排序（Reranking）两族任务。其最引人注目的设计是：**不重载框架、不改 mteb 包源码，而是直接给 MTEB 基类方法赋值，实现"一处定制、全局生效"**（I 阶段洞察 5）。

## 模块结构

`c_mteb/__init__.py` 通配导入 `.Reranking` 与 `.Retrieval`，显式导入 `YDDRESModel`，并 `from mteb import MTEB`（F-bc-032）。由此，**只要 import 了 `BCEmbedding.evaluation.c_mteb`，monkey-patch 即已生效**——这是全局副作用式定制的固有特性（见下文注意事项）。

## monkey-patch：劫持基类方法

`Reranking.py` 在模块级定义 `evaluate` 函数后，直接执行：

```python
AbsTaskReranking.evaluate = evaluate
```

即用自定义评估逻辑整体替换 MTEB 官方基类方法（F-bc-035）。教科书式的评测定制做法是子类化任务类或向框架注册新评估器；此处选择直接改基类方法，代价是副作用不可见——导入该模块即生效，副作用范围等于 import 范围。学习者可掌握此模式作为评测/实验定制的高效手段，但应在模块文档中显式声明。

## 双路径评估器：duck-typing 分流

替换后的 `evaluate` 改用 `ModChineseRerankingEvaluator`（F-bc-035）。该评估器按模型**有无 `compute_score` 方法**分流（而非按类型判断）：

| 路径 | 判定 | 调用方式 | 典型模型 |
|---|---|---|---|
| cross-encoder | 有 `compute_score` | `model.compute_score(sentence_pairs)` | `RerankerModel` |
| bi-encoder | 无 `compute_score` | `encode_queries` / `encode_corpus` | `EmbeddingModel` 及兼容模型 |

指标为 `map` 与 `mrr`。duck-typing 意味着**任何实现 `compute_score` 的模型都会被当作 cross-encoder 评测**——若自定义模型恰好实现了同名方法但语义不同，会被静默分流到 cross-encoder 路径。

## 任务族回顾

- **Retrieval**：13 个 `AbsTaskRetrieval` 子类，六个领域（Books、Finance、Law、Others、Paper、Wiki）中英双向 + Qas En2Zh，`main_score='ndcg_at_3'`（F-bc-033）；
- **Reranking**：4 个 `AbsTaskReranking` 子类（T2/MMarco × Zh2En/En2Zh），`main_score='map'`（F-bc-034）。

任务族详情见 [/concepts/03-query-instruction.md](/concepts/03-query-instruction.md)。

## YDDRESModel：MTEB 检索任务适配层

`yd_dres_model.py` 中的 `YDDRESModel(nn.Module)` 包装 `EmbeddingModel`，默认参数 `pooler='cls'`、`normalize_embeddings=True`、`batch_size=160`、`max_length=512`，对外暴露 MTEB DRES（Dense Retrieval Exact Search）协议要求的三个方法（F-bc-036）：

- `encode_queries(queries)` — 附带 `query_instruction_for_retrieval`；
- `encode_corpus(corpus)` — dict 型 corpus 拼接为 `'{} {}'.format(doc.get('title', ''), doc['text']).strip()`（F-bc-037）；
- `encode(sentences)` — 通用入口；当 `instruction_for_all` 为 `True`（即 `model_name_or_path` 含 `"e5-base"` 或 `"e5-large"`）时强制使用 query 指令（F-bc-037）。

即 YDDRESModel 是"EmbeddingModel → MTEB 检索协议"的薄适配层，内部仍以 `batch_size=160`、`max_length=512` 调用 `EmbeddingModel.encode`（F-bc-036）。

## 评测入口与版本

README 声明 MTEB 评测要求 `mteb==1.1.1`（F-bc-031）。`BCEmbedding/evaluation/` 下的 `eval_mteb`、`eval_rag` 为评测入口脚本，R 阶段仅登记其存在、未逐行采集（详见 [/references/facts.md](/references/facts.md)「存疑与说明」）。RAG 评测要求 `transformers==4.36.0` 与 `llama-index==0.9.22`（F-bc-031）。

## 注意事项

- **import 即副作用**：工程代码中若 import 了 `BCEmbedding.evaluation.c_mteb`，`AbsTaskReranking.evaluate` 已被全局替换，可能波及同进程中其他 MTEB 任务的评测行为（F-bc-035）。
- **duck-typing 的边界**：任何实现 `compute_score` 的模型对象都会被当 cross-encoder 处理（F-bc-035），封装第三方模型时需确认方法名不撞车。
- **版本锁定严格**：mteb 1.1.1 是旧版 API，新版 mteb（≥2.x）任务注册与评估器接口已大改，直接套用本模块代码需先做 API 对齐（F-bc-031）。
- **厂商自宣数据不入清单**：README 的 MTEB/RAG 榜单数字未纳入本知识包事实清单，评测结论应自行复现。

## 相关概念

- [/concepts/03-query-instruction.md](/concepts/03-query-instruction.md) — 任务族与指令字典
- [/concepts/01-embedding-model.md](/concepts/01-embedding-model.md) — encode 数据流（YDDRESModel 的底层）
