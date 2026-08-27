---
type: Concept
title: 插件化应用框架
description: Application类、PluginRegistry插件注册、Token服务标识、IPlugin接口、插件依赖注入与激活流程、自动启动与延迟激活
tags: [lumino, application, plugin, token, di, dependency-injection, extension, architecture]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: application-source
    resource: /external/libs/jupyter/lumino/packages/application/src/index.ts
    title: "@lumino/application 源码"
  - id: plugins-source
    resource: /external/libs/jupyter/lumino/packages/coreutils/src/plugins.ts
    title: "@lumino/coreutils PluginRegistry 源码"
  - id: token-source
    resource: /external/libs/jupyter/lumino/packages/coreutils/src/token.ts
    title: "@lumino/coreutils Token 源码"
---

# 插件化应用框架

## Application：可扩展应用的入口

Application 是构建桌面级 Web 应用的入口类。它将 CommandRegistry、ContextMenu、Shell（根 Widget）和插件系统组合在一起，提供了一个完整的可扩展应用框架。

```typescript
class Application<T extends Widget = Widget> {
  constructor(options: Application.IOptions<T>);

  readonly commands: CommandRegistry;    // 命令注册表
  readonly contextMenu: ContextMenu;     // 右键菜单
  readonly shell: T;                     // 根 Shell Widget
  readonly started: Promise<void>;       // 启动完成 Promise
  readonly pluginRegistry: PluginRegistry<this>;  // 插件注册中心
}
```

### 启动流程

```typescript
const app = new Application({ shell: new MyShell() });

// 注册插件
app.registerPlugin(myPlugin);
app.registerPlugin(anotherPlugin);

// 启动
await app.start();
// 此时所有 autoStart 插件已激活
// shell 已挂载到 DOM
// 键盘事件已绑定

// 激活延迟插件
await app.activateDeferredPlugins();
```

**start() 方法的执行序列**：

1. 对插件进行拓扑排序（根据 requires 依赖关系）
2. 激活所有 `autoStart: true` 的插件（按依赖顺序）
3. 将 shell 挂载到 DOM（`Widget.attach(shell, host)`）
4. 绑定全局键盘事件（keydown/keyup → commands.processKeydownEvent）
5. 绑定窗口 resize 事件 → shell 发送 resize 消息
6. 绑定 contextmenu 事件 → contextMenu 处理
7. resolve started Promise

### 构造选项

```typescript
interface IOptions<T extends Widget> {
  shell: T;                              // 必填：根 Shell Widget
  contextMenuRenderer?: Menu.IRenderer;  // 可选：自定义菜单渲染器
  pluginRegistry?: PluginRegistry;       // 可选：自定义插件注册中心
}
```

## Token：类型安全的服务标识

Token<T> 是 Lumino 插件系统的核心抽象，用于在运行时标识服务类型，同时在编译时携带类型信息：

```typescript
class Token<T> {
  constructor(name: string, description?: string);
  readonly name: string;
  readonly description: string;
  private _tokenStructuralPropertyT: T;  // 编译时类型标记（运行时为null）
}
```

### Token 的作用

TypeScript 的接口在编译后会被擦除（erasue），运行时不存在类型信息。Token 是一个"类型标记"模式：

```typescript
// 定义一个服务接口（编译时存在，运行时擦除）
interface ILogger {
  log(message: string): void;
}

// 创建 Token 作为运行时标识（携带编译时类型信息）
const ILogger = new Token<ILogger>('my-app:ILogger', '日志服务');
//      ^^^^^ 注意：Token实例和接口同名是常见约定（JupyterLab模式）
```

Token 的泛型参数 `T` 将运行时对象和编译时类型绑定在一起：
- 运行时：Token 是一个普通对象，用 `name` 做唯一标识
- 编译时：TypeScript 通过 `Token<T>` 推断服务类型，实现类型安全

## IPlugin：插件接口

IPlugin<T, U> 定义插件的结构：

```typescript
interface IPlugin<T, U> {
  id: string;                                    // 唯一ID
  description?: string;                          // 插件描述
  autoStart?: boolean | 'defer';                 // 自动启动策略
  requires?: Token<any>[];                       // 必需的服务依赖
  optional?: Token<any>[];                       // 可选的服务依赖
  provides?: Token<U> | null;                    // 提供的服务
  activate: (app: T, ...args: any[]) => U | Promise<U>;  // 激活函数
  deactivate?: (app: T, ...args: any[]) => void | Promise<void>;  // 可选的停用函数
}
```

