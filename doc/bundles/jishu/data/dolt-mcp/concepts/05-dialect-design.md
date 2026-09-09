---
type: Concept
title: "dolt-mcp 方言设计（三引擎适配）"
description: "dolt-mcp 如何用 Dialect 接口封装 Dolt(MySQL)/DoltgreSQL(Postgres)/DoltLite(SQLite fork) 三引擎差异——过程调用展开、SQL 生成、只读判定解析器、SupportsTool 工具裁剪与 TLS/DSN 差异对照"
tags: [dolt-mcp, dialect, mysql, postgresql, doltlite, golang, sql]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-mcp-source
    resource: /references/source.md
    title: dolt-mcp 源码事实登记
---

# dolt-mcp 方言设计（三引擎适配）

> 本文解析 dolt-mcp 的多方言架构。对应 [F-040~F-043、F-060~F-074](/references/source.md)。

## 设计问题

dolt-mcp 要服务三种数据库引擎，而它们差异巨大：

- Dolt 走 MySQL 线协议，用 **CALL 存储过程**跑版本控制命令，语句用 Vitess 解析；
- DoltgreSQL 走 PostgreSQL 线协议，把 Dolt 存储过程降级为 **SELECT 函数调用**，语句用 pg_query 解析；
- DoltLite 内嵌 SQLite fork，连"服务器"都没有，过程调用是 **SELECT dolt_*()**，语句靠自研 scanner 解析。

如果 server 逻辑为每种引擎写 if-else，会膨胀且易错。dolt-mcp 的解法是用 `Dialect` 接口把所有差异点收纳为 16 个方法（F-042），server 与工具层只面向接口编程。

## Dialect 接口的核心方法组

### 1. 连接层

| 方法 | 作用 | 三引擎差异 |
|------|------|-----------|
| `DriverName()` | database/sql 驱动名 | mysql / pgx / doltlite（F-060/064/069） |
| `FormatDSN(c)` | 组装连接串 | `user:pass@tcp(host:port)/db` vs `postgres://...` vs 直接文件路径（F-060/064/069） |
| `ConfigureTLS(c)` | 配置连接 TLS | MySQL 读 CA 注册 "custom"；Postgres 走 sslmode DSN 参数；DoltLite 无 TLS（F-063/066） |
| `QuoteIdentifier(name)` | 标识符引用 | MySQL 反引号；PG/DoltLite 双引号（F-060/064/069） |

### 2. SQL 生成层

| 方法 | 三引擎差异 |
|------|-----------|
| `CallProcedure(proc, args...)` | MySQL：`CALL DOLT_MERGE('b');`；PG/DoltLite：`SELECT dolt_merge('b');`（函数名小写）（F-060/067/070） |
| `ShowTablesQuery()` | MySQL/PG：`SHOW TABLES;`；DoltLite：查 sqlite_schema（F-061/071） |
| `ShowCreateTableQuery(table)` / `DescribeTableQuery(table)` | MySQL/PG 各 `SHOW CREATE TABLE`/`DESCRIBE`；DoltLite 用 sqlite_schema 与 pragma_table_info（F-061/071） |
| `HashOfFunction(ref)` | `HASHOF('ref')`（MySQL/PG）vs `dolt_hashof('ref')`（DoltLite）（F-061/071） |
| `ListTableDiffChangesQuery(table, from, to)` | 表 WHERE from/to_commit（MySQL/PG）vs `SELECT * FROM "dolt_diff_t"(from, to)` 表函数（DoltLite）（F-061/071） |
| `UseDatabase(db)` | 返回 `USE db;`；DoltLite 单库返回空串跳过（F-051） |

### 3. SQL 校验层（安全关键，见 [SQL 安全机制](04-sql-safety.md)）

