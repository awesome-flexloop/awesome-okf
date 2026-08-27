---
type: Concept
title: 算法工具与集合库
description: "@lumino/algorithm迭代器与函数式操作、@lumino/collections BTree/LinkedList、核心工具函数、轮询与键盘"
tags: [lumino, algorithm, collections, iterator, btree, functional-programming, utilities]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: algorithm-source
    resource: /external/libs/jupyter/lumino/packages/algorithm/src
    title: "@lumino/algorithm 源码"
  - id: collections-source
    resource: /external/libs/jupyter/lumino/packages/collections/src
    title: "@lumino/collections 源码"
  - id: coreutils-source
    resource: /external/libs/jupyter/lumino/packages/coreutils/src
    title: "@lumino/coreutils 源码"
---

# 算法工具与集合库

Lumino 提供了独立的算法和数据结构包，不依赖 DOM，可以在 Node.js 和浏览器中使用。这些包是整个框架的基础工具层。

## @lumino/algorithm：迭代器与函数式操作

algorithm 包提供了基于 ES6 Iterable/Iterator 的函数式编程工具集，类似 RxJS/Lodash 但使用原生迭代器协议，没有额外抽象。

### 核心概念：Iterable 与 Iterator

所有函数都接受 Iterable<T> 并返回 Iterable<T> 或 Iterator<T>，采用**惰性求值**策略：不创建中间数组，而是通过链式迭代器在消费时逐个计算。

```typescript
// 范围迭代器：产生 0,1,2,3,4
const nums = range(0, 5);
// 此时还没有任何计算发生

// map 转换：惰性
const doubled = map(nums, x => x * 2);
// 仍然没有计算

// filter 过滤：惰性
const evens = filter(doubled, x => x % 2 === 0);
// 还是没有计算

// 消费：forEach/toArray/extrema 等触发实际计算
forEach(evens, x => console.log(x));
// 此时才逐个计算：0→0*2=0→0%2===0→打印 0
//                        1→1*2=2→2%2===0→打印 2
//                        ...
```

### 常用函数

#### 创建迭代器

```typescript
import { ArrayExt, IterableOrArrayLike } from '@lumino/algorithm';

range(start: number, stop: number, step?: number): IterableIterator<number>;
// range(0, 5) → 0,1,2,3,4
// range(5, 0, -1) → 5,4,3,2,1

repeat<T>(value: T, count: number): IterableIterator<T>;
// repeat('a', 3) → 'a','a','a'

iter<T>(object: IterableOrArrayLike<T>): IterableIterator<T>;  // 从数组/Iterable创建迭代器
iterEach<T>(object: IterableOrArrayLike<T>, fn: (value: T, index: number) => void): void;

empty<T>(): IterableIterator<T>;  // 空迭代器
once<T>(value: T): IterableIterator<T>;  // 产生单个值
```

#### 转换操作

```typescript
map<T, U>(object: IterableOrArrayLike<T>, fn: (value: T, index: number) => U): IterableIterator<U>;

filter<T>(object: IterableOrArrayLike<T>, fn: (value: T, index: number) => boolean): IterableIterator<T>;

// 同时map和filter，通过返回undefined跳过
filterMap<T, U>(
  object: IterableOrArrayLike<T>,
  fn: (value: T, index: number) => U | undefined
): IterableIterator<U>;

enumerate<T>(object: IterableOrArrayLike<T>): IterableIterator<[number, T]>;
// enumerate(['a','b']) → [0,'a'], [1,'b']
```

#### 归约与消费

```typescript
forEach<T>(object: IterableOrArrayLike<T>, fn: (value: T, index: number) => void): void;

toArray<T>(object: IterableOrArrayLike<T>): T[];

reduce<T, U>(
  object: IterableOrArrayLike<T>,
  fn: (accumulator: U, value: T, index: number) => U,
  initial: U
): U;

every<T>(object: IterableOrArrayLike<T>, fn: (value: T) => boolean): boolean;
some<T>(object: IterableOrArrayLike<T>, fn: (value: T) => boolean): boolean;
```

#### 查找与比较

