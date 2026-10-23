---
type: reference
scope: zvec
name: zvec.org 官方文档站信源
version: "2026-10-22 快照"
source: https://zvec.org/zh/
description: zvec.org 中文官方文档站登记——db 与 zvec-grep 两大产品文档树，本束文档侧事实的可追溯锚点
generated: { by: "teleagent/seven-concepts-r", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-01-22
---

# zvec.org 官方文档站信源登记

## 一、信源定位

| 属性 | 值 |
|---|---|
| 站点 | [zvec.org](https://zvec.org/zh/)（中文版） |
| 运营方 | Alibaba Group（© 2026，Apache License 2.0） |
| 采集日期 | 2026-10-22（网页快照） |
| 采集方式 | 逐页抓取（首页、docs 总览、db 文档树、zvec-grep 文档树） |

> 网页为活文档，持续更新；本束以 2026-10-22 抓取内容为准。源码与文档冲突时，以源码镜像（commit 8d49969）为准并在正文标注差异。

## 二、文档树结构（本次采集覆盖）

### Zvec 嵌入式向量数据库（/zh/docs/db/）

| 页面 | 采集状态 |
|---|---|
| 关于 Zvec、概念总览、数据结构、向量、向量索引、倒排索引、全文索引 | ✅ 全文采集 |
| 向量索引七子页（flat/hnsw/hnsw-rabitq/diskann/ivf/ivf-rabitq/quantization） | ✅ 全文采集 |
| 快速开始、全局配置、Collection（创建/优化/Schema 演进）、数据操作（总览/查询） | ✅ 全文采集 |
| Embedding、Reranker、MCP 服务器、Skills、基准测试、平台支持 | ✅ 全文采集 |
| AI 友好、源码构建、检索子页（单向量/多向量/过滤/混合/FTS/分组）、遍历、获取等 | ⚪ 未逐页采集（导航引用） |

### Zvec-Grep 本地工作区搜索（/zh/docs/zvec-grep/）

| 页面 | 采集状态 |
|---|---|
| 什么是 Zvec-Grep、快速上手、CLI 参考、管理索引、检索指南 | ✅ 全文采集 |
| Embedding 模型、支持的内容、接入 AI Agent、Benchmark | ✅ 全文采集 |
| 本地 Server、故障排查 | ⚪ 未逐页采集（导航引用） |

## 三、关键事实速查（文档侧）

| 事实 | 数值 |
|---|---|
| 官方语言 SDK | 7 种（Python / Node.js / Go / Rust / Java / Dart/Flutter / C/C++） |
| 官方文档索引类型 | 6 种（Flat / HNSW / HNSW-RaBitQ / DiskANN / IVF / IVF-RaBitQ） |
| 平台覆盖 | Linux / macOS / Windows / Android / iOS + RISC-V（源码构建）；索引可用性矩阵 9 类索引 × 9 平台 |
| MCP 服务器工具数 | 17 个（create/insert/query/optimize/embedding 等，uvx 分发） |
| 性能口径 | Cohere 10M（768 维）：16 vCPU · 64 GiB · INT8 · 最高 20 并发，8500+ QPS，约 1 小时构建 |
| zvec-grep 评测 | SWE-QA-Bench：+1.5pp 回答质量 / −47.3% 输入 Token / −58.6% 工具调用 / −37.5% Agent 耗时；BrowseComp-Plus：+0.33pp / −37.56% / −43.52% / −38.58% |
| zvec-grep 本地模型 | 11 个（Potion×3 / ONNX×6 / GGUF×2） |
| zvec-grep 远程模型 | 3 个（qwen/text-embedding-v4 等） |
| 结构化代码提取语言 | C/C++、Go、Java、JavaScript/JSX、TypeScript/TSX、Python、Rust 共 7 类 |

## 四、开源生态集成（官网首页列示）

| 项目 | 集成角色 |
|---|---|
| [Logseq](https://github.com/logseq/logseq) | 知识管理——本地图谱与 Embedding 桌面端混合检索 |
| [MyContext](https://github.com/openTrinity/mycontext) | 个人上下文——私有上下文检索与知识图谱记忆（向量存储） |
| [ReMe](https://github.com/agentscope-ai/ReMe) | Agent 记忆——可检索、可召回的持久化本地记忆（记忆后端） |
| [txtai](https://github.com/neuml/txtai) | AI 框架——一体化 AI 框架中的语义检索（稠密 ANN） |
| [CocoIndex](https://github.com/cocoindex-io/cocoindex) | 数据管道——增量数据管道的索引 Connector |

## 五、周边仓库（非本束源码，导航登记）

| 仓库 | 说明 |
|---|---|
| [zvec-ai/zvec-grep](https://github.com/zvec-ai/zvec-grep) | `zg` CLI 与 MCP 工具（本束文档侧信源，源码未镜像） |
| [zvec-ai/zvec-mcp-server](https://github.com/zvec-ai/zvec-mcp-server) | 面向 Agent 的 Zvec MCP 服务器（17 工具） |
| [zvec-ai/zvec-agent-skills](https://github.com/zvec-ai/zvec-agent-skills) | Zvec 领域知识 Skill 包 |
| [zvec-ai/zvec-studio](https://github.com/zvec-ai/zvec-studio) | 可视化工作台 |
| zvec-go / zvec-rust / zvec-dart 等 | 各语言 SDK 仓库（zvec-ai 组织） |
