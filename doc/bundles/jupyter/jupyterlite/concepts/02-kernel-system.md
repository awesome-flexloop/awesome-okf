---
type: Concept
title: 内核系统
description: BaseKernel抽象基类、消息路由机制、LiteKernelClient客户端、Worker内核通信模型
tags: [kernel, basickernel, messaging, websocket, worker, mutex]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:14:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-source
    resource: /references/kernel-source.md
    title: 内核系统信源
---

## BaseKernel 抽象类

`BaseKernel` 是所有 JupyterLite 内核实现的基类，位于 `packages/services/src/kernel/base.ts`。它提供了 Jupyter 内核消息协议的标准处理框架，子类只需实现具体的抽象方法。

### 构造函数

```typescript
constructor(options: IKernel.IOptions)
```

`IOptions` 包含：
- `id: string` — 内核唯一ID
- `name: string` — 内核名称（如 `python`、`javascript`）
- `location: string` — 内核启动的虚拟文件系统路径
- `sendMessage: (msg: KernelMessage.IMessage) => void` — 消息发送回调

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | `string` | 内核唯一标识（UUID） |
| `name` | `string` | 内核类型名称 |
| `location` | `string` | 启动目录路径 |
| `ready` | `Promise<void>` | 内核就绪Promise |
| `executionCount` | `number` | 当前执行计数 |
| `parentHeader` | `IHeader \| undefined` | 当前执行请求的父header |
| `parent` | `IMessage \| undefined` | 当前父消息（模拟ipykernel的get_parent） |
| `isDisposed` | `boolean` | 是否已销毁 |
| `disposed` | `ISignal<this, void>` | 销毁信号 |

## 消息处理路由

`handleMessage(msg)` 是内核消息的入口点，它按照 Jupyter Wire Protocol 的消息类型进行分发：

```typescript
async handleMessage(msg: KernelMessage.IMessage): Promise<void> {
  this._busy(msg);          // 发送busy状态
  this._parent = msg;       // 记录父消息

  switch (msg.header.msg_type) {
    case 'kernel_info_request':  await this._kernelInfo(msg); break;
    case 'execute_request':      await this._execute(msg); break;
    case 'input_reply':          this.inputReply(msg.content); break;
    case 'inspect_request':      await this._inspect(msg); break;
    case 'is_complete_request':  await this._isCompleteRequest(msg); break;
    case 'complete_request':     await this._complete(msg); break;
    case 'history_request':      await this._historyRequest(msg); break;
    case 'comm_open':            await this.commOpen(msg); break;
    case 'comm_msg':             await this.commMsg(msg); break;
    case 'comm_close':           await this.commClose(msg); break;
  }

  this._idle(msg);          // 发送idle状态
}
```

### 消息处理流程

1. **进入时**：发送 `status: busy` 消息到 iopub 通道
2. **处理中**：根据 msg_type 调用对应的处理方法
3. **退出时**：发送 `status: idle` 消息到 iopub 通道

这模拟了 ipykernel 的标准行为，前端依赖 busy/idle 状态来判断内核是否在执行中。

## 子类必须实现的抽象方法

| 方法 | 说明 |
|------|------|
| `kernelInfoRequest()` | 返回内核信息（语言版本、协议版本等） |
| `executeRequest(content)` | 执行代码，返回执行结果 |
| `completeRequest(content)` | 代码补全 |
| `inspectRequest(content)` | 对象内省（?/??操作符） |
| `isCompleteRequest(content)` | 判断代码是否完整（用于续行提示） |
| `commInfoRequest(content)` | 查询已打开的comm通道 |
| `inputReply(content)` | 处理标准输入回复 |
| `commOpen(msg)` | 处理comm打开（Widget通信） |
| `commMsg(msg)` | 处理comm消息 |
| `commClose(msg)` | 处理comm关闭 |

## 消息发送辅助方法

BaseKernel 提供了一系列 `protected` 方法用于向客户端发送标准消息：

