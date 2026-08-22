---
type: Concept
title: 配置与设置
description: jupyterlite-ai 的配置模型 IAISettingsModel 管理 Provider、API Key、系统提示词、工具开关、审批策略和技能路径等所有运行时配置
tags: [jupyterlite-ai, settings, configuration, api-key]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: tokens
    resource: /references/tokens-api.md
    title: Token 与核心接口 API 参考
---

# 配置与设置

jupyterlite-ai 通过 `IAISettingsModel` 统一管理所有运行时配置，包括 AI Provider、API Key、模型参数、工具开关、审批策略等。配置通过 JupyterLab 设置系统持久化，API Key 通过 SecretsManager 安全存储。

## IAISettingsModel 接口

```typescript
interface IAISettingsModel extends VDomRenderer.IModel {
  readonly config: IAIConfig;
  updateConfig(updates: Partial<IAIConfig>): Promise<void>;
  readonly providers: IProviderConfig[];
  getProvider(id: string): IProviderConfig | undefined;
  getDefaultProvider(): IProviderConfig | undefined;
  getCompleterProvider(): IProviderConfig | undefined;
  addProvider(providerConfig: Omit<IProviderConfig, 'id'>): Promise<string>;
  removeProvider(id: string): Promise<void>;
  updateProvider(id: string, updates: Partial<IProviderConfig>): Promise<void>;
  setActiveProvider(id: string): Promise<void>;
  setActiveCompleterProvider(id: string | undefined): Promise<void>;
  getApiKey(id: string): string;
}
```

设置模型继承自 `VDomRenderer.IModel`，通过 `stateChanged` 信号通知配置变更。

## IAIConfig 完整配置

```typescript
interface IAIConfig {
  // Provider 配置
  useSecretsManager: boolean;                     // 是否使用 SecretsManager 存储 API Key
  providers: IProviderConfig[];                   // 所有已配置的 Provider 列表
  defaultProvider: string;                        // 默认聊天 Provider ID
  activeCompleterProvider?: string;               // 代码补全 Provider ID（可选）
  useSameProviderForChatAndCompleter: boolean;    // 聊天和补全使用同一 Provider

  // 全局行为
  contextAwareness: boolean;                      // 启用上下文感知（当前单元格/文件内容）
  codeExecution: boolean;                         // 启用代码执行
  systemPrompt: string;                           // 自定义系统提示词
  completionSystemPrompt: string;                 // 代码补全系统提示词
  toolsEnabled: boolean;                          // 全局工具开关

  // 安全与审批
  commandsRequiringApproval: string[];            // 需要用户审批的命令 ID 列表
  commandsAutoRenderMimeBundles: string[];        // 自动渲染 MIME 输出的命令
  trustedMimeTypesForAutoRender: string[];        // 信任的 MIME 类型

  // Diff 显示
  showCellDiff: boolean;                          // 显示 Cell Diff
  showFileDiff: boolean;                          // 显示 File Diff
  diffDisplayMode: 'split' | 'unified';           // Diff 显示模式

  // 技能
  skillsPaths: string[];                          // 技能搜索路径
}
```

## IProviderConfig 单个 Provider 配置

```typescript
interface IProviderConfig {
  id: string;                           // 唯一 ID（UUID）
  name: string;                         // 用户可见名称
  provider: string;                     // ProviderRegistry 中的 Provider 类型 ID
  model: string;                        // 选中的模型名
  apiKey?: string;                      // API Key（可能为 SECRETS_REPLACEMENT 占位符）
  baseURL?: string;                     // 自定义 Base URL
  headers?: Record<string, string>;     // 自定义 HTTP Headers
  parameters?: IProviderParameters;     // 模型参数
  customSettings?: Record<string, any>; // 扩展自定义设置
  [key: string]: any;                   // 索引签名，兼容任意设置
}

interface IProviderParameters {
  temperature?: number;           // 温度（创造性）
  maxOutputTokens?: number;       // 最大输出 token
  maxTurns?: number;              // 最大 tool call 轮次
  contextWindow?: number;         // 覆盖默认上下文窗口
  supportsFillInMiddle?: boolean; // 是否支持 Fill-In-Middle（代码补全）
  useFilterText?: boolean;        // 使用文本过滤
}
```