```typescript
find<T>(object: IterableOrArrayLike<T>, fn: (value: T, index: number) => boolean): T | undefined;
findIndex<T>(object: IterableOrArrayLike<T>, fn: (value: T, index: number) => boolean): number;

min<T>(object: IterableOrArrayLike<T>, fn?: (a: T, b: T) => number): T | undefined;
max<T>(object: IterableOrArrayLike<T>, fn?: (a: T, b: T) => number): T | undefined;
minmax<T>(object: IterableOrArrayLike<T>, fn?: (a: T, b: T) => number): [T, T] | undefined;

includes<T>(object: IterableOrArrayLike<T>, value: T): boolean;
```

#### 组合与扁平化

```typescript
chain<T>(...objects: IterableOrArrayLike<T>[]): IterableIterator<T>;
// 依次迭代多个集合

zip<T>(...iterables: IterableOrArrayLike<T>[]): IterableIterator<T[]>;
// 按位置配对：zip([1,2], ['a','b']) → [1,'a'], [2,'b']

flatten<T>(object: IterableOrArrayLike<IterableOrArrayLike<T>>): IterableIterator<T>;
// 扁平化一层

take<T>(object: IterableOrArrayLike<T>, count: number): IterableIterator<T>;
// 取前N个
```

#### 拓扑排序

```typescript
topologicSort<T>(
  nodes: IterableOrArrayLike<T>,
  edges: (node: T) => IterableOrArrayLike<T>
): T[] | undefined;
```

这是插件系统用来解析依赖顺序的核心算法。返回拓扑排序后的数组，如果存在循环依赖返回 `undefined`。

### ArrayExt：数组扩展

ArrayExt 命名空间提供了针对数组的原地操作函数（不创建新数组，高效）：

```typescript
namespace ArrayExt {
  function insert<T>(array: T[], index: number, value: T): void;
  function removeAt<T>(array: T[], index: number): T | undefined;
  function move<T>(array: T[], fromIndex: number, toIndex: number): void;
  function swap<T>(array: T[], i: number, j: number): void;

  function lowerBound<T, U>(
    array: ReadonlyArray<T>, value: U,
    compare: (a: T, b: U) => number
  ): number;  // 二分查找下界

  function upperBound<T, U>(
    array: ReadonlyArray<T>, value: U,
    compare: (a: T, b: U) => number
  ): number;  // 二分查找上界

  function binarySearch<T, U>(
    array: ReadonlyArray<T>, value: U,
    compare: (a: T, b: U) => number
  ): number;  // 二分查找，找到返回索引，未找到返回-1

  function firstWhere<T>(
    array: ReadonlyArray<T>,
    fn: (value: T, index: number) => boolean
  ): T | undefined;
}
```

这些数组操作函数在 Lumino 内部被广泛使用（Layout、TabBar、DataGrid 等），提供了比 `Array.prototype` 更丰富的原地操作。

## @lumino/collections：高级数据结构

collections 包提供了 JavaScript 标准库没有的高效数据结构。

### BTree：平衡二叉树

BTree 是一个有序的键值对映射，使用 B-tree 数据结构实现：

```typescript
class BTree<T, U> {
  constructor(compare?: (a: T, b: T) => number, cmpByUint32?: boolean);

  readonly size: number;
  readonly isEmpty: boolean;

  set(key: T, value: U): boolean;     // 插入/更新，返回是否新插入
  get(key: T): U | undefined;          // 查找
  has(key: T): boolean;                // 包含检查
  delete(key: T): boolean;             // 删除，返回是否存在
  clear(): void;                       // 清空

  min(): [T, U] | undefined;           // 最小键值对
  max(): [T, U] | undefined;           // 最大键值对
  at(index: number): [T, U] | undefined;  // 按索引访问

  keys(): IterableIterator<T>;         // 按键排序迭代
  values(): IterableIterator<U>;       // 按键排序迭代值
  entries(): IterableIterator<[T, U]>; // 按键排序迭代键值对
  [Symbol.iterator](): IterableIterator<[T, U]>;

  find(min: T | undefined, max: T | undefined): IterableIterator<[T, U]>;
}
```

