---
type: Reference
title: dolt-mcp 源码事实登记
description: "Dolt MCP Server（dolthub/dolt-mcp）源码信源登记——仓库元信息、架构分层、CLI/配置、db 方言层、45 工具注册、DoltLite 内嵌、JWT 认证，F-001~F-162 编号事实零推测登记"
tags: [dolt-mcp, mcp, source-code, golang, facts, dolthub]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-mcp-repo
    resource: https://github.com/dolthub/dolt-mcp
    title: dolthub/dolt-mcp（官方仓库）
  - id: dolt-mcp-local
    resource: "本地克隆（commit cde8e48 ≈ v0.3.8-5-gcde8e48，2026-08-18）"
    title: dolt-mcp 源码逐文件精读
---

# dolt-mcp 源码事实登记

> 本文件是知识包全部正文的事实底账，编号 **F-001 ~ F-162**。所有正文中的数字、工具名、参数、SQL 与行为描述均可在下表找到逐字出处；出处列给出源码相对路径。信源版本见 frontmatter `sources`（官方 GitHub + 本地克隆 commit `cde8e48`，即 tag `v0.3.8` 之上 5 个提交）。

## 一、仓库与版本元信息

| 编号 | 事实 | 出处 |
|---|---|---|
| F-001 | 模块路径 `github.com/dolthub/dolt-mcp`，`go 1.25.0` | go.mod L1-L3 |
| F-002 | 服务名常量 `DoltMCPServerName = "dolt-mcp"`；版本变量 `DoltMCPServerVersion = "0.3.8"` | mcp/pkg/server.go L8-L12 |
| F-003 | 依赖 dolthub/dolt/go v0.40.5-0.20250717234857（携带 Dolt 引擎/jwtauth） | go.mod L6 |
| F-004 | 依赖 dolthub/go-mysql-server v0.20.1、dolthub/vitess、go-sql-driver/mysql v1.9.3 | go.mod L7-L9 |
| F-005 | 依赖 jackc/pgx/v5 v5.7.6（Postgres 驱动）、pganalyze/pg_query_go/v6、wasilibs/go-pgquery（Postgres 解析） | go.mod L11、L14、L16 |
| F-006 | 依赖 mark3labs/mcp-go v0.34.0（MCP 协议）、mattn/go-sqlite3 v1.14.49（DoltLite cgo） | go.mod L12-L13 |
| F-007 | 日志库 go.uber.org/zap v1.27.0 | go.mod L17 |
| F-008 | `--version` 输出 "Dolt MCP server" + version | mcp/cmd/dolt-mcp-server/main.go L241-L244 |

## 二、总体架构

| 编号 | 事实 | 出处 |
|---|---|---|
| F-010 | MCP server 基于 `github.com/mark3labs/mcp-go/server`：`server.NewMCPServer(名称, 版本, WithToolCapabilities(true), WithLogging())` | mcp/pkg/stdio_server.go L37-L42 |
| F-011 | `pkg.Server` 接口：`MCP() *server.MCPServer`、`DBConfig() db.Config`、`Dialect() db.Dialect` | mcp/pkg/server.go L14-L18 |
| F-012 | 工具集抽象 `ToolSet`：`RegisterTools(server pkg.Server)`；`WithToolSet` 以 Option 注入 | mcp/pkg/toolsets/toolset.go |
| F-013 | `PrimitiveToolSetV1` 实现 ToolSet，持 `toolRegistrations` 列表 | mcp/pkg/toolsets/primitive_v1.go L8-L65 |
| F-014 | 工具注册共 **45 项**，注册时经 `dialect.SupportsTool(name)` 过滤 | primitive_v1.go L19-L65、L67-L74 |
| F-015 | 45 工具名清单见正文 concepts/03 | primitive_v1.go L19-L65 |

## 三、CLI 与配置

