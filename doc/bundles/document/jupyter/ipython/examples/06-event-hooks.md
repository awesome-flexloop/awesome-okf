---
type: example
title: "06 - 事件监听与钩子定制"
description: 使用 IPython 事件系统监听执行生命周期、自定义钩子覆盖默认行为、输入转换器，以及 IPython.embed() 嵌入式调试实战
tags: [example, events, hooks, callback, lifecycle, embed, pre-run-cell, post-run-cell, editor-hook]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-events
    title: IPython/core/events.py
  - id: ipython-hooks
    title: IPython/core/hooks.py
  - id: ipython-interactiveshell
    title: IPython/core/interactiveshell.py
  - id: ipython-inputtransformer
    title: IPython/core/inputtransformer2.py
related_concepts: [/concepts/10-events-hooks.md, /concepts/03-shell-lifecycle.md, /concepts/09-extension-system.md]
---

## 目标

本示例演示如何使用 IPython 的事件（Events）和钩子（Hooks）系统定制 Shell 行为，覆盖以下内容：

1. 注册 `pre_run_cell` 和 `post_run_cell` 事件回调实现日志和计时
2. 注册 `shell_initialized` 事件进行启动定制
3. 使用 `set_hook()` 自定义编辑器、剪贴板等默认行为
4. 使用 `TryNext` 异常实现钩子职责链
5. 自定义输入转换器（Input Transformer）
6. 使用 `IPython.embed()` 在代码中嵌入交互式调试会话

## 完整代码

### 示例 1：事件监听——执行计时和日志（可直接在 IPython 中运行）

```python
from IPython import get_ipython
import time

ip = get_ipython()

# ===== 1. 自动计时：记录每次 cell 执行耗时 =====

# 存储计时数据
_execution_log = []

def on_pre_run(info):
    """代码执行前记录开始时间"""
    ip._custom_start_time = time.time()
    ip._custom_current_code = info.raw_cell

def on_post_run(result):
    """代码执行后计算并显示耗时"""
    if not hasattr(ip, '_custom_start_time'):
        return
    start = ip._custom_start_time
    elapsed = time.time() - start
    code = getattr(ip, '_custom_current_code', '')
    success = result.success if hasattr(result, 'success') else True
    
    _execution_log.append({
        'code': code[:80],
        'elapsed': elapsed,
        'success': success,
        'timestamp': time.strftime('%H:%M:%S'),
    })
    
    # 只对耗时超过 0.1s 的代码显示计时
    if elapsed > 0.1:
        status = "✓" if success else "✗"
        print(f"  {status} [{elapsed:.3f}s]")

# 注册事件回调
ip.events.register('pre_run_cell', on_pre_run)
ip.events.register('post_run_cell', on_post_run)

# 测试
# 执行一些代码，看看计时效果
import math
result = sum(math.sqrt(i) for i in range(100_000))
print(f"Result: {result:.2f}")

# 查看执行日志
print("\n=== 执行日志 ===")
for entry in _execution_log[-5:]:
    status = "✓" if entry['success'] else "✗"
    code_preview = entry['code'][:50].replace('\n', '↵')
    print(f"  {entry['timestamp']} {status} [{entry['elapsed']:.3f}s] {code_preview}")

# ===== 2. pre_execute / post_execute：更底层的执行事件 =====

_pre_count = 0
_post_count = 0

def on_pre_execute():
    """每次执行前触发（包括静默执行和 widget 消息）"""
    global _pre_count
    _pre_count += 1

def on_post_execute():
    """每次执行后触发"""
    global _post_count
    _post_count += 1

ip.events.register('pre_execute', on_pre_execute)
ip.events.register('post_execute', on_post_execute)

# ===== 3. 取消注册事件回调 =====
# ip.events.unregister('pre_run_cell', on_pre_run)
# ip.events.unregister('post_run_cell', on_post_run)
```

### 示例 2：错误日志记录

