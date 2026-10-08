---
type: concept
title: "跨语种检索与 query instruction 字典"
description: "query_instructions.py 指令字典的结构（BGE/e5 共 21 键）及其'跨家模型适配层'本质、c_mteb 中英双向检索任务族（13 个 Retrieval + 4 个 Reranking 任务），以及 YDDRESModel 对 e5 模型的自动指令探测。"
tags: [bcembedding, query-instruction, crosslingual, retrieval, bge, e5, c-mteb]
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

# 跨语种检索与 query instruction 字典

`BCEmbedding/utils/query_instructions.py` 维护了一组"模型名 → 查询/篇章指令"的字典，配合 `BCEmbedding/evaluation/c_mteb/` 的中英双向检索任务族，构成本库的跨语种评测体系。一个反常识的事实是：**这套指令字典服务对象全部是第三方模型（BGE、e5），而非 BCE 自家模型**（I 阶段洞察 1）。

## 指令字典的结构

字典共两部分（F-bc-025）：

- `query_instruction_for_retrieval_dict`：17 个键
  - 6 个 `BAAI/bge-*-en*` 英文模型 → `"Represent this sentence for searching relevant passages: "`
  - 7 个 `BAAI/bge-*-zh*` 中文模型 → `"为这个句子生成表示以用于检索相关文章："`
  - 4 个 `intfloat/*e5*` 模型 → `"query: "`
- `passage_instruction_for_retrieval_dict`：4 个键（intfloat e5 系）→ `"passage: "`

两个值得登记的边角事实（F-bc-026）：

- `BAAI/bge-large-zh-noinstruct` 对应的 query 指令值为 `None`（该变体设计上不带指令）；
- 存在键 `"BAAI/bge-small-zh-v.15"`——点号写法与同文件 `v1.5` 系列的命名不一致，按源码原文登记，换底模匹配键名时若以模型名为依据检索，此键可能匹配不上。

## 为什么是"为别人家模型维护的字典"

BCE 自家模型 `bce-embedding-base_v1` 被 README 明确标注 "does not need specific instructions"（F-bc-028），即调用 `encode` 时 `query_instruction` 应保持默认空串（F-bc-010）。字典里甚至登记了 BGE 的无指令变体（`noinstruct → None`）。由此可确认该字典在 RAG 流水线中扮演**跨家模型适配层**：同一套检索/评测代码在 BGE、e5、BCE 等不同底模间切换时，用字典查表自动补上前置指令，保证流程可复现（I 阶段洞察 1）。

## 使用方式

`EmbeddingModel.encode` 的 `query_instruction` 参数为非空字符串时，拼接为每条句子的前缀（F-bc-010）。为 BGE 中文模型生成查询向量：

```python
from BCEmbedding import EmbeddingModel
from BCEmbedding.utils.query_instructions import query_instruction_for_retrieval_dict

model_name = "BAAI/bge-large-zh-v1.5"
model = EmbeddingModel(model_name_or_path=model_name)

instruction = query_instruction_for_retrieval_dict[model_name]  # "为这个句子生成表示以用于检索相关文章："
q_emb = model.encode(["什么是 RAG？"], query_instruction=instruction)
p_emb = model.encode(["检索增强生成是一种……"])
```

注意事项：换底模后若忘记启用对应指令，检索质量下降的原因可能藏在**字典键名与实际模型名是否精确匹配**上（如前述 `bge-small-zh-v.15` 可疑键名，F-bc-026）。

## c_mteb 跨语种任务族

`BCEmbedding/evaluation/c_mteb/Retrieval.py` 定义 13 个 `AbsTaskRetrieval` 子类（Grep 计数 `class CrosslingualRetrieval*` = 13）：Books、Finance、Law、Others、Paper、Wiki 六个领域各含 En2Zh/Zh2En 双向，Qas 仅含 En2Zh；均注册 `hf_hub_name='maidalun1020/CrosslingualRetrieval*'`、`eval_splits=['dev']`、`main_score='ndcg_at_3'`（F-bc-033）。`Reranking.py` 定义 4 个 `AbsTaskReranking` 子类：`T2RerankingZh2En`、`T2RerankingEn2Zh`、`MMarcoRerankingZh2En`、`MMarcoRerankingEn2Zh`，`eval_langs` 为 zh-en/en-zh，`main_score='map'`（F-bc-034）。这两族任务即以中英双向为主轴的跨语种检索/重排序评测集，配套数据集发布于 HuggingFace `maidalun1020` 组织。

## YDDRESModel 的自动指令探测

`BCEmbedding/evaluation/c_mteb/yd_dres_model.py` 中的 `YDDRESModel(nn.Module)` 包装 `EmbeddingModel`，默认参数 `pooler='cls'`、`normalize_embeddings=True`、`batch_size=160`、`max_length=512`，提供 `encode_queries`、`encode_corpus`、`encode` 三个方法供 MTEB 检索任务调用（F-bc-036）。与指令字典的联动点：

- `encode_corpus` 对 dict 型 corpus 拼接为 `'{} {}'.format(doc.get('title', ''), doc['text']).strip()`（F-bc-037）；
- `instruction_for_all` 在 `model_name_or_path` 含 `"e5-base"` 或 `"e5-large"` 时为 `True`，此时 `encode` 强制使用 query 指令（F-bc-037）——即 e5 系的指令是**按模型名子串自动探测**的，不需要人工指定。

这一探测逻辑正是"指令字典作为适配层"思想在评测代码中的落地：评测脚本用同一入口 `encode` 跑所有模型，由模型名决定是否自动注入 `"query: "` 指令。

## 注意事项

- 指令只对检索**查询侧**语义影响显著；为 passage 加指令（e5 的 `"passage: "`）同样是流程正确性的一部分，漏加会改变向量空间对齐方式。
- 字典键名必须与实际模型名精确匹配，换模型前建议先 `in` 检查键是否存在。
- 评测任务的主指标是 `ndcg_at_3`（检索）与 `map`（重排序）（F-bc-033、F-bc-034），解读榜单或复现实验时以这两个指标为准。

## 相关概念

- [/concepts/01-embedding-model.md](/concepts/01-embedding-model.md) — query_instruction 参数的数据流
- [/concepts/02-reranker-model.md](/concepts/02-reranker-model.md) — query 长度约束（<400 token 断言）
- [/concepts/05-evaluation-monkeypatch.md](/concepts/05-evaluation-monkeypatch.md) — 评测任务族的执行机制
