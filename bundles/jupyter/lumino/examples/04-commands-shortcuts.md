---
type: Example
title: 命令与快捷键绑定
description: 注册命令、绑定快捷键、关联菜单和命令面板、动态命令状态
tags: [lumino, commands, keybinding, menu, command-palette, actions]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:15:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: commands-source
    resource: /external/libs/jupyter/lumino/packages/commands/src/index.ts
    title: @lumino/commands 源码
prerequisites:
  - /lumino/concepts/07-command-system
  - /lumino/concepts/05-widget-lifecycle
---

# 示例：命令与快捷键绑定

本示例演示如何使用 CommandRegistry 注册命令、绑定快捷键、创建菜单和命令面板。

## 完整代码

```typescript
import { CommandRegistry } from '@lumino/commands';
import {
  Widget, Menu, MenuBar, CommandPalette, BoxPanel, BoxLayout
} from '@lumino/widgets';
import '@lumino/default-theme/style/index.css';

// 1. 创建命令注册表
const commands = new CommandRegistry();

// 2. 定义应用状态
const appState = {
  currentFile: '' as string,
  isModified: false,
  clipboard: '' as string,
  editorContent: 'Welcome to Lumino!',
};

// 3. 注册命令

// 新建文件
commands.addCommand('file:new', {
  label: '新建文件',
  mnemonic: 0,  // Alt+N
  execute: () => {
    appState.currentFile = '';
    appState.editorContent = '';
    appState.isModified = false;
    updateEditor();
    commands.notifyCommandChanged('file:save');
  },
});

// 打开文件
commands.addCommand('file:open', {
  label: '打开...',
  mnemonic: 0,
  execute: () => {
    const name = prompt('输入文件名:');
    if (name) {
      appState.currentFile = name;
      appState.editorContent = `// ${name}\n`;
      appState.isModified = false;
      updateEditor();
      commands.notifyCommandChanged('file:save');
    }
  },
});

// 保存 - 动态isEnabled状态
commands.addCommand('file:save', {
  label: '保存',
  mnemonic: 0,
  isEnabled: () => appState.isModified || !appState.currentFile,
  execute: () => {
    if (!appState.currentFile) {
      const name = prompt('另存为:');
      if (name) appState.currentFile = name;
    }
    appState.isModified = false;
    console.log('已保存:', appState.currentFile);
    commands.notifyCommandChanged('file:save');
  },
});

// 退出
commands.addCommand('file:exit', {
  label: '退出',
  execute: () => {
    if (appState.isModified) {
      if (!confirm('有未保存的更改，确定退出？')) return;
    }
    window.close();
  },
});

// 编辑命令
commands.addCommand('edit:undo', {
  label: '撤销',
  execute: () => console.log('撤销操作'),
});

commands.addCommand('edit:copy', {
  label: '复制',
  isEnabled: () => !!window.getSelection()?.toString(),
  execute: () => {
    appState.clipboard = window.getSelection()?.toString() ?? '';
  },
});

commands.addCommand('edit:paste', {
  label: '粘贴',
  isEnabled: () => !!appState.clipboard,
  execute: () => {
    console.log('粘贴:', appState.clipboard);
  },
});

// 视图切换 - 使用isToggled
commands.addCommand('view:toggle-sidebar', {
  label: '切换侧边栏',
  isToggled: () => sidebarVisible,
  execute: () => {
    sidebarVisible = !sidebarVisible;
    sidebar.setHidden(!sidebarVisible);
    commands.notifyCommandChanged('view:toggle-sidebar');
  },
});

// 主题切换
commands.addCommand('view:theme-dark', {
  label: '深色主题',
  isToggled: () => currentTheme === 'dark',
  execute: () => {
    setTheme('dark');
    commands.notifyCommandChanged('view:theme-dark');
    commands.notifyCommandChanged('view:theme-light');
  },
});

commands.addCommand('view:theme-light', {
  label: '浅色主题',
  isToggled: () => currentTheme === 'light',
  execute: () => {
    setTheme('light');
    commands.notifyCommandChanged('view:theme-dark');
    commands.notifyCommandChanged('view:theme-light');
  },
});

// Hello命令（带快捷键演示）
commands.addCommand('app:hello', {
  label: 'Hello World',
  caption: '向控制台输出Hello World',
  execute: () => console.log('Hello, Lumino Commands!'),
});

