---
type: example
title: vitess SQL 解析器使用示例
description: "展示 vitess sqlparser 的 SQL 解析、AST 遍历、查询标准化、参数化查询等核心用法"
tags: [vitess, sql-parser, ast, go, example, tutorial]
status: stable
stale_after: 2027-03-09
generated:
  by: example_agent/agnes-2.5-flash
  at: 2026-09-09T15:30:00Z
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: verified
  noted: "基于 facts.md F-026~F-045 验证，Parser API 签名与源码一致"
sources:
  - id: vitess-parser
    resource: d:\spaces\SpecWeave\external\dao\action\DoltHub\vitess
    title: vitess sqlparser 源码
---

# vitess SQL 解析器使用示例

## 示例一：基础 SQL 解析

```go
import (
    "github.com/dolthub/vitess/go/vt/sqlparser"
)

// 解析 SELECT 语句
stmt, err := sqlparser.Parse("SELECT name, age FROM users WHERE age > 18 ORDER BY name LIMIT 10")
if err != nil {
    // handle parse error
}
// stmt 类型为 sqlparser.Statement（接口）

// 类型断言
if selectStmt, ok := stmt.(*sqlparser.Select); ok {
    // 访问 FROM 子句
    for _, from := range selectStmt.From {
        // from 是 *sqlparser.AliasedTableExpr
    }
    // 访问 WHERE 子句
    if selectStmt.Where != nil {
        // where 是 *sqlparser.Expr
    }
    // 访问 ORDER BY
    for _, order := range selectStmt.OrderBy {
        // order.Direction: sqlparser.AscOrder / sqlparser.DescOrder
    }
    // 访问 LIMIT
    if selectStmt.Limit != nil {
        // selectStmt.Limit.RowCount, selectStmt.Limit.Offset
    }
}
```

## 示例二：解析 DDL 语句

```go
// CREATE TABLE
stmt, err := sqlparser.Parse(`
    CREATE TABLE users (
        id INT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
`)
if ddl, ok := stmt.(*sqlparser.DDL); ok {
    // ddl.Action: Create, Alter, Drop, Truncate
    // ddl.Table: TableName
    // ddl.Definition: *TableDef（列定义）
}

// ALTER TABLE
stmt, err = sqlparser.Parse("ALTER TABLE users ADD COLUMN phone VARCHAR(20)")
if ddl, ok := stmt.(*sqlparser.DDL); ok {
    // ddl.Action: Alter
}
```

## 示例三：查询标准化（用于缓存 key）

```go
import (
    "github.com/dolthub/vitess/go/vt/sqlparser"
)

// 标准化查询：将字面量替换为绑定变量，便于缓存
normalized, err := sqlparser.Normalize("SELECT * FROM users WHERE id = 123 AND name = 'Alice'")
// normalized: "SELECT * FROM users WHERE id = ? AND name = ?"
// 可用于生成缓存 key
```

## 示例四：参数化查询（Prepared Query）

```go
// 预处理带绑定变量的查询
parsed, err := sqlparser.Parse("SELECT * FROM users WHERE age > ? AND name = ?")
pq := sqlparser.ParsedQuery{
    Query: "SELECT * FROM users WHERE age > %? AND name = %?",
    BindVars: map[string]*querypbBindVariable{
        "v1": {Type: querypb.Type_INT64, Value: []byte("18")},
        "v2": {Type: querypb.TypeVarChar, Value: []byte("Alice")},
    },
}
// pq.GenerateQuery() 生成最终执行的 SQL
```

## 示例五：AST 遍历与重写

```go
import (
    "github.com/dolthub/vitess/go/vt/sqlparser"
)

// 使用 TreeRewriter 遍历并重写 AST
rewriter := sqlparser.NewTreeRewriter()

// 注册回调：在遍历到特定节点时执行自定义逻辑
rewriter.OnSelect = func(s *sqlparser.Select) {
    // 可以对 SELECT 节点进行修改
}

rewriter.OnTableExpr = funcExpr *sqlparser.AliasedTableExpr) {
    // 可以修改表表达式
}

// 执行重写
newStmt := rewriter.REWrite(stmt)
```

## 示例六：注释处理

```go
// 解析包含注释的 SQL
stmt, err := sqlparser.Parse(`
    /* This is a block comment */
    SELECT /* inline comment */ name, age
    FROM users
    -- line comment
    WHERE age > 18
`)
// 设置 AllowComments 以保留注释
opts := sqlparser.ParserOptions{
    AllowComments: true,
}
stmt, err = sqlparser.ParseWithOptions(sql, opts)
```

## 示例七：SQL 模式配置

```go
import (
    "github.com/dolthub/vitess/go/vt/sqlparser"
    "github.com/dolthub/vitess/go/vt/sqlmode"
)

// 配置 SQL 模式
opts := sqlparser.ParserOptions{
    SQLMode: sqlmode.AnsiQuotes | sqlmode.StrictTransTables,
}

// AnsiQuotes 模式下，双引号用于标识符而非字符串
stmt, err := sqlparser.ParseWithOptions(`SELECT "name" FROM "users"`, opts)
```

## 注意事项

1. **语句终止**：默认解析单条语句，`ParserOptions.StopAfterFirstStmt` 控制行为
2. **嵌套深度**：最大嵌套深度 200 层，超过则报错
3. **线程安全**：解析器本身线程安全（通过 Pool），但 `ParsedQuery` 非线程安全
4. **DoltHub 扩展**：`*DDL`、`*Call`、触发器相关节点为 DoltHub fork 特有
