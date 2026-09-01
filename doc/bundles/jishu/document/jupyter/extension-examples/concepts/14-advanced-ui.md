---
type: Concept
title: 进阶UI模式
description: 掌握React组件集成、Datagrid数据表格、国际化(i18n)、主题扩展、顶部栏Widget等进阶UI开发模式
tags: [jupyterlab, react, datagrid, i18n, translation, theme, top-area, shoutouts]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: react-src
    resource: /references/core-api-tokens.md
    title: react-widget/src/*.tsx React集成示例
  - id: datagrid-src
    resource: /references/examples-index.md
    title: datagrid/src/panel.ts DataGrid示例
  - id: translator-src
    resource: /references/examples-index.md
    title: kernel-messaging/src/panel.ts ITranslator使用
---

## React组件集成

JupyterLab本身使用Lumino（原生DOM），但可以通过ReactDOM.render在Widget中渲染React组件。react-widget示例展示了标准的集成模式。

### 创建ReactWidget

```typescript
import { MainAreaWidget, ReactWidget } from '@jupyterlab/apputils';
import React, { useState } from 'react';

// 定义React组件
const CounterComponent = (): JSX.Element => {
  const [counter, setCounter] = useState(0);

  return (
    <div className="jp-React-Widget">
      <button
        className="jp-Button jp-mod-styled"
        onClick={() => setCounter(counter + 1)}
      >
        Increment
      </button>
      <p>Count: {counter}</p>
    </div>
  );
};

// 创建ReactWidget包装器
class CounterWidget extends ReactWidget {
  render(): JSX.Element {
    return <CounterComponent />;
  }
}

// 使用MainAreaWidget包装并添加到Shell
const widget = new MainAreaWidget<CounterWidget>({
  content: new CounterWidget()
});
widget.title.label = 'React Widget';
widget.title.icon = reactIcon;
app.shell.add(widget, 'main');
```

### ReactWidget关键点

1. **ReactWidget** 是Lumino Widget子类，在 `onAfterAttach` 中调用 `ReactDOM.render(this.render(), this.node)`
2. 继承ReactWidget，实现 `render()` 方法返回JSX
3. React状态（useState/useReducer）正常工作
4. React的事件系统与DOM事件兼容
5. 使用 `jp-Button jp-mod-styled` 类复用JupyterLab内置按钮样式

### 带useEffect的数据获取

ReactWidget可以结合useEffect从Kernel或API获取数据：

```tsx
const DataComponent = ({ kernel }: { kernel: IKernelConnection }) => {
  const [data, setData] = useState<string>('');

  useEffect(() => {
    const future = kernel.requestExecute({ code: 'import pandas as pd; print(df)' });
    future.onIOPub = (msg) => {
      if (msg.header.msg_type === 'stream') {
        setData(prev => prev + (msg.content as any).text);
      }
    };
    return () => { future.dispose(); };
  }, [kernel]);

  return <pre>{data}</pre>;
};
```

## DataGrid数据表格

datagrid示例集成了Lumino DataGrid组件，用于显示结构化数据表格：

```typescript
import { DataGrid, JSONModel } from '@lumino/datagrid';
import { StackedPanel } from '@lumino/widgets';

class DataGridPanel extends StackedPanel {
  constructor() {
    super();
    this.addClass('jp-example-view');
    this.title.closable = true;

    // 创建DataGrid
    const grid = new DataGrid();

    // 设置数据模型
    const data = {
      data: [
        { index: 0, name: 'Alice', score: 95 },
        { index: 1, name: 'Bob', score: 87 },
        { index: 2, name: 'Charlie', score: 92 }
      ],
      schema: {
        fields: [
          { name: 'index', type: 'number' },
          { name: 'name', type: 'string' },
          { name: 'score', type: 'number' }
        ],
        primaryKey: ['index']
      }
    };
    grid.dataModel = new JSONModel(data);

    this.addWidget(grid);
  }
}
```

### DataGrid核心API

- `DataGrid`：可滚动的数据表格组件
- `JSONModel`：从JSON数据创建模型
- `MutableDataModel`：可编辑数据模型基类
- `BasicKeyHandler`：键盘导航支持
- 支持列排序、筛选、单元格编辑、自定义渲染器

## 国际化（i18n）

JupyterLab提供ITranslator接口实现多语言支持：

```typescript
import { ITranslator } from '@jupyterlab/translation';

const extension: JupyterFrontEndPlugin<void> = {
  requires: [ITranslator],
  activate: (app, translator: ITranslator) => {
    // 加载翻译bundle
    const trans = translator.load('jupyterlab');

    // 使用trans.__()包裹需要翻译的字符串
    commands.addCommand(commandId, {
      label: trans.__('Open the Kernel Messaging Panel'),
      caption: trans.__('Open the Kernel Messaging Panel'),
      execute: createPanel
    });
  }
};
```

### 翻译API

| 方法 | 用途 | 示例 |
|------|------|------|
| `trans.__('text')` | 简单翻译 | `trans.__('Run Cell')` |
| `trans._n('singular', 'plural', n)` | 复数形式 | `trans._n('%1 file', '%1 files', n)` |
| `trans._p('context', 'text')` | 带上下文消歧 | `trans._p('verb', 'Run')` |

翻译字符串中的占位符使用 `%1`、`%2` 表示参数位置。

## 主题扩展（Theme）

theme示例展示了如何创建自定义主题。主题扩展注册CSS变量和样式表：

```typescript
// 主题插件
const theme: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/theme:plugin',
  requires: [IThemeManager],
  activate: (app, themeManager: IThemeManager) => {
    // 主题通常通过package.json中的jupyterlab.themePath声明
    // CSS文件定义:root { --jp-*: <value> } CSS变量
  }
};
```

主题CSS文件示例：
```css
:root {
  --jp-layout-color0: #111111;
  --jp-layout-color1: #212121;
  --jp-ui-font-color0: rgba(255,255,255,1.0);
  --jp-brand-color0: #2196f3;
  --jp-cell-prompt-width: 110px;
}
```

主题在package.json中声明：
```json
{
  "jupyterlab": {
    "themePath": "style/index.css",
    "extension": true
  }
}
```

用户可以在Settings→JupyterLab Theme菜单中切换主题。

## 顶部栏Widget

toparea-text-widget示例展示了如何向Shell的top区域添加Widget：

```typescript
import { DOMUtils } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';

const node = document.createElement('div');
node.textContent = 'Hello World, this is made with a simple Lumino Widget!';

const widget = new Widget({ node });
widget.id = DOMUtils.createDomID();  // 生成唯一DOM ID
widget.addClass('jp-TopAreaText');

// 添加到top区域，rank控制位置
app.shell.add(widget, 'top', { rank: 1000 });
```

top区域的Widget通常用于状态栏、面包屑、全局通知等固定UI。

## Clap Button（Notebook右侧）

clap-button示例展示了如何向Notebook面板的右侧区域添加悬浮按钮：

```typescript
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

const plugin: JupyterFrontEndPlugin<void> = {
  requires: [INotebookTracker],
  activate: (app, tracker: INotebookTracker) => {
    // 监听Notebook面板创建
    tracker.widgetAdded.connect((sender, panel: NotebookPanel) => {
      const button = new ClapButtonWidget();
      panel.addWidget(button, 'right');  // 添加到右侧区域
    });
  }
};
```

`panel.addWidget(widget, 'right')` 将Widget添加到Notebook的右侧工具栏/侧边区域。

## 插件间依赖与Shoutouts

shoutouts示例展示了跨插件消息模式——插件之间通过命令系统进行松耦合通信，不直接依赖对方的Token。其他插件可以通过命令面板发现和执行你的命令，而不需要直接导入你的Token。

## 开发调试技巧

1. **浏览器DevTools**：在Console中执行 `window.jupyterapp` 访问app实例
2. **查看已注册命令**：`window.jupyterapp.commands.listCommands()`
3. **查看已注册Token**：检查插件的provides/requires关系
4. **JupyterLab Dev模式**：`jupyter lab --dev-mode --watch`
5. **Source Maps**：开发构建包含source maps，便于TypeScript调试
6. **Console日志**：`console.log()` 在activate中输出调试信息
7. **Notification API**：用 `Notification.info()` 替代 `alert()` 显示调试信息

## 扩展清单

extension-examples仓库包含28个示例，覆盖了主要扩展点：

| 类别 | 示例 | 难度 |
|------|------|------|
| 入门 | hello-world | ⭐ |
| 基础 | commands, command-palette | ⭐ |
| UI | launcher, main-menu, context-menu | ⭐⭐ |
| Widget | widgets, react-widget | ⭐⭐ |
| 布局 | toparea-text-widget, contentheader | ⭐⭐ |
| 设置 | settings, state | ⭐⭐ |
| 工具栏 | toolbar-button, cell-toolbar | ⭐⭐ |
| 文档 | documents, documents-crdt | ⭐⭐⭐ |
| Kernel | kernel-messaging, kernel-output | ⭐⭐⭐ |
| 数据 | datagrid | ⭐⭐⭐ |
| 服务端 | server-extension | ⭐⭐⭐ |
| 日志 | log-messages, custom-log-console | ⭐⭐ |
| 通知 | notifications | ⭐ |
| 主题 | theme-dark-high-contrast, theme-light | ⭐⭐ |
| 国际化 | — | ⭐⭐ |
| 进阶 | cell-toolbar, clap-button, signals, shoutouts | ⭐⭐⭐ |
| 其他 | command-linker, completer, dialogs, svgviewer, open-from-url, widgets-tracker | ⭐⭐ |

## 相关概念

- [Widget与Shell布局](05-widgets-shell.md)
- [命令系统](04-commands.md)
- [插件基础与依赖注入](03-plugin-basics.md)
- [核心API与Token参考](../references/core-api-tokens.md)