```python
from IPython import get_ipython
import traceback
from datetime import datetime

ip = get_ipython()

_error_log = []

def log_errors(result):
    """记录执行错误"""
    if hasattr(result, 'error_in_exec') and result.error_in_exec:
        error = result.error_in_exec
        entry = {
            'time': datetime.now().isoformat(),
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exception(type(error), error, error.__traceback__),
        }
        _error_log.append(entry)
        print(f"  ⚠️  错误已记录 ({entry['type']})")

ip.events.register('post_run_cell', log_errors)

# 查看错误日志
def show_errors(n=5):
    """显示最近的错误日志"""
    if not _error_log:
        print("没有错误记录")
        return
    for i, entry in enumerate(_error_log[-n:], 1):
        print(f"\n--- 错误 {i}: {entry['time']} ---")
        print(f"类型: {entry['type']}")
        print(f"消息: {entry['message']}")
        print("Traceback:")
        for line in entry['traceback'][-3:]:
            print(line.rstrip())

# 测试（故意制造错误）
# 1 / 0
# show_errors()
```

### 示例 3：自定义钩子——编辑器与剪贴板

```python
from IPython import get_ipython
import subprocess
import sys

ip = get_ipython()

# ===== 自定义编辑器钩子 =====

def vscode_editor(self, filename, linenum=None, wait=True):
    """使用 VS Code 作为 %edit 魔法的编辑器"""
    cmd = ['code']
    if linenum:
        cmd += ['--goto', f'{filename}:{linenum}']
    else:
        cmd.append(filename)
    try:
        proc = subprocess.Popen(cmd)
        if wait:
            proc.wait()
    except FileNotFoundError:
        # 如果 code 命令不可用，尝试其他编辑器
        print("VS Code 未找到，尝试使用 notepad（Windows）或 vim...")
        if sys.platform == 'win32':
            subprocess.Popen(['notepad', filename]).wait()
        else:
            subprocess.Popen(['vim', filename]).wait()

# 设置编辑器钩子
ip.set_hook('editor', vscode_editor)
print("✅ 编辑器已设置为 VS Code。使用 %edit 测试。")

# ===== 自定义剪贴板钩子（带职责链）=====

from IPython.core.hooks import CommandChainDispatcher
from IPython.core.error import TryNext

def wl_paste_clipboard(self):
    """Linux Wayland 剪贴板后端"""
    try:
        return subprocess.check_output(
            ['wl-paste', '--no-newline'],
            text=True, stderr=subprocess.DEVNULL
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise TryNext()  # 让下一个处理器尝试

def xclip_clipboard(self):
    """Linux X11 剪贴板后端"""
    try:
        return subprocess.check_output(
            ['xclip', '-selection', 'clipboard', '-o'],
            text=True, stderr=subprocess.DEVNULL
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise TryNext()

# 创建职责链，按优先级尝试
clipboard_chain = CommandChainDispatcher()
clipboard_chain.add(wl_paste_clipboard, priority=10)   # 先尝试 Wayland
clipboard_chain.add(xclip_clipboard, priority=20)     # 再尝试 X11
# 默认剪贴板处理器优先级最低
clipboard_chain.add(ip.hooks.clipboard_get, priority=100)

ip.set_hook('clipboard_get', clipboard_chain)
print("✅ 剪贴板钩子已设置（支持 Wayland/X11 链）")
```

### 示例 4：扩展中组合 Events + Hooks（保存为 `timing_ext.py`）

