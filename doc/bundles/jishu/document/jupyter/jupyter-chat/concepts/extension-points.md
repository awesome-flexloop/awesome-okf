---
type: Concept
title: 扩展点系统
description: jupyter-chat 的注册器扩展机制、Token 依赖注入与第三方扩展开发指南
tags: [extension, plugin, registry, token, advanced]
sources:
  - id: registers-idx
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/registers/index.ts
    title: registers/index.ts
  - id: tokens-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/tokens.ts
    title: tokens.ts
  - id: lab-token-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyterlab-chat/src/token.ts
    title: token.ts
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 扩展点系统

jupyter-chat 提供两种扩展机制：**注册器（Registry）** 用于注入 UI 组件和行为，**Token 依赖注入**用于替换或增强核心服务。

## 注册器系统

`@jupyter/chat` 包导出 4 个注册器模块，每个注册器管理一类扩展点：[^registers-idx]

| 注册器 | 模块 | 扩展内容 |
|---|---|---|
| Attachment Openers | `registers/attachment-openers` | 自定义附件打开方式 |
| Chat Commands | `registers/chat-commands` | 斜杠命令（如 `/help`） |
| Footers | `registers/footers` | 消息底部自定义区域 |
| Preambles | `registers/preambles` | 消息顶部导言区域 |
| Input Toolbar | `components/input`（InputToolbarRegistry） | 输入框工具栏按钮 |

### 使用注册器

注册器通过 ChatReactContext 传递给所有子组件，子组件使用 hook 获取注册器实例：

```tsx
function MyMessageExtension() {
  const { footersRegistry } = useChatContext();

  useEffect(() => {
    // 注册自定义 footer 组件
    footersRegistry.addRenderer((message) => {
      if (message.metadata?.myField) {
        return <MyCustomFooter metadata={message.metadata.myField} />;
      }
      return null;
    });
  }, []);
}
```

### InputToolbarRegistry

输入工具栏注册器提供静态工厂方法创建默认工具栏：

```typescript
// 创建包含默认按钮的工具栏
const registry = InputToolbarRegistry.defaultToolbarRegistry();

// 自定义按钮
registry.addItem({
  element: new MyToolbarButton(),
  rank: 100  // 排序权重
});
```

`ChatWidgetFactory` 接受 `inputToolbarFactory` 参数，支持传入自定义工厂：[^factory-ts]

```typescript
const factory = new ChatWidgetFactory({
  name: 'Chat',
  fileTypes: ['chat'],
  defaultFor: ['.chat'],
  inputToolbarFactory: {
    create: () => InputToolbarRegistry.defaultToolbarRegistry()
  },
  collaborative: true
});
```

## Token 依赖注入

jupyter-chat 使用 Lumino Token 系统进行依赖注入，第三方扩展可以通过提供 Token 实现来替换或增强默认行为。

### 核心 Token（@jupyter/chat）

#### IChatTracker

追踪所有打开的聊天面板实例：

```typescript
// 在插件中获取 tracker
const tracker: IWidgetTracker<IChatPanel> = app.require(IChatTracker);

// 遍历打开的聊天面板
for (const panel of tracker) {
  console.log(panel.model.name, panel.model.messages.length);
}
```

#### IChatPlaceholderFactory

提供空聊天面板的自定义占位组件：

```typescript
const myPlaceholderFactory: IChatPlaceholderFactory = {
  create: (props) => new MyPlaceholderWidget(props)
};

app.register(myPlaceholderFactory, IChatPlaceholderFactory);
```

#### IChatBodyPlaceholderFactory

提供聊天消息区域的空状态组件（React）：

```typescript
const myBodyPlaceholder: IChatBodyPlaceholderFactory = {
  create: (props) => <MyWelcomeScreen {...props} />
};
```

### 集成层 Token（jupyterlab-chat）

#### IChatFactory

ChatWidgetFactory 实例，用于编程方式创建聊天面板：

```typescript
const factory = app.require(IChatFactory);
const widget = factory.createNew(context);
app.shell.add(widget, 'main');
```

#### IWidgetConfig

配置管理对象，可动态修改聊天配置：

```typescript
const config = app.require(IWidgetConfig);
config.config = { sendWithShiftEnter: true };
// config.configChanged 信号通知所有部件
```

#### IWelcomeMessage

自定义欢迎消息字符串：

```typescript
app.register('欢迎使用我的自定义聊天！', IWelcomeMessage);
```

#### IActiveCellManagerToken

提供自定义活动单元格管理器（用于获取当前 notebook 的活动 cell）：

