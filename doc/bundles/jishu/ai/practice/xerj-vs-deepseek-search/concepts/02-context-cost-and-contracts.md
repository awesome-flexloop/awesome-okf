---
type: Concept
title: 上下文成本与接口契约
description: 两种「先摘要后全文」的实现对照——XERJ 的 _passage 切片与 _source 投影 vs DeepSeek 的 snippet/summary/content 三档分层，含各自的默认值陷阱与选型建议
tags: [xerj, deepseek, 上下文成本, token 预算, 接口契约]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: compare-facts
    resource: /references/facts.md
    title: 对比事实清单
  - id: xerj-bundle
    resource: ../../frameworks/xerj/index.md
    title: XERJ 源码学习知识包
---

# 上下文成本与接口契约

在 Agent 语境里，「检索」的成本几乎从来不是查询本身，而是**被塞进上下文的结果**。两侧对此的解法是同一个思想的两种实现（F-035）。

## 同一思想：先摘要，按需全文

### XERJ：服务端切片 + 客户端投影

```json
POST /ax-code/_search
{
  "fields": ["_passage"],
  "_source": ["title", "ax_path"],
  "query": { "match": { "body": "rotate WAL segment" } },
  "size": 5
}
```

- `_passage` 是**伪字段**，返回从原字段切片出的匹配片段：`{field, ordinal, start_offset, end_offset, text, page?}`（F-004）；
- `_source` 投影裁掉其余字段；
- 实测：5 个命中覆盖索引后的源码文件，默认完整文档 **416,630 字节** → 加 `_passage` + 投影后 **12,122 字节**，**34 倍**缩减（F-004）。

### DeepSeek：结果字段天然分层

Search 响应的三个文本字段是**按消费者分层**的（F-021、F-024）：

| 字段 | 量级 | 官方定位 | 建议用法 |
|---|---|---|---|
| `snippet` | 100～200 字符 | 适用于前端展现 | 渲染结果列表 |
| `summary` | 600～800 字符 | **适用于给模型阅读** | 直接拼进上下文 / RAG 片段 |
| `content` | 完整正文 | — | `need_content: true` 开启，或对选中 URL 二次 Fetch |

默认 `need_content: false` 时 `content` **恒为空字符串**（F-019、F-024）。

## 三个默认值陷阱

### 陷阱 1：XERJ 默认返回完整文档

DeepSeek 的默认值更保守（不返回正文），XERJ 的默认值更激进（返回全文）（F-035）。**后果是不对称的**：

- DeepSeek 侧忘记开 `need_content` → 拿到的是摘要，安全但信息少；
- XERJ 侧忘记加 `_passage` → 拿到的是几百 KB 全文，**上下文当场爆掉**。

XERJ 对此有一层补偿：当 `_source` 未投影且未请求 `_passage` 时，响应会在 `_xerj.hints` 里**直接给出改好的请求**（F-006）。但那是事后补救，不是默认值。

> **行动**：在 XERJ 侧，把 `"fields": ["_passage"]` + `_source` 投影写进**每一个** `_search` 的模板里，不要靠每次记得加。

### 陷阱 2：`count` 与 `size` 的语义陷阱

DeepSeek 的 `count`（1～50，默认 10）控制返回条数，**不影响价格**（F-028）；XERJ 的 `size` 控制物化上界（`from + size` 个候选，F-002 侧的引擎行为）。

但真正会咬人的是 XERJ 的 **scroll 上限**：`POST /{index}/_search?scroll=` 的快照窗口是 **10,000** 文档，超出直接 **400**（F-008）——不是静默截断。DeepSeek 侧没有对应概念（它的 `count` 上限是 50）。

### 陷阱 3：`_passage` 与混合查询不兼容

`_passage` 在混合检索（`hybrid` / 多 kNN 融合）下会被拒（400 并指名修法）。所以「用混合检索」与「只要片段」这两个优化在 XERJ 侧不能同时要。

## 两侧都没有的东西

**没有一个接口直接返回「这个问题的答案」**。两侧都返回**证据**，让模型自己读：

- XERJ 返回带 `file:line` 的片段与符号定义——它甚至提供 `xerj def`（跳转到定义，返回 file:line + 签名）和 `xerj code`（返回匹配到的**定义**而非字节窗口）；
- DeepSeek 返回带 `url` 的摘要与正文。

这个共同点是重要的：它决定了**上层的成本优化策略是相似的**——减少塞进上下文的证据量，而不是改变检索算法。

## 成本换算：把两侧放到同一张表

| | XERJ | DeepSeek |
|---|---|---|
| 一次「宽结果」的上下文量 | 默认 ~416 KB（源码语料 5 命中）；裁剪后 ~12 KB（F-004） | `summary` 600～800 字符/条 × `count`（默认 10）≈ 6～8 K 字符；开 `content` 则为全文（F-021） |
| 计费维度 | 无按次费（F-010） | ¥0.005/次，与 `count` 无关（F-028） |
| 成本随结果条数 | 线性（每条都进上下文） | 线性（每条都进上下文），但**计费不随之增加** |

> **反常识**：DeepSeek 侧 `count` 从 10 调到 50，**价格不变但上下文成本 ×5**。它省的是「按结果条数计费」的钱，不是「上下文」的钱。XERJ 侧则连计费维度都没有——成本全部在上下文侧与机器侧。

## 选型建议

| 场景 | 做法 |
|---|---|
| 源码/长文档语料 | XERJ：**必须**加 `_passage` + `_source` 投影 |
| 公网检索 | DeepSeek：默认 `need_content: false` + 只用 `summary`；需要全文时**先 Fetch 选中的少数 URL**，而不是开 `need_content: true` 拉全部正文 |
| 混合场景 | 走「Search 定位 → Fetch 取回 → 落本地索引 → 之后本地查」，把重复的公网内容一次性固化 |
| 上下文预算紧张 | 两侧同一招：**降低结果条数**（`count` / `size`），而不是缩短摘要——DeepSeek 的 `summary` 长度是引擎定的，改不了 |

## 相关概念

- [00 对比框架与结论](00-comparison-frame.md)：九个对照轴
- [03 失败语义与可诊断性](03-failure-semantics-and-boundaries.md)：错误码作为契约
- [04 成本曲线与选型](04-cost-model-and-selection.md)：决策树
- [XERJ 04 检索路径与响应裁剪](../../../frameworks/xerj/concepts/04-search-query-path.md)：`_passage` 与 `_xerj.hints` 细节
- 事实来源：[对比事实清单](/references/facts.md)
