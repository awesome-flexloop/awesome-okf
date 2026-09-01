---
type: Concept
title: 虚拟 DOM 渲染引擎
description: VirtualElement/VirtualText虚拟节点、h()函数创建虚拟树、VirtualDOM.render()差异更新、事件绑定、hpass透传、与React的对比
tags: [lumino, virtualdom, vdom, render, dom, diff, hyperscript]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: vdom-source
    resource: /external/libs/jupyter/lumino/packages/virtualdom/src/index.ts
    title: "@lumino/virtualdom 源码"
---

# 虚拟 DOM 渲染引擎

## 虚拟 DOM 的定位

Lumino 的 VirtualDOM 是一个轻量级的虚拟 DOM 实现，设计目标不是成为通用 UI 框架（如 React/Vue），而是为 Lumino 内部组件（Menu、Tab、DataGrid 等）提供高效的声明式内容渲染。它的核心价值在于：

- **增量更新**：对比新旧虚拟树，只更新变化的 DOM 部分
- **声明式 API**：用 JavaScript 对象描述 DOM 结构
- **零依赖**：不依赖任何框架，与 Lumino Widget 系统紧密集成
- **轻量级**：仅提供核心的 h() 创建函数和 render() 差异渲染

## 虚拟节点类型

虚拟 DOM 树由两种节点组成：

### VirtualText：文本节点

```typescript
class VirtualText {
  readonly type = 'text';
  readonly content: string;

  constructor(content: string);
}
```

表示一个纯文本节点，不支持属性或子节点。

### VirtualElement：元素节点

```typescript
class VirtualElement {
  readonly type: 'element';
  readonly tag: string;                      // HTML标签名，如 'div', 'span', 'input'
  readonly attrs: ElementAttrs;              // 属性集合
  readonly children: ReadonlyArray<VirtualNode>;  // 子节点数组
  readonly renderer?: VirtualElement.IRenderer;  // 自定义渲染器（可选）
}

type VirtualNode = VirtualElement | VirtualText;
```

### VirtualElementPass：透传元素

```typescript
class VirtualElementPass extends VirtualElement {
  // 用于组件传递，跳过该层直接渲染子内容
}
```

`hpass()` 函数创建 VirtualElementPass，用于包装器组件不需要生成额外 DOM 元素的场景。

## h() 函数：创建虚拟元素

h() 是 hyperscript 风格的创建函数，支持多种签名：

```typescript
// 签名1：仅标签
h(tag: string): VirtualElement;

// 签名2：标签 + 子节点
h(tag: string, ...children: h.Child[]): VirtualElement;

// 签名3：标签 + 属性
h(tag: string, attrs: ElementAttrs): VirtualElement;

// 签名4：标签 + 属性 + 子节点
h(tag: string, attrs: ElementAttrs, ...children: h.Child[]): VirtualElement;
```

### 子节点类型 h.Child

子节点可以是：
- `VirtualNode`（VirtualElement 或 VirtualText）
- `string`（自动转为 VirtualText）
- `null` 或 `undefined`（被忽略，用于条件渲染）
- `Array<h.Child>`（嵌套数组会被扁平化）

```typescript
import { h, VirtualElement } from '@lumino/virtualdom';

// 简单元素
const div = h('div', { className: 'box' }, 'Hello');

// 嵌套结构
const list = h('ul', { className: 'list' },
  h('li', 'Item 1'),
  h('li', 'Item 2'),
  h('li', h('strong', 'Bold Item')),
);

// 条件渲染（null被忽略）
const item = showButton
  ? h('button', { onclick: () => console.log('click') }, 'Click')
  : null;
const container = h('div', item);

// 数组映射
const todos = ['Learn Lumino', 'Build App', 'Ship'];
const todoList = h('ul', todos.map(t => h('li', t)));
```

## 元素属性 ElementAttrs

VirtualDOM 支持标准 HTML 属性，通过类型 `ElementAttrNames` 限定支持的属性名。关键属性包括：

