# 示例：分支合并工作流

> 本文档展示 Dolt 的分支/合并/冲突处理完整工作流的源码对照。
> **注意**：当前环境未安装 `dolt`，以源码文件锚点形式呈现。
> 对应 F-112~F-156。

---

## 完整工作流：功能分支开发

### 阶段 1：创建功能分支

```bash
# 确认当前在 main 分支
dolt branch

# 创建并切换到新功能分支
dolt branch feature/new-column
dolt checkout feature/new-column
```

**源码路径**：

| 操作 | 源码 | 核心函数 |
|------|------|---------|
| `dolt branch` | `commands/branch.go` | 调用 `doltdb.ListBranches()` |
| `dolt branch feature/new-column` | `commands/branch.go` | 调用 `doltdb.NewBranch()` |
| `dolt checkout feature/new-column` | `commands/checkout.go` | 调用 `SessionDatabase.SwitchWorkingSet()` |

> **F-136、F-142**

### 阶段 2：在分支上开发

```sql
-- 在 feature 分支上添加新列
ALTER TABLE employees ADD COLUMN bonus DECIMAL(10,2);

-- 插入测试数据
INSERT INTO employees (id, name, bonus)
VALUES ('c3d4', '李四', 2000.00);

-- 查看工作集状态
SELECT * FROM dolt_status;

-- 暂存变更
CALL dolt_add('employees');
SELECT * FROM dolt_status;
```

**源码路径**：

| 操作 | 源码 | 说明 |
|------|------|------|
| `ALTER TABLE` | `sqle/ALTER_TABLE.go` | 调用 schema 修改逻辑 |
| `dolt_add` | `dprocedures/dolt_add.go` | 更新 stagedRoot |
| `dolt_status` | `system_tables/status_table.go` | 比较 workingRoot 与 stagedRoot |

### 阶段 3：提交

```sql
-- 提交变更
CALL dolt_commit('-m', '为 employees 表添加 bonus 列');

-- 查看提交历史
SELECT * FROM dolt_log(5);
```

**源码路径**：

| 操作 | 源码 | 核心逻辑 |
|------|------|---------|
| `dolt_commit` | `dprocedures/dolt_commit.go` | 创建 Commit 对象，更新 HEAD |
| Commit 创建 | `store/datas/commit.go` | `commit.height = max(parents) + 1` |
| 日志查询 | `system_tables/log_table.go` | 遍历 CommitItrForRoots |

> **F-118 ~ F-120**

### 阶段 4：推送到远程

```bash
# 推送 feature 分支
dolt push origin feature/new-column

# 或直接 clone 远程仓库
dolt clone dolt://username/mydb
```

**源码路径**：

| 操作 | 源码 | 说明 |
|------|------|------|
| `dolt push` | `dprocedures/dolt_push.go` | 调用 `Remote.Push()` |
| `dolt clone` | `dprocedures/dolt_clone.go` | 调用 `Remote.Clone()` |
| 远程接口 | `remotesql/remote.go` | Clone/Fetch/Push/Pull |

> **F-157 ~ F-158**

---

## 完整工作流：合并与冲突处理

### 阶段 5：在主分支上合并

```bash
# 切换回 main
dolt checkout main

# 尝试合并 feature 分支
dolt merge feature/new-column
```

**源码路径**：

| 操作 | 源码 | 核心函数 |
|------|------|---------|
| `dolt merge` | `commands/merge.go` | 调用 `merge.StartMerge()` |
| 冲突检测 | `merge/conflict.go L20` | 行级 hash 对比 |

> **F-154 ~ F-155**

### 阶段 6a：无冲突情况

```sql
-- 查看合并状态
SELECT * FROM dolt_merge_status;
-- 输出：空结果（无冲突）

-- 完成合并
CALL dolt_commit('-m', '合并 feature/new-column');
```

### 阶段 6b：有冲突情况

```sql
-- 查看冲突详情
SELECT * FROM dolt_conflicts;

-- 查看冲突的基线（共同祖先）
SELECT * FROM dolt_conflicts_baseline;

-- 查看 ours 版本
SELECT * FROM dolt_conflicts_ours;

-- 查看 theirs 版本
SELECT * FROM dolt_conflicts_theirs;
```