// 4. 绑定快捷键
commands.addKeyBinding({
  command: 'file:new',
  keys: ['Accel N'],
  selector: 'body',
});

commands.addKeyBinding({
  command: 'file:open',
  keys: ['Accel O'],
  selector: 'body',
});

commands.addKeyBinding({
  command: 'file:save',
  keys: ['Accel S'],
  selector: 'body',
});

commands.addKeyBinding({
  command: 'edit:copy',
  keys: ['Accel C'],
  selector: 'body',
});

commands.addKeyBinding({
  command: 'edit:paste',
  keys: ['Accel V'],
  selector: 'body',
});

commands.addKeyBinding({
  command: 'edit:undo',
  keys: ['Accel Z'],
  selector: 'body',
});

commands.addKeyBinding({
  command: 'app:hello',
  keys: ['Accel Shift H'],
  selector: 'body',
});

// 5. 创建菜单
function createMenuBar(): MenuBar {
  const menuBar = new MenuBar();

  // 文件菜单
  const fileMenu = new Menu({ commands });
  fileMenu.title.label = '文件';
  fileMenu.title.mnemonic = 0;
  fileMenu.addItem({ command: 'file:new' });
  fileMenu.addItem({ command: 'file:open' });
  fileMenu.addItem({ command: 'file:save' });
  fileMenu.addItem({ type: 'separator' });
  fileMenu.addItem({ command: 'file:exit' });

  // 编辑菜单
  const editMenu = new Menu({ commands });
  editMenu.title.label = '编辑';
  editMenu.title.mnemonic = 0;
  editMenu.addItem({ command: 'edit:undo' });
  editMenu.addItem({ type: 'separator' });
  editMenu.addItem({ command: 'edit:copy' });
  editMenu.addItem({ command: 'edit:paste' });

  // 视图菜单
  const viewMenu = new Menu({ commands });
  viewMenu.title.label = '视图';
  viewMenu.title.mnemonic = 0;
  viewMenu.addItem({ command: 'view:toggle-sidebar' });
  viewMenu.addItem({ type: 'separator' });
  const themeSubmenu = new Menu({ commands });
  themeSubmenu.title.label = '主题';
  themeSubmenu.addItem({ command: 'view:theme-light' });
  themeSubmenu.addItem({ command: 'view:theme-dark' });
  viewMenu.addItem({ type: 'submenu', submenu: themeSubmenu });

  // 帮助菜单
  const helpMenu = new Menu({ commands });
  helpMenu.title.label = '帮助';
  helpMenu.addItem({ command: 'app:hello' });

  menuBar.addMenu(fileMenu);
  menuBar.addMenu(editMenu);
  menuBar.addMenu(viewMenu);
  menuBar.addMenu(helpMenu);

  return menuBar;
}

// 6. 创建命令面板
function createPalette(): CommandPalette {
  const palette = new CommandPalette({ commands });
  palette.addItem({ command: 'file:new', category: 'File' });
  palette.addItem({ command: 'file:open', category: 'File' });
  palette.addItem({ command: 'file:save', category: 'File' });
  palette.addItem({ command: 'edit:copy', category: 'Edit' });
  palette.addItem({ command: 'edit:paste', category: 'Edit' });
  palette.addItem({ command: 'edit:undo', category: 'Edit' });
  palette.addItem({ command: 'view:toggle-sidebar', category: 'View' });
  palette.addItem({ command: 'view:theme-dark', category: 'View' });
  palette.addItem({ command: 'view:theme-light', category: 'View' });
  palette.addItem({ command: 'app:hello', category: 'Help' });
  return palette;
}

// 7. UI状态
let sidebarVisible = true;
let currentTheme: 'light' | 'dark' = 'light';

// 创建编辑器Widget
const editor = new Widget();
editor.addClass('editor');
editor.node.innerHTML = '<textarea style="width:100%;height:100%;border:none;resize:none;padding:8px;"></textarea>';

const sidebar = new Widget();
sidebar.addClass('sidebar');
sidebar.node.innerHTML = '<h3>侧边栏</h3><p>文件浏览器占位</p>';

function updateEditor(): void {
  const textarea = editor.node.querySelector('textarea')!;
  textarea.value = appState.editorContent;
}

function setTheme(theme: 'light' | 'dark'): void {
  currentTheme = theme;
  document.body.classList.toggle('dark-theme', theme === 'dark');
}