BTree 的特点：
- **有序**：键按比较函数排序
- **O(log n)** 复杂度的 set/get/delete
- **高效范围查询**：find(min, max) 支持区间迭代
- **稳定的键迭代顺序**：不像 Map 依赖插入顺序
- **B-tree 而非红黑树**：在 JavaScript 中缓存友好，性能更好

适用于需要有序键遍历或范围查询的场景（如 DataGrid 的行/列索引）。

### LinkedList：双向链表

LinkedList 是一个双向链表实现：

```typescript
class LinkedList<T> {
  readonly length: number;
  readonly isEmpty: boolean;
  first: INode<T> | null;
  last: INode<T> | null;

  addFirst(value: T): INode<T>;
  addLast(value: T): INode<T>;
  insertBefore(node: INode<T>, value: T): INode<T>;
  insertAfter(node: INode<T>, value: T): INode<T>;

  removeFirst(): T | undefined;
  removeLast(): T | undefined;
  removeNode(node: INode<T>): void;
  clear(): void;

  // O(n) 操作
  find(fn: (value: T) => boolean): INode<T> | undefined;
  insertAt(index: number, value: T): INode<T>;

  // 迭代
  nodes(): IterableIterator<INode<T>>;
  [Symbol.iterator](): IterableIterator<T>;
}

interface INode<T> {
  readonly list: LinkedList<T> | null;
  readonly prev: INode<T> | null;
  readonly next: INode<T> | null;
  value: T;
}
```

LinkedList 适用于频繁在头部/中间插入/删除的场景，O(1) 复杂度。Lumino 的消息队列内部使用了链表结构。

## @lumino/coreutils：核心工具集

coreutils 提供了多种通用工具：

### PromiseDelegate：延迟 Promise

```typescript
class PromiseDelegate<T> {
  readonly promise: Promise<T>;
  resolve(value: T): void;
  reject(reason: unknown): void;
}
```

将 Promise 的 resolve/reject 暴露给外部，用于手动控制 Promise 状态。Application.started 就是用 PromiseDelegate 实现的：

```typescript
this._delegate = new PromiseDelegate<void>();
// 启动完成时
this._delegate.resolve();
// 外部通过 app.started promise 等待
```

### UUID 生成

```typescript
namespace UUID {
  function uuid4(): string;  // 生成符合 UUID v4 的唯一标识符
}
```

### JSON 工具

```typescript
namespace JSONExt {
  const emptyObject: Readonly<{}>;
  const emptyArray: Readonly<any[]>;

  function deepCopy<T>(value: T): T;
  function deepEqual(lhs: unknown, rhs: unknown): boolean;
  function isObject(value: unknown): value is { [key: string]: unknown };
  function isArray(value: unknown): value is unknown[];
  function isPrimitive(value: unknown): boolean;
}
```

deepEqual 和 deepCopy 是常用的深度比较/克隆工具，Lumino 内部（特别是插件状态管理和布局序列化）大量使用。

### MimeData：MIME 类型数据容器

```typescript
class MimeData {
  setData(mime: string, data: any): void;
  getData(mime: string): any;
  clear(): void;
  clearData(mime: string): void;
  hasData(mime: string): boolean;
  types(): string[];
  [Symbol.iterator](): IterableIterator<[string, any]>;
}
```

DragDrop 使用 MimeData 传递拖拽数据，Clipboard 也使用 MimeData。支持在同一数据对象中存储多种 MIME 类型的数据（如 `text/plain`、`text/html`、自定义 MIME）。

### Token & PluginRegistry

见[插件化应用框架](09-plugin-application.md)中的 Token 和 PluginRegistry 部分。

## @lumino/keyboard：键盘布局处理

keyboard 包处理键盘布局差异：

```typescript
namespace Keyboard {
  function getKeyboardLayout(): KeyboardLayout;
  function setKeyboardLayout(layout: KeyboardLayout): void;
}

class KeyboardLayout {
  // 将键码转换为对应键的字符（考虑Shift等修饰键和键盘布局）
  keyForKeydownEvent(event: KeyboardEvent): string;
  // 标准化键名
  canonicalKey(key: string): string;
  // 检查修饰键状态
  isModifierKey(key: string): boolean;
}
```

