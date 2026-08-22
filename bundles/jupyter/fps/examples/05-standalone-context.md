---
type: Example
title: 独立使用Context
description: 不依赖Module系统，独立使用Context管理资源生命周期，实现安全的文件句柄共享和自动清理。
tags: [example, context, resource-management, teardown, standalone]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:55:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-guide
    resource: /references/context-source.md
    title: docs/guide.md Contexts
  - id: fps-context-py
    resource: /references/context-source.md
    title: src/fps/_context.py
---

## 概述

Context不仅在Module系统内部使用，也可以独立使用来管理异步资源的生命周期。本示例演示如何用Context安全地共享文件对象，确保资源在所有使用者完成后才被清理。

## 完整代码

```python
from io import TextIOWrapper
from anyio import run
from fps import Context

async def main():
    async with Context() as context:
        file = open("log.txt", "w")
        print("File opened")

        def teardown_callback():
            file.close()
            print("File closed")

        shared_file = context.put(file, teardown_callback=teardown_callback)
        print("File object published")

        with await context.get(TextIOWrapper) as acquired_file:
            print("File object acquired")
            assert acquired_file is file
            print("Writing to file")
            acquired_file.write("Hello, World!\n")
        print("File object dropped")

        await shared_file.freed()
        print("Shared file freed")

run(main)
```

## 运行输出

```
File opened
File object published
File object acquired
Writing to file
File object dropped
File closed
Shared file freed
```

## 代码解析

### 创建Context

```python
async with Context() as context:
```

Context是异步上下文管理器。进入时建立当前Context（通过ContextVar），退出时自动关闭所有SharedValue并执行teardown回调。

### 注册资源与teardown回调

```python
file = open("log.txt", "w")

def teardown_callback():
    file.close()

shared_file = context.put(file, teardown_callback=teardown_callback)
```

`context.put()` 将资源放入Context，返回 `SharedValue` 句柄。`teardown_callback` 在Context关闭且所有借用者drop后被调用，负责清理资源。

### 获取并使用资源

```python
with await context.get(TextIOWrapper) as acquired_file:
    acquired_file.write("Hello, World!\n")
```

- `await context.get(TextIOWrapper)` 异步获取类型为 `TextIOWrapper` 的值，返回 `Value` 包装器
- `with` 语句对Value使用同步上下文管理器：进入时 `unwrap()` 获取实际对象，退出时自动 `drop()`
- 这确保即使发生异常，借用也会被正确释放

### 等待资源释放

```python
await shared_file.freed()
```

发布者可以通过 `freed()` 确认所有借用者已释放资源。这在需要确保资源安全关闭的场景中很有用。

### Context关闭流程

当退出 `async with Context()` 块时：
1. 等待所有SharedValue的借用者释放（`freed()`）
2. 执行每个SharedValue的teardown_callback
3. 逆序执行Context级别的teardown_callback
4. 标记Context为closed

## 使用模块级函数

FPS提供了模块级的 `put()`/`get()`/`get_nowait()`/`current_context()` 函数，操作当前活动Context：

```python
from fps import Context, put, get, get_nowait

async with Context():
    put(42, int)
    put("hello", str)

    # 在嵌套Context中也能访问
    async with Context():
        value = await get(int)
        print(value)  # 42

        with get_nowait(str) as s:
            print(s)  # "hello"
```

## 嵌套Context

Context可以嵌套形成作用域链，子Context可以访问父Context的值：

```python
async with Context() as outer:
    outer.put("outer_value", str)

    async with Context() as inner:
        inner.put("inner_value", int)

        # 子Context可以获取父Context的值
        with await inner.get(str) as v:
            print(v)  # "outer_value"

        with await inner.get(int) as v:
            print(v)  # 注意：inner.put(int)还没执行到这里，会等待
```

## max_borrowers控制并发

限制资源的并发借用数：

```python
async with Context() as ctx:
    ctx.put("resource", str, max_borrowers=1)  # 独占访问

    async with anyio.create_task_group() as tg:
        v1 = await ctx.get(str)  # 第一个借用成功

        # 第二个借用必须等待v1.drop()
        with pytest.raises(TimeoutError):
            await ctx.get(str, timeout=0.1)

        v1.drop()
        v2 = await ctx.get(str)  # 现在可以借用了
        v2.drop()
```

## 异常处理

teardown_callback可以接收异常参数，了解Context是否因异常关闭：

```python
async def cleanup(exc_value):
    if exc_value is not None:
        print(f"Cleaning up after error: {exc_value}")
    resource.close()

ctx.put(resource, teardown_callback=cleanup)
```

框架自动检测callback是否接受参数，决定是否传入异常对象。

## 关键要点

- Context是独立的资源管理抽象，不依赖Module系统
- 使用 `async with Context()` 确保资源被正确清理
- 推荐使用 `with await context.get(Type) as obj:` 语法自动drop
- teardown_callback在所有借用者释放后执行，支持同步和异步
- 嵌套Context形成作用域链，子可访问父，父不可访问子
- `max_borrowers` 可实现独占访问控制

## 相关概念

- [上下文与共享值](/concepts/03-context-sharing.md)
- [模块系统](/concepts/02-module-system.md)
- [信号使用](06-signals-usage.md)