```python
# timing_ext.py —— 组合事件和钩子的扩展示例
"""执行计时扩展：自动记录每次 cell 执行时间，提供统计命令

加载: %load_ext timing_ext
使用:
    %timing_stats    # 显示执行时间统计
    %timing_on       # 开启计时
    %timing_off      # 关闭计时
卸载: %unload_ext timing_ext
"""

import time
from IPython.core.magic import Magics, magics_class, line_magic


_timing_state = {
    'enabled': True,
    'records': [],
    'pre_cb': None,
    'post_cb': None,
}


@magics_class
class TimingMagics(Magics):
    """执行时间统计魔法"""
    
    @line_magic
    def timing_stats(self, line):
        """显示执行时间统计
        
        用法:
            %timing_stats        # 显示统计
            %timing_stats --clear # 清除记录
            %timing_stats -n 10  # 显示最近 10 条
        """
        records = _timing_state['records']
        
        if '--clear' in line:
            records.clear()
            print("✅ 计时记录已清除")
            return
        
        count = None
        if '-n' in line:
            parts = line.split()
            try:
                idx = parts.index('-n')
                count = int(parts[idx + 1])
            except (ValueError, IndexError):
                pass
        
        show = records[-count:] if count else records
        
        if not show:
            print("尚无计时记录")
            return
        
        times = [r['elapsed'] for r in show]
        avg = sum(times) / len(times)
        
        print(f"=== 执行统计（{len(show)} 条记录）===")
        print(f"平均: {avg:.4f}s  最快: {min(times):.4f}s  最慢: {max(times):.4f}s")
        print(f"总计: {sum(times):.4f}s  状态: {'开启' if _timing_state['enabled'] else '关闭'}")
        print()
        
        for i, r in enumerate(show[-10:], 1):
            code = r['code'][:50].replace('\n', '↵')
            status = "✓" if r['success'] else "✗"
            print(f"  {i:2d}. {status} [{r['elapsed']:.4f}s] {code}")
    
    @line_magic
    def timing_on(self, line):
        """开启计时"""
        _timing_state['enabled'] = True
        print("⏱  执行计时已开启")
    
    @line_magic
    def timing_off(self, line):
        """关闭计时"""
        _timing_state['enabled'] = False
        print("⏱  执行计时已关闭")


def _make_callbacks(ip):
    """创建事件回调"""
    
    def pre_run(info):
        if _timing_state['enabled']:
            ip._timing_start = time.time()
            ip._timing_code = info.raw_cell
    
    def post_run(result):
        if not _timing_state['enabled'] or not hasattr(ip, '_timing_start'):
            return
        elapsed = time.time() - ip._timing_start
        code = getattr(ip, '_timing_code', '')
        if code.strip() and not code.strip().startswith(('%', '!')):
            _timing_state['records'].append({
                'code': code,
                'elapsed': elapsed,
                'success': getattr(result, 'success', True),
            })
            if elapsed > 0.5:
                print(f"  ⏱ [{elapsed:.3f}s]")
    
    return pre_run, post_run


def load_ipython_extension(ip):
    """加载扩展"""
    ip.register_magics(TimingMagics)
    
    pre_cb, post_cb = _make_callbacks(ip)
    ip.events.register('pre_run_cell', pre_cb)
    ip.events.register('post_run_cell', post_cb)
    _timing_state['pre_cb'] = pre_cb
    _timing_state['post_cb'] = post_cb
    
    # 设置自定义编辑器钩子（VS Code 优先）
    import subprocess, sys
    def vscode_hook(self, filename, linenum=None, wait=True):
        cmd = ['code']
        if linenum:
            cmd += ['--goto', f'{filename}:{linenum}']
        else:
            cmd.append(filename)
        try:
            proc = subprocess.Popen(cmd)
            if wait:
                proc.wait()
        except FileNotFoundError:
            from IPython.core.error import TryNext
            raise TryNext()
    
    ip.set_hook('editor', vscode_hook)
    
    print("✅ timing_ext 已加载！%timing_stats 查看统计，%timing_off 关闭")


def unload_ipython_extension(ip):
    """卸载扩展"""
    if _timing_state['pre_cb']:
        ip.events.unregister('pre_run_cell', _timing_state['pre_cb'])
    if _timing_state['post_cb']:
        ip.events.unregister('post_run_cell', _timing_state['post_cb'])
    _timing_state['pre_cb'] = None
    _timing_state['post_cb'] = None
    print("👋 timing_ext 已卸载")
```

**使用：**

