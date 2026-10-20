---
okf_version: "0.2"
title: XERJ 源码学习知识包
description: XERJ 源码教程——Rust 从零实现的 AI 原生搜索引擎，覆盖 18 crate 架构、autoindex 零配置摄取流水线、17 个 MCP 工具、向量与混合检索、第二大脑与参考编码、50 种查询与 62 种聚合、配置面与生产运维，附诚实的边界与基准
---

# XERJ 源码学习知识包

XERJ 是一个用 Rust 从零实现的 AI 原生搜索引擎，同时覆盖向量检索与日志分析，以**一个静态二进制**交付（61.6 MB，含神经嵌入后端；F-013）。它不共享 Elasticsearch 或 Lucene 的任何代码与架构（F-007），但实现了 Elasticsearch 8.x 的 HTTP 线协议，作为零迁移接入桥梁（F-008）。

本知识包基于 `xerj-org/xerj` 仓库 commit `51ff219276d7e55d9d85b4938e8b94f235f9d099` 整理，**分两轮信源**：

- **第一轮（源码与上游自述）**——9 篇概念 + 4 篇实战示例 + 206 条编号事实：从定位、架构、autoindex 流水线、MCP 接口、检索路径、向量与混合检索、记忆与第二大脑，到 ES 兼容与基准诚实性、参考编码与语料库。
- **第二轮（官方文档站 xerj.org/docs/，46 页）**——增量 5 篇概念 + 1 篇示例 + 156 条编号事实：50 种查询与 62 种聚合、4 个分析器与 4 条摄取管线、存储与压缩与集群现状、配置面与环境变量、生产运维与排障。

> **读本束前先记住三件事**
>
> 1. **ES 兼容是传输层，不是产品身份。** 先跑旗舰回路（`autoindex` → `autoindex map` → 查询），再谈 DSL 覆盖度。
> 2. **默认嵌入模式是词法，不是神经。** `semantic` 是字段类型与检索形状的名字，不是模型能力的承诺。
> 3. **人读文档会滞后，机器可读面不会。** 工具清单以 `landing/docs/agents/schemas/mcp-tools.json` 为准（实际 17 个，README 写 13 个）；官方文档站同一发布版内部亦有四处自相矛盾（见 [05 官方文档地图与选型](/examples/05-official-docs-map.md)）。

## 概念文档

### 入门

- [00 整体架构](concepts/00-overview.md) — 18 个 crate 的职责分层、三条并发端口、搜索与摄取路径、「ES 兼容是传输层」这一架构主轴
- [01 安装与快速上手](concepts/01-getting-started.md) — 安装与 SHA-256 校验策略、`--insecure` 信任边界、admin.key 认证模型、14 个顶层子命令全景、首次索引闭环
- [02 autoindex 零配置流水线](concepts/02-autoindex-pipeline.md) — 内容驱动的格式识别（28 个 Family / 25 个抽取器）、字段来源标记决定的数据集划分、阶段序列、10 分钟决策门与退出码语义

### 核心

- [03 MCP 智能体接口](concepts/03-mcp-agent-surface.md) — 17 个工具的分工、代理与非代理之别、回环 admin.key 认证回退、`max_tokens` 硬预算、工具计数漂移
- [04 检索路径与响应裁剪](concepts/04-search-query-path.md) — 查询执行链路、memtable 与 segment 双路合并、`_passage` 伪字段与 `_xerj.hints` 提示、未知字段严格模式
- [05 向量、嵌入与混合检索](concepts/05-vector-and-hybrid.md) — 四类嵌入后端与「嵌入在摄入时绑定」、HNSW 与 flat-slab 重构、精确扫描与 ANN 的判定规则、`rerank` 外呼边界

### 进阶