| 方法 | 通道 | 消息类型 | 用途 |
|------|------|----------|------|
| `stream(content)` | iopub | `stream` | 输出stdout/stderr文本 |
| `displayData(content)` | iopub | `display_data` | 显示富媒体输出（图表、HTML等） |
| `publishExecuteResult(content)` | iopub | `execute_result` | 代码执行结果（Out[N]） |
| `publishExecuteError(content)` | iopub | `error` | 执行错误（traceback） |
| `updateDisplayData(content)` | iopub | `update_display_data` | 更新已显示的输出 |
| `clearOutput(content)` | iopub | `clear_output` | 清除单元格输出 |
| `inputRequest(content)` | stdin | `input_request` | 请求用户输入（input()） |
| `handleComm(type, ...)` | iopub | comm_* | Widget/自定义通信 |

所有这些方法都通过构造函数传入的 `_sendMessage` 回调发送消息，自动填充正确的session和parentHeader。

### execute_request 完整处理流程

```
execute_request消息到达
    ↓
_busy(msg) → status: busy
    ↓
_executeInput(msg) → execute_input广播（显示In[N]代码）
    ↓
executionCount++ (如果store_history)
    ↓
history追加
    ↓
executeRequest(content) → 子类实现的具体执行逻辑
    ↓
发送execute_reply到shell通道
    ↓
_idle(msg) → status: idle
```

## LiteKernelClient

`LiteKernelClient`（`client.ts`）是主线程侧的内核管理客户端，实现了 JupyterLab 的 `Kernel.IKernelAPIClient` 接口。

### 核心职责

1. **内核生命周期管理**：`startNew()` 创建和启动新内核
2. **WebSocket 桥接**：使用 mock-socket 在主线程和Worker之间建立模拟WebSocket连接
3. **消息互斥**：使用 `async-mutex` 保证消息串行处理
4. **中断支持**：通过 `mutex.cancel()` 实现内核中断

### startNew 流程

```typescript
async startNew(options: LiteKernelClient.IKernelOptions): Promise<Kernel.IModel>
```

1. 根据 kernel name 从 `kernelSpecs.factories` 获取内核工厂
2. 创建 mutex 用于消息互斥
3. 创建 WebSocketServer（mock-socket），监听连接
4. 内核工厂创建 Worker 内核实例
5. hook 函数处理新WebSocket客户端连接：
   - 注册socket到 `_clients` map
   - 设置mutex到 `_mutexMap`
   - 监听 `message` 事件：反序列化消息 → mutex.runExclusive → kernel.handleMessage
6. 返回内核模型

### 消息互斥与中断

Jupyter 内核消息必须串行处理（一次只执行一个 cell）。LiteKernelClient 使用 `async-mutex` 的 Mutex 来保证这一点：

```typescript
// 消息处理时获取互斥锁
await mutex.runExclusive(async () => {
  await kernel.ready;
  await kernel.handleMessage(msg);
});
```

中断（interrupt）机制：
1. 调用 `mutex.cancel()` 取消等待锁的请求
2. 等待锁释放（`mutex.waitForUnlock()`）
3. 给所有客户端发送 `error` 消息（ename: `Kernel Interrupt`）
4. 发送 `execute_reply`（status: error, metadata.cause: 'interrupt'）
5. 发送 `status: idle`

这确保了中断后内核能正确回到idle状态，前端可以继续执行新的cell。

## 内核规格（KernelSpecs）

`KernelSpecs` 管理可用内核的规格信息和工厂函数：
- `factories: Map<string, IKernelFactory>` — 内核名称到工厂的映射
- 通过 `LiteKernelSpecClient` 与 JupyterLab 的 KernelSpecManager 对接
- `FALLBACK_KERNEL` 常量指定默认内核

## 相关概念

- [整体架构](/concepts/01-architecture-overview.md)
- [内容管理与文件系统](/concepts/03-contents-and-filesystem.md)
- [Service Worker桥接](/concepts/04-service-worker-bridge.md)
- [浏览器存储](/concepts/05-browser-storage.md)
- [内核系统信源](/references/kernel-source.md)
