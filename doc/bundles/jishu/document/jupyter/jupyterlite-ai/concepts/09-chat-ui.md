---
type: Concept
title: 聊天界面与会话管理
description: jupyterlite-ai 基于 @jupyter/chat 组件实现多面板聊天界面，支持侧边栏/主区域切换、多会话管理、保存/恢复和实时流式响应
tags: [jupyterlite-ai, chat, ui, multi-chat, session]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
  - id: plugins
    resource: /references/plugin-architecture.md
    title: JupyterLab 插件架构参考
---

# 聊天界面与会话管理

jupyterlite-ai 的聊天界面基于 `@jupyter/chat` 包构建，提供侧边栏多会话管理面板和主区域大视图两种模式，支持会话保存/恢复、工具栏操作和聊天命令。

## 界面组件层次

```
JupyterLab Shell
├── Left Area: MultiChatPanel (侧边栏)
│   ├── 聊天列表（可切换/新建/重命名）
│   └── 当前 ChatWidget
│       ├── 消息列表（流式渲染）
│       ├── 工具栏（usage/saveChat）
│       └── 输入区
│           └── InputToolbar（stop/clear/model/tools 按钮）
│
└── Main Area: MainAreaChat（主区域，可选）
    └── ChatWidget（与侧边栏相同组件）
```

## MultiChatPanel 侧边栏

`MultiChatPanel` 是侧边栏的多会话管理容器：

- **聊天列表**：标签页式切换，支持新建、关闭、重命名会话
- **模型选择**：新建聊天时选择使用的 Provider/模型
- **自动创建**：启动时如果没有已恢复的会话且配置了默认 Provider，自动创建一个聊天
- **设置按钮**：打开 AI 设置面板

### 创建新会话

通过 `@jupyterlite/ai:open-chat` 命令创建新聊天：

```typescript
commands.execute(CommandIds.openChat, {
  area: 'sidebar' | 'main',  // 打开位置
  name?: string,             // 会话名称
  provider?: string,         // Provider ID
  input?: string,            // 预填输入
  autoSend?: boolean,        // 是否自动发送
  focus?: boolean            // 是否聚焦输入框
});
```

或使用 `open-or-reveal-chat` 命令打开已存在的会话或创建新会话。

## MainAreaChat 主区域

聊天可以从侧边栏移动到主工作区（和 Notebook 并排）：

- 点击聊天面板工具栏的"移到主区域"按钮
- 或使用 `@jupyterlite/ai:move-chat` 命令
- 主区域聊天支持 split 模式（split-left/split-right/split-top/split-bottom）
- 通过 `@jupyterlite/ai:reposition` 命令调整位置

移动聊天时，底层 `IAIChatModel` 不销毁，只重建 Widget。

## ChatModel 与 ChatModelHandler

`ChatModelHandler` 负责创建和管理聊天模型：

```typescript
interface IChatModelHandler {
  createModel(options: ICreateChatOptions): IAIChatModel;
  activeCellManager: ActiveCellManager | undefined;
}

interface IAIChatModel extends IChatModel {
  readonly nameChanged: ISignal<IAIChatModel, string>;
  title: string | null;
  readonly titleChanged: ISignal<IAIChatModel, string | null>;
  autosave: boolean;
  readonly agentManager: IAgentManager | null;
  readonly tokenUsageChanged: ISignal<IAgentManager, ITokenUsage> | null;
  save(): Promise<void>;
  restore(filepath: string, silent?: boolean): Promise<boolean>;
  requestTitle(): Promise<string>;
  // 队列消息管理
  messageQueue: any[];
  isBusy: boolean;
  removeQueuedMessage(messageId: string): void;
  reorderQueuedMessages(messageIds: string[]): void;
  editQueuedMessage(messageId: string, newBody: string): void;
}
```

`ChatModel` 绑定到一个 `AgentManager` 实例（通过 PersonaRegistry），每个聊天窗口有独立的对话历史和 Agent 上下文。

## 工具栏系统

### 聊天工具栏

每个 ChatWidget 有两级工具栏：

**面板工具栏**（顶部）：
- Token 用量显示（UsageWidget）
- 保存聊天按钮（SaveComponentWidget）
- 移动到主区域/侧边栏按钮

**输入工具栏**（底部输入框旁）：
- `stop`：停止生成（仅 AI 正在输出时显示）
- `clear`：清除对话
- `model`：模型选择下拉
- `tools`：工具选择下拉（toolsEnabled=false 时隐藏）

输入工具栏通过 `InputToolbarRegistry` 管理，支持扩展添加自定义按钮。