- [06 智能体记忆与第二大脑](concepts/06-agent-memory-and-brain.md) — `/_memory` 命名空间记忆、`/_graph` 关系层（9 个确定性检测器）、`/_ask` 确定性规划器、`/_decide` 类型化判断
- [07 ES 兼容与基准诚实性](concepts/07-es-compat-and-benchmarks.md) — ES 8.x 线协议兼容面、零失败一致性门禁、记分卡 55/26/4 与四处败因、能力边界与未实现清单
- [08 参考编码与语料库](concepts/08-reference-coding.md) — `corpus add/index/code` 闭环、返回定义而非字节窗口、退出码契约、许可证分档、MEATL 输出、收益的记忆门控

### 参考与运维（第二轮 · 来自官方文档站）

- [09 查询类型与聚合](concepts/09-query-types-and-aggregations.md) — 50 种查询类型与 2 种显式拒绝、62 种聚合的精确性与采样例外、10,000 文档以上的列式快速路径、查询面与 ES 的语义差异
- [10 分析器与摄取管线](concepts/10-analyzers-and-ingest.md) — 4 个内置分析器与选择规则、4 条进程内摄取路径（turbo-ingest/logs/syslog/otlp）、端到端背压的两种形态
- [11 存储、压缩与集群现状](concepts/11-storage-compression-clustering.md) — 每段三个 mmap 文件、WAL 三档持久性、9 种列编码与 Zstd 三档力度、集群的四项「不提供」与磁盘格式标记
- [12 配置与环境变量](concepts/12-config-and-environment.md) — 24 个配置段与文档键表的差距、16 个完全未接线的键、环境变量优先级不统一、认证与 TLS、WAL tap 与 rerank 的写一次语义
- [13 生产运维与排障](concepts/13-operations-and-troubleshooting.md) — systemd 加固单元、存活与就绪双探针、SIGHUP 热加载边界、容量三数字与三文件 fd、备份四式、升级流程与六类生产症状

## 示例

- [01 从一个文件夹到可查询索引](examples/01-autoindex-to-query.md) — 端到端：估计 → 决策门 → 索引 → 摸清数据 → 带裁剪的查询
- [02 把智能体接到 XERJ 上](examples/02-mcp-integration.md) — MCP 配置、认证优先级、五个检索工具调用形状、无 shell 的 HTTP 路径
- [03 选择检索模式](examples/03-retrieval-mode-selection.md) — 词法/语义/向量/混合的决策表、响应裁剪、三臂评测方法
- [04 从 Elasticsearch 迁移的评估路径](examples/04-migration-from-elasticsearch.md) — 三个零成本对照实验、兼容面与 scroll 边界、迁移要自担的运维清单
- [05 官方文档地图与选型](examples/05-official-docs-map.md) — 46 页导航地图、13 recipe + 5 playbook 选型、Corpus Hub 两条通道、**四处文档漂移的复核方法**

## 参考资料

- [架构洞察与知识地图（第一轮）](references/insights.md) — 六条洞察四元组、事实覆盖分配与三段式学习路径
- [官方文档站洞察（第二轮）](references/insights-docs.md) — 洞察 7～12：接了线但没接线 / 集群给的是选主环 / 诚实被编码进响应体 / 量化换精度不换内存 等
- [事实清单（第一轮·源码）](references/facts.md) — 206 条编号事实（F-001～F-206），每条标注路径与行号
- [事实清单（第二轮·文档站）](references/facts-docs.md) — 156 条编号事实（F-207～F-362）+ 交叉核验记录
- [信源登记（源码快照）](references/source.md) — 仓库身份与 commit 哈希、规模与各 crate 行数（脚本计数）、15 个关键文件清单、路径稳定性判定
- [信源登记（官方文档站）](references/docs-source.md) — 在线站点与本地落地快照的对应、版本锚点、46 页清单与页面→本束对照
- [背景调研](references/background-research.md) — AI 检索栈现状、Rust 生态既有方案、许可证分档、成本模型与研究过程
- [References 索引](references/index.md) — 参考资料汇总列表

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
