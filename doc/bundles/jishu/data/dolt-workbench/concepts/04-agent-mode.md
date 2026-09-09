---
type: concept
title: Agent Mode 实现
description: 基于 Claude AI SDK 的智能助手模式，支持自然语言查询和工具调用确认
tags: [dolt-workbench, agent, claude, ai, mcp]
status: stable
generated:
  by: reference_agent/agnes-2.5-flash
  at: 2026-09-09T04:00:00Z
sources:
  - id: agent-src
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/web/main/agent/anthropicAgent.ts
    title: ClaudeAgent 完整实现
  - id: agent-types
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/web/main/agent/types.ts
    title: Agent 类型定义
  - id: agent-mcp
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/web/main/agent/mcpServerArgs.ts
    title: MCP Server 参数生成
  - id: agent-ipc
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/web/main/agent/ipcHandlers.ts
    title: IPC Agent Handler
---

# Agent Mode 实现

## 概述

Agent Mode 是 dolt-workbench 的 AI 助手功能，基于 Anthropic 的 Claude AI SDK 实现。它允许用户通过自然语言与数据库交互，执行查询、查看 schema、管理分支等操作。

## 核心类：ClaudeAgent

`anthropicAgent.ts` 约 600 行，完整实现了 Claude AI Agent 模式。

### 依赖

```typescript
import { query, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
```

### 类型定义

```typescript
// MCP 服务器配置
type McpServerConfig = {
  host: string;
  port: number;
  user: string;
  database: string;
  databaseFile: string;
  password: string;
  useSSL: boolean;
  type: "mysql" | "postgres" | "sqlite";
  isDolt: boolean;
};

// Agent 配置
type AgentConfig = {
  apiKey: string;
  mcpConfig: McpServerConfig;
  model: string;
};

// 内容块联合类型
type ContentBlock = 
  | TextContentBlock
  | ToolUseContentBlock
  | ImageContentBlock;

// Agent 消息
type AgentMessage = {
  id: string;
  role: "user" | "assistant";
  contentBlocks: ContentBlock[];
  timestamp: number;
};
```

## 动态系统提示词

```typescript
function getSystemPrompt(
  database: string,
  dbType: string,
  isDolt: boolean,
  databaseFile: string,
): string {
  let prompt = `You are a helpful database assistant for ${dbType} database "${database}".\n\n`;
  
  if (isDolt) {
    prompt += `This is a Dolt database with version control capabilities.\n`;
    prompt += `You can help with branches, commits, diffs, and merges.\n\n`;
  }
  
  prompt += `When executing SQL queries:\n`;
  prompt += `1. Always explain what the query does\n`;
  prompt += `2. Show the results in a readable format\n`;
  prompt += `3. Suggest improvements if needed\n`;
  
  return prompt;
}
```

## MCP 服务器注册

Agent 注册 3 个自定义工具：

```typescript
async createWorkbenchMcpServer() {
  const mcpServer = createSdkMcpServer({
    name: "dolt-workbench",
    version: "1.0.0",
  });
  
  // 工具 1: switch_branch - 切换分支
  mcpServer.tool("switch_branch", 
    { branchName: "string" },
    async ({ branchName }) => {
      // 执行分支切换
      await this.executeSwitchBranch(branchName);
      return { success: true, branch: branchName };
    }
  );
  
  // 工具 2: refresh_page - 刷新页面
  mcpServer.tool("refresh_page",
    {},
    async () => {
      // 触发 UI 刷新
      this.mainWindow.webContents.send("agent:refresh-page");
      return { success: true };
    }
  );
  
  // 工具 3: display_image - 显示图片
  mcpServer.tool("display_image",
    { imagePath: "string" },
    async ({ imagePath }) => {
      // 在聊天中显示图片
      return { image: imagePath };
    }
  );
  
  return mcpServer;
}
```

## 敏感工具确认机制

以下工具需要用户确认后才能执行：

```typescript
const TOOLS_REQUIRING_CONFIRMATION = [
  "create_dolt_commit",
  "delete_dolt_branch",
  "move_dolt_branch",
  "dolt_reset_hard",
];

async canUseTool(
  toolName: string,
  input: any,
  options: any
): Promise<boolean> {
  if (!TOOLS_REQUIRING_CONFIRMATION.includes(toolName)) {
    return true;
  }
  
  // 通过 IPC 事件请求用户确认
  const confirmed = await this.requestUserConfirmation(toolName, input);
  return confirmed;
}
```

