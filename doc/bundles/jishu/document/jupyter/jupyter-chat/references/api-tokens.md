---
type: Reference
title: Token 与命令参考
description: jupyterlab-chat 提供的 Lumino Token（依赖注入令牌）和命令 ID 参考
tags: [typescript, api, token, command, reference]
sources:
  - id: tokens-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/tokens.ts
    title: tokens.ts
  - id: lab-token-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyterlab-chat/src/token.ts
    title: token.ts (jupyterlab-chat)
  - id: factory-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyterlab-chat/src/factory.ts
    title: factory.ts
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# Token 与命令参考

本页列出 jupyter-chat 提供的所有 Lumino Token（用于依赖注入）和 JupyterLab 命令 ID。

## @jupyter/chat 核心 Token

| Token | ID | 类型 | 说明 |
|---|---|---|---|
| `IChatTracker` | `@jupyter/chat:IChatTracker` | `IWidgetTracker<IChatPanel>` | 聊天面板追踪器，跟踪所有打开的聊天面板 |
| `IChatPlaceholderFactory` | `@jupyter/chat:IChatPlaceholderFactory` | `{ create(props): Widget }` | 占位符组件工厂（空状态显示） |
| `IChatBodyPlaceholderFactory` | `@jupyter/chat:IChatBodyPlaceholderFactory` | `{ create(props): JSX.Element \| null }` | 聊天区域占位符工厂 |

## jupyterlab-chat 集成 Token

| Token | ID | 类型 | 说明 |
|---|---|---|---|
| `IChatFactory` | `jupyterlab-chat:IChatFactory` | `ChatWidgetFactory` | 聊天部件工厂，用于创建新的聊天窗口 |
| `IChatToolbarFactory` | `jupyterlab-chat:IChatToolbarFactory` | `(panel: IChatPanel) => IObservableList<ToolbarItem>` | 工具栏工厂，主区和侧边面板共享 |
| `IWidgetConfig` | `jupyterlab-chat:IWidgetConfig` | `{ config, configChanged }` | 聊天配置对象，传播设置变更到所有部件 |
| `IMultiChatPanel` | `jupyterlab-chat:IMultiChatPanel` | `MultiChatPanel` | 多聊天面板（侧边栏）实例 |
| `IActiveCellManagerToken` | `jupyterlab-chat:IActiveCellManager` | `IActiveCellManager` | 活动单元格管理器，追踪 notebook 当前活动 cell |
| `ISelectionWatcherToken` | `jupyterlab-chat:ISelectionWatcher` | `ISelectionWatcher` | 选择监听器，追踪文件中的文本选择 |
| `IWelcomeMessage` | `jupyterlab-chat:IWelcomeMessage` | `string` | 欢迎消息字符串，第三方扩展可提供自定义欢迎消息 |

## 命令 ID（CommandIDs）

所有命令定义在 `jupyterlab-chat` 包中：[^lab-token-ts]

| 命令 ID | 说明 |
|---|---|
| `jupyterlab-chat:create` | 创建新的 .chat 文件 |
| `jupyterlab-chat:open` | 打开现有聊天文件 |
| `jupyterlab-chat:createAndOpen` | 创建并打开聊天 |
| `jupyterlab-chat:moveChat` | 在主区和侧边面板之间移动聊天 |
| `jupyterlab-chat:markAsRead` | 标记当前聊天为已读 |
| `jupyterlab-chat:focusInput` | 聚焦当前聊天的输入框 |
| `jupyterlab-chat:renameChat` | 重命名当前聊天 |
| `jupyterlab-chat:openWithMessage` | 打开聊天并发送一条消息 |

## 文件类型注册

聊天文件类型通过 `chatFileType` 常量注册：[^lab-token-ts]

```typescript
const chatFileType: DocumentRegistry.IFileType = {
  name: 'chat',
  displayName: 'Chat',
  mimeTypes: ['text/json', 'application/json'],
  extensions: ['.chat'],
  fileFormat: 'text',
  contentType: 'chat',
  icon: chatIcon
};
```

## 工厂类

### ChatWidgetFactory

继承 `ABCWidgetFactory<LabChatPanel, LabChatModel>`，负责创建聊天面板实例。[^factory-ts]

```typescript
class ChatWidgetFactory extends ABCWidgetFactory<LabChatPanel, LabChatModel> {
  constructor(options: ChatWidgetFactory.IOptions<LabChatPanel>);

  // 在 collaborative=true 时返回 'rtc'，启用 jupyter_collaboration 的 RtcContentProvider
  get contentProviderId(): string | undefined;
}
```

### LabChatModelFactory

实现 `DocumentRegistry.IModelFactory<LabChatModel>`：[^factory-ts]

```typescript
class LabChatModelFactory implements DocumentRegistry.IModelFactory<LabChatModel> {
  readonly name = 'chat';
  readonly contentType = 'chat';
  readonly fileFormat = 'text';

  createNew(options: DocumentRegistry.IModelOptions<YChat>): LabChatModel;
}
```

### WidgetConfig

配置管理类，实现 `IWidgetConfig`，通过 `configChanged` 信号传播配置变更到所有已创建的聊天部件：[^factory-ts]

```typescript
class WidgetConfig implements IWidgetConfig {
  constructor(config: Partial<ILabChatConfig>);

  get config(): Partial<ILabChatConfig>;
  set config(value: Partial<ILabChatConfig>);
  get configChanged(): ISignal<WidgetConfig, Partial<ILabChatConfig>>;
}
```

## IChatPanel 接口

```typescript
interface IChatPanel extends Widget {
  widget: ChatWidget;
  model: IChatModel;
  area: ChatArea;       // 'sidebar' | 'main'
  toolbar: Widget;
}
```

[^factory-ts]: factory.ts
[^lab-token-ts]: token.ts
