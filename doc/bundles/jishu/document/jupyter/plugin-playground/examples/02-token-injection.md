---
type: Example
title: Token 依赖注入示例
description: 演示如何在插件中使用 requires 和 optional 注入 JupyterLab 服务，包括命令面板、启动器、文件浏览器等常用 Token 的用法。
tags: [jupyterlab, plugin-playground, token, dependency-injection, requires, optional]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T05:08:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-22T05:08:00Z
status: stable
stale_after: 2027-02-22
sources:
  - id: source-index
    resource: /references/source-index.md
    title: Plugin Playground 源码索引
related:
  - id: token-system
    resource: /concepts/06-token-system.md
    title: Token 依赖注入系统
  - id: plugin-loader
    resource: /concepts/05-plugin-loader.md
    title: 插件加载流程
---

## 示例说明

本示例演示如何在 Plugin Playground 中使用 Token 依赖注入获取 JupyterLab 核心服务。展示了三种方式：import Token 类、字符串 Token 名、可选依赖处理。

## 完整代码

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette, MainAreaWidget, Notification } from '@jupyterlab/apputils';
import { ILauncher } from '@jupyterlab/launcher';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { Widget } from '@lumino/widgets';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'token-demo:plugin',
  autoStart: true,
  requires: [ICommandPalette],
  optional: [ILauncher, IMainMenu, IFileBrowserFactory, ISettingRegistry],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    launcher: ILauncher | null,
    mainMenu: IMainMenu | null,
    fileBrowser: IFileBrowserFactory | null,
    settings: ISettingRegistry | null
  ) => {
    // 注册一个打开简单面板的命令
    const command = 'token-demo:open-panel';
    app.commands.addCommand(command, {
      label: 'Token Demo Panel',
      caption: 'Open Token Demo Panel',
      execute: () => {
        const content = new Widget();
        content.node.style.padding = '20px';
        content.node.innerHTML = `
          <h2>Token Injection Demo</h2>
          <ul>
            <li>ICommandPalette: <b>${palette ? '✅ 已注入' : '❌ 不可用'}</b></li>
            <li>ILauncher: <b>${launcher ? '✅ 已注入' : '❌ 不可用'}</b></li>
            <li>IMainMenu: <b>${mainMenu ? '✅ 已注入' : '❌ 不可用'}</b></li>
            <li>IFileBrowserFactory: <b>${fileBrowser ? '✅ 已注入' : '❌ 不可用'}</b></li>
            <li>ISettingRegistry: <b>${settings ? '✅ 已注入' : '❌ 不可用'}</b></li>
          </ul>
          <p>当前活动路径：${fileBrowser?.defaultBrowser?.model?.path ?? 'N/A'}</p>
        `;
        const widget = new MainAreaWidget({ content });
        widget.id = 'token-demo-panel';
        widget.title.label = 'Token Demo';
        widget.title.closable = true;

        if (!widget.isAttached) {
          app.shell.add(widget, 'main');
        }
        app.shell.activateById(widget.id);
      }
    });

    // 1. 添加到命令面板（必需依赖，一定可用）
    palette.addItem({ command, category: 'Token Demo' });

    // 2. 添加到启动器（可选依赖，可能不可用）
    if (launcher) {
      launcher.add({
        command,
        category: 'Other',
        rank: 100
      });
      console.log('[Token Demo] 已添加到 Launcher');
    } else {
      console.log('[Token Demo] Launcher 不可用，跳过启动器项');
    }

    // 3. 添加到主菜单（可选依赖）
    if (mainMenu) {
      const { Menu } = require('@lumino/widgets');
      const demoMenu = new Menu({ commands: app.commands });
      demoMenu.title.label = 'Token Demo';
      demoMenu.addItem({ command });
      mainMenu.addMenu(demoMenu, { rank: 300 });
      console.log('[Token Demo] 已添加到主菜单');
    }

    // 4. 读取设置（可选依赖）
    if (settings) {
      settings.load(plugin.id).then(pluginSettings => {
        console.log('[Token Demo] 已加载设置:', pluginSettings.composite);
      }).catch(err => {
        console.log('[Token Demo] 设置加载失败:', err);
      });
    }

    // 5. 显示通知
    Notification.success('Token Demo 插件已激活！', { autoClose: 2000 });
  }
};

export default plugin;
```

## 关键概念解析

### 参数顺序规则

activate 函数的参数顺序严格对应 `[app, ...requires, ...optional]`：

```
activate(app: JupyterFrontEnd, arg1_from_requires, arg2_from_requires, arg1_from_optional, ...)
```

在本示例中：
1. `app`（固定第一个参数）
2. `palette` ← `requires[0]` = ICommandPalette
3. `launcher` ← `optional[0]` = ILauncher（可能为null）
4. `mainMenu` ← `optional[1]` = IMainMenu（可能为null）
5. `fileBrowser` ← `optional[2]` = IFileBrowserFactory（可能为null）
6. `settings` ← `optional[3]` = ISettingRegistry（可能为null）

### 必需 vs 可选依赖

| 依赖类型 | Token 找不到时 | 参数类型 | 使用方式 |
|---------|---------------|---------|---------|
| `requires` | 抛出错误，插件加载失败 | 非 null 类型 | 直接使用，无需判空 |
| `optional` | 传入 null，插件继续加载 | `T \| null` | 必须判空检查 |

### 字符串 Token 名写法

除了 import Token 类，你也可以使用字符串形式。以下两种写法效果相同：

```typescript
// 方式1：import Token（推荐，有类型提示）
import { ICommandPalette } from '@jupyterlab/apputils';
requires: [ICommandPalette]

