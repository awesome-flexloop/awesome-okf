---
type: concept
title: QueryFactory 工厂模式
description: 通过继承链支持 6 种数据库类型的统一查询工厂模式
tags: [dolt-workbench, query-factory, design-pattern, abstraction]
status: stable
generated:
  by: reference_agent/agnes-2.5-flash
  at: 2026-09-09T04:00:00Z
sources:
  - id: qf-index
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/graphql-server/src/queryFactory/index.ts
    title: QueryFactory 接口定义
  - id: qf-base
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/graphql-server/src/queryFactory/base.ts
    title: BaseQueryFactory 抽象基类
  - id: qf-conn
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/graphql-server/src/connections/connection.provider.ts
    title: ConnectionProvider 工厂选择逻辑
---

# QueryFactory 工厂模式

## 设计目标

QueryFactory 是 dolt-workbench 的核心抽象层，旨在为 6 种数据库类型（MySQL、PostgreSQL、Dolt、Doltgres、SQLite、DoltLite）提供统一的查询接口。

## 继承体系

```
BaseQueryFactory (abstract)
  └── MySQLQueryFactory (isDolt=false)
        ├── PostgresQueryFactory (isDolt=false)
        │     └── DoltgresQueryFactory (isDolt=true)
        ├── SqliteQueryFactory (isDolt=false)
        │     └── DoltLiteQueryFactory (isDolt=true)
        └── DoltQueryFactory (isDolt=true)
```

关键设计决策：
- `DoltQueryFactory` 继承自 `MySQLQueryFactory`（因为 Dolt 使用 MySQL 协议）
- `DoltgresQueryFactory` 继承自 `PostgresQueryFactory`（因为 Doltgres 使用 PostgreSQL 协议）
- `DoltLiteQueryFactory` 继承自 `SqliteQueryFactory`（因为 DoltLite 使用 SQLite 存储）
- 每个具体实现通过 `isDolt` 标记区分是否为 Dolt 系列数据库

## BaseQueryFactory 基类

提供通用的查询能力：

```typescript
abstract class BaseQueryFactory {
  // 数据源获取
  getDS(databaseName?: string): DataSource
  getQR(databaseName?: string, queryRunner?: QueryRunner): QueryRunner
  
  // 异步查询处理
  handleAsyncQuery<T>(fn: (qr: QueryRunner) => Promise<T>, ...): Promise<T>
  
  // 查询执行
  query<T>(sql: string, params?: any[]): Promise<T[]>
  queryMultiple<T>(fn: (query: QueryFn) => Promise<T>, ...): Promise<T>
  queryForBuilder<T>(fn: (query: QueryFn) => Promise<T[]>, ...): Promise<T[]>
  queryQR<T>(fn: (qr: QueryRunner) => Promise<T[]>, ...): Promise<T[]>
  
  // 数据库管理
  currentDatabase(): Promise<string>
  createDatabase(name: string): Promise<void>
}
```

## 自动检测逻辑

`connection.provider.ts` 中的 `newQueryFactory(type, ds)` 函数实现数据库类型自动检测：

```typescript
function newQueryFactory(type: string, ds: DataSource): QueryFactory {
  // Postgres → 先尝试检测 Doltgres
  if (type === DatabaseType.Postgres) {
    const doltgresCheck = ds.createQueryRunner();
    const hasDoltVersion = await checkDoltgres(doltgresCheck);
    return hasDoltVersion 
      ? new DoltgresQueryFactory(ds) 
      : new PostgresQueryFactory(ds);
  }
  
  // SQLite → 先尝试检测 DoltLite
  if (type === DatabaseType.Sqlite) {
    const doltliteCheck = ds.createQueryRunner();
    const hasDoltLite = await checkDoltLite(doltliteCheck);
    return hasDoltLite 
      ? new DoltLiteQueryFactory(ds) 
      : new SqliteQueryFactory(ds);
  }
  
  // MySQL → 先尝试检测 Dolt
  if (type === DatabaseType.Mysql) {
    const doltCheck = ds.createQueryRunner();
    const hasDolt = await checkDolt(doltCheck);
    return hasDolt 
      ? new DoltQueryFactory(ds) 
      : new MySQLQueryFactory(ds);
  }
}
```

检测 SQL：
- Dolt/Doltgres: `SELECT dolt_version()`
- DoltLite: `SELECT doltlite_engine()`

## 方法分组（50+ 方法）

### UTILS（工具方法）
- `getDS()` — 获取 DataSource
- `getQR()` — 获取 QueryRunner
- `handleAsyncQuery()` — 异步查询处理器
- `query()` — 执行 SQL
- `queryMultiple()` — 多步查询
- `queryForBuilder()` — 构建器查询
- `queryQR()` — QueryRunner 查询