| 编号 | 事实 | 出处 |
|---|---|---|
| F-020 | 新参数 `--host/--port/--user/--password/--database/--tls/--tls-ca/--dolt/--doltgres/--doltlite/--db-file/--commit-name/--commit-email/--doltlite-busy-timeout` | main.go L22-L61 |
| F-021 | 兼容旧参数 `--dolt-*`（新参数优先，用旧名打 deprecation 警告） | main.go L90-L99、L125-L146 |
| F-022 | 模式 `--http`/`--stdio`；HTTP 端口 `--mcp-port` 默认 8080；HTTPS `--http-cert-file/--http-key-file/--http-ca-file` | main.go L103-L109 |
| F-023 | JWT 认证 `--jwk-claims`（key=value 逗号分隔）+ `--jwk-url`（JWKS），二者须同时提供 | main.go L110-L111、http_server.go L52-L56 |
| F-024 | `--log-level`（debug/info/warn/error 默认 info）；stdio+debug 日志写 `~/.dolt-mcp-server/logs/` 避免污染 stdout | main.go L106、L224-L234 |
| F-025 | `--dolt`/`--doltgres`/`--doltlite` 互斥；默认 MySQL(dolt) | resolveDialect main.go L148-L165 |
| F-026 | 未显式端口时：Doltgres 5432、其余 3306 | main.go L267-L274 |
| F-027 | validateArgs：DoltLite 须 `--db-file`；非 DoltLite 须 host/port/user；HTTP 须 `--mcp-port` | main.go L344-L366 |
| F-028 | `DOLT_PASSWORD` 环境变量兜底密码 | main.go L281-L283 |
| F-029 | `db.Config`：Host/User/Password/DatabaseName/Port/ParseTime/MultiStatements/TLS/TLSCAFile/DialectType + DoltLite Path/CommitName/CommitEmail/BusyTimeout | mcp/pkg/db/config.go L19-L38 |
| F-030 | `Config.Validate`：DoltLite 校验 busy timeout（0~2147483647ms）与 Path；非 DoltLite 校验 Host/User/Port；DSN 非空则跳过 | config.go L40-L63 |
| F-031 | `DefaultDoltLiteBusyTimeout = 5s` | config.go L15 |
| F-032 | Docker env：MCP_MODE/MCP_DIALECT/MCP_PORT/DOLT_HOST/DOLT_USER/DOLT_DATABASE/DOLT_PASSWORD/DOLT_PORT/DOLT_DB_FILE/DOLT_COMMIT_NAME/DOLT_COMMIT_EMAIL/DOLTLITE_BUSY_TIMEOUT/DOLTLITE_CREDS_DIR/DOLTLITE_CREDS_KID/DOLTLITE_CA_FILE | docker/README.md L63-L84 |
| F-033 | 镜像变体 `dolthub/dolt-mcp:latest` 与 `<version>-doltlite`；DoltLite 镜像默认 doltlite/db=/data/doltlite.db；非 root `doltmcp:1001` | docker/README.md L35-L61、L172 |
| F-034 | Docker healthcheck：`wget --spider http://localhost:8080/health` | docker/README.md L106-L110 |
| F-035 | entrypoint.sh：无参数按 env 组参；doltlite 分支强制 `--doltlite --db-file` 且 MCP_MODE 须 http/stdio；dolt/doltgres 校验 DOLT_HOST/DOLT_USER | docker/entrypoint.sh |

## 四、db 层与事务模型

