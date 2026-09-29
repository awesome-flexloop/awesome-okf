---
okf_version: "0.2"
type: Concept
title: "Memory Tree 与 TokenJuice：记忆机制与上下文压缩"
description: "Memory Tree 官方管线——≤3k分块、打分、source/topic/global三棵摘要树、作业队列与leaf生命周期、SQLite+Obsidian vault、20分钟auto-fetch；10亿token口径勘误；TokenJuice七阶段压缩路由器与博文测算边界"
tags: [Memory Tree, NeoCortex, TokenJuice, Obsidian, SQLite, RAG, 上下文压缩, auto-fetch]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-16T20:30:00+08:00" }
verified: { by: "process:blog-article-to-okf-wiki-v", at: "2026-09-16T20:30:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ
    title: 开源先驱博文（2026-07-28）
  - id: gitbook-memory
    url: https://tinyhumans.gitbook.io/openhuman/features/memory-tree
    title: 官方文档 Memory Tree
  - id: gitbook-compression
    url: https://tinyhumans.gitbook.io/openhuman/features/token-compression
    title: 官方文档 Smart Token Compression
---

# Memory Tree 与 TokenJuice：记忆机制与上下文压缩

> **勘误提示**：博文主打数字"Memory Tree 容量可达 10 亿 token"**未见于任何官方文档**，仅出自一个 AI 生成的第三方知识库（F-052）。本文机制描述以官方 GitBook 为准（F-051），容量数字仅作弱源单源标注，请勿当作官方规格引用。

## 一、Memory Tree 是什么（官方机制）

官方定义：Memory Tree 是 OpenHuman 的本地优先知识库——"It is not a vector database with a thin 'memory' wrapper. It is a deterministic, bucket-sealed pipeline"，把聊天、邮件、文档、集成同步结果这股"混乱的日流"变成机器上可查询、有摘要支撑的结构化 Markdown（F-051）。

博文的六步通俗版（F-018：拉取 → ≤3,000 token Markdown 块 → 打分 → per-source/per-topic/per-day 摘要树 → SQLite + Obsidian → 20 分钟增量）方向正确，官方管线更细：

```
source adapters（chat / email / document）
   → canonicalize        规范化 Markdown + provenance 元数据
   → chunker              确定性 ID、≤3k-token 有界分块（内容寻址，重复输入不产生重复块）
   → content_store        原子 .md 文件落盘（body + tags）
   → store                SQLite 持久化（chunks / scores / summaries / jobs，单事务写入）
   → score                信号 + embeddings + 实体抽取（重活在后台 worker）
   → source/topic/global trees   三层摘要树
   → retrieval            search / drill_down / topic / global / fetch
```

关键工程性质（F-051）：

- **热路径无 LLM 调用**：canonicalize→分块→cheap fast-score→落盘全走廉价启发式规则，单事务保证不产生悬挂行
- **持久作业队列 + 后台 worker**：作业类型含 `extract_chunk`（深打分/实体抽取，判 admitted/dropped）、`append_buffer`、`seal`（L0 压缩成 L1 并向上级联）、`topic_route`（按 hotness 决定是否为实体建主题树）、`digest_daily`、`flush_stale`；默认 3 个 worker，信号量限制并发 LLM 调用；worker 租约过期的作业崩溃重启后自动回队
- **leaf 生命周期状态机**：`pending_extraction → admitted → buffered → sealed`，或 `→ dropped`（dropped 行保留以维护 provenance）

## 二、三棵树与磁盘布局

| 树 | 作用域 | 构建方式 |
|----|--------|---------|
| **Source tree** | 每个数据源一棵（每个 Gmail 标签、每个 Slack 频道、每个上传文档） | L0 滚动缓冲填满（或 stale-flush）后 seal 成 L1，逐级级联 |
| **Topic tree** | 每个高热度实体（人、项目、股票代码、仓库）一棵 | 由 hotness 门控惰性物化；实体出现越频繁，树构建刷新越积极 |
| **Global tree** | 全局一棵 | 调度器每天 00:00 UTC 入队一个前一日全局 digest，每天增长一个节点 |

这套结构回答的不是向量库擅长的"什么与查询相似"，而是"今天发生了什么""某人最近怎么样""上周二下午三点 Stripe webhook 说了什么"（F-051）。embeddings 仍在其中（语义检索可用），但树结构负责导航与压缩。

磁盘位置（默认工作区 `~/.openhuman`，可用 `OPENHUMAN_WORKSPACE` 覆盖）：

- `memory_tree/chunks.db`：chunks、scores、summaries、实体索引、jobs、hotness
- `wiki/`：Obsidian 兼容 Markdown vault，桌面端 Intelligence 页可用 `obsidian://open?path=...` 直接打开，支持人工编辑；可选切换外部后端 [agentmemory](https://github.com/rohitg00/agentmemory)（`MemoryConfig.backend = "agentmemory"`）

同步触发有三种：**自动**（每个活跃集成每 20 分钟 auto-fetch）、**手动**（Intelligence 页 "Run ingest"，可按源触发）、**RPC**（`openhuman.memory_tree_ingest`）（F-051）。博文称"同步频率固定 20 分钟没法手动触发"（F-034）与官方手动入口不符——这一点博文的批评已被后续版本功能回应（时序先后无法精确定，以现文档为准）。

## 三、"10 亿 token"数字勘误

| 出处 | 表述 | 可信度 |
|------|------|--------|
| 博文（F-011/F-019） | 容量可达 10 亿 token；对比表中传统窗口几万 / RAG 百万级 / Memory Tree 10 亿 | 博文转述 |
| 官方 README（2026-09） | 仅 "your data compressed into scored Markdown trees in SQLite"，**无容量数字** | 官方一手 |
| 官方 GitBook Memory Tree | 详述管线与三树，**无任何容量/速率数字** | 官方一手 |
| agentic-ai.readthedocs.io（F-052） | "up to 1 billion tokens 累积记忆 / 处理 10M tokens @4,000 tokens/s / NeoCortex 专有系统" | ⚠️ AI 生成第三方知识库，弱源单源；"NeoCortex"之名不见于官方文档 |

**读数指引**：记忆机制本身（层级摘要、三树、本地 SQLite+Obsidian、20 分钟增量）证据充分；但"10 亿 token / 4,000 t/s / NeoCortex"不得作为官方规格引用。博文对比表（F-019）的相对差异定性成立——官方文档同样强调树结构相对向量袋的导航优势、相对线性上下文的自动更新与可编辑性；定量行以官方后续发布为准。

## 四、TokenJuice：压缩在工具输出进入模型之前

官方定位（F-053）：TokenJuice 是串在 Agent **工具执行路径**上的多阶段压缩路由器——任何工具结果在到达模型之前，先被分类、路由到专用压缩器，必要时把完整原文卸载到可恢复缓存，并记录省下的 token 与费用。代码始于对 [vincentkoc/tokenjuice](https://github.com/vincentkoc/tokenjuice) 的移植（JSON 规则覆盖层保留为 log/command 压缩器），后扩展为内容感知的多阶段管线（vendored TinyJuice：`vendor/tinyjuice/src/compress.rs`）。

七步管线（F-053）：

```
raw tool result
 → 1. Size gate       路由器启用？输入 ≥ 2KB？
 → 2. Detect kind     Json · Diff · Html · Search · Code · Log · PlainText
 → 3. Select compressor  每类内容一个专用压缩器（可按类开关）
 → 4. Compress        压缩器拒绝或压缩后变大则回退/直通
 → 5. CCR eligibility 有损且 ≥ ~500 token → 原文卸载缓存
 → 6. Append marker   追加 ⟦tj:<hash>⟧ 脚标，Agent 可取回完整原文
 → 7. Record savings  按模型/压缩器记录 token 与金额节省
```

**80% 上限有官方出处**：README 原文 "TokenJuice: … same information, up to 80% fewer tokens"（F-053 ✅，博文 F-016 的"最高省 80%"准确）。

但博文的两类衍生数字是其**自行测算**，官方文档没有对应口径（F-020/F-021，勘误 2）：

- 细分省幅（HTML→Markdown 40-60%、URL 缩短 5-10%、非 ASCII 清理 5-15%、去重 10-30%）——官方只确认"按内容类型分类压缩"，未公布这些百分比
- 金额测算（30KB/8,000 token→6KB/1,600 token；一次深度分析 $0.04→$0.008；每天 50 次月费 $60→$12）——建立在博文自选输入样例与 GPT-4o 价格假设上，"一个月省几百块"（F-016）是该测算的推广结论

**读数指引**：可引用官方"最高 80%"与七阶段机制；引用具体百分比或美元金额时必须标注"博文测算口径"，不得作为官方 TCO 依据。

## 相关文档

- 产品定位与安装：[00-what-is-openhuman](00-what-is-openhuman.md)
- 记忆的消费者（编排/会议/隐私）：[02-runtime-and-agent-design](02-runtime-and-agent-design.md)
- 竞品记忆方案对照：[03-landscape-and-tradeoffs](03-landscape-and-tradeoffs.md)
- 核验明细：[references/verification](../references/verification.md)
