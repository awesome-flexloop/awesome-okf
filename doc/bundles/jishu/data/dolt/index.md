---
okf_version: "0.2"
type: bundle-index
title: "Dolt — 版本化 SQL 数据库"
description: "Dolt 知识包：从存储层原生支持 Git 式版本控制的 SQL 数据库——行级历史、分支/合并、MySQL/PostgreSQL/SQLite/MongoDB 多协议生态、MCP Server 与 AI Agent 安全操作、Dolt Workbench；含博文 P0 核验、勘误，以及基于本地 DoltHub 主仓源码（v2.3.2）的分层全景教程（CLI 层 → SQL 层 → 存储内核层 → 生态层）"
tags:
  - dolt
  - git
  - sql
  - mysql
  - version-control
  - database
  - mcp
  - prolly-tree
  - cli
  - storage-engine
generated:
  at: "2026-09-08"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
  noted: "F-042 口径需细化（Sysbench 读写已超越 MySQL），F-045 勘误（Web UI 限制误读）；2026-09-09 基于本地 DoltHub 源码补登 F-073~F-085（多协议生态 + 存储引擎架构）；2026-09-09 深化扩展：新增 F-086~F-192 共 107 条主仓源码事实（CLI/SQL/存储内核/生态四层面），新增 concepts/03~06 + examples/，bundle 升级为分层全景教程"
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
  - url: "https://docs.dolthub.com/"
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
  - url: "https://github.com/dolthub/dolt"
    type: source-code
    title: "dolthub/dolt 主仓源码（go/cmd/dolt/cli/command.go、go/libraries/doltcore/doltdb/、go/store/nbs/、go/store/prolly/ 等，HEAD 65bd3306b0，tag v2.3.2）"
    distance: 1
status: stable
---

# Dolt — 版本化 SQL 数据库

本知识包基于微信公众号「开源日记」博文《数据库也能像 Git 一样进行 fork、branch 和 merge 吗？》（2026-06-18）生成，经 [P0 权威核验报告](references/verification.md) 交叉验证，对勘误项标注官方正确口径；并于 2026-09-09 基于本地 `dolthub` 组织源码（12 仓库）补登源码事实（F-073~F-085），将产品矩阵扩展为多协议生态。

**2026-09-09 深化扩展**：基于本地 `dolthub/dolt` 主仓源码（HEAD 65bd3306b0，tag v2.3.2），新增 CLI 命令层（concepts/03）、SQL 版本控制 API 层（concepts/04）、存储内核层（concepts/05）、生态与工作流层（concepts/06）及 examples/ 四篇实操示例，将 bundle 从"技术综述"升级为"分层全景教程"。新增源码事实 F-086~F-192 共 107 条。

所有内容溯源至 [F-001 ~ F-192](references/source.md)，遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

> **⚠️ 勘误提示**：博文所述"超过 1G 数据会变慢"（F-045）为误读，系将 DoltHub Web UI 查询超时限制（约 1GB，2021 年过时信息）泛化为 Dolt 数据库本身能力限制。Dolt 生产环境可处理 TB 级数据。正确口径见 [F-060](references/article-source.md) 与 [verification.md](references/verification.md)。

## 导航

### 核心概念（concepts/）

#### 第一层：发布事实层（博文层）

* [Dolt 概述与产品矩阵](concepts/00-dolt-overview.md) — 产品定位、核心功能、产品矩阵（Dolt/DoltHub/DoltLab/Hosted Dolt/MCP/Workbench）、开源协议与多协议生态（12 仓库）
* [行级版本控制机制](concepts/01-dolt-versioning-mechanism.md) — Prolly Tree 存储、行级历史视图、分支/合并/回滚、MySQL 兼容原理、MCP/AI Agent 工作流
* [边界、限制与选型建议](concepts/02-dolt-boundaries-trends.md) — TPC-C 54% 性能、1G 阈值勘误、迁移成本、适用场景、选型启示

#### 第二层：源码实现层（分层深入）

