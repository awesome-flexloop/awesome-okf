---
type: Reference
title: 内置 Provider 参考
description: jupyterlite-ai 内置的 Anthropic、Google、Mistral、OpenAI、Generic 五个 AI Provider 配置
tags: [jupyterlite-ai, providers, reference]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
---

# 内置 Provider 参考

jupyterlite-ai 内置 5 个 AI 模型 Provider，通过 `ProviderRegistry` 注册。每个 Provider 定义了工厂函数、默认模型列表和能力声明。

## Provider 注册表

| Provider ID | 名称 | API Key | 自定义 BaseURL | 工具调用 | Web 搜索 | Web 抓取 |
|------------|------|---------|---------------|---------|---------|---------|
| `anthropic` | Anthropic Claude | 必需 | 支持 | 是 | anthropic 原生 | anthropic 原生 |
| `google` | Google Generative AI | 必需 | 支持 | 是 | 否 | 否 |
| `mistral` | Mistral AI | 必需 | 支持 | 是 | 否 | 否 |
| `openai` | OpenAI | 必需 | 支持 | 是 | openai 原生 | 否 |
| `generic` | Generic (OpenAI-compatible) | 可选 | 支持 | 是 | 否 | 否 |

## Anthropic Provider

```typescript
// Provider ID: 'anthropic'
// 工厂函数使用 @ai-sdk/anthropic 的 createAnthropic
{
  id: 'anthropic',
  name: 'Anthropic Claude',
  apiKeyRequirement: 'required',
  defaultModels: [
    'claude-opus-4-6', 'claude-sonnet-4-6', 'claude-opus-4-5',
    'claude-opus-4-1', 'claude-opus-4-0', 'claude-sonnet-4-0',
    'claude-haiku-4-5'
  ],
  supportsBaseURL: true,
  supportsHeaders: true,
  providerToolCapabilities: {
    webSearch: { implementation: 'anthropic' },
    webFetch: { implementation: 'anthropic' }
  },
  cacheProviderOptions: {
    anthropic: { cacheControl: { type: 'ephemeral' } }
  }
}
```

**特殊 Headers**：Anthropic 浏览器直连需要设置 `'anthropic-dangerous-direct-browser-access': 'true'`。

## Google Provider

```typescript
// Provider ID: 'google'
// 工厂函数使用 @ai-sdk/google 的 createGoogleGenerativeAI
{
  id: 'google',
  name: 'Google Generative AI',
  apiKeyRequirement: 'required',
  defaultModels: [
    'gemini-3.1-pro-preview', 'gemini-3.1-flash-image-preview',
    'gemini-3-pro-image-preview', 'gemini-3-flash-preview',
    'gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.5-flash-lite'
  ],
  supportsBaseURL: true,
  // 默认模型: 'gemini-2.5-flash'
}
```

## Mistral Provider

```typescript
// Provider ID: 'mistral'
// 工厂函数使用 @ai-sdk/mistral 的 createMistral
{
  id: 'mistral',
  name: 'Mistral AI',
  apiKeyRequirement: 'required',
  defaultModels: [
    'mistral-large-latest', 'mistral-medium-latest', 'mistral-small-latest',
    'ministral-3b-latest', 'ministral-8b-latest', 'codestral-latest'
  ],
  supportsBaseURL: true,
  // 默认模型: 'mistral-large-latest'
}
```

## OpenAI Provider

```typescript
// Provider ID: 'openai'
// 工厂函数使用 @ai-sdk/openai 的 createOpenAI
{
  id: 'openai',
  name: 'OpenAI',
  apiKeyRequirement: 'required',
  defaultModels: [
    'gpt-5.4', 'gpt-5.4-mini', 'gpt-5.2', 'gpt-5.1', 'gpt-5',
    'gpt-5-mini', 'o4-mini', 'o3-pro', 'o3', 'o3-mini', 'o1',
    'gpt-4.1', 'gpt-4o', 'gpt-4o-mini'
  ],
  supportsBaseURL: true,
  supportsHeaders: true,
  providerToolCapabilities: {
    webSearch: { implementation: 'openai' }
  },
  // 默认模型: 'gpt-4o'
}
```

## Generic Provider（OpenAI 兼容）

```typescript
// Provider ID: 'generic'
// 工厂函数使用 @ai-sdk/openai-compatible 的 createOpenAICompatible
{
  id: 'generic',
  name: 'Generic (OpenAI-compatible)',
  apiKeyRequirement: 'optional',  // 本地部署可能不需要
  defaultModels: [],  // 用户自定义
  supportsBaseURL: true,
  supportsHeaders: true,
  supportsToolCalling: true,
  description: 'Uses /chat/completions endpoint',
  baseUrls: [
    { url: 'http://localhost:4000', description: 'Default for local LiteLLM server' },
    { url: 'http://localhost:11434/v1', description: 'Default for local Ollama server' }
  ]
  // 默认模型: 'gpt-4o'（作为fallback）
  // API Key 默认值: 'dummy'（空字符串会导致错误）
}
```

Generic Provider 使用 `createOpenAICompatible`，兼容所有实现 OpenAI `/chat/completions` 接口的服务，包括 Ollama、LiteLLM Proxy、vLLM、LocalAI 等。

## 自定义 Provider 注册

第三方扩展可以通过插件机制注册自定义 Provider：

```typescript
import { IProviderRegistry, IProviderInfo } from '@jupyternaut/agent';

const myProviderPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:my-provider',
  autoStart: true,
  requires: [IProviderRegistry],
  activate: (app, providerRegistry: IProviderRegistry) => {
    const myProvider: IProviderInfo = {
      id: 'my-provider',
      name: 'My AI Provider',
      apiKeyRequirement: 'required',
      defaultModels: ['my-model-v1'],
      supportsBaseURL: true,
      factory: (options) => {
        // 返回 Vercel AI SDK LanguageModel 实例
        return myCreateLanguageModel(options);
      }
    };
    providerRegistry.registerProvider(myProvider);
  }
};
```
