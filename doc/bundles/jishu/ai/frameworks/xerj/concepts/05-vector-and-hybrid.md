---
type: Concept
title: 向量、嵌入与混合检索
description: XERJ 的四类嵌入后端与「嵌入在摄入时绑定」的时机约束、HNSW 图索引的设计与 flat-slab 重构、精确扫描与 ANN 的判定规则、混合融合与 rerank
tags: [xerj, 向量, 嵌入, hnsw, 混合检索, 精确扫描]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-facts
    resource: /references/facts.md
    title: XERJ 事实清单
  - id: xerj-insights
    resource: /references/insights.md
    title: 架构洞察与知识地图
---

# 向量、嵌入与混合检索

本篇覆盖 XERJ 检索侧最容易被误用的部分：向量从哪来、什么时候准、什么时候必须走精确路径。**读这篇前请先记住一条：默认嵌入模式是词法，不是神经。**

## 四类嵌入后端

`Embedder` 把四种后端藏在同一个句柄后面，使引擎的摄入与查询路径**从不在后端上分支**（F-105）：

| 后端 | 实现 | 启用方式 | 性质 |
|---|---|---|---|
| `Lexical` | 内置特征哈希（`crate::local::local_embed`） | **默认** | 零依赖、离线、确定性；词法/子词重叠，**不是神经语义** |
| `Proxy` | 外部 OpenAI 兼容 `/v1/embeddings` | `--embed-mode proxy` | 任意模型/供应商；文档文本会出节点 |
| `Neural` | 内置 BERT 句向量编码器，candle 进程内 | `--embed-mode neural`（`neural` feature） | all-MiniLM-L6-v2，模型约 90 MB 首次使用时下载 |
| `Onnx` | 进程内 ONNX Runtime | `onnx-experimental` feature | 实验性，需显式模型与分词器路径，惰性加载 |

两个关键机制：

- **查询路径用写入时的同一后端自动嵌入** `semantic_text` 字段（F-106）。摄入与查询向量同源，这是可比性的前提。
- `Embedder::is_active` 区分神经/代理/ONNX 与词法回退（F-107）。

## 默认嵌入器：384 维词法特征哈希

`xerj-ai/src/local.rs` 的实现是确定性的特征哈希（hashing vectoriser）：

| 参数 | 值 | 出处 |
|---|---|---|
| 维度 | `DEFAULT_DIMS = 384` | F-108 |
| 哈希函数 | 64 位 FNV-1a（初值 `0xcbf29ce484222325`，质数 `0x00000100000001b3`） | F-109 |
| 桶选择 | `h % dims` | F-110 |
| 符号 | 1 个高位比特决定正负（有符号哈希，降低碰撞偏置） | F-110 |
| 特征一 | 整词一元组，权重 1.0 | F-111 |
| 特征二 | 词内字符三元组（以 `#` 补边），权重 0.35 | F-111 |
| 归一化 | 整体 L2 归一化，使余弦与文本长度无关 | F-112 |

384 这个数字不是随意选的：它对齐 `all-MiniLM-L6-v2` 的输出宽度，因此从内置嵌入器切到同宽度的真实代理模型**不需要任何映射改动**。

源码注释对能力边界写得毫不含糊（F-113）：

> This is **not** a neural model — it captures lexical / sub-word overlap, not deep semantics.

空文本或 `dims == 0` 产生全零向量，余弦相似度按 0 处理，不 panic（F-114）。

## 最重要的一条时机约束

`--embed-mode` 是**服务器启动标志**，且在**摄入时**生效（F-116）：

> 文本在被索引时就被嵌入，所以文档写入时在用的模式，就是该文档此后保留的模式。从词法切到神经**不会**重新嵌入任何已索引内容——你必须重新索引所有在意的语料。**在索引第一个语料之前就决定。**

这条约束的实际后果：

| 决策时机 | 后果 |
|---|---|
| 索引前决定 | 一次到位，零迁移成本 |
| 索引后切换 | 所有语料必须重建；且新旧向量混在同一索引里会得到无法解释的相似度 |

这也是为什么 `llms.txt` 把「索引一个参考库」这条操作指南的**第一句**就是「先决定 `--embed-mode`，因为它在摄入时生效」（`landing/llms.txt:104`）。

## 神经模式的真实代价

`--embed-mode neural` 启用内置 BERT 编码器（F-115）。上游记录的细节：

