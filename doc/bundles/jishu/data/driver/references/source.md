---
type: Reference
title: driver 源码事实登记
description: "Dolt Driver v2（dolthub/driver）源码信源登记——仓库元信息、DSN 格式、Config、Connector/Conn/Stmt/Rows/Lifecycle，F-001~F-022 编号事实零推测登记"
tags: [driver, dolt, source-code, golang, facts, dolthub]
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

# driver 源码事实登记

> 本文件是知识包全部正文的事实底账，编号 **F-001 ~ F-022**。所有正文中的数字、类型名、方法名、参数均可在下表找到逐字出处。

## 一、仓库与版本元信息

| 编号 | 事实 | 出处 |
|---|---|---|
| F-001 | 模块路径 `github.com/dolthub/driver/v2`，package `embedded`，Go 1.26.5 | go.mod L1-L3 |
| F-002 | 驱动注册名常量 `DoltDriverName = "dolt"`，`init()` 调用 `sql.Register(DoltDriverName, &doltDriver{})` | driver.go L1-L8 |
| F-003 | DSN 必须使用 `file://`  scheme 前缀：`file:///path/to/dbs?commitname=X&commitemail=Y` | README.md + data_source.go |
| F-004 | 必需参数：`commitname`（作者名）、`commitemail`（作者邮箱），各只允许一个值 | config.go ParseDSN 逻辑 |
| F-005 | 可选参数：`database`（初始 USE）、`multistatements`（true 开启多语句）、`clientfoundrows`（true 报告 found rows） | config.go |
| F-006 | `ParseDataSource()` 验证 `file://` 前缀并拆分 Directory + Params；`ParamIsTrue()` 不区分大小写检查布尔参数 | data_source.go |
| F-007 | `Config` 字段：DSN、Directory、CommitName、CommitEmail、Database、MultiStatements、ClientFoundRows、Params、BackOff、Version；默认 Version="0.40.17" | config.go |
| F-008 | 旧 API `Open(dsn)` 返回错误 "the Open function is not supported"；新 API `OpenConnector(dsn)` → `ParseDSN` → `NewConnector` | driver.go L20-L35 |
| F-009 | `Connector` 字段：`cfg Config`、`driver *doltDriver`、`se *engine.SqlEngine`、`openCh chan struct{}`；进程级 semaphore `openSem` 序列化 open 调用 | connector.go |
| F-010 | `openEngineWithRetry` 使用 BackOff + `dbfactory.DisableSingletonCacheParam` + `dbfactory.FailOnJournalLockTimeoutParam`；`isRetryableOpenErr()` 检测 `nbs.ErrDatabaseLocked` 和 `os.ErrDeadlineExceeded` | connector.go + retryable_open_err.go |
| F-011 | 嵌入式驱动每 24h 发送匿名指标上报（gRPC，`eventsapi.AppID_APP_DOLT_EMBEDDED`），可通过配置禁用 | connector.go metrics 逻辑 |
| F-012 | `LoadMultiEnvFromDir` 遍历 Directory 下的子目录，每个子目录作为独立 Dolt repository，支持单 DSN 多库模式 | driver.go LoadMultiEnvFromDir |

## 二、Conn 与查询执行

| 编号 | 事实 | 出处 |
|---|---|---|
| F-013 | `DoltConn` 字段：`se *engine.SqlEngine`、`gmsCtx *gms.Context`、`cfg *Config`、`activeQueryCtx *gms.Context`；`globalQueryPid atomic.Uint64` 单调递增 PID | conn.go |
| F-014 | `beginQuery()` 强制串行执行：杀掉已有活跃 query 后再开新 query；`queryWithBindings` 是所有操作的统一入口 | conn.go beginQuery/queryWithBindings |
| F-015 | `BeginTx` 支持 `LevelSerializable` 和 `LevelDefault`；无效隔离级别返回错误 | conn.go BeginTx |
| F-016 | `IsValid()` 恒返回 `false`（不复用 session）；`ResetSession()` 返回 `driver.ErrBadConn`（强制重新连接） | conn.go IsValid/ResetSession |
| F-017 | `doltStmt`（单语句）和 `doltMultiStmt`（多语句，`stmts []*doltStmt`）；`namedArgsToBindings()` 转换命名/位置参数为 `sqlparser.Expr` | statement.go |
| F-018 | `doltRows` 字段：`sch gms.Schema`、`rowIter gms.RowIter`、`drained bool`；`Next()` 处理 Value/Valuer/GeometryValue/EnumType/SetType | rows.go |
| F-019 | `doltResult` 字段：`affected int64`、`last int64`；`newResult()` 遍历 RowIter 累加 RowsAffected 和 InsertID | result.go |
| F-020 | `translateError()` 用 `sql.CastSQLError(err)` → `mysql.MySQLError{Number, Message}`，确保 MySQL 线协议错误码 | errors.go |

## 三、多语句与事务

| 编号 | 事实 | 出处 |
|---|---|---|
| F-021 | `QuerySplitter` 使用 `RuneStack` 追踪括号/引号/反引号嵌套；只在非嵌套状态下按 `;` 拆分；`openRunes = map[rune]bool{'(':true, '"':true, '\'':true, '`':true}` | query_splitter.go |
| F-022 | 核心依赖：`github.com/dolthub/dolt/go` v0.40.5-0.20260902090248-362a86528a8a、`go-sql-driver/mysql` v1.9.3、`go-mysql-server` v0.20.1、`cenkalti/backoff/v4` | go.mod |
