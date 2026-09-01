---
type: Concept
title: 命令系统
description: 掌握JupyterLab命令注册、执行和参数传递机制，命令是所有用户交互的基础
tags: [jupyterlab, commands, addCommand, execute, command-registry]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: commands-src
    resource: /references/core-api-tokens.md
    title: commands/src/index.ts 命令注册示例
---

## 命令是JupyterLab的交互核心

在JupyterLab中，几乎所有用户操作都通过**命令（Command）** 执行：点击菜单项、按快捷键、点击工具栏按钮、从命令面板搜索——全部触发命令。

命令存储在全局 `CommandRegistry` 中，通过 `app.commands` 访问。

## 注册命令

使用 `commands.addCommand(id, options)` 注册命令：

```typescript
const { commands } = app;
const commandId = 'jlab-examples:command';

commands.addCommand(commandId, {
  label: 'Execute jlab-examples:command Command',
  caption: 'Execute jlab-examples:command Command',
  execute: (args: any) => {
    const orig = args['origin'];
    console.log(`jlab-examples:command called from ${orig}.`);
    if (orig !== 'init') {
      window.alert(`Called from ${orig}.`);
    }
  }
});
```

### 命令ID命名约定

- 格式：`<extension-prefix>:<action-name>`
- 使用冒号分隔命名空间和动作名
- 示例：`jlab-examples:command`、`notebook:run-cell`、`docmanager:open`
- JupyterLab内置命令使用简短前缀（如 `notebook:`, `docmanager:`, `filebrowser:`）

### addCommand 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `label` | `string \| (args) => string` | 显示名称，支持根据参数动态生成 |
| `caption` | `string` | 鼠标悬停提示文本 |
| `execute` | `(args) => any` | **必需**，命令执行函数 |
| `icon` | `LabIcon \| (args) => LabIcon` | 图标 |
| `isVisible` | `() => boolean` | 动态控制可见性 |
| `isEnabled` | `() => boolean` | 动态控制启用/禁用状态 |
| `isToggled` | `() => boolean` | 切换按钮状态（如复选框） |
| `mnemonic` | `number` | Alt+助记键位置 |

### 动态label和icon

launcher示例展示了如何根据调用参数改变显示：

```typescript
commands.addCommand(command, {
  label: args => args['isPalette'] ? 'New Python File From Extension' : 'Python File From Extension',
  icon: args => args['isPalette'] ? undefined : icon,
  execute: async args => { /* ... */ }
});
```

当从命令面板调用时（`isPalette: true`），不显示图标并使用不同标签；从Launcher卡片调用时显示图标。

## 执行命令

使用 `commands.execute(id, args)` 执行命令：

```typescript
// 执行时传递参数
commands.execute(commandId, { origin: 'init' }).catch(reason => {
  console.error(`Error executing command.\n${reason}`);
});

// 调用内置命令（创建新文件）
const model = await commands.execute('docmanager:new-untitled', {
  path: cwd,
  type: 'file',
  ext: 'py'
});

// 打开文件
commands.execute('docmanager:open', {
  path: model.path,
  factory: 'Editor'
});

// 执行notebook命令
commands.execute('notebook:run-cell');
```

关键要点：
- `execute()` 返回 Promise，可以使用 `await` 或 `.then()`
- 总是用 `.catch()` 处理执行错误
- 通过 `args` 对象传递参数
- 可以执行其他扩展注册的命令，实现跨扩展协作

## 命令的动态状态控制

### isVisible：条件显示

cell-toolbar示例展示了根据cell类型显示不同按钮：

```typescript
commands.addCommand(CommandIds.runCodeCell, {
  icon: runIcon,
  caption: 'Run a code cell',
  execute: () => { commands.execute('notebook:run-cell'); },
  isVisible: () => tracker.activeCell?.model.type === 'code'
});

commands.addCommand(CommandIds.renderMarkdownCell, {
  icon: markdownIcon,
  caption: 'Render a markdown cell',
  execute: () => { commands.execute('notebook:run-cell'); },
  isVisible: () => tracker.activeCell?.model.type === 'markdown'
});
```

### isEnabled：条件启用

custom-log-console示例根据logConsolePanel状态启用/禁用命令：

```typescript
commands.addCommand('jlab-examples/custom-log-console:clear', {
  execute: () => logConsolePanel?.logger?.clear(),
  icon: clearIcon,
  isEnabled: () => !!logConsolePanel && logConsolePanel.source !== null,
  label: 'Clear Log'
});
```

### isToggled：切换状态

settings示例展示了开关型命令：

```typescript
commands.addCommand(COMMAND_ID, {
  label: 'Toggle Flag and Increment Limit',
  isToggled: () => flag,
  execute: () => { /* 切换flag值 */ }
});
```

### notifyCommandChanged：刷新状态

当动态状态的依赖变化时，通知命令系统刷新：

```typescript
logConsoleWidget.disposed.connect(() => {
  logConsoleWidget = null;
  logConsolePanel = null;
  commands.notifyCommandChanged();  // 刷新所有命令的isEnabled/isToggled状态
});
```

## 命令与UI元素的连接

命令注册后，可以连接到多个UI入口：

| UI入口 | 连接方式 | 示例 |
|--------|---------|------|
| 命令面板 | `palette.addItem({ command, category, args })` | command-palette示例 |
| Launcher | `launcher.add({ command, category, rank })` | launcher示例 |
| 主菜单 | schema/plugin.json 中声明 | main-menu示例 |
| 右键菜单 | schema/plugin.json 中声明 | context-menu示例 |
| 工具栏按钮 | schema/plugin.json 中声明 | toolbar-button示例 |
| Cell工具栏 | 代码中addCommand配合isVisible | cell-toolbar示例 |
| 键盘快捷键 | schema/plugin.json 中声明 | — |

同一个命令可以同时出现在面板、菜单、工具栏中，实现一处定义多处触发。

## 常用内置命令

| 命令ID | 说明 |
|--------|------|
| `docmanager:new-untitled` | 创建新文件 |
| `docmanager:open` | 打开文件 |
| `docmanager:save` | 保存当前文件 |
| `notebook:run-cell` | 运行当前cell |
| `notebook:run-all-cells` | 运行所有cell |
| `notebook:insert-cell-below` | 在下方插入cell |
| `notebook:delete-cells` | 删除选中cell |
| `notebook:change-cell-to-code` | 转为code cell |
| `notebook:change-cell-to-markdown` | 转为markdown cell |
| `notebook:clear-all-cell-outputs` | 清除所有输出 |
| `filebrowser:create-new-directory` | 新建目录 |

## 相关概念

- [插件基础与依赖注入](03-plugin-basics.md)
- [命令面板与Launcher](07-palette-launcher.md)
- [菜单与工具栏](08-menus-toolbars.md)
- [核心API与Token参考](../references/core-api-tokens.md)