- 模型文件（`config.json`、`tokenizer.json`、`model.safetensors`）经 HTTPS 从 **HuggingFace Hub**（`sentence-transformers/all-MiniLM-L6-v2`）下载到 `~/.cache/huggingface`，之后复用；
- **XERJ 自身不为这些文件固定校验和**——完整性保证来自 TLS 与 Hub，而不是 XERJ 验证的摘要（F-117）；
- 空气隔离或策略受限环境：预先下载三个文件，把 `embedding.local_model_dir` 指向该目录，此后不再发生任何下载（F-118）。

## HNSW 图索引

`xerj-vector/src/hnsw.rs` 的设计决策写在文件头（F-119）：

| 参数 | 值 | 说明 |
|---|---|---|
| `m` | 16 | 每层每节点最大双向连接数——精度/内存的折中 |
| `ef_construction` | 200 | 构建期动态候选表大小——构建期高召回 |
| 层选择 | 标准 ln 公式 | — |
| 邻居选择 | 论文 Algorithm 4 多样性启发式 | hnswlib 与 Lucene 使用的变体；「只取最近的 M 会把节点的链接挤成一个紧簇，可测地破坏可导航性」 |

图完全驻内存，持久化交给 storage crate（F-120）。磁盘格式：魔数 `XHNS0001`，格式版本 2（v1 为初版，v2 增加尾部 tombstone 块）（F-122）。

### flat-slab 重构：一个性能教训

2026-07-12 的内存布局改动值得单独记住（F-121）。旧布局是 `HashMap<u64, Arc<RwLock<Node>>>`，每次邻居扩展要付出一次哈希查找 + 两次指针追逐 + 一次 RwLock 获取——结果是 **beam search 约为距离计算本身的 5 倍慢**。新布局把节点放进单一的 slot 索引 slab：

- 一个连续的 `Vec<f32>` 存向量；
- `Vec<Vec<u32>>` 存各层的邻居表；
- `Vec<u64>` 位图存搜索期的访问集。

所有热路径状态按 `slot` 寻址，于是 beam search 在连续数组上跑，**无逐节点锁、无哈希**。磁盘格式与对外（外部 u64 id）API 不变。

> **可迁移的方法论**：当一个「距离计算」系统里，索引结构本身的开销数倍于计算本身时，问题在数据结构而不在算法。slot 化 + 连续数组是通用解法。

## 精确扫描 vs ANN：判定规则

这是本篇最需要精确的部分。上游的表述非常明确：

**走 HNSW（ANN）路径的条件**（F-123）：

- 未过滤的 `knn`；
- 全精度余弦相似度字段；
- 文档数 **≥ 1,024**；
- 图未过期。

此时跑持久化 HNSW 图的 beam search，并对候选**精确重打分**，所以返回的 `_score` 与精确路径**逐位一致**。`num_candidates` 是 beam 宽度（下限 800；缺省时套用 ES 的 1.5×k）。

**走精确暴力扫描的条件**（F-125）：

- 过滤或嵌套 kNN；
- 非余弦相似度；
- SQ8 量化字段；
- 文档数少于 1,024 的索引；
- 图过期；
- `semantic` 与 `/_memory` 召回。

### 召回率的表述纪律

| 路径 | 召回率性质 | 实测值 |
|---|---|---|
| ANN（未过滤） | **实测值，不是保证** | 50k×128 维基准语料上官方基准查询 recall@10 = **1.00**；100 探针均值 **0.976**、最小 **0.90**（同协议下 ES 8.13.4 为 0.937 / 0.70）（F-124） |
| 精确扫描 | **构造保证** | recall 1.00，延迟随扫描的向量数增长（F-125） |

另外，**ANN 路径可能返回少于 k 条命中**（F-126）。

> **反常识**：常见的宣传口径是「recall 1.00 by construction」——那是**精确扫描路径**的性质。ANN 路径的 recall 是量出来的、且会低于 1.00。上游坚持在文档里把这两者分开写，是本项目诚实基准政策的一部分。
>
> **行动**：报告 kNN 质量时，必须区分「未过滤 ANN（实测）」与「过滤/小索引精确扫描（构造保证）」。把前者说成后者，是把一个测量值偷换成构造性质。

## 混合融合

`hybrid` 子句把词法与向量/语义子查询融合起来。**只支持两种融合方式**（F-094）：

- `rrf`——倒数排名融合，默认，k=60；
- `linear`——线性加权。

