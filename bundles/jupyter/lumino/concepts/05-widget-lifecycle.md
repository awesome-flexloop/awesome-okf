---
type: Concept
title: Widget 生命周期与 DOM 管理
description: Widget 基类、DOM节点管理、生命周期消息序列、Flag状态系统、HiddenMode、attach/detach机制
tags: [lumino, widget, lifecycle, dom, component, ui]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:25:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: widget-source
    resource: /external/libs/jupyter/lumino/packages/widgets/src/widget.ts
    title: @lumino/widgets Widget 源码
  - id: title-source
    resource: /external/libs/jupyter/lumino/packages/widgets/src/title.ts
    title: @lumino/widgets Title 源码
---

# Widget 生命周期与 DOM 管理

## Widget：一切 UI 的基类

[Widget](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/widget.ts#L36) 是 Lumino 所有 UI 组件的基类，实现了 `IMessageHandler` 和 `IObservableDisposable` 接口。每个 Widget 拥有一个真实的 DOM 节点（`HTMLElement`），通过消息系统管理生命周期。

## 核心属性

```typescript
class Widget implements IMessageHandler, IObservableDisposable {
  readonly node: HTMLElement;           // Widget 拥有的 DOM 节点
  readonly disposed: ISignal<this, void>; // dispose 信号
  readonly title: Title<Widget>;        // 标题对象（Tab/菜单显示用）
  readonly dataset: DOMStringMap;       // node.dataset 的快捷访问

  id: string;                           // node.id 的快捷访问
  parent: Widget | null;                // 父 Widget（通过 setter 自动管理）
  layout: Layout | null;                // 布局管理器（只能设置一次）
  hiddenMode: Widget.HiddenMode;        // 隐藏模式

  // 状态查询
  readonly isDisposed: boolean;
  readonly isAttached: boolean;         // node 是否已在 DOM 中
  readonly isHidden: boolean;           // 是否显式隐藏
  readonly isVisible: boolean;          // 是否真正可见（递归检查祖先）
}
```

### node：DOM 节点所有权

Widget 构造时自动创建一个 `<div>` 元素作为 `node`：

```typescript
constructor(options: Widget.IOptions = {}) {
  this.node = Private.createNode(options);  // 默认创建 <div>
  this.addClass('lm-Widget');               // 添加基础 CSS 类
}
```

你也可以传入外部创建的节点来托管已有 DOM：

```typescript
const existingNode = document.getElementById('my-content');
const widget = new Widget({ node: existingNode });
```

Widget 对 `node` 拥有**所有权**：dispose 时会从 DOM 中分离 node 并清理。

### title：标题对象

每个 Widget 有一个 [Title](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/widgets/src/title.ts) 对象，供容器组件（TabBar、Menu等）显示标签、图标、关闭按钮等：

```typescript
widget.title.label = '我的面板';
widget.title.icon = someIconRenderer;
widget.title.closable = true;
widget.title.caption = '这是一个示例面板';  // tooltip
widget.title.className = 'my-panel-title';
```

Title 内部使用 AttachedProperty 实现，按需创建（懒加载）。

## Flag 状态系统

Widget 使用位标志（bit flags）管理内部状态：

```typescript
namespace Widget {
  enum Flag {
    IsDisposed    = 0x1,
    IsVisible     = 0x2,   // 已废弃，isVisible 现在递归计算
    IsHidden      = 0x4,
    IsAttached    = 0x8,
    DisallowLayout = 0x10,
  }
}
```

通过 `setFlag`/`clearFlag`/`testFlag` 操作：

```typescript
widget.setFlag(Widget.Flag.IsHidden);    // 标记为隐藏
widget.clearFlag(Widget.Flag.IsHidden);  // 取消隐藏标记
widget.testFlag(Widget.Flag.IsAttached); // 检查是否已挂载
```

## HiddenMode：隐藏方式

Widget 支持三种隐藏模式：

```typescript
namespace Widget {
  enum HiddenMode {
    Display = 'display',   // display: none（默认，从布局中移除）
    Visibility = 'visibility', // visibility: hidden（保留占位）
    Scale = 'scale',       // transform: scale(0)（保留布局，性能最好）
  }
}
```

| 模式 | CSS 效果 | 布局影响 | 性能 | 适用场景 |
|------|----------|----------|------|----------|
| Display | `display: none` | 不占空间 | 触发重排 | 默认，普通隐藏 |
| Visibility | `visibility: hidden` | 占空间 | 较高 | 需要保留布局位置 |
| Scale | `transform: scale(0)` | 占空间 | 最高（GPU合成） | 频繁切换显示/隐藏 |

## 生命周期详解

Widget 的生命周期通过消息驱动，完整序列如下：

### 1. 创建（Constructor）

```typescript
const widget = new Widget();
// 此时：node 已创建（内存中的 DOM 元素，但未加入文档）
// isDisposed=false, isAttached=false, isHidden=false, isVisible=false
```

### 2. 挂载到 DOM（attach）

通过 `Widget.attach(widget, host)` 静态方法将 Widget 挂载到 DOM：

```typescript
Widget.attach(widget, document.body);
```

触发消息序列：

```
before-attach → onBeforeAttach()
  ↓
[将 node 添加到 host DOM]
  ↓
after-attach → onAfterAttach()
```

此时 `isAttached = true`。如果 Widget 未被隐藏，紧接着：

```
before-show → onBeforeShow()
  ↓
[清除隐藏样式]
  ↓
after-show → onAfterShow()
```

此时 `isVisible = true`。之后会发送首次 `resize` 消息。

### 3. 运行时消息

| 操作 | 消息 | 投递方式 | 说明 |
|------|------|----------|------|
| `widget.update()` | `update-request` | postMessage（异步、可合并） | 请求重新布局/更新 |
| `widget.fit()` | `fit-request` | postMessage（异步） | 请求重新计算尺寸约束 |
| `widget.activate()` | `activate-request` | postMessage（异步） | 请求激活（获取焦点） |
| `widget.close()` | `close-request` | sendMessage（同步） | 请求关闭 Widget |
| 窗口/父容器 resize | `resize` | sendMessage（同步） | 通知尺寸变化 |
| 添加子 Widget | `child-added` | sendMessage（同步） | 通知 Layout 有新子组件 |
| 移除子 Widget | `child-removed` | sendMessage（同步） | 通知 Layout 移除子组件 |
| 子 Widget show | `child-shown` | sendMessage（同步） | 通知 Layout 子组件显示 |
| 子 Widget hide | `child-hidden` | sendMessage（同步） | 通知 Layout 子组件隐藏 |

### 4. 显示/隐藏

**show()**：
1. 如果未标记为隐藏，直接返回
2. 如果已挂载且父可见，发送 `before-show`
3. 清除 IsHidden 标志，恢复 CSS 显示
4. 发送 `after-show`
5. 通知父 Widget 发送 `child-shown`

**hide()**：
1. 如果已标记为隐藏，直接返回
2. 如果已挂载且父可见，发送 `before-hide`
3. 设置 IsHidden 标志，应用隐藏 CSS
4. 发送 `after-hide`
5. 通知父 Widget 发送 `child-hidden`

### 5. 从 DOM 分离（detach）

通过 `Widget.detach(widget)` 静态方法：

```
before-hide → after-hide（如果当前可见）
  ↓
before-detach → onBeforeDetach()
  ↓
[将 node 从 DOM 移除]
  ↓
after-detach → onAfterDetach()
```

此时 `isAttached = false`。

### 6. 销毁（dispose）

完整的 dispose 流程：

```typescript
dispose(): void {
  if (this.isDisposed) return;                    // 1. 幂等检查

  this.setFlag(Widget.Flag.IsDisposed);           // 2. 设置标志
  this._disposed.emit(undefined);                 // 3. 发射 disposed 信号

  if (this.parent) {
    this.parent = null;                           // 4a. 从父移除（触发 child-removed）
  } else if (this.isAttached) {
    Widget.detach(this);                          // 4b. 或直接从 DOM 分离
  }

  if (this._layout) {
    this._layout.dispose();                       // 5. 释放布局
    this._layout = null;
  }

  this.title.dispose();                           // 6. 释放标题

  Signal.clearData(this);                         // 7. 清理信号
  MessageLoop.clearData(this);                    // 8. 清理消息
  AttachedProperty.clearData(this);               // 9. 清理附加属性
}
```

## parent setter：自动父子管理

设置 `widget.parent = otherWidget` 时：

1. 如果父相同，no-op
2. 检查循环引用（不能设置后代为父）
3. 通知旧父发送 `child-removed`
4. 更新 `_parent` 引用
5. 通知新父发送 `child-added`
6. 给自己发送 `parent-changed` 消息

**但通常不直接设置 parent**。通过 Layout 管理子 Widget 时，Layout 的 `init()` 方法会自动设置子 Widget 的 parent：

```typescript
protected init(): void {
  for (const widget of this) {
    widget.parent = this.parent;  // Layout 自动设置 parent
  }
}
```

## layout setter：单次设置

Layout 只能设置一次，不可更改：

```typescript
set layout(value: Layout | null) {
  if (this._layout === value) return;
  if (this.testFlag(Widget.Flag.DisallowLayout)) throw new Error('Cannot set layout.');
  if (this._layout) throw new Error('Cannot change widget layout.');
  if (value.parent) throw new Error('Layout already has a parent.');
  this._layout = value;
  value.parent = this;  // 设置 Layout 的 parent 回指，触发 Layout.init()
}
```

这是一种"装配"模式：Widget 和 Layout 的关系一旦建立就固定，运行时不切换布局类型。

## CSS 类名管理

Widget 提供了操作 CSS 类的便捷方法：

```typescript
widget.addClass('my-widget');        // 添加类
widget.removeClass('my-widget');     // 移除类
widget.hasClass('my-widget');        // 检查类是否存在
widget.toggleClass('active');        // 切换类
widget.toggleClass('active', true);  // 强制添加
widget.toggleClass('active', false); // 强制移除
```

所有 Widget 默认添加 `lm-Widget` CSS 类，配合 `@lumino/default-theme` 提供基础样式。

## 自定义 Widget：重写生命周期钩子

创建自定义 Widget 的标准方式是子类化并重写 `onXxx` 方法：

```typescript
class MyWidget extends Widget {
  constructor() {
    super();
    this.addClass('my-widget');
    // 初始化内容
    this.node.innerHTML = '<button>Click me</button>';
  }

  protected onAfterAttach(msg: Message): void {
    super.onAfterAttach(msg);
    // DOM 已挂载，可以安全添加事件监听
    this.node.querySelector('button')!.addEventListener('click', this._onClick);
  }

  protected onBeforeDetach(msg: Message): void {
    // DOM 即将移除，清理事件监听
    this.node.querySelector('button')!.removeEventListener('click', this._onClick);
    super.onBeforeDetach(msg);
  }

  protected onResize(msg: Widget.ResizeMessage): void {
    if (msg.width !== -1) {  // UnknownSize 时 width=-1
      console.log(`尺寸变为: ${msg.width}x${msg.height}`);
    }
  }

  protected onUpdateRequest(msg: Message): void {
    // 处理更新请求（重绘、重布局等）
  }

  private _onClick = () => {
    console.log('Button clicked!');
  };
}
```

**重写规则**：
- `onBeforeAttach` / `onBeforeDetach` 中添加/移除 DOM 事件监听
- `onAfterAttach` / `onAfterShow` 中启动定时器/动画
- `onBeforeHide` / `onBeforeDetach` 中停止定时器/动画
- `onResize` 中根据新尺寸调整布局
- `onUpdateRequest` 中执行重新渲染
- `onCloseRequest`（通过 processMessage 重写）中处理关闭确认

## 静态方法

| 方法 | 说明 |
|------|------|
| `Widget.attach(widget, host)` | 将 widget 的 node 添加到 host DOM |
| `Widget.detach(widget)` | 将 widget 的 node 从 DOM 移除 |

注意：`Widget.attach` 会触发完整的生命周期消息序列。直接操作 `widget.node` 挂到 DOM 中**不会**触发这些消息，应始终使用 `Widget.attach/detach`。

## 相关概念

- [MessageLoop 消息循环机制](04-messaging-loop.md) — Widget 生命周期的消息驱动引擎
- [布局系统详解](06-layout-system.md) — Layout 如何管理子 Widget 的尺寸和位置
- [Signal/Slot 类型安全事件系统](03-signaling-system.md) — Widget.disposed 信号
- [插件化应用框架](09-plugin-application.md) — Application 如何管理 Widget 生命周期
