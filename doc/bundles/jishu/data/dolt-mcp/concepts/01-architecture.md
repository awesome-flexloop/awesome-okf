---
type: Concept
title: "dolt-mcp 架构分层"
description: "dolt-mcp 五层架构——Server 接口（pkg）→ ToolSet 工具集 → Tool 工具 → Dialect 方言抽象 → db 连接与事务层：工具如何注册、方言如何过滤、SQL 如何被执行与格式化返回"
tags: [dolt-mcp, architecture, golang, mcp, toolset, dialect]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-mcp-source
    resource: /references/source.md
    title: dolt-mcp 源码事实登记
---

# dolt-mcp 架构分层

> 本文剖析 dolt-mcp 的代码组织与请求执行链路。对应 [F-010~F-016、F-040~F-053](/references/source.md)。

## 五层架构总览

```mermaid
flowchart LR
    subgraph Client["MCP 客户端（AI 助手）"]
        C["Claude Desktop / CLI / 自定义"]
    end
    subgraph Server["mcp/pkg 层（server.go）"]
        I["Server 接口<br/>MCP() / DBConfig() / Dialect()"]
    end
    subgraph Toolset["mcp/pkg/toolsets 层"]
        T1["ToolSet 接口：RegisterTools(server)"]
        T2["PrimitiveToolSetV1<br/>45 项 toolRegistrations"]
    end
    subgraph Tools["mcp/pkg/tools 层（45 工具）"]
        G["query / exec / create_dolt_commit / ..."]
    end
    subgraph DBase["mcp/pkg/db 层"]
        D1["Dialect 接口"]
        D2["MySQLDialect / PostgresDialect / DoltLiteDialect"]
        D3["NewDatabaseTransaction<br/>事务 + USE + CHECKOUT"]
    end
    C -->|MCP 协议| Server
    Server -->|注入 WithToolSet| Toolset
    Toolset --> Tools
    Tools -->|持有 server.MCP()/DBConfig()/Dialect()| DBase
    DBase -->|"MySQL 线协议 / PG 线协议 / 内嵌"| DB[("Dolt / DoltgreSQL / DoltLite")]
```

对应源码目录：`mcp/pkg/server.go`、`mcp/pkg/toolsets/`、`mcp/pkg/tools/`、`mcp/pkg/db/`（F-011~F-014、F-042）。

## 第 1 层：Server 接口与传输

`pkg.Server` 是所有 server 实现的公共门面，暴露三个能力（F-011）：

- `MCP() *server.MCPServer`：底层 MCP server，工具注册与调用入口；
- `DBConfig() db.Config`：数据库连接配置；
- `Dialect() db.Dialect`：当前方言实现。

dolt-mcp 提供两种传输实现：`stdioServerImpl`（stdio 模式，F-085）与 `httpServerImpl`（HTTP 模式，F-080~F-082）。二者构造时都调用 `server.NewMCPServer(DoltMCPServerName, DoltMCPServerVersion, WithToolCapabilities(true), WithLogging())`（F-010）——MCP 工具能力列表（`tools/list`）由此启用，客户端可先列出全部工具再调用。

## 第 2 层：ToolSet 工具集抽象

工具以"工具集"为单位批量注入 server（F-012）：

```go
type ToolSet interface {
    RegisterTools(server pkg.Server)
}
```

`WithToolSet(ts)` 是一个 `pkg.Option`——在 main 中通过 `toolsets.WithToolSet(&toolsets.PrimitiveToolSetV1{})` 传入（F-012）。这种 Option 模式让 server 构造与工具装配解耦，未来可注入第二套工具集。

## 第 3 层：PrimitiveToolSetV1 与 45 项注册

`PrimitiveToolSetV1` 内部维护静态注册表 `toolRegistrations`（F-013），每个条目是 `{工具名, 注册函数}` 对。注册时执行**方言过滤**（F-014）：

```go
func (v *PrimitiveToolSetV1) RegisterTools(server pkg.Server) {
    dialect := server.Dialect()
    for _, t := range toolRegistrations {
        if dialect.SupportsTool(t.name) {
            t.register(server)
        }
    }
}
```

这意味着：**同一份注册表，在不同方言下暴露的工具数不同**。DoltLite 隐藏 6 个（F-069）、Postgres 隐藏 5 个（F-065），见 [方言设计](05-dialect-design.md)。

## 第 4 层：单个工具的实现模式

每个工具文件遵循高度一致的模板（以 `query` 为例，F-113）：

