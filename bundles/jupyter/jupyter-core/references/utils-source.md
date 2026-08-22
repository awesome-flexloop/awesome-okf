---
okf_version: "0.2"
type: reference
title: "工具函数源码（utils/）"
description: "jupyter_core/utils/__init__.py 中事件循环管理、目录创建、sync/async桥接、弃用警告等工具函数的完整API"
tags: [utils, event-loop, run-sync, ensure-dir, deprecation, async, threading, ensure-async]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: utils-init-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/utils/__init__.py"
    title: "jupyter_core/utils/__init__.py"
---

# 工具函数源码（utils/）

本信源登记 `jupyter_core/utils/__init__.py`（约221行）的所有公开函数与内部机制。utils 模块提供事件循环管理、目录创建、sync/async 桥接、弃用警告等基础工具。

## 公开函数

### ensure_dir_exists(path, mode=0o777) -> None

确保目录存在：

1. 调用 `Path(path).mkdir(parents=True, mode=mode)` 创建目录（含父目录）
2. 捕获 `OSError`，仅忽略 `errno.EEXIST`（目录已存在），其他异常向上传播
3. 创建后验证路径确实是目录（不是文件），否则抛出 `OSError`
4. 使用 `Path.mkdir` 而非 `os.makedirs`，默认权限由当前 umask 决定

> **注意**：JupyterApp 中 data_dir 和 runtime_dir 调用时显式传入 `mode=0o700`。

[F-200]

### deprecation(message, internal="jupyter_core/") -> None

发出弃用警告，自动计算正确的 stacklevel 使警告指向调用者（而非内部代码）：

1. `internal` 参数指定哪些文件名前缀视为"内部帧"（默认为 `"jupyter_core/"`）
2. 调用 `_external_stacklevel(internal)` 找到第一个外部调用帧的深度
3. 使用 `warnings.warn(message, DeprecationWarning, stacklevel=stacklevel+1)` 发出警告
4. `internal` 可以是字符串或字符串列表

[F-201]

### run_sync(coro) -> wrapped

**装饰器**，将 async 协程函数包装为同步函数：

1. **只接受协程函数**（`inspect.iscoroutinefunction(coro)` 必须为 True），不能直接传入协程实例
2. 返回 `wrapped(*args, **kwargs)` 函数
3. wrapped 内部逻辑：
   - 调用 `coro(*args, **kwargs)` 创建协程
   - 检测当前线程是否有运行中的事件循环（`asyncio.get_running_loop()`）
   - **无运行中循环**：调用 `ensure_event_loop()` 获取/创建循环，`loop.run_until_complete(inner)` 执行
   - **有运行中循环**：从 `_runner_map` 按线程名获取/创建 `_TaskRunner`，通过 `runner.run(inner)` 在后台线程执行
4. `wrapped.__doc__ = coro.__doc__` 保留文档字符串

典型用法：

```python
@run_sync
async def my_async_func():
    await asyncio.sleep(0.1)
    return 42

result = my_async_func()  # 在同步上下文中调用
```

[F-202]

### ensure_event_loop(prefer_selector_loop: bool = False) -> asyncio.AbstractEventLoop

获取/创建当前线程的事件循环：

1. 首先检查 `_loop` ContextVar 缓存的循环是否存在且未关闭，存在则直接返回
2. 尝试 `asyncio.get_running_loop()` 获取运行中的循环：
   - 成功则缓存到 `_loop` 并返回
3. 无运行中循环时创建新循环：
   - Windows 且 `prefer_selector_loop=True`：创建 `WindowsSelectorEventLoopPolicy().new_event_loop()`（Tornado 场景）
     - Python 3.14 上需过滤 SelectorEventLoopPolicy 的 DeprecationWarning
   - 其他情况：`asyncio.new_event_loop()`
   - `asyncio.set_event_loop(loop)` 设置为当前线程循环
4. 将新循环缓存到 `_loop` ContextVar 并返回

[F-203]

### ensure_async(obj) -> T (async)

`async def` 函数，将同步/异步对象统一为 awaitable：

1. 若 `obj` 是 awaitable（协程/Future等），await 它并返回结果
2. 若 await 时抛出 `"cannot reuse already awaited coroutine"` RuntimeError，说明 obj 已经是结果值，直接返回
3. 若 `obj` 不是 awaitable，直接返回（同步透传）

用途：编写既能接受同步又能接受异步参数的通用函数。

[F-204]

## 内部函数

### _get_frame(level) -> FrameType | None

获取指定栈深度的 frame 对象：
- 优先使用 `sys._getframe(level+1)`（更快，但非所有Python实现都支持）
- Fallback 到 `inspect.stack(context=0)[level+1].frame`

### _external_stacklevel(internal: list[str]) -> int

从调用栈中找到第一个不包含 `internal` 路径前缀的帧，返回其 stacklevel（从调用者视角）。用于 `deprecation()` 函数确保警告指向外部调用者而非内部代码。

[F-205]

## _TaskRunner 类（内部）

在后台线程中运行 asyncio 事件循环。使用 `_runner_map` 按线程名缓存实例（不是单例），通过 `atexit` 注册清理。

### 构造与生命周期

- `__init__()`：初始化 `__io_loop=None`、`__runner_thread=None`、`__lock`（threading.Lock），`atexit.register(self._close)` 注册退出清理
- `_close()`：停止事件循环（atexit 时调用）
- `_runner()`：在后台线程中运行 `loop.run_forever()`，finally 中关闭循环

### run(coro) -> Any

在后台线程中同步运行协程：
1. 加锁：若 `__io_loop` 为 None，创建新事件循环和后台守护线程并启动
2. `asyncio.run_coroutine_threadsafe(coro, loop)` 将协程提交到后台线程循环
3. `fut.result(None)` 阻塞等待结果（无超时）

[F-206]

## 模块级变量

| 变量 | 类型 | 说明 |
|------|------|------|
| `_runner_map` | `dict[str, _TaskRunner]` | 按线程名缓存的 TaskRunner 实例字典 |
| `_loop` | `ContextVar[asyncio.AbstractEventLoop | None]` | ContextVar 缓存当前线程的事件循环 |
| `T` | `TypeVar` | 泛型类型变量，用于 run_sync/ensure_async 的返回类型 |

[F-207]
