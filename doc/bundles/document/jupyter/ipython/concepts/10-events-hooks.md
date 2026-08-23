---
type: concept
title: "10 - 事件与钩子"
description: IPython EventManager 事件广播系统、Hooks 钩子覆盖机制，以及何时使用 Events/Hooks/Extensions/Magics 的决策指南
tags: [events, hooks, callback, lifecycle, command-chain, customization]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-events
    title: IPython/core/events.py
  - id: ipython-hooks
    title: IPython/core/hooks.py
---

## Events 与 Hooks 的核心区别

IPython 提供了两种不同的定制机制，服务于不同的需求 [F-360][F-370]：

| 维度 | Events（事件） | Hooks（钩子） |
|------|---------------|--------------|
| **设计目的** | 通知/广播 | 定制/覆盖默认行为 |
| **观察者模式** | 多回调（多个扩展可同时监听同一事件） | 单函数或职责链（一个 hook 一个有效实现） |
| **数据流向** | 只读通知（回调不应修改参数） | 可替代默认行为 |
| **异常处理** | 回调异常被捕获，打印警告但不中断 | 支持 TryNext 链传递到下一个处理器 |
| **注册方式** | `events.register(event, callback)` | `shell.set_hook(name, hook)` |
| **典型场景** | 日志、计时、通知、副作用 | 替换编辑器、自定义分页器、剪贴板访问 |

简单记忆：**Events 是"通知我发生了什么"，Hooks 是"让我来处理这件事"**。

## EventManager 事件系统

`EventManager` 管理事件回调的注册和触发 [F-360]。它被实例化为 `shell.events` 属性。

### 核心 API

```python
class EventManager:
    def __init__(self, shell, available_events, print_on_error=True):
        """初始化事件管理器 [F-361]
        shell: InteractiveShell 实例
        available_events: 可用事件名的可迭代对象
        print_on_error: 回调异常时是否打印错误
        """
    
    def register(self, event, function):
        """注册事件回调 [F-362]
        event: 事件名字符串
        function: 回调函数，签名需匹配事件原型
        如果 function 已注册则不重复添加
        """
    
    def unregister(self, event, function):
        """取消注册事件回调 [F-363]"""
    
    def trigger(self, event, *args, **kwargs):
        """触发事件，调用所有注册的回调 [F-364]
        回调中的异常被捕获并打印，不中断执行
        """
```

### 预定义事件

IPython 定义了 5 个生命周期事件 [F-367]：

```python
@_define_event
def pre_execute() -> None:
    """代码执行前触发（包括 comm/widget 消息和静默执行）[F-367]"""

@_define_event
def pre_run_cell(info: ExecutionInfo) -> None:
    """用户代码执行前触发 [F-367]
    info: ExecutionInfo 对象，包含原始代码、cell 名、存储历史标志等
    """

@_define_event
def post_execute() -> None:
    """代码执行后触发（包括 comm/widget 消息和静默执行）[F-367]"""

@_define_event
def post_run_cell(result: ExecutionResult) -> None:
    """用户代码执行后触发 [F-367]
    result: ExecutionResult 对象，包含 success、error_in_exec、result 等
    """

@_define_event
def shell_initialized(ip: InteractiveShell) -> None:
    """Shell 完全初始化后触发 [F-367]
    在扩展和 startup 文件加载之前触发
    """
```

事件触发时序：

```
Shell 初始化完成
  │
  ├── events.trigger('shell_initialized', ip)    ← 扩展加载前
  │
  ├── ... 加载扩展、执行 startup 文件 ...
  │
  ├── REPL 主循环中每次 run_cell():
  │     │
  │     ├── events.trigger('pre_execute')
  │     ├── events.trigger('pre_run_cell', info)
  │     │
  │     ├── 实际执行代码（编译、exec、显示）
  │     │
  │     ├── events.trigger('post_execute')
  │     └── events.trigger('post_run_cell', result)
  │
  ▼
```

### 事件使用示例

```python
ip = get_ipython()

# 示例 1：记录每次 cell 执行的时间
import time
_execution_times = []

def pre_run(info):
    ip._start_time = time.time()

def post_run(result):
    elapsed = time.time() - ip._start_time
    _execution_times.append(elapsed)
    print(f"  ⏱ Cell executed in {elapsed:.3f}s")

ip.events.register('pre_run_cell', pre_run)
ip.events.register('post_run_cell', post_run)

# 示例 2：在每次执行后自动保存变量
import pickle
def autosave():
    with open('autosave.pkl', 'wb') as f:
        user_vars = {k: v for k, v in ip.user_ns.items() 
                    if not k.startswith('_')}
        pickle.dump(user_vars, f)

ip.events.register('post_execute', autosave)

# 取消注册
ip.events.unregister('post_execute', autosave)
```

