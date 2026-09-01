---
type: Example
title: 使用 Signal 实现组件通信
description: 定义和发射Signal、连接和断开Slot、Signal传递数据、防止内存泄漏
tags: [lumino, signal, slot, event, communication, observer]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: signaling-source
    resource: /external/libs/jupyter/lumino/packages/signaling/src/index.ts
    title: "@lumino/signaling 源码"
prerequisites:
  - /lumino/concepts/03-signaling-system
  - /lumino/concepts/02-disposable-pattern
---

# 示例：使用 Signal 实现组件通信

本示例演示如何使用 Signal/Slot 机制在组件之间实现类型安全的事件通信。

## 目标

构建一个简单的计数器组件，使用 Signal 在值变化时通知外部，并展示如何正确连接和断开信号监听。

## 完整代码

```typescript
import { Signal, ISignal } from '@lumino/signaling';
import { Message, Widget } from '@lumino/widgets';
import '@lumino/default-theme/style/index.css';

// 1. 定义携带数据的事件类型
interface ICounterChangedArgs {
  oldValue: number;
  newValue: number;
}

// 2. 定义发送信号的Widget
class CounterWidget extends Widget {
  constructor() {
    super();
    this.addClass('counter-widget');
    this._value = 0;

    this.node.innerHTML = `
      <p>当前值: <span class="value">0</span></p>
      <button class="increment">+1</button>
      <button class="decrement">-1</button>
    `;
  }

  // 暴露ISignal接口（外部只能connect，不能emit）
  get valueChanged(): ISignal<this, ICounterChangedArgs> {
    return this._valueChanged;
  }

  get value(): number {
    return this._value;
  }

  protected onAfterAttach(msg: Message): void {
    super.onAfterAttach(msg);
    this.node.addEventListener('click', this._onClick);
  }

  protected onBeforeDetach(msg: Message): void {
    this.node.removeEventListener('click', this._onClick);
    super.onBeforeDetach(msg);
  }

  private _onClick = (event: MouseEvent) => {
    const target = event.target as HTMLElement;
    if (target.classList.contains('increment')) {
      this._increment();
    } else if (target.classList.contains('decrement')) {
      this._decrement();
    }
  };

  private _increment(): void {
    const oldValue = this._value;
    this._value++;
    this._updateDisplay();
    // 发射信号，传递旧值和新值
    this._valueChanged.emit({ oldValue, newValue: this._value });
  }

  private _decrement(): void {
    const oldValue = this._value;
    this._value--;
    this._updateDisplay();
    this._valueChanged.emit({ oldValue, newValue: this._value });
  }

  private _updateDisplay(): void {
    const span = this.node.querySelector('.value')!;
    span.textContent = String(this._value);
  }

  private _value = 0;
  private _valueChanged = new Signal<this, ICounterChangedArgs>(this);
}

// 3. 创建接收信号的监听器
class ValueDisplay {
  constructor(container: HTMLElement) {
    this._container = container;
    this._el = document.createElement('div');
    this._el.className = 'log-display';
    this._container.appendChild(this._el);
  }

  // Slot方法：接收CounterWidget发射的信号
  onValueChanged = (sender: CounterWidget, args: ICounterChangedArgs) => {
    const entry = document.createElement('p');
    entry.textContent = `值从 ${args.oldValue} 变为 ${args.newValue}`;
    this._el.appendChild(entry);
  };

  private _container: HTMLElement;
  private _el: HTMLElement;
}

// 4. 主函数：连接信号
function main(): void {
  const counter = new CounterWidget();
  const display = new ValueDisplay(document.body);

  // 连接信号
  counter.valueChanged.connect(display.onValueChanged, display);
  //                                Slot方法             thisArg

  Widget.attach(counter, document.body);

  // 也可以用匿名函数作为Slot
  counter.valueChanged.connect((sender, args) => {
    console.log(`[Logger] 值变化: ${args.oldValue} → ${args.newValue}`);
  });

  // 5秒后断开display的监听（演示断开连接）
  setTimeout(() => {
    console.log('断开display监听');
    counter.valueChanged.disconnect(display.onValueChanged, display);
  }, 5000);

  // 10秒后dispose counter（自动清理所有信号）
  setTimeout(() => {
    console.log('销毁counter');
    counter.dispose();
    // dispose后Signal自动清除所有连接，不会再有回调触发
  }, 10000);
}

window.addEventListener('DOMContentLoaded', main);
```