```python
%load_ext timing_ext

# 执行一些代码
import math
for i in range(500_000):
    math.sin(i)

# 查看统计
%timing_stats

# 关闭/开启计时
%timing_off
%timing_on

# 卸载
%unload_ext timing_ext
```

### 示例 5：自定义输入转换器

```python
from IPython import get_ipython
from IPython.core.inputtransformer2 import TransformerManager

ip = get_ipython()

# IPython 的输入转换管线由 TransformerManager 管理
# 可以添加自定义的转换逻辑

# 注意：IPython 9.x 的 inputtransformer2 API 主要用于内部，
# 自定义输入转换推荐使用 startup 文件或扩展中的预处理
# 以下展示如何在代码层面处理输入

# 示例：在 startup 文件中自动给特定命令添加前缀
# ~/.ipython/profile_default/startup/00-input-hooks.py

from IPython import get_ipython

def auto_pdb_transform(line):
    """一个简单的输入转换示例（概念演示）
    
    实际的输入转换器需要通过 TransformerManager 注册，
    但对于简单需求，可以使用 pre_run_cell 事件修改输入
    """
    return line

# 通过事件模拟简单的输入预处理
_shorthand_map = {
    'll': 'ls -la',
    'gs': 'git status',
    'gc': 'git commit',
}

def expand_shorthand(info):
    """展开命令缩写（在执行前）"""
    raw = info.raw_cell.strip()
    if raw in _shorthand_map:
        # 注意：pre_run_cell 不能修改输入，
        # 但可以通过 magics_manager 注册别名来实现
        pass

# 更实用的方式：使用别名系统实现缩写
ip = get_ipython()
for shorthand, full_cmd in _shorthand_map.items():
    try:
        ip.magics_manager.magics['line']['alias'](f'{shorthand} {full_cmd}')
    except Exception:
        pass

print("✅ 缩写已注册: ll, gs, gc")
```

### 示例 6：使用 IPython.embed() 嵌入调试

```python
#!/usr/bin/env python
"""IPython.embed() 嵌入式调试完整示例

embed() 可以在任意 Python 代码中嵌入交互式 IPython 会话，
非常适合调试、数据探索和快速实验。
"""

from IPython import embed
import math
import random


def analyze_data(data):
    """数据分析函数，在关键步骤嵌入 IPython 检查状态"""
    
    # 步骤 1：预处理
    cleaned = [x for x in data if x is not None]
    print(f"预处理后: {len(cleaned)} 个数据点")
    
    # 在这嵌入 IPython，可以检查 data, cleaned 等变量
    # embed()  # 取消注释启用
    
    # 步骤 2：计算统计量
    mean = sum(cleaned) / len(cleaned)
    variance = sum((x - mean) ** 2 for x in cleaned) / len(cleaned)
    std_dev = math.sqrt(variance)
    
    # 步骤 3：异常检测（如果标准差过大，嵌入调试）
    if std_dev > 100:
        print("⚠️  标准差异常大，进入调试模式...")
        embed(
            header="=== 调试模式 ===\n可用变量: data, cleaned, mean, variance, std_dev\n输入 exit() 继续执行",
            colors='neutral',
        )
    
    return {
        'mean': mean,
        'std_dev': std_dev,
        'min': min(cleaned),
        'max': max(cleaned),
        'count': len(cleaned),
    }


def process_with_breakpoints(items):
    """带条件断点的处理函数"""
    results = []
    for i, item in enumerate(items):
        processed = item * 2 + random.gauss(0, 10)
        results.append(processed)
        
        # 在特定条件下嵌入调试
        if abs(processed) > 50:
            print(f"\n🔍 检测到异常值（索引 {i}）：{processed:.2f}")
            embed(
                header=f"调试断点 at item[{i}] = {item} -> {processed:.2f}",
                local_ns=locals(),  # 传入局部变量
            )
    
    return results


# ===== embed() 与 start_ipython() 的区别 =====
#
# embed():
#   - 在当前调用栈中嵌入，可以访问局部变量
#   - 跳过配置文件和完整 startup 流程
#   - 适合调试和数据探索
#   - 退出后继续执行后续代码
#
# start_ipython():
#   - 启动全新的独立 IPython 实例
#   - 执行完整初始化（配置、startup 文件、扩展）
#   - 等价于命令行 `ipython`
#   - 退出后不返回调用点

# 运行示例
if __name__ == '__main__':
    # 示例 1：简单数据
    data = [random.gauss(50, 30) for _ in range(20)]
    data[5] = None  # 添加一个 None 值
    stats = analyze_data(data)
    print(f"统计结果: {stats}")
    
    # 示例 2：处理数据（可能触发断点）
    items = list(range(30))
    results = process_with_breakpoints(items)
    print(f"处理完成，共 {len(results)} 个结果")


# ===== embed() 常用参数 =====
#
# embed(header=None)      嵌入前显示的标题文字
# embed(colors='neutral') 颜色方案
# embed(user_ns={...})    额外注入的命名空间变量
# embed(local_ns=locals())指定局部变量作用域
# embed(verbose=False)    是否显示详细信息
# embed(global_ns=...)    全局命名空间
```

