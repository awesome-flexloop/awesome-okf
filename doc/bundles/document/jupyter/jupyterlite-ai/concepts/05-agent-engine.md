---
type: Concept
title: Agent 执行引擎
description: AgentManager 是 AI 代理的核心执行引擎，基于 Vercel AI SDK ToolLoopAgent 实现 LLM 对话、工具调用循环、审批流程和流式响应
tags: [jupyterlite-ai, agent, execution, tool-loop, streaming]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
  - id: tokens
    resource: /references/tokens-api.md
    title: Token 与核心接口 API 参考
---

# Agent 执行引擎

`AgentManager` 是 jupyterlite-ai 的核心执行引擎，负责管理与 LLM 的完整对话生命周期，包括消息历史、工具调用循环、用户审批、流式响应和 MCP 工具集成。

## AgentManager 职责

| 职责 | 相关方法 |
|------|---------|
| 模型初始化 | `initializeAgent()` |
| 消息生成 | `generateResponse()`, `textResponse()` |
| 工具管理 | `setSelectedTools()`, `selectedAgentTools` |
| 审批流程 | `approveToolCall()`, `rejectToolCall()` |
| 会话管理 | `clearHistory()`, `setHistory()` |
| 中断控制 | `stopStreaming()` |
| 技能刷新 | `refreshSkills()` |
| 事件通知 | `agentEvent` 信号 |
| Token 统计 | `tokenUsage`, `tokenUsageChanged` |

## AgentManagerFactory

工厂类负责创建 AgentManager 实例和管理共享资源：

```typescript
class AgentManagerFactory implements IAgentManagerFactory {
  constructor(options: {
    settingsModel: IAISettingsModel;
    skillRegistry?: ISkillRegistry;
    mcpManager?: IMcpManager;
    secretsManager?: ISecretsManager;
    token: symbol | null;
  });

  createAgent(options: IAgentManager.IOptions): IAgentManager;
  isMCPServerConnected(serverName: string): boolean;
  getMCPTools(): Promise<ToolMap>;
  mcpConnectionChanged: ISignal<this, boolean>;
}
```

工厂维护：
- MCP 客户端连接池（`_mcpClients: IMCPClientWrapper[]`）
- 所有创建的 AgentManager 引用（用于 MCP 工具更新时重新初始化）
- 技能快照缓存（`refreshSkillSnapshots()`）

## 初始化流程

`initializeAgent()` 方法准备 LLM 调用环境：

```
1. 获取当前活跃 Provider 的配置
2. 通过 ProviderRegistry.createChatModel() 创建 LanguageModel
3. 收集用户选中的工具（selectedAgentTools）
4. 如果有 MCP 工具，合并到工具集中
5. 创建 Provider 托管工具（webSearch/webFetch，如果 Provider 支持）
6. 构建系统提示词（包含技能指令）
7. 配置工具审批策略
8. 准备完成，等待 generateResponse() 调用
```

## 对话生成循环

`generateResponse(message)` 是核心方法，执行完整的 Tool Loop：

```
用户消息 → generateResponse(UserContent)
  │
  ├─ 1. 添加用户消息到历史
  ├─ 2. 发出 message_start 事件
  ├─ 3. 调用 ToolLoopAgent.stream()
  │     │
  │     ├─ LLM 生成文本流 → message_chunk 事件（实时更新UI）
  │     │
  │     ├─ LLM 返回 tool_calls
  │     │   ├─ 检查每个工具是否需要审批
  │     │   │   ├─ 需要审批 → tool_approval_request 事件 → 暂停
  │     │   │   │   ├─ approveToolCall() → 继续执行工具
  │     │   │   │   └─ rejectToolCall() → 返回拒绝结果给LLM
  │     │   │   └─ 不需要审批 → 直接执行
  │     │   │
  │     │   ├─ 发出 tool_call_start 事件
  │     │   ├─ 执行工具（execute_command / browser_fetch / MCP工具等）
  │     │   ├─ 发出 tool_call_complete 事件
  │     │   └─ 工具结果加入消息历史 → 继续 LLM 调用
  │     │
  │     └─ LLM 返回最终文本（无更多 tool_calls）
  │        └─ message_complete 事件
  │
  ├─ 4. 更新 tokenUsage 统计
  └─ 5. 完成
```

## 事件系统

AgentManager 通过 `agentEvent` 信号发出类型安全的事件：

```typescript
type IAgentEvent =
  | { type: 'message_start'; data: { messageId: string } }
  | { type: 'message_chunk'; data: { messageId: string; chunk: string; fullContent: string } }
  | { type: 'message_complete'; data: { messageId: string; content: string } }
  | { type: 'tool_call_start'; data: { callId: string; toolName: string; title?: string; input: string } }
  | { type: 'tool_call_complete'; data: { callId: string; toolName: string; outputData: unknown; isError: boolean } }
  | { type: 'tool_approval_request'; data: { toolCallId: string; toolName: string; args: unknown } }
  | { type: 'tool_approval_resolved'; data: { toolCallId: string; approved: boolean } }
  | { type: 'error'; data: { error: Error } };
```

