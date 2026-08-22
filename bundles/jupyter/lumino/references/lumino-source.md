---
type: Reference
title: Lumino 源码信源登记
description: Lumino 源码路径、版本信息、包清单、文件索引
tags: [lumino, source, reference, jupyterlab, typescript]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T12:50:00+08:00" }
verified: { by: "process:grep-api-validation", at: "2026-08-22T13:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: lumino-repo
    resource: /external/libs/jupyter/lumino/
    title: Lumino 本地源码镜像
---

# Lumino 源码信源登记

## 项目基本信息

| 属性 | 值 |
|------|-----|
| 项目名称 | Lumino（原名 PhosphorJS） |
| 本地源码路径 | `external/libs/jupyter/lumino/` |
| 包管理器 | Yarn 3.6.0 (Berry) |
| 多包管理 | Lerna |
| TypeScript 版本 | ~5.1.3 |
| 许可证 | BSD-3-Clause |
| 版权 | Jupyter Development Team |
| 类型 | JavaScript/TypeScript 工具包（monorepo） |

## 包清单（19 个包）

Lumino 采用 monorepo 结构，所有包位于 `packages/` 目录下：

| 包名 | 路径 | 核心职责 |
|------|------|----------|
| `@lumino/algorithm` | packages/algorithm/ | 数组与迭代器工具函数（ArrayExt、chain、filter、map、reduce、zip、sort 等） |
| `@lumino/application` | packages/application/ | 可插拔应用基类（Application + PluginRegistry） |
| `@lumino/collections` | packages/collections/ | 链表数据结构（LinkedList） |
| `@lumino/commands` | packages/commands/ | 命令注册表（CommandRegistry）、快捷键绑定、命令状态 |
| `@lumino/coreutils` | packages/coreutils/ | 核心工具（JSONExt、Token、PluginRegistry、PromiseDelegate、UUID、MIME、随机数） |
| `@lumino/datagrid` | packages/datagrid/ | 高性能数据表格（DataGrid、DataModel、CellRenderer、SelectionModel） |
| `@lumino/default-theme` | packages/default-theme/ | 所有组件的默认 CSS 主题 |
| `@lumino/disposable` | packages/disposable/ | 资源释放模式（IDisposable、DisposableDelegate） |
| `@lumino/domutils` | packages/domutils/ | DOM 工具（ElementExt 尺寸计算、Platform 检测、Selector 匹配、剪贴板） |
| `@lumino/dragdrop` | packages/dragdrop/ | 拖放支持（Drag、IDragEvent） |
| `@lumino/keyboard` | packages/keyboard/ | 键盘布局处理（getKeyboardLayout） |
| `@lumino/messaging` | packages/messaging/ | 消息循环（Message、ConflatableMessage、MessageLoop、IMessageHook） |
| `@lumino/polling` | packages/polling/ | 轮询与限流（Poll、RateLimiter、debounce/throttle） |
| `@lumino/properties` | packages/properties/ | 附加属性（AttachedProperty，在不继承的前提下给对象附加属性） |
| `@lumino/signaling` | packages/signaling/ | 类型安全信号/槽机制（Signal、ISignal） |
| `@lumino/virtualdom` | packages/virtualdom/ | 虚拟 DOM（VirtualElement、VirtualText、h()、VirtualDOM.render()） |
| `@lumino/widgets` | packages/widgets/ | UI 组件集（Widget、Layout、Panel、DockPanel、TabBar、Menu 等） |

## 核心源码文件索引

### 基础设施层

| 文件 | 关键导出 |
|------|----------|
| `packages/disposable/src/index.ts` | `IDisposable`, `DisposableDelegate`, `IObservableDisposable` |
| `packages/signaling/src/index.ts` | `Signal<T, U>`, `ISignal<T, U>`, `Slot<T, U>` |
| `packages/messaging/src/index.ts` | `Message`, `ConflatableMessage`, `IMessageHandler`, `IMessageHook`, `MessageLoop.sendMessage()`, `MessageLoop.postMessage()`, `MessageLoop.installMessageHook()` |
| `packages/properties/src/index.ts` | `AttachedProperty<T, U>` |
| `packages/algorithm/src/index.ts` | `ArrayExt`（静态工具类）, `each`, `filter`, `find`, `map`, `reduce`, `toArray` 等迭代器函数 |
| `packages/collections/src/index.ts` | `LinkedList<T>` |
| `packages/coreutils/src/token.ts` | `Token<T>` |
| `packages/coreutils/src/plugins.ts` | `PluginRegistry`, `IPlugin` |
| `packages/coreutils/src/promise.ts` | `PromiseDelegate<T>` |
| `packages/coreutils/src/json.ts` | `JSONExt.deepEqual`, `JSONExt.deepCopy` |
| `packages/coreutils/src/uuid.ts` | `UUID.uuid4()` |
| `packages/coreutils/src/random.ts` | 随机数生成 |

### 核心抽象层

| 文件 | 关键导出 |
|------|----------|
| `packages/virtualdom/src/index.ts` | `VirtualElement`, `VirtualText`, `VirtualNode`, `h()`, `h.div()/h.span()/...`, `VirtualDOM.realize()`, `VirtualDOM.render()` |
| `packages/widgets/src/widget.ts` | `Widget`（基类）, `Widget.Flag`, `Widget.ResizeMessage`, `Widget.ChildMessage`, `Widget.HiddenMode` |
| `packages/widgets/src/layout.ts` | `Layout`（抽象类）, `LayoutItem`, `Layout.FitPolicy`, `Layout.HorizontalAlignment`, `Layout.VerticalAlignment` |
| `packages/widgets/src/title.ts` | `Title<T>`（Widget 的标题对象） |
| `packages/commands/src/index.ts` | `CommandRegistry`, `CommandRegistry.ICommandOptions`, `CommandRegistry.IKeyBinding` |
| `packages/keyboard/src/index.ts` | `getKeyboardLayout()`, 键码常量 |
| `packages/domutils/src/element.ts` | `ElementExt.boxSizing`, `ElementExt.sizeLimits`, `ElementExt.hitTest` |
| `packages/domutils/src/platform.ts` | `Platform.IS_*` 平台检测 |
| `packages/domutils/src/selector.ts` | `Selector.matches()` |

### 组件层

| 文件 | 关键导出 |
|------|----------|
| `packages/widgets/src/panel.ts` | `Panel`（通用容器） |
| `packages/widgets/src/panellayout.ts` | `PanelLayout`（简单子控件布局） |
| `packages/widgets/src/boxlayout.ts` | `BoxLayout`（水平/垂直盒子布局）, `BoxLayout.Direction` |
| `packages/widgets/src/boxpanel.ts` | `BoxPanel`（盒子面板） |
| `packages/widgets/src/splitlayout.ts` | `SplitLayout`（可拖拽分割布局） |
| `packages/widgets/src/splitpanel.ts` | `SplitPanel`（分割面板） |
| `packages/widgets/src/stackedlayout.ts` | `StackedLayout`（堆叠布局） |
| `packages/widgets/src/stackedpanel.ts` | `StackedPanel`（堆叠面板） |
| `packages/widgets/src/docklayout.ts` | `DockLayout`（停靠布局引擎） |
| `packages/widgets/src/dockpanel.ts` | `DockPanel`（IDE风格停靠面板）, `DockPanel.IAddOptions` |
| `packages/widgets/src/tabbar.ts` | `TabBar<T>`（标签栏）, `TabBar.IRenderer` |
| `packages/widgets/src/tabpanel.ts` | `TabPanel`（标签面板） |
| `packages/widgets/src/accordionlayout.ts` | `AccordionLayout`（手风琴布局） |
| `packages/widgets/src/accordionpanel.ts` | `AccordionPanel`（手风琴面板） |
| `packages/widgets/src/menu.ts` | `Menu`（菜单）, `Menu.IRenderer`, `Menu.IItemOptions` |
| `packages/widgets/src/menubar.ts` | `MenuBar`（菜单栏） |
| `packages/widgets/src/contextmenu.ts` | `ContextMenu`（右键菜单） |
| `packages/widgets/src/commandpalette.ts` | `CommandPalette`（命令面板/搜索框） |
| `packages/widgets/src/scrollbar.ts` | `ScrollBar`（自定义滚动条） |
| `packages/widgets/src/focustracker.ts` | `FocusTracker`（焦点追踪） |
| `packages/widgets/src/gridlayout.ts` | `GridLayout`（网格布局） |
| `packages/dragdrop/src/index.ts` | `Drag`, `Drag.IArea`, `Drag.IOptions` |
| `packages/polling/src/poll.ts` | `Poll<T>`（定时轮询） |
| `packages/polling/src/ratelimiter.ts` | `RateLimiter`（限流器，debounce/throttle） |

### 应用框架层

| 文件 | 关键导出 |
|------|----------|
| `packages/application/src/index.ts` | `Application<T extends Widget>`, `Application.IOptions`, `Application.IStartOptions` |
| `packages/datagrid/src/datagrid.ts` | `DataGrid` |
| `packages/datagrid/src/datamodel.ts` | `DataModel`（抽象数据模型） |
| `packages/datagrid/src/cellrenderer.ts` | `CellRenderer` |
| `packages/datagrid/src/selectionmodel.ts` | `SelectionModel` |

## 构建配置

| 文件 | 说明 |
|------|------|
| `package.json` | 根 package.json，workspaces + scripts |
| `packages/*/package.json` | 各包独立配置 |
| `packages/*/tsconfig.json` | TypeScript 编译配置 |
| `packages/*/rollup.config.mjs` | Rollup 打包配置 |
| `packages/*/api-extractor.json` | API Extractor 配置（生成 .d.ts 报告） |
| `packages/*/typedoc.json` | TypeDoc 文档生成配置 |

## 版本兼容性

- Lumino 是 JupyterLab 的底层 UI 工具包
- `@lumino/widgets` 中的 `Widget` 类是所有可视化组件的基类
- JupyterLab 插件通过 `@lumino/application` 的 `Application` 和 `Token` 机制进行扩展
- 虚拟 DOM 设计支持嵌入第三方渲染器（如 React）
