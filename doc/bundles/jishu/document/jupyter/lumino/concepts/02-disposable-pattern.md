---
type: Concept
title: IDisposable 资源管理模式
description: IDisposable 接口、DisposableDelegate、DisposableSet、IObservableDisposable、资源释放最佳实践
tags: [lumino, disposable, idisposable, resource-management, pattern]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: disposable-source
    resource: /external/libs/jupyter/lumino/packages/disposable/src/index.ts
    title: "@lumino/disposable 源码"
---

# IDisposable 资源管理模式

## 为什么需要 Disposable 模式

在复杂的 UI 应用中，资源泄漏是常见问题：忘记移除事件监听器、定时器未清理、DOM 节点未分离、信号连接未断开……这些都会导致内存泄漏和意外行为。

Lumino 采用 **IDisposable 模式**统一管理所有资源的生命周期。这是贯穿整个 Lumino 代码库的最基础模式，几乎所有对象都实现了它。

## 核心接口：IDisposable

IDisposable 定义在 `@lumino/disposable` 包中：

```typescript
interface IDisposable {
  /** 资源是否已被释放 */
  readonly isDisposed: boolean;

  /** 释放资源。调用后对象不应再被使用 */
  dispose(): void;
}
```

接口非常简单，只有两个成员：

- `isDisposed`：布尔标志，检查对象是否已释放
- `dispose()`：释放资源的方法，**必须幂等**（多次调用安全）

## DisposableDelegate：函数适配器

DisposableDelegate 将任意清理函数包装成 IDisposable：

```typescript
class DisposableDelegate implements IDisposable {
  constructor(fn: () => void);
  get isDisposed(): boolean;  // fn === null 时返回 true
  dispose(): void;            // 首次调用时执行 fn，然后将 fn 置 null
}
```

**核心实现要点**：

```typescript
dispose(): void {
  if (this._fn) {
    const fn = this._fn;
    this._fn = null;   // 先置 null，再执行，保证幂等
    fn();              // 即使 fn 内部再次调用 dispose() 也不会重复执行
  }
}
```

这个"先置 null 再调用"的模式是实现幂等 dispose 的关键技巧。

**使用示例**：

```typescript
// 注册一个事件监听，返回 Disposable 用于取消
function addEventListener(
  element: HTMLElement,
  type: string,
  handler: EventListener
): IDisposable {
  element.addEventListener(type, handler);
  return new DisposableDelegate(() => {
    element.removeEventListener(type, handler);
  });
}

// 使用
const listener = addEventListener(button, 'click', onClick);
// ... 
listener.dispose();  // 清理事件监听
```

Lumino 中大量 API 返回 `IDisposable`：
- `CommandRegistry.addCommand()` 返回 disposable 用于移除命令
- `CommandRegistry.addKeyBinding()` 返回 disposable 用于移除快捷键
- `Signal.connect()` 不需要手动管理（`Signal.clearData()` 批量清理）

## IObservableDisposable：带信号的 Disposable

IObservableDisposable 在 IDisposable 基础上增加了 `disposed` 信号：

```typescript
interface IObservableDisposable extends IDisposable {
  readonly disposed: ISignal<this, void>;
}
```

Widget 就实现了这个接口。外部可以通过监听 `disposed` 信号来响应对象释放：

```typescript
const widget = new Widget();
widget.disposed.connect(() => {
  console.log('Widget 已被释放');
});
widget.dispose();  // 触发 disposed 信号
```

## DisposableSet：批量管理

Lumino 还提供了 `DisposableSet`（在 `@lumino/disposable` 中），用于组合多个 disposable 一次性清理：

```typescript
// DisposableSet 实现 IDisposable，内部维护一组子 disposable
const set = new DisposableSet();
set.add(listener1);
set.add(listener2);
set.add(command);
// ...
set.dispose();  // 一次性释放所有资源
```

## 幂等 dispose 规则

Lumino 对 dispose 方法有严格的幂等要求：

