---
type: Example
title: "query 与 exec：读/写双通道调用实操"
description: "用 MCP 工具调用 JSON 演示 query（只读 SELECT）与 exec（写入 INSERT/CREATE）的真实用法——参数结构、方言差异示例、错误场景与结果形态，取材自官方集成测试"
tags: [dolt-mcp, examples, query, exec, mcp, call-tool]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-mcp-source
    resource: /references/source.md
    title: dolt-mcp 源码事实登记
---

# query 与 exec：读/写双通道调用实操

> 本文基于源码工具注册与官方集成测试（[F-113、F-114、F-150~F-156](/references/source.md)）演示 `query`/`exec` 的标准调用方式。测试基建以 people 表为样例（seed：tim/brian/aaron 三行，F-154）。

## 前置：理解三个必填参数

`query` 与 `exec` 都要三个必填参数（F-113/F-114）：

| 参数 | 含义 |
|------|------|
| `query` | 要执行的 SQL 语句 |
| `working_database` | 调用前切换到哪个数据库 |
| `working_branch` | 调用前检出哪个分支 |

server 收到后自动执行 `USE <db>` + `DOLT_CHECKOUT(<branch>)`，所以 AI 不必自己发切换语句（F-052）。

## 示例 1：query 只读查询（SELECT）

测试库 branch 已检出，对 `people` 表查询：

```json
{
  "name": "query",
  "arguments": {
    "query": "SELECT * FROM `people`;",
    "working_branch": "feature-users",
    "working_database": "test"
  }
}
```

- Dolt 后端 SQL 用反引号标识符（F-060）；DoltgreSQL/DoltLite 用双引号（F-064/F-069）。
- 返回结果为 Markdown 表格文本，行内容包含 seed 的 tim/brian/aaron（F-154/F-155）。
- 该调用在事务内执行后 **Rollback**——不会产生任何写副作用（F-050/F-113）。

方言差异参考（源码 `testQueryToolQuery` 常量）：

| 后端 | query 参数 |
|------|-----------|
| Dolt | `SELECT * FROM \`people\`;` |
| DoltgreSQL / DoltLite | `SELECT * FROM "people";` |

## 示例 2：exec 写入（INSERT）

```json
{
  "name": "exec",
  "arguments": {
    "query": "INSERT INTO `people` (id, first_name, last_name) VALUES (UUID(), 'alice', 'chen');",
    "working_branch": "feature-users",
    "working_database": "test"
  }
}
```

- `exec` 注解 destructive=true，AI 客户端可视之为写操作（F-114）。
- 成功后返回文案 `successfully executed write`（F-114）。
- 写入在独立事务中 **COMMIT**——只有 exec（及建表/改表等写工具）才落库（F-050/F-114）。

## 示例 3：错误场景（对照集成测试用例）

源码集成测试 `testQueryToolInvalidArguments` 覆盖如下 query 错误（F-155）：

| 场景 | 结果 |
|------|------|
| 缺 `working_branch` | 工具错误：`working_branch not defined` |
| `working_branch` 空串 | 同上 |
| `working_branch` 不存在（`doesnotexist`） | 工具错误（checkout 失败） |
| 缺/空 `working_database` | `working_database not defined` |
| `working_database` 不存在 | 工具错误 |
| 缺/空 `query` | `query not defined` |
| `query` 不是合法 SQL（`this is not sql`） | 工具错误（方言解析失败） |

> DoltLite 特例：它没有"多个数据库"概念，`working_database=doesnotexist` 用例会被跳过（F-094/F-156）。

向 `query` 传写语句（如 DELETE）会被方言 `ValidateReadQuery` 拦截返回 `invalid read query`——这是 [SQL 安全机制](../concepts/04-sql-safety.md) 的第一道防线（F-113）。

## 通用调用模板（任意 MCP 客户端）

```
步骤 1：tools/list → 拿到全部工具及其参数 schema（F-010 工具能力开启）
步骤 2：tools/call
        {
          "name": "<工具名>",
          "arguments": {
            ...按工具参数表填...
          }
        }
步骤 3：读 text 类型 content 结果
```

dolt-mcp 依赖 mcp-go 的 TextContent 返回，`CallToolResult.IsError=true` 表示工具内部错误（F-155 的 resultToString 印证）。

## 相关概念

* [工具全景](/concepts/03-tools-overview.md)
* [SQL 安全机制](/concepts/04-sql-safety.md)
* [架构分层](/concepts/01-architecture.md)
* 下一个实操见 [examples/01-branch-commit-merge-workflow.md](01-branch-commit-merge-workflow.md)
