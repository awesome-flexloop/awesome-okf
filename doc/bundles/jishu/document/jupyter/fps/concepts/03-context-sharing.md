---
type: Concept
title: 上下文与共享值
description: FPS的Context、SharedValue、Value三层抽象实现的异步安全资源共享机制，包括借用模型、并发控制和teardown回调。
tags: [context, shared-value, value, borrowing, async, resource-management]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:52:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:52:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-context-py
    resource: /references/context-source.md
    title: src/fps/_context.py
---

## 共享模型概述

FPS的资源共享模型包含三个核心类：

| 类 | 角色 | 类比 |
|----|------|------|
| `Context` | 值的容器，管理值的注册、查找和生命周期 | 作用域/命名空间 |
| `SharedValue[T]` | 可被多方借用的共享值包装器，追踪借用者 | 被共享的资源（Arc/Mutex） |
| `Value[T]` | 借用句柄（borrow handle），用完必须drop | 借用引用（&T） |

这种设计类似Rust的所有权借用系统：资源有"所有者"（发布者），可以被多个"借用者"（获取者）使用，所有借用者释放后资源才会被清理。

## Value：借用句柄

`Value` 是从 `SharedValue` 获取的借用包装器。它的核心API非常简洁：

```python
class Value(Generic[T]):
    def unwrap(self) -> T: ...      # 获取内部值
    def drop(self) -> None: ...    # 释放借用
```

### 上下文管理器自动drop

`Value` 实现了同步上下文管理器协议，推荐使用 `with` 语句自动释放：

```python
from fps import Context, get

async with Context() as ctx:
    ctx.put("hello", str)
    with await ctx.get(str) as value:
        print(value)  # "hello"
    # 退出with块时自动drop
```

如果对已drop的Value调用 `unwrap()`，抛出 `RuntimeError("Already dropped")`。

## SharedValue：共享值

`SharedValue` 管理一个可被多方借用的值，控制并发借用数和生命周期。

### 创建SharedValue

通常不直接创建SharedValue，而是通过 `Context.put()` 创建。也可以独立使用：

```python
from fps import SharedValue

async with SharedValue(resource, max_borrowers=2) as sv:
    # 使用sv...
    pass
```

构造参数：
- `value: T`：要共享的内部值
- `max_borrowers: float`：最大并发借用数，默认 `float("inf")`（无限）
- `teardown_callback`：关闭时调用的清理回调（同步或异步）
- `close_timeout: float | None`：关闭超时

### 借用值

```python
# 异步等待借用（带超时）
value = await shared_value.get(timeout=5.0)

# 非阻塞借用（不可借用时立即抛出RuntimeError）
value = shared_value.get_nowait()
```

当当前借用者数量达到 `max_borrowers` 时，`get()` 会等待直到有借用者drop。

### 等待释放

```python
# 等待所有借用者释放
await shared_value.freed(timeout=5.0)
```

发布者可以用 `freed()` 确认所有使用者已释放资源。

### 关闭SharedValue

```python
await shared_value.aclose(timeout=5.0)
```

`aclose()` 先等待所有借用者drop，然后调用 `teardown_callback`。超时则抛出 `TimeoutError`。使用 `async with SharedValue(...)` 会自动在退出时调用aclose。

## Context：值容器与作用域

`Context` 是值的注册和查找容器，支持嵌套形成作用域链。

### ContextVar 上下文传播

FPS使用Python的 `contextvars.ContextVar` 跟踪当前活动Context。模块级函数 `current_context()`、`put()`、`get()`、`get_nowait()` 都操作当前Context。

```python
from fps import Context, put, get, get_nowait, current_context

async with Context() as ctx:
    # 在当前Context中发布值
    put(42, int)

    # 从当前Context获取值（支持嵌套查找）
    value = await get(int)
    print(value)  # 42

    # 非阻塞获取
    with get_nowait(int) as v:
        print(v)  # 42
```

### 嵌套Context

