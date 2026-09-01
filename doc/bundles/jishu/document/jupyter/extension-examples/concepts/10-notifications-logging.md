---
type: Concept
title: 通知系统与日志
description: 使用Notification API向用户发送通知，使用Logger/LogConsole创建自定义日志面板
tags: [jupyterlab, notifications, logging, logconsole, Notification, ILoggerRegistry]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: notifications-src
    resource: /references/core-api-tokens.md
    title: notifications/src/index.ts
  - id: log-messages-src
    resource: /references/core-api-tokens.md
    title: log-messages/src/index.ts
  - id: custom-log-src
    resource: /references/core-api-tokens.md
    title: custom-log-console/src/index.ts
---

## 通知系统（Notification API）

JupyterLab 4.x 提供了统一的通知API，用于向用户显示临时通知消息（成功、错误、信息、警告），支持操作按钮和异步任务进度。

```typescript
import { Notification } from '@jupyterlab/apputils';
```

### 基本通知类型

```typescript
// 成功通知（自动关闭）
Notification.success('Operation completed successfully.');

// 错误通知（带操作按钮）
Notification.error('Something went wrong.', {
  actions: [
    { label: 'Help', callback: () => alert('Help documentation') }
  ],
  autoClose: 3000  // 3秒后自动关闭
});

// 信息通知
Notification.info('Here is some information.');

// 警告通知
Notification.warning('Please be careful.');
```

### 异步任务通知（Promise通知）

最强大的通知类型——绑定到Promise，自动显示pending→success/error状态：

```typescript
import { PromiseDelegate, ReadonlyJSONValue } from '@lumino/coreutils';

const delegate = new PromiseDelegate<ReadonlyJSONValue>();
const delay = 2000;

setTimeout(() => {
  delegate.resolve({ delay });  // 异步任务完成
}, delay);

Notification.promise(delegate.promise, {
  pending: { message: 'Waiting...', options: { autoClose: false } },
  success: {
    message: (result: any) => `Action successful after ${result.delay}ms.`
  },
  error: { message: () => 'Action failed.' }
});
```

Promise通知的三种状态：
- **pending**：任务进行中，显示加载状态
- **success**：Promise resolve时显示，message可以是函数接收resolve结果
- **error**：Promise reject时显示

### 通知选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `autoClose` | `number \| false` | 自动关闭延迟（毫秒），false为不自动关闭 |
| `actions` | `Array<{label, callback, caption?}>` | 操作按钮列表 |
| `data` | `ReadonlyJSONObject` | 自定义附加数据 |

## 日志消息（Logger）

JupyterLab内置了日志系统，扩展示例展示了两种用法：向Notebook关联的Logger发送消息，以及创建独立的自定义日志面板。

### 向现有Logger发送消息

log-messages示例展示了向当前Notebook的Logger发送文本消息：

```typescript
import { ILoggerRegistry, ITextLog } from '@jupyterlab/logconsole';
import { INotebookTracker } from '@jupyterlab/notebook';

const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/log-messages:plugin',
  autoStart: true,
  requires: [ILoggerRegistry, INotebookTracker],
  activate: (app, loggerRegistry: ILoggerRegistry, nbtracker: INotebookTracker) => {
    const { commands } = app;
    commands.addCommand('jlab-examples/log-messages:logTextMessage', {
      label: 'Text log message',
      execute: () => {
        // 获取当前Notebook关联的Logger
        const logger = loggerRegistry.getLogger(
          nbtracker.currentWidget?.context.path || ''
        );

        const msg: ITextLog = {
          type: 'text',
          level: 'info',
          data: 'Hello world text!!'
        };

        logger?.log(msg);
      }
    });
  }
};
```

### 日志消息类型

| 类型 | 接口 | data类型 | 说明 |
|------|------|---------|------|
| 文本 | `ITextLog` | `string` | 纯文本日志 |
| HTML | `IHtmlLog` | `string`（HTML） | HTML格式日志 |
| 输出 | `IOutputLog` | `nbformat.IOutput` | Notebook输出格式 |

### 日志级别

`level` 字段控制日志级别过滤：
- `'debug'`：调试信息
- `'info'`：一般信息
- `'warning'`：警告
- `'error'`：错误
- `'critical'`：严重错误

## 自定义日志控制台

custom-log-console示例展示了如何创建一个独立的自定义日志面板，包含工具栏、日志级别切换和多种日志类型：

