---
type: Reference
title: Model API 参考
description: AbstractChatModel、IChatModel、InputModel、Message 类的核心 API 参考
tags: [typescript, api, model, reference]
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
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# Model API 参考

本页介绍前端模型层的核心类和接口。

## IChatModel 接口

聊天模型的核心接口，继承 `IDisposable`。[^model-ts]

### 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `id` | `string \| undefined` | 聊天唯一标识 |
| `name` | `string` | 聊天名称 |
| `config` | `IConfig` | 聊天配置 |
| `unreadMessages` | `number[]` | 未读消息索引列表 |
| `ready` | `Promise<string>` | 模型就绪 Promise，resolve 为 chat id |
| `awareness` | `IAwareness \| undefined` | Yjs Awareness 实例（RTC 模式） |
| `messagesInViewport` | `number[] \| undefined` | 视口内消息索引 |
| `user` | `IUser \| undefined` | 当前用户 |
| `messages` | `IMessage[]` | 消息列表 |
| `input` | `IInputModel` | 输入模型 |
| `writers` | `IChatModel.IWriter[]` | 正在输入的用户列表 |
| `activeCellManager` | `IActiveCellManager \| null` | 活动单元格管理器 |
| `selectionWatcher` | `ISelectionWatcher \| null` | 选择监听器 |
| `documentManager` | `IDocumentManager \| null` | 文档管理器 |

### 信号（Lumino ISignal）

| 信号 | 负载类型 | 触发时机 |
|---|---|---|
| `messagesUpdated` | `void` | 消息列表更新 |
| `configChanged` | `void` | 配置变更 |
| `unreadChanged` | `number[]` | 未读消息变更 |
| `viewportChanged` | `number[]` | 视口消息变更 |
| `writersChanged` | `IChatModel.IWriter[]` | 输入用户变更 |
| `messageChanged` | `IMessage` | 单条消息变更（编辑/删除） |
| `messageEditionAdded` | `IInputModel` | 新增消息编辑 |

### 方法

| 方法 | 参数 | 返回 | 说明 |
|---|---|---|---|
| `sendMessage` | `message: INewMessage` | `void` | **抽象方法**，发送消息 |
| `clearMessages` | - | `void` | 清空所有消息 |
| `updateMessage` | `id: string, message: IMessageContent` | `void` | 更新消息（可选实现） |
| `deleteMessage` | `id: string` | `void` | 删除消息（可选实现） |
| `messageAdded` | `message: IMessageContent` | `void` | 添加消息（内部使用） |
| `messagesInserted` | `index: number, messages: IMessageContent[]` | `void` | 批量插入消息 |
| `messagesDeleted` | `index: number, count: number` | `void` | 删除消息 |
| `setWritingStatus` | `user: IUser, status?, timeout?` | `void` | 设置用户输入状态 |
| `clearWritingStatus` | `user: IUser` | `void` | 清除用户输入状态 |
| `createChatContext` | - | `IChatContext` | **抽象方法**，创建只读上下文 |
| `getEditionModel` | `messageID: string` | `IInputModel \| undefined` | 获取消息编辑模型 |

## AbstractChatModel 抽象类

实现了 `IChatModel` 的大部分功能，是自定义模型的基类。[^model-ts]

### 构造函数

```typescript
constructor(options: IChatModel.IOptions)
```

`IChatModel.IOptions` 包含：
- `config?: Partial<IConfig>` - 初始配置
- `model: { sharedModel: YChat }` - 共享模型（RTC 模式）或其他配置

### 默认行为

- 默认配置：`stackMessages: true`, `sendTypingNotification: true`
- 未读消息使用 localStorage 持久化，key 为 `@jupyter/chat:${id}`
- 消息按 `time` 字段排序插入
- 同一发送者的连续消息在 `stackMessages=true` 时设置 `stacked=true`
- 新消息到达时通过 `_notify()` 发送 JupyterLab 通知

## InputModel 类

管理输入框状态，实现 `IInputModel`。[^input-model-ts]

### 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `value` | `string` | 输入框文本 |
| `cursorIndex` | `number \| null` | 光标位置 |
| `currentWord` | `string \| null` | 光标所在词（用于 @mention） |
| `attachments` | `IAttachment[]` | 待发送附件 |
| `mentions` | `IUser[]` | 待发送的 @提及 |

### 方法

| 方法 | 说明 |
|---|---|
| `send()` | 发送消息，构造 INewMessage 并调用 onSend 回调 |
| `addAttachment(attachment)` | 添加附件（自动去重，notebook 类型合并 cells） |
| `removeAttachment(index)` | 移除附件 |
| `replaceCurrentWord(word, addTrailingSpace?)` | 替换光标处词（用于 @mention 补全） |
| `updateMetadata(patch)` | 更新元数据（structuredClone 深拷贝浅合并） |
| `focus()` | 聚焦输入框 |
| `cancel()` | 取消编辑 |

### 静态方法

```typescript
// 获取光标所在词的边界
static getCurrentWordBoundaries(value: string, cursor: number): { start: number, end: number, word: string } | null
static getCurrentWord(value: string, cursor: number): string | null
```

## Message 类

实现 `IMessage` 接口，包装 `IMessageContent` 提供更新通知。[^message-ts]

```typescript
class Message implements IMessage {
  constructor(content: IMessageContent);

  // getter 暴露 content 的所有属性
  readonly type, body, id, time, sender, attachments, mentions,
    raw_time, deleted, edited, stacked, metadata, mime_model;

  readonly changed: ISignal<this, void>;
  readonly renderedDelegate: PromiseDelegate<void>;

  update(content: IMessageContent): void;  // 更新内容，body/deleted/mentions/mime_model 变化时重置 renderedDelegate
}
```

## IChatContext 接口

`IChatModel` 的只读子集，供扩展使用：[^model-ts]

```typescript
interface IChatContext {
  readonly id: string;
  readonly name: string;
  readonly messages: IMessageContent[];
  readonly users: IUser[];
  readonly user: IUser | undefined;
  readonly awareness?: IAwareness;
}
```

[^input-model-ts]: input-model.ts
[^message-ts]: message.ts
[^model-ts]: model.ts