### 示例 7：在扩展中注册 shell_initialized 事件

```python
# 注意：shell_initialized 事件在扩展加载之前触发，
# 所以扩展中注册的 shell_initialized 回调不会被调用。
# 但可以在配置文件或子类中使用。

# 正确使用 shell_initialized 的方式是通过配置文件：
# ~/.ipython/profile_default/ipython_config.py

"""
c = get_config()

# 通过 exec_lines 在启动时注册 shell_initialized 回调
# 注意：exec_lines 执行时 shell 已经初始化，
# 所以 shell_initialized 事件已触发过了
# 直接在 exec_lines 中执行初始化代码即可

c.InteractiveShellApp.exec_lines = [
    # 启动时自动导入常用模块
    "import os, sys, math, json",
    "from pathlib import Path",
    # 设置自定义选项
    "%autoreload 2",
]
"""

# 在 startup 文件中使用 shell_initialized 也是可以的
# 但 startup 文件本身就在 shell 初始化之后执行，
# 所以可以直接执行初始化代码，不需要监听 shell_initialized
```

### 示例 8：事件与钩子选择指南

```python
from IPython import get_ipython
ip = get_ipython()

# ===== 何时使用 Events =====
# Events 适合"通知我发生了什么"的场景：
# - 日志记录（谁在什么时候执行了什么代码）
# - 计时统计（每段代码执行多久）
# - 自动保存（每次执行后保存工作）
# - 通知回调（执行成功/失败时发送通知）
# - 副作用操作（更新 UI、写审计日志）

# 示例：自动保存执行历史到文件
def autosave_history():
    """每次执行后保存历史到文件"""
    import json, os
    history_file = os.path.expanduser('~/.ipython/autosave_history.json')
    try:
        hist = list(ip.history_manager.get_range())
        with open(history_file, 'w') as f:
            json.dump([h for _, _, h in hist[-100:]], f, indent=2)
    except Exception:
        pass  # 自动保存不应影响正常使用

ip.events.register('post_execute', autosave_history)


# ===== 何时使用 Hooks =====
# Hooks 适合"让我来处理这件事"的场景：
# - 替换默认编辑器（%edit 用什么编辑器打开）
# - 自定义分页器（长文本怎么显示）
# - 自定义剪贴板访问（从哪里读取剪贴板）
# - 同步到外部编辑器（IDE 集成）

# 示例：自定义分页器使用 bat 或 less
def custom_pager(self, data, start, screen_lines):
    """使用系统分页器"""
    import subprocess, tempfile, os
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(data)
            tmpname = f.name
        try:
            pager = os.environ.get('PAGER', 'less')
            subprocess.run([pager, tmpname])
        finally:
            os.unlink(tmpname)
    except Exception:
        from IPython.core.error import TryNext
        raise TryNext()

# ip.set_hook('show_in_pager', custom_pager)


# ===== 何时使用 Magics =====
# Magics 适合"添加新的交互命令"：
# - %xxx 执行某个操作
# - %%xxx 处理一段代码
# 参见 04-custom-magic.md 和 02-using-magics.md


# ===== 何时使用 Extensions =====
# Extensions 适合"打包分发功能组合"：
# - 同时注册 magics + events + hooks + formatters
# - 需要可加载/可卸载
# - 需要分享给团队或发布到 PyPI
# 参见 05-extension-basics.md
```

