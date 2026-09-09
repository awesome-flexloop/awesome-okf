# 示例：SQL 版本控制 API

> 本文档展示通过 SQL 接口进行版本控制操作的源码对照。
> **注意**：当前环境未安装 `dolt`，以源码文件锚点形式呈现。
> 对应 F-112~F-153。

---

## 示例 1：存储过程调用

### 1.1 提交变更

```sql
-- 方法一：通过存储过程
CALL dolt_add('employees');
CALL dolt_commit('-m', '更新员工薪资');

-- 方法二：通过表函数
SELECT * FROM dolt_diff();
```

**源码对照**：

| 调用 | 源码文件 | 关键函数 |
|------|---------|---------|
| `CALL dolt_add(...)` | `sqle/dprocedures/dolt_add.go` | `func dolt_add(ctx, args...)` |
| `CALL dolt_commit(...)` | `sqle/dprocedures/dolt_commit.go` | 调用 `DoltDB.Commit()` |
| `SELECT * FROM dolt_diff()` | `sqle/dtablefunctions/diff.go` | 返回 `diffTable` |

> **F-135 ~ F-136**

### 1.2 分支操作

```sql
-- 创建分支
CALL dolt_branch('feature/salary');

-- 切换分支
CALL dolt_checkout('feature/salary');

-- 删除分支
CALL dolt_branch('-d', 'feature/salary');

-- 查看当前分支
SELECT ACTIVE_BRANCH();
```

**源码对照**：

| 调用 | 源码文件 |
|------|---------|
| `CALL dolt_branch()` | `sqle/dprocedures/dolt_branch.go` |
| `CALL dolt_checkout()` | `sqle/dprocedures/dolt_checkout.go` |
| `SELECT ACTIVE_BRANCH()` | `sqle/dfunctions/active_branch.go` |

### 1.3 合并分支

```sql
-- 切换到目标分支
CALL dolt_checkout('main');

-- 执行合并
CALL dolt_merge('feature/salary');

-- 查看合并状态
SELECT * FROM dolt_merge_status;
```

**源码对照**：

| 调用 | 源码文件 | 关键逻辑 |
|------|---------|---------|
| `CALL dolt_merge()` | `sqle/dprocedures/dolt_merge.go` | 调用 `merge.Merge.StartMerge()` |
| `SELECT * FROM dolt_merge_status` | `system_tables/merge_status_table.go` | 查询冲突状态 |

> **F-154 ~ F-156**

---

## 示例 2：标量函数

### 2.1 版本与格式信息

```sql
-- 查看 Dolt 版本
SELECT DOLT_VERSION();
-- 输出："2.3.2"

-- 查看存储格式
SELECT DOLT_STORAGE_FORMAT();
-- 输出："memfs+noms" 或 "sql"
```

**源码对照**：

| 函数 | 源码文件 |
|------|---------|
| `DOLT_VERSION()` | `sqle/dfunctions/version.go` |
| `DOLT_STORAGE_FORMAT()` | `sqle/dfunctions/storage_format.go` |

### 2.2 哈希计算

```sql
-- 计算行的内容哈希
SELECT DOLT_HASHOF('employees', 1);

-- 计算表的哈希
SELECT DOLT_HASHOF_TABLE('employees');

-- 计算数据库的哈希
SELECT DOLT_HASHOF_DB();
```

**源码对照**：

| 函数 | 源码文件 |
|------|---------|
| `DOLT_HASHOF(table, row)` | `sqle/dfunctions/hashof.go` |
| `DOLT_HASHOF_TABLE(table)` | `sqle/dfunctions/hashof_table.go` |
| `DOLT_HASHOF_DB()` | `sqle/dfunctions/hashof_db.go` |

> **F-137**

### 2.3 祖先关系查询

```sql
-- 判断 commit 祖先关系
SELECT HAS_ANCESTOR(
    'abc123def456...',
    '789ghi012jkl345...'
);

-- 查找两个分支的最近公共祖先
SELECT DOLT_MERGE_BASE('main', 'feature');
```

**源码对照**：

| 函数 | 源码文件 |
|------|---------|
| `HAS_ANCESTOR()` | `sqle/dfunctions/has_ancestor.go` |
| `DOLT_MERGE_BASE()` | `sqle/dfunctions/merge_base.go` |

---

## 示例 3：表函数

### 3.1 差异查询

