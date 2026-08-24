---
type: Concept
title: 模型层架构
description: IChatModel 接口、AbstractChatModel 抽象类、InputModel 和 IChatContext 的设计与使用
tags: [model, architecture, typescript, core]
sources:
  - id: model-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/model.ts
    title: model.ts
  - id: input-model-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/input-model.ts
    title: input-model.ts
  - id: message-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/message.ts
    title: message.ts
  - id: context-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/context.ts
    title: context.ts
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 模型层架构

模型层是 jupyter-chat 的状态管理核心，负责消息管理、用户状态、配置、未读计数和写作状态。

## 核心接口关系

```
┌─────────────────────────────────────────────────────┐
│                    IChatModel                       │
│  (接口 - 定义所有聊天模型的契约)                      │
│  - 消息操作: sendMessage, messageAdded, ...         │
│  - 状态属性: messages, config, user, writers, ...   │
│  - 信号: messagesUpdated, configChanged, ...        │
└─────────────────────┬───────────────────────────────┘
                      │ implements
          ┌───────────┴───────────┐
          │                       │
┌─────────▼──────────┐  ┌────────▼─────────┐
│ AbstractChatModel  │  │  LabChatModel    │
│ (抽象类 - 通用实现) │  │ (jupyterlab 集成) │
│ - 消息排序/堆叠    │  │ - RTC/WS 适配    │
│ - 未读通知         │  │ - JupyterLab 集成│
│ - 写作状态管理     │  └──────────────────┘
│ - localStorage 持久化│
└─────────┬──────────┘
          │ owns
┌─────────▼──────────┐
│     InputModel     │
│  (输入状态管理)     │
│  - value/cursor    │
│  - attachments     │
│  - mentions        │
│  - send/cancel     │
└────────────────────┘
```

## IChatModel 接口

`IChatModel` 定义了聊天模型的完整契约：[^model-ts]

### 状态属性

```typescript
interface IChatModel extends IDisposable {
  // 标识
  id?: string;
  name: string;

  // 配置
  config: IConfig;

  // 消息
  messages: IMessage[];
  unreadMessages: number[];

  // 用户
  user?: IUser;
  writers: IChatModel.IWriter[];

  // 集成
  activeCellManager: IActiveCellManager | null;
  selectionWatcher: ISelectionWatcher | null;
  documentManager: IDocumentManager | null;

  // 输入
  input: IInputModel;

  // RTC
  awareness?: IAwareness;
  messagesInViewport?: number[];

  // 生命周期
  ready: Promise<string>;
}
```

### 响应式信号

模型通过 Lumino `ISignal` 发射状态变更事件，UI 组件订阅这些信号更新界面：

```typescript
// 消息列表变更
messagesUpdated: ISignal<IChatModel, void>;

// 配置变更（如 sendWithShiftEnter 切换）
configChanged: ISignal<IChatModel, void>;

// 单条消息变更（编辑/删除）
messageChanged: ISignal<IChatModel, IMessage>;

// 未读消息变更
unreadChanged?: ISignal<IChatModel, number[]>;

// 视口内消息变更
viewportChanged?: ISignal<IChatModel, number[]>;

// 正在输入的用户变更
writersChanged?: ISignal<IChatModel, IChatModel.IWriter[]>;
```

## AbstractChatModel

`AbstractChatModel` 提供了 `IChatModel` 的通用实现，自定义模型应继承此类。[^model-ts]

### 默认配置

```typescript
constructor(options: IChatModel.IOptions) {
  this._config = {
    sendTypingNotification: true,
    stackMessages: true,
    ...options.config
  };
  this._input = new InputModel({ onSend: this.sendMessage.bind(this) });
}
```

### 消息管理

#### 添加消息

`messageAdded(content)` 是内部方法，按时间排序插入消息：

```typescript
messageAdded(message: IMessageContent): void {
  // 按 time 字段找到插入位置
  const index = this._messages.findIndex(m => m.time > message.time);
  const insertAt = index === -1 ? this._messages.length : index;
  this.messagesInserted(insertAt, [message]);
}
```

#### 消息堆叠

当 `config.stackMessages=true` 时，同一发送者的连续消息自动堆叠（不显示重复头像和用户名）：

```typescript
messagesInserted(index: number, messages: IMessageContent[]): void {
  const newMessages = messages.map(content => {
    const msg = new Message(content);
    // 前一条消息的发送者相同且时间差在阈值内 → 堆叠
    if (this._config.stackMessages && previousSender === msg.sender.username) {
      msg.stacked = true;
    }
    return msg;
  });
  this._messages.splice(index, 0, ...newMessages);
  this._markUnread(newMessages);
}
```

#### 未读消息追踪

未读消息索引存储在内存中，"已读位置"通过 localStorage 持久化：

```typescript
// key: "@jupyter/chat:${this.id}"
// value: 最后已读消息的时间戳
private _lastRead: number;
```

