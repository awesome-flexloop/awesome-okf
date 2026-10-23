---
okf_version: "0.2"
type: bundle
title: "Zvec 嵌入式向量数据库"
description: "Alibaba 开源进程内向量检索库源码级中文教程——四层 C++ 架构、六种索引、RaBitQ 量化双轨、FTS/ANTLR 过滤引擎、混合检索与 MCP/zvec-grep Agent 集成"
total_bundles: 1
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-source
    resource: /references/source-code.md
    title: alibaba/zvec 源码信源
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# Zvec 嵌入式向量数据库

本束是 [alibaba/zvec](https://github.com/alibaba/zvec)（Apache 2.0，commit `8d49969` / v0.8.0-4）的源码级中文学习教程，双信源交叉采集：本地源码镜像 + [zvec.org 官方文档](https://zvec.org/zh/)（2026-10-22 快照）。R/I 阶段事实清单与洞察记录见 [spec/facts.md](spec/facts.md) 与 [spec/insights.md](spec/insights.md)。

Zvec 是"本地优先检索基础设施"：进程内嵌入式向量数据库（无需服务器/守护进程），经唯一 C API 辐射 7 语言 SDK；同族产品 zvec-grep（`zg` CLI + MCP）面向开发者与 AI Agent 的本地工作区检索。

## 知识结构

| 章节 | 内容 |
|---|---|
| [概念：总览](concepts/00-overview.md) | 产品矩阵、核心特性、平台与生态 |
| [概念：源码架构](concepts/01-architecture.md) | ailego→turbo→core→db 四层分层与 C API 边界 |
| [概念：数据模型](concepts/02-data-modeling.md) | Collection/Document/Schema/23 种 DataType/DDL |
| [概念：索引类型](concepts/03-index-types.md) | Flat/HNSW/HNSW-RaBitQ/DiskANN/IVF/IVF-RaBitQ 选型 |
| [概念：量化](concepts/04-quantization.md) | 存储压缩轨与 RaBitQ/Uniform 距离估计轨 |
| [概念：FTS 与过滤](concepts/05-fts-and-filter.md) | BM25/WAND/Jieba 与 ANTLR4 SQL 引擎 |
| [概念：混合检索](concepts/06-hybrid-retrieval.md) | 多路 Query + Reranker 融合 |
| [概念：Embedding 与 Reranker](concepts/07-embedding-reranker.md) | 7 种 Embedding + 4 种 Reranker |
| [概念：存储与配置](concepts/08-storage-and-config.md) | WAL/Arrow/IO 后端/init 容器自适应 |
| [概念：Agent 集成](concepts/09-agent-integration.md) | MCP 17 工具/Skills/zvec-grep 检索路由 |
| [示例](examples/index.md) | Python 快速上手 / 混合检索 / zg CLI |
| [信源](references/index.md) | 源码与文档站双信源登记 |

## 学习路径

```text
入门：00-overview → examples/00-quickstart-python
源码：01-architecture → 02-data-modeling → 03-index-types → 04-quantization
检索：05-fts-and-filter → 06-hybrid-retrieval → 07-embedding-reranker
运维：08-storage-and-config
Agent：09-agent-integration → examples/02-zvec-grep-cli
```

## 版本信息

- 源码基准：alibaba/zvec @ `8d4996924bce78f8b072a353803c305101bcc807`（v0.8.0-4-g8d49969）
- 文档快照：zvec.org 中文站 2026-10-22
- 许可证：Apache License 2.0

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
