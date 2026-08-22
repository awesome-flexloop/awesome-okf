---
type: Reference
title: JupyterLite 内核系统源码信源
description: BaseKernel抽象类、LiteKernelClient内核客户端、KernelSpecs的源码API登记
tags: [kernel, websocket, worker, messaging, ipykernel]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:02:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-base
    resource: /references/kernel-source.md
    title: packages/services/src/kernel/base.ts
  - id: kernel-client
    resource: /references/kernel-source.md
    title: packages/services/src/kernel/client.ts
---

## 源码位置

- `packages/services/src/kernel/base.ts` — BaseKernel 抽象类，约630行
- `packages/services/src/kernel/client.ts` — LiteKernelClient 内核客户端
- `packages/services/src/kernel/kernelspecs.ts` — 内核规格管理
- `packages/services/src/kernel/kernelspecclient.ts` — 内核规格客户端
- `packages/services/src/kernel/tokens.ts` — 接口令牌与类型定义

## 导出 API

### BaseKernel（抽象类，base.ts）

| API | 签名 | 行号 |
|-----|------|------|
| `BaseKernel` | `abstract class BaseKernel implements IKernel` | L11 |
| `constructor` | `(options: IKernel.IOptions)` | L17 |
| `ready` | `get: Promise<void>` | L28 |
| `isDisposed` | `get: boolean` | L35 |
| `disposed` | `get: ISignal<this, void>` | L42 |
| `id` | `get: string` | L49 |
| `name` | `get: string` | L56 |
| `location` | `get: string` | L63 |
| `executionCount` | `get: number` | L70 |
| `parentHeader` | `get: KernelMessage.IHeader \| undefined` | L77 |
| `parent` | `get: KernelMessage.IMessage \| undefined` | L84 |
| `dispose()` | `() => void` | L91 |
| `handleMessage(msg)` | `(msg: KernelMessage.IMessage) => Promise<void>` | L104 |
| `kernelInfoRequest()` | `abstract () => Promise<IInfoReplyMsg['content']>` | L153 |
| `executeRequest(content)` | `abstract (content) => Promise<IExecuteReplyMsg['content']>` | L160 |
| `completeRequest(content)` | `abstract (content) => Promise<ICompleteReplyMsg['content']>` | L169 |
| `inspectRequest(content)` | `abstract (content) => Promise<IInspectReplyMsg['content']>` | L180 |
| `isCompleteRequest(content)` | `abstract (content) => Promise<IIsCompleteReplyMsg['content']>` | L191 |
| `commInfoRequest(content)` | `abstract (content) => Promise<ICommInfoReplyMsg['content']>` | L202 |
| `inputReply(content)` | `abstract (content) => void` | L211 |
| `commOpen(msg)` | `abstract (msg: ICommOpenMsg) => Promise<void>` | L218 |
| `commMsg(msg)` | `abstract (msg: ICommMsgMsg) => Promise<void>` | L225 |
| `commClose(msg)` | `abstract (msg: ICommCloseMsg) => Promise<void>` | L232 |
| `stream(content, parentHeader?)` | `protected (content, parentHeader?) => void` | L240 |
| `displayData(content, parentHeader?)` | `protected (content, parentHeader?) => void` | L264 |
| `inputRequest(content, parentHeader?)` | `protected (content, parentHeader?) => void` | L291 |
| `publishExecuteResult(content, parentHeader?)` | `protected (content, parentHeader?) => void` | L315 |
| `publishExecuteError(content, parentHeader?)` | `protected (content, parentHeader?) => void` | L339 |
| `updateDisplayData(content, parentHeader?)` | `protected (content, parentHeader?) => void` | L363 |
| `clearOutput(content, parentHeader?)` | `protected (content, parentHeader?) => void` | L387 |
| `handleComm(type, content, metadata, buffers, parentHeader?)` | `protected (...) => void` | L410 |

### 消息处理路由（handleMessage L104-L146）

| 消息类型 (msg_type) | 处理方法 |
|---------------------|----------|
| `kernel_info_request` | `_kernelInfo()` → `kernelInfoRequest()` |
| `execute_request` | `_execute()` → `executeRequest()` |
| `input_reply` | `inputReply()` |
| `inspect_request` | `_inspect()` → `inspectRequest()` |
| `is_complete_request` | `_isCompleteRequest()` → `isCompleteRequest()` |
| `complete_request` | `_complete()` → `completeRequest()` |
| `history_request` | `_historyRequest()` |
| `comm_open` | `commOpen()` |
| `comm_msg` | `commMsg()` |
| `comm_close` | `commClose()` |

### LiteKernelClient（client.ts）

| API | 说明 |
|-----|------|
| `LiteKernelClient` | `class implements Kernel.IKernelAPIClient` |
| `constructor(options)` | 接收 `kernelSpecs` 和 `serverSettings` |
| `startNew(options)` | 启动新内核：查找kernel factory → 创建Worker内核 → 建立mock-socket桥接 |
| `serverSettings` | getter |
| `changed` | 内核map变更信号 |

### IKernel 接口（tokens.ts）

| 成员 | 类型 |
|------|------|
| `id` | `string` |
| `name` | `string` |
| `location` | `string` |
| `ready` | `Promise<void>` |
| `handleMessage(msg)` | `(msg: KernelMessage.IMessage) => Promise<void>` |
| `dispose()` | `() => void` |

## 核心常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `FALLBACK_KERNEL` | (tokens.ts中定义) | 默认回退内核名称 |
| `KERNEL_WEBSOCKET_PROTOCOL` | `v1.kernel.websocket.jupyter.org` | Jupyter 内核 WebSocket 协议 |

## 内核通信模型

```
主线程 (Main Thread)                     Web Worker (内核线程)
┌─────────────────────┐                 ┌─────────────────────┐
│  JupyterLab Frontend│                 │  Pyodide/Xeus Kernel│
│  LiteKernelClient   │ ←─WebSocket─→   │  BaseKernel impl    │
│  (mock-socket)      │                 │  (PyodideKernel)    │
└─────────────────────┘                 └─────────────────────┘
```

关键机制：
1. 使用 `mock-socket` 的 WebSocketServer/Client 模拟内核WebSocket连接
2. 消息通过 `serialize/deserialize` 进行二进制序列化
3. 使用 `async-mutex` 保证消息串行处理（同一时间只处理一条execute_request）
4. 支持中断（interrupt）：通过 `mutex.cancel()` 取消正在执行的请求
5. 多客户端支持：同一内核可被多个client连接
