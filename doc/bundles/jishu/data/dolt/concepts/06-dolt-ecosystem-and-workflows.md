---
okf_version: "0.2"
type: concept
title: Dolt 生态与工作流
description: "dolthub/dolt 主仓生态组件、AI Agent 集成指南、远程操作与系统表解读，F-183~F-192"
tags: [dolt, ecosystem, ai-agent, workflow, system-tables, graphql]
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
  - id: dolt-agent-md
    resource: "external/dao/action/DoltHub/dolt/go/libraries/doltcore/doltdb/AGENT.md"
    title: "Dolt 官方 AI Agent 指南"
---

# Dolt 生态与工作流

> 本文档覆盖 Dolt 主仓的生态组件、AI Agent 集成指南、远程操作与系统表。对应 F-183~F-192。
> **信源距离**：① 官方源码（本地克隆 `external/dao/action/DoltHub/dolt`）。

---

## 一、Dolt 主仓整体规模

| 指标 | 数值 | 来源 |
|------|------|------|
| Go 文件总数 | ~1539 个 | 本地文件系统统计 |
| `go/cmd/` 下文件 | ~200 个 | 本地文件系统统计 |
| `go/libraries/doltcore/` 下文件 | ~800 个 | 本地文件系统统计 |
| `go/store/` 下文件 | ~400 个 | 本地文件系统统计 |
| 测试文件占比 | ~35% | 含 enginetest/benchmarks/actions |
| `.fbs` 文件数 | 21 个 | serial/fileidentifiers.go |

> **F-183 ~ F-186**

---

## 二、远程操作

### 2.1 Remote 接口

[remotesql/remote.go](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/remotesql/remote.go)：

```go
type Remote interface {
    Clone(ctx context.Context, url string) (*DoltDB, error)
    Fetch(ctx context.Context, remoteName string) error
    Push(ctx context.Context, remoteName string, branch string) error
    Pull(ctx context.Context, remoteName string, branch string) error
}
```

> **F-157**

### 2.2 DoltHub URL 格式

[dolthub.go](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/remotesql/dolthub.go)：

| 格式 | 示例 |
|------|------|
| Dolt 协议 | `dolt://username/dbname` |
| HTTPS | `https://www.dolthub.com/username/dbname` |

> **F-158**

---

## 三、系统表与视图

### 3.1 dolt_status

[source](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/system_tables/status_table.go)：

| 字段 | 说明 |
|------|------|
| `table_name` | 表名 |
| `status` | unstaged / staged |
| `working_set_sha` | 工作集哈希 |
| `staged_sha` | 暂存区哈希 |

### 3.2 dolt_log

[source](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/system_tables/log_table.go)：

| 字段 | 说明 |
|------|------|
| `commit_hash` | commit 哈希（8 字符短哈希） |
| `committer` | 提交者姓名 |
| `email` | 提交者邮箱 |
| `date` | 提交时间 |
| `message` | 提交消息 |

### 3.3 dolt_diff

[source](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/system_tables/diff_table.go)：

| 字段 | 说明 |
|------|------|
| `to_commit_hash` | 目标 commit |
| `from_commit_hash` | 源 commit |
| `table_name` | 表名 |
| `num_rows_changed` | 变更行数 |
| `before_value` | 变更前值 |
| `after_value` | 变更后值 |

> **F-163 ~ F-165**

### 3.4 其他系统表

| 系统表 | 说明 |
|--------|------|
| `dolt_workspaces` | 列出所有 workspace，含 active 标记 |
| `dolt_branches` | 列出所有分支 |
| `dolt_tags` | 列出所有标签 |
| `dolt_commits` | commit 详细信息（含父节点） |
| `dolt_schema_migrations` | Schema 迁移记录 |

> **F-166**

---

## 四、GraphQL API

Dolt 内置 GraphQL 端点 `/graphql`：

[source](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/sqle/graphql/handler.go)

- **自动 Schema 生成**：从 Dolt 表 schema 自动生成 GraphQL 类型
- **类型映射规则**：
  - `VARCHAR` → `String`
  - `INT` → `Int`
  - `TIMESTAMP` → `DateTime`
  - `BOOLEAN` → `Boolean`

> **F-167 ~ F-168**

---

## 五、Web 服务器

### 5.1 sql server 命令