## 代码解析

### 事件系统（EventManager）

事件系统基于观察者模式实现 [F-360]，由 `EventManager` 类管理，实例化为 `shell.events` 属性。

**预定义事件** [F-367]：

| 事件 | 回调签名 | 触发时机 |
|------|---------|---------|
| `pre_execute` | `() -> None` | 每次执行前（含静默执行、widget 消息） |
| `pre_run_cell` | `(info: ExecutionInfo) -> None` | 用户代码执行前 |
| `post_execute` | `() -> None` | 每次执行后 |
| `post_run_cell` | `(result: ExecutionResult) -> None` | 用户代码执行后 |
| `shell_initialized` | `(ip: InteractiveShell) -> None` | Shell 完全初始化后 |

**事件触发时序** [F-367]：

```
shell_initialized(ip)  ← Shell 初始化完成（扩展加载前）
  │
  ├── 加载扩展、执行 startup 文件
  │
  └── REPL 主循环:
        pre_execute()
        pre_run_cell(info)
          └── 执行代码
        post_execute()
        post_run_cell(result)
```

**关键注意事项** [F-364 源码]：
- 事件回调中的异常会被 `EventManager.trigger()` 捕获，打印警告但不中断执行
- 同一事件可注册多个回调，按注册顺序调用
- 回调应该快速执行（避免阻塞 REPL）
- 回调不应修改参数对象（共享给所有回调）
- `shell_initialized` 在扩展加载前触发，扩展中注册的回调不会被调用

### Hooks 钩子系统

Hooks 是设计给用户覆盖的单函数定制点 [F-370]，由 `shell.hooks` 管理，通过 `shell.set_hook(name, hook)` 设置。

**内置 Hooks** [F-371]：

| Hook 名 | 默认行为 | 用途 |
|---------|---------|------|
| `editor` | 读取 `$EDITOR` 环境变量 | `%edit` 魔法使用的编辑器 |
| `synchronize_with_editor` | 空操作 | IDE 集成通知 |
| `show_in_pager` | 抛 TryNext 使用内置分页器 | 长文本分页显示 |
| `clipboard_get` | 平台检测链（win32/osx/wayland/tkinter） | 读取剪贴板内容 |

### CommandChainDispatcher 职责链

`CommandChainDispatcher` 实现职责链模式 [F-372]，用于需要多个候选处理器的 hook（如 `clipboard_get`）：

- 链中的函数按优先级排序（数值越小优先级越高）
- 每个函数尝试处理，成功则返回结果
- 无法处理时抛 `TryNext()` 异常，让链中下一个函数尝试 [F-495]
- 所有函数都失败则抛出最后一个 `TryNext`

### TryNext 异常

`TryNext` 是 hooks 系统中的控制流异常 [F-495]，用于在职责链中传递控制权给下一个处理器。在自定义 hook 中：
- 如果能处理，直接返回结果
- 如果不能处理（如编辑器未安装、剪贴板不可用），抛 `TryNext()`

### IPython.embed()

`embed()` 函数在当前调用栈中嵌入 IPython 交互式会话 [F-007][F-008]：

- 通过 `__getattr__` 延迟导入 `IPython.terminal.embed` 模块
- 可以访问嵌入点的局部变量和全局变量
- 退出后继续执行后续代码
- 支持 `header`、`colors`、`user_ns` 等参数
- 跳过配置文件和 startup 文件的加载（快速启动）

### Events vs Hooks vs Magics vs Extensions 决策指南