* [CLI 命令体系架构](concepts/03-dolt-cli-architecture.md) — main() 入口、Command 接口、SubCommandHandler 分发、DoltEnv 环境模型、Ref 系统、哈希规范、ChunkStore 接口
* [SQL 版本控制 API](concepts/04-sql-version-control-api.md) — dprocedures（38 条）/dfunctions（10 个）/dtablefunctions（13 个）、SQL 引擎集成、HistoryTable、SessionDatabase、事务与 Merge/Conflict
* [存储内核架构](concepts/05-storage-kernel-architecture.md) — NBS 内容寻址 DAG、Prolly Tree（NodeStore/Map）、Flatbuffer 序列化、DoltDB 高层句柄、Commit 模型
* [生态与工作流](concepts/06-dolt-ecosystem-and-workflows.md) — 远程操作、系统表全景、GraphQL API、Web 服务器、AI Agent 指南、测试基准、凭据管理

### 实操示例（examples/）

> 当前环境未安装 `dolt`，示例以源码对照形式呈现（每条命令附带源码文件锚点），方便查阅实现细节。

* [CLI 核心工作流](examples/00-cli-workflow.md) — init/sql server/分支+提交/合并冲突/历史差异/远程操作/MCP 工具映射
* [SQL 版本控制](examples/01-sql-version-control.md) — 存储过程调用/标量函数/表函数/历史表查询/系统表/事务控制
* [分支合并工作流](examples/02-branch-merge-workflow.md) — 完整分支开发流程/三种冲突类型详解/回退操作
* [系统表与测试](examples/03-system-tables-and-testing.md) — 系统表全景/Schema 查询/统计信息/测试基础设施/Benchmark/导入导出/GraphQL

### 信源与核验（references/）

* [博文信源登记](references/article-source.md) — F-001~F-085 全部事实编号登记（博文 72 + 源码补登 13）
* [主仓源码事实登记](references/source.md) — F-086~F-192 全部源码事实登记（107 条，29 章节）
* [P0 权威核验报告](references/verification.md) — 9 项 P0 声明核验结论 + 勘误四张清单

## 学习路径建议

1. **入门**：[Dolt 概述](concepts/00-dolt-overview.md) → [行级版本控制机制](concepts/01-dolt-versioning-mechanism.md) → [边界与选型建议](concepts/02-dolt-boundaries-trends.md)
2. **进阶（源码阅读）**：[CLI 架构](concepts/03-dolt-cli-architecture.md) → [SQL API 层](concepts/04-sql-version-control-api.md) → [存储内核](concepts/05-storage-kernel-architecture.md) → [生态工作流](concepts/06-dolt-ecosystem-and-workflows.md)
3. **实操参考**：[examples/](examples/) 四篇源码对照示例
4. **溯源**：阅读 [references/article-source.md](references/article-source.md) + [references/source.md](references/source.md) 核对全部 F 编号（F-001~F-192），查阅 [verification.md](references/verification.md) 了解核验细节

## 骨架判定说明

- **一问**（有读者可照做的安装/配置/代码/调用流程？）：✅ 满足。examples/ 四篇提供 CLI/SQL/分支合并/系统表的完整源码对照工作流，每条命令均附源码文件锚点。
- **二问**（经作者实测、有版本/输入输出/步骤顺序？）：当前环境未安装 `dolt`，示例以源码对照形式呈现（非实测输出），但仍保留完整命令形态与实现路径，供有 dolt 环境的读者直接运行。
- **结论**：本 bundle 包含完整的 concepts/（6 篇）+ examples/（4 篇）+ references/（3 篇），定位"分层全景教程"，覆盖从产品认知到源码实现的完整学习链路。

## 信任与生命周期说明

- **status 判定依据**：`stable`。9 项 P0 声明核验完成，7 项 ✅，1 项 ⚠️（F-042 口径保守），1 项 ❌（F-045 勘误已补充官方正确口径 F-060）；F-086~F-192 源码事实经本地主仓源码逐行核验。
- **stale_after 解释**：设为 `2026-12-31`。Dolt 为快速发展产品（v2.0+ 版本迭代频繁），性能数据（TPC-C 54%、Sysbench 基准）时效性强，年末重新评估。
- **核验链路**：`generated.at` 2026-09-08（spec:okf-wiki-ecosystem 生成）；`verified.at` 2026-09-09（process:seven-concepts-v 核验 + 深化扩展核验）。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
examples/index
log
```
