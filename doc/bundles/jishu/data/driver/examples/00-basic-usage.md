---
type: Example
title: 基本用法：从 DSN 到事务提交
description: "基于 example/main.go 的完整可运行代码路径：解析 DSN、配置 BackOff 重试、创建表、Prepare/Exec、事务提交。F-002、F-008、F-014~F-015。"
tags: [driver, dolt, example, getting-started]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: driver-repo
    resource: https://github.com/dolthub/driver
    title: dolthub/driver（官方仓库）
  - id: driver-local
    resource: "本地克隆（tag v2.2.0-18，commit 61ccedb7035925b3e4a5f91be6bd68b100e3b1e7）"
    title: driver 源码逐文件精读
---

# 基本用法：从 DSN 到事务提交

> **对应 F 编号**：F-002、F-008、F-014~F-015

## 最小可运行示例

以下代码来自 [example/main.go](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/example/main.go)，展示了从 DSN 解析到事务提交的完整流程：

```go
package main

import (
    "context"
    "database/sql"
    "fmt"
    "os"

    "github.com/cenkalti/backoff/v4"
    embedded "github.com/dolthub/driver/v2"
)

func main() {
    if len(os.Args) != 2 {
        fmt.Println("usage: example file:///path/to/dbs?commitname=X&commitemail=Y&database=Z")
        return
    }

    ctx := context.Background()
    dataSource := os.Args[1]

    // 1. 解析 DSN
    cfg, err := embedded.ParseDSN(dataSource)
    if err != nil {
        fmt.Fprintf(os.Stderr, "failed to parse DSN: %v\n", err)
        os.Exit(1)
    }

    // 2. 可选：配置 BackOff 重试（应对锁冲突）
    cfg.BackOff = backoff.NewExponentialBackOff()

    // 3. 创建 Connector（推荐 API，非 Open()）
    connector, err := embedded.NewConnector(cfg)
    if err != nil {
        fmt.Fprintf(os.Stderr, "failed to create connector: %v\n", err)
        os.Exit(1)
    }
    defer connector.Close()

    // 4. 通过 sql.OpenDB 获取 *sql.DB
    db := sql.OpenDB(connector)
    if err := db.PingContext(ctx); err != nil {
        fmt.Fprintf(os.Stderr, "failed to ping: %v\n", err)
        os.Exit(1)
    }

    // 5. 建库建表（多语句模式）
    _, err = db.ExecContext(ctx, "CREATE DATABASE IF NOT EXISTS testdb; USE testdb;")
    if err != nil {
        fmt.Fprintf(os.Stderr, "create db failed: %v\n", err)
        os.Exit(1)
    }

    _, err = db.ExecContext(ctx, `
        CREATE TABLE IF NOT EXISTS t1 (
            pk   int PRIMARY KEY,
            c1   varchar(512),
            c2   float,
            c3   bool,
            c4   datetime
        );
    `)
    if err != nil {
        fmt.Fprintf(os.Stderr, "create table failed: %v\n", err)
        os.Exit(1)
    }

    // 6. 批量插入（INSERT 语句）
    _, err = db.ExecContext(ctx, `
        REPLACE INTO t1 VALUES
            (1, 'test',      0.0,  0, '1998-01-23 12:45:56'),
            (2, 'another',   1.0,  1, '2010-12-31 01:15:00'),
            (3, NULL,        3.335,0, NULL),
            (4, 'final',     3.5,  1, '2015-04-03 14:00:45');
    `)
    if err != nil {
        fmt.Fprintf(os.Stderr, "insert failed: %v\n", err)
        os.Exit(1)
    }

    // 7. 查询
    rows, err := db.QueryContext(ctx, "SELECT * FROM t1;")
    if err != nil {
        fmt.Fprintf(os.Stderr, "query failed: %v\n", err)
        os.Exit(1)
    }
    defer rows.Close()

    cols, _ := rows.Columns()
    fmt.Println("columns:", cols)
    for rows.Next() {
        vals := make([]interface{}, len(cols))
        ptrs := make([]interface{}, len(cols))
        for i := range ptrs {
            ptrs[i] = &vals[i]
        }
        rows.Scan(ptrs...)
        fmt.Println(vals)
    }

    // 8. 事务（含多语句）
    tx, err := db.Begin()
    if err != nil {
        fmt.Fprintf(os.Stderr, "begin tx failed: %v\n", err)
        os.Exit(1)
    }

    // 事务内多语句
    _, err = tx.ExecContext(ctx, `
        INSERT INTO t1 VALUES (5, 'tx1', 4.0, 0, now());
        INSERT INTO t1 VALUES (6, 'tx2', 7.0, 1, now()), (7, 'tx3', 8.1, 0, now());
    `)
    if err != nil {
        tx.Rollback()
        fmt.Fprintf(os.Stderr, "tx insert failed: %v\n", err)
        os.Exit(1)
    }

    if err := tx.Commit(); err != nil {
        fmt.Fprintf(os.Stderr, "commit failed: %v\n", err)
        os.Exit(1)
    }
}
```

## DSN 格式

```
file:///path/to/dbs?commitname=<user_name>&commitemail=<email>&database=<dbname>&multistatements=true
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `commitname` | ✅ | commit 作者名 |
| `commitemail` | ✅ | commit 作者邮箱 |
| `database` | ❌ | 初始数据库名（对应 `/path/to/dbs/<dbname>/` 子目录） |
| `multistatements` | ❌ | `true` 时支持多条 SQL 以 `;` 分隔 |

## 关键 API 要点

**必须使用 `sql.OpenDB(connector)`，禁止使用 `sql.Open("dolt", dsn)`**：

```go
// ❌ 旧 API，已废弃，会返回错误
db, err := sql.Open("dolt", dsn)

// ✅ 正确做法
cfg, _ := embedded.ParseDSN(dsn)
connector, _ := embedded.NewConnector(cfg)
db := sql.OpenDB(connector)
defer connector.Close()
```

**BackOff 配置**（应对并发锁冲突）：

```go
import "github.com/cenkalti/backoff/v4"

cfg.BackOff = backoff.NewExponentialBackOff()
// 或自定义：
bo := backoff.NewExponentialBackOff()
bo.MaxElapsedTime = 30 * time.Second
cfg.BackOff = bo
```

**多语句查询需显式开启**：

```go
// DSN 中加入 multistatements=true
dsn := "file:///data/dbs?commitname=Alice&commitemail=a@x.com&multistatements=true"
```

## 运行方式

```bash
# 确保 /path/to/dbs 目录存在
mkdir -p /tmp/mydbs
go run example/main.go "file:///tmp/mydbs?commitname=Alice&commitemail=alice@example.com&database=testdb&multistatements=true"
```
