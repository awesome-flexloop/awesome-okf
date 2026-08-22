---
type: Concept
title: MCP 协议集成
description: jupyterlite-ai 通过 jupyter-mcp-manager 和 @ai-sdk/mcp 集成 Model Context Protocol 服务器，自动发现和调用 MCP 工具
tags: [jupyterlite-ai, mcp, model-context-protocol, tools]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
---

# MCP 协议集成

MCP（Model Context Protocol）是一种开放协议，允许 AI 模型通过标准化接口与外部工具和数据源交互。jupyterlite-ai 通过 `jupyter-mcp-manager` 和 `@ai-sdk/mcp` 实现 MCP 服务器的动态连接和工具发现。

## MCP 架构

```
┌─────────────────────────────────────────────────────┐
│                  AgentManager                       │
│  ┌─────────────────────────────────────────────┐   │
│  │           ToolLoopAgent (Vercel AI SDK)    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │ 内置工具  │  │MCP 工具  │  │Provider  │  │   │
│  │  │(commands │  │(来自MCP  │  │托管工具   │  │   │
│  │  │ browser) │  │ servers) │  │(webSearch)│  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────┘
                        │ initializeAgent(mcpTools)
┌───────────────────────┴─────────────────────────────┐
│              AgentManagerFactory                    │
│  ┌─────────────────────────────────────────────┐   │
│  │  MCP 客户端池 (IMCPClientWrapper[])         │   │
│  │  ├─ MCP Server 1 → @ai-sdk/mcp client      │   │
│  │  │   └─ tools() → ToolMap                  │   │
│  │  ├─ MCP Server 2 → ...                      │   │
│  │  └─ ...                                     │   │
│  └──────────────────────┬──────────────────────┘   │
└─────────────────────────┼───────────────────────────┘
                          │ getMCPTools()
┌─────────────────────────┴───────────────────────────┐
│             jupyter-mcp-manager (IMcpManager)       │
│  ┌─────────────────────────────────────────────┐   │
│  │  服务器注册/发现/连接管理                     │   │
│  │  serversChanged 信号                         │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## MCP 客户端连接

`AgentManagerFactory` 管理 MCP 客户端生命周期：

```typescript
interface IMCPClientWrapper {
  name: string;
  client: MCPClient;  // @ai-sdk/mcp 的 MCPClient
}
```

### 连接流程

```
1. IMcpManager.serversChanged 信号触发
2. _initializeAgents() 被调用
3. 为每个已注册的 MCP 服务器创建 MCPClient
4. client = createMCPClient({ transport, ... })
5. 存储到 _mcpClients 数组
6. mcpConnectionChanged 信号发出（true）
7. 调用 getMCPTools() 获取所有 MCP 工具
8. 遍历所有 AgentManager，调用 initializeAgent(mcpTools)
```

### 断开处理

- 服务器断开时从 `_mcpClients` 移除
- `isMCPServerConnected(name)` 查询连接状态
- 断开后自动从 Agent 工具集中移除该服务器的工具

## 工具获取与注入

`getMCPTools()` 方法从所有已连接的 MCP 服务器获取工具：

```typescript
async getMCPTools(): Promise<ToolMap> {
  const mcpTools: ToolMap = {};
  for (const wrapper of this._mcpClients) {
    try {
      const tools = await wrapper.client.tools();
      Object.assign(mcpTools, tools);
    } catch (error) {
      console.warn(`Failed to get tools from MCP server ${wrapper.name}:`, error);
    }
  }
  return mcpTools;
}
```

每个 MCP 工具自动符合 Vercel AI SDK 的 `Tool` 接口，可以直接传递给 `generateText`/`streamText` 使用。

## 对 Agent 透明

MCP 工具对 AI 模型完全透明——模型不区分内置工具和 MCP 工具，统一通过 Tool Calling 机制调用。AgentManager 合并工具集：

```typescript
// initializeAgent 中（简化）
const allTools = {
  ...this._selectedTools,   // 用户选中的内置工具
  ...mcpTools,              // MCP 服务器提供的工具
  ...providerTools          // Provider 原生工具（webSearch等）
};
```

## 设置面板集成

MCP 服务器配置通过设置面板管理，使用 `jupyter-mcp-manager` 提供的表单渲染器：

```typescript
// settings-panel 插件中
const mcpServerRenderer = formRenderer?.getRenderer(
  'jupyter-mcp-manager:manager.mcpSettings'
).fieldRenderer;

const settingsWidget = new AISettingsWidget({
  // ...
  mcpServerRenderer  // 注入 MCP 设置渲染器
});
```

用户可以在设置面板中添加/删除/配置 MCP 服务器连接。

## MCP 服务器示例

用户可以配置多种类型的 MCP 服务器：

| 类型 | 示例 |
|------|------|
| 文件系统 | 提供文件读写工具 |
| 数据库 | 提供 SQL 查询工具 |
| Git | 提供版本控制操作 |
| Jupyter Kernel | 提供代码执行工具 |
| Web API | 提供外部服务调用 |

## 新聊天窗口的 MCP 处理

由于 MCP 连接是异步的，新聊天窗口可能在 MCP 初始化完成前创建。AgentManagerFactory 通过 Promise 队列处理这种竞态条件：

```typescript
createAgent(options) {
  const agentManager = new AgentManager({...});
  this._agentManagers.push(agentManager);

  // MCP 初始化完成后，重新注入工具
  this._initQueue
    .then(() => this.getMCPTools())
    .then(mcpTools => {
      if (Object.keys(mcpTools).length > 0) {
        agentManager.initializeAgent(mcpTools);
      }
    });

  return agentManager;
}
```

`_initQueue` 确保所有 MCP 服务器连接完成后才注入工具，避免工具集不完整。

## 相关概念

- [Agent 执行引擎](05-agent-engine.md)
- [Tool 工具系统](04-tool-system.md)
- [配置与设置](07-settings-and-config.md)
