---
type: Concept
title: 附件系统
description: 附件的类型定义、去重存储策略、ID 引用机制与附件打开器扩展
tags: [attachment, file, notebook, storage, core]
sources:
  - id: types-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/types.ts
    title: types.ts
  - id: input-model-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/input-model.ts
    title: input-model.ts
  - id: ychat-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/ychat.py
    title: ychat.py
  - id: ws-model-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/websocket_model.py
    title: websocket_model.py
  - id: models-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/models.py
    title: models.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 附件系统

jupyter-chat 的附件系统支持将文件、notebook 单元格等内容附加到消息中，采用"独立存储+ID引用"模式避免数据冗余。

## 附件类型

### IAttachment 联合类型

附件是 `IFileAttachment | INotebookAttachment` 的联合类型：[^types-ts]

```typescript
// 文件附件
interface IFileAttachment {
  type: 'file';
  value: string;                     // 文件路径（相对于服务器根目录）
  mimetype?: string;                 // MIME 类型
  selection?: IAttachmentSelection;  // 文本选区（可选）
}

// Notebook 附件
interface INotebookAttachment {
  type: 'notebook';
  value: string;                     // notebook 文件路径
  mimetype?: string;
  cells?: INotebookAttachmentCell[]; // 引用的单元格列表
}
```

### INotebookAttachmentCell

```typescript
interface INotebookAttachmentCell {
  id: string;                        // 单元格 ID
  input_type: 'raw' | 'markdown' | 'code';
  selection?: IAttachmentSelection;  // 单元格内文本选区
}
```

### IAttachmentSelection

文本选区支持行列精确定位：

```typescript
interface IAttachmentSelection {
  start: [number, number];  // 起始位置 [行, 列]（0-based，包含）
  end: [number, number];    // 结束位置 [行, 列]（0-based，不包含）
  content: string;          // 选中的文本内容（冗余存储，便于直接展示）
}
```

### Python 端对应类型

[^models-py]

```python
@dataclass(kw_only=True)
class FileAttachment:
    value: str
    type: Literal['file'] = 'file'
    mimetype: str | None = None
    selection: AttachmentSelection | None = None

@dataclass(kw_only=True)
class NotebookAttachment:
    value: str
    type: Literal['notebook'] = 'notebook'
    mimetype: str | None = None
    cells: list[NotebookAttachmentCell] | None = None
```

## 存储架构

### 核心设计：ID 引用

附件不直接嵌入消息体，而是存储在独立的 `attachments` Map 中，消息中只存储 attachment ID 列表：

```
Chat Document (YDoc / JSON)
├── messages (Y.Array)
│   ├── { id: "msg1", body: "hello", attachments: ["att1", "att2"] }
│   └── { id: "msg2", body: "world", attachments: ["att1"] }  ← 复用 att1
├── attachments (Y.Map / dict)
│   ├── "att1": { type: "file", value: "/a.py", ... }
│   └── "att2": { type: "notebook", value: "/nb.ipynb", ... }
├── users (Y.Map)
└── metadata (Y.Map)
```

### 去重策略

后端 `set_attachment()` 使用 JSON 序列化比较来去重：[^ychat-py]

```python
def set_attachment(self, attachment) -> str:
    att_dict = asdict(attachment)
    att_json = json.dumps(att_dict, sort_keys=True)

    # 查找内容相同的已有附件
    att_id = next(
        (id for id, existing in self._yattachments.items()
         if json.dumps(dict(existing), sort_keys=True) == att_json),
        None
    )
    if att_id is None:
        att_id = str(uuid.uuid4())
        self._yattachments[att_id] = att_dict

    return att_id  # 返回新ID或已有ID
```

WebSocket 模式的 `WsChatModel.set_attachment()` 使用相同逻辑：[^ws-model-py]

```python
def set_attachment(self, attachment) -> str:
    att_dict = asdict(attachment)
    att_json = json.dumps(att_dict, sort_keys=True)
    att_id = next(
        (id for id, existing in self._attachments.items()
         if json.dumps(existing, sort_keys=True) == att_json),
        None
    ) or str(uuid.uuid4())
    self._attachments[att_id] = att_dict
    return att_id
```

**去重粒度**：`sort_keys=True` 确保 JSON 序列化的键顺序一致，内容完全相同的附件（相同文件路径+相同选区）共享同一 ID。

## 消息-附件关联

### 写入（发送消息时）

WebSocket handler 的 `_store_attachments()` 方法：[^websocket_handler.py]

```python
def _store_attachments(self, attachments: list[dict], model: WsChatModel) -> list[str]:
    """将附件 dict 存储到模型，返回 attachment ID 列表"""
    ids = []
    for att in attachments:
        att_json = json.dumps(att, sort_keys=True)
        # 去重
        att_id = next(
            (id for id, existing in model._attachments.items()
             if json.dumps(existing, sort_keys=True) == att_json),
            None
        ) or str(uuid.uuid4())
        model._attachments[att_id] = att
        ids.append(att_id)
    return ids
    # 消息中存储: { ..., attachments: ["att_id_1", "att_id_2"] }
```

### 读取（广播/同步时）

`resolve_message()` 在发送给客户端前将 ID 替换为完整附件对象：[^ws-model-py]