// 方式2：字符串名（无需import）
requires: ['@jupyterlab/apputils:ICommandPalette']
```

字符串名格式为 `'{包名}:{导出名}'`。在 Plugin Playground 的 Extension Points 侧边栏中可以浏览所有可用 Token 的字符串名。

## 常用 Token 速查表

| Token | 字符串名 | 包 | 功能 |
|-------|---------|-----|------|
| ICommandPalette | `@jupyterlab/apputils:ICommandPalette` | @jupyterlab/apputils | 命令面板 |
| ILauncher | `@jupyterlab/launcher:ILauncher` | @jupyterlab/launcher | 启动器页 |
| IMainMenu | `@jupyterlab/mainmenu:IMainMenu` | @jupyterlab/mainmenu | 主菜单栏 |
| IFileBrowserFactory | `@jupyterlab/filebrowser:IFileBrowserFactory` | @jupyterlab/filebrowser | 文件浏览器 |
| ISettingRegistry | `@jupyterlab/settingregistry:ISettingRegistry` | @jupyterlab/settingregistry | 设置系统 |
| IStateDB | `@jupyterlab/statedb:IStateDB` | @jupyterlab/statedb | 状态数据库 |
| ITranslator | `@jupyterlab/translation:ITranslator` | @jupyterlab/translation | 国际化翻译 |
| INotebookTracker | `@jupyterlab/notebook:INotebookTracker` | @jupyterlab/notebook | Notebook追踪器 |
| IEditorTracker | `@jupyterlab/fileeditor:IEditorTracker` | @jupyterlab/fileeditor | 编辑器追踪器 |
| IRenderMimeRegistry | `@jupyterlab/rendermime:IRenderMimeRegistry` | @jupyterlab/rendermime | MIME渲染注册表 |

## 运行步骤

1. 在 Plugin Playground 中创建新文件 `token-demo.ts`
2. 粘贴完整代码
3. 点击 **Load As Extension**
4. 你将看到：
   - 通知中心弹出成功提示
   - 命令面板中出现 "Token Demo Panel" 命令（在 "Token Demo" 分类下）
   - 如果 Launcher 可用，启动器中会出现 "Token Demo Panel" 项
   - 如果 MainMenu 可用，菜单栏会新增 "Token Demo" 菜单
5. 执行命令，会打开一个面板显示各 Token 的注入状态

## 常见错误

### 参数顺序不匹配

**错误**：在 requires/optional 中添加了Token但忘记在activate参数中添加对应参数。

**症状**：后续的所有参数都会错位，导致运行时错误或 `undefined` 值。

**解决**：确保 activate 参数数量和顺序与 `[app, ...requires, ...optional]` 严格对应。

### 直接使用 optional 参数而不判空

**错误**：`launcher.add(...)` 而不检查 `if (launcher)`。

**症状**：当 ILauncher 不可用时抛出 `TypeError: Cannot read property 'add' of null`。

**解决**：始终对 optional 参数进行判空检查。

### Token 名拼写错误

**错误**：`requires: ['@jupyterlab/apputils:CommandPalette']`（少了 `I` 前缀）。

**症状**：加载时报 "Required token ... not found" 错误。

**解决**：JupyterLab Token 类名通常以 `I` 开头（ICommandPalette、ILauncher 等）。参考 Extension Points 侧边栏获取准确名称。

## 进阶：provides 提供服务

除了消费其他插件的服务，你的插件也可以提供服务给其他插件使用：

```typescript
import { Token } from '@lumino/coreutils';

// 定义服务接口
interface IGreeter {
  greet(name: string): string;
}

// 创建 Token（字符串名格式：'{插件id}:{Token名}'）
const IGreeter = new Token<IGreeter>('token-demo:IGreeter');

const servicePlugin: JupyterFrontEndPlugin<IGreeter> = {
  id: 'token-demo:greeter',
  autoStart: true,
  provides: IGreeter,
  activate: (app): IGreeter => {
    return {
      greet: (name: string) => `Hello, ${name}!`
    };
  }
};

// 另一个插件可以消费这个服务
const consumerPlugin: JupyterFrontEndPlugin<void> = {
  id: 'token-demo:consumer',
  autoStart: true,
  requires: [IGreeter],
  activate: (app, greeter) => {
    console.log(greeter.greet('Plugin Playground'));
  }
};

// 导出插件数组
export default [servicePlugin, consumerPlugin];
```

注意：在同一文件中提供和消费同一个 Token 时，要确保服务插件在消费者之前（数组顺序决定加载顺序）。

## 预期结果

- ✅ 插件加载成功，通知显示 "Token Demo 插件已激活"
- ✅ 命令面板中 "Token Demo" 分类下有 "Token Demo Panel" 命令
- ✅ 执行命令后主区域打开一个面板，显示各Token状态
- ✅ Launcher/主菜单根据可用性显示或跳过
