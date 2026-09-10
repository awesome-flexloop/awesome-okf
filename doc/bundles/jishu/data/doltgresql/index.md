---
okf_version: "0.2"
type: bundle-index
id: "doltgresql-index"
title: "DoltgreSQL — PostgreSQL 兼容的版本化 SQL 数据库"
x-toml-ref: "../../../../../../../.meta/toml/projects/awesome-okf-xs/doc/bundles/jishu/data/doltgresql/index.toml"
description: "DoltgreSQL 知识包：基于 Go 的 PostgreSQL 协议兼容数据库，核心为 AST 转换层（pg_query_go → Vitess/GMS）+ Dolt RootValue 扩展 + plpgsql 解释器；1.3.0 Beta 质量级，sqllogictest 正确率 91.17%；含架构全景、RootValue 设计、类型系统、函数注册表等核心机制的源码级教程"
tags:
  - doltgresql
  - postgresql
  - versioned-database
  - ast-conversion
  - rootvalue
  - plpgsql
  - go
generated:
  at: "2026-09-09"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
  noted: "F-001~F-120 全部事实经本地源码逐行核验；GATE-SPS 预检通过（env-bound clone，commit 27ed792b）"
stale_after: "2027-03-09"
sources:
  - url: "https://github.com/dolthub/doltgresql"
    type: source-code
    title: "dolthub/doltgresql — GitHub 主仓源码（HEAD 27ed792b6e67dab9e0cd1bdd14817f203ec63d8e）"
    distance: 1
  - url: "https://github.com/dolthub/doltgresql/blob/main/README.md"
    type: official
    title: "DoltgreSQL README"
    distance: 1
status: stable
---
# DoltgreSQL — PostgreSQL 兼容的版本化 SQL 数据库

本知识包基于本地 `external/dao/action/DoltHub/doltgresql` 源码仓库（HEAD 27ed792b，版本 1.3.0，Beta 质量级）系统性解读，经 P0 权威核验后结构化产出 OKF v0.2 合规 wiki。

**核心发现**：DoltgreSQL 通过三层架构实现 PostgreSQL 兼容——PostgreSQL SQL Parser（pg_query_go）→ 自定义 AST 转换层（server/ast/）→ Vitess/GMS 执行引擎。其独创性在于将 Dolt 的 RootValue 架构扩展为承载 pg_catalog 完整类型系统的 RootObject 集合，并通过 contextValues 缓存机制实现 collection 级性能优化。

所有内容溯源至 [F-001 ~ F-120](references/source.md)，遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 导航

### 核心概念（concepts/）

* [DoltgreSQL 概述与产品定位](concepts/00-overview.md) — 版本、质量级、性能基准、sqllogictest 通过率、与原生 PostgreSQL 对比
* [三层架构与数据流](concepts/01-architecture.md) — PG 解析层 → AST 转换层 → GMS 执行层；Handler/Listener 接口；两种启动模式
* [RootValue 扩展与 RootObject 集合](concepts/02-rootvalue-and-collections.md) — RootValue 核心结构、11 种 root object collection、contextValues 缓存、差异写回机制
* [AST 转换机制](concepts/03-ast-conversion.md) — pg_query_go → tree 节点 → vitess.Statement 全链路；表达式/DDL/DML 转换；未支持特性清单
* [类型系统与 pg_type](concepts/04-type-system.md) — DoltgresType 100+ 字段、TypeCategory 枚举、encoding 映射、globalFunctionRegistry
* [plpgsql 解释器与函数系统](concepts/05-plpgsql-and-functions.md) — OpCode 23 种操作码、InterpreterStack、RoutineParam、内置函数注册

### 实操示例（examples/）

> 当前环境未安装 doltgresql 二进制，示例以源码对照形式呈现。

* [启动 DoltgreSQL 服务器](examples/00-server-launch.md) — 磁盘模式 vs 内存模式、环境变量配置、TLS 配置
* [pg_catalog 虚拟表查询](examples/01-pgcatalog-queries.md) — pg_type/pg_proc/pg_class/pg_sequence 等核心系统表
* [plpgsql 函数编写与调用](examples/02-plpgsql-functions.md) — CREATE FUNCTION、OpCode 流程、INTERPRETER 模式

### 信源与核验（references/）

* [源码事实登记](references/source.md) — F-001~F-120 全部事实编号登记（25 章节，120 条源码事实）

## 学习路径建议

1. **入门**：[DoltgreSQL 概述](concepts/00-overview.md) → [三层架构](concepts/01-architecture.md) → [RootValue 扩展](concepts/02-rootvalue-and-collections.md)
2. **深入**：[AST 转换机制](concepts/03-ast-conversion.md) → [类型系统](concepts/04-type-system.md) → [plpgsql 解释器](concepts/05-plpgsql-and-functions.md)
3. **实操参考**：[examples/](examples/) 三篇源码对照示例
4. **溯源**：阅读 [references/source.md](references/source.md) 核对全部 F 编号（F-001~F-120）

## 骨架判定说明

- **一问**（有读者可照做的安装/配置/代码/调用流程？）：✅ 满足。examples/ 三篇提供启动/查询/函数编写的完整源码对照流程。
- **二问**（经作者实测、有版本/输入输出/步骤顺序？）：当前环境未安装 doltgresql，示例以源码对照形式呈现（非实测输出），保留完整命令形态与实现路径。
- **结论**：本 bundle 定位为"源码级架构教程"，覆盖从产品认知到核心机制实现的完整链路。

## 信任与生命周期说明

- **status 判定依据**：`stable`。120 条源码事实经本地仓库逐行核验；Beta 质量级为官方声明（README.md）。
- **stale_after 解释**：设为 `2027-03-09`。DoltgreSQL 处于快速发展期（当前 1.3.0 Beta），6 个月后重新评估稳定性。
- **核验链路**：`generated.at` 2026-09-09（process:source-code-to-okf-wiki 生成）；`verified.at` 2026-09-09（process:seven-concepts-v 核验）。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/source
examples/index
```
