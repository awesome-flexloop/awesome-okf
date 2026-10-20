---
type: Concept
title: 查询类型与聚合
description: XERJ 的 50 种查询类型与 2 种显式拒绝、62 种聚合的精确性与采样例外、10,000 文档以上的列式快速路径，以及查询面与 ES 的语义差异
tags: [xerj, 查询, 聚合, 精确性, 数据模型]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-docs-facts
    resource: /references/facts-docs.md
    title: 官方文档站事实清单
  - id: xerj-docs-source
    resource: /references/docs-source.md
    title: 官方文档站信源登记
---

# 查询类型与聚合

XERJ 的查询面有两个值得记住的性质：**所有查询都是同一个 `QueryNode` 枚举的变体**（编译到同一执行计划，所以在一个 `bool` 下混搭是零成本的，没有编排器的往返）；**所有桶聚合返回精确计数**（桶路径上没有 HyperLogLog 近似）。

## 查询类型全集：50 种

列表由 `xerj_query::parser::SUPPORTED_QUERY_TYPES` 生成并由测试锁定（F-209）。按家族整理：

### 结构类（7）

| 查询 | 语义 |
|---|---|
| `match_all` | 索引内全部文档 |
| `match_none` | 空。用于 `bool` 分支 |
| `bool` | `must → should → must_not → filter` |
| `constant_score` | 用固定分数包住一个 filter |
| `dis_max` | 取各分支的最大分 |
| `boosting` | 正分支正常、负分支降权 |
| `type` | 遗留 mapping-types 键。每个文档都是 `_doc`，因此退化为 `match_all` |

### Term 级（10）

`term`（精确值 keyword 匹配）、`terms`（多值 OR）、`terms_set`（带每查询最小 should 匹配数的 terms）、`range`（数值/日期范围）、`prefix`、`wildcard`（glob）、`regexp`、`fuzzy`（编辑距离）、`exists`（字段有非空值）、`ids`（按 id 取文档）。

### 全文类（9）

`match`（经分析器）、`match_phrase`（带位置）、`match_phrase_prefix`、`match_bool_prefix`（末 token 变 prefix，其余 term，包在 bool should 下）、`multi_match`（跨字段）、`combined_fields`（**由 `multi_match` 的 `cross_fields` 近似**，没有 ES 的词频统计汇聚）、`query_string`（Lucene 风格 mini-DSL）、`simple_query_string`（面向终端用户输入的安全子集）、`intervals`（规则树，match/prefix/wildcard/all_of/any_of，**下落到标准查询，区间边界不被建模**）。

### Span（7）

`span_term`（位置锚点）、`span_near`（N 个位置内）、`span_or`、`span_not`（span 窗口内的排除）、`span_first`（锚定字段开头）、`span_containing`（大 span 包含小 span）、`span_within`（小 span 被大 span 包含）。

### AI 原生（3）

| 查询 | 说明 |
|---|---|
| `knn` | 向量 k-NN；未过滤走 HNSW（精确重打分），过滤走精确扫描 |
| `semantic` | 查询时嵌入查询文本，检索向量字段 |
| `hybrid` | RRF / 线性融合 |

### 地理（4）

`geo_distance`、`geo_bounding_box`、`geo_polygon`、`geo_shape`（envelope / shape 关系）。

### 打分与脚本（6）

`function_score`（用函数改写分数）、`script_score`（Painless 脚本取代 BM25 分）、`script`（Painless 谓词当 filter）、`rank_feature`（对数值特征字段做 log1p 提升，经 `function_score`）、`distance_feature`（邻近度提升，下落到 `function_score` 的 `field_value_factor`；**ES 的精确衰减曲线未被复现**）、`pinned`（把特定文档顶到前面）。

### 专用（4）

`nested`（按嵌套字段逐元素求值；**`score_mode` 与 `inner_hits` 不被支持**）、`more_like_this`（按文本指纹找相似文档）、`percolate`（存储的查询对内联文档匹配；**index/id 形式被 400 拒绝**）、`wrapper`（base64 编码的查询 JSON）。

### 被识别并显式拒绝（2）

| 查询 | 行为 |
|---|---|
| `has_child` | 解析期 400 |
| `has_parent` | 解析期 400 |

理由（F-210）：XERJ **从不做父子连接物化**。若让这类查询跑起来，它会匹配扁平文档并**静默返回错误的命中**。因此这两个键被识别，只为给出**具体的 400** 而不是笼统的「未知查询类型」。

> **可迁移的方法论**：把「不打算实现」变成一个**专属错误**，比让它落进通用错误路径更有价值——前者告诉调用方「这个语义我们不做，且原因是 X」，后者只说「不认识」。

### 一处需要知道的文档漂移

站点导航栏的摘要写 "Query types · **32** variants · one planner"，而同页正文列出 50 个、源码的 `SUPPORTED_QUERY_TYPES` 也是 50 个（F-212、F-209）。**以代码与正文为准**。

## 聚合：62 种，桶路径精确

