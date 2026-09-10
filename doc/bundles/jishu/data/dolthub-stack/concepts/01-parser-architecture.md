---
type: concept
title: Yacc 生成式 SQL 解析器架构
description: "vitess sqlparser 基于 goyacc 从 sql.y 语法文件生成 LL(1) 解析器；支持 Parser pooling、AST 遍历重写、查询标准化；DoltHub fork 在 AST 层面扩展了 DDL/存储过程/触发器节点"
tags: [sql-parser, yacc, vitess, ast, goyacc, grammar]
status: stable
stale_after: 2027-03-09
generated:
  by: insight_agent/agnes-2.5-flash
  at: 2026-09-09T15:30:00Z
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: verified
  noted: "基于 facts.md F-026~F-045 验证，sql.y→sql.go 生成链路确认"
sources:
  - id: vitess-parser
    resource: d:\spaces\SpecWeave\external\dao\action\DoltHub\vitess
    title: vitess (DoltHub fork) - SQL parser
---

# Yacc 生成式 SQL 解析器架构

## 核心机制

`vitess/sqlparser` 是一个基于 `goyacc`（Go 版 Yacc）生成的 LL(1) SQL 解析器。语法定义在 `sql.y` 文件中，通过 `//go:generate goyacc -o sql.go sql.y` 命令生成 `sql.go`。生成的文件头部明确标注 `DO NOT EDIT`，禁止手动修改。

## 解析流程

```
SQL 字符串
    │
    ▼
Tokenizer.Next()          ← 词法分析（token.go）
    │
    ▼
yyParsePooled(yyLexer)    ← 语法分析（sql.go，由 goyacc 生成）
    │
    ▼
Statement AST             ← 抽象语法树（ast.go）
    │
    ▼
TreeRewriter            ← AST 遍历重写（normalizer.go）
    │
    ▼
Normalized Statement      ← 标准化后的查询
```

## 关键组件

### Tokenizer（词法分析器）

`token.go` 中的 `Tokenizer` 结构体负责将 SQL 字符串拆分为 token 序列。包含字段：
- `ParseTree Statement` — 解析结果
- `AllowComments bool` — 是否允许注释
- `nesting int` — 嵌套深度（上限 200）
- `stopped bool` — 是否已遇到语句终止符

### Parser Pooling（解析器池）

`sql.go` 中的 `yyParsePooled` 函数使用 `sync.Pool` 复用 `yyParserImpl` 对象，避免频繁分配和 GC 压力。规则文件中禁止直接引用栈变量（需通过中间变量中转）。

### AST 节点体系

`ast.go` 定义了两类核心接口：
- `Statement` — 所有 SQL 语句的根接口，实现类型包括 `*Select`、`*Insert`、`*Update`、`*Delete`、`*DDL`、`*Show`、`*Set`、`*Call`、`*Begin`、`*Commit`、`*Rollback`、`*Grant`、`*Revoke`、`*Create`、`*Drop`、`*Alter`、`*TruncateTable`、`*Replace`
- `Expr` — 所有表达式的根接口，实现类型包括 `*Literal`、`*ColName`、`*BinaryExpr`、`*UnaryExpr`、`*FuncExpr`、`*CastExpr`、`*Subquery`、`*ExistsExpr`、`*CaseExpr` 等约 30 种

### ParserOptions（解析选项）

`ast.go` 中的 `ParserOptions` 结构体控制解析行为：
- `AnsiQuotes bool` — 双引号是否作为标识符引号（SQL92 标准）
- `SQLMode sqlmode.SQLMode` — MySQL SQL 模式
- `StopAfterFirstStmt bool` — 是否只解析第一条语句

### 关键词表

`keywords.go` 中 `keywords map[string]int` 映射所有 MySQL 兼容关键字（包括保留字和非保留字）到 token 值。新增关键字需同步更新 `sql.y` 中的 `reserved_keywords` 或 `non_reserved_keywords` 规则。

## DoltHub Fork 扩展

与上游 Vitess 相比，DoltHub fork 在 AST 层面做了以下扩展：
1. **DDL 语句支持**：完整的 `CREATE TABLE`、`ALTER TABLE`、`DROP TABLE` 等 AST 节点
2. **存储过程支持**：`*Call` 节点及 `stored_procedure.go` 计划节点
3. **触发器支持**：触发器定义和执行的相关 AST 节点
4. **代码剪枝**：移除了 90% 的非核心功能（如 VTGate、VTTablet 等集群相关代码）

## 信源信息

- **信源距离**: ① 源码目录
- **固定版本**: `vitess-parent-3.0.0`
- **关键文件**: `go/vt/sqlparser/sql.go`、`go/vt/sqlparser/ast.go`、`go/vt/sqlparser/token.go`、`go/vt/sqlparser/keywords.go`
