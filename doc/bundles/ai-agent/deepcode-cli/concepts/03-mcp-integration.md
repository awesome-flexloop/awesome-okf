---
type: Concept
title: MCP 集成
description: deepcode-cli 内置 MCP 客户端管理器，通过 stdio JSON-RPC 连接外部工具服务器，工具以 mcp__server__tool 命名空间暴露，支持工具、提示和资源三类能力。
tags: [deepcode-cli, mcp, model-context-protocol, 工具集成, json-rpc]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: deepcode-cli 源码信源
---

# MCP 集成

## 概述

deepcode-cli 内置 MCP（Model Context Protocol）客户端，可连接外部 MCP 服务器（如 GitHub、Playwright、文件系统等），将外部工具暴露给 LLM 使用。MCP 相关代码位于 `packages/core/src/mcp/` 目录，包含两个核心类：

- `McpClient`（`mcp-client.ts`）：管理与单个 MCP 服务器的 stdio JSON-RPC 通信
- `McpManager`（`mcp-manager.ts`）：管理多个 MCP 服务器连接、工具注册和状态追踪

## MCP 服务器配置

MCP 服务器在 `settings.json` 的 `mcpServers` 字段中配置。配置类型定义于 `packages/core/src/settings.ts:20-24`：

```typescript
export type McpServerConfig = {
  command: string;
  args?: string[];
  env?: Record<string, string>;
};
```