不同操作系统和键盘布局（QWERTY、AZERTY、Dvorak 等）的键码到字符的映射不同。KeyboardLayout 抽象了这些差异，确保快捷键在不同布局下都能正确工作。

## @lumino/polling：轮询机制

polling 提供可控制的轮询器：

```typescript
type PollState = 'constructed' | 'started' | 'stopped' | 'rejected';

class Poll<T = any, U = any> {
  constructor(options: Poll.IOptions<T, U>);

  readonly state: PollState;
  readonly tick: Promise<T>;  // 下次tick的Promise
  readonly ticked: ISignal<this, Poll.ITickedArgs<T, U>>;

  start(): Promise<void>;
  stop(): Promise<void>;
  refresh(): Promise<void>;
  schedule(interval?: number, immediate?: boolean): void;

  // 页面可见性
  readonly standby: 'when-hidden' | 'never';
}
```

Poll 的核心特性：
- **自动暂停**：`standby: 'when-hidden'` 时，页面隐藏（`document.hidden`）自动暂停轮询，节省资源
- **可调整频率**：通过 `schedule()` 动态调整轮询间隔
- **退避策略**：支持工厂函数动态计算下一次间隔（指数退避）
- **信号通知**：每次 tick 通过 `ticked` 信号通知
- **状态管理**：明确的状态机（constructed → started/stopped → rejected）

```typescript
const poll = new Poll({
  auto: true,
  frequency: { interval: 1000, backoff: true, max: 30000 },
  factory: () => refreshData(),
  standby: 'when-hidden',
});
```

## @lumino/domutils：DOM 工具集

domutils 提供 DOM 相关工具：

### Selector：CSS 选择器特异性计算

```typescript
namespace Selector {
  function calculateSpecificity(selector: string): number;
  function matches(element: Element, selector: string): boolean;
}
```

CommandRegistry 使用 `calculateSpecificity` 确定快捷键选择器的优先级——最具体的选择器优先匹配。

### ElementExt：元素尺寸和位置工具

```typescript
namespace ElementExt {
  function sizeLimits(element: HTMLElement): ElementExt.ISizeLimits;
  // 返回元素的 { minWidth, minHeight, maxWidth, maxHeight }

  function boxSizing(element: HTMLElement): ElementExt.IBoxSizing;
  // 返回边框、内边距尺寸

  function hitTest(element: HTMLElement, x: number, y: number): boolean;
  // 坐标是否在元素内

  function scrollIfNeeded(element: HTMLElement, region: ElementExt.IRect): void;
  // 如果区域不可见，滚动使其可见
}
```

Layout 系统在 fit() 计算尺寸限制时大量使用 `sizeLimits`。

### Platform：平台检测

```typescript
namespace Platform {
  const IS_IE: boolean;
  const IS_EDGE: boolean;
  const IS_FIREFOX: boolean;
  const IS_CHROME: boolean;
  const IS_SAFARI: boolean;
  const IS_WINDOWS: boolean;
  const IS_MAC: boolean;
  const IS_LINUX: boolean;
}
```

用于处理浏览器兼容性差异。注意：随着时间推移，部分属性可能已过时。

## 工具层的设计哲学

这些基础包体现了 Lumino 的设计哲学：

1. **零依赖**：每个工具包尽量自包含，不依赖其他 Lumino 包
2. **惰性求值**：algorithm 包的迭代器函数全部惰性求值，避免不必要的内存分配
3. **原地操作**：ArrayExt 尽量原地修改数组，减少 GC 压力
4. **面向性能**：BTree 使用 B-tree 而非红黑树，DataGrid 使用 Canvas 渲染——都为高性能桌面级应用设计
5. **功能完整但不过度**：提供最常用的数据结构和算法，不追求覆盖所有场景
6. **跨平台**：算法/集合/coreutils 不依赖 DOM，可在任何 JS 环境使用

## 相关概念

- [架构总览](01-architecture-overview.md) — 工具层在四层架构中的位置
- [IDisposable资源管理](02-disposable-pattern.md) — 所有工具对象的生命周期管理
- [插件化应用框架](09-plugin-application.md) — topologicSort 在插件系统中的使用
- [MessageLoop 消息循环机制](04-messaging-loop.md) — LinkedList 在消息队列中的使用
