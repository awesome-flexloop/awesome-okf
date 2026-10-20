---
type: Concept
title: 检索路径与响应裁剪
description: XERJ 的查询执行链路（解析→AST→执行器）、memtable 与 segment 的双路合并、_passage 伪字段与 _xerj.hints 提示、未知字段的严格模式
tags: [xerj, 检索, 查询, _passage, 裁剪, 提示]
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

# 检索路径与响应裁剪

本篇讲两件事：**查询怎么走**（引擎内部）与**结果怎么裁**（返回给智能体的响应）。后者往往才是 token 预算的真正去向。

## 查询执行链路

一个搜索请求自前向后经过四个 crate（F-078）：

```
POST /{index}/_search
  → xerj-api      Axum handler（es_compat.rs）
  → xerj-query    parse_request()：ES JSON → SearchRequest（QueryNode 树）
  → xerj-engine   Engine::get_index() 定位命名索引
  → xerj-engine   Index::search()
       ├─ memtable scan        内存 BM25（ShardedFtsMemtable）
       ├─ segment scan         磁盘 FTS（FtsIndexReader + BM25）
       ├─ doc_matches_query()  term 级 / geo 谓词求值
       ├─ run_aggs()           聚合管线（size:0 走列式快速路径）
       └─ apply_source_filter()、apply_highlight()
  → SearchResult → JSON
```

查询 DSL 的解析器在 `xerj-query/src/parser.rs`（6,634 行），AST 在 `xerj-query/src/ast.rs`（1,380 行），另有规划器（`planner.rs`）、重写器（`rewriter.rs`）、执行器（`executor.rs`）与排序（`sort.rs`）。

### 两条关键性质

**一、memtable 与 segment 双路匹配后合并**（F-079）。新写入的文档此刻还在 memtable 里，因此立即可检索，不必等 flush。这是「刚写完就能查到」的实现基础。

**二、命中物化有上界**（F-080）：`size > 0` 时只物化前 `from + size` 个候选，不会为整条结果集分配内存。

### 聚合的列式快速路径

`size:0` 请求（即只取聚合、不取文档）走列式快速路径（F-081）。这正是 AI 智能体最常问的问题类型——计数、基数、直方图、百分位——所对应的执行路径，也是 XERJ 在对拍中相对 Elasticsearch 占优的部分（`docs/WHY_XERJ.md:44-48`）。

## 摄取路径回顾

```
PUT /{index}/_doc/{id}   或   POST /_bulk
  → xerj-api → xerj-engine → xerj-storage（IndexStore）
       ├─ WAL append        分片 Mutex<WalWriter> + 全局 AtomicU64 seq_no
       ├─ storage memtable  向上取整到 2 的幂的哈希分区
       ├─ FTS memtable      engine.ingest_shards 哈希分区
       ├─ flush             按分片 fan-out，写不可变 segment（含 FTS / doc-values 边车）
       └─ merge             后台合并压实；_forcemerge 同步且静默
```

分片数是三个独立域（F-083、F-084），重启时 `IndexStore::open()` 与 `WalReader::replay()` 分别重放 WAL 进存储 memtable 与 FTS memtable，`doc_count = segments + memtable`（F-085）。

## 响应裁剪：`_passage` 是检索的正确姿势

这是本篇最重要的一节。

**默认 `_search` 返回完整文档**（F-087）。上游给出的实测：

| 做法 | 5 个命中覆盖索引后的源码文件 |
|---|---:|
| 默认（完整 `_source`） | **416,630 字节** |
| 加 `"fields":["_passage"]` + 投影 `_source` | **12,122 字节** |

**缩减 34 倍**（F-087）。

> **反常识**：智能体的 token 预算主要不是被「查询」吃掉的，而是被「返回的文档」吃掉的。对源码类语料，一个默认响应就是几百 KB 起步。而 `xerj code` 的实测中，grep 式 agent 最多拉入 1.06M 输入 token（F-206）——差别就在这里。

### `_passage` 伪字段

`_passage` 返回匹配片段而非整篇文档（F-088）：

```json
{ "field": "body", "ordinal": 12, "start_offset": 4810, "end_offset": 5233, "text": "…", "page": 3 }
```

它是**从原始字段切片**出来的，因此与源内容严格一致。

三个关于 `_passage` 的纪律：