| 编号 | 事实 | 出处 |
|---|---|---|
| F-040 | DialectType：mysql/postgres/doltlite | mcp/pkg/db/dialect.go L8-L12 |
| F-041 | DoltProcedure：DOLT_CHECKOUT/COMMIT/BRANCH/ADD/RESET/MERGE/REMOTE/CLONE/FETCH/PUSH/PULL | dialect.go L25-L37 |
| F-042 | `Dialect` 接口：SupportsTool/DriverName/FormatDSN/ConfigureTLS/QuoteIdentifier/CallProcedure/UseDatabase/ShowTablesQuery/ShowCreateTableQuery/DescribeTableQuery/HashOfFunction/ListTableDiffChangesQuery/ValidateReadQuery/ValidateWriteQuery/ValidateCreateTableQuery/ValidateAlterTableQuery | dialect.go L40-L74 |
| F-043 | `NewDialect(dt)`：Postgres→NewPostgresDialect、DoltLite→NewDoltLiteDialect、default→NewMySQLDialect | dialect.go L77-L85 |
| F-044 | ResultFormat：Undefined/Markdown/CSV；DatabaseTransaction 接口 QueryContext/ExecContext/Rollback/Commit | database.go L13-L32 |
| F-045 | `rowMapToMarkdown` 生成 Markdown 表 | database.go L135-L172 |
| F-046 | `rowMapToCSV` 生成 CSV；[]byte 值转 string | database.go L174-L202、L239-L241 |
| F-047 | `NewDatabaseTransaction`：非 DoltLite 走 newDB→`BEGIN;` | database.go L49-L67 |
| F-048 | DoltLite 事务：设 busy_timeout、按配置 `dolt_config('user.name'/'user.email')`、BEGIN；失败 recoverPinnedTransaction 清理 | database.go L69-L118 |
| F-049 | `finish` 关 conn/db/doltLiteDatabase；提交/回滚后复用报 ErrTransactionHasBeenCommittedOrRolledBack | database.go L289-L313 |
| F-050 | 只读工具 `defer tx.Rollback`；写工具 `CommitTransactionOrRollbackOnError`（nil 提交/有错回滚） | db_helpers.go L9-L15 |
| F-051 | `NewDatabaseTransactionUsingDatabase` = 事务 + `USE db` | db_helpers.go L32-L47 |
| F-052 | `NewDatabaseTransactionUsingDatabaseOnBranch` = 上述 + `DOLT_CHECKOUT(branch)` | db_helpers.go L49-L62 |
| F-053 | DoltLite 打开校验 `doltlite_engine()` 须返回 "prolly" | database.go L395-L425 |

## 五、方言差异

| 编号 | 事实 | 出处 |
|---|---|---|
| F-060 | MySQL：driver "mysql"；DSN `user:pass@tcp(host:port)/[db]`；反引号引用；CALL 展开 `CALL DOLT_X('a','b');` | dialect_mysql.go L34-L97 |
| F-061 | MySQL schema SQL：SHOW TABLES/SHOW CREATE TABLE/DESCRIBE/HASHOF/dolt_diff 查询 | dialect_mysql.go L103-L122 |
| F-062 | MySQL 只读判定 SelectStatement/Show/Explain/OtherRead；Vitess sqlparser 校验 | dialect_mysql.go L126-L189 |
| F-063 | MySQL TLS：读 CA 注册 "custom"；支持 true/false/skip-verify/preferred | dialect_mysql.go L65-L85 |
| F-064 | Postgres：driver "pgx"；DSN `postgres://...`；双引号引用 | dialect_postgres.go L35-L68 |
| F-065 | Postgres 禁 5 工具：add_dolt_test/remove_dolt_test/run_dolt_tests/kill_process/show_processlist | dialect_postgres.go L19-L33 |
| F-066 | Postgres sslmode 映射与 simple_protocol 多语句 | dialect_postgres.go L70-L86 |
| F-067 | Postgres CALL 展开 `SELECT dolt_x('a','b');`（小写） | dialect_postgres.go L97-L104 |
| F-068 | Postgres 只读判定 SelectStmt/VariableShowStmt/ExplainStmt；pg_query 解析 | dialect_postgres.go L133-L189 |
| F-069 | DoltLite：driver "doltlite"；DSN=Path；禁 6 工具 list_databases/create/drop/clone_database/show_processlist/kill_process | dialect_doltlite.go L9-L33 |
| F-070 | DoltLite CALL `SELECT dolt_x(...)`；特判 checkout CASE 守卫/reset "."/branch -f/push --force 重排 | dialect_doltlite.go L58-L88 |
| F-071 | DoltLite schema SQL：sqlite_schema/pragma_table_info；diff 表函数 | dialect_doltlite.go L94-L119 |
| F-072 | DoltLite ValidateReadQuery：SELECT/WITH/VALUES/EXPLAIN 且单语句且禁 dolt_ 变更函数 | dialect_doltlite.go L121-L292 |
| F-073 | DoltLite ValidateWriteQuery：只读关键字+dolt_ 变更函数放行 | dialect_doltlite.go L294-L306 |
| F-074 | DoltLite driver：build tag `doltlite` 注册 sqlite3；无 tag 报 ErrDoltLiteNotSupported | driver_doltlite*.go |

