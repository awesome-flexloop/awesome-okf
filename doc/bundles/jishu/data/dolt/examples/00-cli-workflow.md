# 示例：Dolt CLI 核心工作流

> 本文档提供 Dolt CLI 核心命令的源码对照参考。
> **注意**：当前环境未安装 `dolt`（`dolt NOT on PATH`），本文档以源码文件锚点形式呈现，供查阅实现细节。
> 对应 F-086~F-111。

---

## 示例 1：初始化仓库

### 命令行

```bash
dolt init
```

### 源码锚点

| 步骤 | 源码位置 | 说明 |
|------|---------|------|
| 命令注册 | [doc.go L1](https://github.com/dolthub/dolt/blob/main/go/cmd/dolt/commands/doc.go) | `init` 在 `commandsWithoutCliCtx` 白名单中 |
| 实现文件 | `go/cmd/dolt/commands/init.go` | `Init` struct + `Exec()` |
| 环境加载 | [environment.go L150](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/env/environment.go) | `LoadWithoutDB()` 先加载配置 |
| 仓库创建 | `go/libraries/doltcore/env/fs.go` | 创建 `.dolt/` 目录及 `config.json` |
| 格式版本 | [environment.go L30](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/env/environment.go) | `DoltEnv.Version` 字段写入 |

### 产出物

执行后在当前目录生成 `.dolt/` 目录：

```
.dolt/
├── config.json        # 用户配置（name/email）
├── remotes.db         # 远程仓库列表
└── ...
```

---

## 示例 2：SQL 交互与建表

### 命令行

```bash
# 启动 SQL 服务器
dolt sql server

# 另一终端连接
mysql --host=127.0.0.1 --port=3306 -u root

# 建表
CREATE TABLE employees (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    salary DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO employees (id, name, department, salary)
VALUES ('a1b2', '张三', '工程', 15000.00);
```

### 源码锚点

| 步骤 | 源码位置 | 说明 |
|------|---------|------|
| SQL 服务器 | [sql_server.go L20](https://github.com/dolthub/dolt/blob/main/go/cmd/dolt/commands/sql_server.go) | Vitess 协议栈，默认端口 3306 |
| SQL CLI | [sql_cli.go L10](https://github.com/dolthub/dolt/blob/main/go/cmd/dolt/commands/sql_cli.go) | 交互式 readline shell |
| Schema 定义 | `go/libraries/doltcore/sqle/schema/` | Table/Column/PrimaryKey 结构体 |
| 索引类型 | [schema/index.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/schema/index.go) | PRIMARY/UNIQUE/FULLTEXT/SPATIAL |

---

## 示例 3：分支与提交

### 命令行

```bash
# 创建并切换到新分支
dolt branch feature/payroll
dolt checkout feature/payroll

# 修改数据
UPDATE employees SET salary = 16000 WHERE name = '张三';

# 暂存变更
dolt add employees

# 提交
dolt commit -m "更新张三薪资"

# 切换回 main 查看历史
dolt checkout main
dolt log --oneline
```

### 源码锚点

| 步骤 | 源码锚点 | 关键实现 |
|------|---------|---------|
| 分支创建 | `go/cmd/dolt/commands/branch.go` | 调用 `doltdb.Branch()` |
| 引用解析 | [ref.go L50](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/ref/ref.go) | `Parse()` 路由到 BranchRef |
| Checkout | `go/cmd/dolt/commands/checkout.go` | 调用 `SessionDatabase.SwitchWorkingSet()` |
| 提交 | `go/cmd/dolt/commands/commit.go` | 调用 `dprocedures/dolt_commit.go` |
| 日志 | `go/cmd/dolt/commands/log.go` | 查询 `dolt_log` 系统表 |

### 涉及的核心 API（`doltdb.DoltDB`）

```
ResolveCommitRef("heads/feature/payroll")  → *Commit   （:634）
ResolveWorkingSet("heads/feature/payroll") → *WorkingSet  （:760）
DoltDB.Branch("feature/payroll")           → error
DoltDB.CheckoutBranch("feature/payroll")   → error
```

> **F-132**

---

## 示例 4：合并与冲突处理

### 命令行

```bash
# 在 main 上合并 feature 分支
dolt merge feature/payroll

# 查看合并状态
dolt status

# 若有冲突，查看冲突详情
SELECT * FROM dolt_diff('--conflicted');

# 解决冲突后提交
dolt add <resolved_table>
dolt commit -m "解决薪资合并冲突"
```

### 源码锚点

| 步骤 | 源码锚点 | 说明 |
|------|---------|------|
| 合并执行 | `go/cmd/dolt/commands/merge.go` | 调用 `Merge.StartMerge()` |
| 冲突检测 | [merge/conflict.go L20](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/merge/conflict.go) | 行级 hash 对比 |
| 冲突类型 | [merge/conflict_types.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/merge/conflict_types.go) | InsertInsert/DeleteDelete/UpdateUpdate |
| 合并完成 | `merge/merge.go` | `FinishMerge()` |
| 状态查询 | [system_tables/status_table.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/system_tables/status_table.go) | `dolt_status` 系统表 |

> **F-154 ~ F-156**

---

## 示例 5：查看历史与差异

### 命令行

```bash
# 查看 commit 历史
dolt log --oneline --all

# 查看某表的完整历史
SELECT * FROM dolt_history_employees;

# 比较两个版本的差异
dolt diff main feature/payroll --employees

# 使用表函数获取 diff
SELECT * FROM dolt_diff('main', 'feature/payroll');
```

### 源码锚点

| 查询 | 源码锚点 | 说明 |
|------|---------|------|
| `dolt log` | [system_tables/log_table.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/system_tables/log_table.go) | 遍历 CommitItrForRoots |
| `dolt_history_*` | [history_table.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/history_table.go) | 每 commit 一个 partition |
| `dolt_diff` 表函数 | `sqle/dtablefunctions/diff.go` | 返回差异行集 |
| `dolt_diff` 系统表 | [system_tables/diff_table.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/system_tables/diff_table.go) | from/to commit + 差异统计 |

> **F-141、F-163~F-165**

---

## 示例 6：远程操作

### 命令行

```bash
# 添加远程
dolt remote add origin dolt://username/mydb

# 推送分支
dolt push origin main

# 拉取更新
dolt pull origin main

# 克隆仓库
dolt clone dolt://username/mydb
```

### 源码锚点

| 步骤 | 源码锚点 | 说明 |
|------|---------|------|
| Remote 接口 | [remotesql/remote.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/remotesql/remote.go) | Clone/Fetch/Push/Pull |
| DoltHub URL | [remotesql/dolthub.go L10](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/remotesql/dolthub.go) | `dolt://` 协议解析 |
| 凭据管理 | `go/libraries/doltcore/creds/oauth.go` | OAuth2 PKCE |
| 登录命令 | `go/cmd/dolt/commands/credentials_login.go` | 触发浏览器 OAuth 流程 |

> **F-157 ~ F-158、F-177 ~ F-178**

---

## 示例 7：MCP 工具调用（源码视角）

### 概念映射

以下展示了 MCP 工具与底层 Dolt 源码的对应关系：

| MCP 工具 | 底层 SQL 调用 | 源码实现 |
|----------|-------------|---------|
| `create_dolt_commit` | `CALL DOLT_COMMIT('-m', 'msg')` | `dprocedures/dolt_commit.go` |
| `list_dolt_diff_changes_in_working_set` | `SELECT * FROM dolt_diff WHERE commit_hash='WORKING'` | `dtablefunctions/diff.go` |
| `list_dolt_commits` | `SELECT * FROM dolt_log` | `system_tables/log_table.go` |
| `merge_dolt_branch` | `CALL DOLT_MERGE('branch')` | `dprocedures/dolt_merge.go` |
| `select_active_branch` | `SELECT ACTIVE_BRANCH()` | `dfunctions/active_branch.go` |

> **F-135 ~ F-138**

---

*本文档为源码对照参考，因当前环境未安装 dolt，无法提供实测输出。所有源码链接指向本地克隆路径 `external/dao/action/DoltHub/dolt`。*