```sql
-- 工作集差异
SELECT * FROM dolt_diff();

-- 两版本差异
SELECT * FROM dolt_diff('main', 'feature');

-- 差异统计
SELECT * FROM dolt_diff_stat('main', 'feature');

-- 差异摘要
SELECT * FROM dolt_diff_summary('main', 'feature');
```

**源码对照**：

| 表函数 | 源码文件 | 输出列 |
|--------|---------|--------|
| `dolt_diff()` | `sqle/dtablefunctions/diff.go` | to/from_hash, table, before/after values |
| `dolt_diff_stat()` | `sqle/dtablefunctions/diff_stat.go` | table, rows_added, rows_deleted |
| `dolt_diff_summary()` | `sqle/dtablefunctions/diff_summary.go` | 压缩格式的差异概览 |

### 3.2 历史查询

```sql
-- 提交历史
SELECT * FROM dolt_log();

-- 带限制的日志
SELECT * FROM dolt_log(10);

-- 引用日志（查看 checkout 历史）
SELECT * FROM dolt_reflog();
```

**源码对照**：

| 表函数 | 源码文件 |
|--------|---------|
| `dolt_log()` | `sqle/dtablefunctions/log.go` |
| `dolt_reflog()` | `sqle/dtablefunctions/reflog.go` |

### 3.3 合并预览

```sql
-- 预览合并冲突
SELECT * FROM dolt_preview_merge_conflicts_summary('feature');

-- Schema 差异
SELECT * FROM dolt_schema_diff('main', 'feature');
```

**源码对照**：

| 表函数 | 源码文件 |
|--------|---------|
| `dolt_preview_merge_conflicts_summary()` | `sqle/dtablefunctions/preview_merge_conflicts.go` |
| `dolt_schema_diff()` | `sqle/dtablefunctions/schema_diff.go` |

> **F-138**

---

## 示例 4：历史表查询

### 4.1 基本查询

```sql
-- 查询某行的所有历史版本
SELECT * FROM dolt_history_employees WHERE id = 'a1b2';

-- 查询特定时间段内的变更
SELECT * FROM dolt_history_employees 
WHERE id = 'a1b2' 
  AND commit_date >= '2026-01-01';
```

**源码对照**：

[history_table.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/history_table.go) — 每个 commit 一个 partition，追加 `commit_hash/committer/commit_date` 三列。

> **F-141**

### 4.2 分支视角的历史

```sql
-- 在 feature 分支上查询
CALL dolt_checkout('feature');
SELECT * FROM dolt_history_employees WHERE id = 'a1b2';

-- 回到 main 对比
CALL dolt_checkout('main');
SELECT * FROM dolt_history_employees WHERE id = 'a1b2';
```

分支切换通过 `SessionDatabase.SwitchWorkingSet()` 实现，历史视图自动跟随当前检出分支变化。

> **F-142 ~ F-143**

---

## 示例 5：系统表直接查询

```sql
-- 查看工作集状态
SELECT * FROM dolt_status;

-- 查看所有分支
SELECT * FROM dolt_branches;

-- 查看所有标签
SELECT * FROM dolt_tags;

-- 查看提交详情
SELECT * FROM dolt_commits LIMIT 10;

-- 查看 workspace
SELECT * FROM dolt_workspaces;
```

**源码对照**：

| 系统表 | 源码文件 |
|--------|---------|
| `dolt_status` | `system_tables/status_table.go` |
| `dolt_branches` | `system_tables/branches_table.go` |
| `dolt_tags` | `system_tables/tags_table.go` |
| `dolt_commits` | `system_tables/commits_table.go` |
| `dolt_workspaces` | `system_tables/workspace_table.go` |

> **F-163 ~ F-166**

---

## 示例 6：事务控制

```sql
-- 开启事务
START TRANSACTION;

-- 修改数据
UPDATE employees SET salary = 16000 WHERE id = 'a1b2';

-- 暂存并提交版本控制
CALL dolt_add('employees');
CALL dolt_commit('-m', '更新薪资');

-- 提交 SQL 事务
COMMIT;

-- 或回滚
ROLLBACK;
```

**源码对照**：

| 概念 | 源码文件 |
|------|---------|
| 事务接口 | `sqle/dsess/transaction.go` |
| 隔离级别 | `dsess/session.go L110` |
| BranchState | `dsess/branch_state.go` |

> **F-151 ~ F-153**

---

*本文档为源码对照参考，因当前环境未安装 dolt，无法提供实测输出。*