| 需求 | 使用机制 | 原因 |
|------|---------|------|
| 添加新的交互命令 | Magics | 用户主动调用，有明确语法 |
| 监听执行生命周期 | Events | 多观察者，互不干扰，异常不中断 |
| 替换默认行为 | Hooks | 单职责点，支持链/覆盖 |
| 打包分发功能组合 | Extensions | 可加载/卸载，组合多种机制 |

## 常见问题排查

**问题：注册了 `shell_initialized` 事件回调但从未被调用**

原因：`shell_initialized` 在扩展加载和 startup 文件执行之前就已经触发了 [F-367]。在扩展或 startup 文件中注册此事件为时已晚。

解决方案：
- 如果需要在 Shell 初始化时执行代码，直接在 startup 文件中编写代码（startup 文件本身就在初始化后执行）
- 如果需要更早期的定制，通过配置文件 `ipython_config.py` 的 `exec_lines` 或创建自定义 Shell 子类
- 使用 `pre_run_cell` 或 `pre_execute` 作为替代（在每次执行前触发）

**问题：事件回调中抛出异常导致 IPython 行为异常**

原因：虽然 `EventManager.trigger()` 会捕获异常并打印警告，但如果回调中有资源泄漏（如未关闭的文件），仍可能造成问题。

解决方案：
- 在事件回调内部使用 `try/except` 保护关键代码
- 回调应该快速、安全、无副作用地完成
- 使用 `try/finally` 确保资源清理

**问题：自定义 editor hook 在 `%edit` 时不生效**

原因：可能是 hook 函数的签名不正确，或者在某些平台上 `$EDITOR` 环境变量优先。

解决方案：
- 确保 hook 函数接受 `(self, filename, linenum=None, wait=True)` 参数
- hook 是绑定方法，第一个参数 `self` 是 Shell 实例
- 检查是否有其他配置覆盖了 editor hook
- 如果编辑器命令可能不存在，使用 `TryNext` 回退到默认

**问题：`embed()` 嵌入后无法访问某些局部变量**

原因：`embed()` 默认提取调用帧的局部变量，但在某些情况下（如 Cython 函数、优化帧）可能无法正确获取。

解决方案：
- 显式传递 `local_ns=locals()` 参数
- 或使用 `user_ns={'var1': var1, 'var2': var2}` 显式注入需要的变量
- 确保在纯 Python 函数中调用 `embed()`（非 C 扩展或内建函数）

**问题：事件回调中执行代码导致递归调用**

原因：在 `pre_run_cell`/`post_run_cell` 回调中调用 `shell.run_cell()` 或 `shell.ex()` 会再次触发事件，导致无限递归。

解决方案：
- 避免在事件回调中执行代码
- 如果必须执行，使用 `shell.ex()` 配合一个标志位防止递归：
  ```python
  _in_callback = False
  def post_run(result):
      global _in_callback
      if _in_callback:
          return
      _in_callback = True
      try:
          ip.ex("print('auto cleanup')")
      finally:
          _in_callback = False
  ```

**问题：`CommandChainDispatcher` 添加 hook 后原有 hook 不再工作**

原因：创建新的 `CommandChainDispatcher` 时没有将原有 hook 添加到链中。

解决方案：将原有 hook 作为最低优先级添加到链中：
```python
chain = CommandChainDispatcher()
chain.add(my_hook, priority=0)
chain.add(ip.hooks.clipboard_get, priority=100)  # 保留原 hook 作为后备
ip.set_hook('clipboard_get', chain)
```

## 相关概念

- [事件与钩子](../concepts/10-events-hooks.md)
- [扩展系统](../concepts/09-extension-system.md)
- [Shell 生命周期](../concepts/03-shell-lifecycle.md)
- [魔法命令系统](../concepts/04-magic-system.md)
- [自定义魔法开发](../concepts/11-custom-magics.md)
- [快速开始](../concepts/01-getting-started.md)
- [信源参考 - 事件与钩子](../references/events-hooks-source.md)
