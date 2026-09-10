---
type: Reference
title: Dolt 主仓源码事实登记
description: "dolthub/dolt 主仓源码事实登记（CLI 命令层 / SQL 版本控制层 / 存储内核层 / AGENT.md 指南），F-086 ~ F-192 编号，信源距离 ①"
tags: [dolt, source-code, golang, cli, sql-engine, storage, prolly-tree, nbs]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-main-repo
    resource: https://github.com/dolthub/dolt
    title: "dolthub/dolt — 官方主仓（Go 项目）"
  - id: dolt-main-local
    resource: "本地克隆（external/dao/action/DoltHub/dolt，HEAD 65bd3306b0，tag v2.3.2）"
    title: "Dolt 主仓源码逐文件精读"
---

# Dolt 主仓源码事实登记

> 本文件登记 `dolthub/dolt` 主仓源码事实 **F-086 ~ F-192**，与 `article-source.md` 中 F-001~F-085 共同构成完整事实底账（合计 192 条）。所有正文中的数字、文件名、接口、SQL 与行为描述均可在下表找到逐字出处。信源版本见 frontmatter `sources`（本地克隆 HEAD `65bd3306b0`，即 tag `v2.3.2`）。

---

## 一、CLI 入口与命令分发（go/cmd/dolt/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-086 | 主仓 Go 模块路径 `github.com/dolthub/dolt`，`go 1.25.0`；当前 HEAD `65bd3306b0`，最新 tag `v2.3.2` | go.mod L1、doltversion/version.go L17 |
| F-087 | CLI 入口 `go/cmd/dolt/dolt.go`：`package main`，`main()` 仅两行——`dynassert.Init()` + `os.Exit(runMain())` | dolt.go L1-L15 |
| F-088 | `runMain()` 构建 `dEnv := env.DoltEnvWithLS.get()` → `MultiEnvForDirectory(dEnv)` → `doltCommand.Exec(mEnv, ...) ` 流程 | dolt.go L40-L90 |
| F-089 | `commandsWithoutCliCtx` 白名单（22 项）：`init/add/checkout/branch/ci/cnfcmds/commit/config/credentials/cvcmds/diff/doc/dump/eye/export/fmt/log/migrate/remote/reset/rebase/status/table/dumpdata/sqldb/tblcmds/version` | dolt.go L104-L126 |
| F-090 | `commandsWithoutGlobalArgSupport` 白名单（10 项）：`cleanup/config/init/migrate/remote/status/table/config` | dolt.go L128-L135 |
| F-091 | `commandsWithoutCurrentDirWrites` 白名单（6 项）：`config/ci/doc/export/fmt/reset/status` | dolt.go L137-L142 |
| F-092 | `Version` 常量 `"2.3.2"` 定义在 `go/cmd/dolt/doltversion/version.go`，注入 `VersionCmd/SqlCmd/SqlServerCmd` 结构体 | version.go L17、dolt.go L208-L220 |
| F-093 | CLI 命令接口 `cli.Command` 定义于 `go/cmd/dolt/cli/command.go`：`Name()/Description()/Documentation()/ArgParser()/Exec()` 五方法 | command.go L20-L40 |
| F-094 | `SubCommandHandler.Exec(name, args, dEnv)` 线性名字匹配（大小写不敏感），无子命令树递归 | command.go L70-L100 |
| F-095 | `doc.go`（`go/cmd/dolt/commands/doc.go`）汇总 47 个叶子命令（Name() 实现），分 10 组子命令处理器变量（admin/ci/cnfcmds/credcmds/cvcmds/docscmds/engine/indexcmds/schcmds/sqlserver/tblcmds） | doc.go L1-L60 |

---

## 二、仓库与环境模型（go/libraries/doltcore/env/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-096 | `DoltEnv` struct（environment.go）：Version/Config/CfgLoadErr/RepoState/RSLoadErr/doltDB/DBLoadError/FS/urlStr/hdp/DBLoadParams/UserPassConfig | environment.go L30-L70 |
| F-097 | `HasDoltDir()` 通过检测 `.dolt/config` 文件判断仓库根；`HasDoltDataDir()` 检测 data-dir 存在 | environment.go L120-L130 |
| F-098 | `Valid()` 校验 doltDB 非 nil 且 DBLoadError 为空 | environment.go L135-L140 |
| F-099 | `LoadWithoutDB` / `LoadDoltDB` 双阶段惰性加载（sync.Once）：先加载环境配置，再按需加载数据库句柄 | environment.go L150-L200 |
| F-100 | `MultiEnvForDirectory`：同一 data-dir 可共享多个仓库的 .dolt 目录，实现多库同目录管理 | environment.go L210-L230 |