```typescript
import {
  LoggerRegistry,
  LogConsolePanel,
  IHtmlLog, ITextLog, IOutputLog
} from '@jupyterlab/logconsole';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import * as nbformat from '@jupyterlab/nbformat';

const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/custom-log-console:plugin',
  autoStart: true,
  requires: [ICommandPalette, IRenderMimeRegistry, ILayoutRestorer],
  activate: (app, palette, rendermime, restorer) => {
    let logConsolePanel: LogConsolePanel | null = null;
    let logConsoleWidget: MainAreaWidget<LogConsolePanel> | null = null;

    // 创建Logger注册表
    const createLogConsoleWidget = (): void => {
      logConsolePanel = new LogConsolePanel(
        new LoggerRegistry({
          defaultRendermime: rendermime,
          maxLength: 1000  // 最多保留1000条日志
        })
      );
      logConsolePanel.source = 'custom-log-console';

      // 包装在MainAreaWidget中（带工具栏）
      logConsoleWidget = new MainAreaWidget<LogConsolePanel>({
        content: logConsolePanel
      });
      logConsoleWidget.title.label = 'Custom Log console';
      logConsoleWidget.title.icon = listIcon;

      // 添加工具栏按钮
      logConsoleWidget.toolbar.addItem('checkpoint', new CommandToolbarButton({
        commands: app.commands,
        id: 'jlab-examples/custom-log-console:checkpoint'
      }));
      logConsoleWidget.toolbar.addItem('clear', new CommandToolbarButton({
        commands: app.commands,
        id: 'jlab-examples/custom-log-console:clear'
      }));
      logConsoleWidget.toolbar.addItem('level', new LogLevelSwitcher(logConsoleWidget.content));

      app.shell.add(logConsoleWidget, 'main', { mode: 'split-bottom' });
      tracker.add(logConsoleWidget);
    };

    // 发送HTML日志
    commands.addCommand('jlab-examples/custom-log-console:logHTMLMessage', {
      label: 'HTML Log Message',
      execute: () => {
        const msg: IHtmlLog = { type: 'html', level: 'debug', data: '<div>Hello HTML!!</div>' };
        logConsolePanel?.logger?.log(msg);
      }
    });

    // 发送Notebook输出日志
    commands.addCommand('jlab-examples/custom-log-console:logOutputMessage', {
      label: 'Output Log Message',
      execute: () => {
        const data: nbformat.IOutput = {
          output_type: 'display_data',
          data: { 'text/plain': 'Hello nbformat!!' }
        };
        const msg: IOutputLog = { type: 'output', level: 'warning', data };
        logConsolePanel?.logger?.log(msg);
      }
    });
  }
};
```

### LoggerRegistry 配置

```typescript
new LoggerRegistry({
  defaultRendermime: rendermime,  // 用于渲染富文本输出
  maxLength: 1000                 // 最大日志条数（超出自动截断）
})
```

### LogConsolePanel API

| 属性/方法 | 说明 |
|----------|------|
| `source` | 设置日志来源名称 |
| `logger` | 获取当前Logger实例 |
| `logger.log(msg)` | 发送日志消息 |
| `logger.checkpoint()` | 添加检查点标记 |
| `logger.clear()` | 清空日志 |
| `logger.level` | 设置/获取日志级别 |

### 日志级别切换命令

```typescript
commands.addCommand('jlab-examples/custom-log-console:level', {
  execute: (args: any) => {
    if (logConsolePanel?.logger) {
      logConsolePanel.logger.level = args.level;
    }
  },
  isEnabled: () => !!logConsolePanel && logConsolePanel.source !== null,
  label: args => `Set Log Level to ${args.level as string}`
});
```

## 通知 vs 日志 vs 对话框

| 机制 | 适用场景 | 持久性 |
|------|---------|--------|
| Notification | 操作结果反馈、错误提示 | 临时（自动关闭） |
| Logger/LogConsole | 长时间运行的过程输出、调试信息 | 持久（在面板中累积） |
| showDialog | 需要用户确认的重要操作 | 模态阻塞 |
| window.alert | 简单调试 | 模态阻塞（避免在生产中使用） |

## 相关概念

- [菜单与工具栏](08-menus-toolbars.md)
- [设置与状态持久化](09-settings-state.md)
- [Widget与Shell布局](05-widgets-shell.md)
- [核心API与Token参考](../references/core-api-tokens.md)
