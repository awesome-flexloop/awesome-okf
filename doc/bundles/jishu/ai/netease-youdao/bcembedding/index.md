---
type: bundle
title: BCEmbedding 双语 Embedding/Reranker 模型库
okf_version: "0.2"
---

# BCEmbedding 知识库

本知识包是网易有道开源的双语 Embedding/Reranker 模型库 [BCEmbedding](https://github.com/netease-youdao/BCEmbedding)（Apache-2.0 许可证）的系统化中文源码教程，基于 vendor 子模块 `vendor/netease-youdao/BCEmbedding/` 源码与 README（信源基线 commit `1aa07ea64f94523965c8672e93da47c3faf4d2cd`，采集版本 0.1.5）深度阅读生成，经 R→I→E→V→C 五阶段链路产出。覆盖从 EmbeddingModel 向量化数据流到 RerankerModel 长文本滑窗策略、从 query instruction 跨家适配字典到 LangChain/LlamaIndex 框架集成、从 c_mteb 评测体系到 monkey-patch 定制模式的完整知识体系，全部内容溯源至 BCEmbedding Python 源码（`models/`、`utils/`、`tools/`、`evaluation/`）。

## 基础与双模型篇（concepts/）

* [安装与快速上手](concepts/00-quickstart.md) — 包元数据与依赖约束（transformers 锁定 <4.37.0）、pip/源码两种安装方式、封装类/原生 transformers/sentence-transformers 三种调用路径、bce-embedding-base_v1 与 bce-reranker-base_v1 模型清单。
* [EmbeddingModel：向量化接口全解](concepts/01-embedding-model.md) — 构造参数（pooler/device/fp16/多卡 DataParallel）、encode 完整数据流（指令前缀→分词→CLS/mean pooling→L2 归一化）、device 解析的 xpu 支持。
* [RerankerModel 与长文本滑窗策略](concepts/02-reranker-model.md) — compute_score/rerank 接口、128000 字符硬截断、query <400 token 断言、应用层滑窗切分与 max 合并机制、与 EmbeddingModel 的 device 支持不对称问题。

## 检索与生态篇（concepts/）

* [跨语种检索与 query instruction 字典](concepts/03-query-instruction.md) — query_instructions.py 指令字典结构（BGE/e5 共 21 键）及其"跨家模型适配层"本质、c_mteb 中英双向检索任务族（13 个 Retrieval + 4 个 Reranking）、YDDRESModel 对 e5 模型的自动指令探测。
* [LangChain 与 LlamaIndex 集成：两个 BCERerank](concepts/04-framework-integrations.md) — tools/langchain 与 tools/llama_index 下两个同名 BCERerank 封装的接口约定、top_n 默认值差异（3 vs 5）、延迟导入模式、分数写回约定与版本锁定。
* [评测体系与 monkey-patch 模式](concepts/05-evaluation-monkeypatch.md) — c_mteb 评测模块的任务族导入结构、AbsTaskReranking.evaluate 的 monkey-patch 劫持、ModChineseRerankingEvaluator 的 duck-typing 双路径（cross/bi-encoder）、YDDRESModel 适配层。

## 实战示例（examples/）

* [Embedding 文本向量化流程](examples/embedding-text-vectorization.md) — 官方封装类与 sentence-transformers 两条向量化路径：模型加载、encode 调用、余弦相似度计算、指令前缀的正确使用（应为空）。
* [LangChain 集成接入：检索-精排管线](examples/langchain-rag-rerank.md) — 基于 README 官方 demo 的 HuggingFaceEmbeddings 向量检索 + BCERerank 上下文压缩，复现检索-精排两段式 RAG 管线，核对版本锁定与 top_n 约定。
* [Reranker 打分与重排序](examples/reranker-scoring-and-sorting.md) — compute_score 与 rerank 完成查询-篇章相关性打分与排序：单 pair 标量返回、多 pair 列表返回、rerank 三键返回结构、长文本滑窗的 max 合并效果。

## 信源登记簿（references/）

* [BCEmbedding 源码事实清单（F-bc 系列）](references/facts.md) — R 阶段事实采集产物：40 条事实（F-bc-001~040）逐条登记、零推测，证据位置为 vendor 仓库相对路径 + 符号名，数量陈述均经实际 Glob/Grep 计数。
* [BCEmbedding 架构洞察与知识地图](references/insights.md) — I 阶段产物：基于 40 条事实提炼 5 条架构洞察，每条挂接证据编号供 V 阶段回查，含反常识点与行动建议。
* [BCEmbedding 信源登记表](references/sources.md) — 上游仓库 URL、固定基线 commit `1aa07ea64f94523965c8672e93da47c3faf4d2cd`、本地引用位置（vendor 只读子模块）、Apache-2.0 许可证与采集版本 0.1.5 的登记。

## 信任与生命周期说明

* **status 判定依据**：全部 12 个内容文档（6 个概念 + 3 个示例 + 3 个信源登记）均 `status: stable`。内容基于对 BCEmbedding 源码（`models/`、`utils/`、`tools/`、`evaluation/` 目录）与 README 的逐文件阅读与事实提取（40 条源码事实 F-bc-001~040），经 R→I→E→V→C 五阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-09-09`。BCEmbedding 包版本 0.1.5 已长期未发新版，核心接口（EmbeddingModel.encode、RerankerModel.compute_score/rerank、BCERerank 封装）稳定；该日期作为针对上游发布新版本（如 transformers 锁定区间调整、模型清单更新）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（类名/方法签名/字段/依赖约束逐一比对源码），两者分离、可追溯。

本知识包共收录 12 个内容文档（6 个概念 + 3 个示例 + 3 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