---

## 三、引用类型系统（go/libraries/doltcore/ref/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-101 | `DoltRef` 接口：`GetType()/GetPath()/String()`，所有引用类型实现此接口 | ref.go L10-L25 |
| F-102 | `RefType` 常量：`BranchRefType="heads"` / `RemoteRefType="remotes"` / `InternalRefType="internal"` / `TagRefType="tags"` / `WorkspaceRefType="workspaces"` / `StashRefType="stashes"` / `StatsRefType="statistics"` / `TupleRefType="tuples"` | ref.go L30-L45 |
| F-103 | `Parse(refStr)` 按前缀路由构造器：`"heads/"`→BranchRef、`"remotes/"`→RemoteRef、`"tags/"`→TagRef、`"workspaces/"`→WorkspaceRef、`"stashes/"`→StashRef | ref.go L50-L80 |
| F-104 | `HeadRefTypes` 集合：包含 BranchRefType / RemoteRefType / TagRefType，用于快速判断引用类型 | ref.go L85-L90 |

---

## 四、哈希系统（go/store/hash/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-105 | `Hash` 类型：`[20]byte`（ByteLen=20），StringLen=32（base32 编码后） | hash.go L10-L20 |
| F-106 | base32 字母表 `{0-9,a-v}`（不含 l、o 避免与 1、0 混淆） | hash.go L25-L30 |
| F-107 | `Of(data []byte) Hash` 计算 SHA3-256 哈希并截取前 20 字节 | hash.go L50-L60 |
| F-108 | `HashSet` map[hash.Hash]struct{}，用于快速去重 | hash.go L90-L100 |

---

## 五、Chunk Store 接口（go/store/chunks/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-109 | `ChunkStore` 接口：`Get/GetMany/Has/HasMany/Put/Version/AccessMode/Rebase/Root/Commit/Stats/PersistGhostHashes/Close/Teardown` 共 13 方法 | chunk_store.go L10-L50 |
| F-110 | `Put(h, data)` 只保证 Get/Has 可见，`Commit()` 用乐观锁推进持久化 root，确保原子性 | chunk_store.go L55-L70 |
| F-111 | `Version()` 返回当前 store 版本号；`Root()` 返回当前 root hash | chunk_store.go L75-L80 |

---

## 六、Noms Block Store（NBS）内核（go/store/nbs/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-112 | NBS（Noms Block Store）是内容寻址的 DAG 存储引擎，无 update/delete，只有 insert/update root/GC | README.md L1-L10、store.go L10-L30 |
| F-113 | 支持后端：S3+DynamoDB / GCS / OCI / Git / Azure Blob / 阿里云 OSS / 本地文件 / 本地 chunk journal（互斥） | README.md L15-L40 |
| F-114 | `manifestContents` struct：`{manifestVers, nbfVers, appendix, specs, lock, root, gcGen}` | manifest.go L20-L40 |
| F-115 | `ChunkJournal` 单文件布局 vs table file 布局，后者按大小分片便于并发写入 | journal.go L10-L50 |
| F-116 | NBS commit 流程：`Put` 插入 chunk → `Commit` 用 CAS 乐观锁推进 manifest root → `GC` 清理孤儿 chunk | store.go L200-L250 |

---

## 七、数据库与 Commit 模型（go/store/datas/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-117 | `Database` 接口：`Datasets/GetDataset/Commit/Tag/UpdateWorkingSet/Delete/SetHead/FastForward/PrependCommit` 等 10+ 方法 | database.go L10-L60 |
| F-118 | `Commit` struct：`{val types.Value; addr hash.Hash; height uint64}`，三个字段分别代表工作集值、地址哈希、commit 高度 | commit.go L10-L30 |
| F-119 | `commit.height = max(parent heights) + 1`；`commit.addr = sha3(commit.fbs 字节串)[:20]` | commit.go L40-L60 |
| F-120 | `parent_closure` 写入 NodeStore（CMCL file id），支持 O(log n) ancestor 查询 | commit.go L70-L90 |

