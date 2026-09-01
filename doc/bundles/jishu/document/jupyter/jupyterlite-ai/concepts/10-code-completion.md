---
type: Concept
title: 代码补全系统
description: jupyterlite-ai 的 AI 驱动行内代码补全功能，基于 IInlineCompletionProvider 接口，支持 FIM（Fill-In-the-Middle）和 Notebook 上下文感知
tags: [jupyterlite-ai, code-completion, inline-completer, fim, ai-coding]
generated: { by: "ai:trae-claude", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: completion
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
  - id: tokens
    resource: /references/tokens-api.md
    title: Token 与核心接口 API 参考
---

# 代码补全系统

jupyterlite-ai 提供 AI 驱动的行内代码补全功能（Inline Completion），在 Notebook 和代码编辑器中，用户输入代码时 AI 自动生成续写建议，按 Tab 键即可接受。

## 核心组件

代码补全功能由 `@jupyternaut/persona` 包中的 `AICompletionProvider` 类实现：

| 组件 | 文件 | 职责 |
|------|------|------|
| `AICompletionProvider` | `packages/persona/src/completion/completion-provider.ts` | 实现 `IInlineCompletionProvider` 接口，处理补全请求 |
| `ICompletionProvider` 入口 | `packages/persona/src/completion/index.ts` | 导出补全模块 |
| Provider 配置 | `packages/persona/src/models/settings-model.ts` | 管理补全 Provider 的配置和选择 |
| `createCompletionModel` | `packages/agent/src/providers/provider-registry.ts` | 创建用于补全的 LanguageModel 实例 |

## IInlineCompletionProvider 实现

`AICompletionProvider` 实现了 JupyterLab 的 `IInlineCompletionProvider` 接口：

```typescript
class AICompletionProvider implements IInlineCompletionProvider {
  readonly identifier = '@jupyternaut/persona:completer';

  get name(): string {
    // 返回当前补全提供商名称，如 "openai-completer"
    const activeProvider = this._settingsModel.getCompleterProvider();
    return activeProvider ? `${activeProvider.provider}-completer` : 'none';
  }

  async fetch(
    request: CompletionHandler.IRequest,
    context: IInlineCompletionContext
  ): Promise<IInlineCompletionList> {
    // 核心方法：根据光标位置和上下文请求补全
  }
}
```

## 补全工作流程

```
用户输入代码触发补全
  → JupyterLab completer 调用 AICompletionProvider.fetch()
    → 提取光标前后的代码（prefix/suffix）
    → 判断当前环境（Notebook 或文件编辑器）
    → 构建补全 Prompt：
        ├─ Notebook 模式：提取上下单元格内容构建上下文
        └─ 文件模式：使用 prefix + 可选 FIM 格式
    → 调用 Vercel AI SDK generateText() 获取补全
    → 清理结果（移除 FIM 标签、代码块标记）
    → 返回 IInlineCompletionList（insertText）
      → JupyterLab 显示灰色 Ghost Text 建议
        → 用户按 Tab 接受，按 Esc 拒绝
```

## 两种补全上下文模式

### 1. Notebook 上下文模式

当补全发生在 Notebook 中时（`context.widget instanceof NotebookPanel`），AICompletionProvider 会提取丰富的上下文：

- **上方单元格（cellsAbove）**：遍历当前单元格之前的所有代码单元格，将其内容作为上下文
- **当前单元格（current cell）**：光标前的代码（prefix）和光标后的代码（suffix）
- **下方单元格（cellsBelow）**：当前单元格之后的代码单元格内容

构建的 Prompt 格式：

```
# Code before cursor:
# Cell 1:
[上方单元格代码]

# Cell 2:
[当前单元格光标前的代码]

# Complete the code at cursor position

# Code after cursor:
[当前单元格光标后的代码]

# Cells below:
# Cell 1:
[下方单元格代码]
```

### 2. 文件编辑器模式

对于普通文件编辑器，使用更简洁的策略：

- **基础模式**：直接使用光标前的文本作为 prompt
- **FIM（Fill-In-the-Middle）模式**：当 Provider 支持 FIM 且存在 suffix 时，使用特殊格式：

```
<PRE>{prefix}<SUF>{suffix}<MID>
```

FIM 格式让模型知道需要在 prefix 和 suffix 之间填充代码，提供更准确的补全。

## Provider 补全配置

不同 AI 提供商可以有不同的补全行为配置，通过 `IProviderCompletionConfig` 接口定义：

```typescript
interface IProviderCompletionConfig {
  temperature?: number;           // 补全温度，默认 0.3（比聊天更低，更确定）
  supportsFillInMiddle?: boolean; // 是否支持 FIM 格式
  useFilterText?: boolean;        // 是否设置 filterText 用于排序过滤
}
```

### 默认补全参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `temperature` | 0.3 | 低温度确保补全更确定、更准确 |
| `supportsFillInMiddle` | false | 需 Provider 显式支持 |
| `useFilterText` | false | 通常不需要 |

## 补全模型选择

补全可以使用与聊天不同的模型：

- **独立配置**：通过设置中的 `completerProvider` 配置，可以为补全选择不同的 Provider 和模型
- **共用配置**：设置 `useSameProviderForChatAndCompleter: true` 时，补全使用与聊天相同的 Provider
- **系统提示词**：补全使用独立的 `completionSystemPrompt`，与聊天的 `systemPrompt` 分开配置

## 密钥获取流程

补全 Provider 的 API Key 获取与聊天一致：

1. 如果启用了 SecretsManager（`useSecretsManager: true`），从安全存储中获取
2. 否则从设置中直接获取明文 API Key
3. 调用 `createCompletionModel()` 创建 LanguageModel 实例
4. 模型实例缓存到 `_model`，设置变更时自动更新

## 结果后处理

补全结果经过多步清理：

1. **移除 FIM 标签**：`<PRE>`、`<SUF>`、`<MID>` 标记
2. **移除代码块标记**：Markdown 代码块围栏 ` ```language ... ``` `
3. **修剪空白**：去除首尾空白
4. **构造 insertText**：作为最终插入文本
5. **可选 filterText**：用于 JupyterLab completer 的过滤排序

## 补全与聊天的区别

| 特性 | 代码补全 | 聊天 |
|------|---------|------|
| 触发方式 | 自动（输入时触发） | 手动（发送消息） |
| 使用的 SDK 方法 | `generateText()` | `streamText()` + ToolLoop |
| Temperature | 0.3（低，确定性强） | 较高（创造性强） |
| 输出类型 | 纯代码（insertText） | 富文本 Markdown + 工具调用 |
| 上下文 | 单元格/文件内容 | 对话历史 + Notebook |
| 用户交互 | Tab 接受/Esc 拒绝 | 对话式多轮交互 |
| 工具调用 | 不支持 | 支持完整工具循环 |

## 配置选项

在 AI 设置中，与补全相关的配置项：

```typescript
interface IAIConfig {
  // 补全相关
  activeCompleterProvider?: string;       // 补全使用的 Provider ID
  useSameProviderForChatAndCompleter: boolean; // 是否与聊天共用 Provider
  completionSystemPrompt: string;         // 补全的系统提示词
  contextAwareness: boolean;              // 是否启用上下文感知（Notebook 单元格上下文）
}
```

## 相关概念

- [Token 依赖注入系统](02-token-di-system.md)
- [Provider 模型提供商系统](03-provider-system.md)
- [设置与配置系统](07-settings-and-config.md)
- [Chat UI 交互](09-chat-ui.md)
- [插件架构参考](../references/plugin-architecture.md)
