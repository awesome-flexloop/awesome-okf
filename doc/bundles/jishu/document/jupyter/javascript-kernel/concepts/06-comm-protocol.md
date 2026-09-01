---
type: Concept
title: Comm 协议
description: Jupyter 自定义消息通道、CommManager 实现和 Widget 通信原理
tags: [comm, protocol, messaging, ipywidgets, custom-messages, bidirectional]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-comm
    title: comm.ts
  - id: jk-comm-start
    title: comm-startup.ts
  - id: jk-widget
    title: widgets/widget.ts
---

# Comm 协议

Comm 是 Jupyter 内核和前端之间的自定义双向通信通道。JavaScript Kernel 通过 `CommManager` 类实现完整的 comm 协议，是 Widget 系统和自定义交互的基础。

## 什么是 Comm？

Comm 是内核和前端之间的**命名消息通道**。每个 comm 有一个唯一 ID，关联一个 `target_name`（处理模块名）。双方可以通过 comm 通道发送任意 JSON 数据和二进制缓冲区。

```
┌──────────┐  comm_open/comm_msg/comm_close  ┌──────────┐
│  Kernel   │◄──────────────────────────────►│ Frontend │
│  (runtime)│                                │  (Lab)   │
└──────────┘                                └──────────┘
     │                                            │
     ├─ Jupyter.widget (Widget 通信)               │
     ├─ jupyter.widget.control                    │
     └─ 自定义 comm (registerCommTarget)          │
```

## Comm 协议消息类型

| 消息类型 | 方向 | 说明 |
|---------|------|------|
| `comm_open` | Kernel ↔ Frontend | 打开 comm 通道 |
| `comm_msg` | Kernel ↔ Frontend | 发送消息数据 |
| `comm_close` | Kernel ↔ Frontend | 关闭 comm 通道 |

每条消息包含：
- `comm_id`：通道唯一标识
- `target_name`（仅 comm_open）：target 处理器名称
- `data`：JSON 消息体
- `buffers`（可选）：二进制数据数组

## CommManager

`CommManager` 管理所有 comm 实例和 target 处理器的注册。

### 创建 CommManager

CommManager 需要两个回调：
- `sendCommMessage(type, commId, data, targetName?, buffers?, parentMessageId?)`：发送 comm 消息到前端
- `onWidgetCommOpen?(commId, data, buffers?, parentMessageId?)`：widget comm 打开回调

### 打开 Comm (内核主动)

```javascript
// 在 kernel 代码中（Notebook 单元格内）
const comm = Jupyter.comm.open(targetName, data, metadata, buffers);
```

`open()` 方法：
1. 生成唯一 comm ID（`c-${UUID.uuid4()}`）
2. 创建 Comm 实例
3. 发送 `comm_open` 消息到前端
4. 等待 target 处理器注册（如果前端还未注册）
5. 返回 Comm 实例

### 注册 Target Handler

```javascript
// 前端打开的 comm 需要内核端注册 target handler
Jupyter.comm.registerTarget(targetName, handler);
```

Handler 签名：
```javascript
function handler(comm, message): Promise<void> | void {
  // comm: Comm 实例
  // message: { data, buffers, parentMessageId }
  comm.onMsg = (data) => { /* 处理前端消息 */ };
  comm.send({ result: "ok" });
}
```

### 处理前端打开的 Comm

当前端发送 `comm_open`（target_name 为已注册的 target）时：
1. CommManager 创建 Comm 实例
2. 查找注册的 target handler
3. 调用 handler(comm, message)
4. 返回 Comm 实例

## Comm 类

每个 Comm 实例代表一个双向通信通道。

### Comm 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `commId` | `string` | comm 唯一 ID（只读） |
| `targetName` | `string \| undefined` | target 名称（只读） |
| `onMsg` | `function \| null` | 消息回调，接收 `{ data, buffers }` |
| `onClose` | `function \| null` | 关闭回调，接收 `{ data, buffers }` |
| `isDisposed` | `boolean` | 是否已关闭 |

### Comm 方法

```javascript
// 发送消息到前端
comm.send(data, options?);
// options: { buffers?: ArrayBuffer[]; parentMessageId?: string }

// 关闭 comm
comm.close(data?);
```

- `send()`：发送 `comm_msg`，自动结构化克隆处理数据
- `close()`：发送 `comm_close` 消息，清理回调和引用

### Comm 内部方法（CommManager 使用）

| 方法 | 说明 |
|------|------|
| `_handleMsg(data, buffers?)` | 处理来自前端的 comm_msg |
| `_handleClose(data, buffers?)` | 处理来自前端的 comm_close |
| `_setTargetHandler(handler)` | 设置 target handler（前端打开后调用） |

## Widget Comm 协议

Widget 使用特殊的 `jupyter.widget` target，消息遵循 Widget 协议：

```javascript
// Widget 创建时自动打开 comm
this._comm = manager.open('jupyter.widget', {
  state: this._serializeState(this._state),
  buffer_paths: []
}, { version: WIDGET_PROTOCOL_VERSION });
```

### Widget 消息格式

**State Update（状态同步）**：
```json
{
  "method": "update",
  "state": {
    "value": 42,
    "description": "Slider"
  },
  "buffer_paths": []
}
```

**Custom Message（自定义消息）**：
```json
{
  "method": "custom",
  "content": { /* 自定义数据 */ }
}
```