### 事件的注意事项

1. **回调应该快速**：事件回调在 REPL 主循环中同步执行，耗时操作会阻塞交互
2. **不要在回调中抛出异常**：虽然 EventManager 会捕获异常，但会打印错误信息影响用户体验
3. **回调不要修改参数**：事件参数是共享的，修改它们可能影响其他回调和主逻辑
4. **多回调顺序不确定**：同一事件的多个回调按注册顺序调用，但不应依赖顺序
5. **shell_initialized 的特殊时机**：在扩展加载前触发，只能在子类中通过覆写使用，扩展中注册的回调不会被调用

## Hooks 钩子系统

Hooks 是 IPython 设计给用户覆盖的定制点 [F-370]。与 Events 的多回调广播不同，Hooks 允许用户替换特定的默认行为。

### 内置 Hooks

IPython 预定义了 4 个钩子 [F-371]：

```python
__all__ = [
    "editor",                  # 打开编辑器
    "synchronize_with_editor", # 与编辑器同步
    "show_in_pager",           # 在分页器中显示内容
    "clipboard_get",           # 从剪贴板获取文本
]
```

#### editor 钩子

默认行为：读取 `$EDITOR` 环境变量，使用系统默认编辑器（vi 或 notepad）打开文件 [F-371]。

```python
def editor(self, filename, linenum=None, wait=True):
    """默认编辑器钩子 [F-371]"""
    editor = self.editor  # 从 $EDITOR 或配置获取
    # 构建编辑器命令并执行 subprocess.Popen
    ...
```

#### synchronize_with_editor 钩子

默认行为：空操作（no-op）。IDE 集成通常设置此钩子，在 IPython 中执行 `%edit` 时通知外部编辑器。

```python
def synchronize_with_editor(self, filename, linenum, column):
    """同步到外部编辑器的钩子 [F-371]"""
    pass  # 默认空实现
```

#### show_in_pager 钩子

默认行为：抛出 TryNext，使用 IPython 内置分页器 [F-371]。

```python
def show_in_pager(self, data, start, screen_lines):
    """分页显示钩子，默认抛 TryNext 使用内置分页器"""
    raise TryNext
```

#### clipboard_get 钩子

默认行为：按平台尝试多种剪贴板获取方法（win32、osx、wayland、tkinter）[F-371]。

### CommandChainDispatcher 职责链

`CommandChainDispatcher` 实现职责链模式，支持多个候选函数按优先级尝试 [F-372]：

```python
class CommandChainDispatcher:
    def __init__(self, commands=None):
        self.chain = commands or []  # [(priority, func), ...]
    
    def __call__(self, *args, **kw):
        """按优先级调用链中函数，返回第一个不抛 TryNext 的结果 [F-372]"""
        last_exc = TryNext()
        for prio, cmd in self.chain:
            try:
                return cmd(*args, **kw)
            except TryNext as exc:
                last_exc = exc
        raise last_exc  # 所有函数都抛 TryNext 则向上抛出
    
    def add(self, func, priority=0):
        """添加函数到链中，按优先级排序 [F-372]"""
        self.chain.append((priority, func))
        self.chain.sort(key=lambda x: x[0])
```

这是 `clipboard_get` 钩子的默认实现方式——按平台优先级依次尝试不同的剪贴板后端，第一个成功的返回结果。

### set_hook 设置钩子

通过 `shell.set_hook(name, hook)` 方法设置钩子：

```python
ip = get_ipython()

# 示例 1：替换默认编辑器为 VS Code
def vscode_editor(self, filename, linenum=None, wait=True):
    import subprocess
    cmd = ['code']
    if linenum:
        cmd += ['--goto', f'{filename}:{linenum}']
    else:
        cmd.append(filename)
    proc = subprocess.Popen(cmd)
    if wait:
        proc.wait()

ip.set_hook('editor', vscode_editor)

# 示例 2：使用 CommandChainDispatcher 添加自定义剪贴板后端
from IPython.core.hooks import CommandChainDispatcher

def my_clipboard(self):
    """自定义剪贴板（例如从 Wayland 主选择）"""
    try:
        import subprocess
        return subprocess.check_output(['wl-paste', '--primary'], text=True)
    except Exception:
        from IPython.core.error import TryNext
        raise TryNext()

# 如果已有 CommandChainDispatcher，添加到链中
if isinstance(ip.hooks.clipboard_get, CommandChainDispatcher):
    ip.hooks.clipboard_get.add(my_clipboard, priority=0)
else:
    # 创建新的链，默认方法放最后
    chain = CommandChainDispatcher()
    chain.add(my_clipboard, priority=0)
    chain.add(ip.hooks.clipboard_get, priority=100)
    ip.set_hook('clipboard_get', chain)
```

