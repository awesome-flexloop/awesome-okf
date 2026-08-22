---
type: Example
title: 最小聊天示例
description: 在 JupyterLab 扩展中使用 jupyter-chat 创建一个最基本的聊天面板
tags: [example, getting-started, minimal]
sources:
  - id: factory-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyterlab-chat/src/factory.ts
    title: factory.ts
  - id: lab-token-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyterlab-chat/src/token.ts
    title: token.ts
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 最小聊天示例

本示例演示如何在 JupyterLab 扩展中创建一个最基本的聊天面板。

## 前提条件

- JupyterLab 4.x
- jupyter-chat 已安装
- 基本的 JupyterLab 扩展开发知识

## 步骤 1：创建扩展插件

创建一个 JupyterFrontEndPlugin，注册聊天文件类型和工厂：

```typescript
// src/index.ts
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { WidgetConfig, ChatWidgetFactory, LabChatModelFactory,
         chatFileType, IChatFactory, IWidgetConfig, ILabChatConfig } from 'jupyterlab-chat';
import { InputToolbarRegistry } from '@jupyter/chat';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-chat-extension:plugin',
  autoStart: true,
  requires: [IFileBrowserFactory],
  provides: IChatFactory,
  optional: [],
  activate: (
    app: JupyterFrontEnd,
    browserFactory: IFileBrowserFactory
  ) => {
    // 1. 注册 .chat 文件类型
    app.docRegistry.addFileType(chatFileType);

    // 2. 创建配置对象
    const config: Partial<ILabChatConfig> = {
      sendWithShiftEnter: false,    // Enter 发送（Shift+Enter 换行）
      stackMessages: true,          // 连续消息堆叠
      unreadNotifications: true,    // 启用未读通知
      sendTypingNotification: true, // 发送输入中状态
      defaultDirectory: '/chats'    // 默认聊天文件目录
    };
    const widgetConfig = new WidgetConfig(config);

    // 3. 创建模型工厂
    const modelFactory = new LabChatModelFactory({
      collaborative: true,  // 使用 RTC 模式（默认）
      config
    });
    app.docRegistry.addModelFactory(modelFactory);

    // 4. 创建并注册 Widget 工厂
    const widgetFactory = new ChatWidgetFactory({
      name: 'Chat',
      modelName: 'chat',
      fileTypes: ['chat'],
      defaultFor: ['chat'],
      preferKernel: false,
      canStartKernel: false,
      collaborative: true,
      inputToolbarFactory: {
        create: () => InputToolbarRegistry.defaultToolbarRegistry()
      },
      config: widgetConfig
    });
    app.docRegistry.addWidgetFactory(widgetFactory);

    return widgetFactory;
  }
};

export default plugin;
```

## 步骤 2：创建聊天文件

用户可以通过文件浏览器创建 `.chat` 文件，或通过命令创建：

```typescript
// 在插件 activate 中添加命令
app.commands.addCommand('my-chat:create', {
  label: 'New Chat',
  execute: async () => {
    // 在默认目录创建新的 .chat 文件
    const model = await app.serviceManager.contents.newUntitled({
      path: '/chats',
      type: 'file',
      ext: '.chat'
    });
    // 打开新创建的聊天
    app.commands.execute('docmanager:open', {
      path: model.path
    });
  }
});

// 添加到启动器
app.restored.then(() => {
  app.commands.execute('launcher:add', {
    command: 'my-chat:create',
    category: 'Other',
    rank: 1
  });
});
```

## 步骤 3：发送第一条消息

用户在聊天面板中：
1. 输入消息文本
2. 按 Enter 发送（如果配置了 `sendWithShiftEnter: false`）
3. 消息立即显示在聊天区域

在 RTC 模式下，其他协作用户会实时看到新消息。

## 代码解析

### ChatWidgetFactory

```typescript
const widgetFactory = new ChatWidgetFactory({
  name: 'Chat',                          // 工厂名称
  modelName: 'chat',                     // 对应模型工厂名称
  fileTypes: ['chat'],                   // 关联的文件类型
  collaborative: true,                   // 启用 RTC 模式
  inputToolbarFactory: { create: () => InputToolbarRegistry.defaultToolbarRegistry() },
  config: widgetConfig                   // 配置对象
});
```

- `collaborative: true` 设置 `contentProviderId = 'rtc'`，启用 jupyter_collaboration 的实时同步
- `inputToolbarFactory` 创建包含默认按钮（附件、发送等）的工具栏

### LabChatModelFactory

```typescript
const modelFactory = new LabChatModelFactory({
  collaborative: true,
  config
});
```

- `contentType = 'chat'` 对应 Python 端注册的 YChat entry-point
- RTC 模式下自动创建 YChat 共享文档模型

### WidgetConfig

```typescript
const widgetConfig = new WidgetConfig(config);

// 运行时修改配置（例如从 settings 加载后更新）
widgetConfig.config = { sendWithShiftEnter: true };
// configChanged 信号会通知所有已创建的聊天面板更新配置
```

## 运行效果

安装并启用扩展后：
1. JupyterLab 启动器中出现 "New Chat" 按钮
2. 点击后在 `/chats` 目录创建新的 `.chat` 文件
3. 聊天面板在主区域打开，包含消息列表和输入框
4. 多个用户打开同一 `.chat` 文件时可以实时协作聊天

## 下一步

- [自定义扩展示例](/examples/custom-extension.md)：添加自定义工具栏按钮、消息渲染
- [Bot 集成示例](/examples/bot-integration.md)：实现自动回复的聊天机器人
- [扩展点系统](/concepts/extension-points.md)：了解所有扩展机制
