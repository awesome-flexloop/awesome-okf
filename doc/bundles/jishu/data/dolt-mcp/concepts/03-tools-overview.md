---
type: Concept
title: "dolt-mcp 工具全景与安全注解"
description: "dolt-mcp 的 45 个 MCP 工具分类全景——库管理/表操作/读写/分支/版本控制/diff/合并/重置/远程/测试十大类，每个工具的工具名、参数与 hint 安全注解四元组参考表"
tags: [dolt-mcp, tools, reference, mcp, sql, version-control]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-mcp-source
    resource: /references/source.md
    title: dolt-mcp 源码事实登记
---

# dolt-mcp 工具全景与安全注解

> 本文给出 45 工具的完整分类、参数与安全注解参考。对应 [F-100~F-147](/references/source.md)。
> 数据/库表工具未单列时均需 `working_database`（+`working_branch`）参数；两参数语义："调用前先切换到该库/检出该分支"（F-101、F-118）。

## 安全注解四元组速读

每个工具携带四个 hint 注解，顺序记为 **(readOnly, destructive, idempotent, openWorld)**（F-100）：

- **readOnly=1**：纯读，事务内只 `Rollback`，无任何副作用（F-050）；
- **destructive=1**：破坏性操作（删库/删表/硬重置/强杀进程等），客户端应二次确认；
- **idempotent=1**：可安全重试（如 `if_not_exists`/`if_exists` 语义）；
- **openWorld=1**：访问外部世界（远程仓库/网络），不能仅靠本地状态推导结果。

## 一、数据库与服务器管理

| 工具 | 参数 | 注解 | 底层行为 |
|------|------|------|---------|
| `list_databases` | 无 | (1,0,1,0) | `SHOW DATABASES;`（F-102） |
| `create_database` | database*, if_not_exists | (0,0,1,0) | `CREATE DATABASE [IF NOT EXISTS] db;`（F-103） |
| `drop_database` | database*, if_exists | (0,1,1,0) | `DROP DATABASE [IF EXISTS] db;`（F-104） |
| `clone_database` | remote_url*, name | (0,0,1,**1**) | `CALL DOLT_CLONE(url[, name])`（F-105） |
| `select_version` | 无 | (1,0,1,0) | `SELECT DOLT_VERSION();`（F-106） |
| `show_processlist` | full | (1,0,1,0) | `SHOW [FULL] PROCESSLIST;`（F-115） |
| `kill_process` | process_id*, kill_query | (0,**1**,0,0) | `KILL [QUERY] id;`（F-116） |

> 注意：DoltLite 方言隐藏 list/create/drop/clone_database 与 show_processlist/kill_process（F-069）；Postgres 方言隐藏 show_processlist/kill_process（F-065）。

## 二、表结构操作

| 工具 | 参数 | 注解 | 底层行为 |
|------|------|------|---------|
| `show_tables` | +db+branch | (1,0,1,0) | `SHOW TABLES;`（方言化）（F-107） |
| `show_create_table` | +db+branch+table* | (1,0,1,0) | `SHOW CREATE TABLE t;`；找不到返回 "table not found"（F-108） |
| `describe_table` | +db+branch+table* | (1,0,1,0) | `DESCRIBE t;`；同守卫（F-109） |
| `create_table` | +db+branch+query* | (0,0,**0**,0) | 校验 CREATE TABLE 后直接执行语句（F-110） |
| `alter_table` | +db+branch+query* | (0,0,**0**,0) | 校验 ALTER TABLE 后执行（F-111） |
| `drop_table` | +db+branch+table*+if_exists | (0,**1**,1,0) | `DROP TABLE [IF EXISTS] t;`（F-112） |

## 三、数据读写（核心通道）

| 工具 | 参数 | 注解 | 底层行为 |
|------|------|------|---------|
| `query` | +db+branch+query* | (1,0,1,0) | 只读 SELECT/SHOW/EXPLAIN，校验后执行，Markdown 返回，事务 Rollback（F-113） |
| `exec` | +db+branch+query* | (0,**1**,**0**,0) | 写入 INSERT/UPDATE/DELETE，校验后执行并 COMMIT（F-114） |

## 四、分支管理

| 工具 | 参数 | 注解 | 底层行为 |
|------|------|------|---------|
| `list_dolt_branches` | working_database | (1,0,1,0) | `SELECT * FROM dolt_branches;`（F-117） |
| `select_active_branch` | +db+branch | (1,0,1,0) | `SELECT ACTIVE_BRANCH();`（F-118） |
| `create_dolt_branch` | +db + original_branch*, new_branch*, force | (0,0,0,0) | `CALL DOLT_BRANCH('-c'[, '-f'], orig, new)`（F-119） |
| `create_dolt_branch_from_head` | +db+branch + new_branch*, force | (0,0,0,0) | `CALL DOLT_BRANCH(['-f',] new)`（F-120） |
| `delete_dolt_branch` | +db+branch + branch*, force | (0,**1**,1,0) | `CALL DOLT_BRANCH('-d'[, '-f'], branch)`（F-121） |
| `move_dolt_branch` | +db+branch + old_name*, new_name*, force | (0,0,0,0) | `CALL DOLT_BRANCH('-m'[, '-f'], old, new)`（F-122） |

## 五、暂存与提交（版本控制核心）

