---
type: Concept
title: Provider 模型管理
description: Provider 注册表管理多个 AI 模型提供商，统一 Vercel AI SDK LanguageModel 接口，支持内置和自定义 Provider
tags: [jupyterlite-ai, provider, llm, model]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: tokens
    resource: /references/tokens-api.md
    title: Token 与核心接口 API 参考
  - id: providers
    resource: /references/built-in-providers.md
    title: 内置 Provider 参考
---

# Provider 模型管理

Provider 系统是 jupyterlite-ai 的模型抽象层，通过 `IProviderRegistry` 统一管理多个 AI 模型提供商，将它们适配到 Vercel AI SDK 的 `LanguageModel` 接口。

## Provider 注册表

`ProviderRegistry` 是核心单例，实现 `IProviderRegistry` 接口：

```typescript
class ProviderRegistry implements IProviderRegistry {
  get providers(): Record<string, IProviderInfo>;
  get providersChanged(): ISignal<IProviderRegistry, void>;
  registerProvider(info: IProviderInfo): void;
  getProviderInfo(id: string): IProviderInfo | null;
  createChatModel(id: string, options: IModelOptions): LanguageModel | null;
  createCompletionModel(id: string, options: IModelOptions): LanguageModel | null;
  getAvailableProviders(): string[];
}
```

### 核心方法

| 方法 | 描述 |
|------|------|
| `registerProvider(info)` | 注册新 Provider，重复 ID 抛出错误 |
| `getProviderInfo(id)` | 获取 Provider 元信息 |
| `createChatModel(id, options)` | 创建聊天模型实例 |
| `createCompletionModel(id, options)` | 创建补全模型实例（当前实现与 Chat 相同） |
| `getAvailableProviders()` | 返回所有已注册 Provider ID 列表 |

注册表内部使用 `Record<string, IProviderInfo>` 存储，通过 `providersChanged` 信号通知变更。

## IProviderInfo 结构

每个 Provider 通过 `IProviderInfo` 描述其能力：

```typescript
interface IProviderInfo {
  id: string;                              // 唯一标识符
  name: string;                            // 显示名称
  apiKeyRequirement: 'required' | 'optional' | 'none';  // API Key 策略
  defaultModels: string[];                 // 默认模型列表
  modelInfo?: Record<string, IProviderModelInfo>;  // 模型元数据
  supportsBaseURL?: boolean;               // 是否支持自定义 Base URL
  supportsHeaders?: boolean;               // 是否支持自定义 Headers
  supportsToolCalling?: boolean;           // 是否支持工具调用
  description?: string;                    // 可选描述
  baseUrls?: { url: string; description?: string }[];  // 预设 URL（如本地服务）
  providerToolCapabilities?: IProviderToolCapabilities; // Provider 原生工具能力
  cacheProviderOptions?: ModelMessage['providerOptions']; // 缓存配置
  factory: IProviderFactory;               // 模型工厂函数
}
```

### 模型元数据

```typescript
interface IProviderModelInfo {
  contextWindow?: number;    // 上下文窗口大小（token 数）
  supportsImages?: boolean;  // 是否支持图像输入
  supportsPdf?: boolean;     // 是否支持 PDF 输入
  supportsAudio?: boolean;   // 是否支持音频输入
}
```

### Provider 原生工具能力

部分 Provider 提供内置的 Web 搜索/抓取能力：

```typescript
interface IProviderToolCapabilities {
  webSearch?: {
    implementation: 'openai' | 'anthropic';
    requiresNoFunctionTools?: boolean;  // 启用此能力时需禁用 function tools
  };
  webFetch?: {
    implementation: 'anthropic';
  };
}
```

## 内置 Provider

jupyterlite-ai 内置 5 个 Provider：

### Anthropic Claude

- **ID**：`anthropic`
- **SDK**：`@ai-sdk/anthropic` 的 `createAnthropic()`
- **特殊配置**：需要 `anthropic-dangerous-direct-browser-access: 'true'` header 允许浏览器直连
- **原生工具**：Web Search、Web Fetch（anthropic 实现）
- **缓存**：启用 ephemeral prompt caching
- **默认模型**：claude-opus-4-6、claude-sonnet-4-6、claude-haiku-4-5 等

### Google Gemini

- **ID**：`google`
- **SDK**：`@ai-sdk/google` 的 `createGoogleGenerativeAI()`
- **默认模型**：gemini-2.5-flash（兜底默认）、gemini-3.1-pro-preview 等

### Mistral AI

