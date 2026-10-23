---
type: reference
scope: zvec
name: zvec 洞察记录
version: "1.0.0"
source: spec/facts.md
description: I 阶段核心洞察四元组（陈述/证据/反常识/行动）与知识地图设计
generated: { by: "teleagent/seven-concepts-i", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
---

# zvec 洞察记录（I 阶段）

## 洞察一：库即数据库——进程内形态重划向量库边界

- **陈述**：Zvec 把向量数据库全套能力（WAL、多版本 segment、SQL 过滤引擎、量化、多类索引）压缩为进程内 C++ 库，经唯一 C API 头文件辐射 7 语言 SDK。
- **证据**：F-031（include/zvec 仅 c_api.h/export.h/version.h.in）、F-003/F-005（进程内、无服务器）、F-028（WAL + segment 存储）、F-026（ANTLR SQL 引擎）、F-008（7 SDK 共享 C API 边界）。
- **反常识**：主流向量库（Milvus 等）走 client-server；Zvec 反向把 RocksDB/Arrow/ANTLR 全部静态嵌入单进程——代价是写入单进程独占（F-003 并发模型：多进程读、单进程写），换来零部署与 Android/iOS 边缘可用。
- **行动**：教程以"嵌入式优先"心智组织：collection 目录自包含可迁移、open/create_and_open 生命周期、cgroup 自适应 init()。

## 洞察二：量化双轨制——存储压缩与距离估计分层正交

- **陈述**：量化被拆为两层——turbo 层（FP16/INT8/INT4/PQ，存储格式压缩）与 core 层（RaBitQ/Uniform，算法内嵌的距离估计），两层组合出 IndexType × QuantizeType 能力矩阵。
- **证据**：F-022（turbo/quantizer 七种标量/PQ 量化器）、F-024（core/quantizer 的 binary/cosine/mips/uniform converter+reformer）、F-042/F-043（IndexType 与 QuantizeType 枚举并列）、F-023（hnsw_rabitq/ivf_rabitq 为独立算法目录）。
- **反常识**：多数库把量化当索引参数；Zvec 把 RaBitQ 升格为独立索引类型（HNSW-RaBitQ/IVF-RaBitQ），因为 RaBitQ 改变的是距离计算方式（随机旋转+二值编码+位运算），而非仅存储格式——这解释了其平台约束（AVX2/AVX512）来自位运算内核。
- **行动**：索引章按"6 官方类型 + Vamana 源码彩蛋 + 量化双轨"展开；调参建议表区分构建参数与查询参数。

## 洞察三：FTS 是一等公民而非外挂——但与向量在单 Query 内互斥

- **陈述**：全文检索能力完整内嵌——ANTLR4 词法/语法/分析/计划四段 SQL 引擎编译过滤表达式，BM25 + WAND（128 doc 块）+ 内置 Jieba/HMM 中文分词，倒排列落 RocksDB。
- **证据**：F-026（sqlengine 完整栈）、F-067/F-068（WAND、分词器三选）、F-030（bm25_scorer 引用 rocksdb）、F-006（v0.8.0 内置 Jieba 词典）、F-069（fts 与 vector 互斥）。
- **反常识**：嵌入式库通常只做向量 ANN；Zvec 同时内置搜索引擎级 FTS 栈。但"混合检索"不是单查询魔法——必须多路 Query + RrfReRanker/WeightedReRanker 融合，这是文档明确的路由约束。
- **行动**：混合检索章以"多路 Query + Reranker"为主线模式，给出两阶段检索（召回→精排）最佳实践。

## 洞察四：Agent 三件套分层——库侧全量 MCP，grep 侧刻意单工具

- **陈述**：AI-Native 能力分层产品化——zvec 库侧 MCP（17 工具）+ Agent Skills 面向应用开发者；zvec-grep（zg CLI，独立仓库）面向开发者本人与 Agent，仅暴露 1 个 MCP 工具。
- **证据**：F-090（17 工具五类）、F-091（Skills 注入领域知识）、F-092/F-098（zvec-grep 独立仓库、仅 zvec_grep_search 单工具、索引管理权留用户）、F-100（SWE-QA +1.5pp/−47.3% Token）、F-095（四条检索路径）。
- **反常识**：两个仓库、两种工具面哲学——库侧放开全部操作给 Agent，grep 侧收窄到单检索工具并把索引管理权留在用户 CLI 手里（防止 Agent 误重建索引）；检索路由表明确划分原生 rg 与 zvec_grep_search 的分工。
- **行动**：Agent 集成章覆盖 MCP/Skills/zvec-grep 三条路径 + 检索路由决策表 + 远程模型授权模型（zg auth grant）。

## 洞察五：服务器级运维特性下放嵌入式场景

- **陈述**：生产级运维能力（4 种磁盘 I/O 后端、cgroup 感知默认配置、日志轮转、Arrow/Parquet 列存混合）被完整带入嵌入式与边缘场景。
- **证据**：F-045（PREAD/LIBAIO/IO_URING/WINDOWS_OVERLAPPED）、F-048（init 12 参数 None 回落 cgroup 推断，memory_limit_mb 默认 cgroup×0.8）、F-028（Arrow IPC + Parquet + bufferpool/mmap/memory 三种 forward store）、F-073（optimize 后台合并不锁）。
- **反常识**：嵌入式库通常不带平台矩阵与 cgroup 感知；Zvec 的默认配置会读容器配额自动定线程/内存——Kubernetes 部署时"不配置"反而是最佳配置。
- **行动**：存储与配置章讲 IO 后端选择、init() 容器自适应、三种 forward store 与内存权衡。

## 知识地图

```
入门 ──→ 00-overview（产品矩阵与特性）
      ──→ examples/00-quickstart-python（5 分钟上手）
核心 ──→ 01-architecture（四层源码架构 + C API）
      ──→ 02-data-modeling（Collection/Document/Schema/23 DataType）
      ──→ 03-index-types（6+2 索引类型与选型）
      ──→ 04-quantization（量化双轨）
进阶 ──→ 05-fts-and-filter（FTS/BM25/WAND/ANTLR 过滤）
      ──→ 06-hybrid-retrieval（多路混合 + Reranker）
      ──→ 07-embedding-reranker（7+4 函数体系与自定义）
      ──→ 08-storage-and-config（WAL/存储/init 运维）
Agent ──→ 09-agent-integration（MCP/Skills/zvec-grep）
      ──→ examples/01-hybrid-search（混合检索实战）
      ──→ examples/02-zvec-grep-cli（zg CLI 实战）
```