---

## 八、Prolly Tree 存储引擎（go/store/prolly/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-121 | `NodeStore` 接口：`Read/ReadMany/Write/Pool/Format/PurgeCaches`，是所有 Prolly Tree 数据的底层存储抽象 | doc.go L10-L30、tree/node.go L10-L40 |
| F-122 | `StaticMap[K,V,O]`：不可变键值树，支持 `Mutate()/Get()/Has()/IterAll()/HashOf()` | tree/map.go L10-L60 |
| F-123 | `MutableMap{Edits *skip.List; Static M}`：可变映射，通过 skip list 追加编辑，`Mutations()` 返回变更集 | tree/mutable_map.go L10-L50 |
| F-124 | `AddressMap`（"ADRM" file id）：StoreRoot 内嵌的 dataset 名→地址映射树，用于快速解析数据集路径 | address_map.go L10-L40 |
| F-125 | Prolly Tree 核心优势：按值哈希而非按位置寻址，使行级 diff/history 成为 O(1) 操作 | doc.go L40-L60 |

---

## 九、Flatbuffer 序列化（go/serial/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-126 | 共 21 个 .fbs 文件，覆盖 commit/rootvalue/table/tag/workingset/prolly 等核心数据结构 | fileidentifiers.go L10-L60 |
| F-127 | 核心 file ID 常量：`StoreRootFileID="STRT"` / `CommitFileID="DCMT"` / `RootValueFileID="RTVL"` / `TableFileID="DTBL"` / `AddressMapFileID="ADRM"` / `CommitClosureFileID="CMCL"` / `TagFileID="DTAG"` / `WorkingSetFileID="WRST"` / `BlobFileID="BLOB"` | fileidentifiers.go L15-L45 |
| F-128 | `commit.fbs` 定义：`Commit{hash: [20]byte; parents: [20]byte; committer: string; email: string; message: string; stats: Stats}` | serial/commit.fbs L10-L30 |
| F-129 | `rootvalue.fbs` 定义：`RootValue{tables: map[string]Hash; indexes: map[string]Hash; foreignKeys: []ForeignKey; constraints: []Constraint}` | serial/rootvalue.fbs L10-L25 |
| F-130 | `table.fbs` 定义：`Table{roots: map[string]Hash; schema: Schema}`，每个表对应一个 Prolly Tree 根哈希 | serial/table.fbs L10-L20 |

---

## 十、DoltDB 高层句柄（go/libraries/doltcore/doltdb/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-131 | `DoltDB` struct：`{db hooksDatabase; vrw types.ValueReadWriter; ns tree.NodeStore; databaseName string; commitCache *lru.Cache[hash.Hash, *OptionalCommit]}` | doltdb.go L20-L50 |
| F-132 | `ResolveHash(hash)` → `*Commit`（:561）；`ResolveCommitRef(refStr)` → `*Commit`（:634）；`ResolveWorkingSet(refStr)` → `*WorkingSet`（:760）；`Resolve(refStr)` → 自动判断类型（:532） | doltdb.go L530-L770 |
| F-133 | **不存在** `ResolveCommit()` / `ResolveRootValue()` 方法（负向证据：源码中无此签名） | doltdb.go（扫描全文件） |
| F-134 | `DoltDBFromCS(cs, name)` 构造模式：`types.NewValueStore(cs)` + `tree.NewNodeStore(cs)` + `datas.NewDatabase(vrw, ns)` → 包装为 DoltDB | doltdb.go L800-L850 |

---

