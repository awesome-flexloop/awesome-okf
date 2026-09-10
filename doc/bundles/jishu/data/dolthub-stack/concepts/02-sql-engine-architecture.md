---
type: concept
title: Interface 驱动的计划树执行架构
description: "go-mysql-server 通过 Node/Expression/Catalog 三大核心接口构建不可变计划树；分析器应用 72 条规则将 AST 转换为可执行计划；NodeExecBuilder 将计划树编译为 RowIter 迭代器"
tags: [sql-engine, node-tree, interface-driven, analyzer, execution-plan, go-mysql-server]
status: stable
stale_after: 2027-03-09
generated:
  by: insight_agent/agnes-2.5-flash
  at: 2026-09-09T15:30:00Z
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: verified
  noted: "基于 facts.md F-046~F-075 验证，Node/Expression/Catalog 接口体系确认"
sources:
  - id: gms-core
    resource: d:\spaces\SpecWeave\external\dao\action\DoltHub\go-mysql-server
    title: go-mysql-server — sql/core.go, sql/catalog.go
---

# Interface 驱动的计划树执行架构

## 核心接口体系

`go-mysql-server` 采用纯 interface 驱动的设计，所有关键组件均通过接口定义，实现与抽象完全解耦。

### Expression 接口

```go
type Expression interface {
    Resolvable
    fmt.Stringer
    Type(ctx *Context) Type
    IsNullable(ctx *Context) bool
    Eval(ctx *Context, row Row) (interface{}, error)
    Children() []Expression
    WithChildren(ctx *Context, children ...Expression) (Expression, error)
}
```

扩展接口：
- `RowIterExpression` — 返回 `RowIter` 而非标量值（集合函数）
- `ExpressionWithNodes` — 子节点为 `Node` 类型（含计划节点的表达式）
- `NonDeterministicExpression` — 标记结果不可缓存（如 `NOW()`、`RAND()`）
- `IsNullExpression` / `IsNotNullExpression` — IS NULL / IS NOT NULL 优化
- `ValueExpression`（实验性）— 替代 `Eval` 的快路径：`EvalValue(ctx, row) (Value, error)`

### Node 接口

```go
type Node interface {
    Resolvable
    fmt.Stringer
    Schema(ctx *Context) Schema
    Children() []Node
    WithChildren(ctx *Context, children ...Node) (Node, error)
    IsReadOnly() bool
}
```

扩展接口：
- `NodeExecBuilder` — `Build(ctx, n Node, r Row) (RowIter, error)` 编译计划节点
- `ExecSourceRel` — 无子节点的执行源（直接实现 `RowIter(ctx, r) (RowIter, error)`）
- `ExecBuilderNode` — 控制自身迭代器但有子节点的节点
- `SchemaTarget` — DDL 操作的 target schema（`WithTargetSchema(Schema) (Node, error)`）
- `Projector` — 返回投影表达式列表（用于 GroupBy/Window/Project）
- `Expressioner` — 返回节点内含的表达式列表
- `OpaqueNode` — 禁止对其子节点进行变换
- `Nameable` / `RenameableNode` / `Tableable` / `CommentedNode`

### Catalog 接口

```go
type Catalog interface {
    DatabaseProvider
    FunctionProvider
    TableFunctionProvider
    ExternalStoredProcedureProvider
    StatsProvider
    CreateDatabase(ctx, dbName, collation) error
    RemoveDatabase(ctx, dbName) error
    Table(ctx, dbName, tableName) (Table, Database, error)
    TableAsOf(ctx, dbName, tableName, asOf) (Table, Database, error)
    LockTable(ctx, table string)
    UnlockTables(ctx, id uint32) error
    AuthorizationHandler() AuthorizationHandler
    Overrides() EngineOverrides
}
```

`CatalogTable` 接口扩展 `Table`，增加 `AssignCatalog(cat Catalog) Table`。

## 执行流水线

```
SQL 字符串
    │
    ▼ vitess sqlparser.Parse()
Statement AST
    │
    ▼ analyzer.Analyze(rules...)
    │   72 条分析规则依次应用
    │   - resolve_database: 解析数据库引用
    │   - resolve_tables: 解析表引用
    │   - resolve_columns: 列名解析
    │   - optimize_joins: 连接优化
    │   - triggers: 触发器加载
    │   - stored_procedures: 存储过程解析
    │   ...（共 ~72 条）
    ▼
Resolved sql.Node 计划树
    │
    ▼ NodeExecBuilder.Build()
RowIter 行迭代器
    │
    ▼ 迭代消费
Result Rows
```

## 不可变节点模式

所有 `WithChildren` 操作返回新节点，不修改原节点。这使得分析器可以在不破坏原始计划的情况下应用变换规则。

## 内置函数体系

`sql/expression/function/` 目录包含约 90 个内置函数，涵盖：
- 字符串函数（`concat`、`substring`、`length` 等）
- 数学函数（`abs`、`ceil`、`floor`、`rand` 等）
- 日期时间函数（`now`、`date`、`time`、`datediff` 等）
- 聚合函数（`count`、`sum`、`avg`、`min`、`max` 等）
- 条件函数（`if`、`case`、`coalesce` 等）
- Dolt 扩展函数（`dolt_*` 系列）
- 向量函数（`distance` 等，支持 `Vector` 类型）

## 信源信息

- **信源距离**: ① 源码目录
- **固定版本**: `v0.20.0`
- **关键文件**: `sql/core.go`、`sql/catalog.go`、`sql/analyzer/analyzer.go`、`sql/analyzer/rules.go`
