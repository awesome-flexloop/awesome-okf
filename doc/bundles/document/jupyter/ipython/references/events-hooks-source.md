---
type: Reference
title: Events & Hooks API 参考
description: IPython 事件系统与钩子系统完整 API 参考，包括 EventManager 回调管理、内置事件列表、CommandChainDispatcher 链式钩子分发和可覆盖的用户钩子
tags: [api, events, hooks, callback, extension, reference, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ipython-events
    resource: /references/events-hooks-source.md
    title: IPython/core/events.py EventManager & Available Events
  - id: ipython-hooks
    resource: /references/events-hooks-source.md
    title: IPython/core/hooks.py CommandChainDispatcher & Default Hooks
---

# Events & Hooks API 参考

IPython 提供两套自定义机制：**Events**（事件回调，面向扩展作者，同一事件可注册多个回调）和 **Hooks**（钩子，面向终端用户，按优先级链式尝试）。

---

## EventManager

### 类定义

```python
class EventManager:
    """管理事件集合及其回调序列

    挂载在 InteractiveShell 实例上作为 ``shell.events`` 属性。
    """
```

定义在 `IPython/core/events.py`。

### 构造函数

```python
def __init__(self, shell: InteractiveShell,
             available_events: Iterable[str],
             print_on_error: bool = True):
    """
    Parameters
    ----------
    shell : InteractiveShell — 关联的 Shell 实例
    available_events : Iterable[str] — 可用事件名称列表
    print_on_error : bool — 回调出错时是否打印警告（默认 True）
    """
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `shell` | InteractiveShell | 关联的 IPython Shell 实例 |
| `callbacks` | dict[str, list[Callable]] | 事件名 → 回调函数列表的映射 |
| `print_on_error` | bool | 回调异常时是否打印错误信息 |

### 核心方法

#### register()

```python
def register(self, event: str, function: Callable[..., Any]) -> None:
    """注册事件回调

    Parameters
    ----------
    event : str — 事件名称（必须在 available_events 中）
    function : Callable — 回调函数，参数需与事件原型匹配

    Raises
    ------
    TypeError — function 不可调用
    KeyError — event 不是已知事件

    同一函数不会被重复注册（去重检查）。
    """
```

#### unregister()

```python
def unregister(self, event: str, function: Callable[..., Any]) -> None:
    """移除事件回调

    Raises
    ------
    ValueError — 函数未注册到该事件
    """
```

#### trigger()

```python
def trigger(self, event: str, *args: Any, **kwargs: Any) -> None:
    """触发事件，按注册顺序调用所有回调

    回调中的异常被捕获：
    - print_on_error=True 时打印错误信息
    - 通过 shell.showtraceback() 显示 traceback
    - 不影响其他回调执行
    - KeyboardInterrupt 也会被捕获
    """
```

### 使用示例

```python
ip = get_ipython()

# 注册回调
def my_pre_run(info):
    print(f"About to run: {info.raw_cell[:50]}...")

ip.events.register('pre_run_cell', my_pre_run)

# 移除回调
ip.events.unregister('pre_run_cell', my_pre_run)
```

---

## 内置事件

所有事件通过 `@_define_event` 装饰器注册到 `available_events` 字典中，作为 no-op 原型函数定义。

### 事件列表

| 事件名 | 回调签名 | 触发时机 |
|--------|---------|---------|
| `shell_initialized` | `(ip: InteractiveShell) -> None` | Shell 初始化完成后（加载扩展和启动脚本之前） |
| `pre_execute` | `() -> None` | 代码执行前（包括 comm/widget 消息和静默执行） |
| `pre_run_cell` | `(info: ExecutionInfo) -> None` | 用户输入的代码单元格执行前 |
| `post_execute` | `() -> None` | 代码执行后（包括 comm/widget 消息和静默执行） |
| `post_run_cell` | `(result: ExecutionResult) -> None` | 用户输入的代码单元格执行后 |

### 事件执行顺序

```
用户输入单元格
    │
    ▼
pre_execute()           ← 无参数
    │
    ▼
pre_run_cell(info)      ← 传入 ExecutionInfo
    │
    ▼
[ 实际代码执行 ]
    │
    ▼
post_run_cell(result)   ← 传入 ExecutionResult
    │
    ▼
post_execute()          ← 无参数
```

> ⚠️ `pre_execute`/`post_execute` 的触发范围更广，包括 widget/comm 消息和 `silent=True` 的执行；`pre_run_cell`/`post_run_cell` 仅对用户输入的单元格触发。

> ⚠️ `shell_initialized` 在扩展加载前触发，因此只能通过子类化 Shell 来注册此事件回调，不能通过扩展注册。

### ExecutionInfo

```python
class ExecutionInfo:
    """传递给 pre_run_cell 的执行信息对象"""

    raw_cell: str           # 原始单元格文本（转换前）
    transformed_cell: str   # 转换后的单元格文本
    store_history: bool     # 是否存入历史
    silent: bool            # 是否静默执行
    shell_futures: bool     # 是否启用 shell futures
    cell_id: str | None     # 单元格 ID
    cell_meta: dict | None  # 单元格元数据
```

### ExecutionResult

```python
class ExecutionResult:
    """传递给 post_run_cell 的执行结果对象"""

    execution_count: int | None         # 执行计数
    error_before_exec: BaseException | None  # 执行前错误
    error_in_exec: BaseException | None      # 执行中错误
    info: ExecutionInfo                 # 对应的 ExecutionInfo
    result: Any                         # 返回值（成功时）

    @property
    def success(self) -> bool: ...      # 是否成功执行
```

### 扩展中注册事件示例

```python
def load_ipython_extension(ip):
    def on_pre_run(info):
        print(f"[Logger] Running cell {info.cell_id}: {info.raw_cell[:30]}")

    def on_post_run(result):
        if result.error_in_exec:
            print(f"[Logger] Error: {result.error_in_exec}")

    ip.events.register('pre_run_cell', on_pre_run)
    ip.events.register('post_run_cell', on_post_run)

def unload_ipython_extension(ip):
    # 记得在卸载时移除回调
    pass
```

---

## Hooks 系统

Hooks 是 IPython 设计用于被终端用户覆盖的方法，通过 `shell.hooks` 命名空间访问。与 Events 的区别：
- **Events**：多个回调并存，依次执行，面向扩展作者
- **Hooks**：按优先级链式分发，第一个成功（不抛 TryNext）的结果被采用，面向终端用户自定义

### CommandChainDispatcher

```python
class CommandChainDispatcher:
    """按优先级链分发调用，直到某个函数成功处理

    函数抛出 TryNext 异常表示"我不能处理，请尝试下一个"
    """
```

定义在 `IPython/core/hooks.py`。

#### 构造函数

```python
def __init__(self, commands: list[tuple[int, Callable]] | None = None):
    """
    commands: 可选的 (priority, func) 元组列表初始化
    """
```

#### 核心方法

##### \_\_call\_\_()

```python
def __call__(self, *args: Any, **kw: Any) -> Any:
    """按优先级顺序调用链中所有函数

    返回第一个不抛 TryNext 的函数的返回值。
    若所有函数都抛 TryNext，则抛出最后一个 TryNext。
    """
```

##### add()

```python
def add(self, func: Callable[..., Any], priority: int = 0) -> None:
    """添加函数到命令链

    Parameters
    ----------
    func : Callable — 钩子函数（第一个参数为 self，即 Shell 实例）
    priority : int — 优先级，数字越小优先级越高（0 > 50 > 100）
    """
```

> **优先级约定**：
> - 默认钩子优先级为 100（最低）
> - 用户钩子推荐使用 0-100
> - `display_page` 的 pager 钩子优先级为 90

##### \_\_iter\_\_()

```python
def __iter__(self):
    """迭代链中所有 (priority, func) 元组"""
```

### TryNext 异常

```python
from IPython.core.error import TryNext

class TryNext(Exception):
    """钩子函数抛出此异常表示"我无法处理，请尝试链中的下一个函数"

    可携带消息参数: raise TryNext("Reason for skipping")
    """
```

---

## 默认 Hooks

所有默认钩子定义在 `IPython/core/hooks.py`，通过 `__all__` 导出：

```python
__all__ = ["editor", "synchronize_with_editor", "show_in_pager", "clipboard_get"]
```

### editor

```python
def editor(self, filename, linenum=None, wait=True):
    """打开默认编辑器到指定文件和行号

    Parameters
    ----------
    filename : str — 文件路径
    linenum : int, optional — 行号
    wait : bool — 是否等待编辑器关闭（默认 True）

    行为:
    - 读取 self.editor（从 $EDITOR 环境变量或平台默认值）
    - unix 默认 vi，windows 默认 notepad
    - notepad 不支持 +linenum 参数
    - 路径含空格且是有效文件时自动加引号
    - wait=True 且进程退出码非 0 时抛 TryNext
    """
```

### synchronize_with_editor

```python
def synchronize_with_editor(self, filename, linenum, column):
    """同步编辑器到指定位置（无操作默认实现）

    用于集成开发环境中的编辑器同步（如 PyCharm、VSCode）
    """
```

### show_in_pager

```python
def show_in_pager(self, data, start, screen_lines):
    """通过 pager 显示文本（默认抛 TryNext 使用内置 pager）

    覆盖此方法可自定义 pager 行为（如使用外部 less 程序）
    """
    raise TryNext
```

### clipboard_get

```python
def clipboard_get(self):
    """从剪贴板获取文本

    平台特定的链式分发:
    - Windows: win32_clipboard_get → tkinter_clipboard_get
    - macOS: osx_clipboard_get → tkinter_clipboard_get
    - Linux: wayland_clipboard_get → tkinter_clipboard_get
    """
```

---

## InteractiveShell 的 Hooks API

### init_hooks()

```python
def init_hooks(self):
    """初始化钩子系统（在 Shell 构造时调用）

    1. 创建 self.hooks = Struct()
    2. 为 hooks.__all__ 中每个钩子名注册默认实现（priority=100）
    3. 若 self.display_page 为 True，注册 page.display_page（priority=90）
    """
```

### set_hook()

```python
def set_hook(self, name, hook, priority=50, str_key=None, re_key=None):
    """设置 IPython 内部钩子

    Parameters
    ----------
    name : str — 钩子名称（如 'editor', 'show_in_pager'）
    hook : Callable — 钩子函数（第一个参数为 self/Shell 实例）
    priority : int — 优先级（默认 50，数字越小越高）
    str_key : str, optional — 字符串分派键（用于 StrDispatch）
    re_key : str, optional — 正则分派键（用于 StrDispatch）

    行为:
    - hook 通过 types.MethodType 绑定为实例方法
    - 指定 str_key/re_key 时使用 StrDispatch 分派
    - 未知钩子名会打印警告
    - 已有 CommandChainDispatcher 则追加；普通函数则替换
    """
```

### 设置钩子示例

```python
# 示例 1: 替换编辑器钩子
def my_editor(self, filename, linenum=None, wait=True):
    import subprocess
    subprocess.run(['code', '-g', f'{filename}:{linenum or 1}'])
    if wait:
        raise TryNext()  # 让其他钩子也有机会处理

ip = get_ipython()
ip.set_hook('editor', my_editor, priority=50)

# 示例 2: 自定义 pager
def my_pager(self, data, start, screen_lines):
    import subprocess
    subprocess.run(['less', '-R'], input=data, text=True)

ip.set_hook('show_in_pager', my_pager, priority=50)

# 示例 3: 从 startup 文件加载
# ~/.ipython/profile_default/startup/my_hooks.py
def load_ipython_extension(ip):
    def custom_editor(self, filename, linenum=None, wait=True):
        import os
        editor = os.environ.get('MY_EDITOR', 'vim')
        ...
    ip.set_hook('editor', custom_editor, priority=40)
```

---

## Events 与 Hooks 对比

| 特性 | Events | Hooks |
|------|--------|-------|
| 设计目标 | 扩展作者 | 终端用户 |
| 多回调 | 全部执行 | 链式：第一个成功的结果 |
| 失败处理 | 捕获异常，继续执行 | TryNext 跳到下一个 |
| 优先级 | 注册顺序 | 数字优先级 |
| 移除支持 | unregister() | 替换或创建新链 |
| 典型用途 | 日志、监控、自动保存 | 编辑器、pager、剪贴板 |
| 访问方式 | `ip.events.register()` | `ip.set_hook()` |
| 定义数量 | 5 个内置事件 | 4 个默认钩子 |

---

## 相关概念

- **[扩展系统](extension-source.md)**：扩展中如何注册事件回调（load_ipython_extension）
- **[InteractiveShell](interactiveshell-source.md)**：init_hooks() 和 init_events() 初始化流程
- **生命周期**：pre_execute/post_execute 与单元格执行生命周期
- **启动文件**：通过 startup 脚本设置自定义钩子
