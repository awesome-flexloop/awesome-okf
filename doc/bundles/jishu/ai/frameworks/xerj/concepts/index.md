# Concepts 索引

本目录是 XERJ 知识包的概念文档，按「入门 → 核心 → 进阶」三段组织，并按信源分两轮：前 9 篇来自源码与上游自述（第一轮），后 5 篇来自官方文档站（第二轮）。

## 入门：建立心智模型（第一轮）

| 文档 | 一句话简介 |
|---|---|
| [00 整体架构](00-overview.md) | 18 个 crate 的职责分层、三条并发端口、搜索与摄取路径、「ES 兼容是传输层」这一架构主轴 |
| [01 安装与快速上手](01-getting-started.md) | 安装与 SHA-256 校验策略、`--insecure` 信任边界、admin.key 认证模型、14 个顶层子命令全景、首次索引闭环 |
| [02 autoindex 零配置流水线](02-autoindex-pipeline.md) | 内容驱动的格式识别（28 个 Family / 25 个抽取器）、字段来源标记决定的数据集划分、阶段序列、10 分钟决策门与退出码语义 |

## 核心：主要接口面（第一轮）

| 文档 | 一句话简介 |
|---|---|
| [03 MCP 智能体接口](03-mcp-agent-surface.md) | 17 个工具的分工、代理与非代理之别、回环 admin.key 认证回退、`max_tokens` 硬预算、工具计数漂移 |
| [04 检索路径与响应裁剪](04-search-query-path.md) | 查询执行链路、memtable 与 segment 双路合并、`_passage` 伪字段与 `_xerj.hints`、未知字段严格模式 |
| [05 向量、嵌入与混合检索](05-vector-and-hybrid.md) | 四类嵌入后端与「嵌入在摄入时绑定」、HNSW 与 flat-slab 重构、精确扫描与 ANN 的判定规则、`rerank` 外呼边界 |

## 进阶：边界与替代路径（第一轮）

| 文档 | 一句话简介 |
|---|---|
| [06 智能体记忆与第二大脑](06-agent-memory-and-brain.md) | `/_memory` 命名空间记忆、`/_graph` 关系层（9 个确定性检测器）、`/_ask` 确定性规划器、`/_decide` 类型化判断 |
| [07 ES 兼容与基准诚实性](07-es-compat-and-benchmarks.md) | ES 8.x 线协议兼容面、零失败一致性门禁、记分卡 55/26/4 与四处败因、能力边界与未实现清单 |
| [08 参考编码与语料库](08-reference-coding.md) | `corpus add/index/code` 闭环、返回定义而非字节窗口、退出码契约、许可证分档、MEATL 输出、收益的记忆门控 |

## 参考与运维（第二轮 · 来自官方文档站）

| 文档 | 一句话简介 |
|---|---|
| [09 查询类型与聚合](09-query-types-and-aggregations.md) | 50 种查询类型与 2 种显式拒绝、62 种聚合的精确性与采样例外、10,000 文档以上的列式快速路径、查询面与 ES 的语义差异 |
| [10 分析器与摄取管线](10-analyzers-and-ingest.md) | 4 个内置分析器与选择规则、4 条进程内摄取路径（turbo-ingest/logs/syslog/otlp）、端到端背压的两种形态 |
| [11 存储、压缩与集群现状](11-storage-compression-clustering.md) | 每段三个 mmap 文件、WAL 三档持久性、9 种列编码与 Zstd 三档力度、集群的四项「不提供」与磁盘格式标记 |
| [12 配置与环境变量](12-config-and-environment.md) | 24 个配置段与文档键表的差距、16 个完全未接线的键、环境变量优先级不统一、认证与 TLS、WAL tap 与 rerank 的写一次语义 |
| [13 生产运维与排障](13-operations-and-troubleshooting.md) | systemd 加固单元、存活与就绪双探针、SIGHUP 热加载边界、容量三数字与三文件 fd、备份四式、升级流程与六类生产症状 |

```{toctree}
:maxdepth: 2

00-overview
01-getting-started
02-autoindex-pipeline
03-mcp-agent-surface
04-search-query-path
05-vector-and-hybrid
06-agent-memory-and-brain
07-es-compat-and-benchmarks
08-reference-coding
09-query-types-and-aggregations
10-analyzers-and-ingest
11-storage-compression-clustering
12-config-and-environment
13-operations-and-troubleshooting
```