### 通用属性

```typescript
h('div', {
  id: 'my-id',
  className: 'my-class',
  title: 'tooltip text',
  hidden: false,
  draggable: true,
  tabindex: 0,
});
```

### style 属性

`style` 接受字符串或对象：

```typescript
h('div', {
  style: {
    color: 'red',
    fontSize: '14px',
    display: 'flex',
    padding: '8px 16px',
  },
});

// 或字符串形式
h('div', { style: 'color: red; font-size: 14px;' });
```

### 数据集 data-*

```typescript
h('div', { dataset: { id: '123', type: 'item' } });
// 渲染为 <div data-id="123" data-type="item">
```

### 事件处理

事件监听器通过 `on` 前缀属性注册：

```typescript
h('button', {
  onclick: (event: MouseEvent) => { console.log('clicked!'); },
  ondblclick: handleDoubleClick,
  onmousedown: handleMouseDown,
  onkeydown: handleKeyDown,
  oninput: handleInput,
}, 'Click Me');
```

**注意**：VirtualDOM 的事件处理使用 DOM 原生事件名（`onclick` 而非 React 风格的 `onClick`），直接使用 `addEventListener` 绑定。

### 特殊属性

| 属性 | 说明 |
|------|------|
| `innerHTML` | 设置元素的 innerHTML（注意 XSS 风险） |
| `accesskey` | 快捷键访问键 |
| `contenteditable` | 是否可编辑 |
| `disabled` | 是否禁用（表单元素） |
| `checked` | 是否选中（checkbox/radio） |
| `value` | 值（input/select/textarea） |
| `placeholder` | 占位文字 |

## VirtualDOM.render()：差异渲染

核心渲染函数：

```typescript
namespace VirtualDOM {
  function render(
    content: VirtualNode | ReadonlyArray<VirtualNode> | null,
    host: HTMLElement
  ): void;

  function realize(node: VirtualNode): HTMLElement | Text;
}
```

### render() 工作原理

`render()` 将虚拟节点渲染到宿主元素中，使用 diff 算法进行增量更新：

1. **首次渲染**：创建所有新的 DOM 节点，附加到 host
2. **后续渲染**：
   - 从 WeakMap 中取出上次渲染的虚拟内容（oldContent）
   - 对比 oldContent 和 newContent，计算最小操作集
   - 只对发生变化的部分执行 DOM 操作
   - 更新 WeakMap 中的缓存
3. **清空内容**：传入 `null` 清除所有渲染内容

```typescript
import { VirtualDOM, h } from '@lumino/virtualdom';

const host = document.getElementById('app')!;

// 首次渲染
VirtualDOM.render(h('div', { className: 'greeting' }, 'Hello!'), host);

// 更新：只更新文本节点，不重建 div
VirtualDOM.render(h('div', { className: 'greeting' }, 'Hello, World!'), host);

// 更新：className 变化会更新 class 属性
VirtualDOM.render(h('div', { className: 'greeting active' }, 'Hello!'), host);

// 清空
VirtualDOM.render(null, host);
```

### realize()：一次性创建

`realize()` 不执行 diff，直接从虚拟节点创建真实 DOM 节点。适用于不需要后续更新的场景：

```typescript
const node = VirtualDOM.realize(h('span', { className: 'icon' }, '★'));
document.body.appendChild(node);
```

## Diff 算法要点

VirtualDOM 的 diff 算法基于同层比较：

1. **同位置同标签**：复用 DOM 元素，比较属性差异
2. **属性 diff**：
   - 新增属性：设置属性/属性
   - 删除属性：移除属性
   - 变更属性：更新值
   - 事件监听器：移除旧的、添加新的
3. **子节点 diff**：
   - 同位置同类型（文本 vs 元素）：递归更新
   - 类型变化：移除旧节点，创建新节点
   - 列表：按索引比较（不支持 key-based 移动优化，列表重排会重建）
4. **文本节点**：内容变化时更新 textContent

