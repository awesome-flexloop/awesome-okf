---
type: Concept
title: 命令面板与Launcher
description: 将命令注册到命令面板（Command Palette）和Launcher启动卡片，让用户能够发现和调用扩展功能
tags: [jupyterlab, command-palette, launcher, ICommandPalette, ILauncher]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: palette-src
    resource: /references/core-api-tokens.md
    title: command-palette/src/index.ts
  - id: launcher-src
    resource: /references/core-api-tokens.md
    title: launcher/src/index.ts
---

## 命令面板（Command Palette）

命令面板是JupyterLab中用户通过Ctrl+Shift+C（或View→Activate Command Palette）打开的搜索式命令列表。将命令注册到面板后，用户可以通过搜索命令名快速执行。

### 注册命令到面板

使用 `ICommandPalette.addItem()` 方法：

```typescript
import { ICommandPalette } from '@jupyterlab/apputils';

const extension: JupyterFrontEndPlugin<void> = {
  id: 'command-palette',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app, palette: ICommandPalette) => {
    const { commands } = app;
    const commandId = 'jlab-examples:command-palette';

    // 1. 先注册命令
    commands.addCommand(commandId, {
      label: 'Execute jlab-examples:command-palette Command',
      execute: (args) => {
        console.log(`called ${args['origin']}.`);
      }
    });

    // 2. 添加到命令面板
    const category = 'Extension Examples';
    palette.addItem({
      command: commandId,
      category,
      args: { origin: 'from palette' }
    });
  }
};
```

### addItem 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `command` | `string` | 已注册的命令ID |
| `category` | `string` | 分类名称（面板中按category分组显示） |
| `args` | `JSONObject` | 调用命令时传递的参数 |
| `rank` | `number` | 排序权重（可选） |

### category 约定

- JupyterLab内置命令使用分类如 "Notebook"、"File"、"Edit"、"View"、"Run"、"Kernel"
- 扩展示例统一使用 `"Extension Examples"` 分类
- 选择有意义的分类名，让用户能在相关分类下找到你的命令

### 动态args传递

`args` 参数在用户从面板调用命令时传入，可以用于区分调用来源：

```typescript
palette.addItem({
  command,
  category,
  args: { origin: 'from palette' }  // 命令execute函数中通过args['origin']获取
});
```

launcher示例展示了更高级的用法：根据args动态改变label和icon：

```typescript
commands.addCommand(command, {
  label: args => args['isPalette'] ? 'New Python File From Extension' : 'Python File',
  icon: args => args['isPalette'] ? undefined : icon,
  execute: async args => { /* ... */ }
});

palette.addItem({
  command,
  args: { isPalette: true },  // 告诉命令是从面板调用的
  category
});
```

## Launcher（启动器）

Launcher是JupyterLab初始页面显示的卡片网格（点击File→New→Launcher也可打开），用户点击卡片创建新文件或打开功能面板。

### 注册Launcher卡片

```typescript
import { ILauncher } from '@jupyterlab/launcher';
import { LabIcon } from '@jupyterlab/ui-components';
import pythonIconStr from '../style/Python-logo-notext.svg';

const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/launcher:plugin',
  autoStart: true,
  requires: [IFileBrowserFactory],
  optional: [ILauncher, ICommandPalette],  // ILauncher是optional!
  activate: (app, browserFactory, launcher, palette) => {
    const { commands } = app;

    // 创建自定义图标
    const icon = new LabIcon({
      name: 'launcher:python-icon',
      svgstr: pythonIconStr
    });

    commands.addCommand(command, {
      label: args => args['isPalette'] ? 'New Python File' : 'Python File',
      caption: 'Create a new Python file',
      icon: args => args['isPalette'] ? undefined : icon,
      execute: async args => {
        const cwd = args['cwd'] || browserFactory.tracker.currentWidget?.model.path;
        const model = await commands.execute('docmanager:new-untitled', {
          path: cwd, type: 'file', ext: 'py'
        });
        return commands.execute('docmanager:open', {
          path: model.path, factory: 'Editor'
        });
      }
    });

    // 添加到Launcher（注意null检查！）
    if (launcher) {
      launcher.add({
        command,
        category: 'Extension Examples',
        rank: 1
      });
    }

    if (palette) {
      palette.addItem({ command, args: { isPalette: true }, category: 'Extension Examples' });
    }
  }
};
```

### launcher.add 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `command` | `string` | 命令ID |
| `category` | `string` | 分类名（如 "Notebook"、"Console"、"Other"） |
| `rank` | `number` | 排序权重（数值越小越靠前） |
| `kernelIconUrl` | `string` | kernel图标URL（可选） |

### ILauncher 是 optional

注意 launcher 示例将 `ILauncher` 放在 `optional` 而非 `requires` 中：

```typescript
optional: [ILauncher, ICommandPalette],
```

原因是在某些环境（如JupyterLite精简配置）中Launcher可能不可用。使用null检查确保扩展不会因为Launcher缺失而无法加载。

### 自定义图标 LabIcon

```typescript
import { LabIcon } from '@jupyterlab/ui-components';
import pythonIconStr from '../style/Python-logo-notext.svg';

const icon = new LabIcon({
  name: 'launcher:python-icon',  // 唯一名称，格式 "namespace:icon-name"
  svgstr: pythonIconStr           // SVG字符串内容（通过import导入）
});
```

然后在命令中使用：
```typescript
icon: args => args['isPalette'] ? undefined : icon,
```

命令面板中通常不显示图标（节省空间），Launcher卡片中显示。

### 使用内置图标

```typescript
import { reactIcon, runIcon, markdownIcon, buildIcon, addIcon, clearIcon, listIcon } from '@jupyterlab/ui-components';
```

常用内置图标：
- `reactIcon`：React原子图标
- `runIcon`：运行按钮图标
- `markdownIcon`：Markdown图标
- `buildIcon`：构建/设置图标
- `addIcon`：添加/新建图标
- `clearIcon`：清除图标
- `listIcon`：列表图标

## Launcher命令的cwd参数

Launcher卡片被点击时，会自动传递 `cwd` 参数（当前工作目录），命令可以使用它在正确目录创建文件：

```typescript
execute: async args => {
  // 如果args中没有cwd，使用文件浏览器当前目录
  const cwd = args['cwd'] || browserFactory.tracker.currentWidget?.model.path;
  const model = await commands.execute('docmanager:new-untitled', {
    path: cwd, type: 'file', ext: 'py'
  });
  return commands.execute('docmanager:open', { path: model.path, factory: 'Editor' });
}
```

## 同时注册到多个UI入口

推荐模式：一个命令，多个入口（Launcher + Command Palette）：

```typescript
commands.addCommand(command, { /* ... */ });

if (launcher) launcher.add({ command, category, rank: 1 });
if (palette) palette.addItem({ command, args: { isPalette: true }, category });
```

这样确保无论用户从哪里发现功能，都能调用同一个命令。

## 相关概念

- [命令系统](/concepts/04-commands.md)
- [Widget与Shell布局](/concepts/05-widgets-shell.md)
- [菜单与工具栏](/concepts/08-menus-toolbars.md)
- [核心API与Token参考](/references/core-api-tokens.md)
