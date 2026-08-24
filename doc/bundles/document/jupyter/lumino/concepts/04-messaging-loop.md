---
type: Concept
title: MessageLoop 消息循环机制
description: Message 类、同步 sendMessage 与异步 postMessage、消息合并 Conflation、消息钩子 MessageHook、消息队列调度
tags: [lumino, messaging, message-loop, conflation, event-loop, widget-lifecycle]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: messaging-source
    resource: /external/libs/jupyter/lumino/packages/messaging/src/index.ts
    title: "@lumino/messaging 源码"
---

# MessageLoop 消息循环机制

## 消息 vs 信号：两种通信范式

Lumino 同时提供 Signal 和 Message 两种通信机制，它们解决不同问题：

| | Signal（信号） | Message（消息） |
|--|----------------|----------------|
| 通信模式 | 一对多广播 | 一对一投递 |
| 投递时机 | 同步立即 | sendMessage同步 / postMessage异步 |
| 压缩合并 | ❌ 不支持 | ✅ 支持 conflation 自动合并 |
| 拦截机制 | ❌ 无拦截 | ✅ MessageHook 钩子链 |
| 生命周期 | 通用事件 | Widget 生命周期驱动 |
| 典型用途 | 属性变化、状态通知 | 布局更新、显示隐藏、尺寸变化 |

理解这两者的区别是掌握 Lumino 的关键。

## 核心类型

### Message 基类