聚合类型由 `xerj_engine::aggs::SUPPORTED_AGG_TYPES` 生成并由测试锁定（F-211）。家族与数量：**metric 19 种、bucket 28 种、pipeline 15 种，合计 62 种**（家族划分已与源码清单逐项比对，无遗漏无多余）。

### 精确性的边界

**每个桶聚合返回精确计数**，没有 HLL 近似（F-213）。唯一的例外是**采样家族**（F-214）：

| 聚合 | 行为 |
|---|---|
| `sampler` | 按 `_score` 截断到前 `shard_size` 条匹配文档（默认 200），子聚合只看到该切片 |
| `diversified_sampler` | 同样的截断，外加「共享同一字段值的文档数」上限 `max_docs_per_value`（默认 1） |
| `random_sampler` | 共用 sampler 实现，同样是「按 `_score` 的前若干条」切片；**ES 的 probability 参数不被读取** |

### 两条快速路径

**列式直方图**（F-215）：索引活文档超过 **10,000** 后，`terms` 及其他列式可用聚合改读 **doc-values ordinal 直方图**（`fast_aggs.rs`），而不是扫描倒排。低于该阈值走 JSON 路径，文档称其为**参考实现**。

这解释了为什么 XERJ 在「百万级事件上的 top-N」这类查询上能给出亚秒级结果——它根本不在扫倒排。

**精确基数**（F-217）：`cardinality` 是精确的——每个不同值都进哈希集合，**内存随基数增长**。

### 百分位

`percentiles` 默认在排序值上做**线性插值**；`hdr` 选项切到 **HdrHistogram 最近秩**（F-216）。两者精度特性不同：线性插值平滑但可能低估尾部分位；HdrHistogram 秩精确但分辨率受桶宽限制。

### Pipeline 家族在第二遍计算

Pipeline 聚合（`avg_bucket`、`max_bucket`、`min_bucket`、`sum_bucket`、`stats_bucket`、`extended_stats_bucket`、`percentiles_bucket`、`derivative`、`cumulative_sum`、`moving_avg`、`moving_fn`、`serial_diff`、`bucket_script`、`bucket_selector`、`bucket_sort`）在**上面那些聚合产出的桶树上再跑一遍**，因此它们取的是 `buckets_path` 而不是字段。

## 请求形状

```json
{
  "query": { "match_all": {} },
  "aggs": {
    "by_service": {
      "terms": { "field": "service", "size": 10 },
      "aggs": {
        "p95_latency": {
          "percentiles": { "field": "latency_ms", "percents": [50, 95, 99] }
        }
      }
    }
  },
  "size": 0
}
```

`size: 0` 是纯聚合请求的标准写法，它同时走上文的列式快速路径（见 [04 检索路径与响应裁剪](/concepts/04-search-query-path.md)）。

## 与 ES 的语义差异（查询面）

| 差异 | 说明 |
|---|---|
| BM25 分数 | XERJ 自己的。排序顺序符合查询意图，但精确 `_score` 浮点与 ES 不同，且会随后台合并移动 collection statistics 而对同一查询发生位移——与两个 ES 次版本之间的内部差异同类（F-325）。**放宽断言精确分数的测试** |
| `_cat/indices?v` | 只输出数据行，**没有列头行**；列顺序与 ES 相同，故按位置解析可用、按表头解析不可用（F-326） |
| 未支持的调用 | 返回结构化 `not_supported_yet` 错误而不是 500（F-327） |
| `PUT /:index/_mapping` | 只允许追加（F-328） |

## 不在查询面里的东西

官方文档明确列出需要重写的几项（F-324）：

| 能力 | 状态 | 替代 |
|---|---|---|
| Painless 脚本 / 脚本化度量 | **未实现** | 用 `function_score` 覆盖它能覆盖的场景 |
| Runtime fields | 不支持 | 在摄入期或查询期算好 |
| 跨集群搜索 | v0.1 是单集群 | — |
| ML 作业 | 不是特性 | — |
| Watcher / 告警框架 | 不提供 | 用 `/v1/explain-plan` 端点 + 外部规则运行器 |
| ILM | 不执行，也没有保留作业 | `[logs] retention_days` 被接受但未接线；自己按计划删索引或用 `_delete_by_query` |

> 注意 `script` 与 `script_score` **在查询类型列表里**（打分类 6 种），但「脚本化度量」被列为需重写。两者不是一回事：查询侧的 Painless 谓词与分数替换存在，**聚合侧的脚本化度量**才是未实现的部分。

## 相关概念

- [04 检索路径与响应裁剪](/concepts/04-search-query-path.md)：查询执行链路与 `_passage`
- [07 ES 兼容与基准诚实性](/concepts/07-es-compat-and-benchmarks.md)：一致性门禁与记分卡
- [09 查询类型与聚合](/concepts/09-query-types-and-aggregations.md)：本文
- 事实来源：[第二轮事实清单](/references/facts-docs.md)
- 架构洞察：[第二轮洞察](/references/insights-docs.md)
