---
type: Reference
title: fps._context 源码信源
description: fps上下文系统Context/SharedValue/Value的源码登记，对应src/fps/_context.py
tags: [core, context, shared-value, async]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:50:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-context-py
    resource: /references/context-source.md
    title: src/fps/_context.py
---

## 源码位置

`src/fps/_context.py` — fps异步上下文与共享值系统，约537行。

## 导出API

| API | 签名 | 行号 |
|-----|------|------|
| `Value` | `class Value(Generic[T])` | L26 |
| `Value.__init__` | `(shared_value: SharedValue[T])` | L33 |
| `Value.unwrap()` | `() -> T` | L51 |
| `Value.drop()` | `() -> None` | L66 |
| `SharedValue` | `class SharedValue(Generic[T])` | L73 |
| `SharedValue.__init__` | `(value: T, max_borrowers: float=inf, teardown_callback=None, close_timeout=None)` | L82 |
| `SharedValue.get()` | `(timeout: float=inf) -> Value[T]`（async） | L124 |
| `SharedValue.get_nowait()` | `() -> Value[T]` | L145 |
| `SharedValue.freed()` | `(timeout: float=inf) -> None`（async） | L161 |
| `SharedValue.aclose()` | `(*, timeout=None, ...) -> None`（async） | L177 |
| `Context` | `class Context` | L213 |
| `Context.__init__` | `()` | L226 |
| `Context.put()` | `(value, types=None, max_borrowers=inf, teardown_callback=None, shared_value=None) -> SharedValue[T]` | L279 |
| `Context.get()` | `(value_type: type[T], timeout=inf) -> Value[T]`（async） | L322 |
| `Context.get_nowait()` | `(value_type: type[T]) -> Value[T]` | L356 |
| `Context.add_teardown_callback()` | `(callback) -> None` | L266 |
| `Context.aclose()` | `(*, timeout=None, ...) -> None`（async） | L400 |
| `current_context()` | `() -> Context` | L453 |
| `put()` | `(value, types=None, max_borrowers=inf, teardown_callback=None) -> SharedValue[T]`（模块级） | L464 |
| `get()` | `(value_type: type[T], timeout=inf) -> Value[T]`（async，模块级） | L489 |
| `get_nowait()` | `(value_type: type[T]) -> Value[T]`（模块级） | L512 |

## 核心机制

### Value借用句柄

- `Value`是`SharedValue`的借用包装器，实现同步上下文管理器协议
- `__enter__`返回`unwrap()`的结果，`__exit__`自动调用`drop()`
- `unwrap()`在value已被drop时抛出`RuntimeError("Already dropped")`

### SharedValue借用管理

- 内部维护`_borrowers: set[Value]`集合追踪活跃借用
- `_max_borrowers`控制最大并发借用数（默认无限）
- `_dropped: Event`用于在借用释放时通知等待者（每次drop后重建Event）
- `_closing: bool`防止重复close
- `get()`在fail_after超时中循环等待可用借用槽位
- `aclose()`先等待`freed()`，再执行`teardown_callback`，超时则抛出TimeoutError

### Context嵌套查找

- `_current_context: ContextVar[Context]` 使用contextvars管理当前上下文
- `__aenter__`自动建立父子关系，`__aexit__`解除关系
- `get()`沿`_parent`链向上查找，使用task_group并行竞争，先找到的获胜
- `put()`以`id(value_type)`为key注册，同类型重复注册抛出RuntimeError
- 支持将已有SharedValue传入（`shared_value`参数）实现跨context共享同一底层值

### teardown_callback调用约定

- `call(callback, exc_value)`自动检测callback参数数量（0或1个参数）
- 有参数时传入异常对象（正常退出传None）
- 同步callback直接调用，异步callback自动await
- Context的teardown_callback按LIFO（逆序）调用
