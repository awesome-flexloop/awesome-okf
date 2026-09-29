---
type: concept
title: LocalDocQA 问答编排链与硬编码阈值
description: 逐帧拆解 get_knowledge_based_answer() 生成器——问题改写、检索、rerank 过滤、prompt 组装、SSE 输出——并剖析 0.28/0.5/0.9/300 阈值集群的工程含义与治理建议。
tags: [qanything, rag, orchestration, localdocqa]
generated: { by: okf-wiki/0.2, at: 2026-09-09 }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: QAnything 源码事实清单（F-qa-001~060）
  - id: insights
    resource: /references/insights.md
    title: QAnything 架构洞察与知识地图
---

# LocalDocQA 问答编排链与硬编码阈值

`LocalDocQA` 是 QAnything 的问答编排核心类，定义于 `qanything_kernel/core/local_doc_qa.py`，构造函数签名为 `LocalDocQA(port)`，其 `init_cfg()` 一次性完成向量库客户端、ParentRetriever 检索器、embedding/rerank 客户端与 MySQL 管理器的初始化（F-qa-001）。它的主编排方法 `get_knowledge_based_answer()` 是一个生成器，串联起从原始问题到流式回答的全部阶段（F-qa-002）。本文逐帧拆解这条链路，并重点剖析散布其中的硬编码阈值——它们决定了召回质量，却不在任何配置文件中。

## 编排链总览

`get_knowledge_based_answer()` 依次产出以下帧（F-qa-002）：

```
用户 question (+ history)
  → ① 问题改写（condense_question）      [RewriteQuestionChain]
  → ② 检索文档（向量/混合检索 child）     [ParentRetriever]
  → ③ rerank 结果（精排 + 过滤）
  → ④ prompt（模板 + <reference> 检索片段）
  → ⑤ LLM 增量输出（SSE data: 帧）
  → ⑥ 结束帧 [DONE]
```

### ① 问题改写

多轮对话场景下，历史轮次与当前问题会先交给 `RewriteQuestionChain`：它以 `ChatOpenAI(temperature=0, top_p=0.01, seed=1234)` 为改写模型（极低温度保证确定性），用中文系统提示词把"history + question"改写为可独立理解的问句，链式表达式为 `condense_q_prompt | chat_model | StrOutputParser()`（F-qa-017）。改写结果既作为检索 query，也作为生成帧回传给客户端。

### ② 检索

改写后的问题经 embedding 客户端向量化，进入检索阶段。默认向量检索 top_k 为 30（`VECTOR_SEARCH_TOP_K=30`），相似度分数阈值 0.3（`VECTOR_SEARCH_SCORE_THRESHOLD=0.3`）（F-qa-023）。检索返回的是 child 文档，parent 全文需从 MySQL 回填，两级切分机制详见 [/concepts/03-retrieval.md](/concepts/03-retrieval.md)。

### ③ rerank 与硬编码阈值集群

这是整条链路上阈值最密集的阶段。当且仅当 `num_tokens_rerank(query) <= 300` 时才触发 rerank（F-qa-005）——**query 超过 300 tokens 时整个 rerank 阶段被跳过**，最终排序退化为向量检索的原始顺序。触发后，rerank 分数的过滤与截断规则为（F-qa-003）：

- 分数 < 0.28 的文档直接剔除；
- 相邻文档 rerank 分数相对差 > 0.5 时截断，后续文档不再保留；
- 过滤完成后按 `top_k` 截断（F-qa-005）。

这里有两个工程隐患。其一，0.28 这个生效阈值在 `get_knowledge_based_answer` 与 `get_rerank_results` 两处重复出现（后者同样返回分数 ≥ 0.28 的结果，F-qa-009），同一阈值两个维护点，存在漂移风险。其二，"rerank 门槛前置"是隐性行为：API 入参中的 `rerank` 开关（F-qa-038）并不能覆盖"query 过长则跳过"这一规则，长问题用户会静默得到更弱的召回。调参时不能只改 `model_config.py`，必须先全文检索 `local_doc_qa.py` 中的字面量。

### FAQ 短路

在 LLM 生成之前还有一条快速通路：当某文档为 FAQ 且（query 与 question 完全匹配，或 `calculate_relevance_optimized` 得分 ≥ 0.9）时，直接返回 FAQ 答案，跳过 LLM 生成（F-qa-004）。`calculate_relevance_optimized()` 使用 `scipy.spatial.cKDTree` 检索 query 嵌入的近邻，以 0.5/0.5 加权几何平均融合向量相似度与字符串重合度（F-qa-008）。这使得高频标准问题可以零生成成本命中。

### ④ prompt 组装

`generate_prompt()` 对模板执行 `{{context}}`、`{{question}}` 占位符替换，检索文档以 `<reference>` 标签包裹后拼入提示词（F-qa-007）。`model_config.py` 预置 SYSTEM、INSTRUCTIONS、PROMPT_TEMPLATE、CUSTOM_PROMPT_TEMPLATE、SIMPLE_PROMPT_TEMPLATE 五组提示词模板（F-qa-025），Bot 可绑定自定义 prompt（F-qa-040）。拼入前，`reprocess_source_documents()` 会按 token 预算裁切文档内容，使拼接后的上下文不超过 LLM 上下文长度预算（F-qa-006）。

### ⑤⑥ LLM 生成与 SSE 输出

LLM 调用经抽象层完成：`OpenAILLM` 构造函数参数为 `(model, max_token, api_base, api_key, api_context_length, top_p, temperature)`，类常量 `offcut_token=50` 预留输出余量；token 统计经 tiktoken（编码 `cl100k_base` 回退）并乘 1.2/1.1 余量系数，调用入口为 `client.chat.completions.create`（F-qa-020）。抽象层定义了 `AnswerResult` 数据类（含 history、llm_output、prompt、total_tokens 等字段）与抽象基类 `BaseAnswer(ABC)`，便于替换不同 LLM 实现（F-qa-021）。增量输出按 SSE `data: ` 前缀封装逐帧产出，结束帧为 `[DONE]`（F-qa-002）。

## 阈值集群一览

| 阈值 | 位置 | 作用 | 事实编号 |
|---|---|---|---|
| 0.28 | `get_knowledge_based_answer` + `get_rerank_results` | rerank 分数下限（两处重复） | F-qa-003、F-qa-009 |
| 0.5 | `get_knowledge_based_answer` | 相邻 rerank 分数相对差截断 | F-qa-003 |
| 0.9 | `get_knowledge_based_answer` | FAQ 相关性短路 | F-qa-004 |
| 300 | `get_knowledge_based_answer` | rerank 触发 token 上限 | F-qa-005 |
| 0.3 | `model_config.py` | 向量检索分数阈值 | F-qa-023 |

## 二次开发建议

1. 将 0.28/0.5/0.9/300 提取为配置项，并消除 0.28 的重复定义；
2. 评估长 query 场景时须意识到 rerank 可能未生效，需单独验证；
3. 替换 LLM 时实现 `BaseAnswer` 抽象基类并返回 `AnswerResult`，即可接入编排链（F-qa-021）；
4. 自定义 prompt 优先使用 CUSTOM_PROMPT_TEMPLATE 机制，而非改写默认模板（F-qa-025）。

## 相关概念

- [00 QAnything 全景](/concepts/00-overview.md)
- [03 父子切分与 Milvus/ES 混合检索](/concepts/03-retrieval.md)
- [07 演进痕迹：死代码、失效导入与版本错位](/concepts/07-evolution-traces.md)