新消息到达时，如果聊天面板不在视口中，消息索引加入 `unreadMessages` 数组，并通过 JupyterLab 通知系统发送通知。

### 写作状态管理

```typescript
setWritingStatus(user: IUser, status?: IWritingStatus, timeout?: number): void {
  // 添加/更新写作用户
  this._writers.set(user.username, { user, ...status });

  // 可选超时，超时后自动清除
  if (timeout) {
    setTimeout(() => this.clearWritingStatus(user), timeout);
  }

  this.writersChanged.emit(Array.from(this._writers.values()));
}
```

### 消息编辑

模型支持内联编辑消息：

```typescript
getEditionModel(messageID: string): IInputModel | undefined;
addEditionModel(messageID: string, inputModel: IInputModel): void;
getEditionModels(): Map<string, IInputModel>;
```

每条被编辑的消息关联一个独立的 `InputModel` 实例。

## Message 类

`Message` 包装 `IMessageContent`，提供变更通知和渲染委托：[^message-ts]

```typescript
class Message implements IMessage {
  constructor(content: IMessageContent);

  // 所有 content 属性通过 getter 暴露
  readonly body, id, time, sender, attachments, mentions, deleted, edited, stacked, ...

  // 消息内容变更时发射
  readonly changed: ISignal<this, void>;

  // 渲染完成通知（支持异步渲染，如 Markdown）
  readonly renderedDelegate: PromiseDelegate<void>;

  update(content: IMessageContent): void;
}
```

**关键机制**：`update()` 方法检测到 `body`/`deleted`/`mentions`/`mime_model` 变化时重置 `renderedDelegate`，触发 UI 重新渲染。

## InputModel

`InputModel` 独立管理输入框状态，不依赖具体 UI 框架。[^input-model-ts]

### 状态属性

```typescript
class InputModel implements IInputModel {
  value: string;              // 输入文本
  cursorIndex: number | null; // 光标位置
  currentWord: string | null; // 光标所在词（@mention 检测）
  attachments: IAttachment[]; // 待发送附件
  mentions: IUser[];          // 待发送的 @提及
  metadata: Record<string, any>; // 扩展元数据
  config: { sendWithShiftEnter, sendWithSelection };
}
```

### 核心方法

#### 发送消息

```typescript
send(): void {
  const message: INewMessage = {
    body: this.value,
    attachments: this._attachments,
    mentions: this._mentions,
    metadata: this._metadata
  };
  this._onSend(message);
  // 发送后清空状态
  this.value = '';
  this._attachments = [];
  this._mentions = [];
}
```

#### @mention 支持

```typescript
// 静态方法：检测光标处的词边界
static getCurrentWord(value: string, cursor: number): string | null;

// 替换当前词（用于 @mention 补全）
replaceCurrentWord(word: string, addTrailingSpace?: boolean): void;
```

当输入 `@` 后，`currentWord` 被检测为 `@xxx` 模式，UI 层可显示用户选择下拉框。选中用户后调用 `replaceCurrentWord()` 替换，并将用户加入 `mentions` 数组。

#### 附件管理

```typescript
addAttachment(attachment: IAttachment): void {
  // JSON.stringify 去重
  const attJson = JSON.stringify(attachment);
  const exists = this._attachments.some(a => JSON.stringify(a) === attJson);
  if (!exists) {
    // notebook 类型附件合并相同文件的 cells
    if (attachment.type === 'notebook') { ... }
    this._attachments.push(attachment);
  }
}
```

## IChatContext（只读上下文）

扩展插件不应直接持有 `IChatModel` 引用（避免意外修改），而是使用 `IChatContext` 只读接口：

```typescript
interface IChatContext {
  readonly id: string;
  readonly name: string;
  readonly messages: IMessageContent[];  // 只读内容
  readonly users: IUser[];
  readonly user: IUser | undefined;
  readonly awareness?: IAwareness;
}
```

通过 `model.createChatContext()` 创建。`AbstractChatContext` 提供了基于 Signal 的自动更新实现。

## React Context 桥接

模型层通过 `ChatReactContext`（React Context）向组件树注入 props：[^context-ts]

```tsx
// ChatBody 组件中
<ChatReactContext.Provider value={props}>
  <ChatMessages />
  <ChatInput />
</ChatReactContext.Provider>

// 子组件中使用 hook
function ChatInput() {
  const { model, translator } = useChatContext();
  // ...
}
```

## 相关概念

- [组件层次结构](/concepts/component-hierarchy.md)
- [双传输架构](/concepts/dual-transport.md)
- [扩展点系统](/concepts/extension-points.md)
- [消息生命周期](/concepts/message-lifecycle.md)
- [Model API 参考](/references/api-model.md)

[^context-ts]: context.ts
[^input-model-ts]: input-model.ts
[^message-ts]: message.ts
[^model-ts]: model.ts
