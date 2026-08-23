---
type: Example
title: 自定义扩展示例
description: 通过注册器和 Token 扩展 jupyter-chat 的功能，包括自定义工具栏按钮、消息页脚和欢迎消息
tags: [example, extension, plugin, customization]
sources:
  - id: lab-token-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyterlab-chat/src/token.ts
    title: token.ts
  - id: tokens-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/tokens.ts
    title: tokens.ts
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 自定义扩展示例

本示例演示如何通过 jupyter-chat 的扩展点系统自定义聊天功能。

## 示例 1：自定义欢迎消息

通过 `IWelcomeMessage` Token 提供自定义欢迎消息：

```typescript
import { IWelcomeMessage } from 'jupyterlab-chat';

const welcomeMessagePlugin: JupyterFrontEndPlugin<string> = {
  id: 'my-chat:welcome',
  autoStart: true,
  provides: IWelcomeMessage,
  activate: () => {
    return '欢迎来到团队聊天！输入消息开始协作，使用 @ 提及同事。';
  }
};
```

## 示例 2：添加自定义工具栏按钮

创建一个包含自定义按钮的输入工具栏：

```typescript
import { InputToolbarRegistry, ChatWidget, ToolbarButton } from '@jupyter/chat';
import { IChatFactory, IWidgetConfig } from 'jupyterlab-chat';

// 自定义工具栏工厂
function createCustomToolbar(): InputToolbarRegistry {
  const registry = InputToolbarRegistry.defaultToolbarRegistry();

  // 添加自定义按钮：插入代码片段
  registry.addItem({
    name: 'insert-code',
    rank: 200,  // 排序权重，数字越小越靠左
    element: new ToolbarButton({
      iconClass: 'jp-CodeIcon',
      tooltip: '插入代码片段',
      onClick: () => {
        // 通过全局 tracker 获取当前活动的 chat
        const activeChat = tracker.currentWidget;
        if (activeChat) {
          const model = activeChat.model;
          model.input.value += '\n```python\n# 你的代码\n```\n';
          model.input.focus();
        }
      }
    })
  });

  return registry;
}

// 在 ChatWidgetFactory 中使用
const widgetFactory = new ChatWidgetFactory({
  name: 'Chat',
  modelName: 'chat',
  fileTypes: ['chat'],
  collaborative: true,
  inputToolbarFactory: {
    create: createCustomToolbar  // 使用自定义工具栏
  },
  config: widgetConfig
});
```

## 示例 3：通过消息观察者添加自定义页脚

```tsx
import React, { useState, useEffect } from 'react';
import { useChatContext } from '@jupyter/chat';

// 自定义消息页脚组件：显示消息反应按钮
function MessageReactions() {
  const { model } = useChatContext();
  const [messages, setMessages] = useState(model.messages);

  useEffect(() => {
    const onUpdate = () => setMessages([...model.messages]);
    model.messagesUpdated.connect(onUpdate);
    return () => model.messagesUpdated.disconnect(onUpdate);
  }, [model]);

  const addReaction = (messageId: string, emoji: string) => {
    // 使用 metadata 存储反应
    const message = model.messages.find(m => m.id === messageId);
    if (message) {
      const reactions = message.metadata?.reactions || {};
      reactions[emoji] = (reactions[emoji] || 0) + 1;
      model.updateMessage(messageId, {
        ...message,
        metadata: { ...message.metadata, reactions }
      });
    }
  };

  return (
    <div className="my-message-reactions">
      {messages.map(msg => (
        <div key={msg.id} className="reaction-bar">
          <button onClick={() => addReaction(msg.id, '👍')}>👍</button>
          <button onClick={() => addReaction(msg.id, '❤️')}>❤️</button>
        </div>
      ))}
    </div>
  );
}
```

## 示例 4：自定义空状态占位符

通过 `IChatBodyPlaceholderFactory` 提供自定义空状态：

```tsx
import React from 'react';
import { IChatBodyPlaceholderFactory } from '@jupyter/chat';

const customPlaceholderFactory: IChatBodyPlaceholderFactory = {
  create: (props) => {
    if (props.model.messages.length > 0) {
      return null;  // 有消息时不显示占位符
    }
    return (
      <div className="my-chat-welcome">
        <h2>👋 开始对话</h2>
        <p>在下方输入消息，或拖放文件来分享代码。</p>
        <div className="quick-actions">
          <button onClick={() => props.model.input.value = '/help'}>
            查看帮助
          </button>
        </div>
      </div>
    );
  }
};

// 注册到应用
app.register(customPlaceholderFactory, IChatBodyPlaceholderFactory);
```

## 示例 5：使用 Token 获取聊天面板并编程控制

```typescript
import { IChatTracker, IChatPanel } from '@jupyter/chat';

const chatControlPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-chat:control',
  autoStart: true,
  requires: [IChatTracker],
  activate: (app: JupyterFrontEnd, tracker: IChatTracker) => {

    // 添加命令：聚焦当前聊天的输入框
    app.commands.addCommand('my-chat:focus', {
      label: 'Focus Chat Input',
      isEnabled: () => tracker.currentWidget !== null,
      execute: () => {
        const panel = tracker.currentWidget;
        if (panel) {
          panel.activate();
          panel.model.input.focus();
        }
      }
    });

    // 添加键盘快捷键
    app.commands.addKeyBinding({
      command: 'my-chat:focus',
      keys: ['Accel Shift C'],
      selector: 'body'
    });

    // 监听面板变化
    tracker.widgetAdded.connect((sender, panel: IChatPanel) => {
      console.log('Chat opened:', panel.model.name);
    });
  }
};
```

## 示例 6：扩展消息元数据类型

使用 TypeScript 模块增强扩展元数据类型：

```typescript
// types/chat-metadata.d.ts
import '@jupyter/chat';

declare module '@jupyter/chat' {
  interface IMessageMetadata {
    /** AI 模型生成的回复 */
    aiModel?: string;
    /** 消息评分 */
    rating?: 'up' | 'down';
    /** 生成耗时（毫秒） */
    latencyMs?: number;
    /** 引用来源 */
    sources?: Array<{
      title: string;
      url: string;
    }>;
  }
}
```

之后所有代码中 `message.metadata.aiModel` 都是类型安全的：

```typescript
// 发送带元数据的消息
model.input.updateMetadata({
  aiModel: 'my-custom-model',
  latencyMs: 1250,
  sources: [{ title: 'Docs', url: 'https://...' }]
});
model.input.send();
```

## 示例 7：监听配置变更

```typescript
import { IWidgetConfig, ILabChatConfig } from 'jupyterlab-chat';

const configPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-chat:config',
  autoStart: true,
  requires: [IWidgetConfig],
  activate: (app: JupyterFrontEnd, widgetConfig: IWidgetConfig) => {
    // 监听配置变化
    widgetConfig.configChanged.connect((sender, newConfig) => {
      console.log('Chat config updated:', newConfig);
      // 例如：根据 sendWithShiftEnter 更新快捷键提示
    });

    // 动态更新配置（如从 settings 读取后）
    app.serviceManager.settings.load('my-chat:settings').then(settings => {
      widgetConfig.config = {
        sendWithShiftEnter: settings.get('sendWithShiftEnter') as boolean,
        stackMessages: settings.get('stackMessages') as boolean
      } as Partial<ILabChatConfig>;
    });
  }
};
```

## 相关概念

- [扩展点系统](/concepts/extension-points.md)
- [组件层次结构](/concepts/component-hierarchy.md)
- [模型层架构](/concepts/model-architecture.md)
- [Token 与命令参考](/references/api-tokens.md)