## 六、HTTP/stdio/JWT

| 编号 | 事实 | 出处 |
|---|---|---|
| F-080 | HTTP = `NewStreamableHTTPServer`；端点须 `/mcp`；debug 包 access-log | http_server.go L44-L49 |
| F-081 | HTTP 优雅关闭：signal+ctx，10s Shutdown | http_server.go L116-L145 |
| F-082 | HTTPS：tls.LoadX509KeyPair、TLS1.2+、ListenAndServeTLS("","") | main.go L167-L196、http_server.go L148-L152 |
| F-083 | Bearer 认证：Authorization "Bearer" 或 query `jwt`；无 token 401 | jwt_auth.go L16-L56 |
| F-084 | JWT 链：JWTProvider(URL, iss/aud/sub)→NewJWTValidator→ValidateJWT | jwt_auth.go L58-L91 |
| F-085 | stdio：NewStdioServer→Listen(stdin, stdout)；打印 "Serving Dolt MCP on Stdin" | stdio_server.go L44-L91 |

## 七、DoltLite 内嵌模式

| 编号 | 事实 | 出处 |
|---|---|---|
| F-090 | DoltLite 需 cgo + `-tags "doltlite libsqlite3"` + libdoltlite；预编译归档与 `-doltlite` 镜像提供 | README L199-L281 |
| F-091 | DoltLite flags：`--doltlite --db-file` + 可选 commit-name/email/busy-timeout | README L221-L236 |
| F-092 | 每工具调用独立 pin handle 防状态泄漏；并发读/单写者协调 | README L297 |
| F-093 | DoltLite 远程 file/HTTP(S)（自有协议≠Dolt）；凭据 dolt_creds_new/`~/.doltlite/creds` | README L283-L298 |
| F-094 | DoltLite：working_database 忽略；提交作者默认 "doltlite"；dirty working set 分支独立 | README L294-L298 |
| F-095 | DoltLite 保留 39 工具（含 dolt_tests）；Postgres 禁 dolt_tests（F-065 差异） | README L283-L298 |

## 八、工具层总览（A/B/C 组逐文件登记）

> 参数缺失报 `"%s not defined"`（grpc InvalidArgument）。hint 四元组 = (readOnly, destructive, idempotent, openWorld)。