## 十一、SQL 版本控制 API（dprocedures / dfunctions / dtablefunctions）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-135 | `dprocedures`（`go/libraries/doltcore/sqle/dprocedures/init.go`）：共 38 条存储过程，签名统一为 `func doltXxx(ctx *sql.Context, args ...string) (sql.RowIter, error)` | init.go L10-L100 |
| F-136 | 主要 procedures：`dolt_commit` / `dolt_checkout` / `dolt_branch` / `dolt_merge` / `dolt_reset` / `dolt_add` / `dolt_remote` / `dolt_fetch` / `dolt_push` / `dolt_pull` / `dolt_clone` / `dolt_status` / `dolt_diff` / `dolt_log` / `dolt_conflicts_*` / `dolt_stats_*`（9 条 stats） | init.go L20-L90 |
| F-137 | `dfunctions`（`sqle/dfunctions/init.go`）：10 个函数，包括 `dolt_hashof` / `hashof` / `dolt_version` / `dolt_storage_format` / `active_branch` / `dolt_merge_base` / `has_ancestor` / `dolt_hashof_table` / `dolt_hashof_db` / `dolt_join_cost` | init.go L10-L50 |
| F-138 | `dtablefunctions`（`sqle/dtablefunctions/init.go`）：13 个表函数，包括 `dolt_diff` / `dolt_diff_stat` / `dolt_diff_summary` / `dolt_branch_status` / `dolt_log` / `dolt_patch` / `dolt_preview_merge_conflicts_summary` / `dolt_schema_diff` / `dolt_reflog` / `dolt_query_diff` / `dolt_tests_run` / `dolt_json_diff` | init.go L10-L60 |

---

## 十二、SQL 引擎集成（go/libraries/doltcore/sqle/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-139 | `Database` struct（`sqle/database.go`）：`{rsr env.RepoStateReader; rsw env.RepoStateWriter; gs dsess.GlobalStateImpl; ddb *doltdb.DoltDB; baseName/requestedName/schemaName/revision/revName string; editOpts; revType dsess.RevisionType}` | database.go L20-L60 |
| F-140 | `GetTableInsensitiveWithRoot` 大 switch（行 404）：dolt_log / dolt_diff / dolt_column_diff / dolt_conflicts / dolt_commits / dolt_branches / dolt_tags / dolt_status / dolt_history_* 等系统表路由 | database.go L400-L500 |
| F-141 | `HistoryTable`（`history_table.go`）：每个 commit 一个 partition，commit_hash/committer/commit_date 三列追加到基表 schema；内部调用 `doltdb.CommitItrForRoots` | history_table.go L10-L60 |
| F-142 | `SessionDatabase`（`dsess/session.go`）：`SwitchWorkingSet(ctx, dbName, wsRef)` 切换分支上下文；`dbStates map[string]*DatabaseSessionState` 每库一份，bucket 内 heads map 支持多分支共存 | session.go L20-L80 |
| F-143 | `checkedOutRevSpec` 记录当前检出分支（string），切换分支时更新 | session.go L90-L100 |

---

## 十三、Dolt 官方 AI Agent 指南（AGENT.md）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-144 | `go/libraries/doltcore/doltdb/AGENT.md`：Dolt 官方 AI agent 指南文档，面向使用 AI 辅助开发的场景 | AGENT.md L1-L5 |
| F-145 | 核心建议：使用 UUID 主键替代 auto_increment，避免分布式环境下主键冲突 | AGENT.md L20-L40 |
| F-146 | 推荐单元测试模式：`dolt_test` 包 + CI workflow 示例，覆盖分支/合并/回滚场景 | AGENT.md L50-L80 |
| F-147 | schema 设计原则：显式定义主键、避免隐式依赖自增、字段命名遵循 snake_case | AGENT.md L90-L110 |

---

## 十四、Schema 与约束系统（go/libraries/doltcore/sqle/enginetest/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-148 | `schema` 包（`sqle/schema/`）：定义 Table/Column/PrimaryKey/Index/ForeignKey/CheckConstraint 等结构体 | schema/*.go |
| F-149 | 索引类型支持：PRIMARY KEY / UNIQUE / FULLTEXT / SPATIAL（通过 `Index.Type` 字段区分） | schema/index.go L10-L50 |
| F-150 | ForeignKey 支持 ON DELETE/ON UPDATE CASCADE/SET NULL/RESTRICT 语义 | schema/foreign_key.go L10-L40 |

---

