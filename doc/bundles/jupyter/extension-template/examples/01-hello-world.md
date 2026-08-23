---
type: Example
title: 你的第一个前端扩展（Hello World）
description: 从零开始创建一个最简前端扩展，学习扩展激活、命令注册、菜单添加和侧边栏 Widget 的完整流程。
tags: [hello-world, frontend, beginner, command, widget, sidebar]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
prerequisites:
  - 完成快速开始：/concepts/01-getting-started.md
related_concepts:
  - /concepts/06-frontend-extension.md
  - /concepts/05-build-system.md
---

## 你的第一个前端扩展（Hello World）

本示例引导你创建一个完整的前端扩展，实现以下功能：
1. 扩展激活时在控制台输出消息
2. 注册一个 "Show Hello" 命令
3. 在命令面板和菜单栏中可访问
4. 点击命令后弹出一个简单的侧边栏面板

## 步骤 1：生成项目

```bash
mkdir hello-extension && cd hello-extension
copier copy --trust https://github.com/jupyterlab/extension-template .
```

Copier 交互时选择：
- extension kind: **frontend**
- JavaScript package name: **hello-extension**
- Python package name: **hello_extension**（自动）
- Does the extension have user settings: **No**
- Do you want to set up tests: **No**（简单示例不需要）
- Include AI assistant rules: **No**

## 步骤 2：安装开发环境

```bash
pip install -e ".[dev]"
jupyter-builder develop . --overwrite
jlpm install
jlpm build
```

## 步骤 3：编写扩展代码

修改 `src/index.ts`：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';

/**
 * 一个简单的 Hello World Widget
 */
class HelloWidget extends Widget {
  constructor() {
    super();
    this.addClass('hello-extension-widget');
    this.id = 'hello-extension-panel';
    this.title.label = 'Hello Panel';
    this.title.closable = true;
    this.node.innerHTML = '<h2>Hello from JupyterLab Extension!</h2>';
  }
}

/**
 * 插件定义
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'hello-extension:plugin',
  description: 'A simple Hello World JupyterLab extension.',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    console.log('JupyterLab extension hello-extension is activated!');

    const { commands, shell } = app;
    const COMMAND_ID = 'hello-extension:show';

    // 注册命令
    commands.addCommand(COMMAND_ID, {
      label: 'Show Hello Panel',
      caption: 'Show the Hello World panel',
      execute: () => {
        // 如果 widget 已存在，激活它
        let widget = new HelloWidget();
        shell.add(widget, 'main');
        shell.activateById(widget.id);
      }
    });

    // 添加到命令面板
    palette.addItem({
      command: COMMAND_ID,
      category: 'Hello Extension'
    });
  }
};

export default plugin;
```

## 步骤 4：添加样式

修改 `style/base.css`：

```css
.hello-extension-widget {
  padding: 16px;
  color: var(--jp-ui-font-color1);
  background: var(--jp-layout-color1);
}

.hello-extension-widget h2 {
  color: var(--jp-brand-color1);
}
```

## 步骤 5：构建并运行

```bash
jlpm run watch  # 终端 1：监听构建
jupyter lab     # 终端 2：启动 JupyterLab
```

## 步骤 6：测试

1. 在浏览器中打开 JupyterLab
2. 按 `Ctrl+Shift+C`（或 `Cmd+Shift+C`）打开命令面板
3. 输入 "Show Hello Panel" 并执行
4. 你应该看到一个 "Hello Panel" 标签页打开，显示 "Hello from JupyterLab Extension!"

## 代码解析

### JupyterFrontEndPlugin

| 字段 | 值 | 说明 |
|------|---|------|
| `id` | `'hello-extension:plugin'` | 唯一标识符，格式为 `<package>:<name>` |
| `autoStart` | `true` | JupyterLab 启动时自动激活 |
| `requires` | `[ICommandPalette]` | 需要注入命令面板服务 |
| `activate` | 函数 | 激活时执行的逻辑 |

### activate 函数

`activate` 接收 `app`（JupyterFrontEnd 实例）和 `requires` 中声明的依赖（这里是 `ICommandPalette`）。

通过 `app.commands` 添加命令，通过 `app.shell` 管理界面布局。

### Widget

Lumino 的 `Widget` 是 JupyterLab UI 的基础单元：
- `addClass()` 添加 CSS 类名
- `title.label` 设置标签页标题
- `title.closable` 允许关闭
- `shell.add(widget, 'main')` 添加到主工作区

## 下一步

- 添加菜单项：使用 `app.commands.addCommand` 的 `isEnabled`/`isToggled` 状态，配合 `IMainMenu` 添加到菜单栏
- 添加快捷键：在 `commands.addKeyBinding()` 中绑定按键
- 添加设置：启用 `has_settings` 并集成 ISettingRegistry
- 参考 [前端扩展开发](/concepts/06-frontend-extension.md) 了解更多 API