1. **多次调用 `dispose()` 必须安全**：第二次及以后调用是 no-op
2. **dispose 期间允许调用 dispose**：如果清理回调中触发了对同一对象的 dispose，不能出错
3. **dispose 后访问属性应返回合理值**：如 `isDisposed` 返回 true，其他方法不抛异常

**Widget.dispose() 的实现**展示了完整的清理流程：

```typescript
dispose(): void {
  // 1. 幂等检查
  if (this.isDisposed) return;

  // 2. 设置标志 + 发射信号
  this.setFlag(Widget.Flag.IsDisposed);
  this._disposed.emit(undefined);

  // 3. 从父控件或 DOM 移除
  if (this.parent) {
    this.parent = null;          // 通过 parent setter 触发生命周期消息
  } else if (this.isAttached) {
    Widget.detach(this);
  }

  // 4. 释放布局
  if (this._layout) {
    this._layout.dispose();
    this._layout = null;
  }

  // 5. 释放标题
  this.title.dispose();

  // 6. 清理所有附加数据
  Signal.clearData(this);        // 清理所有信号连接
  MessageLoop.clearData(this);   // 清理消息队列和钩子
  AttachedProperty.clearData(this);  // 清理附加属性
}
```

## 最佳实践

### 编写自定义 Disposable

```typescript
class MyResource implements IDisposable {
  private _isDisposed = false;
  private _timer: number | null;

  constructor() {
    this._timer = window.setInterval(() => this.tick(), 1000);
  }

  get isDisposed(): boolean {
    return this._isDisposed;
  }

  dispose(): void {
    if (this._isDisposed) return;
    this._isDisposed = true;
    if (this._timer !== null) {
      clearInterval(this._timer);
      this._timer = null;
    }
    // 清理其他资源...
  }

  private tick(): void {
    if (this._isDisposed) return;  // 防御性检查
    // ...
  }
}
```

### 返回 Disposable 而非提供 remove 方法

当你编写 API 注册某种资源时，**返回 IDisposable** 而非提供独立的 `removeXxx()` / `unregister()` 方法：

```typescript
// ✅ 好的设计：返回 disposable
registerHandler(handler: Handler): IDisposable {
  this._handlers.push(handler);
  return new DisposableDelegate(() => {
    ArrayExt.removeFirstOf(this._handlers, handler);
  });
}

// ❌ 不好的设计：需要记住两个方法
addHandler(handler: Handler): void;
removeHandler(handler: Handler): void;
```

这种设计的好处：
- 统一了资源清理模式
- 可以放入 DisposableSet 批量管理
- 调用方不需要记住具体的移除 API

### 清理顺序

dispose 时应遵循以下顺序：
1. 先设置 `isDisposed` 标志
2. 发射 `disposed` 信号（通知外部）
3. 从父容器/宿主中移除自身
4. 释放子资源（layout、子 widget、事件监听等）
5. 清理所有关联数据（Signal/Message/AttachedProperty）

## 与其他语言 RAII 模式的对比

| 语言/平台 | 资源管理模式 | Lumino 的对应 |
|-----------|-------------|---------------|
| C# | `IDisposable` + `using` | `IDisposable`（无 using 语法糖） |
| Python | 上下文管理器 `with` | 无直接对应，但 dispose 模式类似 |
| Java | `AutoCloseable` + try-with-resources | 无直接对应 |
| C++ | RAII + 析构函数 | JavaScript 无析构函数，靠手动 dispose |
| Rust | `Drop` trait | 无 GC，所有权系统自动 drop |

JavaScript 的 GC 只能回收内存，不能自动清理 DOM 监听器、定时器、信号连接等外部资源。IDisposable 模式填补了这一空白。

## 相关概念

- [Signal/Slot 类型安全事件系统](03-signaling-system.md) — Signal 也遵循 disposable 模式
- [Widget 生命周期](05-widget-lifecycle.md) — Widget.dispose() 是最复杂的 dispose 实现
- [MessageLoop 消息循环](04-messaging-loop.md) — MessageLoop.clearData() 配合 dispose
