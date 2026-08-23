---
type: concept
title: "12 - 异步支持"
description: IPython 原生 async/await 支持——顶层 await 检测、asyncio/trio/curio 异步运行器、_pseudo_sync_runner 降级、%autoawait 魔法
tags: [async, await, asyncio, trio, curio, event-loop, autoawait]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-async-helpers
    title: IPython/core/async_helpers.py
---

## 异步支持概述

IPython 7.0+ 原生支持 Python 的 `async`/`await` 语法，允许在交互式会话中直接使用顶层 `await`，无需将代码包装在 async 函数中 [F-480]。这是 IPython 相比标准 Python REPL 的重要优势之一。

```python
# 在 IPython 中可以直接使用顶层 await
In [1]: import aiohttp

In [2]: async with aiohttp.ClientSession() as session:
   ...:     async with session.get('https://api.example.com/data') as resp:
   ...:         data = await resp.json()
   ...:

In [3]: await asyncio.sleep(1, result="done")
Out[3]: 'done'
```

标准 Python REPL 不支持顶层 `await`（Python 3.8+ 的 `python -m asyncio` 提供了有限支持）。

## should_run_async 异步检测

IPython 在执行代码前通过 `should_run_async()` 判断代码是否需要异步执行 [F-218][F-480]：

```python
def _should_be_async(cell: str) -> bool:
    """检测代码是否包含顶层 await，需要异步执行 [F-480]"""
    try:
        # 使用 PyCF_ALLOW_TOP_LEVEL_AWAIT 标志编译
        code = compile(
            cell, "<>", "exec",
            flags=getattr(ast, "PyCF_ALLOW_TOP_LEVEL_AWAIT", 0x0)
        )
        # 检查 code.co_flags 是否包含 CO_COROUTINE 标志
        return inspect.CO_COROUTINE & code.co_flags == inspect.CO_COROUTINE
    except (SyntaxError, ValueError, MemoryError):
        return False
```

检测逻辑：
1. 使用 `PyCF_ALLOW_TOP_LEVEL_AWAIT` 编译标志编译代码
2. 检查编译后的 code object 的 `co_flags` 是否设置了 `CO_COROUTINE` 位
3. 如果代码包含顶层 `await`、`async for` 或 `async with`，编译器会标记 CO_COROUTINE
4. 编译失败（语法错误等）返回 False，走同步路径由编译器报告错误

特殊处理：
- 顶层 `return` 和 `yield` 会被特殊处理以保持 Python 语义（抛出 SyntaxError）
- 语法错误的代码不进入异步路径

## 异步代码执行流程

当 `should_run_async()` 返回 True 时，IPython 将整个 cell 包装在一个 async 函数中执行：

```
原始异步代码:
  await fetch_data()
  result = await process(result)
  │
  ▼ IPython AST 改写
async def __async_exec_cell():
    await fetch_data()
    result = await process(result)
  │
  ▼ 通过异步运行器执行
runner(__async_exec_cell())
```

执行路径选择：
- `run_cell()` 检测到异步 → 委托给 `run_cell_async()` [F-216][F-217]
- `run_cell_async()` 将代码包装为 async def，通过配置的 runner 执行
- 运行结果通过正常的 DisplayHook 显示

## 异步运行器

IPython 支持三种异步运行器，以及一个伪同步降级运行器 [F-481][F-482]：

### asyncio 运行器（默认）

```python
class _AsyncIORunner:
    """asyncio 事件循环运行器 [F-483]"""
    def __call__(self, coro):
        return get_asyncio_loop().run_until_complete(coro)
    
    def __str__(self):
        return "asyncio"

_asyncio_runner = _AsyncIORunner()
```

asyncio 运行器是默认运行器 [F-481]，它管理一个全局的 asyncio 事件循环：

```python
def get_asyncio_loop():
    """获取或创建 IPython 的 asyncio 事件循环 [F-483]"""
    import asyncio
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        pass
    
    global _asyncio_event_loop
    if _asyncio_event_loop is None or _asyncio_event_loop.is_closed():
        _asyncio_event_loop = asyncio.new_event_loop()
    return _asyncio_event_loop
```

关键特性：
- 维护 IPython 自己的事件循环（不是线程局部的）
- 如果已在运行的循环中（如 ipykernel 中），使用当前运行的循环
- 不使用已弃用的 `asyncio.get_event_loop()`

### Trio 运行器

```python
def _trio_runner(async_fn):
    """Trio 异步运行器 [F-481]"""
    import trio
    
    async def loc(coro):
        """包装器保护 trio 内部状态"""
        return await coro
    
    return trio.run(loc, async_fn)
```

Trio 运行器通过 `trio.run()` 执行协程。使用 Trio 需要安装 trio 包并通过 `%autoawait trio` 切换。

### Curio 运行器

```python
def _curio_runner(coroutine):
    """Curio 异步运行器 [F-481]"""
    import curio
    return curio.run(coroutine)
```

Curio 运行器通过 `curio.run()` 执行协程。使用 Curio 需要安装 curio 包。

### _pseudo_sync_runner 伪同步运行器

```python
def _pseudo_sync_runner(coro):
    """不真正运行事件循环的降级运行器 [F-482]
    
    仅推进协程一步，如果协程在第一步就完成（StopIteration）则返回结果，
    否则抛出 RuntimeError。
    """
    try:
        coro.send(None)
    except StopIteration as exc:
        return exc.value
    else:
        raise RuntimeError(
            f"{coro.__name__!r} needs a real async loop"
        )
```

