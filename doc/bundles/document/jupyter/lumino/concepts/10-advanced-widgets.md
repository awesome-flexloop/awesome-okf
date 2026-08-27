---
type: Concept
title: 高级组件与DataGrid
description: TabBar标签栏、TabPanel标签面板、Menu菜单系统、ContextMenu右键菜单、DataGrid高性能数据表格、DragDrop拖拽
tags: [lumino, widget, tab, menu, datagrid, dragdrop, advanced-components, table]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: widgets-source
    resource: /external/libs/jupyter/lumino/packages/widgets/src
    title: "@lumino/widgets 源码目录"
  - id: datagrid-source
    resource: /external/libs/jupyter/lumino/packages/datagrid/src
    title: "@lumino/datagrid 源码目录"
  - id: dragdrop-source
    resource: /external/libs/jupyter/lumino/packages/dragdrop/src/index.ts
    title: "@lumino/dragdrop 源码"
---

# 高级组件与DataGrid

除了基础 Widget 和布局系统，Lumino 还提供了一系列开箱即用的高级 UI 组件。这些组件是构建桌面级应用的关键积木。

## TabBar：标签栏

TabBar 是渲染标签的水平/垂直条，通常与 StackedPanel 配合使用构成 TabPanel。

```typescript
class TabBar<T extends Widget = Widget> extends Widget {
  constructor(options?: TabBar.IOptions<T>);

  // 标签管理
  addTab(value: Title<T>): void;
  insertTab(index: number, value: Title<T>): void;
  removeTab(value: Title<T>): void;

  // 当前选中
  currentIndex: number;
  currentTitle: Title<T> | null;
  readonly currentChanged: ISignal<this, ICurrentChangedArgs<T>>;

  // 标签关闭
  readonly tabCloseRequested: ISignal<this, TabBar.ITabCloseRequestedArgs<T>>;
  readonly tabDetachRequested: ISignal<this, TabBar.ITabDetachRequestedArgs<T>>;

  // 拖拽相关
  readonly tabMoved: ISignal<this, TabBar.ITabMovedArgs<T>>;

  // 方向
  orientation: 'horizontal' | 'vertical';
  tabsMovable: boolean;
  allowDeselect: boolean;
}
```

TabBar 渲染的是 Widget 的 `title` 对象——这就是为什么每个 Widget 都有一个 title 属性。TabBar 本身不管理内容面板，它只管理标签的选择、关闭、移动等交互。

TabBar 使用 VirtualDOM 渲染标签内部，支持自定义渲染器（IRenderer）。

## TabPanel：标签面板

TabPanel 将 TabBar 和 StackedPanel 组合为一个完整的标签面板：

```typescript
class TabPanel extends Widget {
  constructor(options?: TabPanel.IOptions);

  readonly tabBar: TabBar<Widget>;
  readonly stackedPanel: StackedPanel;

  // 快捷方法
  addWidget(widget: Widget): void;
  insertWidget(index: number, widget: Widget): void;
  currentIndex: number;
  currentWidget: Widget | null;
  readonly currentChanged: ISignal<this, TabPanel.ICurrentChangedArgs>;

  // TabBar属性代理
  tabsMovable: boolean;
  tabBarPlacement: 'top' | 'bottom' | 'left' | 'right';
}
```

```typescript
const tabPanel = new TabPanel();
tabPanel.addWidget(new FileBrowserWidget());  // 自动用widget.title创建标签
tabPanel.addWidget(new EditorWidget());
tabPanel.addWidget(new TerminalWidget());
tabPanel.currentIndex = 0;  // 选中第一个标签
Widget.attach(tabPanel, document.body);
```

## Menu：菜单系统

Menu 实现下拉菜单/弹出菜单，基于 CommandRegistry：

```typescript
class Menu extends Widget {
  constructor(options: Menu.IOptions);

  readonly commands: CommandRegistry;

  // 菜单项管理
  addItem(options: Menu.IItemOptions): IDisposable;
  insertItem(index: number, options: Menu.IItemOptions): IDisposable;
  removeItem(item: Menu.IItem): void;
  clearItems(): void;

  // 菜单项类型
  addItem({ command: 'file:new' });        // 命令项
  addItem({ type: 'separator' });          // 分隔线
  addItem({ type: 'submenu', submenu: otherMenu });  // 子菜单

  // 打开菜单
  open(x: number, y: number, options?: Menu.IOpenOptions): void;

  // 层级关系
  readonly parentMenu: Menu | null;
  readonly childMenu: Menu | null;

  // 信号
  readonly menuItemTriggered: ISignal<this, Menu.IMenuItemTriggeredArgs>;
}
```

菜单项自动从 CommandRegistry 获取 label、icon、isEnabled、isToggled、mnemonic 等状态，并在 commandChanged 信号触发时刷新。