// 8. 组装界面
function main(): void {
  const menuBar = createMenuBar();
  const palette = createPalette();

  // Ctrl+Shift+P打开命令面板
  commands.addCommand('app:toggle-palette', {
    execute: () => {
      if (palette.isAttached) {
        palette.parent = null;
      } else {
        palette.show();
        palette.node.style.position = 'fixed';
        palette.node.style.top = '40px';
        palette.node.style.left = '50%';
        palette.node.style.transform = 'translateX(-50%)';
        palette.node.style.width = '500px';
        palette.node.style.zIndex = '1000';
        document.body.appendChild(palette.node);
        palette.inputNode.focus();
      }
    },
  });
  commands.addKeyBinding({
    command: 'app:toggle-palette',
    keys: ['Accel Shift P'],
    selector: 'body',
  });

  // 主布局
  const root = new BoxPanel({ direction: 'top-to-bottom', spacing: 0 });
  root.id = 'app-root';
  root.addWidget(menuBar);
  BoxPanel.setStretch(menuBar, 0);

  const body = new BoxPanel({ direction: 'left-to-right', spacing: 0 });
  body.addWidget(sidebar);
  BoxPanel.setStretch(sidebar, 0);
  sidebar.node.style.width = '200px';
  body.addWidget(editor);
  BoxPanel.setStretch(editor, 1);

  root.addWidget(body);
  BoxPanel.setStretch(body, 1);

  Widget.attach(root, document.body);

  // 绑定键盘事件到整个文档
  document.addEventListener('keydown', (event) => {
    commands.processKeydownEvent(event);
  });

  // 编辑器事件
  const textarea = editor.node.querySelector('textarea')!;
  textarea.addEventListener('input', () => {
    appState.editorContent = textarea.value;
    appState.isModified = true;
    commands.notifyCommandChanged('file:save');
  });

  updateEditor();
}

window.addEventListener('DOMContentLoaded', main);
```

## 关键点说明

### 1. Accel 修饰符：跨平台快捷键

```typescript
keys: ['Accel S']
// macOS 上自动映射为 Cmd+S
// Windows/Linux 上自动映射为 Ctrl+S
```

始终使用 `Accel` 而非硬编码 `Ctrl` 或 `Cmd`，确保快捷键在各平台符合用户习惯。

### 2. 动态状态：isEnabled / isToggled

```typescript
isEnabled: () => appState.isModified || !appState.currentFile,
isToggled: () => sidebarVisible,
```

状态函数在菜单显示、命令面板渲染、快捷键触发时被调用。状态变化时必须调用 `notifyCommandChanged(id)` 通知 UI 刷新。

### 3. notifyCommandChanged 的时机

```typescript
// 修改影响命令状态的数据后
appState.isModified = false;
commands.notifyCommandChanged('file:save');  // 通知file:save状态变化

// 切换主题影响两个命令
setTheme('dark');
commands.notifyCommandChanged('view:theme-dark');
commands.notifyCommandChanged('view:theme-light');
```

### 4. 键盘事件绑定

CommandRegistry 本身不自动绑定键盘事件，需要在 Application 或手动绑定：

```typescript
document.addEventListener('keydown', (event) => {
  commands.processKeydownEvent(event);
});
```

Application.start() 会自动绑定此事件。如果不使用 Application，则需要手动绑定。

### 5. Selector 的作用域

```typescript
selector: 'body',          // 全局
selector: '.editor',       // 仅在.editor内有效
selector: 'input, textarea' // 在可编辑元素内
```

selector 使用 CSS 选择器，Lumino 计算选择器特异性来决定哪个快捷键优先。

## 运行效果

- 菜单栏：文件/编辑/视图/帮助菜单，包含子菜单和分隔线
- 快捷键：Ctrl+N/O/S/Z/C/V、Ctrl+Shift+H、Ctrl+Shift+P 均可使用
- 命令面板：Ctrl+Shift+P 打开，输入过滤命令
- 动态状态：未修改时"保存"禁用，侧边栏/主题切换显示勾选状态

## 扩展练习

1. 添加"另存为"命令，使用 args 参数区分保存和另存为
2. 为复制/粘贴添加 ContextMenu（右键菜单）支持
3. 添加更多键绑定，支持多键序列（如 Ctrl+K Ctrl+C）
4. 实现命令执行后的撤销/重做栈
