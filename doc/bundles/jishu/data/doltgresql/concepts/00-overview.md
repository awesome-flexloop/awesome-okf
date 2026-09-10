---
okf_version: "0.2"
type: concept
id: "concepts-overview"
title: "DoltgreSQL 概述与产品定位"
x-toml-ref: "../../../../../../../../.meta/toml/projects/awesome-okf-xs/doc/bundles/jishu/data/doltgresql/concepts/00-overview.toml"
description: "DoltgreSQL 1.3.0 Beta 版本定位、性能基准（5.2x 慢于原生 Postgres）、sqllogictest 91.17% 正确率、与 Dolt 的关系"
tags:
  - doltgresql
  - postgresql
  - versioned-database
  - overview
  - beta
generated:
  at: "2026-09-09"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
sources:
  - url: "https://github.com/dolthub/doltgresql/blob/main/README.md"
    type: source-code
    title: "dolthub/doltgresql README.md"
    distance: 1
  - url: "https://github.com/dolthub/doltgresql/blob/main/go.mod"
    type: source-code
    title: "dolthub/doltgresql go.mod"
    distance: 1
---
# DoltgreSQL 概述与产品定位

DoltgreSQL 是 DoltHub 开源的 **PostgreSQL 协议兼容的版本化 SQL 数据库**，在 Dolt（Git 式 MySQL 兼容数据库）基础上增加了完整的 PostgreSQL 协议支持。

## 关键数据

| 指标 | 数值 | 说明 |
|------|------|------|
| 当前版本 | **1.3.0** | [F-001](../source.md#f-001) |
| 质量级别 | **Beta** | 自 2025-04-16 起，SQL 接口为主（无 Git CLI）[F-002](../source.md#f-002) |
| 相对性能 | **~5.2x 慢于原生 Postgres** | sysbench 基准测试，v0.50.0 数据 [F-003](../source.md#f-003) |
| sqllogictest 正确率 | **91.16721%** | 5,188,604 / 5,691,305 通过 [F-004](../source.md#f-004) |
| Go 版本 | **1.26.2** | go.mod 要求 [F-005](../source.md#f-005) |
| 核心依赖 | dolthub/dolt/go v0.40.5 + pg_query_go/v6 + go-mysql-server | [F-006](../source.md#f-006) |

## 产品定位

DoltgreSQL 与 Dolt 的关系：

1. **共享存储内核**：两者共用 Dolt 的 Prollly Tree 存储引擎和 RootValue 版本控制机制
2. **协议差异**：Dolt 使用 MySQL 协议，DoltgreSQL 使用 PostgreSQL 协议（PgWire）
3. **类型系统差异**：DoltgreSQL 实现了完整的 `pg_catalog` 系统 schema，包括 `pg_type`、`pg_proc`、`pg_class` 等约 100+ 虚拟表
4. **扩展语言**：DoltgreSQL 支持 plpgsql 存储过程语言（内置解释器）

## 适用场景

- **PostgreSQL 应用迁移到版本控制数据库**：需要保留 PG 语法/类型/函数的场景
- **GitOps 数据管理**：利用 Dolt 的分支/合并能力管理 PG 格式数据
- **数据考古**：通过版本历史回溯数据变更
- **测试/开发环境**：轻量级 PG 兼容数据库，支持快速 fork/clone

## 已知限制

| 限制 | 说明 | 来源 |
|------|------|------|
| 无 Git CLI | Beta 阶段 SQL 接口为主，不提供 dolt CLI 式 Git 操作 | [F-002](../source.md#f-002) |
| UNLOGGED 表不支持 | CREATE TABLE ... UNLOGGED 返回错误 | [F-072](../source.md#f-072) |
| TABLESPACE 不支持 | CREATE TABLE ... TABLESPACE 返回错误 | [F-073](../source.md#f-073) |
| ON CONFLICT 部分支持 | 仅支持 DO NOTHING 和简单 DO UPDATE | [F-075](../source.md#f-075) |
| 别名子查询插入不支持 | INSERT INTO (SELECT ...) 返回错误 | [F-076](../source.md#f-076) |

## 架构一句话

> DoltgreSQL = Dolt 存储内核 + PostgreSQL 协议层 + pg_query_go 解析器 + 自定义 AST 转换器（server/ast/）+ plpgsql 解释器

```{toctree}
:hidden:
```