### TryNext 异常

`TryNext` 是 hooks 链中传递控制权的特殊异常 [F-495]。当一个 hook 函数无法处理请求时，抛出 `TryNext()` 让链中下一个函数尝试：

```python
def my_hook(self, *args):
    if can_handle:
        return result
    else:
        raise TryNext()  # 让下一个处理器尝试
```

## 四种扩展机制的决策指南

IPython 提供四种互补的扩展机制，选择正确的机制很重要：

```
你需要做什么？
  │
  ├── 添加新的交互式命令（%xxx 或 %%xxx）
  │     → 注册 Magics（见 [04-magic-system] 和 [11-custom-magics]）
  │
  ├── 在执行生命周期中执行副作用（日志/计时/通知/自动保存）
  │     → 使用 Events（多观察者，互不干扰）
  │
  ├── 替换 IPython 的默认行为（编辑器/分页器/剪贴板）
  │     → 使用 Hooks（单职责点，可链式尝试）
  │
  └── 分发一个可安装/卸载的功能包（组合多种机制）
        → 创建 Extension（在 load_ipython_extension 中注册 magics/events/hooks/formatter）
```

### 扩展机制对比表

| 特性 | Magics | Events | Hooks | Extensions |
|------|--------|--------|-------|------------|
| **用途** | 添加命令 | 生命周期通知 | 替换默认行为 | 功能包分发 |
| **注册** | `register_magics()` | `events.register()` | `set_hook()` | `%load_ext` |
| **卸载** | 手动移除 | `events.unregister()` | 恢复默认 | `%unload_ext` |
| **多实例** | 同名覆盖 | 多回调 | 链/单函数 | 单加载 |
| **典型用途** | `%timeit`、`%run` | 日志、计时 | 编辑器、剪贴板 | autoreload |

## 完整扩展示例：组合 Events 和 Hooks

```python
# my_ipython_setup.py
"""组合使用 Events 和 Hooks 的扩展示例"""

import time
from IPython.core.magic import Magics, magics_class, line_magic

@magics_class
class TimerMagics(Magics):
    @line_magic
    def timer_stats(self, line):
        """显示执行时间统计"""
        if not hasattr(self.shell, '_exec_times'):
            print("No timing data available")
            return
        times = self.shell._exec_times
        avg = sum(times) / len(times)
        print(f"Total cells: {len(times)}")
        print(f"Average time: {avg:.3f}s")
        print(f"Max time: {max(times):.3f}s")
        print(f"Min time: {min(times):.3f}s")

def load_ipython_extension(ip):
    # 注册魔法
    ip.register_magics(TimerMagics)
    
    # 注册事件回调
    ip._exec_times = []
    
    def pre_run(info):
        ip._start = time.time()
    
    def post_run(result):
        elapsed = time.time() - ip._start
        ip._exec_times.append(elapsed)
    
    ip.events.register('pre_run_cell', pre_run)
    ip.events.register('post_run_cell', post_run)
    
    # 设置自定义编辑器钩子
    def nvim_editor(self, filename, linenum=None, wait=True):
        import subprocess, os
        cmd = ['nvim']
        if linenum:
            cmd.append(f'+{linenum}')
        cmd.append(filename)
        subprocess.Popen(cmd).wait()
    
    ip.set_hook('editor', nvim_editor)
    
    print("Timer extension loaded. Use %timer_stats to see stats.")

def unload_ipython_extension(ip):
    # 清理：但 events 和 magics 的清理较复杂
    print("Timer extension unloaded.")
```

## 相关概念

- [扩展系统](/concepts/09-extension-system.md)
- [魔法命令系统](/concepts/04-magic-system.md)
- [Shell 生命周期](/concepts/03-shell-lifecycle.md)
- [自定义魔法开发](/concepts/11-custom-magics.md)
- [信源参考 - 事件与钩子](/references/events-hooks-source.md)