```typescript
class MyActiveCellManager implements IActiveCellManager {
  // 实现 activeCell、activeCellChanged 等
}
app.register(new MyActiveCellManager(), IActiveCellManagerToken);
```

#### ISelectionWatcherToken

提供自定义文本选择监听器（用于发送代码片段）。

#### IChatToolbarFactory

自定义工具栏工厂，主区和侧边面板共享同一个工厂：

```typescript
const toolbarFactory: ChatToolbarFactory = (panel) => {
  const items = new ObservableList<ToolbarRegistry.IToolbarItem>();
  items.push({ name: 'myButton', widget: new MyButton() });
  return items;
};
```

#### IMultiChatPanel

多聊天面板（侧边栏）实例，用于编程控制侧边栏。

## 元数据扩展

### IMessageMetadata 模块增强

TypeScript 模块增强（module augmentation）扩展消息元数据类型：[^types-ts]

```typescript
// 在你的扩展中
declare module '@jupyter/chat' {
  interface IMessageMetadata {
    /** AI 模型 ID */
    modelId?: string;
    /** 消息生成耗时（毫秒） */
    latency?: number;
    /** 反馈评分 */
    rating?: 'up' | 'down';
  }
}
```

这使得所有使用 `message.metadata.modelId` 的代码都是类型安全的。

## 消息观察者（Python）

后端扩展通过 `observe_messages` 注册消息回调，实现 bot/自动化功能：[^models-py]

```python
from jupyterlab_chat.models import MessageObserverCallback, ChatMessageEvent, ChatMessageAction

def my_bot_callback(event: ChatMessageEvent):
    """监听消息事件，实现 bot 响应"""
    if event.action == ChatMessageAction.CLIENT_MSG_RECEIVED:
        message = event.message
        if message.body.startswith('/echo '):
            # 处理命令
            response = message.body[6:]
            # 发送回复...
            pass

# 注册观察者
observer = model.observe_messages(my_bot_callback)

# 取消观察
model.unobserve_messages(observer)
```

### Chat 生命周期事件监听

通过 Jupyter Events 系统监听 chat 生命周期事件：[^events-py]

```python
from jupyter_events import EventLogger

async def on_chat_event(logger, schema_id: str, data: dict):
    action = data.get("action")
    chat_id = data.get("chat_id")
    path = data.get("path")

    if action == "opened":
        print(f"Chat opened: {path} (id={chat_id})")
    elif action == "client_connected":
        client_id = data.get("client_id")
        print(f"Client {client_id} joined chat {chat_id}")

event_logger.add_listener(
    schema_id="https://schema.jupyter.org/jupyterlab_chat/room/v1",
    listener=on_chat_event
)
```

## 文件类型扩展

聊天文件类型通过 `chatFileType` 常量注册：[^token-ts]

```typescript
// 文件类型定义
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

第三方扩展可以创建自定义文件类型，使用相同的 ChatWidgetFactory 但使用不同的扩展名。

## 扩展示例：自定义命令

```typescript
// 注册一个 /clear 斜杠命令
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-chat-extension:clear-command',
  requires: [IChatTracker],
  autoStart: true,
  activate: (app: JupyterFrontEnd, tracker: IWidgetTracker<IChatPanel>) => {
    // 通过 chatCommandsRegistry 注册命令
    // ...
  }
};
```

## 扩展开发最佳实践

1. **使用 IChatContext 而非 IChatModel**：只读操作使用 `model.createChatContext()` 获取只读上下文，避免意外修改模型状态
2. **通过 Token 注入依赖**：不要直接 import 内部模块，使用 Lumino Token 获取服务
3. **消息观察者要防御性编程**：观察者中的异常会被捕获并记录日志，但不应阻塞主流程
4. **附件使用 ID 引用**：自定义附件类型通过 `set_attachment` 存储，不要直接嵌入消息体
5. **元数据使用模块增强**：TypeScript 中使用 `declare module` 扩展 IMessageMetadata，保持类型安全
6. **清理资源**：在 dispose/useEffect cleanup 中断开信号连接、移除观察者，避免内存泄漏

## 相关概念

- [模型层架构](model-architecture.md)
- [组件层次结构](component-hierarchy.md)
- [生命周期事件](lifecycle-events.md)
- [附件系统](attachment-system.md)
- [Token 与命令参考](../references/api-tokens.md)

[^events-py]: binderhub/events.py 源码
[^factory-ts]: factory.ts
[^models-py]: models.py
[^registers-idx]: registers/index.ts
[^token-ts]: chatFileType 令牌常量模块
[^types-ts]: TypeScript类型定义
