---
type: Example
title: 构建插件化应用
description: 使用Application类创建完整应用、定义Plugin和Token、实现服务依赖注入、插件间通信
tags: [lumino, application, plugin, token, di, ioc, shell, extensible]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: application-source
    resource: /external/libs/jupyter/lumino/packages/application/src/index.ts
    title: "@lumino/application 源码"
prerequisites:
  - /lumino/concepts/09-plugin-application
  - /lumino/concepts/07-command-system
  - /lumino/concepts/06-layout-system
---

# 示例：构建插件化应用

本示例演示如何使用 `@lumino/application` 构建一个完整的、可通过插件扩展的桌面级 Web 应用。

## 目标

创建一个简化的"代码编辑器"应用，包含以下插件：
1. **日志服务** — 提供日志记录功能（服务提供者）
2. **状态栏** — 显示应用状态（服务消费者）
3. **编辑器** — 文本编辑功能（服务消费者）
4. **侧边栏** — 文件列表面板

## 完整代码

```typescript
import { Application, IPlugin } from '@lumino/application';
import { Token } from '@lumino/coreutils';
import {
  Widget, BoxPanel, BoxLayout, DockPanel, MenuBar, Menu, CommandPalette
} from '@lumino/widgets';
import '@lumino/default-theme/style/index.css';

// ========== Step 1: 定义服务接口和Token ==========

// 日志服务接口
interface ILogger {
  log(message: string): void;
  readonly logs: ReadonlyArray<string>;
}
// Token：运行时标识ILogger服务
const ILogger = new Token<ILogger>('simple-app:ILogger', '日志服务');

// 状态栏服务接口
interface IStatusBar {
  setStatus(text: string): void;
}
const IStatusBar = new Token<IStatusBar>('simple-app:IStatusBar', '状态栏服务');

// ========== Step 2: 定义Shell（应用根Widget）==========

class AppShell extends Widget {
  constructor() {
    super();
    this.id = 'app-shell';
    this.addClass('app-shell');

    const layout = new BoxLayout({ spacing: 0 });
    this.layout = layout;

    this._menuBar = new MenuBar();
    this._menuBar.id = 'menu-bar';

    this._dock = new DockPanel();
    this._dock.id = 'main-dock';
    this._dock.spacing = 4;

    this._statusBar = new Widget();
    this._statusBar.id = 'status-bar';
    this._statusBar.node.style.height = '24px';
    this._statusBar.node.style.padding = '2px 8px';
    this._statusBar.node.style.background = '#f0f0f0';
    this._statusBar.node.style.fontSize = '12px';
    this._statusBar.node.textContent = '就绪';

    this._sidebar = new Widget();
    this._sidebar.id = 'sidebar';
    this._sidebar.title.label = '文件浏览器';
    this._sidebar.node.style.width = '200px';
    this._sidebar.node.style.background = '#fafafa';
    this._sidebar.node.style.borderRight = '1px solid #ddd';

    // 布局结构：菜单栏 | 水平分割(侧边栏+DockPanel) | 状态栏
    const hbox = new BoxPanel({ direction: 'left-to-right', spacing: 0 });
    hbox.addWidget(this._sidebar);
    BoxPanel.setStretch(this._sidebar, 0);
    hbox.addWidget(this._dock);
    BoxPanel.setStretch(this._dock, 1);

    layout.addWidget(this._menuBar);
    BoxLayout.setStretch(this._menuBar, 0);
    layout.addWidget(hbox);
    BoxLayout.setStretch(hbox, 1);
    layout.addWidget(this._statusBar);
    BoxLayout.setStretch(this._statusBar, 0);
  }

  get menuBar(): MenuBar { return this._menuBar; }
  get dock(): DockPanel { return this._dock; }

  // 实现IStatusBar
  setStatus(text: string): void {
    this._statusBar.node.textContent = text;
  }

  addToSidebar(widget: Widget): void {
    this._sidebar.node.appendChild(widget.node);
    Widget.attach(widget, this._sidebar.node);
  }

  private _menuBar: MenuBar;
  private _dock: DockPanel;
  private _statusBar: Widget;
  private _sidebar: Widget;
}

// ========== Step 3: 定义插件 ==========

// 插件1：日志服务（提供ILogger）
const loggerPlugin: IPlugin<App, ILogger> = {
  id: 'simple-app:logger',
  provides: ILogger,
  autoStart: true,
  activate: (app: App): ILogger => {
    const logs: string[] = [];
    const logger: ILogger = {
      log: (message: string) => {
        const entry = `[${new Date().toLocaleTimeString()}] ${message}`;
        logs.push(entry);
        console.log(entry);
      },
      get logs() { return logs; },
    };
    logger.log('日志服务已启动');
    return logger;
  },
};

// 插件2：状态栏服务（提供IStatusBar）
const statusBarPlugin: IPlugin<App, IStatusBar> = {
  id: 'simple-app:status-bar',
  provides: IStatusBar,
  autoStart: true,
  requires: [ILogger],
  activate: (app: App, logger: ILogger): IStatusBar => {
    logger.log('状态栏服务已启动');
    return app.shell;  // Shell本身实现了IStatusBar
  },
};

// 插件3：核心命令
const commandsPlugin: IPlugin<App, void> = {
  id: 'simple-app:commands',
  requires: [ILogger, IStatusBar],
  autoStart: true,
  activate: (app: App, logger: ILogger, statusBar: IStatusBar) => {
    const { commands, shell } = app;

    // 新建文件命令
    commands.addCommand('file:new', {
      label: '新建文件',
      execute: () => {
        logger.log('执行: 新建文件');
        statusBar.setStatus('新建文件');
        const editor = createEditorWidget('untitled.txt');
        shell.dock.addWidget(editor);
        shell.dock.activateWidget(editor);
      },
    });

    // 退出命令
    commands.addCommand('app:about', {
      label: '关于',
      execute: () => {
        alert('Simple Lumino App\n基于 @lumino/application 构建');
      },
    });

    // 快捷键
    commands.addKeyBinding({
      command: 'file:new',
      keys: ['Accel N'],
      selector: 'body',
    });

    // 菜单
    const fileMenu = new Menu({ commands });
    fileMenu.title.label = '文件';
    fileMenu.addItem({ command: 'file:new' });

    const helpMenu = new Menu({ commands });
    helpMenu.title.label = '帮助';
    helpMenu.addItem({ command: 'app:about' });

    shell.menuBar.addMenu(fileMenu);
    shell.menuBar.addMenu(helpMenu);

    logger.log('命令和菜单已注册');
  },
};

// 插件4：编辑器功能
const editorPlugin: IPlugin<App, void> = {
  id: 'simple-app:editor',
  requires: [ILogger, IStatusBar],
  autoStart: true,
  activate: (app: App, logger: ILogger, statusBar: IStatusBar) => {
    // 创建默认编辑器
    const editor = createEditorWidget('welcome.txt');
    editor.node.querySelector('textarea')!.value = '// 欢迎使用 Simple Lumino App!\n// 按 Ctrl+N 新建文件';
    app.shell.dock.addWidget(editor);
    app.shell.dock.activateWidget(editor);

    logger.log('编辑器插件已启动');
    statusBar.setStatus('就绪');
  },
};

// ========== Step 4: 辅助函数 ==========

function createEditorWidget(filename: string): Widget {
  const widget = new Widget();
  widget.addClass('editor-widget');
  widget.title.label = filename;
  widget.title.closable = true;
  widget.node.style.height = '100%';

  const header = document.createElement('div');
  header.className = 'editor-header';
  header.textContent = filename;
  header.style.padding = '4px 8px';
  header.style.background = '#e8e8e8';
  header.style.borderBottom = '1px solid #ccc';
  header.style.fontSize = '12px';

  const textarea = document.createElement('textarea');
  textarea.style.cssText = 'width:100%;height:calc(100% - 26px);border:none;resize:none;padding:8px;font-family:monospace;';
  textarea.spellcheck = false;

  widget.node.appendChild(header);
  widget.node.appendChild(textarea);
  return widget;
}

// ========== Step 5: 定义Application子类和启动 ==========

type App = Application<AppShell>;

function main(): void {
  const app = new Application<AppShell>({ shell: new AppShell() });

  // 注册所有插件
  app.registerPlugin(loggerPlugin);
  app.registerPlugin(statusBarPlugin);
  app.registerPlugin(commandsPlugin);
  app.registerPlugin(editorPlugin);

  // 启动应用
  app.start().then(() => {
    console.log('应用启动完成!');
    console.log('已注册插件:', app.listPlugins());
    Widget.attach(app.shell, document.body);
  });

  // Application.start() 自动绑定键盘事件
  // 不需要手动addEventListener('keydown')
}

window.addEventListener('DOMContentLoaded', main);
```

