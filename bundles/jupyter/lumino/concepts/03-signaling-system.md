---
type: Concept
title: Signal/Slot 类型安全事件系统
description: Signal 类型安全事件机制、connect/disconnect/emit API、内存安全设计、信号与DOM事件对比
tags: [lumino, signal, slot, event, typescript, observer-pattern]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:15:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: signaling-source
    resource: /external/libs/jupyter/lumino/packages/signaling/src/index.ts
    title: @lumino/signaling 源码
---

# Signal/Slot 类型安全事件系统

## 为什么需要 Signal 而非 EventEmitter

Node.js 的 `EventEmitter` 和浏览器的 `EventTarget` 都是经典的事件机制，但它们存在类型安全问题：事件名是字符串，参数类型无法在编译时检查。

Lumino 的 [Signal](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/signaling/src/index.ts) 实现了**类型安全的信号/槽（Signal/Slot）机制**，灵感来自 Qt 的信号槽系统。它在编译时确保信号发送者类型和参数类型匹配。

## 核心类型

### ISignal 与 Signal

```typescript
// 只读接口，供外部订阅使用
interface ISignal<T, U> {
  connect(slot: Slot<T, U>, thisArg?: any): boolean;
  disconnect(slot: Slot<T, U>, thisArg?: any): boolean;
}

// 具体实现类
class Signal<T, U> implements ISignal<T, U> {
  constructor(sender: T);
  readonly sender: T;

  connect(slot: Slot<T, U>, thisArg?: any): boolean;
  disconnect(slot: Slot<T, U>, thisArg?: any): boolean;
  emit(args: U): void;
}

// Slot 是回调函数类型
type Slot<T, U> = (sender: T, args: U) => void;
```

泛型参数含义：
- `T`：信号发送者（sender）的类型
- `U`：信号发射时传递的参数类型

### 基本用法

```typescript
import { Signal, ISignal } from '@lumino/signaling';

class Counter {
  // 定义一个值变化信号：sender 是 Counter，参数是 number（新值）
  private _valueChanged = new Signal<this, number>(this);

  get valueChanged(): ISignal<this, number> {
    return this._valueChanged;
  }

  private _value = 0;

  get value(): number {
    return this._value;
  }

  set value(newValue: number) {
    if (this._value !== newValue) {
      this._value = newValue;
      this._valueChanged.emit(newValue);  // 发射信号
    }
  }
}

// 使用
const counter = new Counter();

// 连接槽函数
counter.valueChanged.connect((sender, newValue) => {
  console.log(`值变为: ${newValue}`);
  console.log(sender === counter);  // true
});

counter.value = 42;  // 控制台输出 "值变为: 42"
```

## 关键设计要点

### 1. sender 作为构造参数

`Signal` 构造时需要传入 sender 对象。这个 sender 会在 emit 时作为第一个参数传给 slot：

```typescript
const signal = new Signal<MyClass, string>(this);  // sender 是 this
signal.emit('hello');  // slot 收到 (this, 'hello')
```

这样设计的好处：
- slot 函数始终知道信号来自哪个对象
- 多个对象可以共享同一个 slot 函数，通过 sender 参数区分来源

### 2. ISignal 只读视图 vs Signal 写权限

类内部持有 `Signal<this, U>` 实例（可以 emit），对外暴露 `ISignal<this, U>`（只能 connect/disconnect）：

```typescript
class Model {
  // 私有：只有 Model 自己能 emit
  private _changed = new Signal<this, void>(this);

  // 公有只读：外部只能订阅
  get changed(): ISignal<this, void> {
    return this._changed;
  }
}
```

这是 TypeScript 中常见的"只读 getter 返回更宽类型"模式，确保外部代码不能随意发射信号。

### 3. thisArg 上下文管理

`connect` 支持传入 `thisArg`，Signal 内部会正确绑定上下文：

```typescript
class Observer {
  onValueChanged(sender: Counter, value: number): void {
    console.log(`Observer看到值变为: ${value}`);
  }
}

const observer = new Observer();
counter.valueChanged.connect(observer.onValueChanged, observer);
// 断开时也需要传入相同的 thisArg
counter.valueChanged.disconnect(observer.onValueChanged, observer);
```

**注意**：connect 和 disconnect 必须使用相同的 `slot` + `thisArg` 组合才能正确匹配。

### 4. connect 返回值

`connect()` 返回 `boolean`：
- `true`：连接成功
- `false`：该 slot+thisArg 组合已经连接过（避免重复连接）

## 内存安全：Signal.clearData

Signal 最巧妙的设计之一是 `Signal.clearData()` 静态方法：

```typescript
namespace Signal {
  function clearData(object: any): void;
}
```