- **ID**：`mistral`
- **SDK**：`@ai-sdk/mistral` 的 `createMistral()`
- **默认模型**：mistral-large-latest（兜底默认）

### OpenAI

- **ID**：`openai`
- **SDK**：`@ai-sdk/openai` 的 `createOpenAI()`
- **原生工具**：Web Search（openai 实现）
- **默认模型**：gpt-4o（兜底默认）、gpt-5.4、o3、o1 等

### Generic（OpenAI 兼容）

- **ID**：`generic`
- **SDK**：`@ai-sdk/openai-compatible` 的 `createOpenAICompatible()`
- **API Key**：可选（本地部署可能不需要），默认值 `'dummy'`
- **预设 URL**：`http://localhost:4000`（LiteLLM）、`http://localhost:11434/v1`（Ollama）
- **用途**：对接 Ollama、LiteLLM Proxy、vLLM、LocalAI、OpenRouter 等兼容服务

## 工厂函数模式

每个 Provider 的 `factory` 字段是一个函数，接收 `IModelOptions` 返回 Vercel AI SDK 的 `LanguageModel`：

```typescript
type IProviderFactory = (options: IModelOptions) => LanguageModel;

interface IModelOptions {
  apiKey?: string;
  baseURL?: string;
  headers?: Record<string, string>;
  model?: string;
  provider?: string;  // Provider ID（generic provider 使用）
  // ... 其他参数
}
```

工厂函数示例（以 OpenAI 为例）：

```typescript
factory: (options: IModelOptions) => {
  if (!options.apiKey) {
    throw new Error('API key required for OpenAI');
  }
  const openai = createOpenAI({
    apiKey: options.apiKey,
    ...(options.baseURL && { baseURL: options.baseURL }),
    ...(options.headers && { headers: options.headers })
  });
  const modelName = options.model || 'gpt-4o';
  return openai(modelName);
}
```

## 用户配置

用户通过设置面板配置 Provider，配置存储在 `IAIConfig.providers` 数组中：

```typescript
interface IProviderConfig {
  id: string;
  name: string;
  provider: string;       // 对应 ProviderRegistry 中的 Provider ID
  model: string;          // 选中的模型名
  apiKey?: string;
  baseURL?: string;
  headers?: Record<string, string>;
  parameters?: IProviderParameters;
  customSettings?: Record<string, any>;
}

interface IProviderParameters {
  temperature?: number;
  maxOutputTokens?: number;
  maxTurns?: number;      // 最大 tool call 轮次
  contextWindow?: number;
  supportsFillInMiddle?: boolean;  // 代码补全 FIM 支持
  useFilterText?: boolean;
}
```

### 安全密钥存储

API Key 不直接存储在设置文件中，而是通过 `jupyter-secrets-manager` 安全存储。设置中保存 `SECRETS_REPLACEMENT`（`'***'`）占位符，实际值通过 SecretsManager 获取。

## 注册自定义 Provider

第三方扩展可以添加自定义 Provider：

```typescript
import { IProviderRegistry, IProviderInfo } from '@jupyternaut/agent';
import { createMyAISDK } from 'my-ai-sdk';

const myProvider: IProviderInfo = {
  id: 'my-custom-ai',
  name: 'My Custom AI',
  apiKeyRequirement: 'required',
  defaultModels: ['my-model-v1', 'my-model-v2'],
  supportsToolCalling: true,
  supportsBaseURL: true,
  factory: (options) => {
    const client = createMyAISDK({
      apiKey: options.apiKey,
      baseURL: options.baseURL
    });
    return client(options.model || 'my-model-v1');
  }
};

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:register-provider',
  autoStart: true,
  requires: [IProviderRegistry],
  activate: (app, registry) => {
    registry.registerProvider(myProvider);
  }
};
```

## 模型创建流程

当 AgentManager 需要调用模型时：

```
1. 从 IAISettingsModel 获取当前 Provider 配置（IProviderConfig）
2. 调用 ProviderRegistry.createChatModel(providerId, modelOptions)
3. ProviderRegistry 查找 IProviderInfo.factory
4. 工厂函数调用对应 @ai-sdk/* 的 createXxx() 创建 LanguageModel
5. 将 LanguageModel 传递给 Vercel AI SDK 的 generateText/streamText
```

## 相关概念

- [Token 依赖注入系统](02-token-di-system.md)
- [Agent 执行引擎](05-agent-engine.md)
- [配置与设置](07-settings-and-config.md)
- [内置 Provider 参考](/references/built-in-providers.md)