Context可以嵌套形成父子链。子Context可以访问父Context中的值，但父Context不能访问子Context的值：

```python
async with Context() as parent:
    parent.put("from_parent", str)

    async with Context() as child:
        # 子Context可以获取父Context的值
        with await child.get(str) as v:
            print(v)  # "from_parent"

        child.put("from_child", int)

    # 父Context不能获取子Context的值
    with pytest.raises(RuntimeError):
        parent.get_nowait(int)
```

`Context.get()` 沿 `_parent` 链向上并行查找，使用 `create_task_group` 同时查询自身和所有祖先Context，第一个返回的值获胜。

### put：发布值

```python
def put(
    self,
    value: T,
    types: Iterable | Any | None = None,
    max_borrowers: float = float("inf"),
    teardown_callback: Callable | None = None,
    shared_value: SharedValue[T] | None = None,
) -> SharedValue[T]
```

- `types` 参数控制值注册为什么类型。默认 `[type(value)]`
- 可以传入单个类型或类型列表：`put(app, [FastAPI, ASGIApp])`
- 同一类型在同一Context中只能注册一次，重复注册抛出 `RuntimeError: Value type "..." already exists`
- 传入 `shared_value` 参数可以在多个Context间共享同一个底层SharedValue（Module.put使用此机制实现值冒泡）

### add_teardown_callback

Context本身也支持teardown回调，在Context关闭时逆序（LIFO）执行：

```python
async with Context() as ctx:
    ctx.add_teardown_callback(lambda: print("second"))
    ctx.add_teardown_callback(lambda: print("first"))

# Context关闭时输出:
# first
# second
```

### Context关闭流程

`Context.aclose()` 的执行顺序：
1. 在超时限制内并行关闭所有SharedValue（等待借用者释放 → 执行teardown_callback）
2. 逆序执行Context级别的teardown_callbacks
3. 标记 `_closed = True`

关闭后对Context调用 `put()` 或 `get()` 会抛出 `RuntimeError("Context is closed")`。

### teardown_callback的异常参数

teardown_callback可以接收0或1个参数。如果接收1个参数，框架会传入导致关闭的异常对象（正常关闭为None）：

```python
async def cleanup(exc_value):
    if exc_value is not None:
        print(f"Cleaning up after error: {exc_value}")
    resource.close()

ctx.put(resource, teardown_callback=cleanup)
```

框架通过 `inspect.signature` 检测callback的参数数量（结果被 `@lru_cache(maxsize=1024)` 缓存）。

## 独立使用Context

Context不依赖Module系统，可以独立使用来管理资源生命周期：

```python
from anyio import run
from fps import Context
from io import TextIOWrapper

async def main():
    async with Context() as context:
        file = open("log.txt", "w")

        def teardown_callback():
            file.close()

        context.put(file, teardown_callback=teardown_callback)
        with await context.get(TextIOWrapper) as f:
            f.write("Hello, World!\n")

run(main)
```

执行流程：
1. 打开文件，放入context并注册关闭回调
2. 获取文件对象（类型为 `TextIOWrapper`），写入内容
3. with语句退出时自动drop借用
4. Context退出时等待所有借用释放，然后执行teardown_callback关闭文件

## max_borrowers并发控制

设置 `max_borrowers=1` 可以实现独占访问：

```python
import anyio

async def exclusive_access():
    async with Context() as ctx:
        ctx.put("resource", str, max_borrowers=1)

        async with anyio.create_task_group() as tg:
            # 第一个获取者成功
            v1 = await ctx.get(str)

            # 第二个获取者必须等待第一个drop
            with pytest.raises(TimeoutError):
                v2 = await ctx.get(str, timeout=0.1)

            v1.drop()
            # 现在第二个可以获取了
            v2 = await ctx.get(str)
            v2.drop()
```

## 相关概念

- [模块系统](02-module-system.md)
- [生命周期阶段](04-lifecycle-phases.md)
- [信号系统](06-signal-system.md)
- [独立使用Context](../examples/05-standalone-context.md)