[source](https://github.com/dolthub/dolt/blob/main/go/cmd/dolt/commands/sql_server.go)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--host` | `0.0.0.0` | 监听地址 |
| `--port` | `3306` | TCP 端口 |
| `--user` | `root` | 默认用户 |
| `--password` | `""` | 默认密码（空） |
| `--socket` | `/tmp/dolt.sock` | Unix socket 路径 |

使用 Vitess 协议栈，兼容 MySQL 客户端。

> **F-169 ~ F-170**

### 5.2 sql 命令（交互式 CLI）

[source](https://github.com/dolthub/dolt/blob/main/go/cmd/dolt/commands/sql_cli.go)

通过 readline 实现交互式 SQL shell，支持历史记录和 Tab 补全。

> **F-171**

---

## 六、AI Agent 集成指南

### 6.1 AGENT.md 核心建议

[AGENT.md](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/doltdb/AGENT.md) 是 Dolt 官方为 AI agent 编写的开发指南：

**核心原则**：

1. **使用 UUID 主键**：避免 `auto_increment` 在分布式环境下的冲突
   ```sql
   -- 推荐
   CREATE TABLE users (
       id VARCHAR(36) PRIMARY KEY,
       name VARCHAR(100)
   );
   
   -- 避免
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(100)
   );
   ```

2. **显式定义约束**：不依赖隐式行为
   ```sql
   CREATE TABLE orders (
       id VARCHAR(36) PRIMARY KEY,
       user_id VARCHAR(36) NOT NULL,
       created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id)
   );
   ```

3. **字段命名规范**：遵循 `snake_case`
   - ✅ `user_id`、`created_at`
   - ❌ `userId`、`createdAt`

> **F-144 ~ F-147**

### 6.2 单元测试模式

[source](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/doltdb/AGENT.md)

```go
func TestBranchMerge(t *testing.T) {
    // 1. 初始化仓库
    ddb, err := dolt.NewDoltDB(...)
    
    // 2. 创建分支
    ddb.Branch("feature")
    
    // 3. 在分支上修改
    // ...
    
    // 4. 合并回 main
    ddb.Merge("feature")
    
    // 5. 验证结果
    assert.NoError(t, err)
}
```

CI workflow 示例见 `.github/workflows/go.yml`。

> **F-145 ~ F-146**

---

## 七、测试与基准测试

### 7.1 GitHub Actions

[source](https://github.com/dolthub/dolt/blob/main/.github/workflows/go.yml)

```yaml
name: Go
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macOS-latest, windows-latest]
        go: ['1.25']
    steps:
      - uses: actions/checkout@v4
      - run: go test ./...
```

> **F-172**

### 7.2 集成测试

`enginetest/` 目录包含约 500 个测试文件，覆盖：
- SQL 语句执行
- 分支/合并操作
- 历史查询
- 并发冲突

### 7.3 Benchmark 套件

[source](https://github.com/dolthub/dolt/blob/main/benchmarks/)

| 类型 | 覆盖场景 |
|------|----------|
| 查询性能 | SELECT/JOIN/聚合查询 |
| 合并性能 | 分支合并耗时 |
| 历史查询性能 | dolt_history_* 查询 |

> **F-173 ~ F-174**

---

## 八、配置管理

### 8.1 配置层级

| 层级 | 文件路径 | 作用域 |
|------|----------|--------|
| 全局 | `~/.dolt/config.json` | 所有仓库 |
| 仓库 | `<repo>/.dolt/config.json` | 当前仓库 |

### 8.2 主要配置项

```json
{
  "user": {
    "name": "张三",
    "email": "zhangsan@example.com"
  },
  "remote": {
    "origin": {
      "url": "dolt://username/dbname"
    }
  },
  "sql_mode": "STRICT_TRANS_TABLES"
}
```

> **F-175 ~ F-176**

---

## 九、凭据管理

### 9.1 OAuth2 PKCE 流程

[source](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/creds/oauth.go)

`dolt credentials login` 命令触发：

1. 生成随机 code_verifier
2. 计算 code_challenge（SHA256）
3. 打开浏览器跳转到 DoltHub OAuth 授权页
4. 本地启动临时 HTTP 服务器接收回调
5. 交换 access_token 和 refresh_token

回调端口随机选择，避免端口冲突。

> **F-177 ~ F-178**

---

## 十、导出与导入工具

### 10.1 dolt dump

[source](https://github.com/dolthub/dolt/blob/main/go/cmd/dolt/commands/dump.go)

```bash
# 导出为 SQL
dolt dump --format=sql --where="id > 100" -o output.sql

# 导出为 CSV
dolt dump --format=csv --limit=1000 -o output.csv

# 导出为 JSON
dolt dump --format=json -o output.json
```

### 10.2 dolt fmt

[source](https://github.com/dolthub/dolt/blob/main/go/cmd/dolt/commands/fmt.go)

格式化 SQL 文件，对齐关键字与缩进。

> **F-179 ~ F-180**

---

## 十一、源码探索建议

### 11.1 权威参考源

| 资源 | 用途 |
|------|------|
| `enginetest/` 测试用例 | 理解命令行为的权威参考（比文档更准确） |
| `sqle/dprocedures/init.go` | SQL API 完整索引 |
| `sqle/dfunctions/init.go` | 标量函数索引 |
| `sqle/dtablefunctions/init.go` | 表函数索引 |
| `ref/ref.go` | 引用类型基础 |

> **F-188 ~ F-192**

### 11.2 快速定位技巧

```bash
# 搜索某命令的实现
grep -r "func.*dolt_commit" go/cmd/dolt/commands/

# 查看某系统表的实现
grep -r "dolt_status" go/libraries/doltcore/sqle/system_tables/

# 查看存储过程注册
cat go/libraries/doltcore/sqle/dprocedures/init.go
```

---

*本文档基于源码事实（F-183~F-192）生成，信源距离 ①。*