### QUERIES（标准查询）
- `databases()` / `currentDatabase()` — 数据库管理
- `schemas()` / `createSchema()` — Schema 管理
- `getTableNames()` / `getTables()` / `getTableInfo()` — 表信息
- `getTablePKColumns()` — 主键列
- `getTableRows()` — 表行数据
- `getSqlSelect()` / `selectTableRows()` — SQL 查询
- `deleteRow()` / `insertRow()` / `updateRow()` / `previewInsertRow()` — DML
- `dropColumn()` / `dropTable()` — DDL
- `createView()` / `callProcedure()` — 视图和存储过程
- `doltCommitDiff()` / `doltCellDiff()` / `doltCellHistory()` — Dolt diff
- `schemaDefinition()` — Schema 定义
- `saveDoc()` / `deleteDoc()` — 文档管理
- `getSchemas()` / `getProcedures()` — 元数据

### DOLT-SPECIFIC（Dolt 专属）
- `getTableRowsWithDiff()` / `getWorkingDiffRows()` — 带 diff 的行
- `getBranch()` / `getBranches()` / `getRemoteBranches()` / `getAllBranches()` — 分支
- `createNewBranch()` / `callDeleteBranch()` — 分支操作
- `callDoltClone()` — 克隆
- `getLogs()` / `getTwoDotLogs()` — 提交日志
- `getDiffStat()` / `getThreeDotDiffStat()` — Diff 统计
- `getDiffSummary()` / `getThreeDotDiffSummary()` — Diff 摘要
- `getSchemaPatch()` / `getThreeDotSchemaPatch()` — Schema patch
- `getSchemaDiff()` / `getThreeDotSchemaDiff()` — Schema diff
- `getDocs()` — 文档
- `getStatus()` — 状态
- `getTag()` / `getTags()` / `createNewTag()` / `callDeleteTag()` — Tag 操作
- `callMerge()` / `callMergeWithResolveConflicts()` — 合并
- `resolveRefs()` — 引用解析
- `getOneSidedRowDiff()` / `getRowDiffs()` — 行 diff
- `getPullConflictsSummary()` / `getPullRowConflicts()` — Pull 冲突
- `restoreAllTables()` — 恢复表
- `getRemotes()` / `addRemote()` / `callDeleteRemote()` — Remote 管理
- `callPullRemote()` / `callPushRemote()` / `callFetchRemote()` — 远程操作
- `callCreateBranchFromRemote()` — 从远程创建分支
- `getMergeBase()` — 获取 merge-base
- `getTests()` / `runTests()` / `saveTests()` — 测试管理

## Build 目录（查询构建器）

`queryFactory/build/` 提供类型安全的 SQL 构建：

| 构建函数 | 功能 |
|---|---|
| `buildSelectTableRows` | 表行查询构建 |
| `buildInsertRow` | 行插入构建 |
| `buildUpdateRow` | 行更新构建 |
| `buildDeleteRow` | 行删除构建 |
| `buildDropTable` | 表删除构建 |
| `buildDropColumn` | 列删除构建 |
| `buildCreateView` | 视图创建构建 |
| `buildCallProcedure` | 存储过程调用构建 |
| `buildDoltCommitDiff` | 提交 diff 构建 |
| `buildDoltCellDiff` | 单元格 diff 构建 |
| `buildDoltCellHistory` | 单元格历史构建 |
| `buildSchemaDefinition` | Schema 定义构建 |
| `buildSaveDoc` | 文档保存构建 |
| `buildUtils` | 通用工具函数 |

## 类型定义

`types.ts` 定义的核心类型（190+ 行）：

```typescript
// 参数类型
type DBArgs = { databaseName: string }
type CloneArgs = { remoteUrl: string; dbName: string; branchName?: string }
type SchemaArgs = { databaseName: string; schemaName: string }
type RefArgs = { databaseName: string; refName?: string }
type TableArgs = { databaseName: string; refName?: string; tableName: string }

// 行类型
type RawRow = Record<string, any>
type RawRowWithDiff = RawRow & { diff?: WorkingDiff }
type RawRows = RawRow[]
type RawRowsWithDiff = RawRowWithDiff[]

// 结果类型
type SqlSelectResult = { columns: Column[]; rows: Row[]; warnings?: string[] }
type MutationResult = { affectedRows: number; message: string }
type DiffRes = { diff: string; stats: DiffStat }
type CommitsRes = { commits: Commit[] }

// 辅助类型
type ColumnValue = { column: string; value?: string | null; type?: string }
type OrderByClause = { column: string; direction: "ASC" | "DESC" }
```

## 参考文档

- [架构总览](./01-architecture.md)
- [DoltLite Revision 缓存](./03-dolt-lite-revision-cache.md)
