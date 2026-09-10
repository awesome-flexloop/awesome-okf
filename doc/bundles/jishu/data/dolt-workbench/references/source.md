---
type: reference
title: dolt-workbench 源码事实登记
description: DoltWorkbench 项目的源代码结构、API、类型定义与行为事实的完整登记
resource: https://github.com/dolthub/dolt-workbench
tags: [dolt-workbench, fact, source]
status: stable
stale_after: 2027-03-09
generated:
  by: reference_agent/agnes-2.5-flash
  at: 2026-09-09T04:00:00Z
sources:
  - id: dolt-workbench-repo
    resource: https://github.com/dolthub/dolt-workbench
    title: Dolt Workbench GitHub 仓库
    author: team:dolthub
    last_modified: 2026-08-24
  - id: dolt-workbench-v0375
    resource: https://github.com/dolthub/dolt-workbench/tree/8fb67574a12509f009aa046f4a71e615078e7e4c
    title: v0.3.75 release tag (commit 8fb6757)
    author: team:dolthub
    last_modified: 2026-08-24
---

# dolt-workbench 源码事实登记

## F-001: 项目概述

DoltWorkbench 是 DoltHub 官方推出的现代浏览器 SQL 工作台，基于 Electron + NestJS GraphQL Server + Next.js (React) 构建。连接层支持 MySQL、PostgreSQL、SQLite 三种数据库方言（`DatabaseType` 枚举），每种方言经自动探测再派生出 Dolt、Doltgres、DoltLite 三个 Dolt 版本化变体，共形成六个 QueryFactory（详见 F-009~F-011）[^dolt-workbench-repo]。

**来源**: `README.md`

## F-002: 技术栈

| 层次 | 技术 | 版本 |
|---|---|---|
| Electron 主进程 | Nextron (Electron + Next.js) | — |
| GraphQL Server | NestJS + @apollo/server | — |
| Frontend | Next.js 15 + React 19 | — |
| SQL 编辑器 | ace-builds (Ace Editor) | ^1.37.5 |
| 数据网格 | react-data-grid | 7.0.0-beta.44 |
| ER 图 | reactflow | ^11.11.4 |
| GraphQL 客户端 | @apollo/client | ^3.9.9 |
| 本地存储 | localforage | ^1.10.0 |
| Electron 配置 | electron-store | ^8.2.0 |
| AI Agent | @anthropic-ai/claude-agent-sdk | — |

**来源**: `graphql-server/package.json`, `web/package.json`

## F-003: 应用入口与子模块

