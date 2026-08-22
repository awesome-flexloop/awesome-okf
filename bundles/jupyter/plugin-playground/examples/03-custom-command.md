---
type: Example
title: 自定义命令与UI面板
description: 创建包含自定义命令、侧边栏面板、主区域Widget、键盘快捷键的完整插件示例，展示 Lumino Widget 系统与 JupyterLab UI 集成。
tags: [jupyterlab, plugin-playground, command, widget, panel, lumino, ui]
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
  - id: plugin-basics
    resource: /concepts/02-plugin-basics.md
    title: JupyterLab 插件基础结构
  - id: token-system
    resource: /concepts/06-token-system.md
    title: Token 依赖注入系统
---

## 示例说明

本示例创建一个功能较完整的插件，包含：
1. 多个自定义命令
2. 命令面板分类
3. 主区域 Widget（使用 React 渲染简单 UI）
4. 侧边栏面板
5. 键盘快捷键
6. 命令状态管理（isEnabled/isToggled/ isVisible）

## 完整代码

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette, MainAreaWidget, ReactWidget } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';
import React from 'react';

// --- React 组件 ---
class CounterWidget extends ReactWidget {
  private _count = 0;

  render(): JSX.Element {
    return React.createElement(
      'div',
      { style: { padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px', alignItems: 'center' } },
      React.createElement('h2', { key: 'title' }, '计数器面板'),
      React.createElement(
        'div',
        { key: 'counter', style: { fontSize: '48px', fontWeight: 'bold', color: '#1976d2' } },
        this._count
      ),
      React.createElement(
        'div',
        { key: 'buttons', style: { display: 'flex', gap: '8px' } },
        React.createElement(
          'button',
          {
            key: 'dec',
            onClick: () => { this._count--; this.update(); },
            style: { padding: '8px 16px', fontSize: '18px', cursor: 'pointer' }
          },
          '−'
        ),
        React.createElement(
          'button',
          {
            key: 'inc',
            onClick: () => { this._count++; this.update(); },
            style: { padding: '8px 16px', fontSize: '18px', cursor: 'pointer' }
          },
          '+'
        ),
        React.createElement(
          'button',
          {
            key: 'reset',
            onClick: () => { this._count = 0; this.update(); },
            style: { padding: '8px 16px', fontSize: '14px', cursor: 'pointer' }
          },
          '重置'
        )
      )
    );
  }
}

// --- 侧边栏信息面板 ---
class SidebarInfoWidget extends Widget {
  constructor() {
    super();
    this.node.style.padding = '12px';
    this.node.innerHTML = `
      <div style="font-size: 13px; color: #666;">
        <h3 style="margin-top: 0;">命令演示</h3>
        <p>本插件演示了：</p>
        <ul style="padding-left: 18px; margin: 4px 0;">
          <li>自定义命令注册</li>
          <li>命令状态控制</li>
          <li>主区域Widget</li>
          <li>侧边栏面板</li>
          <li>键盘快捷键</li>
        </ul>
        <p style="margin-top: 12px;">快捷键: <b>Ctrl+Shift+X</b></p>
      </div>
    `;
  }
}

// --- 插件定义 ---
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'custom-command-demo:plugin',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    const category = 'Command Demo';
    let mainWidget: MainAreaWidget<CounterWidget> | null = null;
    let isToggled = false;

    // 命令1：打开计数器面板
    const openCmd = 'cmd-demo:open-counter';
    app.commands.addCommand(openCmd, {
      label: '打开计数器面板',
      caption: '在主区域打开一个计数器面板',
      execute: () => {
        // 如果面板已存在，激活它
        if (mainWidget && !mainWidget.isDisposed) {
          app.shell.activateById(mainWidget.id);
          return;
        }
        // 创建新面板
        const content = new CounterWidget();
        content.addClass('cmd-demo-counter');
        mainWidget = new MainAreaWidget({ content });
        mainWidget.id = 'cmd-demo-counter-widget';
        mainWidget.title.label = '计数器';
        mainWidget.title.closable = true;
        mainWidget.disposed.connect(() => {
          mainWidget = null;
        });
        app.shell.add(mainWidget, 'main');
        app.shell.activateById(mainWidget.id);
      }
    });

    // 命令2：切换状态的命令（模拟开关）
    const toggleCmd = 'cmd-demo:toggle';
    app.commands.addCommand(toggleCmd, {
      label: '切换状态',
      caption: '演示 isToggled 状态',
      isToggled: () => isToggled,
      execute: () => {
        isToggled = !isToggled;
        app.commands.notifyCommandChanged(toggleCmd);
        console.log('[Cmd Demo] 状态:', isToggled ? 'ON' : 'OFF');
      }
    });

    // 命令3：带条件启用的命令
    const conditionCmd = 'cmd-demo:conditional';
    app.commands.addCommand(conditionCmd, {
      label: '条件命令',
      caption: '仅在面板打开时可用',
      isEnabled: () => mainWidget !== null && !mainWidget.isDisposed,
      execute: () => {
        console.log('[Cmd Demo] 条件命令执行');
        alert('面板是打开的！');
      }
    });

    // 命令4：显示通知
    const notifyCmd = 'cmd-demo:notify';
    app.commands.addCommand(notifyCmd, {
      label: '显示通知',
      caption: '弹出一个通知消息',
      execute: () => {
        const { Notification } = require('@jupyterlab/apputils');
        Notification.info('这是一个来自命令演示的通知！', {
          autoClose: 3000
        });
      }
    });

    // 添加到命令面板
    palette.addItem({ command: openCmd, category });
    palette.addItem({ command: toggleCmd, category });
    palette.addItem({ command: conditionCmd, category });
    palette.addItem({ command: notifyCmd, category });

    // 添加键盘快捷键
    app.commands.addKeyBinding({
      command: openCmd,
      keys: ['Ctrl Shift X'],
      selector: 'body'
    });

    // 添加侧边栏面板
    const sidebarWidget = new SidebarInfoWidget();
    sidebarWidget.id = 'cmd-demo-sidebar';
    sidebarWidget.title.iconClass = 'jp-BuildIcon jp-SideBar-tabIcon';
    sidebarWidget.title.caption = '命令演示';
    app.shell.add(sidebarWidget, 'left');

    // 定期刷新条件命令的启用状态（当面板关闭/打开时）
    // 注意：通常通过信号(signal)来通知，这里用定时器简化演示
    setInterval(() => {
      app.commands.notifyCommandChanged(conditionCmd);
    }, 1000);

    console.log('[Cmd Demo] 插件已激活');
  }
};