这个方法一次性清理与指定对象关联的**所有**信号连接数据。Widget.dispose() 中就调用了它：

```typescript
dispose(): void {
  // ...
  Signal.clearData(this);  // 清理所有信号连接，防止内存泄漏
}
```

**为什么这很重要**？在传统的 addEventListener 模式中，你需要手动追踪每个监听器并逐个移除。忘记移除任何一个都会导致内存泄漏。而 `Signal.clearData()` 让你在对象销毁时一次性切断所有连接，无需手动追踪。

实现原理：Signal 使用一个全局 WeakMap 存储 sender → 连接列表的映射。`clearData` 直接删除该 sender 的所有条目。WeakMap 确保如果对象被 GC，其信号数据也会被自动回收。

## 信号连接的生命周期

```
sender.signal.connect(slot, thisArg)
  │
  ├→ 如果已连接相同 slot+thisArg → 返回 false（不重复添加）
  └→ 添加到连接列表 → 返回 true

sender.signal.emit(args)
  │
  └→ 遍历连接列表，同步调用每个 slot(sender, args)
      （注意：emit 是同步的，slot 会立即执行）

sender.signal.disconnect(slot, thisArg)
  │
  └→ 从连接列表移除匹配项（标记为 null，延迟清理）

Signal.clearData(sender)
  │
  └→ 删除 sender 的所有连接数据（dispose 时调用）
```

## 异常安全

Signal.emit() 会捕获 slot 函数抛出的异常，确保一个 slot 的异常不会影响其他 slot 的执行：

```typescript
// 伪代码逻辑
emit(args: U): void {
  for (const connection of this._connections) {
    try {
      connection.slot.call(connection.thisArg, this.sender, args);
    } catch (err) {
      console.error(err);  // 异常被捕获并打印，但不中断其他 slot
    }
  }
}
```

## Signal vs DOM 事件 vs EventEmitter

| 特性 | Lumino Signal | DOM addEventListener | Node.js EventEmitter |
|------|---------------|---------------------|---------------------|
| 类型安全 | ✅ 泛型编译时检查 | ❌ 字符串事件名 | ❌ 字符串事件名 |
| 自动清理 | ✅ clearData() 批量清理 | ❌ 需手动 removeEventListener | ❌ 需手动 removeListener |
| sender 信息 | ✅ 自动传入 sender | ❌ event.target（DOM目标） | ❌ 无 |
| 异常隔离 | ✅ slot 异常不中断其他 | ❌ 无隔离 | ✅ domain/error 事件 |
| 连接重复检测 | ✅ 自动去重 | ❌ 可重复添加 | ❌ 可重复添加 |
| 异步/同步 | 同步 emit | 异步派发（event loop） | 同步 emit |

## 常见使用模式

### 1. 属性变化通知

```typescript
class ViewModel {
  private _selectionChanged = new Signal<this, string[]>(this);
  get selectionChanged(): ISignal<this, string[]> { return this._selectionChanged; }

  private _selection: string[] = [];

  setSelection(ids: string[]): void {
    this._selection = [...ids];
    this._selectionChanged.emit(this._selection);
  }
}
```

### 2. 事件总线模式

```typescript
// 全局事件总线
class EventBus {
  readonly commandExecuted = new Signal<this, { id: string; args: any }>(this);
  readonly widgetAdded = new Signal<this, Widget>(this);
  readonly widgetRemoved = new Signal<this, Widget>(this);
}
```

### 3. 一次性连接

```typescript
function connectOnce<T, U>(
  signal: ISignal<T, U>,
  slot: Slot<T, U>,
  thisArg?: any
): void {
  const wrapper = (sender: T, args: U) => {
    signal.disconnect(wrapper as any);  // 注意：这种方式需要自己管理
    slot.call(thisArg, sender, args);
  };
  signal.connect(wrapper as any);
}
```

## 最佳实践

1. **对外暴露 ISignal 而非 Signal**：防止外部代码随意 emit
2. **dispose 时调用 Signal.clearData(this)**：自动清理所有连接
3. **disconnect 使用与 connect 相同的 slot+thisArg**：否则无法正确断开
4. **保持 slot 函数轻量**：emit 是同步的，重的 slot 会阻塞后续处理
5. **避免在 slot 中修改信号连接列表**：Signal 内部对此有保护，但最好避免

## 相关概念

- [IDisposable 资源管理模式](02-disposable-pattern.md) — Signal 与 disposable 配合使用
- [MessageLoop 消息循环](04-messaging-loop.md) — 消息和信号的区别：消息可异步合并，信号是同步立即
- [Widget 生命周期](05-widget-lifecycle.md) — Widget.disposed 是一个 Signal