| 编号 | 事实 | 出处（mcp/pkg/tools/） |
|---|---|---|
| F-100 | 四个 With*HintAnnotation 注解语义 | 各工具文件 |
| F-101 | 库级工具无 working 参数：list_databases/create_database/drop_database/clone_database/select_version | - |
| F-102 | list_databases：`SHOW DATABASES;` readOnly(1,0,1,0) | list_databases.go |
| F-103 | create_database：database+if_not_exists；`CREATE DATABASE [IF NOT EXISTS] %s;` (0,0,1,0) | create_database.go |
| F-104 | drop_database：database+if_exists；`DROP DATABASE [IF EXISTS] %s;` (0,1,1,0) | drop_database.go |
| F-105 | clone_database：remote_url+name；DOLT_CLONE(url[,name])；openWorld=1 | clone_database.go |
| F-106 | select_version：`SELECT DOLT_VERSION();` readOnly | select_version.go |
| F-107 | show_tables：working 双参；dialect.ShowTablesQuery；readOnly | show_tables.go |
| F-108 | show_create_table：+table；dialect.ShowCreateTableQuery；<2 行→"table not found" | show_create_table.go |
| F-109 | describe_table：+table；dialect.DescribeTableQuery；同守卫 | describe_table.go |
| F-110 | create_table：+query；ValidateCreateTableQuery；(0,0,0,0) 文案 "successfully created table" | create_table.go |
| F-111 | alter_table：+query；ValidateAlterTableQuery；(0,0,0,0) 文案 "successfully altered table" | alter_table.go |
| F-112 | drop_table：+table+if_exists；`DROP TABLE [IF EXISTS] %s;` (0,1,1,0) | drop_table.go |
| F-113 | query：+query；ValidateReadQuery；Markdown；(1,0,1,0) Rollback | query.go |
| F-114 | exec：+query；ValidateWriteQuery；(0,1,0,0) 文案 "successfully executed write" Commit | exec.go |
| F-115 | show_processlist：+full；`SHOW [FULL] PROCESSLIST;` readOnly | show_processlist.go |
| F-116 | kill_process：+process_id(正整数)+kill_query；`KILL [QUERY] id;` (0,1,0,0) | kill_process.go |
| F-117 | list_dolt_branches：working_database；`SELECT * FROM dolt_branches;` readOnly | list_dolt_branches.go |
| F-118 | select_active_branch：双参；`SELECT ACTIVE_BRANCH();` readOnly | select_active_branch.go |
| F-119 | create_dolt_branch：orig+new+force；`DOLT_BRANCH('-c'[, '-f'], orig, new)` (0,0,0,0) | create_dolt_branch.go |
| F-120 | create_dolt_branch_from_head：new+force；`DOLT_BRANCH([-f,] new)` (0,0,0,0) | create_dolt_branch_from_head.go |
| F-121 | delete_dolt_branch：branch+force；`DOLT_BRANCH('-d'[, '-f'], branch)` (0,1,1,0) | delete_dolt_branch.go |
| F-122 | move_dolt_branch：old+new+force；`DOLT_BRANCH('-m'[, '-f'], old, new)` (0,0,0,0) | move_dolt_branch.go |
| F-123 | stage_table_for_dolt_commit：+table；`DOLT_ADD(table)` (0,0,1,0) | stage_table_for_dolt_commit.go |
| F-124 | stage_all_tables_for_dolt_commit：`DOLT_ADD('-A')` (0,0,1,0) 文案 "successfully staged tables" | stage_all_tables_for_dolt_commit.go |
| F-125 | unstage_table：+table；`DOLT_RESET(table)` (0,0,1,0) | unstage_table.go |
| F-126 | unstage_all_tables：`DOLT_RESET('.')` (0,0,1,0) | unstage_all_tables.go |
| F-127 | create_dolt_commit：+message；`DOLT_COMMIT('-m', msg)` (0,0,1,0) 文案 "successfully committed changes" | create_dolt_commit.go |
| F-128 | dolt_reset_soft：+revision；`DOLT_RESET('--soft', rev)` (0,0,1,0) | dolt_reset_soft.go |
| F-129 | dolt_reset_hard：+revision；`DOLT_RESET('--hard', rev)` (0,1,1,0) | dolt_reset_hard.go |
| F-130 | list_dolt_commits：`SELECT * FROM dolt_log;` readOnly（TODO 分页） | list_dolt_commits.go |
| F-131 | diff working_set：`SELECT * FROM dolt_diff WHERE commit_hash='WORKING';` readOnly | list_dolt_diff_changes_in_working_set.go |
| F-132 | diff by_table：+table+from/to_commit+hash_of_*；互斥校验；HASHOF/字面量 | list_dolt_diff_changes_by_table_name.go |
| F-133 | diff date_range：+start/end；`SELECT * FROM dolt_diff WHERE date BETWEEN '%s' AND '%s';` readOnly | list_dolt_diff_changes_in_date_range.go |
| F-134 | get_dolt_merge_status：`SELECT * FROM dolt_merge_status;` readOnly | get_dolt_merge_status.go |
| F-135 | merge_dolt_branch：+branch+message；`DOLT_MERGE(branch[, '-m', msg])` (0,1,0,0) 文案 "successfully merged branch" | merge_dolt_branch.go |
| F-136 | merge_dolt_branch_no_fast_forward：加 `'--no-ff'` (0,1,0,0) | merge_dolt_branch_no_ff.go |
| F-137 | list_dolt_remotes：working_database；`SELECT * FROM dolt_remotes;` readOnly | list_dolt_remotes.go |
| F-138 | add_dolt_remote：remote_name+remote_url；`DOLT_REMOTE('add', name, url)` (0,0,1,0) | add_dolt_remote.go |
| F-139 | remove_dolt_remote：remote_name；`DOLT_REMOTE('remove', name)` (0,0,1,0) | remove_dolt_remote.go |
| F-140 | dolt_fetch_branch：remote_name+branch；`DOLT_FETCH(remote, branch)` (0,0,1,1) | dolt_fetch_branch.go |
| F-141 | dolt_fetch_all_branches：remote_name；`DOLT_FETCH(remote)` (0,0,1,1) | dolt_fetch_all_branches.go |
| F-142 | dolt_push_branch：remote+branch+force；force→`DOLT_PUSH('--force', remote, branch)` (0,0,0,1) | dolt_push_branch.go |
| F-143 | dolt_pull_branch：remote+branch+force；force→`DOLT_PULL(remote, branch, '--force')` (0,0,0,1) | dolt_pull_branch.go |
| F-144 | run_dolt_tests：+target；`SELECT * FROM dolt_test_run()['<target>']` readOnly | run_dolt_tests.go |
| F-145 | add_dolt_test：test_name+query+assertion_type+comparator(+group/value)；REPLACE INTO dolt_tests（六列）(0,0,1,0) | add_dolt_test_tool.go |
| F-146 | remove_dolt_test：test_name；`DELETE FROM dolt_tests ...` (0,1,1,0) | remove_dolt_test_tool.go |
| F-147 | 源码怪癖：stage_all 描述单数；date_range 描述错绑 create_dolt_branch 文案；pull working_database 描述错绑 branch 文案；by_table_name to/hash 描述复用 from 描述 | 见 F-124/133/143/132 |