## API Key 安全存储

API Key 不直接存储在 JupyterLab 设置文件中（JSON 明文），而是通过 `jupyter-secrets-manager` 加密存储：

```
用户输入 API Key
  → 设置面板
    → 如果 useSecretsManager=true:
      → secretsManager.set(token, SECRETS_NAMESPACE, providerId, {value: apiKey})
      → 配置中保存 SECRETS_REPLACEMENT ('***') 占位符
    → 否则:
      → 直接保存在设置中（不推荐）

读取 API Key:
  → getApiKey(providerId)
    → 优先从 SecretsManager 获取
    → 回退到配置中的 apiKey 字段
```

SecretsManager 通过 `SecretsManager.sign()` 颁发 token，只有签名插件才能访问密钥命名空间。

## 设置面板 UI

用户通过 `AISettingsWidget` 配置 AI 设置，可通过以下方式打开：

1. 聊天面板工具栏的设置按钮（齿轮图标）
2. 命令面板："Jupyternaut Settings"
3. 命令：`@jupyternaut/persona:open-settings`

设置面板包含：
- Provider 管理（添加/删除/编辑 Provider）
- API Key 输入（密码框，自动绑定 SecretsManager）
- 模型选择下拉列表
- Base URL / Headers 配置（支持的 Provider）
- 系统提示词编辑
- 工具启用开关
- 需要审批的命令列表
- 技能路径配置
- MCP 服务器配置（通过 `jupyter-mcp-manager` 渲染器）
- 代码补全 Provider 选择

## 默认值与初始化

`AISettingsModel` 在首次创建时使用合理默认值：

```typescript
// 默认配置（源码参考）
{
  useSecretsManager: true,
  providers: [],  // 初始无配置，引导用户添加
  defaultProvider: '',
  useSameProviderForChatAndCompleter: true,
  contextAwareness: true,
  codeExecution: true,
  toolsEnabled: true,
  commandsRequiringApproval: [],  // 默认无审批（信任内置命令）
  showCellDiff: true,
  showFileDiff: true,
  diffDisplayMode: 'split',
  skillsPaths: [],
  systemPrompt: '',  // 使用内置默认
  // ...
}
```

首次使用时，如果未配置任何 Provider，打开聊天会提示设置 Provider 并自动打开设置面板。

## 配置变更传播

配置变更通过信号链自动传播到所有组件：

```
用户修改设置
  → IAISettingsModel.updateConfig()
    → stateChanged 信号
      → AgentManagerFactory._onSettingsChanged
        → 重新初始化所有 AgentManager（新模型/工具/提示词生效）
      → ChatToolbar
        → 更新工具/模型选择按钮状态
      → SkillsPlugin
        → 如果 skillsPaths 变更，重新加载技能
      → AICompletionProvider
        → 更新补全模型配置
      → SidePanel
        → 更新聊天列表
```

## 代码补全配置

代码补全可以使用独立于聊天的 Provider：

- `useSameProviderForChatAndCompleter: true`：补全跟随聊天 Provider
- `useSameProviderForChatAndCompleter: false`：通过 `activeCompleterProvider` 单独指定

代码补全 Provider 的 `parameters.supportsFillInMiddle` 需要正确设置以支持 FIM（Fill-In-Middle）补全模式。

## 配置持久化

配置通过 JupyterLab 的 `ISettingRegistry` 持久化：

```typescript
// settings-model.ts 中
constructor({ settingRegistry }) {
  this._settings = await settingRegistry.load(SETTINGS_PLUGIN_ID);
  this._loadConfig();  // 从设置加载配置
  this._settings.changed.connect(this._onSettingsChanged, this);
}
```

设置存储在 JupyterLab 用户配置目录中（通常是 `~/.jupyter/lab/user-settings/`）。

## 相关概念

- [Provider 模型管理](03-provider-system.md)
- [Token 依赖注入系统](02-token-di-system.md)
- [代码补全](10-code-completion.md)