### 插件字段详解

| 字段 | 说明 |
|------|------|
| `id` | 全局唯一字符串，通常使用命名空间格式（如 `'my-app:logger'`） |
| `description` | 插件功能描述，用于文档和调试 |
| `autoStart` | `true`=应用启动时激活；`'defer'`=启动后延迟激活；`false`（默认）=按需激活 |
| `requires` | 依赖的 Token 数组，激活时按顺序传入对应服务实例 |
| `optional` | 可选依赖的 Token 数组，不可用时传 `null` |
| `provides` | 插件提供的服务 Token，`activate` 返回值将注册为该服务 |
| `activate` | 激活函数，第一个参数是 Application，后续是 requires+optional 解析出的服务 |
| `deactivate` | 可选的停用函数，用于清理资源（支持热卸载） |

### 插件示例

**1. 纯功能插件（不提供服务）**：

```typescript
const helloPlugin: IPlugin<App, void> = {
  id: 'my-app:hello',
  autoStart: true,
  activate: (app: App) => {
    console.log('Hello from plugin!');
    app.commands.addCommand('hello:world', {
      execute: () => console.log('Hello World!'),
      label: 'Hello',
    });
  },
};
```

**2. 提供服务的插件**：

```typescript
// 定义服务Token和接口
const ILogger = new Token<ILogger>('my-app:ILogger');
interface ILogger {
  log(msg: string): void;
}

const loggerPlugin: IPlugin<App, ILogger> = {
  id: 'my-app:logger',
  provides: ILogger,
  autoStart: true,
  activate: (app: App): ILogger => {
    const logger: ILogger = {
      log: (msg: string) => console.log(`[${new Date().toISOString()}] ${msg}`),
    };
    return logger;  // 返回值注册为 ILogger 服务
  },
};
```

**3. 消费服务的插件（有依赖）**：

```typescript
const editorPlugin: IPlugin<App, void> = {
  id: 'my-app:editor',
  requires: [ILogger],                // 依赖ILogger服务
  optional: [ICommandPalette],        // 可选依赖命令面板
  autoStart: true,
  activate: (app: App, logger: ILogger, palette: ICommandPalette | null) => {
    logger.log('Editor plugin activating...');

    const editor = new EditorWidget();
    app.shell.add(editor, 'main');

    if (palette) {
      palette.addItem({ command: 'editor:new', category: 'Editor' });
    }
  },
};
```

## 插件激活流程

PluginRegistry 管理插件的注册、依赖解析和激活：

### 注册阶段

```typescript
app.registerPlugin(loggerPlugin);
app.registerPlugin(editorPlugin);
```

注册时：
1. 检查 id 唯一性（重复则抛出错误）
2. 检查循环依赖（requires 形成环则抛出错误）
3. 将插件存入内部注册表

### 激活阶段（拓扑排序 + 懒加载）

当 `app.start()` 或 `app.activatePlugin(id)` 被调用时：

1. **依赖解析**：遍历插件的 `requires` 和 `optional`，递归解析依赖树
2. **拓扑排序**：使用 `topologicSort`（@lumino/algorithm）对依赖图排序，确保被依赖的插件先激活
3. **按需激活**：如果一个依赖的插件尚未激活，先激活它
4. **服务解析**：从服务注册表中取出 requires 对应的服务实例
5. **调用 activate**：按顺序传入 app 和解析出的服务参数
6. **服务注册**：如果插件有 `provides`，将 activate 返回值注册为对应 Token 的服务

```
editorPlugin.requires = [ILogger]
        ↓
发现 ILogger 由 loggerPlugin 提供
        ↓
loggerPlugin 是否已激活？否 → 先激活 loggerPlugin
        ↓
loggerPlugin.activate(app) → 返回 logger 实例
        ↓
注册 ILogger → logger 实例
        ↓
editorPlugin.activate(app, logger)
```

### 自动启动策略

| autoStart 值 | 激活时机 |
|--------------|----------|
| `true` | app.start() 时激活 |
| `'defer'` | app.start() 完成后，通过 activateDeferredPlugins() 激活 |
| `false`（默认） | 仅在被其他插件依赖或手动 activatePlugin 时激活 |