## 九、测试基建

| 编号 | 事实 | 出处 |
|---|---|---|
| F-150 | 三方言集成测试；MCP HTTP `http://0.0.0.0:8080/mcp` | suite.go、helper_test.go |
| F-151 | MySQL：spawn dolt server（benchmark_runner）+ mcp-client-1 用户 + DOLT_ROOT_PATH 隔离 | suite.go L276-L461 |
| F-152 | Postgres：spawn doltgres + postgres/password 建库轮询 | suite.go L463-L555 |
| F-153 | DoltLite：临时 db + NewDatabaseTransaction 建链 | suite.go L314-L364 |
| F-154 | seed.sql：people 表（id PK, first_name, last_name）3 行 tim/brian/aaron | testdata/seed.sql |
| F-155 | 客户端 mcp-go：Initialize/ListTools/CallTool；StreamableHTTP+WithContinuousListening | client.go |
| F-156 | Setup/Teardown 建分支隔离；DoltLite 用 dolt_connect_branch 刷新 | suite.go L109-L265 |

## 十、README 能力宣称

| 编号 | 事实 | 出处 |
|---|---|---|
| F-160 | 六大类工具宣称（Database/Table/Data/VC/Diff/Remote 等） | README L7-L14 |
| F-161 | DoltLite 定位：本地优先 AI 工作流、单文件内嵌 | README L199-L234 |
| F-162 | DOLT_PASSWORD 环境变量 | README L329-L331 |
