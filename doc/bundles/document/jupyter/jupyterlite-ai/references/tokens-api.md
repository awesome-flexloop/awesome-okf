---
type: Reference
title: Token 与核心接口 API 参考
description: jupyterlite-ai 核心 Lumino Token 和 TypeScript 接口定义
tags: [jupyterlite-ai, tokens, api, reference]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
---

# Token 与核心接口 API 参考

## Token 注册表

jupyterlite-ai 使用 Lumino `Token` 机制实现依赖注入，所有核心服务通过 Token 暴露：

| Token 常量 | 接口类型 | 所在包 | 描述 |
|-----------|---------|--------|------|
| `IToolRegistry` | `IToolRegistry` | @jupyternaut/agent | AI 工具注册表 |
| `ISkillRegistry` | `ISkillRegistry` | @jupyternaut/agent | AI 技能注册表 |
| `IProviderRegistry` | `IProviderRegistry` | @jupyternaut/agent | AI Provider 注册表 |
| `IAISettingsModel` | `IAISettingsModel` | @jupyternaut/agent | AI 设置模型 |
| `IAgentManager` | `IAgentManager` | @jupyternaut/agent | AI 代理管理器 |
| `IAgentManagerFactory` | `IAgentManagerFactory` | @jupyternaut/agent | Agent 管理器工厂 |
| `IDiffManager` | `IDiffManager` | @jupyternaut/agent | Diff 显示管理器 |

## IToolRegistry 接口

```typescript
interface IToolRegistry {
  readonly tools: Record<string, ITool>;
  readonly namedTools: INamedTool[];
  readonly toolsChanged: ISignal<IToolRegistry, void>;
  add(name: string, tool: ITool): void;
  get(name: string | null): ITool | null;
  remove(name: string): boolean;
}
```

## IProviderRegistry 接口

```typescript
interface IProviderRegistry {
  readonly providers: Record<string, IProviderInfo>;
  readonly providersChanged: ISignal<IProviderRegistry, void>;
  registerProvider(info: IProviderInfo): void;
  getProviderInfo(id: string): IProviderInfo | null;
  createChatModel(id: string, options: IModelOptions): LanguageModel | null;
  createCompletionModel(id: string, options: IModelOptions): LanguageModel | null;
  getAvailableProviders(): string[];
}
```

## IProviderInfo 接口

```typescript
interface IProviderInfo {
  id: string;
  name: string;
  apiKeyRequirement: 'required' | 'optional' | 'none';
  defaultModels: string[];
  modelInfo?: Record<string, IProviderModelInfo>;
  supportsBaseURL?: boolean;
  supportsHeaders?: boolean;
  supportsToolCalling?: boolean;
  description?: string;
  baseUrls?: { url: string; description?: string }[];
  providerToolCapabilities?: IProviderToolCapabilities;
  cacheProviderOptions?: NonNullable<ModelMessage['providerOptions']>;
  factory: IProviderFactory;
}
```

## ISkillRegistry 接口

```typescript
interface ISkillRegistry {
  readonly skillsChanged: ISignal<ISkillRegistry, void>;
  registerSkill(skill: ISkillRegistration): IDisposable;
  listSkills(query?: string): ISkillSummary[];
  getSkill(name: string): ISkillDefinition | null;
  getSkillResource(name: string, resource: string): Promise<ISkillResourceResult>;
}
```

## IAgentManager 接口

```typescript
interface IAgentManager {
  activeProvider: string;
  readonly agentEvent: ISignal<IAgentManager, IAgentManager.IAgentEvent>;
  readonly activeProviderChanged: ISignal<IAgentManager, string | undefined>;
  readonly tokenUsage: ITokenUsage;
  readonly tokenUsageChanged: ISignal<IAgentManager, ITokenUsage>;
  readonly selectedAgentTools: ToolMap;
  refreshSkills(): void;
  setSelectedTools(toolNames: string[]): void;
  hasValidConfig(): boolean;
  clearHistory(): Promise<void>;
  setHistory(messages: ModelMessage[]): void;
  stopStreaming(): void;
  approveToolCall(toolCallId: string, reason?: string): void;
  rejectToolCall(toolCallId: string, reason?: string): void;
  generateResponse(message: UserContent): Promise<void>;
  textResponse(messages: ModelMessage[]): Promise<string>;
  initializeAgent(mcpTools?: ToolMap): Promise<void>;
}
```

## IAgentEvent 事件类型

```typescript
namespace IAgentManager {
  type IAgentEvent =
    | { type: 'message_start'; data: { messageId: string } }
    | { type: 'message_chunk'; data: { messageId: string; chunk: string; fullContent: string } }
    | { type: 'message_complete'; data: { messageId: string; content: string } }
    | { type: 'tool_call_start'; data: { callId: string; toolName: string; title?: string; input: string } }
    | { type: 'tool_call_complete'; data: { callId: string; toolName: string; outputData: unknown; isError: boolean } }
    | { type: 'tool_approval_request'; data: { toolCallId: string; toolName: string; args: unknown } }
    | { type: 'tool_approval_resolved'; data: { toolCallId: string; approved: boolean } }
    | { type: 'error'; data: { error: Error } };
}
```

## IAIConfig 配置接口

```typescript
interface IAIConfig {
  useSecretsManager: boolean;
  providers: IProviderConfig[];
  defaultProvider: string;
  activeCompleterProvider?: string;
  useSameProviderForChatAndCompleter: boolean;
  contextAwareness: boolean;
  codeExecution: boolean;
  systemPrompt: string;
  completionSystemPrompt: string;
  toolsEnabled: boolean;
  commandsRequiringApproval: string[];
  commandsAutoRenderMimeBundles: string[];
  trustedMimeTypesForAutoRender: string[];
  showCellDiff: boolean;
  showFileDiff: boolean;
  diffDisplayMode: 'split' | 'unified';
  skillsPaths: string[];
}
```