IPC 事件流：
```
ClaudeAgent → mainWindow.webContents.send("agent:tool-confirmation-request", {...})
用户确认 → mainWindow.webContents.send("agent:tool-confirmation-response", { confirmed: true/false })
```

## 事件处理

### IPC 事件发送

| 事件 | 说明 |
|---|---|
| `agent:session-id` | 会话 ID 生成 |
| `agent:content-block` | 内容块更新 |
| `agent:tool-result` | 工具执行结果 |
| `agent:error` | 错误信息 |
| `agent:message-complete` | 消息完成 |
| `agent:interrupted` | 中断信号 |
| `agent:switch-branch` | 分支切换通知 |
| `agent:refresh-page` | 页面刷新通知 |

### 事件处理流程

```typescript
async processEvents(handle: any) {
  for await (const event of handle) {
    switch (event.type) {
      case "system":
        // 系统事件（开始/结束）
        this.mainWindow.webContents.send("agent:content-block", {
          type: "system",
          data: event.data,
        });
        break;
        
      case "assistant":
        // AI 回复
        this.mainWindow.webContents.send("agent:content-block", {
          type: "assistant",
          data: event.data,
        });
        break;
        
      case "user":
        // 用户消息确认
        this.mainWindow.webContents.send("agent:content-block", {
          type: "user",
          data: event.data,
        });
        break;
        
      case "result":
        // 查询结果
        this.mainWindow.webContents.send("agent:tool-result", {
          data: event.data,
        });
        break;
    }
  }
}
```

## MCP Server 参数生成

`mcpServerArgs.ts` 根据数据库类型生成不同的 MCP 启动参数：

```typescript
function getMcpServerArgs(
  mcpConfig: McpServerConfig,
  commitAuthor?: string
): string[] {
  const args: string[] = ["--stdio"];
  
  switch (mcpConfig.type) {
    case "sqlite":
    case "doltlite":
      args.push("--doltlite", "--db-file", mcpConfig.databaseFile);
      break;
      
    case "mysql":
    case "dolt":
      args.push(
        "--host", mcpConfig.host,
        "--port", String(mcpConfig.port),
        "--user", mcpConfig.user,
        "--password", mcpConfig.password,
        "--database", mcpConfig.database,
      );
      break;
      
    case "postgres":
    case "doltgres":
      args.push(
        "--host", mcpConfig.host,
        "--port", String(mcpConfig.port),
        "--user", mcpConfig.user,
        "--password", mcpConfig.password,
        "--database", mcpConfig.database,
        "--doltgres",
      );
      break;
  }
  
  if (mcpConfig.useSSL) {
    args.push("--tls", "skip-verify");
  }
  
  if (commitAuthor) {
    args.push("--author", commitAuthor);
  }
  
  return args;
}
```

## IPC Handler 接口

15 个 IPC handler ID 定义在 `ipcHandlers.ts`：

| Handler ID | 方向 | 功能 |
|---|---|---|
| `agent:get-api-key` | Main→Renderer | 获取 API Key |
| `agent:store-api-key` | Renderer→Main | 存储 API Key |
| `agent:clear-api-key` | Main→Renderer | 清除 API Key |
| `agent:connect` | Renderer→Main | 连接到 Agent |
| `agent:send-message` | Renderer→Main | 发送消息 |
| `agent:disconnect` | Renderer→Main | 断开连接 |
| `agent:clear-history` | Renderer→Main | 清除历史 |
| `agent:cancel-tool` | Renderer→Main | 取消工具调用 |
| `agent:set-model` | Renderer→Main | 设置模型 |
| `agent:abort` | Renderer→Main | 中止当前操作 |
| `agent:list-sessions` | Renderer→Main | 列出会话 |
| `agent:load-session-messages` | Renderer→Main | 加载会话消息 |
| `agent:register-session` | Renderer→Main | 注册会话 |
| `agent:unregister-session` | Renderer→Main | 注销会话 |
| `agent:switch-session` | Renderer→Main | 切换会话 |

`ClaudeAgent` 类在 `anthropicAgent.ts` 中定义，作为单例通过 `registerAgentIpcHandlers()` 注册到主进程。

## 参考文档

- [架构总览](./01-architecture.md)
- [QueryFactory 工厂模式](./02-query-factory-pattern.md)