## 关键点说明

### 1. Token 定义模式

```typescript
interface ILogger { log(message: string): void; }
const ILogger = new Token<ILogger>('simple-app:ILogger');
```

这是 JupyterLab 生态中标准的模式：
- 接口（ILogger）在编译时存在，定义服务契约
- Token（ILogger）在运行时存在，携带类型信息
- 同名约定：接口和 Token 常量同名，TypeScript 会自动根据上下文区分

### 2. 插件依赖链

```
loggerPlugin（提供ILogger）
    ↑
statusBarPlugin（需要ILogger，提供IStatusBar）
    ↑
commandsPlugin（需要ILogger + IStatusBar）
editorPlugin（需要ILogger + IStatusBar）
```

PluginRegistry 自动拓扑排序，确保 loggerPlugin 在 statusBarPlugin 之前激活，statusBarPlugin 在 commandsPlugin/editorPlugin 之前激活。

### 3. activate 参数顺序

```typescript
activate: (app: App, logger: ILogger, statusBar: IStatusBar) => { ... }
//         ^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//         App实例   requires[] 按顺序 + optional[] 按顺序
```

`requires` 中的 Token 按顺序解析为对应的服务实例，`optional` 中的 Token 解析后追加在后面（不可用时传 null）。

### 4. Shell 作为服务提供者

