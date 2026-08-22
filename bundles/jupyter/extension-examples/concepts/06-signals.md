---
type: Concept
title: 信号与事件通信
description: 使用Lumino Signal实现Widget间的松耦合通信，掌握Signal的connect/emit模式
tags: [jupyterlab, signals, lumino, event-communication, widget-communication]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: docs-model-src
    resource: /references/core-api-tokens.md
    title: documents/src/model.ts Signal使用模式
---

## Lumino Signal 机制

JupyterLab/Lumino 使用 **Signal（信号）** 实现发布-订阅模式的事件通信。Signal 比 DOM 事件更通用，可以在任意对象间传递类型安全的事件通知。

```typescript
import { ISignal, Signal } from '@lumino/signaling';
```

## 基本用法

### 定义Signal

```typescript
class ExampleDocModel {
  // 公开ISignal接口（只允许订阅，不允许外部emit）
  get stateChanged(): ISignal<this, IChangedArgs<any>> {
    return this._stateChanged;
  }

  // 私有Signal实例（允许本类emit）
  private _stateChanged = new Signal<this, IChangedArgs<any>>(this);
}
```

关键模式：
- 公共getter返回 `ISignal<T, U>` 接口（只读，只能connect）
- 私有字段存储 `Signal<T, U>` 实例（可以emit）
- Signal构造函数接收 `this` 作为sender参数

### 发射Signal

```typescript
protected triggerStateChange(args: IChangedArgs<any>): void {
  this._stateChanged.emit(args);
}

// 设置dirty属性时发射信号
set dirty(newValue: boolean) {
  if (newValue === this._dirty) return;
  this._dirty = newValue;
  this.triggerStateChange({ name: 'dirty', oldValue: !newValue, newValue });
}
```

### 订阅Signal

```typescript
// 在Widget中监听model的变化
context.ready.then(() => {
  this._model.contentChanged.connect(this._onContentChanged, this);
  this._model.clientChanged.connect(this._onClientChanged, this);
});

// 回调函数
private _onContentChanged = (): void => {
  this._cube.style.left = this._model.position.x + 'px';
  this._cube.style.top = this._model.position.y + 'px';
  this._cube.innerText = this._model.content;
};
```

`connect(slot, thisArg)` 方法：
- 第一个参数是回调函数
- 第二个参数是 `this` 上下文
- 返回boolean表示连接是否成功
- 使用箭头函数属性确保 `this` 绑定正确

### 断开Signal连接

```typescript
dispose(): void {
  if (this.isDisposed) return;
  this._model.contentChanged.disconnect(this._onContentChanged);
  Signal.clearData(this);  // 清除该对象所有信号连接
  super.dispose();
}
```

- `disconnect(slot, thisArg)` 断开特定连接
- `Signal.clearData(obj)` 清除obj对象的所有信号连接（重要！防止内存泄漏）

## Signal在JupyterLab中的典型应用

### 1. Model → Widget 数据变化通知

documents示例中，Model变化通过Signal通知Widget更新UI：

```typescript
// Model中
private _onSharedModelChanged = (sender, changes) => {
  if (changes.contentChange || changes.positionChange) {
    this.triggerContentChange();  // emit contentChanged信号
  }
};

// Widget中
this._model.contentChanged.connect(this._onContentChanged);
// → 更新DOM显示新位置和内容
```

### 2. Factory → 注册逻辑 Widget创建通知

```typescript
widgetFactory.widgetCreated.connect((sender, widget) => {
  widget.context.pathChanged.connect(() => {
    tracker.save(widget);
  });
  tracker.add(widget);
});
```

`widgetCreated` 信号在每次创建新Widget时触发，允许外部逻辑追踪Widget。

### 3. 设置变化监听

settings示例展示了设置变更通知：

```typescript
setting.changed.connect(loadSetting);  // 设置改变时重新加载
```

### 4. Widget生命周期事件

```typescript
logConsoleWidget.disposed.connect(() => {
  logConsoleWidget = null;
  commands.notifyCommandChanged();
});
```

所有Widget都有 `disposed` 信号，可以监听Widget销毁事件。

### 5. Awareness状态变化

collaborative document示例监听其他用户的光标位置变化：

```typescript
this.sharedModel.awareness.on('change', this._onClientChanged);
```

这是Yjs的awareness事件（非Lumino Signal，但模式类似）。

## 信号 vs 回调 vs Promise

| 机制 | 适用场景 | 特点 |
|------|---------|------|
| Signal | 多次发生的事件 | 一对多，可连接/断开 |
| Promise | 一次性异步结果 | 一发一收，then/await |
| 回调函数 | 简单通知 | 一对一，需手动管理 |
| DOM Event | DOM层面的用户交互 | 冒泡/捕获机制 |

**选择原则**：
- 数据变化可能多次发生 → Signal
- 异步操作的一次性结果 → Promise
- 父子组件直接通信 → 回调函数
- 用户输入（点击/鼠标/键盘）→ DOM事件

## Signal最佳实践

1. **始终在dispose中断开连接**：使用 `Signal.clearData(this)` 确保无内存泄漏
2. **使用箭头函数作为slot**：`private _handler = () => {}` 避免bind问题
3. **公共API暴露ISignal而非Signal**：防止外部代码随意emit
4. **避免在slot中做重操作**：Signal是同步的，emit会阻塞所有slot执行
5. **Slot中不要修改sender状态**：可能导致意外的递归触发

## 示例：两个Widget通过Signal通信

signals示例展示了面板Widget通过Signal与子组件通信的模式：

```typescript
// 面板Widget创建命令并打开
function activate(app, palette, translator, launcher) {
  commands.addCommand(CommandIDs.create, {
    label: trans.__('Open the Signal Example Panel'),
    execute: createPanel  // createPanel创建SignalExamplePanel并add到shell
  });
}
```

SignalExamplePanel 内部包含子Widget，通过Signal连接model和view，类似kernel-messaging和documents示例的模式：
1. 创建Model（持有数据和业务逻辑）
2. 创建View/Widget（持有DOM引用）
3. Model的Signal连接到View的更新方法
4. View的用户操作调用Model的方法
5. Model状态变化通过Signal通知View更新

这是典型的MVC/MVP模式，Signal充当了Model→View的变更通知通道。

## 相关概念

- [Widget与Shell布局](/concepts/05-widgets-shell.md)
- [自定义文档类型](/concepts/12-documents.md)
- [Kernel交互](/concepts/11-kernel-interaction.md)
- [核心API与Token参考](/references/core-api-tokens.md)
