---
okf_version: "0.2"
type: bundle-index
title: "Dolt — 版本化 SQL 数据库"
description: "Dolt 知识包：从存储层原生支持 Git 式版本控制的 SQL 数据库——行级历史、分支/合并、MySQL/PostgreSQL/SQLite/MongoDB 多协议生态、MCP Server 与 AI Agent 安全操作、Dolt Workbench，含博文 P0 核验、勘误与本地源码核验"
tags:
  - dolt
  - git
  - sql
  - mysql
  - version-control
  - database
  - mcp
  - prolly-tree
generated:
  at: "2026-09-08"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
  noted: F-042 口径需细化（Sysbench 读写已超越 MySQL），F-045 勘误（Web UI 限制误读）；2026-09-09 基于本地 DoltHub 源码补登 F-073~F-085（多协议生态 + 存储引擎架构）
stale_after: "2026-12-31"
sources:
  - url: "https://mp.weixin.qq.com/s/ES_KncqKLiQxIzaEZ-58gg"
    type: blog-article
    title: "数据库也能像 Git 一样进行 fork、branch 和 merge 吗？"
    author: "开源日记"
    published: "2026-06-18"
    distance: 3
  - url: "https://github.com/dolthub/dolt"
    type: official
    title: "dolthub/dolt — GitHub"
    distance: 1
  - url: "https://docs.doltdb.com/"
    type: official-docs
    title: "Dolt Documentation"
    distance: 1
  - url: "https://www.dolthub.com/latency-benchmarks"
    type: official
    title: "Dolt Latency Benchmarks"
    published: "2026-05-14"
    distance: 1
  - url: "https://github.com/dolthub/dolt-mcp"
    type: official
    title: "dolthub/dolt-mcp — MCP Server"
    distance: 1
  - url: "https://github.com/dolthub/dolt-workbench"
    type: official
    title: "dolthub/dolt-workbench"
    distance: 1
  - url: "https://www.dolthub.com/blog/2021-05-26-dolt-web-ui/"
    type: official
    title: "Dolt Web UI Blog (2021-05-26)"
    distance: 1
  - url: "https://github.com/dolthub"
    type: source-code
    title: "dolthub 组织源码（dolt/dolt-mcp/dolt-workbench/doltgresql/doltlite/dumbodb/driver 等 12 仓库，本地克隆）"
    distance: 1
status: stable
---

# Dolt — 版本化 SQL 数据库

本知识包基于微信公众号「开源日记」博文《数据库也能像 Git 一样进行 fork、branch 和 merge 吗？》（2026-06-18）生成，经 [P0 权威核验报告](references/verification.md) 交叉验证，对勘误项标注官方正确口径；并于 2026-09-09 基于本地 `dolthub` 组织源码（12 仓库）补登源码事实（F-073~F-085），将产品矩阵扩展为多协议生态。所有内容溯源至 [F-001 ~ F-085](references/article-source.md)，遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

> **⚠️ 勘误提示**：博文所述"超过 1G 数据会变慢"（F-045）为误读，系将 DoltHub Web UI 查询超时限制（约 1GB，2021 年过时信息）泛化为 Dolt 数据库本身能力限制。Dolt 生产环境可处理 TB 级数据。正确口径见 [F-060](references/article-source.md) 与 [verification.md](references/verification.md)。

## 导航

### 核心概念（concepts/）

* [Dolt 概述与产品矩阵](concepts/00-dolt-overview.md) — 产品定位、核心功能、产品矩阵（Dolt/DoltHub/DoltLab/Hosted Dolt/MCP/Workbench）、开源协议与兼容生态
* [行级版本控制机制](concepts/01-dolt-versioning-mechanism.md) — Prolly Tree 存储、行级历史视图、分支/合并/回滚、MySQL 兼容原理、MCP/AI Agent 工作流
* [边界、限制与选型建议](concepts/02-dolt-boundaries-trends.md) — TPC-C 54% 性能、1G 阈值勘误、迁移成本、适用场景、选型启示

### 信源与核验（references/）

* [博文信源登记](references/article-source.md) — F-001 ~ F-085 全部事实编号登记（含源码事实 F-073~F-085）
* [P0 权威核验报告](references/verification.md) — 9 项 P0 声明核验结论 + 勘误四张清单

## 学习路径建议

1. **入门**：[Dolt 概述](concepts/00-dolt-overview.md) → [行级版本控制机制](concepts/01-dolt-versioning-mechanism.md)
2. **进阶**：[边界与选型建议](concepts/02-dolt-boundaries-trends.md)（含勘误说明）
3. **溯源**：阅读 [references/article-source.md](references/article-source.md) 核对全部 F 编号，查阅 [verification.md](references/verification.md) 了解核验细节

## 骨架判定说明

- **一问**（有读者可照做的安装/配置/代码/调用流程？）：博文含 `dolt init`、`dolt sql server`、`mysql --host=...` 等命令，但无版本/输出/步骤顺序的完整实测记录
- **二问**（经作者实测、有版本/输入输出/步骤顺序？）：博文称"我试了一把"但未提供具体版本、输入输出记录
- **结论**：两问均未完全满足，本 bundle **不设 examples/**，定位"技术综述/产品介绍"

## 信任与生命周期说明

- **status 判定依据**：`stable`。9 项 P0 声明核验完成，7 项 ✅，1 项 ⚠️（F-042 口径保守），1 项 ❌（F-045 勘误已补充官方正确口径 F-060）。
- **stale_after 解释**：设为 `2026-12-31`。Dolt 为快速发展产品（v2.0+ 版本迭代频繁），性能数据（TPC-C 54%、Sysbench 基准）时效性强，年末重新评估。
- **核验链路**：`generated.at` 与 `verified.at` 均为 2026-09-08（spec:okf-wiki-ecosystem 生成、process:seven-concepts-v 核验）。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