`fusion: "learned"` **未实现并显式失败**：`400 hybrid fusion learned is not yet supported; use rrf or linear`。不要依赖它。

### 一个必须知道的耦合：向量臂的覆盖范围

向量臂**只对把字段映射为 `semantic_text` 的索引有效**。在未映射该字段的索引上发起语义查询**不降级**，而是让整个请求 400，并连带拖垮通配符下的其他索引（F-183）。

`xerj code` 因此会**先读 mapping**，只把向量臂瞄准有能力的索引；每次混合检索的开头会给出「实际跑了哪些臂」的说明行，例如：

```
[hybrid RRF(k=60) — BM25 over 9 index(es), vector over 3 of 9]
```

若向量臂跑不了，它会明说 `BM25 only — …`，而不是假装跑过。

> 这条坑有历史教训：混合模式曾是默认模式，依据只在 rust-text 一个语料上（其 top-1 更优）；在 C 语料上，向量臂只覆盖 407 个索引中的 **5 个**（issue #173），融合等于把一个好的排名和一个看不见 98.8% 材料的排名混在一起（F-181）。

## `rerank`：唯一在搜索期外呼的特性

加 `"rerank": {}` 到 `_search`，XERJ 会把排序靠前的结果发给第三方相关性评判服务，用返回的 0–1 概率取代 `_score`（F-095）。

必须知道的边界：

| 项 | 值 |
|---|---|
| 外发内容 | 问题文本 + 最多 `window` 条命中的文本（默认 30，上限 300） |
| 密钥来源 | 只能由运维方配置（`[rerank] api_key` 或 `TYPESAFE_API_KEY`），**请求内不能传** |
| 完全关闭 | `[rerank] enabled = false` |
| 提供方慢 | HTTP **200** + 引擎原序 + `_rerank.applied:false`——**必须读 `_rerank.applied`** |
| 无密钥 | 503 |
| 已禁用 | 403 |
| 密钥被拒 / 体畸形 / 不可达 | 502，带 `rerank_exception` 且**无命中**——不要重试，去掉 `rerank` 重跑 |
| 与哪些查询互斥 | `sort`、`search_after`、`collapse`、scroll（打开与续取）、`size:0`、`_msearch`、搜索模板、`_async_search`、原生 `/v1` 搜索 API、gRPC —— 一律**拒绝**（400），不静默忽略（F-097） |

失败策略被概括为「超时降级、契约违约上报」（F-096）：慢是降级，坏是报错。

另有两个特性在**运维方开启**时也会外发文本，且默认关闭（F-099）：`[embedding] default_endpoint` / `--embed-mode proxy`（摄入时的文档文本与查询时的查询文本），以及 WAL tap（`PUT /_xerj/wal_tap`，被监听索引上的每一次写入发往外部 `_bulk` 端点）。默认节点两者都不联系；节点的其他出站连接（一次性的神经模型下载、到你自己的对等节点的集群 Raft）**不携带文档文本**。

> **行动**：除非用户明确同意，不要在必须留在本地的数据上加 `rerank`。`rerank.fields` 是穷尽式允许列表，`_source` 过滤也同时限制外发内容。

## 决策表：这次该用哪种检索

| 需求 | 选择 | 理由 |
|---|---|---|
| 已知符号名 | `xerj def` / `match` + `prefix` | 定义优先排序，跳过全文打分噪声 |
| 精确短语 | `match_phrase` | — |
| 语义/同义 | `semantic` | **先确认嵌入模式**（默认是词法） |
| 向量近邻 | `knn` | 自带 query vector |
| 词法+向量 | `hybrid`（`rrf`） | 确认向量臂的索引覆盖 |
| 需要真语义 | 先 `--embed-mode neural` **再索引** | 摄入时绑定 |
| 只要片段 | `fields: ["_passage"]` + `_source` 投影 | 34 倍响应缩减 |

## 相关概念

- [00 整体架构](/concepts/00-overview.md)：`xerj-vector` 在整体中的位置
- [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md)：语义/向量/混合三个工具
- [04 检索路径与响应裁剪](/concepts/04-search-query-path.md)：`_passage` 与 `_source` 投影
- [06 智能体记忆与第二大脑](/concepts/06-agent-memory-and-brain.md)：`/_memory` 的召回模式
- [07 ES 兼容与基准诚实性](/concepts/07-es-compat-and-benchmarks.md)：基准口径与外呼边界
- 事实来源：[事实清单](/references/facts.md)
