---
title: 前端Shell布局
type: concept
bundle: jupyter-notebook
okf-version: "0.2"
chapter: "03"
difficulty: intermediate
tags: ["frontend", "shell", "lumino", "layout"]
prerequisites: ["01-architecture-overview"]
sources: ["F-030", "F-031", "F-032", "F-033", "F-034", "F-035", "F-036", "F-037"]
next: ["06-extension-system", "03-customize-shell"]
---

# 03 | 前端Shell布局：NotebookShell

`NotebookShell` 是Notebook v7前端布局的核心，它基于Lumino Widget系统，将用户界面划分为6个命名区域，并管理各区域的widget添加、显示和布局。

## Shell与JupyterFrontEnd的关系

```python
# app.ts
export class NotebookApp extends JupyterFrontEnd<INotebookShell> {
    constructor(options: NotebookApp.IOptions = { shell: new NotebookShell() }) {
        super({ ...options, shell: options.shell ?? new NotebookShell() });
        this.docRegistry.addModelFactory(new Base64ModelFactory());
        // ...
    }
}
```

> **信源**: [app.ts:L27-35](file:///d:/spaces/SpecWeave/external/libs/jupyter/notebook/packages/application/src/app.ts#L27-L35)（F-030, F-031）

- `NotebookApp` 在构造时创建或接收一个 `NotebookShell` 实例
- Shell通过泛型参数 `INotebookShell` 暴露给插件系统
- 插件通过 `app.shell` 访问Shell，通过Token `INotebookShell` 注入

## INotebookShell Token

```typescript
export const INotebookShell = new Token<INotebookShell>(
    '@jupyter-notebook/application:INotebookShell'
);

export interface INotebookShell extends NotebookShell {}
```

> **信源**: [shell.ts:L31-38](file:///d:/spaces/SpecWeave/external/libs/jupyter/notebook/packages/application/src/shell.ts#L31-L38)（F-034）

Token字符串 `@jupyter-notebook/application:INotebookShell` 是全局唯一的DI标识符。插件在需要访问Shell时声明依赖此Token：

```typescript
const plugin: JupyterFrontEndPlugin<void> = {
    id: '@jupyter-notebook/my-extension:plugin',
    requires: [INotebookShell],
    autoStart: true,
    activate: (app: JupyterFrontEnd, shell: INotebookShell) => {
        // 使用shell...
    }
};
```

## 六区域模型

Shell定义了6个widget区域（F-033）：

```typescript
export namespace INotebookShell {
    export type Area = 'main' | 'top' | 'menu' | 'left' | 'right' | 'down';
}
```

### 区域布局结构

```
┌─────────────────────────────────────────────┐
│              menu-panel (role=navigation)    │  ← 菜单栏
├─────────────────────────────────────────────┤
│              top-panel (role=banner)         │  ← 顶部工具栏
├──────────┬──────────────────────┬───────────┤
│          │                      │           │
│ left     │     main-panel       │ right     │  ← 主工作区
│ Handler  │                      │ Handler   │
│ (tabbar) │   TabPanelSvg        │ (tabbar)  │
│          │   (Notebook/Editor)  │           │
│          │                      │           │
├──────────┴──────────────────────┴───────────┤
│              down-panel                      │  ← 底部面板
│         (默认25%高度，可折叠)                 │
└─────────────────────────────────────────────┘
```

> **信源**: shell.ts构造函数中的PanelHandler/SidePanelHandler初始化（F-037）

### 各区域详解

| 区域 | Widget管理 | 典型内容 | ARIA角色 |
|------|-----------|---------|---------|
| `menu` | PanelHandler | 菜单栏（File/Edit/View/...） | `navigation` |
| `top` | PanelHandler | 工具栏、面包屑导航 | `banner` |
| `left` | SidePanelHandler | 文件浏览器、运行面板、TOC | 侧边栏标签页 |
| `main` | Panel (TabPanelSvg) | Notebook编辑器、文件编辑器 | 主内容区 |
| `right` | SidePanelHandler | 属性检查器、调试器 | 侧边栏标签页 |
| `down` | PanelHandler | 控制台、日志输出 | 底部面板 |

## 核心实现

### 构造函数

```typescript
export class NotebookShell extends Widget implements JupyterFrontEnd.IShell {
    constructor() {
        super();
        this.id = 'main';
        this._userLayout = {};

        this._topHandler = new PanelHandler();
        this._menuHandler = new PanelHandler();
        this._leftHandler = new SidePanelHandler('left', this.translator);
        this._rightHandler = new SidePanelHandler('right', this.translator);
        this._main = new Panel();
        // ...
        this._topHandler.panel.id = 'top-panel';
        this._topHandler.panel.node.setAttribute('role', 'banner');
        this._menuHandler.panel.id = 'menu-panel';
        this._menuHandler.panel.node.setAttribute('role', 'navigation');
        this._main.id = 'main-panel';
    }
}
```

> **信源**: [shell.ts:L82-100](file:///d:/spaces/SpecWeave/external/libs/jupyter/notebook/packages/application/src/shell.ts#L82-L100)（F-037）

### PanelHandler vs SidePanelHandler

NotebookShell使用两种Handler来管理不同区域：

**PanelHandler**（用于menu/top/down区域）：
- 简单的垂直/水平面板容器
- Widget按rank顺序排列
- 支持显示/隐藏切换

**SidePanelHandler**（用于left/right区域）：
- 带标签栏（TabBar）的侧边栏
- 每个widget对应一个标签
- 支持标签页切换、展开/折叠
- 左侧和右侧各自独立管理

### 常量定义

```typescript
const DEFAULT_DOWN_AREA_SIZE = 0.25;  // down区域默认占25%高度（F-035）
const DEFAULT_RANK = 900;              // widget默认rank（F-036）
```

rank值决定widget在同一区域内的排列顺序，rank小的靠前：
- 菜单栏通常rank=0-100
- 工具栏rank=100-300
- 侧边栏标签rank=300-900
- 用户自定义widget默认rank=900

## IWidgetPosition 与用户布局

```typescript
export interface IWidgetPosition {
    area?: Area;
    options?: DocumentRegistry.IOpenOptions;
}

export interface IUserLayout {
    [k: string]: IWidgetPosition;
}
```

> **信源**: [shell.ts:L52-71](file:///d:/spaces/SpecWeave/external/libs/jupyter/notebook/packages/application/src/shell.ts#L52-L71)

`IUserLayout` 允许用户自定义widget的打开位置。例如，将文件浏览器从默认的left区域移到right区域。

## Shell实现的IShell接口

`NotebookShell` 实现了 `JupyterFrontEnd.IShell` 接口，必须提供以下核心方法：

### add(widget, area, options)

向指定区域添加widget：

```typescript
// 插件中向Shell添加widget的典型用法
app.shell.add(new MyWidget(), 'left', { rank: 500 });
```

参数说明：
- `widget`: 要添加的Lumino Widget
- `area`: 目标区域（'main'|'top'|'menu'|'left'|'right'|'down'）
- `options.rank`: 排序权重，小值在前
- `options.ref`: 参考widget，用于相对定位

### expandLeft()/expandRight()/expandTop()

展开/折叠侧边栏：

```typescript
shell.expandLeft();   // 展开左侧边栏
shell.collapseLeft(); // 折叠左侧边栏
```

## 与JupyterLab Shell的区别

| 特性 | JupyterLab Shell | NotebookShell |
|------|-----------------|---------------|
| 主区域 | 支持多文档dock（可拖拽分屏） | 单文档TabPanel（类似经典Notebook） |
| 区域数 | 更多（header, top, left, main, right, bottom, down） | 6个（menu, top, left, main, right, down） |
| 简单模式 | 提供"Single Document Mode" | 默认就是单文档模式 |
| 自定义布局 | 完整dock布局支持 | 简化布局，专注Notebook体验 |

NotebookShell的设计目标是提供**经典Jupyter Notebook的简洁体验**，去掉JupyterLab中过于复杂的多文档拖拽布局，但保留插件系统的完整能力。

## CSS布局

Shell使用CSS Flexbox/BoxLayout进行布局：

- 顶层使用垂直BoxLayout：menu → top → (left/main/right SplitPanel) → down
- left/main/right区域使用SplitPanel允许用户拖拽调整宽度
- down区域默认折叠，展开时占25%高度
- 各panel通过id设置CSS样式：`#main-panel`, `#top-panel`, `#menu-panel`

## 插件如何使用Shell

```typescript
// 示例：向左侧边栏添加一个自定义面板
import { INotebookShell } from '@jupyter-notebook/application';

const myPlugin: JupyterFrontEndPlugin<void> = {
    id: 'my-extension:sidebar',
    autoStart: true,
    requires: [INotebookShell],
    activate: (app: JupyterFrontEnd, shell: INotebookShell) => {
        const widget = new Widget();
        widget.id = 'my-extension-panel';
        widget.title.icon = myIcon;
        widget.title.caption = 'My Panel';

        shell.add(widget, 'left', { rank: 700 });
    }
};
```

## 下一步

- → [插件系统](./06-extension-system.md) 理解JupyterLab插件如何注册到Shell并构建完整UI
- → [实战：自定义Shell布局](../examples/03-customize-shell.md) 动手修改Shell布局