```typescript
const fileMenu = new Menu({ commands });
fileMenu.addItem({ command: 'file:new' });
fileMenu.addItem({ command: 'file:open' });
fileMenu.addItem({ type: 'separator' });
fileMenu.addItem({ command: 'file:save' });
fileMenu.addItem({ command: 'file:save-as' });

// 在按钮点击处打开菜单
fileMenu.open(buttonRect.left, buttonRect.bottom);
```

### MenuBar：菜单栏

MenuBar 是水平菜单栏，用于应用程序顶部的文件/编辑/视图等菜单：

```typescript
class MenuBar extends Widget {
  constructor(options?: MenuBar.IOptions);

  addMenu(menu: Menu): IDisposable;
  insertMenu(index: number, menu: Menu): IDisposable;

  readonly menus: ReadonlyArray<Menu>;
  activeIndex: number;
  activeMenu: Menu | null;

  open(x: number, y: number, options?: MenuBar.IOpenOptions): void;
}
```

### ContextMenu：右键菜单

ContextMenu 集成在 Application 中，根据 CSS 选择器匹配可用的菜单项：

```typescript
class ContextMenu {
  constructor(options: ContextMenu.IOptions);
  readonly menu: Menu;

  addItem(options: ContextMenu.IItemOptions): IDisposable;
  // 包含 selector: string 和 rank?: number

  open(event: MouseEvent, options?: ContextMenu.IOpenOptions): void;
}

// 注册上下文菜单项
app.contextMenu.addItem({
  command: 'file:rename',
  selector: '.file-item',
  rank: 10,
});
app.contextMenu.addItem({
  command: 'file:delete',
  selector: '.file-item',
  rank: 20,
});
```

右键点击 `.file-item` 元素时，ContextMenu 会自动收集所有 selector 匹配的命令，按 rank 排序，构建并显示 Menu。

## DockPanel：停靠面板

DockPanel 是 Lumino 最强大的容器 Widget，封装了 DockLayout：

```typescript
class DockPanel extends Widget {
  constructor(options?: DockPanel.IOptions);

  // 添加Widget
  addWidget(widget: Widget, options?: DockPanel.IAddOptions): void;

  // 操作
  activateWidget(widget: Widget): void;
  selectWidget(widget: Widget): void;
  activateNextTab(): void;
  activatePreviousTab(): void;

  // 选中状态
  activeWidget: Widget | null;
  selectedWidgets: Widget[];

  // 模式
  mode: 'single-document' | 'multiple-document';

  // 拖拽
  readonly dragDropped: ISignal<DockPanel, DockPanel.IDragDroppedArgs>;

  // 布局持久化
  saveLayout(): DockPanel.ILayoutConfig;
  restoreLayout(config: DockPanel.ILayoutConfig): void;

  // 外观
  spacing: number;
  renderer: DockPanel.IRenderer;
}
```

DockPanel 是 JupyterLab 主区域的核心，支持：
- 拖拽标签到边缘进行分割
- 拖拽标签到中心进行标签组合
- 标签组的切换和关闭
- 单文档模式（类似 VS Code 的 Zen Mode）
- 布局保存和恢复（跨会话保持面板位置）

```typescript
const dock = new DockPanel();
dock.id = 'main-dock';
dock.addWidget(notebook);
dock.addWidget(terminal, { mode: 'split-right', ref: notebook });
dock.addWidget(console, { mode: 'split-bottom', ref: notebook });
```

## DragDrop：拖拽系统

@lumino/dragdrop 提供底层拖拽支持：

```typescript
namespace Drag {
  // 启动拖拽
  function start(options: Drag.IOptions): Drag | null;
  function overrideCursor(cursor: string): IDisposable;
  function dispose(): void;
}

interface IOptions {
  document?: Document;
  mimeData: MimeData;        // 拖拽携带的数据
  dragImage: HTMLElement;    // 拖拽时显示的图像
  proposedAction?: 'copy' | 'link' | 'move' | 'none';
  supportedActions?: DragActions;
  source?: any;
}

class MimeData implements Iterable<[string, any]> {
  setData(mime: string, data: any): void;
  getData(mime: string): any;
  clear(): void;
  hasData(mime: string): boolean;
  types(): string[];
}
```

DockPanel 和 SplitPanel 的拖拽交互都基于此模块。MimeData 是一个 MIME 类型到数据的映射表，支持多种数据格式（类似剪贴板）。

## DataGrid：高性能数据表格

@lumino/datagrid 是一个高性能的虚拟滚动数据表格组件，专为展示大规模数据设计：

```typescript
class DataGrid extends Widget {
  constructor(options?: DataGrid.IOptions);

  // 数据源
  dataModel: DataModel | null;

  // 尺寸策略
  stretchLastColumn: boolean;
  stretchLastRow: boolean;
  columnWidths: SectionResize;
  rowHeights: SectionResize;
  defaultSizes: DefaultSizes;

  // 表头
  headerVisibility: HeaderVisibility;

  // 选区
  readonly selectionModel: SelectionModel;

  // 滚动
  scrollTo(x: number, y: number): void;
  scrollToCell(r: number, c: number): void;

  // 视口
  readonly viewport: DataGrid.Viewport;
}
```

