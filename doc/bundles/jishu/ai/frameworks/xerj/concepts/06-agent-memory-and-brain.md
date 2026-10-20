---
type: Concept
title: 智能体记忆与第二大脑
description: XERJ 的三层连续性设施——命名空间长期记忆 /_memory、基于文档的关系层第二大脑 /_graph（9 个确定性检测器）、以及确定性规划器 /_ask 与类型化判断 /_decide
tags: [xerj, 记忆, 第二大脑, 知识图谱, 规划器]
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

# 智能体记忆与第二大脑

经典搜索引擎解决不了「连续性」问题：一个智能体在本次会话里学到的东西，如何在下次会话被按意义召回，且不需要另起一个向量库和一个嵌入服务。XERJ 用三层设施回答它——**命名空间记忆**、**关系层第二大脑**、**确定性规划与判断**。

## 第一层：`/_memory` 命名空间记忆

### 写入

```
POST /_memory/{namespace}
{
  "text": "user prefers dark mode",
  "metadata": { "source": "chat", "topic": "ui" },
  "id": "opt-001",              // 可选
  "vector": [/* 可选 */],        // 可选，自带向量则跳过嵌入
  "dedup": true,                // 可选
  "dedup_threshold": 0.95       // 可选
}
```

文本自动嵌入，命名空间互相隔离（F-127）。命名空间是「私域隔离」的单位——上游文档专门有一条讲「如何让一台笔记本上的两个智能体各有私域记忆」。

### 召回

```
POST /_memory/{namespace}/_recall
{
  "query": "what UI theme?",
  "semantic": true,
  "k": 5,
  "filter": { /* 可选 */ },
  "recency_weight": 0.2         // 可选
}
```

召回模式**按序尝试**（F-129）：

| 优先级 | 模式 | 说明 |
|---|---|---|
| 1 | 显式 `vector` kNN | 调用方自带向量 |
| 2 | `hybrid: true` | BM25 + 服务端语义，按倒数排名融合；`fusion:"linear"` 可选 |
| 3 | `semantic: true` | 服务端嵌入查询文本 |
| 4 | 纯 `query` 文本 | BM25 |

这个顺序是有意义的：**从最确定的信号逐步退到最模糊的**。调用方有向量时用它；没有则先试词法+语义；再退到纯 BM25。`recency_weight` 提供新近度混合——智能体的记忆里，「最近提到的偏好」往往比「三个月前的事实」更相关。

> **注意嵌入器继承性**：`/_memory` 召回的**语义模式走精确扫描**（F-125），并且用的是**写入时那个后端**的嵌入（F-106）。若节点在词法模式下写入了记忆，召回时不会突然变成神经语义。

## 第二层：`/_graph` 第二大脑

### 它不是什么

这一节最重要，因为它划清了边界（F-133）：

> 第二大脑是**已有文档之上的关系层**。它**不是图数据库**：没有查询语言、没有最短路径、没有 PageRank、没有无界遍历。边就是普通的 XERJ 文档，遍历是**有界的、批量的、列式读取，每次调用最多两跳**。

这三个「没有」是刻意设计，不是未完成。

### 构成

一个脑由**一个名字 + 两个保留索引**派生（F-134）：

| 角色 | 索引名 | 来源 |
|---|---|---|
| 边 | `.xerj-memory-{brain}-edges` | `authz::brain_edges_index` |
| 节点（默认） | `.xerj-memory-{brain}` | `authz::memory_namespace_index` |

保留前缀 `.xerj-memory-` 与智能体记忆 API 用的命名空间相同，因此**一个脑的默认节点索引就是同名的记忆命名空间**（F-135）——两条设施在存储层合流。

节点只是文档。图层从不解释节点内容，只把它们的 id 存成 `src` 与 `dst` 字符串。**任何有文档 id 的东西都能当节点**，包括记忆条目和 autoindex 的段落文档。

边也是普通文档，走正常写入路径（WAL → memtable → segment → doc values），所以重放、flush、合并、快照对它都免费可用（F-136 上下文）。

### 边的映射

| 字段 | 类型 |
|---|---|
| `edge_id`、`src`、`dst`、`type`、`detector`、`src_file`、`src_format`、`dst_format` | `keyword` |
| `weight`、`confidence` | `float` |
| `valid_at`、`invalid_at`、`created_at`、`expired_at` | `date`，格式 `epoch_millis` |
| `schema_version` | `integer` |
| `evidence.quote` | `text` |
| `evidence.source` | `keyword` |
| `evidence.offset` | `long` |

时间戳以 epoch 毫秒数字存储，**从不存 ISO 字符串**（F-136）。每条边都带**产生它的原文引用**（`evidence.quote`），这让「为什么这两者有关系」可被人或智能体复核。

### 边的身份是派生的

```
edge_id = xxh3_128("xg1\0" src "\0" type "\0" dst "\0" decimal(valid_at_ms))
```

渲染为 32 位小写十六进制（F-137）。两个写入方（HTTP handler 与 autoindex 检测器管线）**钉死同一个函数**。

后果（F-137、F-138）：

- 同一 `(src, type, dst, valid_at)` 产生同一文档 id，**重复断言一条边是覆盖而非重复**；
- 对未变语料重跑检测器**收敛**而不是增长；
- 边被**软失效**而非删除，所以「上周二它相信什么」仍可回答。

### 9 个确定性检测器