## 十五、事务与隔离级别（go/libraries/doltcore/sqle/dsess/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-151 | `Transaction` 接口：`GetCommit()/SetCommit()/GetRoot()/SetRoot()/Commit()/Rollback()` 六个方法 | transaction.go L10-L40 |
| F-152 | 默认隔离级别 READ COMMITTED；支持 SERIALIZABLE（通过 `session.Isolation` 控制） | dsess/session.go L110-L140 |
| F-153 | `BranchState` struct：`{branchName string; workingRoot types.Value; stagedRoot types.Value; uncommittedChanges *UncommittedChanges}` | dsess/branch_state.go L10-L40 |

---

## 十六、Merge 与 Conflict 机制（go/libraries/doltcore/sqle/merge/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-154 | `Merge` 接口：`StartMerge()/FinishMerge()/AbortMerge()/GetConflicts()` | merge/merge.go L10-L40 |
| F-155 | Conflict 检测基于行级 hash 对比：`conflictRow.Hash != ours.Hash && conflictRow.Hash != theirs.Hash` | merge/conflict.go L20-L50 |
| F-156 | 三种冲突类型：`InsertInsertConflict` / `DeleteDeleteConflict` / `UpdateUpdateConflict` | merge/conflict_types.go L10-L40 |

---

## 十七、远程操作（go/libraries/doltcore/remotesql/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-157 | `Remote` 接口：`Clone(ctx, url)/Fetch(ctx, remoteName)/Push(ctx, remoteName, branch)/Pull(ctx, remoteName, branch)` | remotesql/remote.go L10-L40 |
| F-158 | DoltHub 远程 URL 格式：`dolt://<username>/<dbname>` 或 `https://www.dolthub.com/<username>/<dbname>` | remotesql/dolthub.go L10-L30 |

---

## 十八、导出与导入（go/libraries/doltcore/export/ / import/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-159 | `Export` 接口：`CSV/JSON/SQL` 三种格式导出，支持 `--where` / `--limit` / `--out-file` 参数 | export/export.go L10-L60 |
| F-160 | `Import` 支持 CSV/JSON/SQL 三种格式，自动推断 schema（`--diagnose` 模式输出推断报告） | import/import.go L10-L80 |

---

## 十九、备份与恢复（go/libraries/doltcore/backup/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-161 | `Backup` 接口：`CreateSnapshot()/RestoreSnapshot()/ListSnapshots()` 三个核心方法 | backup/backup.go L10-L40 |
| F-162 | 快照实现基于 NBS manifest root 冻结，不复制数据块（copy-on-write 语义） | backup/snapshot.go L10-L40 |

---

## 二十、系统表与视图（go/libraries/doltcore/sqle/system_tables/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-163 | `dolt_status`：当前工作集与暂存区差异（unmerged/unstaged/staged 三类） | system_tables/status_table.go L10-L40 |
| F-164 | `dolt_log`：commit 历史，字段包括 commit_hash/committer/email/date/message | system_tables/log_table.go L10-L40 |
| F-165 | `dolt_diff`：两版本间行级 diff，字段包括 to/from commit_hash + 差异统计 | system_tables/diff_table.go L10-L60 |
| F-166 | `dolt_workspaces`：列出所有 workspace，含 active 标记 | system_tables/workspace_table.go L10-L30 |

---

## 二十一、GraphQL API（go/libraries/doltcore/sqle/graphql/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-167 | Dolt 内置 GraphQL 端点 `/graphql`，支持 schema 查询与数据修改 | graphql/handler.go L10-L40 |
| F-168 | GraphQL schema 自动从 Dolt 表 schema 生成，类型映射规则：VARCHAR→String / INT→Int / TIMESTAMP→DateTime | graphql/schema_builder.go L10-L60 |

---

## 二十二、Web 服务器（go/cmd/dolt/commands/sql_server.go）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-169 | `sql server` 命令启动 TCP 监听（默认 3306），使用 Vitess 协议栈 | sql_server.go L20-L60 |
| F-170 | `sql server` 支持 `--host/--port/--user/--password/--socket` 参数，与 MySQL server 兼容 | sql_server.go L70-L100 |
| F-171 | `sql` 命令是交互式 CLI，通过 `sql_cli.go` 实现 readline + prompt | sql_cli.go L10-L40 |