**注意**：Lumino 的 VirtualDOM 不支持 React 风格的 key 优化。对于列表重排场景，它采用重建策略。这在 Lumino 的使用场景（Menu、Tab、DataGrid 等结构化组件）中是可接受的。

## 自定义渲染器（IRenderer）

VirtualElement 支持可选的 `renderer`，允许自定义元素的渲染逻辑：

```typescript
interface IRenderer {
  render(attrs: ElementAttrs): HTMLElement;
}
```

这在 Lumino 内部被广泛用于图标渲染，例如 Title 中的 icon 渲染器。

## 与 Widget 的集成模式

VirtualDOM 通常在 Widget 内部使用，在 `onUpdateRequest` 或 `render()` 方法中调用：

```typescript
import { Widget } from '@lumino/widgets';
import { h, VirtualDOM, VirtualNode } from '@lumino/virtualdom';

class CounterWidget extends Widget {
  private _count = 0;

  constructor() {
    super();
    this.addClass('counter');
  }

  protected onAfterAttach(msg: Message): void {
    super.onAfterAttach(msg);
    this._render();  // 首次渲染
    this.node.addEventListener('click', this._onClick);
  }

  protected onBeforeDetach(msg: Message): void {
    this.node.removeEventListener('click', this._onClick);
    super.onBeforeDetach(msg);
  }

  increment(): void {
    this._count++;
    this._render();
  }

  private _render(): void {
    const content = h('div', { className: 'counter-display' },
      h('span', { className: 'count' }, `Count: ${this._count}`),
      h('button', { className: 'inc-btn' }, '+1'),
    );
    VirtualDOM.render(content, this.node);
  }

  private _onClick = (e: Event) => {
    const target = e.target as HTMLElement;
    if (target.classList.contains('inc-btn')) {
      this.increment();
    }
  };
}
```

但更常见的模式是，Lumino 内置组件（Menu、TabBar、CommandPalette）内部使用 VirtualDOM 渲染其内容，应用开发者通常不直接操作 VirtualDOM，而是通过 Widget 的布局和命令系统构建 UI。

## 与 React/Vue 的对比

| 特性 | Lumino VirtualDOM | React |
|------|-------------------|-------|
| 定位 | 组件内部渲染工具 | 完整 UI 框架 |
| 组件模型 | Widget（类） | 函数/类组件 |
| 状态管理 | Widget 属性 + Signal | useState/useReducer/外部 store |
| Diff 策略 | 同层比较，无 key | Fiber + key 优化 |
| 事件系统 | 原生 DOM 事件 | SyntheticEvent |
| 包体积 | 极小（~5KB gzipped） | ~40KB+ gzipped |
| 适合场景 | 结构化桌面组件 | 通用 Web 应用 |

**实践建议**：
- Lumino 提供"外壳"（窗口管理、布局、命令），内部渲染可以用 VirtualDOM 或 React/Vue
- JupyterLab 使用 Lumino 做应用框架，但 Notebook 单元格内可以使用 React 组件
- 简单组件直接用 VirtualDOM，复杂交互组件可以引入 React

## hpass()：透传元素

`hpass()` 创建 VirtualElementPass，它在渲染时不生成额外的 DOM 元素，直接渲染其子节点：

```typescript
import { hpass, h } from '@lumino/virtualdom';

// 一个包装函数不产生额外 DOM 层级
function withTooltip(child: VirtualNode, tooltip: string) {
  return hpass('div',
    h('span', { className: 'tooltip', title: tooltip }, '?'),
    child,
  );
}
```

hpass 常用于高阶组件模式中传递内容而不增加 DOM 嵌套深度。

## 相关概念

- [Widget 生命周期与DOM管理](05-widget-lifecycle.md) — Widget 中使用 VirtualDOM 的模式
- [架构总览](01-architecture-overview.md) — VirtualDOM 在架构中的位置
- [Signal/Slot 类型安全事件系统](03-signaling-system.md) — VirtualDOM 事件与 Signal 的对比