Shell 本身可以实现服务接口（本例中 Shell 实现了 IStatusBar），这样 Shell 的 UI 功能就通过服务接口暴露给插件：

```typescript
const statusBarPlugin: IPlugin<App, IStatusBar> = {
  provides: IStatusBar,
  activate: (app) => app.shell,  // Shell实现了IStatusBar接口
};
```

### 5. Application.start() 自动完成的事情

- 拓扑排序并激活所有 autoStart 插件
- 将 shell 挂载到指定的 host DOM 元素
- 绑定全局 keydown/keyup 事件到 commands
- 绑定窗口 resize 事件
- resolve `app.started` Promise

### 6. 扩展新功能：添加新插件

```typescript
// 新功能插件：文件浏览器侧边栏
const fileBrowserPlugin: IPlugin<App, void> = {
  id: 'simple-app:file-browser',
  requires: [ILogger, IStatusBar],
  autoStart: true,
  activate: (app, logger, statusBar) => {
    const list = document.createElement('ul');
    list.innerHTML = '<li>welcome.txt</li><li>untitled.txt</li>';
    app.shell.addToSidebar(new (class extends Widget {
      constructor() { super(); this.node.appendChild(list); }
    })());
    logger.log('文件浏览器已添加');
  },
};

app.registerPlugin(fileBrowserPlugin);
// 无需修改现有代码！
```

这就是插件系统的核心价值：**对扩展开放，对修改封闭**。

## 项目结构建议

```
my-app/
├── src/
│   ├── index.ts          # main() 函数，注册插件并start
│   ├── shell.ts          # AppShell 类
│   ├── tokens.ts         # ILogger、IStatusBar等Token定义
│   └── plugins/
│       ├── logger.ts     # loggerPlugin
│       ├── statusbar.ts  # statusBarPlugin
│       ├── commands.ts   # commandsPlugin
│       └── editor.ts     # editorPlugin
├── package.json
└── tsconfig.json
```

## 扩展练习

1. 添加一个 `ICommandPalette` 服务插件，提供命令面板功能
2. 实现 `deactivate` 函数，使插件可以被停用
3. 使用 `autoStart: 'defer'` 延迟激活非首屏必需的插件
4. 添加 ContextMenu 服务，通过 `app.contextMenu` 注册右键菜单项
5. 使用 Poll 轮询插件实现文件变更监听
6. 实现布局保存/恢复功能（DockPanel.saveLayout/restoreLayout）