| 方法 | MySQL | Postgres | DoltLite |
|------|-------|----------|----------|
| 解析器 | Vitess sqlparser | pg_query_go | 自研 scanner |
| `ValidateReadQuery` | AST 只读类型 | Stmt 类型 | 关键字+单语句+禁 dolt_ 变更函数 |
| `ValidateWriteQuery` | 非只读 | 非只读 | 只读关键字内放行 dolt_ 变更函数 |
| `ValidateCreate/AlterTableQuery` | AST DDL/AlterTable | AST CreateStmt/AlterTableStmt | 关键字 CREATE/ALTER TABLE |

（F-062/F-068/F-072/F-073）

### 4. 能力裁剪：SupportsTool

每个方言构造时声明不支持的工具黑名单（F-014 注册时过滤）：

| 方言 | 禁用的工具 | 数量 |
|------|-----------|------|
| Dolt(MySQL) | 无 | 45 全量 |
| DoltgreSQL | add/remove/run_dolt_test、kill_process、show_processlist | 40 |
| DoltLite | list/create/drop/clone_database、show_processlist、kill_process | 39 |

（F-065、F-069、F-095）

裁剪逻辑背后是引擎能力差异：DoltLite 单库单文件，故无库管理工具（F-069）；Postgres 版暂无 dolt_tests 三工具，且 `show_processlist`/`kill_process` 是 MySQL 概念（F-065）。工具在客户端 `tools/list` 中自然消失，AI 不会尝试不存在的操作。

## 方言特判：同一命令不同语义

DoltLite 的过程调用在通用展开之外还有多个特殊分支（F-070），反映 SQLite 系引擎需要运行时语义修正：

```go
// checkout 单参：目标分支已是 active 分支则不重复 checkout（避免报错）
if proc == DoltCheckout && len(args) == 1 {
    return fmt.Sprintf(
        "SELECT CASE WHEN active_branch() = %s THEN 0 ELSE dolt_checkout(%s) END;",
        quotedArgs[0], quotedArgs[0])
}
// reset "."：dolt_reset 无参调用等价清暂存
if proc == DoltReset && len(args) == 1 && args[0] == "." {
    return "SELECT dolt_reset();"
}
// branch -f：active 分支守卫
if proc == DoltBranch && len(args) == 2 && args[0] == "-f" { ... }
// push --force：DoltLite 把 --force 重排到参数末位
if proc == DoltPush && len(args) == 3 && args[0] == "--force" {
    return fmt.Sprintf("SELECT dolt_push(%s, %s, %s);", quotedArgs[1], quotedArgs[2], quotedArgs[0])
}
```

这说明"三引擎适配"不是简单字符串拼接，而是每个引擎有独立的语义修补层。

## DSN/TLS 对照速查

| 项 | Dolt(MySQL) | DoltgreSQL(PG) | DoltLite |
|----|-------------|----------------|----------|
| 驱动 | go-sql-driver/mysql | jackc/pgx | mattn/go-sqlite3 |
| 端口默认 | 3306 | 5432 | 无 |
| TLS 表达 | `tls=` DSN 参数 + 自定义 CA 注册 | `sslmode`/`sslrootcert` | 无 |
| 多语句 | `multiStatements=true` | `default_query_exec_mode=simple_protocol` | 自研单语句判定 |
| 数据库选择 | USE | USE（保留） | 无（单库） |

（F-060~F-069）

## 选型含义

- **加新方言的成本被隔离**：新引擎只需实现 `Dialect` 接口，工具层零改动；如果新引擎缺某能力，在黑名单加一行即裁剪该工具。
- **AI 侧无需感知方言**：同 45 工具统一暴露，方言只影响后端与个别工具可见性。
- **版本控制语义一致性是关键难点**：checkout/reset/push 在各引擎的边界条件不同，DoltLite 特判是这类问题的缩影。

## 相关概念

* [架构分层](/concepts/01-architecture.md)
* [SQL 安全机制](/concepts/04-sql-safety.md)
* [DoltLite 内嵌模式](/concepts/06-doltlite-mode.md)