export default plugin;
```

## 关键技术点解析

### 1. 命令选项详解

`addCommand(id, options)` 的常用选项：

| 选项 | 类型 | 说明 |
|------|------|------|
| `label` | string \| () => string | 命令显示名称（命令面板/菜单中） |
| `caption` | string \| () => string | 鼠标悬停提示 |
| `execute` | (args) => any | 命令执行函数 |
| `isEnabled` | () => boolean | 命令是否可用（灰色禁用） |
| `isToggled` | () => boolean | 命令是否切换为激活状态（勾选标记） |
| `isVisible` | () => boolean | 命令是否可见 |
| `iconClass` | string | 图标CSS类 |
| `iconLabel` | string | 图标标签 |
| `usage` | string | 使用说明文本（命令补全文档） |

当 `isEnabled`/`isToggled` 状态变化时，需要调用 `app.commands.notifyCommandChanged(commandId)` 通知UI更新。

### 2. Widget 类型

| Widget类型 | 用途 | 特点 |
|-----------|------|------|
| `Widget` (Lumino) | 基础Widget | 直接操作DOM，`this.node` 访问DOM节点 |
| `ReactWidget` | React渲染 | 重写 `render()` 方法返回JSX，调用 `this.update()` 触发重渲染 |
| `MainAreaWidget<T>` | 主区域容器 | 包含标题栏、工具栏、closable属性，包裹content widget |

### 3. Shell 区域

`app.shell.add(widget, area)` 将 Widget 添加到不同区域：

| 区域 | 位置 | 典型用途 |
|------|------|---------|
| `'main'` | 中央主区域 | 文档、编辑器、面板 |
| `'left'` | 左侧边栏 | 文件浏览器、Extension Points等 |
| `'right'` | 右侧边栏 | 属性面板、检查器 |
| `'top'` | 顶部 | 工具栏 |
| `'bottom'` | 底部 | 状态栏下方区域 |

侧边栏 Widget 的 `title.caption` 和 `title.iconClass` 控制标签页显示。

### 4. 单例Widget模式

使用 `if (mainWidget && !mainWidget.isDisposed)` 检查并激活已有 Widget，而非重复创建：

```typescript
execute: () => {
  if (mainWidget && !mainWidget.isDisposed) {
    app.shell.activateById(mainWidget.id);  // 激活已有
    return;
  }
  // 创建新的...
  mainWidget.disposed.connect(() => {
    mainWidget = null;  // Widget销毁时清空引用
  });
}
```

这是 JupyterLab 插件的常见模式，避免重复打开多个相同面板。

### 5. 键盘快捷键

```typescript
app.commands.addKeyBinding({
  command: openCmd,
  keys: ['Ctrl Shift X'],
  selector: 'body'
});
```

- `keys`：快捷键数组，支持 `Ctrl`、`Alt`、`Shift`、`Accel`（Mac上为Cmd，其他为Ctrl）
- `selector`：CSS选择器，限定快捷键生效的元素范围
- 多个keys表示不同的快捷键绑定到同一命令

## 运行步骤

1. 创建文件 `cmd-demo.ts`
2. 粘贴代码并加载
3. 在命令面板中搜索 "Command Demo" 分类
4. 执行 "打开计数器面板" 或按 `Ctrl+Shift+X`
5. 观察：
   - 左侧边栏新增"命令演示"面板
   - 主区域打开计数器面板
   - "条件命令"在面板打开后变为可用
   - "切换状态"命令可切换勾选状态

## 常见问题

### ReactWidget 中 React.createElement 太繁琐

Plugin Playground 环境中默认没有 JSX 编译支持（除非你的代码被TypeScript转译）。如果要使用JSX语法，可以：
1. 使用 `React.createElement` 直接调用（如本例所示）
2. 或者使用纯 DOM 操作（如 SidebarInfoWidget 所示）
3. 或者使用 `h()` 函数（如果有 hyperscript 库可用）

### Widget 无法关闭

确保设置了 `widget.title.closable = true`，否则标题栏不会显示关闭按钮。

### 快捷键不生效

检查：
1. `selector` 是否覆盖了当前焦点元素（`'body'` 全局生效）
2. 快捷键是否被其他绑定覆盖
3. 浏览器是否拦截了该快捷键（如 `Ctrl+T` 是新建标签页）

## 扩展练习

1. 添加一个命令，在计数器面板打开时显示当前计数值
2. 添加一个 `'right'` 区域的侧边栏面板
3. 给命令添加 `iconClass`（使用 JupyterLab 内置图标类，如 `'jp-FileIcon'`）
4. 使用 Lumino Signal 替代 setInterval 来通知命令状态变化

## 预期结果

- ✅ 左侧边栏出现"命令演示"面板
- ✅ 命令面板有4个命令在"Command Demo"分类下
- ✅ Ctrl+Shift+X 可打开/激活计数器面板
- ✅ "条件命令"在面板关闭时灰色禁用，打开时可用
- ✅ "切换状态"命令可切换勾选状态
- ✅ 计数器面板的+/-/重置按钮可正常工作
