---
type: Concept
title: Token 依赖注入系统
description: jupyterlite-ai 使用 Lumino Token 实现类型安全的依赖注入，所有核心服务通过 Token 暴露和消费
tags: [jupyterlite-ai, token, di, lumino, plugin]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: tokens
    resource: /references/tokens-api.md
    title: Token 与核心接口 API 参考
  - id: plugins
    resource: /references/plugin-architecture.md
    title: JupyterLab 插件架构参考
---

# Token 依赖注入系统

jupyterlite-ai 基于 Lumino 的 `Token` 机制实现依赖注入（DI）。这是 JupyterLab 生态的标准模式，实现了插件间的类型安全解耦。

## Token 基本原理

Lumino Token 是一个泛型类，将服务接口类型绑定到唯一的符号标识符：

```typescript
import { Token } from '@lumino/coreutils';

// 定义 Token，绑定接口类型
export const IToolRegistry = new Token<IToolRegistry>(
  '@jupyternaut/agent:IToolRegistry',
  'Tool registry for AI agent functionality'
);
```

Token 的构造函数接收两个参数：
1. **唯一标识符**：通常使用 `包名:接口名` 格式，确保全局唯一
2. **描述文本**：用于开发者文档和调试

## 核心 Token 列表

| Token 常量 | 接口 | 提供插件 | 描述 |
|-----------|------|---------|------|
| `IProviderRegistry` | `IProviderRegistry` | `persona:provider-registry` | AI 模型 Provider 注册表 |
| `IToolRegistry` | `IToolRegistry` | `persona:tool-registry` | AI 工具注册表 |
| `ISkillRegistry` | `ISkillRegistry` | `persona:skill-registry` | AI 技能注册表 |
| `IAISettingsModel` | `IAISettingsModel` | `persona:settings-model` | AI 配置设置模型 |
| `IAgentManagerFactory` | `IAgentManagerFactory` | `persona:<secrets>` | Agent 管理器工厂 |
| `IDiffManager` | `IDiffManager` | `persona:diff-manager` | Diff 显示管理器 |
| `IChatModelHandler` | `IChatModelHandler` | `ai:chat-model-handler` | 聊天模型创建处理器 |
| `IChatToolbarFactory` | `ChatToolbarFactory` | `ai:chat-toolbar-factory` | 聊天工具栏工厂 |

## 插件中的使用方式

JupyterFrontEndPlugin 通过 `requires` 和 `optional` 数组声明依赖，JupyterLab 在激活插件时自动注入：

```typescript
const myPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:my-plugin',
  autoStart: true,
  // 必需依赖：如果这些 Token 没有提供者，插件不会激活
  requires: [IProviderRegistry, IAISettingsModel],
  // 可选依赖：可能不存在，不影响插件激活
  optional: [IToolRegistry, ISecretsManager],
  activate: (
    app: JupyterFrontEnd,
    providerRegistry: IProviderRegistry,    // 按 requires 顺序注入
    settingsModel: IAISettingsModel,
    toolRegistry?: IToolRegistry,          // 可选依赖可能为 undefined
    secretsManager?: ISecretsManager
  ) => {
    // 使用注入的服务
    if (toolRegistry) {
      toolRegistry.add('my_tool', myTool);
    }
  }
};
```

## 提供服务（provides）

插件通过 `provides` 字段声明自己提供某个 Token 的实现：

```typescript
const toolRegistryPlugin: JupyterFrontEndPlugin<IToolRegistry> = {
  id: '@jupyternaut/persona:tool-registry',
  autoStart: true,
  provides: IToolRegistry,  // 声明本插件提供 IToolRegistry
  optional: [ISkillRegistry],
  activate: (app, skillRegistry?: ISkillRegistry): IToolRegistry => {
    const toolRegistry = new ToolRegistry();
    // 注册内置工具
    toolRegistry.add('discover_commands', createDiscoverCommandsTool(app.commands));
    toolRegistry.add('execute_command', createExecuteCommandTool(app.commands));
    toolRegistry.add('browser_fetch', createBrowserFetchTool());
    if (skillRegistry) {
      toolRegistry.add('discover_skills', createDiscoverSkillsTool(skillRegistry));
      toolRegistry.add('load_skill', createLoadSkillTool(skillRegistry));
    }
    return toolRegistry;  // 必须返回 provides 声明类型的实例
  }
};
```

## 依赖解析规则

1. **拓扑排序**：JupyterLab 根据 `requires` 关系拓扑排序激活插件
2. **单例保证**：每个 Token 在应用中只有一个提供者，所有消费者共享同一实例
3. **可选容忍**：`optional` 中的依赖如果不可用，注入 `undefined`
4. **循环依赖检测**：JupyterLab 启动时检测循环依赖并报错

## SecretsManager 特殊 Token

`IAgentManagerFactory` 的创建需要 `SecretsManager.sign()` 包装，这是为了确保 API Key 的安全访问：

```typescript
const agentManagerFactory: JupyterFrontEndPlugin<IAgentManagerFactory> =
  SecretsManager.sign(SECRETS_NAMESPACE, token => {
    // token 是 SecretsManager 颁发的安全令牌
    // 只有持有此 token 的插件才能访问对应命名空间的密钥
    Private.setAISecretsToken(token);
    return {
      id: SECRETS_NAMESPACE,
      autoStart: true,
      provides: IAgentManagerFactory,
      requires: [IAISettingsModel, IProviderRegistry],
      optional: [ISkillRegistry, ICompletionProviderManager, ISecretsManager, IMcpManager],
      activate: (app, settingsModel, providerRegistry, ...) => {
        return new AgentManagerFactory({
          settingsModel,
          secretsManager,
          token,  // 传递安全令牌
          // ...
        });
      }
    };
  });
```

SecretsManager 使用 `sign()` 创建带签名的插件，只有通过签名的插件才能获取有效的 token，进而通过 `secretsManager.get(token, namespace, id)` 访问存储的密钥。

## Token 命名约定

所有 Token 遵循统一命名约定：

- **接口名**：`I` 前缀 + PascalCase（如 `IToolRegistry`）
- **Token 常量名**：与接口名相同（`IToolRegistry`）
- **唯一标识**：`@<package-name>:<InterfaceName>` 格式（如 `@jupyternaut/agent:IToolRegistry`）

## 扩展第三方 Token

自定义扩展可以定义自己的 Token 供其他扩展消费：

```typescript
// 定义自定义 Token
export const IMyService = new Token<IMyService>(
  'my-extension:IMyService'
);

export interface IMyService {
  doSomething(): void;
}

// 提供实现
const myServicePlugin: JupyterFrontEndPlugin<IMyService> = {
  id: 'my-extension:my-service',
  provides: IMyService,
  autoStart: true,
  activate: () => new MyService()
};

// 其他插件消费
const consumerPlugin: JupyterFrontEndPlugin<void> = {
  id: 'other:consumer',
  requires: [IMyService],
  autoStart: true,
  activate: (app, myService) => {
    myService.doSomething();
  }
};
```

## 相关概念

- [架构概览](01-architecture-overview.md)
- [Provider 模型管理](03-provider-system.md)
- [插件架构参考](../references/plugin-architecture.md)