```python
def resolve_message(self, message: dict) -> dict:
    """返回消息副本，attachment ID 替换为完整对象"""
    atts = message.get("attachments")
    if not atts:
        return message
    resolved = dict(message)
    resolved["attachments"] = [
        self._attachments[att_id]
        for att_id in atts
        if att_id in self._attachments
    ]
    return resolved
```

客户端始终收到展开后的完整附件对象，无需再次查询。

## 前端附件管理

### InputModel.addAttachment()

前端添加附件时也做去重处理：[^input-model-ts]

```typescript
addAttachment(attachment: IAttachment): void {
  const attJson = JSON.stringify(attachment);

  // 基础去重：完全相同的附件不重复添加
  const exists = this._attachments.some(a => JSON.stringify(a) === attJson);
  if (exists) return;

  // Notebook 特殊处理：相同文件的 cells 合并
  if (attachment.type === 'notebook') {
    const existing = this._attachments.find(
      a => a.type === 'notebook' && a.value === attachment.value
    );
    if (existing && existing.cells && attachment.cells) {
      // 合并 cells（避免重复 cell ID）
      const existingIds = new Set(existing.cells.map(c => c.id));
      const newCells = attachment.cells.filter(c => !existingIds.has(c.id));
      existing.cells.push(...newCells);
      this.attachmentsChanged.emit();
      return;
    }
  }

  this._attachments.push(attachment);
  this.attachmentsChanged.emit();
}
```

**Notebook 合并逻辑**：如果已附加同一 notebook 的单元格，新选择的单元格会被合并到现有附件中，而不是创建新附件。

### 拖拽添加附件

`ChatWidget` 支持从 JupyterLab UI 拖拽创建附件：[^chat-widget.tsx]

| MIME 类型 | 来源 | 创建附件类型 |
|---|---|---|
| `application/x-jupyter-icontentsrich` | 文件浏览器 | `IFileAttachment` |
| `application/vnd.jupyter.cells` | Notebook cell 拖拽 | `INotebookAttachment` |
| `application/vnd.lumino.widget-factory` | 标签栏文件 | `IFileAttachment` |

## 附件打开器注册器

`AttachmentOpenerRegistry` 允许扩展注册自定义附件打开方式：[^registers-idx]

```typescript
// 注册文件类型处理器
attachmentOpenersRegistry.addOpener({
  mimeType: 'application/vnd.jupyter.notebook',
  open: (attachment, panel) => {
    // 打开 notebook
    app.commands.execute('docmanager:open', { path: attachment.value });
  }
});

// 注册代码选区处理器
attachmentOpenersRegistry.addOpener({
  mimeType: 'text/x-python',
  open: (attachment, panel) => {
    // 打开文件并定位到选区
    // ...
  }
});
```

## WebSocket 帧中的附件

### 客户端发送

```jsonc
// 新消息帧（附件是完整对象，服务器会转换为 ID 存储）
{
  "type": "msg",
  "id": "<msg-uuid>",
  "body": "看这段代码",
  "attachments": [
    { "type": "file", "value": "/src/main.py", "selection": { "start": [0,0], "end": [10,0], "content": "..." } }
  ]
}
```

### 服务端广播

```jsonc
// 广播帧（附件已展开为完整对象）
{
  "type": "msg",
  "message": {
    "id": "<msg-uuid>",
    "body": "看这段代码",
    "attachments": [
      { "type": "file", "value": "/src/main.py", "selection": { ... } }
    ]
  }
}
```

### 连接初始化

```jsonc
// 连接响应中的历史消息（附件已展开）
{
  "type": "connection",
  "messages": [
    { "id": "...", "body": "...", "attachments": [{ ... }] }
  ],
  "users": { ... }
}
```

## 文件格式：.chat 文件

.chat 文件是 JSON 格式，附件以展开形式存储（便于直接阅读和迁移）：

```json
{
  "messages": [
    {
      "id": "msg1",
      "type": "msg",
      "body": "看这个文件",
      "time": 1703000000.0,
      "sender": "alice",
      "attachments": ["att1"]
    }
  ],
  "users": {
    "alice": { "username": "alice", "name": "Alice", ... }
  },
  "attachments": {
    "att1": {
      "type": "file",
      "value": "/src/main.py",
      "mimetype": "text/x-python"
    }
  },
  "metadata": {
    "id": "<chat-uuid>"
  }
}
```

RTC 模式下，`YChat.get()` 返回相同格式的 JSON；WebSocket 模式下，`WsChatModel.save()` 直接写入此格式。

## 自定义附件类型

通过 TypeScript 模块增强可以扩展附件类型：

```typescript
declare module '@jupyter/chat' {
  interface IImageAttachment {
    type: 'image';
    value: string;     // 图片 URL 或 base64
    width?: number;
    height?: number;
  }

  // 扩展 IAttachment 联合类型
  type IAttachment = IFileAttachment | INotebookAttachment | IImageAttachment;
}
```

后端需对应扩展 dataclass 类型和处理逻辑。

## 相关概念

- [消息生命周期](message-lifecycle.md)
- [模型层架构](model-architecture.md)
- [扩展点系统](extension-points.md)
- [核心类型参考](../references/api-types.md)

[^chat-widget.tsx]: ChatWidget 前端组件源码
[^input-model-ts]: input-model.ts
[^models-py]: models.py
[^registers-idx]: registers/index.ts
[^types-ts]: TypeScript类型定义
[^websocket_handler.py]: WebSocket 消息处理器源码
[^ws-model-py]: websocket_model.py
[^ychat-py]: ychat.py