`'defer'` 模式用于不阻塞首屏渲染的插件，提高启动性能。

### 插件停用

```typescript
const deactivated = await app.deactivatePlugin('my-plugin');
// 返回被一起停用的下游依赖插件ID列表
```

停用会递归停用依赖该插件的其他插件（下游），要求被停用的插件都实现了 `deactivate` 函数。

## Shell：应用根容器

Shell 是 Application 的根 Widget，作为应用 UI 的容器。它通常是一个 DockLayout 或自定义布局，提供多个区域供插件插入内容：

```typescript
class AppShell extends Widget {
  constructor() {
    super();
    this.layout = new BoxLayout();
  }

  // 提供注册Widget的API供插件调用
  add(widget: Widget, area: 'left' | 'right' | 'main' | 'top' | 'bottom'): void {
    // 根据area将Widget添加到对应区域
  }
}
```

JupyterLab 的 Shell 提供了更丰富的区域（header、top、left、main、right、bottom 等），插件通过 `app.shell.add(widget, area, options)` 将内容放入特定区域。

## 全局事件绑定

Application.start() 自动绑定以下全局事件：

1. **键盘事件**（捕获阶段）：`keydown` → `commands.processKeydownEvent()`，`keyup` → `commands.processKeyupEvent()`。返回 true 时 preventDefault，阻止浏览器默认行为。
2. **窗口 resize**：`window.resize` → 向 shell 发送 resize 消息
3. **右键菜单**：`document.body` 上的 `contextmenu` 事件 → `contextMenu.open(event)`
4. **beforeunload**（可选）：页面关闭前处理未保存更改

## ContextMenu 集成

ContextMenu 使用 CommandRegistry 构建上下文菜单，根据事件目标的 CSS 选择器匹配可用命令：

```typescript
// 插件中注册带selector的命令
app.commands.addCommand('file:rename', {
  execute: () => renameCurrentFile(),
  label: '重命名',
  isVisible: () => hasSelectedFile(),
});

// 在ContextMenu中注册项（指定选择器）
app.contextMenu.addItem({
  command: 'file:rename',
  selector: '.file-item',  // 仅在 .file-item 元素上右键时显示
  rank: 10,  // 排序优先级
});
```

右键时，ContextMenu 从事件目标向上冒泡，收集所有 selector 匹配的菜单项，按 rank 排序后显示菜单。

## 插件系统的设计原则

Lumino 的插件系统遵循以下设计原则：

1. **依赖倒置**：插件依赖抽象的 Token（接口），不依赖具体实现
2. **类型安全**：Token 携带类型参数，activate 函数参数类型自动推导
3. **延迟加载**：非 autoStart 的插件仅在被需要时激活
4. **无全局状态**：服务通过参数传递，不通过全局单例访问
5. **组合优于继承**：Application 组合 CommandRegistry、PluginRegistry、Shell，而非通过继承扩展
6. **生命周期管理**：插件提供 activate/deactivate 钩子，支持启停控制

## 典型插件代码结构

参考 JupyterLab 的插件编写模式：

```typescript
// 1. 导入Token和依赖
import { ICommandPalette } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';

// 2. 定义插件（通常直接导出对象）
const plugin: IPlugin<JupyterFrontEnd, void> = {
  id: 'my-extension:plugin',
  autoStart: true,
  requires: [INotebookTracker],
  optional: [ICommandPalette],
  activate: (app, notebooks, palette) => {
    // 注册命令
    const { commands } = app;
    commands.addCommand('my:command', {
      execute: () => { /* ... */ },
      label: 'My Command',
    });

    // 添加到命令面板
    if (palette) {
      palette.addItem({ command: 'my:command', category: 'My Extension' });
    }

    // 添加Widget到Shell
    const widget = new MyWidget();
    app.shell.add(widget, 'right');
  },
};

export default plugin;
```

## 相关概念

- [命令系统与快捷键](07-command-system.md) — Application.commands 的命令注册
- [Widget 生命周期与DOM管理](05-widget-lifecycle.md) — Shell 作为根 Widget
- [布局系统详解](06-layout-system.md) — Shell 使用布局管理区域
- [IDisposable资源管理](02-disposable-pattern.md) — registerPlugin返回IDisposable