伪同步运行器用于没有真正事件循环可用的环境，只能执行不真正 await 的协程（如返回已完成的 Future）。当真正的异步操作需要 await 时，会抛出 RuntimeError 提示需要真实的事件循环。

### _AsyncIOProxy 异步代理

```python
class _AsyncIOProxy:
    """将同步对象的协程方法包装为线程安全调用 [F-483]
    
    通过 asyncio.run_coroutine_threadsafe 将协程调度到事件循环线程
    """
    def __init__(self, obj, event_loop):
        self._obj = obj
        self._event_loop = event_loop
    
    def __getattr__(self, key):
        attr = getattr(self._obj, key)
        if inspect.iscoroutinefunction(attr):
            @wraps(attr)
            def _wrapped(*args, **kwargs):
                concurrent_future = asyncio.run_coroutine_threadsafe(
                    attr(*args, **kwargs), self._event_loop
                )
                return asyncio.wrap_future(concurrent_future)
            return _wrapped
        else:
            return attr
```

_AsyncIOProxy 用于在线程安全地调用异步方法，主要在 Jupyter 内核中使用，允许其他线程向事件循环线程提交协程。

## %autoawait 魔法

`%autoawait` 魔法控制异步行为和运行器切换：

```python
# 查看当前 autoawait 状态
%autoawait
# → %autoawait is on, using asyncio

# 切换到 Trio 运行器
%autoawait trio

# 切换到 Curio 运行器
%autoawait curio

# 切回 asyncio
%autoawait asyncio

# 关闭异步支持
%autoawait off

# 开启异步支持
%autoawait on
```

## 运行器选择与 trio_runner trait

Shell 实例的 `trio_runner` 属性用于 Trio 事件循环的前台集成 [F-234]。与 `_trio_runner`（每个 cell 调用 `trio.run()`）不同，`shell.trio_runner` 允许在单个 Trio 事件循环中运行所有 cell（由 ipykernel 设置）。

```python
# 通过配置设置运行器
# ipython_config.py
c.InteractiveShell.loop_runner = "asyncio"  # 默认
# c.InteractiveShell.loop_runner = "trio"
# c.InteractiveShell.loop_runner = "curio"
```

## 异步魔法支持

魔法命令本身也可以是异步的。当魔法函数是 coroutine function 时，IPython 会自动 await 它：

```python
@magics_class
class AsyncMagics(Magics):
    
    @line_magic
    async def fetch(self, line):
        """异步魔法：获取 URL 内容"""
        import aiohttp
        url = line.strip()
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()
                print(f"Fetched {len(data)} bytes from {url}")
                return data
```

内置的 `AsyncMagics` 类（在 `IPython.core.magics.basic` 中）提供了 `%autoawait` 魔法本身 [F-340]。

## 顶层 await 的限制

虽然 IPython 支持顶层 await，但有一些限制：

1. **不是真正的顶层**：IPython 将代码包装在 `async def` 中执行，因此 `return` 和 `yield` 在某些上下文中行为不同
2. **每次 cell 独立包装**：每个 cell 的 await 是独立的，跨 cell 的异步上下文（如 `async with` 会话）需要在同一个 cell 中使用
3. **同步/异步混合**：同步代码和异步代码在同一个 cell 中时，IPython 会检测 await 关键字决定走哪条路径
4. **运行器限制**：不同运行器的行为可能有细微差异（如 Trio 的 nurseries 语义）

```python
# 这个在同一个 cell 中可以工作：
In [1]: async with aiohttp.ClientSession() as session:
   ...:     resp = await session.get('https://example.com')
   ...:     data = await resp.text()

# 但跨 cell 的 async with 不行（每个 cell 独立执行）：
In [2]: session = aiohttp.ClientSession()  # 没有 async with
In [3]: resp = await session.get(...)      # 可能工作但不优雅
```

## 实际使用示例

```python
# 1. 基本 await
In [1]: import asyncio
In [2]: await asyncio.sleep(0.5, result="hello")
Out[2]: 'hello'

# 2. 异步 HTTP 请求
In [3]: import aiohttp
In [4]: async with aiohttp.ClientSession() as s:
   ...:     r = await s.get('https://httpbin.org/json')
   ...:     j = await r.json()
   ...:     print(j['slideshow']['title'])

# 3. 并发执行
In [5]: async def fetch(url):
   ...:     async with aiohttp.ClientSession() as s:
   ...:         r = await s.get(url)
   ...:         return await r.text()
   ...:
In [6]: results = await asyncio.gather(
   ...:     fetch('https://example.com'),
   ...:     fetch('https://example.org'),
   ...: )

# 4. 切换到 Trio
In [7]: %autoawait trio
In [8]: import trio
In [9]: async def child(msg):
   ...:     print(f"start {msg}")
   ...:     await trio.sleep(0.1)
   ...:     print(f"end {msg}")
In [10]: async with trio.open_nursery() as nursery:
   ...:     nursery.start_soon(child, "a")
   ...:     nursery.start_soon(child, "b")
```

## 在 ipykernel 中的异步

Jupyter 内核（ipykernel）环境中的异步行为略有不同：
- ipykernel 已经运行在一个 asyncio 事件循环中
- `get_asyncio_loop()` 返回当前运行的循环，而非创建新循环
- `trio_runner` trait 可以设置为在 Trio 循环中运行所有 cell
- Widget 和 comm 消息在事件循环中处理，与用户代码并发

## 相关概念

- [代码执行管线](/concepts/05-execution-pipeline.md)
- [Shell 生命周期](/concepts/03-shell-lifecycle.md)
- [魔法命令系统](/concepts/04-magic-system.md)