## 关键点说明

### 1. 暴露 ISignal 而非 Signal

```typescript
// ✅ 最佳实践：对外暴露ISignal（只读接口）
get valueChanged(): ISignal<this, ICounterChangedArgs> {
  return this._valueChanged;
}
private _valueChanged = new Signal<this, ICounterChangedArgs>(this);

// ❌ 不好：外部可以随意调用emit()
readonly valueChanged = new Signal<this, ICounterChangedArgs>(this);
```

外部代码通过 `ISignal` 接口只能 `connect`/`disconnect`，不能调用 `emit()`，保证信号发射的控制权在发送方手中。

### 2. thisArg 的重要性

```typescript
counter.valueChanged.connect(display.onValueChanged, display);
//                                       Slot              thisArg
```

如果 Slot 是一个方法（需要 `this` 访问实例属性），必须提供 `thisArg`。如果使用箭头函数（已经绑定 this），可以不传 thisArg：

```typescript
counter.valueChanged.connect((sender, args) => {
  // 箭头函数捕获词法this，不需要thisArg
  console.log(args.newValue);
});
```

### 3. 断开连接

```typescript
// 断开特定连接（需要提供与connect相同的slot和thisArg）
counter.valueChanged.disconnect(display.onValueChanged, display);

// 断开某个对象的所有连接
Signal.disconnectAll(display);  // 断开display在所有Signal上的连接

// 断开某个sender的所有连接
Signal.clearData(counter);  // 断开counter的所有信号连接
```

### 4. 内存安全：dispose 自动清理

```typescript
counter.dispose();
// 内部调用 Signal.clearData(this)
// 所有对counter信号的连接被清理
// 不会再有回调被调用
// 防止内存泄漏
```

### 5. 对比 DOM addEventListener

| 特性 | Signal.connect() | addEventListener() |
|------|------------------|---------------------|
| 类型安全 | ✅ 泛型参数约束 sender 和 args 类型 | ❌ Event 无参数类型 |
| 发送者身份 | ✅ sender 参数可区分多个发送源 | ❌ event.target 可能变化 |
| 自定义数据 | ✅ 任意类型 args | ❌ 只能通过 Event 子类扩展 |
| 自动清理 | ✅ dispose 时 Signal.clearData | ❌ 必须手动 removeEventListener |
| 多次连接 | ✅ 同一(slot, thisArg)只能连一次 | ❌ 同一listener多次addEventListener会多次触发 |

## 多Widget通信场景

```typescript
// 中介者模式：使用Signal做事件总线
class EventBus {
  readonly commandExecuted = new Signal<this, { command: string; args: any }>(this);
  readonly widgetOpened = new Signal<this, { widget: Widget }>(this);
  readonly widgetClosed = new Signal<this, { widget: Widget }>(this);
}

const bus = new EventBus();

// 插件A发射事件
bus.commandExecuted.emit({ command: 'save', args: {} });

// 插件B监听
bus.commandExecuted.connect((sender, args) => {
  if (args.command === 'save') saveDocument();
});
```

## 扩展练习

1. 添加一个 `reset()` 方法，点击重置按钮时值归零并发射信号
2. 创建两个 CounterWidget，用信号同步它们的值
3. 使用 `DisposableSet` 管理多个信号连接的生命周期
4. 实现一个简单的 EventBus，使用 Signal 做发布/订阅
