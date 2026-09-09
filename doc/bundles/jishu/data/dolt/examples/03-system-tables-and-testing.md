# 示例：系统表与测试

> 本文档展示 Dolt 系统表的查询方式与测试基础设施的源码对照。
> **注意**：当前环境未安装 `dolt`，以源码文件锚点形式呈现。
> 对应 F-163~F-174。

---

## 示例 1：系统表全景查询

### 1.1 查看所有系统表

```sql
-- Dolt 系统表清单
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = DATABASE()
  AND table_name LIKE 'dolt_%';
```

### 1.2 各系统表查询示例

```sql
-- 工作集状态（unstaged/staged 变更）
SELECT * FROM dolt_status;

-- 提交历史
SELECT commit_hash, committer, email, date, message
FROM dolt_log 
ORDER BY date DESC 
LIMIT 20;

-- 版本差异（当前 vs 上一个 commit）
SELECT * FROM dolt_diff();

-- 两版本间差异
SELECT * FROM dolt_diff('abc123', 'def456');

-- 分支列表
SELECT * FROM dolt_branches;

-- 标签列表
SELECT * FROM dolt_tags;

-- Workspace 列表
SELECT * FROM dolt_workspaces;

-- Commit 详细信息（含父节点）
SELECT * FROM dolt_commits LIMIT 10;
```

**源码锚点**：

| 系统表 | 源码文件 | 主要字段 |
|--------|---------|---------|
| `dolt_status` | `system_tables/status_table.go` | table_name, status, working_set_sha, staged_sha |
| `dolt_log` | `system_tables/log_table.go` | commit_hash, committer, email, date, message |
| `dolt_diff` | `system_tables/diff_table.go` | to/from_commit_hash, table_name, num_rows_changed |
| `dolt_branches` | `system_tables/branches_table.go` | branch_name, is_current, commit_hash |
| `dolt_tags` | `system_tables/tags_table.go` | tag_name, commit_hash, tagger, date |
| `dolt_commits` | `system_tables/commits_table.go` | commit_hash, parents, committer, message |
| `dolt_workspaces` | `system_tables/workspace_table.go` | workspace_name, active, head |

> **F-163 ~ F-166**

---

## 示例 2：Schema 查询

### 2.1 查看表结构

```sql
-- 标准 DESCRIBE
DESCRIBE employees;

-- Dolt 扩展信息（含版本控制元数据）
SHOW CREATE TABLE employees;

-- Schema 变更历史
SELECT * FROM dolt_schema_migrations;
```

### 2.2 多版本 Schema 对比

```sql
-- 比较两个版本的 Schema 差异
SELECT * FROM dolt_schema_diff('main', 'feature');

-- 查看当前 Schema
SELECT * FROM dolt_schema();
```

---

## 示例 3：查询优化器统计

```sql
-- 更新统计信息（对查询规划很重要）
CALL dolt_stats_update_statistics();

-- 查看统计信息
SELECT * FROM dolt_stats;

-- 导出统计信息
CALL dolt_stats_dump_statistics();

-- 加载统计信息
CALL dolt_stats_load_statistics('/path/to/stats.json');

-- 删除统计信息
CALL dolt_stats_delete_statistics();
```

**源码锚点**：

| 过程 | 源码文件 |
|------|---------|
| `dolt_stats_update_statistics` | `dprocedures/dolt_stats_update.go` |
| `dolt_stats_dump_statistics` | `dprocedures/dolt_stats_dump.go` |
| `dolt_stats_load_statistics` | `dprocedures/dolt_stats_load.go` |
| `dolt_stats_delete_statistics` | `dprocedures/dolt_stats_delete.go` |

> **F-136**

---

## 示例 4：测试基础设施

### 4.1 单元测试

[source](https://github.com/dolthub/dolt/blob/main/.github/workflows/go.yml)

```bash
# 运行全部测试
go test ./...

# 运行指定包
go test ./go/libraries/doltcore/sqle/...

# 运行指定测试函数
go test ./go/libraries/doltcore/doltdb -run TestBranchMerge
```

### 4.2 集成测试结构

[enginetest/](https://github.com/dolthub/dolt/tree/main/go/enginetest) 目录包含约 500 个测试文件，覆盖：

| 测试类别 | 示例文件 | 覆盖场景 |
|---------|---------|---------|
| SQL 执行 | `sql_insert_test.go` | INSERT/UPDATE/DELETE |
| 分支操作 | `branch_test.go` | 创建/切换/删除分支 |
| 合并操作 | `merge_test.go` | 合并/冲突/解决 |
| 历史查询 | `history_test.go` | dolt_history_* 查询 |
| 并发测试 | `concurrent_test.go` | 多客户端并发写入 |

### 4.3 Benchmark 测试

[benchmarks/](https://github.com/dolthub/dolt/tree/main/benchmarks) 目录：

```bash
# 运行查询性能基准
go test ./benchmarks -run BenchmarkSelectQuery -bench=.

# 运行合并性能基准
go test ./benchmarks -run BenchmarkMerge -bench=.

# 运行历史查询基准
go test ./benchmarks -run BenchmarkHistoryQuery -bench=.
```

---

## 示例 5：配置管理

### 5.1 全局配置

```bash
# 设置全局用户名和邮箱
dolt config --global user.name "张三"
dolt config --global user.email "zhangsan@example.com"

# 查看配置
dolt config --list
```

**源码锚点**：

| 配置项 | 配置文件路径 |
|--------|-------------|
| 全局配置 | `~/.dolt/config.json` |
| 仓库配置 | `<repo>/.dolt/config.json` |

> **F-175 ~ F-176**

### 5.2 仓库配置

```json
{
  "user": {
    "name": "张三",
    "email": "zhangsan@example.com"
  },
  "remote": {
    "origin": {
      "url": "dolt://username/mydb"
    }
  },
  "sql_mode": "STRICT_TRANS_TABLES"
}
```

---

## 示例 6：数据导入导出

### 6.1 导出

```bash
# 导出为 SQL 文件
dolt dump --format=sql --where="department='工程'" -o employees.sql

# 导出为 CSV
dolt dump --format=csv --limit=100 -o employees.csv

# 导出为 JSON
dolt dump --format=json -o employees.json
```

**源码锚点**：[dump.go L10](https://github.com/dolthub/dolt/blob/main/go/cmd/dolt/commands/dump.go)

### 6.2 导入

```bash
# 从 SQL 文件导入
dolt sql < employees.sql

# 从 CSV 导入（自动推断 schema）
dolt import --diagnose employees.csv
```

**源码锚点**：[import.go L10](https://github.com/dolthub/dolt/blob/main/go/cmd/dolt/commands/import.go)

---

## 示例 7：GraphQL 探索

```bash
# 启动 SQL 服务器
dolt sql server &

# 访问 GraphQL 端点
curl http://localhost:3307/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```

**源码锚点**：[graphql/handler.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/graphql/handler.go)

---

*本文档为源码对照参考，因当前环境未安装 dolt，无法提供实测输出。*
