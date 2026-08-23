---
type: Concept
title: 命令系统与快捷键
description: CommandRegistry命令注册表、命令选项（label/icon/enabled/toggled/visible）、KeyBinding快捷键绑定、命令面板、菜单集成
tags: [lumino, commands, keybinding, menu, command-palette, shortcut, actions]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:35:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: commands-source
    resource: /external/libs/jupyter/lumino/packages/commands/src/index.ts
    title: @lumino/commands 源码
---

# 命令系统与快捷键

## 命令系统的设计目标

在桌面级应用中，"命令"是一个核心抽象——同一个操作可能通过菜单项、工具栏按钮、快捷键、命令面板等多种方式触发。命令系统将"做什么"与"怎么触发"解耦：

- 命令本身定义：执行逻辑、显示名称、图标、启用/选中状态
- 触发方式独立：快捷键、菜单、按钮、命令面板都引用同一个命令 ID

Lumino 的 [CommandRegistry](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/commands/src/index.ts#L39) 实现了这一模式。

## CommandRegistry 核心 API

### 注册命令

```typescript
class CommandRegistry {
  addCommand(id: string, options: CommandRegistry.ICommandOptions): IDisposable;
}
```

命令 ID 是全局唯一的字符串（通常使用命名空间格式，如 `'docmanager:save'`）。返回的 IDisposable 用于移除命令。

### 命令选项 ICommandOptions

```typescript
interface ICommandOptions {
  execute: (args: ReadonlyPartialJSONObject) => any;  // 必填：执行函数

  // 以下都是可选的，可以是静态值或函数（根据args动态计算）
  label?: string | ((args: ReadonlyPartialJSONObject) => string);
  icon?: VirtualElement.IRenderer | string | ((args) => VirtualElement.IRenderer | undefined | string);
  caption?: string | ((args) => string);           // tooltip
  usage?: string;                                  // 命令面板中的使用说明
  className?: string | ((args) => string);
  isEnabled?: boolean | ((args) => boolean);       // 是否可用（默认true）
  isToggled?: boolean | ((args) => boolean);       // 是否选中/勾选（默认false）
  isVisible?: boolean | ((args) => boolean);       // 是否可见（默认true）
  mnemonic?: number | ((args) => number);          // Alt+键的助记符位置
}
```

**函数式选项的威力**：label/icon/enabled/toggled 等都可以是函数，根据传入的 `args` 动态计算。这让一个命令 ID 可以处理多种上下文：

```typescript
// 示例：一个通用的"关闭标签"命令，根据args关闭不同标签
commands.addCommand('tabs:close', {
  execute: (args) => {
    const tab = args.tab as Widget;
    tab.close();
  },
  label: (args) => {
    const tab = args.tab as Widget;
    return tab ? `关闭 ${tab.title.label}` : '关闭标签';
  },
  isEnabled: (args) => args.tab !== undefined,
});
```

### 查询命令状态

```typescript
// 查询命令元信息
commands.label(id, args?): string;          // 显示名称
commands.caption(id, args?): string;        // 提示文字
commands.className(id, args?): string;      // CSS类名
commands.icon(id, args?): VirtualElement.IRenderer | undefined;
commands.isEnabled(id, args?): boolean;     // 是否可用
commands.isToggled(id, args?): boolean;     // 是否选中
commands.isVisible(id, args?): boolean;     // 是否可见

// 执行命令
commands.execute(id, args?): Promise<any>;
```

所有查询方法都接受 args 参数，用于计算动态状态。

### 通知状态变化

```typescript
commands.notifyCommandChanged(id?: string): void;
```

当命令的外部状态变化导致 enabled/toggled/label 等值改变时，调用此方法通知系统。这会发射 `commandChanged` 信号，菜单、工具栏等 UI 组件收到信号后刷新显示。

```typescript
// 示例：当选择变化时通知命令状态更新
selectionChanged.connect(() => {
  commands.notifyCommandChanged('edit:copy');
  commands.notifyCommandChanged('edit:cut');
});
```

### 信号

```typescript
// 命令变化（添加/移除/状态改变）
commands.commandChanged: ISignal<CommandRegistry, ICommandChangedArgs>;

// 命令执行后
commands.commandExecuted: ISignal<CommandRegistry, ICommandExecutedArgs>;

// 快捷键绑定变化
commands.keyBindingChanged: ISignal<CommandRegistry, IKeyBindingChangedArgs>;
```

## 快捷键绑定（KeyBinding）

### 注册快捷键

```typescript
commands.addKeyBinding(options: IKeyBindingOptions): IDisposable;

interface IKeyBindingOptions {
  command: string;              // 要触发的命令ID
  keys: string[];               // 快捷键序列（支持多组）
  selector: string;             // CSS选择器，限定焦点范围
  args?: ReadonlyPartialJSONObject;  // 执行命令时传入的参数
}
```

**keys 格式**：使用修饰符前缀组合
- `'Accel X'` — 在 macOS 上是 `Cmd+X`，在 Windows/Linux 上是 `Ctrl+X`（推荐！跨平台）
- `'Ctrl X'` — 强制 Ctrl
- `'Cmd X'` — 强制 Cmd（macOS）
- `'Alt X'` — Alt 键
- `'Shift X'` — Shift 键
- 多键序列：`'Ctrl K Ctrl C'`（先按 Ctrl+K，再按 Ctrl+C）

**selector**：CSS 选择器决定快捷键在哪个 DOM 元素获得焦点时生效。例如：
- `'body'` — 全局生效
- `'.jp-Notebook'` — 仅在 Notebook 中生效
- `'input, textarea, [contenteditable]'` — 在可编辑元素中生效

```typescript
// 示例：注册保存快捷键
commands.addKeyBinding({
  command: 'docmanager:save',
  keys: ['Accel S'],
  selector: 'body',
});
```

### 快捷键处理流程

当 keydown 事件发生时：

1. **精确匹配**：查找与当前按键序列和选择器完全匹配的快捷键
2. **部分匹配**：如果有多键序列前缀匹配，等待下一个按键
3. **选择器优先级**：使用 `@lumino/domutils` 的 `Selector` 计算选择器特异性（specificity），最具体的选择器优先
4. **冒泡 vs 捕获**：默认在捕获阶段处理，可以通过 `bubblingKeydown` 选项改为冒泡阶段
5. **键盘布局**：通过 `@lumino/keyboard` 的 `getKeyboardLayout()` 处理不同键盘布局的键码映射

### 键盘事件处理方法

```typescript
commands.processKeydownEvent(event: KeyboardEvent): boolean;
commands.processKeyupEvent(event: KeyboardEvent): void;
```

Application 类默认在 keydown/keyup 事件中调用这些方法。`processKeydownEvent` 返回 `true` 表示事件被处理（应 preventDefault）。

## 与 Menu 集成

CommandRegistry 不直接创建 UI 菜单，但 `@lumino/widgets` 的 Menu 类使用 CommandRegistry 来构建菜单项：

```typescript
import { Menu } from '@lumino/widgets';

const menu = new Menu({ commands });

// 添加命令作为菜单项
menu.addItem({ command: 'file:new' });
menu.addItem({ command: 'file:open' });
menu.addItem({ type: 'separator' });
menu.addItem({ command: 'file:save' });
menu.addItem({ command: 'file:save-as' });

// 添加子菜单
const openRecentMenu = new Menu({ commands });
// ...添加最近文件项...
menu.addItem({ type: 'submenu', submenu: openRecentMenu });
```

Menu 自动从 CommandRegistry 获取 label、icon、isEnabled、isToggled 等状态，并在 `commandChanged` 信号时刷新。

## 与 CommandPalette 集成

CommandPalette 是命令面板（类似 VS Code 的 Ctrl+Shift+P）：

```typescript
import { CommandPalette } from '@lumino/widgets';

const palette = new CommandPalette({ commands });

// 将命令添加到面板
palette.addItem({ command: 'file:new', category: 'File' });
palette.addItem({ command: 'file:open', category: 'File' });
palette.addItem({ command: 'edit:copy', category: 'Edit' });
palette.addItem({ command: 'edit:paste', category: 'Edit' });

// 用户输入搜索
palette.inputNode.value = 'save';  // 过滤显示相关命令
```

命令的 `usage` 字段会在命令面板中显示使用说明，帮助用户发现命令。

## 命令的常见模式

### 1. 切换命令（Toggle）

```typescript
commands.addCommand('view:toggle-sidebar', {
  execute: () => { sidebarVisible = !sidebarVisible; updateSidebar(); },
  label: '切换侧边栏',
  isToggled: () => sidebarVisible,  // 反映当前状态
});
```

### 2. 上下文命令

```typescript
commands.addCommand('file:rename', {
  execute: (args) => {
    const widget = args.widget as Widget;
    return showRenameDialog(widget);
  },
  isEnabled: (args) => args.widget instanceof FileWidget,
  label: '重命名',
});
```

### 3. 异步命令

execute 可以返回 Promise：

```typescript
commands.addCommand('file:save', {
  execute: async () => {
    await saveCurrentFile();
  },
  isEnabled: () => hasCurrentFile && !isSaving,
  label: '保存',
});
```

## 应用中的使用

在 Application 中，commands 和 contextMenu 是自动创建的：

```typescript
class MyApp extends Application<Shell> {
  constructor() {
    super({ shell: new Shell() });
    // this.commands 已自动创建
    // this.contextMenu 已自动创建
  }
}

// 应用启动后注册命令和快捷键
app.started.then(() => {
  app.commands.addCommand('hello:world', {
    execute: () => console.log('Hello!'),
    label: 'Hello World',
  });
  app.commands.addKeyBinding({
    command: 'hello:world',
    keys: ['Accel Shift H'],
    selector: 'body',
  });
});
```

右键菜单通过 contextMenu 打开：

```typescript
// 在 contextmenu 事件中
app.contextMenu.open(event);
// 内部查找匹配选择器的命令，构建并显示菜单
```

## 相关概念

- [Signal/Slot 类型安全事件系统](03-signaling-system.md) — CommandRegistry 使用 Signal 通知状态变化
- [Widget 生命周期与DOM管理](05-widget-lifecycle.md) — Menu、CommandPalette 都是 Widget
- [插件化应用框架](09-plugin-application.md) — 插件通过 Application.commands 注册命令
- [高级组件与DataGrid](10-advanced-widgets.md) — Menu、MenuBar、ContextMenu、CommandPalette 的使用