`default_detectors()` 注册 **9** 个检测器（F-139、F-140）：

| 检测器 | 标签 | 检测什么 |
|---|---|---|
| wikilink | `wikilink@2` | Obsidian 风格 `[[wiki 链接]]` |
| mdlink | `mdlink@2` | `[text](relative/path.md)` 指向语料内文件 |
| href | `href@2` | `<a href="…">`，仅对 HTML 抽取后的文件 |
| pathcite | `pathcite@1` | 散文里提到的文件路径（``see `src/index.rs:123` ``） |
| cratecite | `cratecite@1` | 散文里提到的 crate 目录名（`BM25 (xerj-fts)`） |
| sequence | `sequence@2` | 文件卡片开启链，每个段落依次相接 |
| samedir | `samedir@2` | 同目录文件，**成链不成团**（避免团块） |
| sharedterm | `sharedterm@1` | 两文档使用同一 distinctive 词汇 |
| emailthread | `email-thread@1` | 一个检测器对应两种边：`replies_to` 与 `attachment_of`（F-142） |

### 为什么是确定性而不是 LLM

源码注释给出了理由（F-141）：

> 同一语料必须在每次运行中产出**逐字节相同**的边集（mtime 不变时），因为边身份——进而幂等重跑、kill -9 安全、双时态历史——都挂在 `(src, type, dst, valid_at)` 的内容哈希上。**把模型放进这个循环，会让每次重跑都变成一套新的信念。**

每条发出的边都带着**教给它的那句原文**和一个版本化标签（`detector: "wikilink@2"`）；任何行为变更都要 bump `@N`，这样旧边仍可归因到产生它们的规则。

> **这是本项目里最值得抄的一条设计**：把「不确定性」挡在需要幂等与可追溯的层之外。关系抽取可以是规则的，因为关系的**身份**必须是确定的。

### 脑名的校验

非空、长度 ≤ 200、首字符为小写字母或数字、其余字符限于 `a-z 0-9 _ - .`、不含 `..`、**不得以 `-edges` 结尾**（否则名为 `kb-edges` 的脑会与名为 `kb` 的脑的边索引冲突）（F-144）。

### 建脑

```sh
xerj autoindex <folder> --brain <NAME>
xerj brain <folder> [--brain <NAME>]
```

`--no-graph` 跳过关系检测。

## 第三层：`/_ask` 确定性规划器

```
POST /_ask
{ "index": "ax-orders", "prompt": "orders over 100 in 2026" }
→ { "query": {…}, "plan": [ … ], "confidence": …, "indices": [ … ] }
```

- 输入自然语言过滤条件，输出**经过校验的**查询 DSL（F-130）；
- **确定性规则引擎，不是 LLM**（F-131）；
- 无法在索引中落地的短语返回 **422** 并**指名该短语**，**从不猜测**（F-131）；
- 返回的每个查询**都已通过节点自身的解析器**（F-132）——可直接放进 `_search` 正文。

对智能体而言这是一个极划算的能力：「把自然语言条件变成可执行查询」不需要额外一次模型调用，也不需要智能体自己猜字段名。它对应 MCP 的 `xerj_plan` 工具。

## 第四层：`/_decide` 类型化判断

```
POST /v1/systemone   （原生 REST 端口，= --port + 1）
POST /_decide         （ES 兼容端口）
```

输入问题与一个已标注的历史索引，XERJ **在本地**用「带标签历史索引上的秩加权投票」给出类型化答案（F-145）：

- `noul`：0–1 概率；
- `choice`：各选项的概率。

三个刻意的偏离（F-146）：

- `model` 字段回显 `xerj-history-vote-1`，**绝不是** Jev 模型名——它不是 Jev；
- **零标注支持的问题是 422 并指名 ids**，不伪造 0.5；
- `/_decide` 额外返回**证据**：带标签的邻居、引擎分数、权重。

实测（F-147）：AG News（12 万条带标签样本）上准确率 **0.9182**，覆盖全部 7,600 条测试项，`/v1/systemone` 每项 **p50 42.7 ms**。

这解决了「不调用 LLM 也能做分类/路由」的需求：拿已标注的样例（已标为垃圾/非垃圾的消息）做最近邻投票，答案不出本机。

## 三层设施怎么配合

```
写入：  /_memory/{ns}            存一条记忆
         ↓
关系：  autoindex --brain NAME   在语料里检出关系边（确定性）
         ↓
召回：  /_memory/{ns}/_recall    按意义/词法召回记忆
         /_graph/{brain}/ego     展开某个节点的证据化邻域（最多两跳）
         ↓
行动：  /_ask                    自然语言 → 可执行查询
         /_decide                问题 → 类型化判断
```

`xerj_brain_ego` 是其中最实用的一个：它给出**一个节点的双时态、证据支撑的邻域**（F-076、F-133）——既有当前有效的边，也有被软失效的旧边，带产生它们的原文。

## 相关概念

- [00 整体架构](/concepts/00-overview.md)：`xerj-ai` 与 `xerj-ai` 之外的角色
- [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md)：记忆与 brain 的 MCP 工具
- [05 向量、嵌入与混合检索](/concepts/05-vector-and-hybrid.md)：召回用到的嵌入与扫描路径
- [07 ES 兼容与基准诚实性](/concepts/07-es-compat-and-benchmarks.md)：能力边界与未实现清单
- 事实来源：[事实清单](/references/facts.md)
