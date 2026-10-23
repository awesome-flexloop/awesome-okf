# 概念索引

zvec 束的概念文档按"入门 → 核心 → 进阶 → Agent"的学习路径组织。

| 文档 | 主题 |
|---|---|
| [00-overview](00-overview.md) | 产品定位、特性矩阵、平台与生态 |
| [01-architecture](01-architecture.md) | 四层 C++ 源码架构与 C API 边界 |
| [02-data-modeling](02-data-modeling.md) | Collection/Document/Schema 与 23 种 DataType |
| [03-index-types](03-index-types.md) | 六种官方索引类型与选型决策 |
| [04-quantization](04-quantization.md) | 量化双轨：存储压缩与距离估计 |
| [05-fts-and-filter](05-fts-and-filter.md) | FTS/BM25/WAND 与 ANTLR SQL 过滤引擎 |
| [06-hybrid-retrieval](06-hybrid-retrieval.md) | 多路 Query 与 Reranker 融合 |
| [07-embedding-reranker](07-embedding-reranker.md) | Embedding 与 Reranker 函数体系 |
| [08-storage-and-config](08-storage-and-config.md) | WAL/列存/IO 后端/init 容器自适应 |
| [09-agent-integration](09-agent-integration.md) | MCP/Skills/zvec-grep 三条 Agent 路径 |

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-architecture
02-data-modeling
03-index-types
04-quantization
05-fts-and-filter
06-hybrid-retrieval
07-embedding-reranker
08-storage-and-config
09-agent-integration
```
