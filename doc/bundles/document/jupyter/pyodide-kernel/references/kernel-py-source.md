---
type: Reference
title: 浏览器端 Python Kernel 源码参考
description: py/pyodide-kernel 目录下浏览器内运行的 Python 内核代码，包括 PyodideKernel、Interpreter、LiteStream、Comm、Mocks、Patches
tags: [python, kernel, browser, wasm, ipython]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: kernel-py-init
    resource: /references/kernel-py-source.md
    title: "py/pyodide-kernel/pyodide_kernel/__init__.py"
  - id: kernel-py-kernel
    resource: /references/kernel-py-source.md
    title: "py/pyodide-kernel/pyodide_kernel/kernel.py"
  - id: kernel-py-interp
    resource: /references/kernel-py-source.md
    title: "py/pyodide-kernel/pyodide_kernel/interpreter.py"
---

## 源码文件位置

浏览器端 Python Kernel 位于 `packages/pyodide-kernel/py/pyodide-kernel/pyodide_kernel/`，源码路径：
`external/libs/jupyter/pyodide-kernel/packages/pyodide-kernel/py/pyodide-kernel/pyodide_kernel/`

## 核心模块清单

| 文件 | 类/函数 | 说明 |
|------|---------|------|
| `__init__.py` | — | 入口：mocks → patches → streams → shell → stdout/stderr 重定向 |
| `kernel.py` | `PyodideKernel` | Python 端 Kernel 逻辑（代码执行/补全/内省） |
| `interpreter.py` | `Interpreter`、`LitePythonShellApp`、`CustomHistoryManager` | IPython InteractiveShell 子类化 |
| `display.py` | `LiteStream`、`LiteDisplayPublisher`、`LiteDisplayHook` | 输出/显示回调桥接 |
| `comm.py` | `Comm` | Comm 通信桥接 |
| `mocks.py` | `apply_mocks()` | POSIX 模块 mock（termios/fcntl/resource/tornado/pexpect） |
| `patches.py` | `apply_patches()` | 运行时补丁（matplotlib backend） |
| `litetransform.py` | `LiteTransformerManager`、`pip_magic` | 代码预转换（%pip → piplite.install） |
| `jsonutil.py` | `json_clean()`、`encode_images()` | JSON 序列化工具 |

## 初始化顺序（__init__.py）

```python
# 步骤 0：早期 mock（修改 sys.modules）
from . import mocks
mocks.apply_mocks()

# 步骤 1：补丁（需要 import 的配置）
from . import patches
patches.apply_patches()

# 步骤 2：创建 IPython 环境
from .display import LiteStream
from .interpreter import LitePythonShellApp

stdout_stream = LiteStream("stdout")
stderr_stream = LiteStream("stderr")

ipython_shell_app = LitePythonShellApp()
ipython_shell_app.initialize()
kernel_instance = ipython_shell_app.shell.kernel

# 步骤 3：重定向标准流
sys.stdout = stdout_stream
sys.stderr = stderr_stream
```

## PyodideKernel（Python 端）

```python
class PyodideKernel(LoggingConfigurable):
    interpreter: Interpreter = Instance("pyodide_kernel.interpreter.Interpreter")
    comm_manager: CommManager = Instance(CommManager)
    parent_header: typing.Any = Instance(Any, allow_none=True)
    lite_transform_manager: LiteTransformerManager = Instance(LiteTransformerManager, ())

    async def run(self, code): ...
    def complete(self, code, cursor_pos): ...
    def inspect(self, code, cursor_pos, detail_level): ...
    def is_complete(self, code): ...
    def comm_info(self, target_name=""): ...
```

`run()` 方法执行流程：
1. `lite_transform_manager.transform_cell(code)` — 应用 pyodide 特定转换（%pip）
2. `pyodide_js.loadPackagesFromImports(lite_cell)` — 自动加载 import 语句中的包
3. `transform_cell(lite_cell)` — IPython 标准转换
4. 根据 `should_run_async` 判断同步/异步执行
5. 返回 results（含 status/payload 或 error 信息）

## Interpreter（IPython 子类）

```python
class Interpreter(InteractiveShell):
    kernel: PyodideKernel
    Completer.use_jedi = True
    _last_traceback: dict | None = None
    _input: Callable | None
    _getpass: Callable | None

    @property
    def input(self): ...
    @input.setter
    def input(self, value): ...  # 替换 builtins.input

    @property
    def getpass(self): ...
    @getpass.setter
    def getpass(self, value): ...  # 替换 getpass.getpass

    def init_history(self): ...  # 使用 CustomHistoryManager（禁用）
    def enable_gui(self, gui=None): ...  # 空实现（不支持 GUI）
    def _showtraceback(self, etype, evalue, stb): ...  # 捕获 traceback
```

## Display/Stream 桥接类

```python
class LiteStream:
    encoding = "utf-8"
    name: str  # "stdout" 或 "stderr"
    publish_stream_callback: Callable | None = None
    def write(self, text): ...  # 调用 callback
    def flush(self): ...  # no-op
    def isatty(self): return False

class LiteDisplayPublisher(DisplayPublisher):
    display_data_callback: Callable | None = None
    update_display_data_callback: Callable | None = None
    clear_output_callback: Callable | None = None
    def publish(self, data, metadata=None, ...): ...  # 路由到对应 callback
    def clear_output(self, wait=False): ...

class LiteDisplayHook(DisplayHook):
    publish_execution_result: Callable | None = None
    def write_format_data(self, format_dict, md_dict=None): ...
    def finish_displayhook(self): ...  # 调用 publish_execution_result
```

## Mock 模块清单

| Mock 模块 | 内容 |
|-----------|------|
| `termios` | 空模块 + `TCSAFLUSH = 2` |
| `fcntl` | 空模块 |
| `resource` | 空模块 |
| `tornado` / `tornado.gen` | `coroutine` 装饰器（返回原函数）、`sleep`（no-op）、`is_coroutine_function`（返回 False） |
| `pexpect` | 空模块 |

## 相关概念

- [架构总览](/concepts/02-architecture-overview.md)
- [Python 兼容性层](/concepts/06-python-compatibility.md)
- [消息桥接机制](/concepts/07-message-bridge.md)