### 共享工具栏工厂

`ChatToolbarFactory` 是共享工厂，侧边栏和主区域共用同一套工具栏配置，避免重复注册。通过 `injectAreaArg()` 自动注入当前面板区域参数。

## 聊天命令

支持斜杠命令和 @提及：

| 命令 | 来源 | 功能 |
|------|------|------|
| `/clear` | ClearCommandProvider | 清除当前聊天历史 |
| `/skills [query]` | SkillsCommandProvider | 列出/搜索可用技能 |
| `@` | MentionCommandProvider | @提及 Persona |

聊天命令通过 `IChatCommandRegistry` 注册，第三方扩展可添加自定义命令。

## 会话保存与恢复

### 保存

`save()` 方法将聊天序列化为 JSON 文件：

- 通过 JupyterLab 文件对话框选择保存位置
- 包含消息历史、模型配置、标题、时间戳
- 保存格式兼容 @jupyter/chat 的标准格式

### 恢复

`restore(filepath)` 从 JSON 文件恢复聊天：

- 如果当前会话有消息，提示用户确认覆盖
- 恢复消息历史并重建 Agent 上下文
- 自动加载到当前 ChatWidget

默认备份目录通过 JupyterLab 设置 `chatBackupDirectory` 配置。

## 自动标题生成

`requestTitle()` 方法使用 AI 自动生成聊天标题：

- 在收到 AI 首次回复后自动调用
- 使用 `textResponse()` 发送历史摘要请求轻量级模型生成标题
- 标题通过 `titleChanged` 信号更新到 UI
- 标题用于聊天列表标签和布局恢复

## 布局恢复

通过 `ILayoutRestorer` 支持 JupyterLab 刷新后恢复聊天面板：

```typescript
restorer.add(sidePanel, sidePanel.id);
restorer.restore(tracker, {
  command: CommandIds.openChat,
  args: widget => ({
    name: widget.model.name,
    area: widget instanceof MainAreaChat ? 'main' : 'side',
    provider: widget.model.agentManager?.activeProvider
  }),
  name: widget => `${area}:${widget.model.name}`
});
```

## Persona 绑定

PersonaRegistry 将 Chat Model 映射到 AgentManager：

```typescript
// PersonaRegistry.activate 中
const attachPersona = (widget: IChatPanel) => {
  if (registry.get(widget.model)) return;  // 已绑定则跳过

  const agentManager = agentManagerFactory.createAgent({
    settingsModel,
    providerRegistry,
    toolRegistry
  });

  registry.register(widget.model, agentManager);
  widget.disposed.connect(() => {
    registry.unregister(widget.model);  // 面板关闭时清理
  });
};

// 监听新面板创建
chatTracker?.forEach(widget => attachPersona(widget));
chatTracker?.widgetAdded.connect((_, widget) => attachPersona(widget));
```

每个 ChatWidget 生命周期绑定一个独立 AgentManager，Widget 销毁时 AgentManager 一并清理。

## 活动单元格感知

`ActiveCellManager` 追踪 Notebook 中当前活动的单元格，使 AI 能够：
- 获取当前单元格内容作为上下文
- 支持"将代码复制到单元格"功能
- 通过 `activeCellManager` 属性注入到 ChatModelHandler

## 命令列表

| 命令 ID | 标签 | 功能 |
|---------|------|------|
| `@jupyterlite/ai:open-chat` | Open a chat | 打开新聊天 |
| `@jupyterlite/ai:open-or-reveal-chat` | Open or reveal the chat panel | 打开或显示已有聊天 |
| `@jupyterlite/ai:move-chat` | Move the chat | 在侧边栏和主区域间移动 |
| `@jupyterlite/ai:save-chat` | Save chat | 保存聊天到文件 |
| `@jupyterlite/ai:restore-chat` | Restore chat | 从文件恢复聊天 |
| `@jupyterlite/ai:reposition` | Reposition Widget | 调整主区域聊天位置 |

保存/恢复命令注册到命令面板（AI Assistant 分类）。

## 组件扩展点

通过 `IComponentsRendererFactory` 可以自定义聊天组件渲染：

- `groupedToolCallCallbacks`：工具调用权限决策回调（自定义审批 UI）
- `queueMessageCallbacks`：消息队列操作回调

这允许第三方扩展替换默认的工具审批对话框或消息队列 UI。

## 相关概念

- [架构概览](01-architecture-overview.md)
- [Agent 执行引擎](05-agent-engine.md)
- [代码补全](10-code-completion.md)
