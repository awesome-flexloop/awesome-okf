---
okf_version: "0.2"
type: concept
title: SQL 版本控制 API
description: "dolthub/dolt 主仓 SQL 版本控制层源码解读——dprocedures/dfunctions/dtablefunctions 三类 API、SQL 引擎集成、历史表与事务模型，F-112~F-153"
tags: [dolt, sql, source-code, stored-procedure, prolly-tree, transaction]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-main-repo
    resource: https://github.com/dolthub/dolt
    title: "dolthub/dolt 官方主仓"
  - id: dolt-main-local
    resource: "external/dao/action/DoltHub/dolt（HEAD 65bd3306b0，tag v2.3.2）"
    title: "Dolt 主仓源码逐文件精读"
---

# SQL 版本控制 API

> 本文档覆盖 Dolt 的 SQL 版本控制 API 层，包括三类特殊 SQL 对象（存储过程/函数/表函数）、SQL 引擎集成、历史表与事务模型。对应 F-112~F-153。
> **信源距离**：① 官方源码（本地克隆 `external/dao/action/DoltHub/dolt`）。

---

## 一、三类 SQL 对象总览

Dolt 通过三类特殊 SQL 对象暴露版本控制能力：

| 类型 | 目录 | 数量 | 签名模式 |
|------|------|------|----------|
| 存储过程 | `sqle/dprocedures/` | 38 条 | `func doltXxx(ctx, args...string) (RowIter, error)` |
| 标量函数 | `sqle/dfunctions/` | 10 个 | `func doltXxx(ctx, args...) (interface{}, error)` |
| 表函数 | `sqle/dtablefunctions/` | 13 个 | `func doltXxx(ctx, args...) (sql.TableFunction, error)` |

> **F-135 ~ F-138**

---

## 二、存储过程（dprocedures）

### 2.1 核心命令映射

| dproc 名称 | 对应 CLI 命令 | 功能 |
|------------|-------------|------|
| `dolt_commit` | `dolt commit` | 提交暂存变更 |
| `dolt_checkout` | `dolt checkout` | 切换分支/恢复文件 |
| `dolt_branch` | `dolt branch` | 创建/删除/移动分支 |
| `dolt_merge` | `dolt merge` | 合并分支 |
| `dolt_reset` | `dolt reset` | 重置暂存区/工作集 |
| `dolt_add` | `dolt add` | 暂存文件 |
| `dolt_remote` | `dolt remote` | 管理远程仓库 |
| `dolt_fetch` | `dolt fetch` | 拉取远程更新 |
| `dolt_push` | `dolt push` | 推送分支 |
| `dolt_pull` | `dolt pull` | 拉取并合并 |
| `dolt_clone` | `dolt clone` | 克隆远程仓库 |
| `dolt_status` | `dolt status` | 查看工作集状态 |
| `dolt_diff` | `dolt diff` | 比较版本差异 |
| `dolt_log` | `dolt log` | 查看提交历史 |

> **F-136**

### 2.2 Stats 存储过程

9 条 stats 存储过程用于统计信息更新：

```sql
CALL dolt_stats_update_statistics();
CALL dolt_stats_delete_statistics();
CALL dolt_stats_dump_statistics();
CALL dolt_stats_load_statistics();
-- ... 等共 9 条
```

> **F-136**

---

## 三、标量函数（dfunctions）

| 函数名 | 返回类型 | 说明 |
|--------|---------|------|
| `DOLT_VERSION()` | string | 返回 Dolt 版本号 |
| `DOLT_STORAGE_FORMAT()` | string | 返回当前存储格式版本 |
| `ACTIVE_BRANCH()` | string | 返回当前检出分支名 |
| `DOLT_HASHOF(table, row)` | hash | 计算行的内容哈希 |
| `DOLT_MERGE_BASE(branch1, branch2)` | hash | 返回两分支的最近公共祖先 |
| `HAS_ANCESTOR(commit1, commit2)` | bool | commit1 是否是 commit2 的祖先 |
| `DOLT_JOIN_COST(query)` | int | 预估查询代价 |

> **F-137**

---

## 四、表函数（dtablefunctions）

表函数返回的是可被 `SELECT * FROM dolt_xxx()` 查询的结果集：

| 表函数 | 用途 |
|--------|------|
| `dolt_diff([from], [to])` | 版本间行级差异 |
| `dolt_diff_stat([from], [to])` | 差异统计（行数变化） |
| `dolt_diff_summary([from], [to])` | 差异摘要 |
| `dolt_branch_status()` | 分支状态（是否 ahead/behind） |
| `dolt_log([limit])` | 提交历史（替代 `SELECT * FROM dolt_log`） |
| `dolt_patch([from], [to])` | 生成 SQL patch |
| `dolt_preview_merge_conflicts_summary()` | 预览合并冲突 |
| `dolt_schema_diff([from], [to])` | Schema 差异 |
| `dolt_reflog()` | 引用日志 |
| `dolt_query_diff(query)` | 查询结果差异 |
| `dolt_tests_run()` | 运行测试 |
| `dolt_json_diff([from], [to])` | JSON 格式差异 |

