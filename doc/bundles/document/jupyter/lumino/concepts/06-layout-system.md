---
type: Concept
title: 布局系统详解
description: Layout抽象类与LayoutItem、FitPolicy尺寸策略、对齐属性、BoxLayout/DockLayout/SplitLayout等内置布局引擎
tags: [lumino, layout, widget, boxlayout, docklayout, splitlayout, css, positioning]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: layout-source
    resource: /external/libs/jupyter/lumino/packages/widgets/src/layout.ts
    title: "@lumino/widgets Layout 源码"
---

# 布局系统详解

## 布局的核心职责

Lumino 的布局系统负责将子 Widget 排列在父 Widget 的 DOM 节点内，处理尺寸计算、位置分配和对齐。与 CSS 布局（flexbox/grid）不同，Lumino 布局使用**绝对定位**手动计算每个子 Widget 的位置和尺寸，这是为了精确控制和高性能。

## Layout 抽象基类

[Layout](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/layout.ts#L37) 是所有布局的抽象基类：

```typescript
abstract class Layout implements Iterable<Widget>, IDisposable {
  constructor(options?: Layout.IOptions);

  parent: Widget | null;         // 父 Widget（自动设置）
  fitPolicy: Layout.FitPolicy;   // 尺寸适应策略

  abstract [Symbol.iterator](): IterableIterator<Widget>;  // 遍历子Widget
  abstract removeWidget(widget: Widget): void;             // 移除子Widget

  processParentMessage(msg: Message): void;  // 处理父Widget的消息
  dispose(): void;

  protected init(): void;           // 初始化（parent设置后调用）
  protected onResize(msg): void;    // 尺寸变化处理
  protected onUpdateRequest(msg): void;
  protected onBeforeAttach(msg): void;
  protected onAfterAttach(msg): void;
  protected onBeforeDetach(msg): void;
  protected onAfterDetach(msg): void;
  protected onBeforeShow(msg): void;
  protected onAfterShow(msg): void;
  protected onBeforeHide(msg): void;
  protected onAfterHide(msg): void;
  protected onChildRemoved(msg): void;
  protected onFitRequest(msg): void;
}
```

### FitPolicy：尺寸适应策略

```typescript
type FitPolicy = 'set-no-constraint' | 'set-min-size';
```

| 策略 | 行为 |
|------|------|
| `set-min-size`（默认） | 布局计算子 Widget 的最小尺寸，应用到父 Widget 的 `min-width/min-height` |
| `set-no-constraint` | 不向父 Widget 应用尺寸约束 |

### 消息处理：processParentMessage

Layout 通过 `processParentMessage` 接收父 Widget 的生命周期消息，并默认将消息转发给所有子 Widget（非隐藏的）。子类可以重写各生命周期钩子实现自定义行为：

```typescript
processParentMessage(msg: Message): void {
  switch (msg.type) {
    case 'resize':        this.onResize(msg);        break;
    case 'update-request': this.onUpdateRequest(msg); break;
    case 'fit-request':   this.onFitRequest(msg);    break;
    case 'before-show':   this.onBeforeShow(msg);    break;
    // ... 其他生命周期消息
    case 'child-removed': this.onChildRemoved(msg);  break;
  }
}
```

## LayoutItem：布局计算单元

[LayoutItem](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/layout.ts#L614) 是布局系统中的工作单元，它包装一个 Widget，负责计算和应用位置尺寸：

```typescript
class LayoutItem implements IDisposable {
  constructor(widget: Widget);
  readonly widget: Widget;

  // 计算出的尺寸限制（fit()后更新）
  readonly minWidth: number;
  readonly minHeight: number;
  readonly maxWidth: number;
  readonly maxHeight: number;

  // 状态代理
  readonly isHidden: boolean;
  readonly isVisible: boolean;
  readonly isAttached: boolean;

  fit(): void;     // 计算尺寸限制（通过ElementExt.sizeLimits）
  update(left: number, top: number, width: number, height: number): void;  // 应用位置尺寸
}
```

LayoutItem 在构造时做了两个关键操作：

```typescript
constructor(widget: Widget) {
  this.widget = widget;
  this.widget.node.style.position = 'absolute';  // 设置绝对定位
  this.widget.node.style.contain = 'strict';     // 启用CSS containment
}
```

### update()：位置尺寸应用

LayoutItem 的 `update()` 方法是布局的核心——它将计算出的位置和尺寸应用到 widget.node：

1. **尺寸裁剪**：将 width/height 裁剪到 [minWidth, maxWidth] × [minHeight, maxHeight] 范围内
2. **对齐调整**：如果分配空间大于 Widget 最大尺寸，根据水平/垂直对齐调整偏移
3. **增量更新**：只在值变化时修改 style.top/left/width/height
4. **发送 resize 消息**：尺寸变化时向 Widget 发送 ResizeMessage

### 对齐属性：AttachedProperty 实现

水平和垂直对齐通过 `AttachedProperty` 附加到 Widget 上：

```typescript
// 获取/设置对齐方式
Layout.getHorizontalAlignment(widget);  // 'left' | 'center' | 'right'（默认 'center'）
Layout.setHorizontalAlignment(widget, 'left');
Layout.getVerticalAlignment(widget);    // 'top' | 'center' | 'bottom'（默认 'top'）
Layout.setVerticalAlignment(widget, 'center');
```

对齐属性变化时，自动向父 Widget 发送 `update-request` 触发重布局。

## 内置布局引擎

Lumino 提供了多种内置布局，满足不同 UI 需求：

### PanelLayout：最简单的布局

[PanelLayout](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/panellayout.ts) 是最基础的布局，将子 Widget 直接附加到父节点，不做任何位置计算（依赖子 Widget 自身的 CSS 布局）。适用于简单容器。

### BoxLayout：盒子布局

[BoxLayout](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/boxlayout.ts) 实现水平或垂直方向的弹性盒子布局，类似 CSS flexbox：

```typescript
class BoxLayout extends PanelLayout {
  direction: BoxLayout.Direction;  // 'left-to-right' | 'right-to-left' | 'top-to-bottom' | 'bottom-to-top'
  spacing: number;                 // 子Widget间距

  // 设置子Widget的拉伸因子
  static setStretch(widget: Widget, value: number): void;
  static getStretch(widget: Widget): number;

  // 设置子Widget的尺寸基础值
  static setSizeBasis(widget: Widget, value: number): void;
}
```

BoxLayout 配合 [BoxEngine](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/boxengine.ts) 算法计算弹性分配：
- 每个子 Widget 有 minSize、maxSize、stretch（拉伸因子）
- BoxEngine 根据可用空间和 stretch 因子分配尺寸
- 类似 CSS flex-grow/flex-shrink，但更精确

```typescript
// 使用示例
const panel = new BoxPanel();
panel.direction = 'left-to-right';
panel.spacing = 4;
panel.addWidget(leftSidebar);
panel.addWidget(mainContent);
BoxPanel.setStretch(leftSidebar, 0);     // 不拉伸，保持自然尺寸
BoxPanel.setStretch(mainContent, 1);     // 拉伸填充剩余空间
```

### SplitLayout：可拖拽分割布局

[SplitLayout](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/splitlayout.ts) 在 BoxLayout 基础上增加了可拖拽分割条（handle），用户可以通过拖拽调整各面板大小：

```typescript
class SplitLayout extends BoxLayout {
  renderer: SplitLayout.IRenderer;  // 分割条渲染器
  handleSize: number;               // 分割条尺寸（像素）
  // 拖拽相关...
}

class SplitPanel extends Panel {
  constructor(options?: SplitPanel.IOptions);
  orientation: 'horizontal' | 'vertical';
  spacing: number;
  setRelativeSizes(sizes: number[]): void;  // 设置相对尺寸比例
}
```

### StackedLayout：堆叠布局

[StackedLayout](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/stackedlayout.ts) 将所有子 Widget 堆叠在同一区域，只显示当前选中的一个：

```typescript
class StackedLayout extends Layout {
  currentIndex: number;           // 当前显示的Widget索引
  currentWidget: Widget | null;   // 当前显示的Widget
  readonly currentChanged: ISignal<this, ICurrentChangedArgs>;
}
```

常用于 TabPanel 的内容区域（标签页切换时切换显示的子 Widget）。

### DockLayout：停靠布局（IDE 核心）

[DockLayout](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/docklayout.ts) 是 Lumino 最复杂的布局引擎，实现了类似 VS Code/JupyterLab 的 IDE 风格停靠面板：

- **标签组**：多个 Widget 可以放在同一区域通过标签切换
- **分割**：可以水平/垂直分割区域
- **拖拽停靠**：拖拽标签到边缘/中心可以停靠/分割/创建标签组
- **布局状态序列化**：可以保存/恢复布局状态

```typescript
class DockLayout extends Layout {
  // 添加Widget到指定位置
  addWidget(widget: Widget, options?: DockLayout.IAddOptions): void;

  // 移除Widget
  removeWidget(widget: Widget): void;

  // 选中指定Widget
  selectWidget(widget: Widget): void;

  // 布局迭代器
  [Symbol.iterator](): IterableIterator<Widget>;

  // 保存/恢复布局
  saveLayout(): DockLayout.ILayoutConfig;
  restoreLayout(config: DockLayout.ILayoutConfig): void;
}

interface IAddOptions {
  mode?: 'split-top' | 'split-bottom' | 'split-left' | 'split-right'
       | 'tab-before' | 'tab-after' | 'split-mode';
  ref?: Widget;  // 参考Widget
}
```

DockLayout 使用**树结构**表示布局：
- 叶节点是 TabGroup（标签组）
- 内部节点是 SplitNode（水平或垂直分割）
- 整棵树代表一个嵌套的分割-标签组层次结构

### AccordionLayout：手风琴布局

[AccordionLayout](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/accordionlayout.ts) 实现可折叠的手风琴面板，同一时间可以展开一个或多个区域。

### GridLayout：网格布局

[GridLayout](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/gridlayout.ts) 类似 CSS Grid，支持行列网格放置子 Widget。

### SingletonLayout：单组件布局

[SingletonLayout](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/singletonlayout.ts) 只容纳一个 Widget，适用于一次只显示一个内容的容器。

## 面板 Widget（Panel）

每种布局对应一个便捷的 Panel Widget：

| Layout | Panel | 用途 |
|--------|-------|------|
| PanelLayout | `Panel` | 通用容器，addWidget 添加子组件 |
| BoxLayout | `BoxPanel` | 水平/垂直弹性排列 |
| SplitLayout | `SplitPanel` | 可拖拽分割 |
| StackedLayout | `StackedPanel` | 堆叠切换 |
| DockLayout | `DockPanel` | IDE 风格停靠布局 |
| TabPanel（内置） | `TabPanel` | 标签面板（TabBar+StackedPanel） |
| AccordionLayout | `AccordionPanel` | 手风琴折叠面板 |

## 布局工作流程

当父 Widget 收到 `resize` 或 `update-request` 消息时，布局的工作流程：

```
父Widget收到resize消息
  ↓
Layout.onResize(msg)
  ↓
1. 遍历所有 LayoutItem，调用 fit() 计算各子Widget尺寸限制
   （通过ElementExt.sizeLimits读取DOM计算的min/max尺寸）
  ↓
2. 根据布局算法（BoxEngine/DockLayout树/分割算法等）
   计算每个子Widget的分配区域(left, top, width, height)
  ↓
3. 遍历所有 LayoutItem，调用 update(left, top, width, height)
   → 内部裁剪尺寸、调整对齐、设置style
   → 尺寸变化时向子Widget发送ResizeMessage
  ↓
子Widget收到resize消息，各自处理
```

## 绝对定位与 CSS Containment

Lumino 布局使用绝对定位 + `contain: strict` 的关键原因：

1. **避免 reflow 风暴**：子 Widget 变化不会触发兄弟节点的重排计算
2. **精确控制**：手动管理位置和尺寸，不依赖浏览器布局引擎的隐式行为
3. **高性能拖拽**：分割条拖拽、停靠面板移动时，直接更新 style 属性，不需要浏览器重算整个布局
4. **独立绘制**：`contain: strict` 提示浏览器该子树的布局/绘制/样式不影响外部，浏览器可以优化

## 相关概念

- [Widget 生命周期与DOM管理](05-widget-lifecycle.md) — Widget 与 Layout 的关系
- [MessageLoop 消息循环机制](04-messaging-loop.md) — 布局消息的投递与合并
- [高级组件与DataGrid](10-advanced-widgets.md) — DockPanel、TabBar 等使用布局的组件