```go
func NewQueryTool() mcp.Tool {
    return mcp.NewTool(
        QueryToolName,                          // "query"
        mcp.WithDescription("Executes a READ query."),
        mcp.WithReadOnlyHintAnnotation(true),   // ← 安全注解
        mcp.WithDestructiveHintAnnotation(false),
        mcp.WithIdempotentHintAnnotation(true),
        mcp.WithOpenWorldHintAnnotation(false),
        mcp.WithString("working_branch", mcp.Required(), ...),
        mcp.WithString("working_database", mcp.Required(), ...),
        mcp.WithString("query", mcp.Required(), ...),
    )
}

func RegisterQueryTool(server pkg.Server) {
    tool := NewQueryTool()
    server.MCP().AddTool(tool, func(ctx, request) (*mcp.CallToolResult, error) {
        // 1. 提取并校验参数（GetRequiredStringArgumentFromCallToolRequest）
        // 2. 方言 SQL 校验（ValidateReadQuery）
        // 3. 建事务（UsingDatabaseOnBranch：USE + CHECKOUT）
        // 4. 执行（QueryContext，Markdown 格式化）
        // 5. 事务处理（Rollback 或 Commit）
    })
}
```

### 安全注解四元组

每个工具都声明四枚 hint 注解（F-100），把风险元数据交给 MCP 客户端，供其在调用前判断：

| 注解 | 含义 | 例 |
|------|------|-----|
| `ReadOnly` | 是否只读 | query(1) vs exec(0) |
| `Destructive` | 是否有破坏性 | drop_database(1) vs create_database(0) |
| `Idempotent` | 是否幂等 | create_database(1) vs create_table(0) |
| `OpenWorld` | 是否访问外部世界 | clone_database/dolt_push/fetch/pull(1) |

四元组差异构成 [工具全景](03-tools-overview.md) 的安全分类骨架。

## 第 5 层：db 层（连接、事务、方言、结果格式化）

### 事务生命周期：三步上下文装配

绝大多数工具先经 `NewDatabaseTransactionUsingDatabaseOnBranch`（F-052）开启事务并装配上下文——等价于开连接 + `USE <db>` + `CALL DOLT_CHECKOUT('<branch>')`（F-051/F-052）：

| 辅助函数 | 动作 | 使用场景 |
|---------|------|---------|
| `NewDatabaseTransaction` | 开事务（BEGIN） | 库级工具（list_databases 等） |
| `NewDatabaseTransactionUsingDatabase` | + USE db | list_dolt_branches、remote 工具等 |
| `NewDatabaseTransactionUsingDatabaseOnBranch` | + USE db + CHECKOUT branch | 表级/版本控制工具 |

**只读与写入的生命周期刻意分离**（F-050）：只读工具 `defer tx.Rollback(ctx)` 结束即丢弃；写工具走 `CommitTransactionOrRollbackOnError`（无错 COMMIT，有错 ROLLBACK）。query 工具即便成功也回滚，保证读通道零副作用（F-113）。

### 结果格式化

查询结果默认以 Markdown 表格返回（`rowMapToMarkdown`，F-045），也内置 CSV 格式化器（`rowMapToCSV`，F-046）。工具通过 `db.ResultFormatMarkdown/CSV` 选择；`[]byte` 类型的单元格统一转 string 便于 AI 阅读（F-046）。

### SQL 安全校验链

工具提交 SQL 前先过方言 `Validate*Query`（F-042）：MySQL 用 Vitess 解析器判读（F-062）、Postgres 用 pg_query 判读（F-068）、DoltLite 用自研 scanner 判读（F-072/F-073）。拦截失败的语句在到达数据库前即被拒绝，见 [SQL 安全机制](04-sql-safety.md)。

## 一条请求的完整生命周期

以"在 main 分支的 testdb 库查 people 表"为例：

1. AI 客户端向 MCP server 发送 `tools/call`，参数 `{query: "SELECT * FROM people", working_branch: "main", working_database: "testdb"}`（F-113）。
2. `query` handler 提取参数；缺失/空串报 `"query not defined"`（InvalidArgument）。
3. `dialect.ValidateReadQuery("SELECT * FROM people")`——Dolt 后端走 MySQL 方言，Vitess 解析确认是只读语句（F-062）。
4. `NewDatabaseTransactionUsingDatabaseOnBranch`：开连接→`USE testdb;`→`CALL DOLT_CHECKOUT('main');`（F-052）。
5. `tx.QueryContext(..., Markdown)` 执行并格式化为 Markdown 表（F-045）。
6. `defer tx.Rollback(ctx)` 收尾（F-050），把 Markdown 文本作为工具结果返回给 AI。

## 相关概念

* [工具全景](/concepts/03-tools-overview.md)
* [SQL 安全机制](/concepts/04-sql-safety.md)
* [方言设计](/concepts/05-dialect-design.md)