> **F-138**

---

## 五、SQL 引擎集成

### 5.1 Database 结构

[database.go](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/database.go) 中的 `Database` 结构体：

```go
type Database struct {
    rsr        env.RepoStateReader
    rsw        env.RepoStateWriter
    gs         dsess.GlobalStateImpl
    ddb        *doltdb.DoltDB
    baseName     string
    requestedName string
    schemaName   string
    revision     string
    revName      string
    editOpts     sql.DatabaseOptions
    revType      dsess.RevisionType
}
```

> **F-139**

### 5.2 系统表路由

`GetTableInsensitiveWithRoot()` 大 switch（约 100 行）路由到对应系统表实现：

```go
switch tableName {
case "dolt_log":       return newLogTable(...)
case "dolt_diff":      return newDiffTable(...)
case "dolt_status":    return newStatusTable(...)
case "dolt_commits":   return newCommitsTable(...)
case "dolt_branches":  return newBranchesTable(...)
case "dolt_tags":      return newTagsTable(...)
// ... 等约 20 个系统表
}
```

> **F-140**

---

## 六、历史表（HistoryTable）

[history_table.go](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/history_table.go) 实现 `dolt_history_<tablename>` 系统表：

**核心设计**：
- 每个 commit 对应一个 partition
- 原始表的每一行追加三个元数据列：`commit_hash` / `committer` / `commit_date`
- 内部调用 `doltdb.CommitItrForRoots` 遍历历史

**查询示例**：
```sql
-- 查询某行在所有版本中的历史
SELECT * FROM dolt_history_employees WHERE id = 0;

-- 查询特定 commit 之后的历史
SELECT * FROM dolt_history_employees 
WHERE id = 0 AND commit_hash >= 'abc123';
```

> **F-141**

---

## 七、会话与分支管理

### 7.1 SessionDatabase

[session.go](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/dsess/session.go) 维护连接级别的分支状态：

| 字段 | 类型 | 说明 |
|------|------|------|
| `dbStates` | `map[string]*DatabaseSessionState` | 每数据库一份状态 |
| `heads` | `map[string]*branchState` | 每库内多分支共存 |
| `checkedOutRevSpec` | `string` | 当前检出分支 |

`SwitchWorkingSet(ctx, dbName, wsRef)` 方法切换分支上下文。

> **F-142 ~ F-143**

### 7.2 BranchState

```go
type BranchState struct {
    branchName         string
    workingRoot        types.Value
    stagedRoot         types.Value
    uncommittedChanges *UncommittedChanges
}
```

- `workingRoot`：工作集根哈希
- `stagedRoot`：暂存区根哈希
- `uncommittedChanges`：未提交的变更集合

> **F-153**

---

## 八、事务模型

### 8.1 Transaction 接口

```go
type Transaction interface {
    GetCommit() *commit.Commit
    SetCommit(*commit.Commit)
    GetRoot() types.Value
    SetRoot(types.Value)
    Commit() error
    Rollback() error
}
```

> **F-151**

### 8.2 隔离级别

| 级别 | 说明 | 默认 |
|------|------|------|
| `READ COMMITTED` | 每次查询读取最新已提交数据 | ✅ |
| `SERIALIZABLE` | 完全串行化，通过 `session.Isolation` 控制 | ❌ |

> **F-152**

---

## 九、Merge 与 Conflict

### 9.1 Merge 接口

```go
type Merge interface {
    StartMerge(targetBranch string) error
    FinishMerge() error
    AbortMerge() error
    GetConflicts() ([]Conflict, error)
}
```

> **F-154**

### 9.2 冲突检测

基于行级 hash 对比：
```go
if conflictRow.Hash != ours.Hash && conflictRow.Hash != theirs.Hash {
    // 三方冲突
}
```

三种冲突类型：
- `InsertInsertConflict`：双方都插入了相同主键
- `DeleteDeleteConflict`：双方都删除了同一行
- `UpdateUpdateConflict`：双方都修改了同一行

> **F-155 ~ F-156**

---

## 十、源码阅读路径

建议阅读顺序：

```
dprocedures/init.go（过程入口索引）
    ↓
dfunctions/init.go（函数入口索引）
    ↓
dtablefunctions/init.go（表函数入口索引）
    ↓
sqle/database.go（SQL 引擎集成）
    ↓
sqle/history_table.go（历史表实现）
    ↓
sqle/dsess/session.go（会话与分支管理）
    ↓
sqle/merge/（合并与冲突处理）
```

> **F-187**

---

*本文档基于源码事实（F-112~F-153）生成，信源距离 ①。*
