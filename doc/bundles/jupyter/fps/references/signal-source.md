---
type: Reference
title: fps._signal 源码信源
description: fps Signal信号系统源码登记，对应src/fps/_signal.py
tags: [core, signal, event, async]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:50:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-signal-py
    resource: /references/signal-source.md
    title: src/fps/_signal.py
---

## 源码位置

`src/fps/_signal.py` — fps异步信号系统，约53行。

## 导出API

| API | 签名 | 行号 |
|-----|------|------|
| `Signal` | `class Signal(Generic[T])` | L12 |
| `Signal.__init__` | `()` | L13 |
| `Signal.iterate()` | `() -> MemoryObjectReceiveStream[T]` | L17 |
| `Signal.connect()` | `(callback: Callable[[T], None]) -> None` | L22 |
| `Signal.disconnect()` | `(callback: Callable[[T], None]) -> None` | L25 |
| `Signal.emit()` | `(value: T) -> None`（async） | L28 |

## 核心机制

### 双模式监听

Signal支持两种监听方式：

1. **回调模式**：通过`connect(callback)`注册回调函数，`disconnect(callback)`取消注册
   - 回调可以是同步函数或协程函数（通过`iscoroutinefunction`检测）
   - 协程回调通过`tg.start_soon`并行执行，同步回调直接调用

2. **迭代器模式**：通过`iterate()`返回anyio `MemoryObjectReceiveStream`
   - 内部调用`create_memory_object_stream[T]()`创建内存流
   - send_stream存入`_send_streams`集合
   - 使用`async for value in stream`异步迭代信号值

### emit 并发模型

- `emit()`在`create_task_group()`中并行执行：
  - 所有已注册回调
  - 向所有send_stream发送值
- 发送时遇到`BrokenResourceError`（接收方已关闭）自动清理断开的stream