UI 层监听这些事件实现实时更新：
- `message_chunk` → 逐字渲染 AI 回复
- `tool_call_start/complete` → 显示工具调用状态指示器
- `tool_approval_request` → 弹出审批对话框
- `error` → 显示错误提示

## 工具审批实现

审批流程基于 Vercel AI SDK 的 `toolApproval` 选项：

```typescript
// AgentManager 内部实现审批策略
const approvalPolicy = (input) => {
  const needApproval = settingsModel.config.commandsRequiringApproval;
  if (input.toolName === 'execute_command') {
    const commandId = input.args?.commandId;
    if (commandId && needApproval.includes(commandId)) {
      return 'user-approval';  // 暂停执行，等待用户决策
    }
  }
  return undefined;  // 自动批准
};
```

`approveToolCall()` 和 `rejectToolCall()` 方法通过 Promise 决议恢复 Tool Loop 执行。

## 流式处理

流式响应通过 Vercel AI SDK 的 `streamText` 实现：

```typescript
// 核心模式（简化）
const { textStream, toolCalls, stepResults } = agent.stream({
  model: languageModel,
  system: systemPrompt,
  messages: history,
  tools: allTools,
  toolApproval: approvalPolicy,
  maxSteps: maxTurns  // 防止无限工具调用循环
});

for await (const chunk of textStream) {
  this._agentEvent.emit('message_chunk', {
    messageId,
    chunk,
    fullContent: accumulatedContent
  });
}
```

`maxTurns` 参数（默认来自 Provider 配置）限制最大工具调用轮次，防止无限循环。

## 中断控制

`stopStreaming()` 通过 `AbortController` 中断正在进行的 LLM 请求：

```typescript
stopStreaming(): void {
  this._abortController?.abort();
  this._abortController = new AbortController();
}
```

中断后 Tool Loop 立即停止，已生成的部分文本保留在聊天中。

## Token 使用统计

```typescript
interface ITokenUsage {
  inputTokens: number;           // 累计输入 token
  outputTokens: number;          // 累计输出 token
  lastRequestInputTokens?: number;  // 最近请求的 prompt token
  contextWindow?: number;        // 当前模型的上下文窗口大小
}
```

Token 统计在每次 LLM 调用完成后更新，并通过 `tokenUsageChanged` 信号通知 UI 显示用量。

## 会话历史管理

- `clearHistory()`：清除所有消息，重置 Agent 状态
- `setHistory(messages)`：从预构建的消息恢复历史（用于聊天恢复功能）
- 历史消息格式为 Vercel AI SDK 的 `ModelMessage[]`，支持多模态内容（图像、文件等）

## 技能集成

`refreshSkills()` 方法重新加载技能快照并重建 Agent：

1. 从 `SkillRegistry` 获取所有可用技能
2. 将技能指令注入系统提示词
3. 重新初始化 Agent（`initializeAgent()`）
4. 新技能在后续对话中生效

`skillsChanged` 信号触发自动刷新。

## MCP 工具动态更新

当 MCP 服务器连接状态变化时：

1. `AgentManagerFactory._onSettingsChanged` 监听 MCP 变更
2. 重新获取所有 MCP 工具（`getMCPTools()`）
3. 遍历所有已创建的 AgentManager，调用 `initializeAgent(mcpTools)` 注入新工具

这意味着 MCP 服务器在运行时连接/断开，所有打开的聊天窗口会自动感知。

## textResponse 方法

`textResponse(messages)` 是一个轻量级方法，用于一次性文本请求（不加入历史、不触发事件）：

```typescript
async textResponse(messages: ModelMessage[]): Promise<string>
```

用途：
- 自动生成聊天标题（`requestTitle()`）
- 其他后台 AI 分析任务

## 配置有效性检查

`hasValidConfig()` 检查当前配置是否可用于发起对话：

```typescript
hasValidConfig(): boolean {
  const provider = settingsModel.getProvider(this.activeProvider);
  if (!provider) return false;
  const info = providerRegistry.getProviderInfo(provider.provider);
  if (!info) return false;
  if (info.apiKeyRequirement === 'required' && !this.getApiKey()) return false;
  return true;
}
```

## 相关概念

- [Tool 工具系统](04-tool-system.md)
- [Skill 技能系统](06-skill-system.md)
- [聊天界面与会话管理](09-chat-ui.md)
- [MCP 协议集成](08-mcp-integration.md)
