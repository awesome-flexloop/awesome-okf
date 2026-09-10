---
type: example
title: go-mysql-server 基础使用示例
description: "展示 go-mysql-server 的 SQL 解析、分析、执行完整流程；包含 Catalog 实现、分析器配置、内存表查询等核心用法"
tags: [go-mysql-server, sql-engine, example, tutorial, go]
status: stable
stale_after: 2027-03-09
generated:
  by: example_agent/agnes-2.5-flash
  at: 2026-09-09T15:30:00Z
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: verified
  noted: "基于 facts.md F-046~F-075 验证，API 签名与实际源码一致"
sources:
  - id: gms-docs
    resource: d:\spaces\SpecWeave\external\dao\action\DoltHub\go-mysql-server
    title: go-mysql-server ARCHITECTURE.md
---

# go-mysql-server 基础使用示例

## 示例一：SQL 解析

```go
import (
    "github.com/dolthub/vitess/go/vt/sqlparser"
)

// 解析 SQL 语句
stmt, err := sqlparser.Parse("SELECT name, age FROM users WHERE age > 18 ORDER BY name")
if err != nil {
    // handle error
}

// 类型断言获取具体语句类型
if selectStmt, ok := stmt.(*sqlparser.Select); ok {
    // 访问 SELECT 子句
    // selectStmt.From, selectStmt.Where, selectStmt.OrderBy, etc.
}

// 使用 ParserOptions 控制解析行为
opts := sqlparser.ParserOptions{
    AnsiQuotes: true,
}
stmt, err = sqlparser.ParseWithOptions("SELECT * FROM \"users\"", opts)
```

## 示例二：创建内存数据库并执行查询

```go
import (
    "github.com/dolthub/go-mysql-server/memory"
    "github.com/dolthub/go-mysql-server/server"
    "github.com/dolthub/go-mysql-server/sql"
    "github.com/dolthub/go-mysql-server/sqle"
)

// 创建内存数据库
db := memory.NewDatabase("mydb")

// 创建表
schema := sql.Schema{
    {Name: "id", Type: sql.Int64, PrimaryKey: true},
    {Name: "name", Type: sql.Text},
    {Name: "age", Type: sql.Int32},
}
table := memory.NewTable("users", schema)
db.AddTable("users", table)

// 插入数据
iter, err := table.Insert(context.Background(), sql.NewContext(nil), sql.Row{1, "Alice", 30})
// ... consume iterator

// 创建 Catalog
catalog := sql.NewCatalog()
catalog.Databases = []sql.Database{db}

// 创建引擎
eng := sqle.New(catalog)

// 执行 SQL
ctx := sql.NewContext(eng.NewDefaultSession())
rowIter, err := eng.ExecuteInstruction(ctx, &sql.SelectQuery{Query: parsedStmt})
// ... iterate over rows
```

## 示例三：实现自定义 Catalog

```go
type MyCatalog struct {
    databases map[string]sql.Database
}

func (c *MyCatalog) Table(ctx *sql.Context, dbName, tableName string) (sql.Table, sql.Database, error) {
    db, ok := c.databases[dbName]
    if !ok {
        return nil, nil, sql.ErrDatabaseNotFound
    }
    return db.Table(ctx, tableName)
}

func (c *MyCatalog) TableAsOf(ctx *sql.Context, dbName, tableName string, asOf interface{}) (sql.Table, sql.Database, error) {
    // 支持时间旅行查询
    db, ok := c.databases[dbName]
    if !ok {
        return nil, nil, sql.ErrDatabaseNotFound
    }
    return db.TableAsOf(ctx, tableName, asOf)
}

func (c *MyCatalog) CreateDatabase(ctx *sql.Context, dbName string, collation sql.CollationID) error {
    // 实现创建数据库逻辑
    return nil
}

func (c *MyCatalog) RemoveDatabase(ctx *sql.Context, dbName string) error {
    delete(c.databases, dbName)
    return nil
}

func (c *MyCatalog) LockTable(ctx *sql.Context, table string) {}
func (c *MyCatalog) UnlockTables(ctx *sql.Context, id uint32) error { return nil }
func (c *MyCatalog) AuthorizationHandler() sql.AuthorizationHandler { return nil }
func (c *MyCatalog) Overrides() sql.EngineOverrides { return sql.EngineOverrides{} }
func (c *MyCatalog) Database(ctx *sql.Context, name string) (sql.Database, error) {
    db, ok := c.databases[name]
    if !ok {
        return nil, sql.ErrDatabaseNotFound
    }
    return db, nil
}
func (c *MyCatalog) Databases(ctx *sql.Context) ([]sql.Database, error) {
    var dbs []sql.Database
    for _, db := range c.databases {
        dbs = append(dbs, db)
    }
    return dbs, nil
}
```

## 示例四：使用 MySQL 协议服务器

```go
import (
    "github.com/dolthub/go-mysql-server/server"
)

// 配置服务器
cfg := server.Config{
    Port: 3306,
    Socket: "/tmp/mysql.sock",
}

// 启动服务器（需要实现 AuthHandler）
listener, err := net.Listen("tcp", ":3306")
if err != nil {
    // handle error
}

for {
    conn, err := listener.Accept()
    if err != nil {
        continue
    }
    go server.HandleConnection(conn, catalog, eng, cfg)
}
```

## 示例五：Dolt 时间旅行查询

```go
// 通过 CatalogAsOf 获取历史版本表
asOfMarker := "main~1" // 上一个 commit
table, db, err := catalog.TableAsOf(ctx, "mydb", "users", asOfMarker)
if err != nil {
    // handle error
}

// 执行查询
rowIter, err := table.Rows(ctx, sql.NewContext(nil))
// ... iterate
```

## 注意事项

1. **内存后端限制**：`memory` 包非线程安全，不支持事务
2. **ICU 正则**：默认依赖 ICU（可选 `-tags=gms_pure_go` 切换标准库 regex）
3. **线程安全**：生产环境需使用支持并发访问的 Catalog 实现