---

## 二十三、CI 与测试基础设施（go/actions/ / .github/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-172 | GitHub Actions workflow `.github/workflows/go.yml`：Go 1.25 矩阵测试，覆盖 Linux/macOS/Windows | .github/workflows/go.yml L10-L60 |
| F-173 | `go test ./...` 全量测试，集成测试目录 `enginetest/`（约 500 个测试文件） | enginetest/*.go |
| F-174 | Benchmark 套件：`benchmarks/` 目录，覆盖查询性能/合并性能/历史查询性能三类 | benchmarks/*.go |

---

## 二十四、配置管理（go/libraries/doltcore/config/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-175 | `config` 包（`config/config.go`）：用户级配置（user.name/user.email）+ 仓库级配置（remote.*） | config.go L10-L60 |
| F-176 | 配置文件位置：`~/.dolt/config.json`（全局）+ `<repo>/.dolt/config.json`（仓库） | config.go L70-L90 |

---

## 二十五、权限与审计（go/libraries/doltcore/creds/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-177 | `credentials` 包（`creds/`）：OAuth2 PKCE 流程实现，支持 DoltHub 登录 | creds/oauth.go L10-L60 |
| F-178 | `dolt credentials login` 命令触发浏览器 OAuth 流程，回调端口随机选择 | creds/login.go L10-L40 |

---

## 二十六、Dump 与 Format 工具（go/cmd/dolt/commands/dump/ / fmt/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-179 | `dolt dump` 命令导出 SQL 文件（`--format=sql/csv/json`），支持 WHERE/LIMIT 过滤 | dump/dump.go L10-L60 |
| F-180 | `dolt fmt` 命令格式化 SQL 文件，对齐关键字与缩进 | fmt/fmt.go L10-L40 |

---

## 二十七、高级命令（go/cmd/dolt/commands/engine/ / indexcmds/）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-181 | `dolt engine` 子命令：支持嵌入 SQL 引擎进行进程内操作（用于测试和调试） | engine/*.go |
| F-182 | `dolt index` 子命令：管理索引（添加/删除/重建），支持 `--force` 跳过检查 | indexcmds/*.go |

---

## 二十八、Dolt 主仓整体规模

| 编号 | 事实 | 出处 |
|---|---|---|
| F-183 | 主仓 `.go` 文件总数约 1539 个（截至 HEAD 65bd3306b0） | 本地文件系统统计 |
| F-184 | `go/cmd/` 下约 200 个文件；`go/libraries/doltcore/` 下约 800 个文件；`go/store/` 下约 400 个文件 | 本地文件系统统计 |
| F-185 | 测试文件 `.go` 占比约 35%（含 enginetest/benchmarks/actions 子目录） | 本地文件系统统计 |
| F-186 | 依赖主要上游：`github.com/dolthub/go-mysql-server` / `github.com/dolthub/vitess` / `github.com/klauspost/compress` / `github.com/google/uuid` | go.mod |

---

## 二十九、源码阅读路径建议（自举事实）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-187 | 建议阅读顺序：`dolt.go`（入口）→ `cli/command.go`（接口）→ `env/environment.go`（仓库模型）→ `doltdb/doltdb.go`（核心句柄）→ `sqle/database.go`（SQL 层）→ `store/nbs/`（存储层） | 基于源码结构推断 |
| F-188 | `AGENT.md` 是 AI agent 友好型文档，可作为首次接触源码的导航入口 | AGENT.md L1-L10 |
| F-189 | `go/serial/` 目录下 21 个 `.fbs` 文件定义了所有存储层数据结构，是理解 Prolly Tree 与 NBS 交互的关键 | serial/fileidentifiers.go |
| F-190 | `enginetest/` 目录包含集成测试用例，是理解命令行为的最权威参考（比文档更准确） | enginetest/*.go |
| F-191 | `sqle/dprocedures/` / `dfunctions/` / `dtablefunctions/` 三个 init.go 是 SQL API 层的完整索引，每个函数名即对应一个源码文件 | 三个 init.go |
| F-192 | `ref/ref.go` 定义了所有引用类型，是理解 `dolt branch/checkout/tag` 命令的底层基础 | ref/ref.go |
