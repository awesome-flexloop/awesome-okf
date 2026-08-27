---
type: Concept
title: Python 兼容性层
description: IPython InteractiveShell 在 Pyodide WASM 环境中的适配策略——Mock、Patch 和子类化三层方案
tags: [python, compatibility, ipython, wasm, mock, patch, interpreter]
prerequisites: ["02-architecture-overview"]
objectives: ["理解三层兼容策略（Mock/Patch/子类化）", "掌握哪些 Python 功能在浏览器中不可用", "理解 Interpreter 和 Display 桥接类的作用"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: mocks
    resource: /references/kernel-py-source.md
    title: mocks.py
  - id: patches
    resource: /references/kernel-py-source.md
    title: patches.py
  - id: interpreter
    resource: /references/kernel-py-source.md
    title: interpreter.py
  - id: display
    resource: /references/kernel-py-source.md
    title: display.py
---

# Python 兼容性层

## 为什么需要兼容性层

IPython 是为完整 POSIX 环境设计的交互式 Python 解释器，它依赖：
- 终端 I/O（termios、fcntl、tty 控制）
- 进程管理（signal、resource 限制）
- 系统级事件循环（tornado 异步）
- 本地文件系统历史记录
- 真实的 GUI 事件循环

在 Pyodide WASM 环境中，这些系统调用要么不存在，要么行为完全不同。pyodide-kernel 没有重写 IPython，而是采用三层适配策略，让 IPython "以为"自己在正常 POSIX 环境中运行。

## 三层适配策略

```
┌────────────────────────────────────────────┐
│  Layer 3: 子类化（Subclassing）            │
│  - Interpreter(InteractiveShell)          │
│  - CustomHistoryManager(HistoryAccessor)  │
│  - LiteDisplayPublisher(DisplayPublisher) │
│  - LiteDisplayHook(DisplayHook)           │
│  - LiteStream(TextIOBase)                 │
│  - Comm 桥接                               │
├────────────────────────────────────────────┤
│  Layer 2: 运行时补丁（Patches）            │
│  - matplotlib backend → 'module://matplotlib_inline.backend_inline'│
│  - 环境变量设置                             │
├────────────────────────────────────────────┤
│  Layer 1: 模块 Mock（Mocks）              │
│  - termios → 空模块 + TCSAFLUSH           │
│  - fcntl → 空模块                         │
│  - resource → 空模块                      │
│  - tornado/tornado.gen → 空实现           │
│  - pexpect → 空模块                       │
└────────────────────────────────────────────┘
```

执行顺序很重要：**Mocks 最先执行**（在任何其他 import 之前注入 sys.modules），然后 Patches（需要 import 模块后修改），最后子类化（创建实际的解释器实例）。

## Layer 1：模块 Mock

`apply_mocks()` 函数在 `__init__.py` 最开始执行，在任何 IPython 相关 import 之前将模拟模块注入 `sys.modules`（F-104）。

### 为什么必须在最早时机 Mock？

Python 的 import 系统会缓存模块。如果某个模块在 mock 之前已经被 import，后续对 `sys.modules` 的修改不会影响已导入的引用。因此 mock 必须在所有业务代码之前执行。

```python
# __init__.py 开头
from . import mocks
mocks.apply_mocks()  # 必须最先执行！
# 之后才能 import IPython 等
```

### Mock 的模块清单

| 模块 | Mock 内容 | 为什么需要 |
|------|----------|-----------|
| `termios` | 空模块 + `TCSAFLUSH = 2` | IPython 使用 termios 控制终端属性 |
| `fcntl` | 空模块 | Unix 文件控制（非阻塞 I/O、文件锁等） |
| `resource` | 空模块 | Unix 进程资源限制（getrlimit/setrlimit） |
| `tornado` | `coroutine` 装饰器（返回原函数）、`sleep`（no-op）、`is_coroutine_function`（返回 False） | IPython/pyzmq 的事件循环依赖 tornado |
| `tornado.gen` | 同 tornado | tornado 子模块 |
| `pexpect` | 空模块 | 终端交互 expect 库 |

### tornado Mock 的特殊性

tornado 不能简单 mock 为空模块，因为 IPython 的代码路径中会实际调用 `tornado.gen.coroutine` 和 `tornado.gen.sleep`。这些需要提供不报错的实现：

```python
# mocks.py 中的 tornado mock
class _TornadoModule:
    @staticmethod
    def coroutine(func):
        """coroutine 装饰器直接返回原函数（不做异步包装）"""
        return func

    @staticmethod
    async def sleep(seconds):
        """sleep 是真正的 no-op（不等待）"""
        pass

    @staticmethod
    def is_coroutine_function(func):
        """永远返回 False——WASM 中没有 tornado 协程"""
        return False
```

这样，当 IPython 内部尝试 `@tornado.gen.coroutine` 装饰函数时，函数保持原样，不会报错；调用 `yield tornado.gen.sleep(0)` 时相当于 `await asyncio.sleep(0)`（让出事件循环但不实际等待）。

## Layer 2：运行时 Patches

`apply_patches()` 在 mocks 之后执行，做需要 import 模块后才能应用的修改（F-105）。

### Matplotlib Backend 补丁

```python
# patches.py
def apply_patches():
    import matplotlib
    matplotlib.use('module://matplotlib_inline.backend_inline')
```

这个补丁确保 matplotlib 使用 inline backend，图形直接作为 display_data 消息发送到前端，而不是尝试打开 GUI 窗口。

在浏览器中没有 GUI 窗口系统，默认 backend 会失败。inline backend 将图形渲染为 PNG/SVG 数据，通过 Jupyter 的 display 机制发送到前端展示。

## Layer 3：子类化

这是最核心的适配层——通过继承 IPython 的基类并重写有问题的方法，实现 WASM 环境下的正确行为。

### Interpreter（InteractiveShell 子类）

`Interpreter` 类继承自 `IPython.core.interactiveshell.InteractiveShell`（F-088）：

```python
class Interpreter(InteractiveShell):
    kernel: PyodideKernel
    Completer.use_jedi = True
    _last_traceback: dict | None = None
    _input: Callable | None
    _getpass: Callable | None
```

关键重写：

**init_history()**（F-092）：
```python
def init_history(self):
    """使用 CustomHistoryManager，不持久化历史"""
    self.history_manager = CustomHistoryManager(shell=self, parent=self)
    self.configurables.append(self.history_manager)
```

IPython 默认使用 `SqliteHistory`，需要本地文件系统存储 SQLite 数据库。`CustomHistoryManager` 提供空实现，历史只在当前会话内存中存在，刷新后丢失。

**enable_gui()**：
```python
def enable_gui(self, gui=None):
    """空实现——WASM 中不支持 GUI 事件循环"""
    pass
```

IPython 支持 `%gui` 魔法命令启用 GUI 事件循环（qt/tk/wx 等），在浏览器中无意义。

**_showtraceback()**：
```python
def _showtraceback(self, etype, evalue, stb):
    """捕获 traceback 信息而不是打印到终端"""
    self._last_traceback = {
        "ename": etype.__name__,
        "evalue": str(evalue),
        "traceback": stb,
    }
```

IPython 默认将 traceback 打印到 stderr。重写后将 traceback 存储在 `_last_traceback` 属性中，供 kernel 层获取并通过 `execute_error` 消息发送到前端。

**input/getpass 属性**（F-093/F-094）：
```python
@property
def input(self):
    return self._input

@input.setter
def input(self, value):
    import builtins
    self._input = builtins.input
    builtins.input = value

@property
def getpass(self):
    return self._getpass

@getpass.setter
def getpass(self, value):
    import getpass
    self._getpass = getpass.getpass
    getpass.getpass = value
```

这将 Python 的 `builtins.input()` 和 `getpass.getpass()` 替换为 Worker 端提供的回调函数，使 `input()` 调用能够通过消息机制请求前端用户输入。

### LitePythonShellApp

`LitePythonShellApp` 继承自 IPython 的 `IPythonConsoleApp` / `InteractiveShellApp`，是创建 Interpreter 实例的应用入口（F-089）：

```python
class LitePythonShellApp(InteractiveShellApp):
    def initialize(self, argv=None):
        """初始化 IPython 环境"""
        super().initialize(argv)
        self.kernel = PyodideKernel(interpreter=self.shell)
```

它的作用是创建并配置 Interpreter 实例，将 kernel 实例注入到 shell 中。

### LiteStream（输出桥接）

`LiteStream` 替换 `sys.stdout` 和 `sys.stderr`，将输出通过回调发送到 Worker 端（F-097）：

```python
class LiteStream:
    encoding = "utf-8"

    def __init__(self, name: str):
        self.name = name  # "stdout" 或 "stderr"
        self.publish_stream_callback: Callable | None = None

    def write(self, text: str) -> int:
        if self.publish_stream_callback:
            self.publish_stream_callback(self.name, text)
        return len(text)

    def flush(self):
        pass  # 无缓冲，write 即发送

    def isatty(self):
        return False  # 不是真正的终端
```

关键点：`publish_stream_callback` 在 Worker 初始化时（`initGlobals` 阶段）被设置为 Worker JS 端的回调函数，形成 Python→JS 的输出桥。

### LiteDisplayPublisher（富媒体显示桥接）

`LiteDisplayPublisher` 继承自 IPython 的 `DisplayPublisher`，负责处理 `display(obj)` 等富媒体输出（F-099）：

```python
class LiteDisplayPublisher(DisplayPublisher):
    display_data_callback: Callable | None = None
    update_display_data_callback: Callable | None = None
    clear_output_callback: Callable | None = None

    def publish(self, data, metadata=None, source=None, *, transient=None, update=False):
        if update and self.update_display_data_callback:
            self.update_display_data_callback(data, metadata, transient)
        elif self.display_data_callback:
            self.display_data_callback(data, metadata, transient)

    def clear_output(self, wait=False):
        if self.clear_output_callback:
            self.clear_output_callback(wait)
```

它拦截 IPython 的 display 机制，将 display_data、update_display_data、clear_output 消息通过回调发送到 JS 端。

### LiteDisplayHook（执行结果桥接）

`LiteDisplayHook` 继承自 `DisplayHook`，处理 cell 最后一个表达式的自动显示（即 `Out[n]` 结果）（F-100）：

```python
class LiteDisplayHook(DisplayHook):
    publish_execution_result: Callable | None = None

    def write_format_data(self, format_dict, md_dict=None):
        # 存储格式化结果
        ...

    def finish_displayhook(self):
        if self.publish_execution_result:
            self.publish_execution_result(self.execution_count, self.data, self.metadata)
```

当 cell 的最后一行是一个表达式（如 `1+1` 或 `df`）时，IPython 会调用 display hook 将结果作为 `execute_result` 消息发送。

### Comm 桥接

`Comm` 类实现了 Jupyter Comm 协议，用于 Widget 和前端双向通信（F-101）：

```python
class Comm:
    def __init__(self, target_name, data=None, metadata=None, ...):
        # 注册到 comm_manager
        ...

    def send(self, data=None, metadata=None, buffers=None):
        # 通过 comm_msg_callback 发送消息到 JS 端
        ...

    def close(self, data=None, metadata=None):
        # 发送 comm_close 消息
        ...

    def on_msg(self, callback):
        # 注册消息处理函数
        ...
```

Comm 的回调同样在 Worker 初始化时绑定到 JS 端函数。

## 不支持的 Python 功能

由于 WASM 环境的限制，以下 Python 标准库功能在 pyodide-kernel 中不可用或受限：

| 功能 | 原因 | 替代方案 |
|------|------|---------|
| 多进程（multiprocessing） | WASM 无进程模型 | 使用 asyncio 或 Web Worker |
| 线程（threading） | Pyodide 的线程支持有限 | asyncio |
| 网络 socket（socket） | 浏览器无原始 TCP/UDP | fetch() / XMLHttpRequest（通过 JS 桥） |
| 文件系统持久化 | MEMFS 内存文件系统 | Coincident 模式下 DriveFS 同步 |
| C 扩展动态加载 | 无法 dlopen | 必须预编译为 WASM |
| signal 信号处理 | 无操作系统信号 | N/A |
| subprocess 子进程 | 无进程模型 | N/A |
| locale 设置 | 浏览器环境限制 | 手动处理 |
| GUI 窗口（tkinter/qt） | 无 GUI 系统 | matplotlib inline backend |

## 执行代码的完整路径

当执行 Python 代码时，三层适配如何协作：

```python
# 用户在 Notebook 中执行：
import numpy as np
print("Hello")
display(HTML("<b>World</b>"))
1 + 1
```

1. **输入阶段**：代码通过 `execute_request` 消息到达 Worker，经 kernel.run() → interpreter.run_cell()
2. **代码转换**：LiteTransformerManager 转换 %pip 等特殊语法
3. **自动加载**：loadPackagesFromImports 自动加载 numpy（pyodide-lock 内置包）
4. **执行**：Interpreter（InteractiveShell 子类）执行代码
5. **输出重定向**：print("Hello") → sys.stdout.write() → LiteStream.write() → publish_stream_callback → Worker JS
6. **富媒体显示**：display(HTML(...)) → LiteDisplayPublisher.publish() → display_data_callback → Worker JS
7. **表达式结果**：1+1 → LiteDisplayHook.finish_displayhook() → publish_execution_result → Worker JS
8. **错误处理**：如果异常 → _showtraceback() 捕获 → execute_error 消息
9. **消息回传**：Worker JS → 主线程 _processWorkerMessage → 前端显示

## 下一步

- [消息桥接机制](07-message-bridge.md) — Python↔JS 回调绑定的详细机制
- [Worker 通信模式](03-worker-communication.md) — Comlink/Coincident 下回调的差异
- [架构总览](02-architecture-overview.md)

## 源码参考

- [浏览器端 Python Kernel 源码](../references/kernel-py-source.md)
