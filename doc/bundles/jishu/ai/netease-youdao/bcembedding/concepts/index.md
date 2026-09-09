# 概念文档

BCEmbedding 核心概念，共 6 篇，按"双模型基础 → 检索与生态"的依赖顺序组织。

## 基础与双模型

* [00 安装与快速上手](00-quickstart.md) — 包元数据与依赖约束（transformers 锁定 <4.37.0）、pip/源码安装、封装类/原生 transformers/sentence-transformers 三种调用路径、模型清单。
* [01 EmbeddingModel：向量化接口全解](01-embedding-model.md) — 构造参数（pooler/device/fp16/多卡 DataParallel）、encode 数据流（指令前缀→分词→CLS/mean pooling→L2 归一化）、xpu device 解析。
* [02 RerankerModel 与长文本滑窗策略](02-reranker-model.md) — compute_score/rerank 接口、128000 字符硬截断、query <400 token 断言、应用层滑窗切分与 max 合并。

## 检索与生态

* [03 跨语种检索与 query instruction 字典](03-query-instruction.md) — 指令字典结构（BGE/e5 共 21 键）与"跨家模型适配层"本质、c_mteb 中英双向任务族、YDDRESModel 自动指令探测。
* [04 LangChain 与 LlamaIndex 集成：两个 BCERerank](04-framework-integrations.md) — 两个同名 BCERerank 封装约定、top_n 默认值差异（3 vs 5）、延迟导入、分数写回、版本锁定。
* [05 评测体系与 monkey-patch 模式](05-evaluation-monkeypatch.md) — c_mteb 任务族导入结构、AbsTaskReranking.evaluate 劫持、duck-typing 双路径（cross/bi-encoder）、YDDRESModel 适配层。

```{toctree}
:hidden:
:maxdepth: 7

00-quickstart
01-embedding-model
02-reranker-model
03-query-instruction
04-framework-integrations
05-evaluation-monkeypatch
```
