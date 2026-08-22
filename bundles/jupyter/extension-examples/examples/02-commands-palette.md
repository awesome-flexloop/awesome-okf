---
type: Example
title: 示例2：添加命令和面板入口
description: 创建一个可从命令面板调用的命令，并添加Launcher卡片
tags: [example, commands, palette, launcher, addCommand]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
status: stable
sources:
  - id: launcher-src
    resource: /references/core-api-tokens.md
    title: launcher/src/index.ts
---

## 目标

在Hello World基础上，注册一个命令到命令面板，并添加Launcher启动卡片。点击时弹出对话框。

## 前置知识

- [命令系统](/concepts/04-commands.md)
- [命令面板与Launcher](/concepts/07-palette-launcher.md)

## 完整代码

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, showDialog, Dialog } from '@jupyterlab/apputils';
import { ILauncher } from '@jupyterlab/launcher';
import { addIcon } from '@jupyterlab/ui-components';

const PLUGIN_ID = '@my-org/my-extension:plugin';

const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  requires: [ICommandPalette],       // 命令面板是必需依赖
  optional: [ILauncher],            // Launcher是可选依赖
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    launcher: ILauncher | null
  ) => {
    const { commands } = app;
    const commandId = 'my-extension:greet';

    // 1. 注册命令
    commands.addCommand(commandId, {
      label: 'Greet from My Extension',
      caption: 'Show a greeting dialog',
      icon: addIcon,
      execute: (args: any) => {
        const origin = args['origin'] || 'unknown';
        showDialog({
          title: 'Hello!',
          body: `Command called from ${origin}!`,
          buttons: [Dialog.okButton()]
        });
      }
    });

    // 2. 添加到命令面板
    const category = 'My Extension';
    palette.addItem({
      command: commandId,
      category,
      args: { origin: 'command palette' }
    });

    // 3. 添加到Launcher（可能为null）
    if (launcher) {
      launcher.add({
        command: commandId,
        category,
        rank: 1
      });
    }
  }
};

export default plugin;
```

## 关键步骤解析

### 依赖声明

```typescript
requires: [ICommandPalette],    // 必须有ICommandPalette才能加载
optional: [ILauncher],          // ILauncher可能不存在
```

在activate函数中，`requires`的参数直接对应，`optional`的参数可能是`null`。

### 命令注册

```typescript
commands.addCommand(commandId, {
  label: 'Greet from My Extension',  // 在面板/菜单中显示的名称
  caption: 'Show a greeting dialog', // 鼠标悬停提示
  icon: addIcon,                     // 内置图标
  execute: (args) => { /* 执行逻辑 */ }
});
```

### 命令面板注册

```typescript
palette.addItem({
  command: commandId,
  category: 'My Extension',
  args: { origin: 'command palette' }
});
```

`args`对象会传递给execute函数，可以用来区分调用来源。

### Launcher注册（null检查）

```typescript
if (launcher) {
  launcher.add({ command: commandId, category, rank: 1 });
}
```

ILauncher是optional，必须null检查。`rank: 1`让卡片排在前面。

## 验证步骤

1. 重新构建：`jlpm build`
2. 刷新JupyterLab（Ctrl+Shift+R强制刷新）
3. 按Ctrl+Shift+C打开命令面板，搜索"Greet"
4. 点击"Greet from My Extension"，应弹出对话框
5. 打开Launcher（File→New Launcher），应看到My Extension分类下有一个卡片
6. 点击Launcher卡片，应弹出对话框

## 常见问题

**Q: Launcher卡片不显示？**
A: 检查是否执行了 `jupyter labextension develop . --overwrite`，并确认构建成功（`jlpm build`无错误）。

**Q: 命令面板中找不到命令？**
A: 确认palette.addItem的category名称正确，在面板中可能需要滚动到对应分类。

**Q: TypeScript编译错误"Cannot find module"？**
A: 运行 `jlpm install` 确保依赖安装完整。

## 下一步

- 添加图标（使用自定义SVG）
- 注册到主菜单（使用schema/plugin.json声明）
- 创建Widget并添加到Shell（参考[示例3：创建自定义Widget](03-custom-widget.md)）

## 相关概念

- [命令系统](/concepts/04-commands.md)
- [命令面板与Launcher](/concepts/07-palette-launcher.md)
- [菜单与工具栏](/concepts/08-menus-toolbars.md)