[Message](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/messaging/src/index.ts#L24-L101) 是所有消息的基类：

```typescript
class Message {
  constructor(type: string);
  readonly type: string;           // 消息类型字符串，用于区分和派发
  readonly isConflatable: boolean; // 是否可合并，默认 false
  conflate(other: Message): boolean;  // 合并逻辑，默认返回 false
}
```

消息通过 `type` 字符串标识类型。子类可以添加任意数据字段。例如 Widget 的 ResizeMessage：

```typescript
class ResizeMessage extends Message {
  constructor(width: number, height: number);
  readonly width: number;
  readonly height: number;
  static UnknownSize: ResizeMessage;  // 单例：未知尺寸
}
```

### ConflatableMessage：自动合并消息

[ConflatableMessage](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/messaging/src/index.ts#L116-L136) 是无状态的可合并消息：

```typescript
class ConflatableMessage extends Message {
  get isConflatable(): boolean;  // 始终 true
  conflate(other: ConflatableMessage): boolean;  // 始终 true
}
```

典型用途：`update-request` 消息。如果一个 Widget 在一个事件循环内被多次调用 `update()`，多个 update-request 消息会被合并为一个，避免重复布局计算。

### IMessageHandler 接口

```typescript
interface IMessageHandler {
  processMessage(msg: Message): void;
}
```

Widget 实现了这个接口，`processMessage` 根据消息类型分发到具体的 `onXxx` 处理方法。

## MessageLoop：全局消息循环

[MessageLoop](file:///d:/spaces/SpecWeave/external/libs/jupyter/lumino/packages/messaging/src/index.ts#L201-L641) 是一个命名空间（非类），提供全局静态方法管理消息投递：

### sendMessage：同步立即投递

```typescript
function sendMessage(handler: IMessageHandler, msg: Message): void;
```

- 消息**立即同步**处理，不会进入队列
- 消息不会被合并（因为是立即处理）
- 处理流程：钩子链 → `processMessage`
- 钩子或处理器抛出的异常会被捕获并通过 `exceptionHandler` 记录（默认 `console.error`）

使用场景：需要立即处理的消息，如 `child-removed`、`before-attach` 等生命周期消息。

### postMessage：异步排队投递

```typescript
function postMessage(handler: IMessageHandler, msg: Message): void;
```

- 消息进入队列，在下一个微任务（Promise.then）中批量处理
- **支持消息合并**：如果队列中已有同类型可合并消息，则调用 `conflate()` 合并
- 使用 `LinkedList` 作为消息队列，使用哨兵值（sentinel）分隔批次
- 处理期间新加入的消息会在下一批次处理

使用场景：可以延迟合并的消息，如 `update-request`（重布局）、`fit-request`（重计算尺寸）。

### installMessageHook / removeMessageHook

```typescript
function installMessageHook(handler: IMessageHandler, hook: MessageHook): void;
function removeMessageHook(handler: IMessageHandler, hook: MessageHook): void;

type MessageHook = IMessageHook | ((handler: IMessageHandler, msg: Message) => boolean);

interface IMessageHook {
  messageHook(handler: IMessageHandler, msg: Message): boolean;
}
```

消息钩子允许在消息到达 handler **之前**拦截消息：

- 钩子返回 `true`：消息继续传递给下一个钩子或 handler
- 钩子返回 `false`：消息被拦截，不再传递
- **最新安装的钩子最先执行**（栈式顺序）
- 钩子使用 WeakMap 存储，不会阻止 GC
- 移除钩子时先标记为 null，延迟清理（避免在钩子执行期间修改数组）

```typescript
// 示例：拦截 Widget 的关闭消息
MessageLoop.installMessageHook(widget, (handler, msg) => {
  if (msg.type === 'close-request' && hasUnsavedChanges()) {
    showSaveDialog();
    return false;  // 拦截关闭消息
  }
  return true;  // 放行其他消息
});
```

### clearData

```typescript
function clearData(handler: IMessageHandler): void;
```

清理指定 handler 的所有消息数据：清空消息队列中该 handler 的待处理消息，移除所有已安装的钩子。Widget.dispose() 中调用。

### flush

```typescript
function flush(): void;
```

立即处理队列中所有待处理消息，不等待下一个微任务。主要用于解决浏览器特殊场景（如某些事件需要同步处理）。有递归保护，不会无限递归。

## 消息合并（Conflation）机制

消息合并是 Lumino 性能优化的核心之一。当多次 post 同类型可合并消息时，只保留一份最新状态：

```
postMessage(widget, updateMsg1) → 入队
postMessage(widget, updateMsg2) → 发现同类型可合并消息
                                  → 调用 updateMsg1.conflate(updateMsg2)
                                  → 如果返回 true，updateMsg2 不重复入队
                                  → 如果返回 false，updateMsg2 正常入队
```

**Widget 中的 update-request 消息**就是典型的合并消息：

```typescript
// Widget.update() 发送 update-request
update(): void {
  if (!this.isDisposed) {
    MessageLoop.sendMessage(this, Widget.Msg.UpdateRequest);
    // 注意：这里用的是 sendMessage（同步），但布局层会 post 给子组件
  }
}
```

Layout 的 `onUpdateRequest` 默认给所有子 widget 发送 `UnknownSize` resize 消息，这些 resize 消息通过 postMessage 异步派发并合并，避免在一次更新中多次触发布局计算。

## 消息队列调度

```
postMessage(handler, msg)
  │
  ├→ msg.isConflatable?
  │   ├→ No → enqueueMessage(handler, msg)
  │   └→ Yes ─→ 队列中已有同类型同handler可合并消息?
  │              ├→ Yes: oldMsg.conflate(newMsg) → 成功则不入队
  │              └→ No → enqueueMessage(handler, msg)
  │
enqueueMessage(handler, msg)
  │
  ├→ 加入 LinkedList 尾部
  └→ 队列为空时 schedule(runMessageLoop)
       │
       └→ Promise.resolve().then(runMessageLoop)
            （微任务，在当前宏任务结束后、下一次渲染前执行）

runMessageLoop()
  │
  ├→ 在队列尾部添加哨兵值 sentinel
  │
  └→ while(true)
       ├→ 取出队首消息
       ├→ 如果是 sentinel → 退出循环
       ├→ 如果 handler 和 msg 都有效 → sendMessage(handler, msg)
       └→ （处理期间新入队的消息会在 sentinel 之后，下一批处理）
```

## Widget 标准消息类型

Widget 定义了一组标准生命周期消息，Layout 也通过 `processParentMessage` 转发这些消息：

| 消息类型 | 触发时机 | 方向 |
|----------|---------|------|
| `before-attach` | 节点插入 DOM 前 | Widget → Layout → 子Widget |
| `after-attach` | 节点插入 DOM 后 | 同上 |
| `before-show` | 显示前 | 同上（仅非隐藏的子Widget） |
| `after-show` | 显示后 | 同上 |
| `resize` | 尺寸变化时 | 父Layout → 子Widget |
| `update-request` | 请求更新/重布局 | Widget → Layout |
| `fit-request` | 请求重新计算尺寸 | Widget → Layout |
| `before-hide` | 隐藏前 | 同上（仅非隐藏的子Widget） |
| `after-hide` | 隐藏后 | 同上 |
| `child-removed` | 子Widget移除时 | 父Widget → Layout |
| `child-shown` | 子Widget显示时 | 父Widget → Layout |
| `child-hidden` | 子Widget隐藏时 | 父Widget → Layout |
| `before-detach` | 节点移出 DOM 前 | Widget → Layout → 子Widget |
| `after-detach` | 节点移出 DOM 后 | 同上 |
| `close-request` | 请求关闭 Widget | 发送到 Widget |
| `activate-request` | 请求激活（获得焦点） | 发送到 Widget |

## 消息处理链

当一个消息被发送到 Widget 时，完整处理链如下：

```
MessageLoop.sendMessage(widget, msg)
  │
  ├→ 查找 widget 上安装的消息钩子（MessageHook）
  │   │
  │   └→ 从最新到最旧依次执行钩子
  │       ├→ 任何一个钩子返回 false → 消息被拦截，终止处理
  │       └→ 所有钩子返回 true → 继续
  │
  └→ widget.processMessage(msg)
      │
      └→ switch(msg.type)
          case 'resize' → onResize(msg)
          case 'update-request' → onUpdateRequest(msg)
          case 'before-show' → onBeforeShow(msg)
          case 'after-show' → onAfterShow(msg)
          case 'before-hide' → onBeforeHide(msg)
          // ... 等等
```

Layout 的 `processParentMessage` 遵循相同模式，大多数消息默认转发给所有子 Widget。

## 异常处理

MessageLoop 提供了可定制的异常处理器：

```typescript
// 获取当前异常处理器（默认 console.error）
const handler = MessageLoop.getExceptionHandler();

// 设置自定义异常处理器
MessageLoop.setExceptionHandler((err: Error) => {
  // 可以上报到错误监控系统
  errorReporting.captureException(err);
});
```

所有在消息钩子和 processMessage 中抛出的异常都会被捕获并传给异常处理器，不会中断消息循环的运行。这保证了一个 Widget 的错误不会导致整个应用崩溃。

## 相关概念

- [Signal/Slot 类型安全事件系统](03-signaling-system.md) — 对比消息与信号的适用场景
- [Widget 生命周期](05-widget-lifecycle.md) — 消息驱动 Widget 生命周期的具体流程
- [布局系统详解](06-layout-system.md) — Layout 如何通过消息实现尺寸管理
