---
type: Concept
title: 菜单与工具栏
description: 通过JSON Schema声明和代码注册两种方式，向主菜单、右键菜单、Notebook工具栏和Cell工具栏添加按钮
tags: [jupyterlab, menu, toolbar, context-menu, cell-toolbar, schema]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: main-menu-src
    resource: /references/core-api-tokens.md
    title: main-menu/src/index.ts
  - id: context-menu-src
    resource: /references/core-api-tokens.md
    title: context-menu/src/index.ts
  - id: toolbar-src
    resource: /references/plugin-anatomy.md
    title: toolbar-button/schema/plugin.json
  - id: cell-toolbar-src
    resource: /references/core-api-tokens.md
    title: cell-toolbar/src/index.ts
---

## 两种菜单/工具栏注册方式

JupyterLab 支持两种方式添加菜单和工具栏项：

1. **Schema声明式**（`schema/plugin.json`）：通过JSON Schema声明菜单项、工具栏按钮，简单直观
2. **代码命令式**：通过注册命令配合动态可见性/启用状态控制，适用于复杂逻辑

## 主菜单

主菜单项通过 `schema/plugin.json` 中的 `jupyter.lab.menus` 声明。main-menu示例虽然在README中描述了菜单添加，但实际使用命令面板作为入口。更复杂的菜单通过schema声明。

### 菜单声明结构

在 `schema/plugin.json` 中添加：

```json
{
  "jupyter.lab.menus": {
    "main": [
      {
        "id": "jp-mainmenu-example",
        "label": "Example Menu",
        "rank": 80,
        "items": [
          {
            "command": "jlab-examples:main-menu",
            "args": { "origin": "from the menu" }
          }
        ]
      }
    ]
  }
}
```

### 主菜单rank参考值

| 内置菜单 | rank |
|---------|------|
| File | 1 |
| Edit | 2 |
| View | 3 |
| Run | 4 |
| Kernel | 5 |
| Tabs | 6 |
| Settings | 7 |
| Help | 1000 |

扩展菜单通常放在 Settings 和 Help 之间（rank 8-999）。

## 右键上下文菜单

context-menu示例展示了如何向文件浏览器的右键菜单添加项目：

```typescript
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { showDialog, Dialog } from '@jupyterlab/apputils';
import { buildIcon } from '@jupyterlab/ui-components';

const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/context-menu:plugin',
  autoStart: true,
  requires: [IFileBrowserFactory],
  activate: (app, factory: IFileBrowserFactory) => {
    app.commands.addCommand('jlab-examples/context-menu:open', {
      label: 'Example',
      caption: "Example context menu button for file browser's items.",
      icon: buildIcon,
      execute: () => {
        // 获取当前选中的文件
        const file = factory.tracker.currentWidget
          ?.selectedItems()
          .next().value;

        if (file) {
          showDialog({
            title: file.name,
            body: 'Path: ' + file.path,
            buttons: [Dialog.okButton()]
          }).catch(e => console.log(e));
        }
      }
    });
  }
};
```

context-menu的项目通常通过schema声明（在 `jupyter.lab.context-menu` 中），将命令绑定到特定的上下文菜单选择器。

### 通过Schema声明上下文菜单

```json
{
  "jupyter.lab.menus": {
    "context": [
      {
        "command": "jlab-examples/context-menu:open",
        "selector": ".jp-DirListing-item",
        "rank": 10
      }
    ]
  }
}
```

`selector` 是CSS选择器，指定在哪些DOM元素上右键时显示此菜单项。

## Notebook工具栏按钮

toolbar-button示例展示了最简单的方式——通过schema声明：

```json
{
  "jupyter.lab.toolbars": {
    "Notebook": [
      {
        "name": "clear-all-outputs",
        "command": "notebook:clear-all-cell-outputs"
      }
    ]
  },
  "title": "@jupyterlab-examples/toolbar-button",
  "type": "object",
  "properties": {},
  "additionalProperties": false
}
```

插件的activate函数可以是空的，因为所有配置都通过schema声明：

```typescript
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/toolbar-button:plugin',
  autoStart: true,
  activate: () => {
    // 无需代码！工具栏按钮通过schema/plugin.json声明
  }
};
```

### 工具栏声明结构

```json
{
  "jupyter.lab.toolbars": {
    "<FactoryName>": [
      {
        "name": "<unique-button-name>",
        "command": "<command-id>",
        "rank": <number>  // 可选，控制排序
      }
    ]
  }
}
```

常用Factory名称：
- `"Notebook"`：Notebook面板工具栏
- `"Cell"`：Cell工具栏（需要代码配合）
- `"Editor"`：文本编辑器工具栏
- 自定义DocumentWidget的factory名称

## Cell工具栏按钮

cell-toolbar示例展示了更复杂的模式——根据cell类型动态显示按钮：

```typescript
import { INotebookTracker } from '@jupyterlab/notebook';

const CommandIds = {
  renderMarkdownCell: 'toolbar-button:render-markdown-cell',
  runCodeCell: 'toolbar-button:run-code-cell'
};

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/cell-toolbar:plugin',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app, tracker: INotebookTracker) => {
    const { commands } = app;

    // 代码cell按钮：只在code cell上可见
    commands.addCommand(CommandIds.runCodeCell, {
      icon: runIcon,
      caption: 'Run a code cell',
      execute: () => { commands.execute('notebook:run-cell'); },
      isVisible: () => tracker.activeCell?.model.type === 'code'
    });

    // Markdown cell按钮：只在markdown cell上可见
    commands.addCommand(CommandIds.renderMarkdownCell, {
      icon: markdownIcon,
      caption: 'Render a markdown cell',
      execute: () => { commands.execute('notebook:run-cell'); },
      isVisible: () => tracker.activeCell?.model.type === 'markdown'
    });
  }
};
```

关键技术：
1. 使用 `INotebookTracker` 获取当前活动cell
2. 通过 `tracker.activeCell?.model.type` 判断cell类型（`'code'`/`'markdown'`/`'raw'`）
3. 使用 `isVisible` 动态控制按钮显示
4. Cell工具栏项通过schema的 `jupyter.lab.toolbars.Cell` 声明

## 对话框

context-menu示例使用了 `showDialog` 显示信息对话框：

```typescript
import { showDialog, Dialog } from '@jupyterlab/apputils';

showDialog({
  title: 'Dialog Title',
  body: 'Dialog body content',
  buttons: [Dialog.okButton()],
}).then(result => {
  if (result.button.accept) {
    // 用户点击OK
  }
});
```

### InputDialog：获取用户输入

state示例使用 `InputDialog.getItem()` 获取用户选择：

```typescript
import { InputDialog } from '@jupyterlab/apputils';

const result = await InputDialog.getItem({
  title: 'Pick an option',
  items: ['one', 'two', 'three'],
  current: 0  // 默认选中索引
});

if (result.button.accept) {
  const option = result.value;
}
```

InputDialog提供多种输入方式：
- `getText()`：文本输入
- `getNumber()`：数字输入
- `getItem()`：下拉选择
- `getBoolean()`：布尔确认

## showDialog按钮类型

| 按钮 | 说明 |
|------|------|
| `Dialog.okButton()` | 确定按钮 |
| `Dialog.cancelButton()` | 取消按钮 |
| `Dialog.warnButton()` | 警告按钮（红色） |
| 自定义按钮 | `Dialog.createButton({ label, icon?, className?, accept? })` |

## 相关概念

- [命令系统](04-commands.md)
- [命令面板与Launcher](07-palette-launcher.md)
- [通知系统与日志](10-notifications-logging.md)
- [核心API与Token参考](../references/core-api-tokens.md)
