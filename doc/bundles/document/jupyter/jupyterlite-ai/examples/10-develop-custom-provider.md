---
type: Example
title: "开发自定义模型提供商"
description: "为 JupyterLite AI 添加自定义 AI 模型提供商，支持新的 LLM 服务"
tags: [jupyterlite-ai, developer, custom-provider, llm, integration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: source
    resource: /references/source-code.md
    title: 源码结构与核心文件索引
  - id: tokens
    resource: /references/tokens-api.md
    title: Token 与核心接口 API 参考
  - id: providers
    resource: /references/built-in-providers.md
    title: 内置 AI Provider 配置参考
---

# 开发自定义模型提供商

本指南介绍如何通过 JupyterLab 扩展为 JupyterLite AI 添加自定义 AI 模型提供商，以支持新的 LLM 服务或私有部署模型。

## 前置条件

- 熟悉 Vercel AI SDK 的 Provider 接口
- 了解目标 LLM API 的格式（OpenAI 兼容或自定义）
- TypeScript 开发环境
- JupyterLab 4.x 扩展开发基础

## Provider 接口

JupyterLite AI 使用 Vercel AI SDK 的 Language Model 接口。自定义 Provider 需要返回符合该接口的模型实例。

## 开发步骤

### 1. 创建扩展并添加依赖

```json
{
  "dependencies": {
    "@jupyternaut/agent": "^0.19.0",
    "ai": "^3.0.0",
    "zod": "^3.0.0"
  }
}
```

### 2. 定义 Provider Factory

```typescript
// src/providers/my-provider.ts
import type { LanguageModel } from 'ai';
import type { IProviderFactory } from '@jupyternaut/agent';

export interface MyProviderSettings {
  apiKey: string;
  baseUrl?: string;
  model: string;
}

/**
 * 创建自定义 Provider 的工厂函数
 * 返回一个 Vercel AI SDK 兼容的 LanguageModel
 */
export function createMyProvider(
  settings: MyProviderSettings
): LanguageModel {
  const { apiKey, baseUrl, model } = settings;

  // 方式1：如果你的服务兼容 OpenAI API 格式
  // 直接使用 Vercel AI SDK 的 createOpenAI 工厂
  const { createOpenAI } = require('@ai-sdk/openai');
  const provider = createOpenAI({
    apiKey,
    baseURL: baseUrl ?? 'https://api.my-provider.com/v1',
  });
  return provider(model);

  // 方式2：如果是完全自定义的 API
  // 需要实现 LanguageModel 接口
  // return new MyCustomLanguageModel(apiKey, baseUrl, model);
}
```

### 3. 注册到 IProviderRegistry

```typescript
// src/index.ts
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from '@jupyterlab/application';
import { IProviderRegistry } from '@jupyternaut/agent';
import { createMyProvider } from './providers/my-provider';

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@my-org/my-custom-provider',
  autoStart: true,
  requires: [IProviderRegistry],
  activate: (app: JupyterFrontEnd, providerRegistry: IProviderRegistry) => {
    providerRegistry.registerProvider('my-provider', {
      id: 'my-provider',
      name: 'My Provider',
      description: 'My custom LLM provider',

      // 设置字段定义（决定设置面板显示什么配置项）
      settingsSchema: {
        type: 'object',
        properties: {
          apiKey: {
            type: 'string',
            title: 'API Key',
            description: '你的 My Provider API Key',
          },
          baseUrl: {
            type: 'string',
            title: 'Base URL',
            description: 'API 端点地址（可选）',
            default: 'https://api.my-provider.com/v1',
          },
          model: {
            type: 'string',
            title: 'Model',
            description: '模型名称',
            default: 'my-model-v1',
          },
        },
        required: ['apiKey', 'model'],
      },

      // 工厂函数：根据设置创建 LanguageModel
      factory: (settings) => createMyProvider(settings),

      // 可选：默认模型列表
      defaultModels: [
        { id: 'my-model-v1', name: 'My Model V1' },
        { id: 'my-model-v2', name: 'My Model V2' },
      ],

      // 可选：能力声明
      capabilities: {
        toolCalling: true,      // 是否支持工具调用
        streaming: true,        // 是否支持流式输出
        structuredOutput: false, // 是否支持结构化输出
      },
    });

    console.log('My custom provider registered!');
  },
};

export default plugin;
```

### 4. 添加设置 Schema（Python 端）

如果需要通过 pip 安装并在 JupyterLab 设置系统中识别，还需要在 Python 包中添加 JSON Schema：

```python
# my_provider/_schema.py
MY_PROVIDER_SCHEMA = {
    "my-provider": {
        "type": "object",
        "properties": {
            "apiKey": {"type": "string", "title": "API Key"},
            "baseUrl": {"type": "string", "title": "Base URL", "default": "https://api.my-provider.com/v1"},
            "model": {"type": "string", "title": "Model", "default": "my-model-v1"},
        },
        "required": ["apiKey", "model"],
    }
}
```

## IProviderRegistry 接口

```typescript
interface IProviderRegistry {
  registerProvider(id: string, provider: IProviderFactory): void;
  unregisterProvider(id: string): void;
  getProvider(id: string): IProviderFactory | undefined;
  getProviders(): Record<string, IProviderFactory>;
  providersChanged: ISignal<this, void>;
}

interface IProviderFactory {
  id: string;
  name: string;
  description?: string;
  settingsSchema: object;          // JSON Schema for settings
  factory: (settings: any) => LanguageModel;
  defaultModels?: Array<{ id: string; name: string }>;
  capabilities?: {
    toolCalling?: boolean;
    streaming?: boolean;
    structuredOutput?: boolean;
    webSearch?: boolean;
    webFetch?: boolean;
  };
}
```

## 适配不同 API 格式

### OpenAI 兼容 API

最简单的情况——使用 `@ai-sdk/openai`：

```typescript
import { createOpenAI } from '@ai-sdk/openai';

factory: (settings) => {
  const openai = createOpenAI({
    apiKey: settings.apiKey,
    baseURL: settings.baseUrl,
  });
  return openai(settings.model);
}
```

适用于：Ollama、LM Studio、vLLM、Together AI、Fireworks、Groq、Mistral API（兼容模式）等。

### Anthropic 兼容 API

使用 `@ai-sdk/anthropic`：

```typescript
import { createAnthropic } from '@ai-sdk/anthropic';

factory: (settings) => {
  const anthropic = createAnthropic({
    apiKey: settings.apiKey,
    baseURL: settings.baseUrl,
  });
  return anthropic(settings.model);
}
```

### Google Generative AI

使用 `@ai-sdk/google`：

```typescript
import { createGoogleGenerativeAI } from '@ai-sdk/google';

factory: (settings) => {
  const google = createGoogleGenerativeAI({
    apiKey: settings.apiKey,
  });
  return google(settings.model);
}
```

### 完全自定义 API

需要自己实现 `LanguageModel` 接口，参考 Vercel AI SDK 文档：
- 实现 `doGenerate` 方法（非流式）
- 实现 `doStream` 方法（流式）
- 处理工具调用格式
- 映射请求/响应格式

## 测试 Provider

1. 构建并安装扩展：
```bash
jlpm build
pip install -e .
jupyter labextension develop . --overwrite
```

2. 启动 JupyterLab，打开 AI 设置面板
3. 确认你的 Provider 出现在下拉列表中
4. 配置 API Key 和模型，发送测试消息
5. 验证工具调用和流式输出正常工作

## 常见问题

**Q: Provider 没有出现在列表中？**
→ 检查插件是否正确加载（查看 JupyterLab 控制台日志），确认 `IProviderRegistry` 依赖注入成功。

**Q: 工具调用不工作？**
→ 确认 `capabilities.toolCalling` 设为 `true`，且底层模型实际支持工具调用。

**Q: 流式输出中断？**
→ 检查 API 响应的流式格式是否正确，CORS 头是否允许流式响应。
