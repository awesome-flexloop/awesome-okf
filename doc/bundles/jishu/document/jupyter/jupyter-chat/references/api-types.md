---
type: Reference
title: 核心类型参考
description: jupyter-chat TypeScript 核心类型定义参考，包含 IUser、IMessageContent、IConfig、IAttachment 等接口
tags: [typescript, api, types, reference]
sources:
  - id: types-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/types.ts
    title: types.ts
  - id: models-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/models.py
    title: models.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 核心类型参考

本页列出 jupyter-chat 前端 TypeScript 和后端 Python 的核心数据类型。

## 用户类型

### IUser（TypeScript）

表示聊天中的用户身份：[^types-ts]

```typescript
interface IUser {
  username: string;           // 必填，用户名（唯一标识）
  name?: string;              // 显示名
  display_name?: string;      // 显示名称（同 name）
  initials?: string;          // 用户名首字母
  color?: string;             // 用户颜色（头像背景色）
  avatar_url?: string;        // 头像 URL
  mention_name?: string;      // @提及名称
  bot?: boolean;              // 是否为机器人
}
```

### User（Python）

Python 后端的用户模型，继承自 `jupyter_server.auth.User`（JupyterUser）：[^models-py]

```python
@dataclass(kw_only=True)
class User(JupyterUser):
    bot: bool = False

    @property
    def mention_name(self) -> str:
        # display_name || name || username，空格替换为 '-'
```

## 消息类型

### IMessageContent（TypeScript）

消息内容的核心接口，泛型参数 T=IUser（发送者类型）, U=IAttachment（附件类型）：[^types-ts]

```typescript
interface IMessageContent<T = IUser, U = IAttachment> {
  type: string;               // 消息类型，默认 "msg"
  body: string;               // 消息正文
  id: string;                 // 消息唯一 ID（UUID）
  time: number;               // 时间戳（Unix 秒）
  sender: T;                  // 发送者
  attachments?: U[];          // 附件列表
  mentions?: T[];             // @提及的用户列表
  raw_time?: boolean;         // 时间戳是否为客户端原始时间
  deleted?: boolean;          // 是否已删除
  edited?: boolean;           // 是否已编辑
  stacked?: boolean;          // 是否与前一消息堆叠显示
  metadata?: IMessageMetadata; // 扩展元数据
  mime_model?: IMimeModelBody; // MIME 模型（富内容）
}
```

### Message（Python）

Python 后端的消息 dataclass：[^models-py]

```python
@dataclass(kw_only=True)
class Message:
    body: str
    id: str
    time: float
    sender: str               # 发送者 username
    type: Literal["msg"] = "msg"
    attachments: list[str] | None = None   # 附件 ID 列表
    mentions: list[str] = field(default_factory=list)  # 提及的 username 列表
    raw_time: bool | None = None
    deleted: bool | None = None
    edited: bool | None = None
    metadata: dict | None = None
    mime_model: MimeModel | None = None
```

### INewMessage（TypeScript）

发送新消息时的输入类型：

```typescript
type INewMessage<T = IUser, U = IAttachment> = Partial<
  Pick<IMessageContent, 'body' | 'attachments' | 'mentions' | 'metadata' | 'mime_model' | 'sender'>
>;
```

### NewMessage（Python）

```python
@dataclass(kw_only=True)
class NewMessage:
    body: str
    sender: str
    mime_model: MimeModel | None = None
```

## 配置类型

### IConfig（TypeScript）

聊天行为配置：[^types-ts]

```typescript
interface IConfig {
  sendWithShiftEnter?: boolean;      // Shift+Enter 发送（默认 false，Enter 发送）
  stackMessages?: boolean;           // 同一发送者连续消息堆叠显示（默认 true）
  unreadNotifications?: boolean;     // 未读消息通知（默认 true）
  enableCodeToolbar?: boolean;       // 启用代码工具栏
  sendTypingNotification?: boolean;  // 发送输入中状态（默认 true）
  showDeleted?: boolean;             // 显示已删除消息
  sendWithSelection?: boolean;       // 发送时附带代码选择
}
```

### ILabChatConfig（jupyterlab-chat 扩展）

```typescript
interface ILabChatConfig extends IConfig {
  defaultDirectory?: string;         // 创建/查找聊天文件的默认目录
}
```

## 附件类型

### IAttachment（TypeScript）

`IFileAttachment | INotebookAttachment` 联合类型。

### IFileAttachment

```typescript
interface IFileAttachment {
  type: 'file';
  value: string;                     // 文件路径
  mimetype?: string;
  selection?: IAttachmentSelection;  // 文本选区
}
```

### INotebookAttachment

```typescript
interface INotebookAttachment {
  type: 'notebook';
  value: string;                     // notebook 路径
  mimetype?: string;
  cells?: INotebookAttachmentCell[]; // 引用的单元格
}

interface INotebookAttachmentCell {
  id: string;                        // 单元格 ID
  input_type: 'raw' | 'markdown' | 'code';
  selection?: IAttachmentSelection;  // 单元格内选区
}
```

### IAttachmentSelection

```typescript
interface IAttachmentSelection {
  start: [number, number];           // 起始位置 [行, 列]（0-based）
  end: [number, number];             // 结束位置 [行, 列]
  content: string;                   // 选中的文本内容
}
```

## 其他类型

### ChatArea

```typescript
type ChatArea = 'sidebar' | 'main';  // 聊天面板位置
```

### IMessageMetadata（可扩展）

空接口，支持 TypeScript 模块增强（module augmentation）扩展：

```typescript
declare module '@jupyter/chat' {
  interface IMessageMetadata {
    myCustomField?: MyCustomType;
  }
}
```

### MimeModel（Python）

```python
@dataclass(kw_only=True)
class MimeModel:
    data: dict[str, Any]             // MIME 类型到内容的映射
    metadata: dict | None = None
    trusted: bool | None = None
```

[^models-py]: models.py
[^types-ts]: TypeScript类型定义