### 配置示例

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    }
  }
}
```

### 配置字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | string | 是 | 可执行文件路径或命令（npx、node、python 等） |
| `args` | string[] | 否 | 传递给命令的参数列表 |
| `env` | object | 否 | 传递给服务器进程的环境变量 |

当命令为 `npx` 时，`McpClient` 会自动添加 `-y` 参数（`mcp-client.ts:393-405`）。

## 设置合并

MCP 服务器配置通过 `mergeMcpServers` 函数（`settings.ts:471-519`）合并用户级和项目级配置：

1. 收集用户设置和项目设置中的所有服务器名称
2. 项目级配置的 `command` 和 `args` 优先于用户级
3. 环境变量按以下优先级叠加：用户 env → 用户配置 env → 用户 MCP_ env → 项目 env → 项目配置 env → 项目 MCP_ env → 系统 env → 系统 MCP_ env
4. 以 `MCP_` 为前缀的环境变量会被提取并合并到服务器进程环境中

## 工具命名空间

### 命名格式

MCP 工具通过 `mcp__<serverName>__<toolName>` 格式命名空间化（`mcp-manager.ts:33-57`）：

```typescript
function buildMcpNamespacedName(
  serverName: string,
  toolName: string,
  usedNames: ReadonlySet<string> = new Set()
): string {
  const rawName = buildRawMcpNamespacedName(serverName, toolName);
  const sanitizedName = `mcp__${sanitizeApiToolNamePart(serverName)}__${sanitizeApiToolNamePart(toolName)}`;
  let candidate = fitApiToolName(sanitizedName, rawName);
  // ... 哈希消歧逻辑
}
```

原始名称格式为 `mcp__<server>__<tool>`（`mcp-manager.ts:500-502`）：

```typescript
function buildRawMcpNamespacedName(serverName: string, toolName: string): string {
  return `mcp__${serverName}__${toolName}`;
}
```

### 名称约束

- 最大长度：64 字符（`API_TOOL_NAME_MAX_LENGTH = 64`，`mcp-manager.ts:10`）
- 允许字符：`[a-zA-Z0-9_-]`（`API_TOOL_NAME_PATTERN`，`mcp-manager.ts:9`）
- 非法字符替换为下划线（`sanitizeApiToolNamePart`，`mcp-manager.ts:504-507`）

### 哈希消歧

当名称超长或包含非法字符时：

1. 截断名称并附加 SHA-256 哈希前 8 位（`mcp-manager.ts:522-523`）
2. 若仍冲突，追加递增序号 `_2`、`_3`...
3. 当名称被修改时，工具描述会附加 `MCP source: <server>: <originalName>` 行（`mcp-manager.ts:487-497`）

### 命名示例

| 服务器 | 工具 | 完整名称 |
|--------|------|---------|
| github | search_code | `mcp__github__search_code` |
| github | create_pull_request | `mcp__github__create_pull_request` |
| playwright | browser_navigate | `mcp__playwright__browser_navigate` |

## MCP 客户端通信

### 进程启动

`McpClient` 通过 `child_process.spawn` 启动 MCP 服务器进程（`mcp-client.ts:141-146`）：

```typescript
this.process = spawn(spawnSpec.command, spawnSpec.args, {
  stdio: ["pipe", "pipe", "pipe"],
  env: childEnv,
  shell: spawnSpec.shell,
  windowsHide: spawnSpec.windowsHide,
});
```

Windows 平台使用 `shell: true` 并将命令与参数合并为单字符串（`mcp-client.ts:425-437`），以解决 `.cmd` 文件解析问题。

### JSON-RPC 2.0 协议

通信基于 JSON-RPC 2.0，通过 stdin/stdout 逐行传输。支持三种消息类型：

- **Request**：包含 `id`、`method`、`params`，需要响应
- **Response**：包含 `id`、`result` 或 `error`
- **Notification**：无 `id`，不需要响应（如 `notifications/tools/list_changed`）

支持 JSON-RPC 批量消息（数组格式），符合 MCP 2025-03-26 规范要求（`mcp-client.ts:346-354`）。

### 协议握手

连接时发送 `initialize` 请求（`mcp-client.ts:191-198`）：

```typescript
this.sendRequest("initialize", {
  protocolVersion: "2025-03-26",
  capabilities: {},
  clientInfo: { name: "deepcode-cli", version: "0.1.0" },
}, timeoutMs)
```

支持的协议版本为 `"2025-03-26"` 和 `"2024-11-05"`（`mcp-client.ts:204`）。握手成功后发送 `notifications/initialized` 通知。

### 支持的 MCP 方法

| 方法 | 功能 | 分页限制 |
|------|------|---------|
| `tools/list` | 获取工具列表 | 最多 100 页 |
| `tools/call` | 调用工具 | 超时 60 秒 |
| `prompts/list` | 获取提示列表 | 最多 100 页 |
| `prompts/get` | 获取提示内容 | 超时 30 秒 |
| `resources/list` | 获取资源列表 | 最多 100 页 |
| `resources/read` | 读取资源内容 | 超时 30 秒 |

### 超时配置

- 启动超时：30000ms（可通过 `DEEPCODE_MCP_TIMEOUT` 环境变量覆盖，`mcp-manager.ts:5-7`）
- 工具调用超时：60000ms（`MCP_CALL_TOOL_TIMEOUT_MS`，`mcp-manager.ts:8`）

### 动态工具更新

当服务器发送 `notifications/tools/list_changed` 通知时，`McpManager` 自动重新获取工具列表（`mcp-manager.ts:162-166`），并通过 `onToolsListChanged` 回调通知上层。

## 服务器状态管理

`McpServerStatus` 类型（`mcp-manager.ts:20-31`）追踪每个服务器的状态：

```typescript
export type McpServerStatus = {
  name: string;
  status: "starting" | "ready" | "failed" | "reconnecting";
  connected: boolean;
  error?: string;
  toolCount: number;
  tools: string[];
  promptCount: number;
  prompts: string[];
  resourceCount: number;
  resources: string[];
};
```

### 状态流转

```
starting ──▶ ready        连接成功，工具已加载
starting ──▶ failed       连接失败
ready ──▶ failed          服务器崩溃（onServerCrash）
failed ──▶ reconnecting   手动重连（reconnect 方法）
reconnecting ──▶ ready    重连成功
reconnecting ──▶ failed   重连失败
```

### 崩溃恢复

服务器进程意外退出时，`McpClient` 的 disconnect handler 触发 `onServerCrash`（`mcp-manager.ts:264-283`）：

1. 清理该服务器的所有工具、提示、资源条目
2. 移除断开的客户端
3. 触发 `onToolsListChanged` 回调
4. 将状态设为 `failed`

### 判断 MCP 工具

`McpManager.isMcpTool(name)` 通过检查名称是否以 `"mcp__"` 开头来判断（`mcp-manager.ts:336-338`）：

```typescript
isMcpTool(name: string): boolean {
  return name.startsWith("mcp__");
}
```

## 工具执行

`executeMcpTool` 方法（`mcp-manager.ts:340-368`）根据命名空间名称查找工具，调用原始工具名，并提取 text 类型的内容拼接返回：

```typescript
const result = await tool.client.callTool(tool.originalName, args, timeoutMs);
const text = result.content
  .filter((c) => c.type === "text" && c.text)
  .map((c) => c.text)
  .join("\n");
```

## 使用方式

在 TUI 中输入 `/mcp` 可查看所有已配置 MCP 服务器的状态和工具列表。配置完成后，直接在对话中描述需求，LLM 会自动选择并调用对应的 MCP 工具。

## 相关概念

- [项目简介](/concepts/00-introduction.md)
- [三包 monorepo 架构](/concepts/01-architecture.md)
- [权限系统](/concepts/02-permission-system.md)
- [CLI 命令与会话管理](/concepts/04-cli-commands.md)