### DataModel：数据模型

```typescript
abstract class DataModel {
  // 行数/列数
  abstract rowCount(region: CellRegion): number;
  abstract columnCount(region: CellRegion): number;

  // 单元格数据
  data(region: CellRegion, row: number, column: number): any;

  // 元数据（用于渲染）
  metadata(region: CellRegion, row: number, column: number): DataModel.Metadata;

  // 数据变化信号
  readonly changed: ISignal<this, DataModel.ChangedArgs>;
}
```

DataGrid 的关键设计特点：

1. **虚拟滚动**：只渲染可见区域的单元格，支持百万级数据行而不卡顿
2. **Canvas 渲染**：使用 `<canvas>` 绘制单元格内容（非 DOM），性能极高
3. **区域划分**：corner（左上角）、column-header（列表头）、row-header（行表头）、body（数据区）四个区域
4. **灵活的数据源**：通过继承 DataModel 适配任何数据源（JSON、CSV、数据库查询结果等）
5. **内置交互**：选区（单选/多选）、列宽/行高调整、复制粘贴、键盘导航
6. **可定制渲染**：通过 CellRenderer 自定义单元格绘制

### JSON 数据模型示例

```typescript
import { DataGrid, JSONModel } from '@lumino/datagrid';

const data = [
  { name: 'Alice', age: 30, city: 'Beijing' },
  { name: 'Bob', age: 25, city: 'Shanghai' },
  { name: 'Charlie', age: 35, city: 'Shenzhen' },
];

const model = new JSONModel(data);
const grid = new DataGrid();
grid.dataModel = model;
grid.headerVisibility = 'all';  // 显示所有表头
```

### 基本渲染器

DataGrid 提供了基础的文本渲染器，也支持自定义：

```typescript
class CustomRenderer extends CellRenderer {
  paint(ctx: CanvasRenderingContext2D, config: CellRenderer.ICellConfig): void {
    // 使用 Canvas API 自定义绘制
    const { x, y, width, height, value } = config;
    ctx.fillStyle = value > 100 ? 'red' : 'green';
    ctx.fillText(String(value), x + 4, y + height / 2);
  }
}
```

## 其他实用组件

| 组件 | 位置 | 用途 |
|------|------|------|
| `ScrollBar` | widgets/src/scrollbar.ts | 自定义滚动条（非原生） |
| `ScrollPanel` | widgets/src/scrollpanel.ts | 带滚动条的容器面板 |
| `CommandPalette` | widgets/src/commandpalette.ts | 命令面板（Ctrl+Shift+P 风格） |
| `BoxPanel` | widgets/src/boxpanel.ts | 便捷的 BoxLayout 面板 |
| `SplitPanel` | widgets/src/splitpanel.ts | 便捷的 SplitLayout 面板 |
| `StackedPanel` | widgets/src/stackedpanel.ts | 便捷的 StackedLayout 面板 |
| `AccordionPanel` | widgets/src/accordionpanel.ts | 手风琴折叠面板 |
| `Panel` | widgets/src/panel.ts | 基础容器（最简单的Widget容器） |

## Polling：轮询机制

@lumino/polling 提供了可暂停、可调整频率的轮询器，用于定时刷新数据：

```typescript
class Poll<T, U> {
  constructor(options: Poll.IOptions<T, U>);
  start(): Promise<void>;
  stop(): Promise<void>;
  schedule(interval?: number, immediate?: boolean): void;
  readonly ticked: ISignal<this, Poll.ITickedArgs<T, U>>;
}
```

与 `setInterval` 的区别：支持根据页面可见性自动暂停/恢复，支持退避策略，与 Lumino 的信号系统集成。

## Properties：附加属性

@lumino/properties 提供 AttachedProperty 模式，允许在不修改对象类定义的情况下附加属性：

```typescript
class AttachedProperty<T, U> {
  constructor(options: AttachedProperty.IOptions<T, U>);
  get(owner: T): U;
  set(owner: T, value: U): void;
}
```

Lumino 内部大量使用此模式，例如 Layout 的 horizontalAlignment、widget title 等。属性变更时可以触发回调（如向父组件发消息）。

## 相关概念

- [Widget 生命周期与DOM管理](05-widget-lifecycle.md) — 所有高级组件都继承自 Widget
- [布局系统详解](06-layout-system.md) — DockPanel/TabPanel 使用的布局引擎
- [命令系统与快捷键](07-command-system.md) — Menu/ContextMenu 基于 CommandRegistry
- [Signal/Slot 类型安全事件系统](03-signaling-system.md) — 组件交互通过信号通信