**源码路径**：

| 查询 | 源码 |
|------|------|
| `dolt_conflicts` | `system_tables/conflicts_table.go` |
| `dolt_conflicts_baseline` | `system_tables/conflicts_baseline_table.go` |
| `dolt_conflicts_ours` | `system_tables/conflicts_ours_table.go` |
| `dolt_conflicts_theirs` | `system_tables/conflicts_theirs_table.go` |

### 阶段 7：解决冲突

```sql
-- 方案一：保留 theirs 版本
INSERT INTO employees (id, name, bonus)
SELECT id, name, bonus FROM dolt_conflicts_theirs
WHERE conflict_type = 'UpdateUpdateConflict';

-- 方案二：手动合并（取平均值）
INSERT INTO employees (id, name, bonus)
SELECT id, name, (ours.bonus + theirs.bonus) / 2
FROM dolt_conflicts_ours ours
JOIN dolt_conflicts_theirs theirs ON ours.id = theirs.id;

-- 标记冲突已解决
CALL dolt_conflicts_resolve('employees');

-- 完成合并提交
CALL dolt_commit('-m', '解决 employees 表合并冲突');
```

**源码路径**：

| 操作 | 源码 |
|------|------|
| 冲突解决 | `dprocedures/dolt_conflicts_resolve.go` |
| 合并完成 | `merge/merge.go:FinishMerge()` |
| 冲突类型判定 | `merge/conflict_types.go` |

> **F-156**

---

## 三种冲突类型详解

### 1. InsertInsertConflict

双方在不同分支都插入了相同主键的行：

```sql
-- 冲突特征：
-- ours:  INSERT INTO employees VALUES ('e5f6', '王五', 3000);
-- theirs: INSERT INTO employees VALUES ('e5f6', '王五', 3500);

SELECT * FROM dolt_conflicts WHERE conflict_type = 'InsertInsertConflict';
```

### 2. DeleteDeleteConflict

双方都删除了同一行：

```sql
-- 冲突特征：
-- ours:  DELETE FROM employees WHERE id = 'e5f6';
-- theirs: DELETE FROM employees WHERE id = 'e5f6';

SELECT * FROM dolt_conflicts WHERE conflict_type = 'DeleteDeleteConflict';
```

### 3. UpdateUpdateConflict

双方都修改了同一行的不同列：

```sql
-- 冲突特征：
-- ours:  UPDATE employees SET salary = 16000 WHERE id = 'a1b2';
-- theirs: UPDATE employees SET bonus = 2000 WHERE id = 'a1b2';

SELECT * FROM dolt_conflicts WHERE conflict_type = 'UpdateUpdateConflict';
```

**冲突检测源码**（`merge/conflict.go`）：

```go
if conflictRow.Hash != ours.Hash && conflictRow.Hash != theirs.Hash {
    // 三方冲突：三方 hash 均不同
}
```

> **F-155 ~ F-156**

---

## 回退操作

```bash
# 撤销最近一次 commit（保留工作集变更）
dolt reset HEAD~1

# 撤销最近一次 commit（丢弃工作集变更）
dolt reset --hard HEAD~1

# 恢复到指定版本
dolt reset --soft abc123def
```

**源码路径**：

| 操作 | 源码 |
|------|------|
| `dolt reset` | `dprocedures/dolt_reset.go` |
| 软重置 | 调用 `DoltDB.SetHead()` 不修改 workingRoot |
| 硬重置 | 调用 `DoltDB.SetHead()` + `ResetWorkingSet()` |

---

## 源码阅读建议

若深入理解此工作流的实现，建议按以下顺序阅读源码：

```
doltdb.go:ResolveCommitRef()      → 理解分支引用解析
doltdb.go:ResolveWorkingSet()     → 理解工作集结构
history_table.go                  → 理解历史视图实现
merge/conflict.go                 → 理解冲突检测逻辑
dprocedures/dolt_commit.go        → 理解提交实现
dprocedures/dolt_merge.go         → 理解合并入口
```

---

*本文档为源码对照参考，因当前环境未安装 dolt，无法提供实测输出。*