| 工具 | 参数 | 注解 | 底层行为 |
|------|------|------|---------|
| `stage_table_for_dolt_commit` | +db+branch+table* | (0,0,1,0) | `CALL DOLT_ADD(table)`（F-123） |
| `stage_all_tables_for_dolt_commit` | +db+branch | (0,0,1,0) | `CALL DOLT_ADD('-A')`（F-124） |
| `unstage_table` | +db+branch+table* | (0,0,1,0) | `CALL DOLT_RESET(table)`（F-125） |
| `unstage_all_tables` | +db+branch | (0,0,1,0) | `CALL DOLT_RESET('.')`（F-126） |
| `create_dolt_commit` | +db+branch+message* | (0,0,1,0) | `CALL DOLT_COMMIT('-m', msg)`（F-127） |
| `list_dolt_commits` | +db+branch | (1,0,1,0) | `SELECT * FROM dolt_log;`（F-130） |
| `dolt_reset_soft` | +db+branch+revision* | (0,0,1,0) | `CALL DOLT_RESET('--soft', rev)`（F-128） |
| `dolt_reset_hard` | +db+branch+revision* | (0,**1**,1,0) | `CALL DOLT_RESET('--hard', rev)`（F-129） |

> revision 取值：分支名/commit sha/祖先表达式（如 `HEAD~1`）；表名不是合法 revision（F-128/F-129 描述）。

## 六、Diff 与状态

| 工具 | 参数 | 注解 | 底层行为 |
|------|------|------|---------|
| `list_dolt_diff_changes_in_working_set` | +db+branch | (1,0,1,0) | `SELECT * FROM dolt_diff WHERE commit_hash='WORKING';`（F-131） |
| `list_dolt_diff_changes_by_table_name` | +db+branch+table* + from_commit/to_commit/hash_of_from_commit/hash_of_to_commit | (1,0,1,0) | 两提交间某表 diff；显式 commit 优先否则 HASHOF()（F-132） |
| `list_dolt_diff_changes_in_date_range` | +db+branch+start*+end* | (1,0,1,0) | `SELECT * FROM dolt_diff WHERE date BETWEEN start AND end;`（F-133） |
| `get_dolt_merge_status` | +db+branch | (1,0,1,0) | `SELECT * FROM dolt_merge_status;`（F-134） |

## 七、合并

| 工具 | 参数 | 注解 | 底层行为 |
|------|------|------|---------|
| `merge_dolt_branch` | +db+branch + branch*, message | (0,**1**,0,0) | `CALL DOLT_MERGE(branch[, '-m', msg])`（F-135） |
| `merge_dolt_branch_no_fast_forward` | 同上 | (0,**1**,0,0) | 加 `'--no-ff'` 强制生成合并提交（F-136） |

## 八、远程仓库操作

| 工具 | 参数 | 注解 | 底层行为 |
|------|------|------|---------|
| `list_dolt_remotes` | working_database | (1,0,1,0) | `SELECT * FROM dolt_remotes;`（F-137） |
| `add_dolt_remote` | +db + remote_name*, remote_url* | (0,0,1,0) | `CALL DOLT_REMOTE('add', name, url)`（F-138） |
| `remove_dolt_remote` | +db + remote_name* | (0,0,1,0) | `CALL DOLT_REMOTE('remove', name)`（F-139） |
| `dolt_fetch_branch` | +db + remote_name*, branch* | (0,0,1,**1**) | `CALL DOLT_FETCH(remote, branch)`（F-140） |
| `dolt_fetch_all_branches` | +db + remote_name* | (0,0,1,**1**) | `CALL DOLT_FETCH(remote)`（F-141） |
| `dolt_push_branch` | +db + remote_name*, branch*, force | (0,0,**0**,**1**) | force→`DOLT_PUSH('--force', remote, branch)`（F-142） |
| `dolt_pull_branch` | +db + remote_name*, branch*, force | (0,0,**0**,**1**) | force→`DOLT_PULL(remote, branch, '--force')`（F-143） |

> push 的 `--force` 在参数首位，pull 的 `--force` 在末位——两者 force 位置相反（F-142/F-143 差异）。

## 九、测试工具（dolt_tests）

| 工具 | 参数 | 注解 | 底层行为 |
|------|------|------|---------|
| `run_dolt_tests` | +db+branch + target | (1,0,1,0) | `SELECT * FROM dolt_test_run()['<target>']`（F-144） |
| `add_dolt_test` | +db+branch + test_name*, query*, assertion_type*, assertion_comparator* + test_group/assertion_value | (0,0,1,0) | 校验 query 只读后 `REPLACE INTO dolt_tests` 六列 upsert（F-145） |
| `remove_dolt_test` | +db+branch + test_name* | (0,**1**,1,0) | `DELETE FROM dolt_tests ...`（F-146） |

> 断言枚举：assertion_type ∈ expected_rows/expected_columns/expected_single_value；comparator ∈ `==`/`!=`/`<`/`>`/`<=`/`>=`（F-145）。Postgres 方言禁用这三个工具（F-065）；DoltLite 支持（F-095）。

## 已知源码怪癖（按源码如实记录）

- `stage_all_tables_for_dolt_commit` 描述误用单数 "Stages a table..."（F-124/F-147）；
- `list_dolt_diff_changes_in_date_range` 的描述错绑为 `create_dolt_branch` 的描述（F-133/F-147）；
- `dolt_pull_branch` 的 working_database 参数描述错绑为 working_branch 文案（F-143/F-147）；
- `merge_dolt_branch_no_fast_forward` 描述含拼写 "fast-foward"（F-136）；
- `list_dolt_diff_changes_by_table_name` 的 to_commit/hash_of_* 参数描述复用 from_commit 描述（F-132/F-147）。

这些属描述性瑕疵，不影响工具行为，读者遇 AI 依据描述用错时可参考本表。

## 相关概念

* [架构分层](/concepts/01-architecture.md)
* [SQL 安全机制](/concepts/04-sql-safety.md)
* [DoltLite 内嵌模式](/concepts/06-doltlite-mode.md)
* 实操见 [examples/01-branch-commit-merge-workflow](../examples/01-branch-commit-merge-workflow.md)