- **graphql-server/**: NestJS GraphQL API 服务，监听 `:9002`
- **web/**: Electron + Next.js 前端应用，监听 `:3002`
- **eventsapi_schema/**: git submodule（https://github.com/dolthub/eventsapi_schema.git）
- **desktop app**: 通过 `yarn download:dolt` 下载 Dolt CLI，`yarn dev:app` 启动

**来源**: `.gitmodules`, `README.md`

## F-004: Docker 部署

```bash
docker run -p 9002:9002 -p 3000:3000 dolthub/dolt-workbench:latest
```

运行后通过 `http://localhost:3000` 访问。

**来源**: `README.md`

## F-005: 环境变量配置

| 变量 | 说明 |
|---|---|
| `DW_DB_HOST` | 数据库主机地址 |
| `DW_DB_CONNECTION_URI` | 连接 URI（优先于单独字段） |
| `DW_DB_PORT` | 端口 |
| `DW_DB_USER` | 用户名 |
| `DW_DB_PASS` | 密码 |
| `DW_DB_DBNAME` | 数据库名 |
| `DW_DB_USE_SSL` | 是否启用 SSL |

**来源**: `graphql-server/src/dataStore/dataStore.service.ts`

## F-006: GraphQL 模块注册

`AppModule` 使用 `@Module` 装饰器注册以下模块：
- `GraphQLModule.forRoot<ApolloDriverConfig>`（动态 schema 路径：Electron 模式使用 `SCHEMA_PATH` 环境变量，否则使用 `schema.gql`）
- `FileStoreModule`
- `TerminusModule`
- `ConfigModule.forRoot({ isGlobal: true })`
- `DataStoreModule`

providers 包含 `ConnectionProvider` 和 22 个 Resolver 类。

**来源**: `graphql-server/src/app.module.ts`

## F-007: 22 个 Resolver 类

`resolvers.ts` 导出包含以下 Resolver 的数组：
BranchResolver, CommitResolver, DatabaseResolver, DiffStatResolver, DiffSummaryResolver, DocsResolver, FileUploadResolver, PullConflictsResolver, PullResolver, RemoteResolver, RowDiffResolver, RowMutationResolver, RowResolver, SchemaDiffResolver, SchemaResolver, DoltDiffResolver, SelectTableRowsResolver, SqlSelectResolver, StatusResolver, TableResolver, TagResolver, TestResolver

**来源**: `graphql-server/src/resolvers.ts`

## F-008: DataStore 连接持久化

`DataStoreService` 使用 TypeORM DataSource 管理连接配置。支持 `getStoredConnections()`、`addStoredConnection()`、`removeStoredConnection()` 方法。优先使用 TypeORM 服务端持久化，降级到 `FileStoreService`（本地 JSON 存储）。

**来源**: `graphql-server/src/dataStore/dataStore.service.ts`

## F-009: ConnectionProvider 单例模式

`ConnectionProvider` 使用单例模式管理全局 `DataSource` 和 `QueryFactory`。`getDataSource(config)` 函数根据数据库类型返回不同的 TypeORM DataSource：
- SQLite → 使用 `better-sqlite3` 类型 + 自定义 `doltliteDriver`
- 其他类型 → 使用 TypeORM 标准 DataSource

**来源**: `graphql-server/src/connections/connection.provider.ts`

## F-010: 数据库类型自动检测

`newQueryFactory(type, ds)` 函数根据数据库类型自动检测并选择对应的 QueryFactory：
- Postgres → 先尝试 `SELECT dolt_version()` 检测 Doltgres，失败则用 `PostgresQueryFactory`
- SQLite → 先尝试 `SELECT doltlite_engine()` 检测 DoltLite，失败则用 `SqliteQueryFactory`
- MySQL → 先尝试 `SELECT dolt_version()` 检测 Dolt，失败则用 `MySQLQueryFactory`

**来源**: `graphql-server/src/connections/connection.provider.ts`

## F-011: QueryFactory 继承体系

```
BaseQueryFactory (abstract)
  └── MySQLQueryFactory (isDolt=false)
        ├── PostgresQueryFactory (isDolt=false)
        │     └── DoltgresQueryFactory (isDolt=true)
        ├── SqliteQueryFactory (isDolt=false)
        │     └── DoltLiteQueryFactory (isDolt=true)
        └── DoltQueryFactory (isDolt=true)
```

每个 QueryFactory 实现 50+ 个方法，覆盖数据库管理、查询执行、Dolt 专属操作等。

**来源**: `graphql-server/src/queryFactory/index.ts`, `graphql-server/src/queryFactory/base.ts`

## F-012: QueryFactory 核心方法分组

1. **UTILS**: `getDS/getQR/handleAsyncQuery/query/queryMultiple/queryForBuilder/queryQR`
2. **QUERIES**: `databases/currentDatabase/schemas/createDatabase/createSchema/getTableNames/getTables/getTableInfo/getTablePKColumns/getTableRows/getSqlSelect/selectTableRows/deleteRow/insertRow/previewInsertRow/updateRow/dropColumn/dropTable/createView/callProcedure/doltCommitDiff/doltCellDiff/doltCellHistory/schemaDefinition/saveDoc/deleteDoc/getSchemas/getProcedures`
3. **DOLT-SPECIFIC**: `getTableRowsWithDiff/getWorkingDiffRows/getBranch/getBranches/getRemoteBranches/getAllBranches/createNewBranch/callDeleteBranch/callDoltClone/getLogs/getTwoDotLogs/getDiffStat/getThreeDotDiffStat/getDiffSummary/getThreeDotDiffSummary/getSchemaPatch/getThreeDotSchemaPatch/getSchemaDiff/getThreeDotSchemaDiff/getDocs/getStatus/getTag/getTags/createNewTag/callDeleteTag/callMerge/callMergeWithResolveConflicts/resolveRefs/getOneSidedRowDiff/getRowDiffs/getPullConflictsSummary/getPullRowConflicts/restoreAllTables/getRemotes/addRemote/callDeleteRemote/callPullRemote/callPushRemote/callFetchRemote/callCreateBranchFromRemote/getMergeBase/getTests/runTests/saveTests`

**来源**: `graphql-server/src/queryFactory/index.ts`

## F-013: DoltLite 自定义 TypeORM Driver

`doltliteDriver.ts` 提供 TypeORM better-sqlite3 driver 的适配器：
- `DoltLiteStatement` 类：包装 `StatementSync`，提供 `all/get/run` 方法，`reader` 属性检测是否返回结果集
- `DoltLiteConnection` 类：包装 `DatabaseSync`，提供 `prepare/prisma/exec/close` 方法
- 支持 `readOnly` 和 `fileMustExist` 选项

**来源**: `graphql-server/src/connections/doltliteDriver.ts`

## F-014: DoltLite Revision 缓存机制

`DoltLiteQueryFactory` 实现 `RevisionSource` 类型：`{ revision, ds, activeRunners, retired, destroyPromise? }`。

核心方法：
- `withDetachedFallback()`: refName 找不到时解析为 commit hash，创建 `file@revision` DataSource
- `acquireRevisionSource()`: 每个 revision 对应一个 DataSource，activeRunners 引用计数
- `callMerge()` 无显式事务（autocommit 模式），冲突时抛错
- `callMergeWithResolveConflicts()` 有 BEGIN/ROLLBACK 事务模式
- `callPushRemote()` 之后额外调用 `callFetchRemote()`（DoltLite 推送后不自动更新 tracking ref）
- `resolveThreeDotRefs()` 手动计算 merge-base 模拟 three-dot diff（DoltLite 不支持原生 `to...from` 语法）

**来源**: `graphql-server/src/queryFactory/doltlite/index.ts`

## F-015: DoltQueryFactory 继承关系

`DoltQueryFactory extends MySQLQueryFactory implements QueryFactory`，`isDolt = true`。使用 `doltEntityManager` 和自定义 `queries.ts`。

**来源**: `graphql-server/src/queryFactory/dolt/index.ts`

## F-016: FileUploadResolver 文件上传

- MySQL 路径：mysql2 Connection + `LOAD DATA LOCAL INFILE` + `local_infile=ON`
- Postgres/Doltgres 路径：pg-copy-streams + `COPY ... FROM STDIN`
- SQLite 不支持文件上传，抛出 Error
- `FileType` enum: `Csv`, `Psv`, `Tsv`
- `LoadDataModifier` enum: `Ignore`, `Replace`
- 最大文件大小：400MB（graphqlUploadExpress 配置）

**来源**: `graphql-server/src/tables/upload.resolver.ts`

## F-017: 系统表枚举

```typescript
export enum DoltSystemTable {
  DOCS = "dolt_docs",
  QUERY_CATALOG = "dolt_query_catalog",
  SCHEMAS = "dolt_schemas",
  PROCEDURES = "dolt_procedures",
  TESTS = "dolt_tests",
}
```

**来源**: `graphql-server/src/systemTables/systemTable.enums.ts`

## F-018: Row NULL 值表示

`row.model.ts` 中：
- `NULL_VALUE = "\uf5f2\ueb94NULL\uf5a8\ue6ff"`（不可打印哨兵字符串）
- `getCellValue()`: null→NULL_VALUE, '""'→"", Array+colName==="dolt_commit"→首元素, Date→UTC字符串, Buffer→utf8, 对象→JSON.stringify

**来源**: `graphql-server/src/rows/row.model.ts`

## F-019: SqlSelect GraphQL 类型

`SqlSelect` ObjectType 包含：
- `_id`, `databaseName`, `refName`, `queryString`, `columns`, `rows`, `queryExecutionStatus`, `queryExecutionMessage`, `isMutation`, `warnings?`

`QueryExecutionStatus` enum: `Success`, `Error`, `Timeout`

**来源**: `graphql-server/src/sqlSelects/sqlSelect.model.ts`

## F-020: Branch GraphQL 类型

`Branch` ObjectType:
- `_id`, `databaseName`, `branchName`, `lastCommitter`, `lastUpdated`, `table`, `tableNames`, `head`, `remote`, `remoteBranch`

`SortBranchesBy` enum: `Unspecified`, `LastUpdated`

`getDefaultBranchFromBranchesList`: 排序逻辑，"master"/"main" 优先级，双分支偏好"main"

**来源**: `graphql-server/src/branches/branch.model.ts`, `graphql-server/src/branches/branch.resolver.ts`

## F-021: Commit GraphQL 类型

`Commit` ObjectType:
- `_id`, `commitId`, `databaseName`, `message`, `committedAt`, `committer`, `parents`

`DoltWriter` ObjectType:
- `_id`, `displayName`, `emailAddress`, `username`

`ListCommitsArgs` 支持 two-dot 模式（`twoDot` + `excludingCommitsFromRefName`）。参数校验：refName 与 afterCommitId 互斥，twoDot 需配合 excludingCommitsFromRefName。

**来源**: `graphql-server/src/commits/commit.model.ts`, `graphql-server/src/commits/commit.resolver.ts`

## F-022: Table GraphQL 类型

`Table` ObjectType 继承自 `TableDetails`:
- `tableName`, `columns`, `foreignKeys`, `indexes`

GraphQL operations: `table()`, `tableNames()`, `tables()`, `maybeTable()`

`filterSystemTables` 参数控制是否过滤 dolt_* 系统表

**来源**: `graphql-server/src/tables/table.model.ts`, `graphql-server/src/tables/table.resolver.ts`

## F-023: Pull GraphQL 类型

`PullWithDetails` ObjectType: `state`, `summary`, `details`

`PullState` enum: `Open`, `Merged`, `Unspecified`

mergePull mutation: `callMerge()`，可选 author

mergeAndResolveConflicts mutation: `callMergeWithResolveConflicts()`，支持 ours/theirс tables 选择

**来源**: `graphql-server/src/pulls/pull.model.ts`, `graphql-server/src/pulls/pull.resolver.ts`

## F-024: Test GraphQL 类型

`Test` ObjectType: `testName`, `testGroup`, `testQuery`, `assertionType`, `assertionComparator`, `assertionValue`

`TestResult` ObjectType: `testName`, `query`, `status`, `message`

GraphQL operations: `tests()`, `runTests()`, `saveTests()`

**来源**: `graphql-server/src/tests/test.model.ts`, `graphql-server/src/tests/test.resolver.ts`

## F-025: Electron 主进程架构

`background.ts` 约 530 行，环境变量：
- `NEXT_PUBLIC_FOR_ELECTRON=true`
- `NEXT_PUBLIC_FOR_MAC_NAV`
- `NEXT_PUBLIC_USER_DATA_PATH`

`createGraphqlSeverProcess()` 使用 `utilityProcess.fork()` 启动 graphql-server。`waitForGraphQLServer(url, timeout)` 轮询健康检查，超时 30s。

18 个 IPC handlers：`start-dolt-server`, `remove-dolt-connection`, `dolt-login`, `cancel-dolt-login`, `clone-dolthub-db`, `select-sqlite-database-file`, `select-sqlite-database-directory`, `get-doltlite-database-destination`, `create-doltlite-database-file`, `discard-created-doltlite-database-file`, `retain-created-doltlite-database-file`, `set-commit-author`, `get-commit-author`, `toggle-left-sidebar`, `api-config`, `get-headers`, `update-menu`

窗口最小尺寸：1200x780

**来源**: `web/main/background.ts`

## F-026: Dolt sql-server 进程管理

`doltServer.ts` 提供：
- `startServer(mainWindow, connectionName, port, init?, dbName?)`: 初始化 Dolt 仓库并启动 sql-server
- `initializeDoltRepository(doltPath, dbFolderPath, mainWindow)`: 执行 `dolt init --name local_user --email user@local.com`
- `startServerProcess(doltPath, dbFolderPath, port, mainWindow)`: spawn dolt sql-server 进程
- macOS 特殊处理：额外传入 `--socket socketPath`
- 进程输出过滤：`level=error` 和 `Port X already in use` 视为 fatal；`level=warning` 视为非致命；`Server ready` 触发 resolve

**来源**: `web/main/doltServer.ts`

## F-027: Claude AI Agent 实现

`anthropicAgent.ts` 约 600 行，完整实现 Claude AI Agent 模式：
- 使用 `@anthropic-ai/claude-agent-sdk` 的 `query()` 和 `createSdkMcpServer()` API
- `getSystemPrompt(database, dbType, isDolt, databaseFile)` 动态生成系统提示词
- `createWorkbenchMcpServer()` 注册 3 个自定义工具：`switch_branch`, `refresh_page`, `display_image`
- `TOOLS_REQUIRING_CONFIRMATION` 列表：`create_dolt_commit`, `delete_dolt_branch`, `move_dolt_branch`, `dolt_reset_hard`
- `canUseTool(toolName, input, options)`: 对敏感工具请求用户确认（IPC 事件 `agent:tool-confirmation-request/response`）
- IPC 事件发送：`agent:session-id`, `agent:content-block`, `agent:tool-result`, `agent:error`, `agent:message-complete`, `agent:interrupted`, `agent:switch-branch`, `agent:refresh-page`

**来源**: `web/main/agent/anthropicAgent.ts`

## F-028: MCP Server 参数生成

`mcpServerArgs.ts` 提供 `getMcpServerArgs(mcpConfig, commitAuthor?)`：
- SQLite/DoltLite 路径：`["--stdio", "--doltlite", "--db-file", ...]`
- MySQL/Dolt 路径：`["--stdio", "--host", ..., "--database", ..., "--password", ...]`
- Postgres/Doltgres 路径：额外追加 `--doltgres`
- useSSL 时追加 `--tls skip-verify`

**来源**: `web/main/agent/mcpServerArgs.ts`

## F-029: IPC Agent Handler 接口

15 个 IPC handler ID：`agent:get-api-key`, `agent:store-api-key`, `agent:clear-api-key`, `agent:connect`, `agent:send-message`, `agent:disconnect`, `agent:clear-history`, `agent:cancel-tool`, `agent:set-model`, `agent:abort`, `agent:list-sessions`, `agent:load-session-messages`, `agent:register-session`, `agent:unregister-session`, `agent:switch-session`

`ClaudeAgent` 单例管理模式。

**来源**: `web/main/agent/ipcHandlers.ts`

## F-030: 菜单系统

`menu.ts` 提供 `initMenu(win, isProd, hasChosenDatabase?)`：
- 5 个顶层菜单：Application, Edit, View, Tools, Window, Help
- Tools 菜单（需要已选择数据库）：Import File, Commit Graph, Schema Diagram, New submenu, Run Query
- 快捷键：CmdOrCtrl+I (Import), CmdOrCtrl+G (Graph), CmdOrCtrl+D (Schema), CmdOrCtrl+Q (Query)

**来源**: `web/main/helpers/menu.ts`

## F-031: UI 页面路由

30+ 个 page 文件，主要路由：
- `/connections` — 连接管理（新连接、列表）
- `/database/[databaseName]` — 数据库首页
- `/database/[databaseName]/data/[refName]/[tableName]` — 数据浏览
- `/database/[databaseName]/data/create` — 建表
- `/database/[databaseName]/query/[refName]` — SQL 查询
- `/database/[databaseName]/branches` — 分支管理
- `/database/[databaseName]/commits/[refName]` — 提交历史
- `/database/[databaseName]/commits/[refName]/graph` — 提交图
- `/database/[databaseName]/compare/[refName]` — Diff 对比
- `/database/[databaseName]/pulls` — Pull 请求
- `/database/[databaseName]/schema/[refName]` — Schema 视图
- `/database/[databaseName]/doc/[refName]` — 文档管理
- `/database/[databaseName]/tests/[refName]` — 测试管理
- `/database/[databaseName]/remotes` — Remote 管理
- `/database/[databaseName]/releases` — Releases 管理
- `/database/[databaseName]/upload` — 文件上传

**来源**: `web/renderer/pages/` 目录结构

## F-032: SqlEditor 组件

- Props: `{ params: OptionalRefParams; ["data-cy"]?: string }`
- AceEditor 配置：fontSize=15, maxLines=20, minLines=6
- 初始光标位置：第 1 行第 9 列
- 100ms debounce 防抖
- 使用 `useSqlEditorContext("Tables")` 获取上下文

**来源**: `web/renderer/components/SqlEditor/index.tsx`

## F-033: DataTable 上下文

`DataTableContextType`: `rows`, `workingDiffRows`, `hasMore`, `columns`, `foreignKeys`, `error` 等

支持四种查询：`useDataTableQuery`, `useSelectTableRowsForDataTableQuery`, `useRowsForDataTableQuery`, `useWorkingDiffRowsForDataTableQuery`

**来源**: `web/renderer/contexts/dataTable/index.tsx`

## F-034: Apollo GraphQL 客户端配置

默认 GraphQL URL: `http://localhost:9002/graphql`

Apollo Client 配置：
- `uploadLink` 支持文件上传
- `errorLink` 处理错误
- `authLink` 处理认证
- `cache` 使用 InMemoryCache

**来源**: `web/renderer/lib/apollo.tsx`

## F-035: Agent 配置类型

`McpServerConfig`: `host`, `port`, `user`, `database`, `databaseFile`, `password`, `useSSL`, `type`, `isDolt`

`AgentConfig`: `apiKey`, `mcpConfig`, `model`

`ContentBlock` union: `TextContentBlock` | `ToolUseContentBlock` | `ImageContentBlock`

`AgentMessage`: `id`, `role`, `contentBlocks`, `timestamp`

**来源**: `web/main/agent/types.ts`

## F-036: 数据库类型枚举

```typescript
export enum DatabaseType {
  Mysql = "mysql",
  Postgres = "postgres",
  Sqlite = "sqlite",
}
```

**来源**: `graphql-server/src/databases/database.enum.ts`

## F-037: 应用整体架构

```
┌─────────────────────────────────────────────┐
│  Electron Main Process (background.ts)       │
│  ├─ GraphQL Server 进程管理                   │
│  ├─ Dolt sql-server 进程管理                   │
│  ├─ IPC Handlers (18 个)                    │
│  └─ Claude Agent 模式                        │
├─────────────────────────────────────────────┤
│  NestJS GraphQL Server (:9002)               │
│  ├─ ConnectionProvider (单例)                │
│  ├─ QueryFactory 工厂模式                     │
│  │   └─ 6 种数据库类型                       │
│  ├─ 22 个 Resolver                           │
│  └─ TypeORM DataStore (连接持久化)            │
├─────────────────────────────────────────────┤
│  Next.js Renderer (:3002)                    │
│  ├─ 30+ 个页面路由                          │
│  ├─ Apollo GraphQL Client                   │
│  ├─ SqlEditor (Ace)                         │
│  ├─ DataTable (react-data-grid)              │
│  └─ SWR 数据缓存                            │
└─────────────────────────────────────────────┘
```

**来源**: 综合分析多个源文件

## F-038: QueryFactory types.ts 核心类型

`types.ts` 定义 190+ 行核心类型：
- DBArgs, CloneArgs, SchemaArgs, RefArgs, TableArgs
- Row 类型：RawRow, RawRowWithDiff, RawRows, RawRowsWithDiff
- Result 类型：SqlSelectResult, MutationResult, DiffRes, CommitsRes
- `ColumnValue` = `{ column: string; value?: string | null; type?: string }`
- `OrderByClause` = `{ column: string; direction: "ASC" | "DESC" }`

**来源**: `graphql-server/src/queryFactory/types.ts`

## F-039: Build 目录（查询构建器）

`queryFactory/build/` 目录包含 15 个构建函数：
- `buildSelectTableRows` — 表行查询构建
- `buildInsertRow` — 行插入构建
- `buildUpdateRow` — 行更新构建
- `buildDeleteRow` — 行删除构建
- `buildDropTable` — 表删除构建
- `buildDropColumn` — 列删除构建
- `buildCreateView` — 视图创建构建
- `buildCallProcedure` — 存储过程调用构建
- `buildDoltCommitDiff` — 提交 diff 构建
- `buildDoltCellDiff` — 单元格 diff 构建
- `buildDoltCellHistory` — 单元格历史构建
- `buildSchemaDefinition` — Schema 定义构建
- `buildSaveDoc` — 文档保存构建
- `buildUtils` — 通用工具函数

每个构建函数都有对应的 `.test.ts` 测试文件。

**来源**: `graphql-server/src/queryFactory/build/` 目录

## F-040: DoltLite 测试与冲突预览限制

`DoltLiteQueryFactory` 中：
- `getPullConflictsSummary()` 和 `getPullRowConflicts()` 均抛出 "Merge conflict previews are not supported for DoltLite"
- `saveTests()` 手动填充 generatedMaps（better-sqlite3 不自动填充）

**来源**: `graphql-server/src/queryFactory/doltlite/index.ts`

[^dolt-workbench-repo]: [Dolt Workbench GitHub 仓库](https://github.com/dolthub/dolt-workbench)（固定版本 v0.3.75，commit 8fb6757）
