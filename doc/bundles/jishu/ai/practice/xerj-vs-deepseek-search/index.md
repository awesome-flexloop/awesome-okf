---
okf_version: "0.2"
title: XERJ × DeepSeek Search/Fetch 对比
description: XERJ 自建本地检索栈与 DeepSeek 托管搜索 API 的九轴对比——语料归属是第一决策轴、上下文成本的两套实现、失败语义的可诊断性差距、成本曲线与选型决策树
---

# XERJ × DeepSeek Search/Fetch 对比

## 结论先行

**XERJ 与 DeepSeek Search/Fetch 不是竞品，而是语料两端。**

它们的检索面几乎不重叠：

| | XERJ | DeepSeek Search / Fetch |
|---|---|---|
| 语料 | **你的**：本地文件、代码库、日志、邮件、PDF、长期记忆 | **公网的**：实时网页 |
| 形态 | 自建、本地、一个静态二进制 61.6 MB | 托管 API，`api.deepseek.com` |
| 记忆 | 命名空间记忆 + 第二大脑 | 无状态 |
| 成本 | 固定成本，边际近零 | ¥0.005/次成功请求，重复查询照收 |
| 隐私 | 默认不出机器 | 检索词与目标 URL 必然出网 |

所以「选 XERJ 还是选 DeepSeek 搜索」这个问题**提错了**。正确的问题是：**「要检索的东西归谁」**。

## 本束内容

### 概念文档（5 篇）

- [00 对比框架与结论](concepts/00-comparison-frame.md) — 九个对照轴、三个根本差异与总表
- [01 语料归属](concepts/01-corpus-ownership.md) — 第一决策轴；四类不可互换的问题；归属判定的三个问题
- [02 上下文成本与接口契约](concepts/02-context-cost-and-contracts.md) — 「先摘要后全文」的两种实现与三个默认值陷阱
- [03 失败语义与可诊断性](concepts/03-failure-semantics-and-boundaries.md) — 边界编码进响应体 vs 404 五因合并；边界探测清单
- [04 成本曲线与选型](concepts/04-cost-model-and-selection.md) — 固定 vs 线性成本、深研型量级、选型决策树与组合架构

### 示例（1 篇）

- [01 组合检索回路实战](examples/01-composed-retrieval-pipeline.md) — 一个同时含「内部日志 + 公网最新文档」的任务的完整回路、成本账与失败处理速查表

### 参考资料（3 篇）

- [信源登记](references/source.md) — 三类信源、采信规则与 DeepSeek 侧 13 项逐条复核表
- [事实清单](references/facts.md) — 42 条编号事实，分 XERJ 侧 / DeepSeek 侧 / 对照三组
- [核验记录](references/verification.md) — 核验方法、未核验项与缺失性断言、引用纪律、门禁记录

## 三条使用建议

**① 按语料归属选，不按检索能力选。** 问「我们内部昨晚那次 CI 失败日志里写了什么」——DeepSeek 结构上做不到；问「今天 Rust 发布了什么新特性」——XERJ 结构上做不到。

**② 高频重复的查询走自建，低频时效性的查询走托管。** DeepSeek 的按次计费结构会惩罚重复查询；XERJ 的边际成本近乎零。

**③ 两者可以串联。** Search 定位 → Fetch 取正文 → 写入 XERJ 索引 → 之后本地查。一次性付费，多次命中。

## 引用边界

- 本束的 DeepSeek 侧事实**逐条复核自在线官方文档**（`https://api-docs.deepseek.com/zh-cn/guides/search`）；
- XERJ 侧事实**跨束引用** [XERJ 源码学习知识包](../../frameworks/xerj/index.md) 的编号事实，不重复采集；
- 事实 F-033 与 F-040 是**对照推论与架构建议**，不是任一方的官方立场；
- 本束**不含**跨引擎的同语料召回对比实验，任何此类数字都不应从本束引用。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