1. **它是 opt-in 的**，不出现在任何 `_mapping` 或默认响应里（F-089）；
2. 当 `_source` 未投影且未请求 `_passage` 时，响应会**自己说出**应该怎么改——一条 `_xerj.hints` 条目携带一份开箱即用的修正请求（F-089）；
3. `_xerj.hints` 是**追加式**的，不落在 `hits`/`total`/`_score` 内，因此既有 ES 客户端不受影响（F-091）。

判定「请求字段里是否含 `_passage`」的函数是 `fields_request_includes_passage()`（F-090）。

### 推荐的查询形态

```json
POST /ax-code/_search
{
  "fields": ["_passage"],
  "_source": ["title", "ax_path"],
  "query": { "match": { "body": "rotate WAL segment" } },
  "size": 5
}
```

注意 `_passage` 与 `hybrid` / 多 kNN 融合不兼容：混合查询下请求 `_passage` 会 400 并指名修法（F-087 相关说明，`landing/llms.txt:71`）。

### 向量字段默认不出现在 `_source` 里

默认 `_search` 省略引擎生成的 `<field>_vector` 与 `<field>_vector_chunks` 伴随字段，需要时显式 `"_source": true`（F-086）。这是一个好默认：向量是引擎的内部产物，默认吐出来纯属浪费带宽。

## 未知字段：一个刻意的「更严格」偏离

ES 的行为是：对未映射字段的查找返回 **0 命中**。智能体无法区分「字段名写错了」和「语料真的没有」——上游测量过：30 个智能体意图中有 5 个静默搜索了错误的字段名（F-092）。

XERJ 的处理分两层：

| 索引类型 | 行为 |
|---|---|
| 普通索引 | 保持 ES 行为（0 命中），但响应附带 `_xerj.hints` 的 `unknown_field` 条目，指名不存在的字段与实际存在的字段 |
| `ax-*`（autoindex 创建） | **400**，报出字段名与可检索字段 |

autoindex 创建的索引带有完整显式 schema，所以那里可以放心严格（F-092）。在严格模式下，下列查询会触发 400：`term`、`terms`、`match`、`match_phrase`、`match_phrase_prefix`、`prefix`、`wildcard`、`regexp`、`fuzzy`、`range`，以及 `multi_match` 且其 `fields` **全部**未映射（F-092）。**半真**的 `multi_match` 仍会搜索真实字段，只是带一条提示。

严格模式可以按请求开（`?strict_unknown_fields=true`）或按索引开（`index.query.strict_unknown_fields=true`），一个严格目标即可覆盖整个请求；`?strict_unknown_fields=false` 可让单次请求退出严格模式（F-093）。

两个豁免（F-093）：

- `exists` 查询在未映射字段上仍是**真实的 0 命中**（这是正确语义，不是错误）；
- 刚创建、还没有 mappings 的索引**不被校验**。

## `_source` 投影

投影是另一半的节省手段，与 `_passage` 配合使用：

```json
"_source": ["title", "ax_path"]     // 只要几个字段
"_source": false                    // 或完全不要
```

对源码语料，`ax_path` + `_passage` 通常已经足够回答「在哪个文件哪一段」。

## 兼容性边界：scroll 不是游标

**scroll 是有界的前置快照**，不是逐 segment 行走的游标（F-153）：精确总数超出快照窗口的查询被**拒绝为 400**，而不是静默截断。任意大小的结果集应使用 `search_after`。

这个设计是诚实的：静默截断会让人以为拿到了全部数据，而 400 至少是明说的。

## 与 `highlight` 的一个坑

`xerj code` 从不请求 `highlight`：在本引擎上 highlight 块会改变 `_score` 并重排命中（issue #177）——同一查询，top-1 命中在无 highlight 时是 6/6，有 highlight 时是 1/6（F-184）。由于段落已改从 `symbols[]` 取得，highlight 不再带来任何收益，只带来排序损失。

> 这是「加一个看起来更友好的功能，结果改变了排序」的一类典型副作用。检索类系统里，任何参与打分的环节都是排序语义的一部分。

## 相关概念

- [00 整体架构](/concepts/00-overview.md)：整体 crate 图
- [02 autoindex 零配置流水线](/concepts/02-autoindex-pipeline.md)：数据集与字段从哪来
- [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md)：五个检索工具的入口
- [05 向量、嵌入与混合检索](/concepts/05-vector-and-hybrid.md)：`knn` 与 `hybrid` 的执行细节
- [07 ES 兼容与基准诚实性](/concepts/07-es-compat-and-benchmarks.md)：一致性门禁与记分卡
- 事实来源：[事实清单](/references/facts.md)
