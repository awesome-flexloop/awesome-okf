---
type: Concept
title: Zvec 总览：本地优先检索基础设施
description: Alibaba 开源嵌入式向量数据库的产品定位、核心特性、性能口径与生态矩阵，含 zvec-grep/Studio/MCP/Skills 产品线全景
tags: [zvec, vector-database, embedded, retrieval, alibaba]
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

# Zvec 总览：本地优先检索基础设施

**Zvec** 是阿里巴巴开源的高性能嵌入式向量数据库（Apache 2.0，GitHub [alibaba/zvec](https://github.com/alibaba/zvec)），完全以进程内方式运行——无需服务器、守护进程或外部软件设施，安装后即可进行向量索引与查询。它既可作为独立向量数据库做端到端存储检索，也可嵌入既有搜索系统充当专用向量引擎，服务语义搜索、RAG、推荐系统等 AI 应用。

围绕同一检索内核，Zvec 形成了面向不同工作流的产品矩阵：**Zvec** 库本体（应用进程内）、**Zvec-Grep**（`zg` CLI + MCP 的本地工作区搜索）、**Zvec Studio**（可视化工作台）、**MCP Server** 与 **Agent Skills**（AI Agent 集成件）。

## 产品矩阵

| 产品 | 形态 | 面向 | 典型场景 |
|---|---|---|---|
| Zvec 库 | 进程内 C++ 库 + 7 语言 SDK | 应用开发者 | 存储/查询应用生成的 Embedding，代码内控制 Schema、索引、过滤 |
| Zvec-Grep（zg） | Node.js CLI + MCP 工具 | 开发者与 AI Agent | 直接检索现有代码/文档工作区，扫描→分块→Embedding→索引全托管 |
| Zvec Studio | 图形界面 | 数据调试 | 零代码浏览数据与调试查询 |
| zvec-mcp-server | MCP 服务器（uvx 分发，17 工具） | AI 编程助手 | Claude Code/Qoder 对话中直接操作向量库 |
| zvec-agent-skills | Skill 包 | AI 编程助手 | 注入 Schema 设计、索引选型等领域经验 |

两条产品线的数据链路差异：Zvec 库由应用自行负责数据解析与向量生成；Zvec-Grep 托管全链路（工作区文件扫描、解析与分块、BM25+向量索引），用户只管查询。

## 核心特性

- **进程内运行**：纯本地运行，Notebook、高性能服务器、CLI 工具、边缘设备随处可用；多进程可并发读同一 Collection，写入为单进程独占。
- **稠密 + 稀疏向量**：支持稠密向量（FP16/FP32/FP64/INT8/UINT8）、稀疏向量（SPARSE_VECTOR_FP32/FP16）与多向量联合查询。
- **全文检索（FTS）**：原生 BM25 关键词检索，支持自然语言、短语匹配与布尔表达式；内置 Jieba 中文分词（v0.8.0 起开箱即用，含 HMM 模型）。
- **混合检索**：单次查询融合向量语义、全文检索与标量过滤。
- **持久化**：WAL 预写日志保障崩溃/断电后数据不丢。
- **极致性能**：Cohere 10M（768 维、INT8、16 vCPU/64 GiB、最高 20 并发）口径 8500+ QPS、约 1 小时构建；已历经阿里巴巴生产级负载验证。

## 平台与 SDK

7 种官方语言 SDK（Python/Node.js/Go/Rust/Java/Dart/Flutter/C/C++）共享同一条稳定 C API 边界。平台覆盖 Linux（x86_64/ARM64，glibc 与 musl）、macOS（Intel/Apple Silicon）、Windows（x86_64/ARM64）、Android（arm64-v8a）、iOS（arm64）；RISC-V 需源码构建。索引可用性矩阵为 9 类索引 × 9 平台。

Python 安装：`pip install zvec`（需 64 位 Python 3.10–3.14；32 位解释器在 import 时即报错拒绝）。

## 开源生态集成

Logseq（本地图谱混合检索）、MyContext（私有上下文向量存储）、ReMe（Agent 持久化记忆后端）、txtai（AI 框架稠密 ANN）、CocoIndex（增量数据管道索引 Connector）等项目已将 Zvec 嵌入各自产品。

## 版本速览（v0.8.0）

Intel Mac 与 Windows ARM64 构建；DiskANN 扩展至 Windows/Android/iOS；RaBitQ 新增 Windows x86_64；中文全文检索内置 Jieba 词典；UTF-8 文档 ID 上限 1024 字节；新增 Uniform 系列量化器；Vamana 图布局与预取优化。

## 相关概念

- [源码架构](01-architecture.md)：四层 C++ 架构与 C API 边界
- [数据模型](02-data-modeling.md)：Collection/Document/Schema
- [Agent 集成](09-agent-integration.md)：MCP/Skills/zvec-grep 三条路径