**Backend Call（前端调用内核方法）**：
```json
{
  "method": "request_state"
}
// 或 Button 的 click 消息
{
  "method": "custom",
  "content": {
    "event": "click"
  }
}
```

## Bootstrap Widget Target (comm-startup.ts)

内核启动时自动注册 `jupyter.widget` target handler，用于：
- 前端发起 widget comm 连接
- 恢复 widget 状态（前端请求 full state）
- 处理前端发来的 update/custom 消息

### 内置 Comm Target

| target_name | 说明 |
|------------|------|
| `jupyter.widget` | Widget 主通道（自动注册） |
| `jupyter.widget.control` | Widget 控制通道（自动注册） |
| 自定义 target | 通过 `registerCommTarget()` 或 startup extension 注册 |

## 注册自定义 Comm Target

有两种方式注册自定义 comm target：

### 方式 1：在 Notebook 中注册

```javascript
Jupyter.comm.registerTarget('my-custom-target', (comm, msg) => {
  console.log('Got comm open:', msg.data);
  
  comm.onMsg = ({ data, buffers }) => {
    console.log('Got message:', data);
    comm.send({ echo: data });
  };
  
  comm.onClose = ({ data }) => {
    console.log('Comm closed:', data);
  };
});
```

### 方式 2：通过 Startup Extension 预注册

前端插件可以预加载模块注册 comm target，无需用户手动执行：

```typescript
// 前端插件代码
startup.registerStartupExtension({
  id: 'my-extension:comm',
  activate: async (context) => {
    await context.registerCommTarget(
      'my-extension-target',
      './my-comm-handler.js'  // ES 模块路径
    );
  }
});
```

ES 模块需要导出指定名称的 handler 创建函数（默认为 `create`）：

```javascript
// my-comm-handler.js
export async function create({ commManager }) {
  commManager.registerTarget('my-extension-target', (comm, msg) => {
    // handler 逻辑
  });
}
```

## Comm 消息流：Slider 值变化

```
前端拖动滑块
    │
    ▼
comm_msg (method: "update", state: { value: 75 })
    │
    ▼
CommManager._handleCommMsg
    │
    ▼
Widget._handleCommMsg
    │
    ├─► method === 'update' → _applyState(state)
    │       └─► 更新 _state
    │       └─► 触发 change:value 和 change 事件
    │       └─► ⚠️ 不发送回前端（不回显）
    │
    ├─► method === 'request_state' → 回发 full state
    │
    └─► method === 'custom' → 触发 'custom' 事件
```

### 重要：避免回显循环

当 Widget 收到前端的 update 消息时，只更新状态和触发事件，**不重新发送 update 回前端**。这防止了双向同步的无限循环：

```typescript
private _handleCommMsg(data: any, buffers?: ArrayBuffer[]): void {
  const method = data.method;
  switch (method) {
    case 'update':
      // 处理来自前端的状态更新
      this._applyState(data.state);  // 仅更新本地状态，不 _syncState
      break;
    // ...
  }
}
```

而内核端 `set()` 方法调用 `_syncState()` 发送 update 到前端，触发事件（包含 front-end 标记）：

```typescript
protected set(key: string | object, value?: unknown): void {
  // ...值变化检测
  this._syncState(changedKeys);  // 发送到前端
  for (const key of changedKeys) {
    this.fire(`change:${key}`, newVal, oldVal);
  }
  this.fire('change', changeDetails);
}
```

## Widget 协议版本

WIDGET_PROTOCOL_VERSION = `'2.1.0'`

对应 @jupyter-widgets/base 的控制协议版本。

## 跨环境 Comm 消息传递

Comm 消息从运行时（iframe/Worker）到前端的完整路径：

```
Runtime (iframe/Worker)
    │
    │ Comlink proxy (onOutput callback)
    │
    ▼
AbstractRuntimeBackend._sendOutput
    │
    │ onOutput callback（构造时传入）
    │
    ▼
JavaScriptKernel._handleOutputMessage
    │
    ├─► stream → publishStream
    ├─► execute_result → publishExecuteResult
    ├─► execute_error → publishExecuteError
    ├─► comm_open → publishCommOpen
    ├─► comm_msg → publishCommMsg
    ├─► comm_close → publishCommClose
    ├─► display_data → publishDisplayData
    ├─► update_display_data → publishUpdateDisplayData
    ├─► input_request → publishInputRequest
    └─► clear_output → publishClearOutput
```

`publishComm*` 方法来自 JupyterLite `BaseKernel`，通过 WebSocket（在 JupyterLite 中为 postMessage）发送到前端。

## Buffer 支持

Comm 消息支持二进制数据传输（`ArrayBuffer`）：

```javascript
// 发送二进制数据
const buffer = new ArrayBuffer(1024);
comm.send({ type: 'data' }, { buffers: [buffer] });

// 接收二进制数据
comm.onMsg = ({ data, buffers }) => {
  const [buffer] = buffers;  // ArrayBuffer[]
  console.log(data, buffer);
};
```

Buffer 传输通过 Comlink 的结构化克隆机制传递，不需要 base64 编码。

## 相关文档

- [05-Widget系统](05-widget-system.md) — Widget 基于 Comm 构建
- [08-启动扩展](08-startup-extensions.md) — 通过 startup extension 注册 comm target
- [02-内核架构](02-kernel-architecture.md) — 内核如何将 comm 消息传递给后端
