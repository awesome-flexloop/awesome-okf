---
type: concept
title: MCP 集成（MCP Integration）
description: CodeWhale 通过 McpManager 与 McpManagedClient trait 管理本地 stdio 或远程 HTTP 的 MCP 服务器并暴露其工具
tags: [codewhale, mcp, stdio, http]
sources:
  - resource: "/references/tools-mcp-api.md"
    title: "Tools 与 MCP API 参考"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# MCP 集成

CodeWhale 通过 MCP（Model Context Protocol）加载外部工具。MCP 服务器既可以是 TUI 启动的本地 stdio 进程，也可以是「Streamable HTTP + legacy SSE fallback」的远程 URL 服务器（见 [F-089]）。

## 配置模型

`McpServerConfig`（见 [F-067]）描述单个服务器进程：`name`、`command`、`args`、`env`、`enabled`。`ToolFilter`（见 [F-068]）控制暴露哪些工具——`allow` 为空表示全部放行，`deny` 优先于 `allow`。二者合起来构成 `McpServerDefinition`（见 [F-069]）。

## 管理器与传输抽象

`McpManager` 只持有两个 HashMap：`configs`（name → 配置+过滤器）与 `clients`（name → 客户端）（见 [F-071]）。真正的通信由 `McpManagedClient` trait 抽象（见 [F-070]），四个方法：

```text
list_tools() -> Vec<McpToolDescriptor>
call_tool(name, arguments) -> Value
list_resources() -> Vec<McpResourceDescriptor>
read_resource(uri) -> Value
```

每个服务器都是 `Box<dyn McpManagedClient>`，stdlib 进程由 `ChildProcessMcpClient` 承载（见 [F-066]）。`register_server` 在 `sanitize_component` 折叠后做名称去重：`my-server`、`my_server`、`My.Server` 都会产生 `mcp__my_server__*` 限定名，冲突注册直接 `bail!`（见 [F-071] 上下文）。

## 无头 stdio 服务器

`run_stdio_server(initial_definitions) -> Result<Vec<McpServerDefinition>>`（见 [F-072]）从 stdin 逐行读取 JSON-RPC 请求、构建 stdio 状态并返回最终定义。它与 CLI 入口 `codewhale mcp-server` 对应，且 `codewhale-tui serve --mcp` 运行同一服务器（见 [F-090]）。

## 日常管理命令

```bash
codewhale-tui mcp init                  # 生成 starter mcp.json
codewhale-tui mcp list                  # 列出服务器
codewhale-tui mcp tools [server]        # 列出某服务器的工具
codewhale-tui mcp add <name> --command "<cmd>" --arg "<arg>"
codewhale-tui mcp add <name> --url "http://localhost:3000/mcp"
codewhale-tui mcp login/logout/enable/disable <name>
```

（命令清单见 [F-090]）

## 相关概念

- [工具系统](/concepts/02-tools-system.md)
- [Workflow 与 Fleet](/concepts/04-workflow-fleet.md)
- [Tools 与 MCP API](/references/tools-mcp-api.md)