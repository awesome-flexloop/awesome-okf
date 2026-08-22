---
type: example
title: "05 - IPython 扩展开发"
description: 编写可加载/卸载的 IPython 扩展，包括扩展入口协议、魔法注册、事件绑定、autoreload 使用，以及 pip 可安装扩展的打包方法
tags: [example, extension, load_ext, unload_ext, autoreload, plugin, packaging]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-extensions
    title: IPython/core/extensions.py
  - id: ipython-ext-autoreload
    title: IPython/extensions/autoreload.py
  - id: ipython-magic
    title: IPython/core/magic.py
related_concepts: [/concepts/09-extension-system.md, /concepts/10-events-hooks.md, /concepts/11-custom-magics.md]
---

## 目标

本示例演示如何开发 IPython 扩展（Extension），覆盖以下内容：

1. 扩展的基本结构：`load_ipython_extension(ip)` 和 `unload_ipython_extension(ip)` 入口函数
2. 在扩展中注册魔法命令、事件回调和钩子
3. 使用内置 `autoreload` 扩展自动重载修改的模块
4. 通过 `%load_ext`、`%unload_ext`、`%reload_ext` 管理扩展生命周期
5. 创建可通过 pip 安装的分发扩展
6. 理解扩展与 startup 脚本、魔法模块的区别

## 完整代码

### 示例 1：最小可用扩展

将以下代码保存为 `hello_ext.py`：

```python
# hello_ext.py —— 最简单的 IPython 扩展
"""一个最简 IPython 扩展示例

加载方式:
    %load_ext hello_ext
"""

from IPython.core.magic import Magics, magics_class, line_magic


@magics_class
class HelloMagics(Magics):
    """问候相关魔法"""
    
    @line_magic
    def hello(self, line):
        """问候魔法
        
        用法: %hello [name]
        """
        name = line.strip() or "World"
        print(f"Hello, {name}! 来自扩展的问候 🎉")
    
    @line_magic
    def goodbye(self, line):
        """告别魔法"""
        print("Goodbye! 👋")


def load_ipython_extension(ipython):
    """扩展加载入口 —— 必须实现此函数
    
    Parameters
    ----------
    ipython : InteractiveShell
        当前 IPython Shell 实例
    """
    ipython.register_magics(HelloMagics)
    print("✅ hello_ext 已加载！使用 %hello 和 %goodbye")


def unload_ipython_extension(ipython):
    """扩展卸载入口 —— 可选但推荐
    
    在此清理扩展注册的资源。
    """
    # 注意：注销魔法需要手动从 magics_manager 中移除
    # 简单扩展可以不做清理，但好的扩展应该做
    print("👋 hello_ext 已卸载")
```

**在 IPython 中使用：**

```python
%load_ext hello_ext
%hello
%hello Alice
%goodbye
%unload_ext hello_ext
```

### 示例 2：组合魔法 + 事件 + 钩子的完整扩展

将以下代码保存为 `devtools_ext.py`：

```python
# devtools_ext.py —— 开发工具扩展
"""一个开发工具扩展，组合魔法、事件和钩子

功能:
- %timer_stats: 显示代码执行时间统计
- %%profile: 简单性能分析（基于 time）
- 自动记录每次执行的时间
- 自定义编辑器钩子（使用 VS Code）
- 自动导入常用模块

加载方式:
    %load_ext devtools_ext
配置:
    # 在 ipython_config.py 中设置自动加载
    c.InteractiveShellApp.extensions = ['devtools_ext']
"""

import time
import sys
import os
from IPython.core.magic import (
    Magics, magics_class, line_magic, cell_magic,
    needs_local_scope, no_var_expand, line_cell_magic,
)
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring,
)


# ===== 全局状态（扩展实例级） =====

_extension_state = {
    'exec_times': [],      # (cell_code_start, elapsed_time) 列表
    'callbacks_registered': False,
    'pre_run_cb': None,
    'post_run_cb': None,
    'shell': None,
}


@magics_class
class DevToolsMagics(Magics):
    """开发工具魔法集合"""
    
    @line_magic
    def timer_stats(self, line):
        """显示执行时间统计
        
        用法:
            %timer_stats          # 显示所有统计
            %timer_stats --clear  # 清除统计数据
            %timer_stats -n 5     # 显示最近 5 条
        """
        times = _extension_state['exec_times']
        if not times:
            print("尚无计时数据。执行一些代码后再试。")
            return
        
        if '--clear' in line:
            _extension_state['exec_times'].clear()
            print("✅ 统计数据已清除")
            return
        
        # 解析 -n 参数
        count = None
        if '-n' in line:
            parts = line.split()
            try:
                idx = parts.index('-n')
                count = int(parts[idx + 1])
            except (ValueError, IndexError):
                pass
        
        display_times = times[-count:] if count else times
        
        print(f"=== 执行时间统计（共 {len(display_times)} 条记录）===")
        elapsed_list = [t for _, t in display_times]
        avg = sum(elapsed_list) / len(elapsed_list)
        print(f"平均: {avg:.4f}s")
        print(f"最快: {min(elapsed_list):.4f}s")
        print(f"最慢: {max(elapsed_list):.4f}s")
        print(f"总计: {sum(elapsed_list):.4f}s")
        print()
        for i, (code, elapsed) in enumerate(display_times[-10:], 1):
            code_preview = code[:50].replace('\n', '↵') + ('...' if len(code) > 50 else '')
            print(f"  {i:2d}. [{elapsed:.4f}s] {code_preview}")
    
    @no_var_expand
    @line_cell_magic
    def profile(self, line, cell=None):
        """简单性能分析魔法
        
        用法:
            %profile <expression>        # 分析单行
            %%profile [label]            # 分析整个代码块
            <code>
        """
        import timeit
        
        if cell is None:
            # 行模式
            code = line.strip()
            if not code:
                print("用法: %profile <expression>")
                return
            
            # 使用 timeit 运行
            number = 1000
            try:
                timer = timeit.Timer(
                    code,
                    globals=self.shell.user_ns,
                )
                # 自动选择循环次数
                number, _ = timer.autorange()
                times = timer.repeat(repeat=3, number=number)
                best = min(times) / number * 1e6
                print(f"⏱  最佳: {best:.2f} µs（{number} 次循环，3 轮重复）")
            except Exception as e:
                print(f"执行错误: {e}")
        else:
            # 单元模式
            label = line.strip() or "Code Block"
            start = time.time()
            self.shell.run_cell(cell)
            elapsed = time.time() - start
            print(f"⏱  {label}: {elapsed:.4f}s")
    
    @magic_arguments()
    @argument('modules', nargs='+', help='要自动导入的模块名')
    @line_magic
    def autoimport(self, line):
        """导入模块并添加到全局命名空间
        
        用法:
            %autoimport os sys json
            %autoimport numpy as np pandas as pd
        
        注意：简单实现，不支持 'as' 别名（使用标准 import 语法）
        """
        import importlib
        args = parse_argstring(self.autoimport, line)
        for mod_name in args.modules:
            try:
                mod = importlib.import_module(mod_name)
                self.shell.user_ns[mod_name] = mod
                print(f"✅ import {mod_name}")
            except ImportError as e:
                print(f"❌ 无法导入 {mod_name}: {e}")
    
    @line_magic
    def whereami(self, line):
        """显示当前工作目录和文件信息"""
        cwd = os.getcwd()
        print(f"📍 当前目录: {cwd}")
        if line.strip():
            target = line.strip()
            path = os.path.join(cwd, target)
            if os.path.exists(path):
                print(f"   存在: {path}")
                print(f"   大小: {os.path.getsize(path)} bytes")
            else:
                print(f"   不存在: {path}")


def _register_event_callbacks(ip):
    """注册事件回调"""
    if _extension_state['callbacks_registered']:
        return
    
    def pre_run_callback(info):
        """代码执行前记录开始时间"""
        _extension_state['_start_time'] = time.time()
        _extension_state['_current_code'] = info.raw_cell
    
    def post_run_callback(result):
        """代码执行后记录耗时"""
        if hasattr(_extension_state, '_start_time'):
            start = _extension_state.get('_start_time', time.time())
            elapsed = time.time() - start
            code = _extension_state.get('_current_code', '')
            # 只记录非空、非魔法的代码
            code_stripped = code.strip()
            if code_stripped and not code_stripped.startswith(('%', '!')):
                _extension_state['exec_times'].append((code, elapsed))
    
    ip.events.register('pre_run_cell', pre_run_callback)
    ip.events.register('post_run_cell', post_run_callback)
    
    _extension_state['pre_run_cb'] = pre_run_callback
    _extension_state['post_run_cb'] = post_run_callback
    _extension_state['callbacks_registered'] = True


def _unregister_event_callbacks(ip):
    """注销事件回调"""
    if not _extension_state['callbacks_registered']:
        return
    
    if _extension_state['pre_run_cb']:
        ip.events.unregister('pre_run_cell', _extension_state['pre_run_cb'])
    if _extension_state['post_run_cb']:
        ip.events.unregister('post_run_cell', _extension_state['post_run_cb'])
    
    _extension_state['pre_run_cb'] = None
    _extension_state['post_run_cb'] = None
    _extension_state['callbacks_registered'] = False


def _setup_editor_hook(ip):
    """设置编辑器钩子（使用 VS Code，如果可用）"""
    def vscode_editor(self_hook, filename, linenum=None, wait=True):
        import subprocess
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
            # VS Code 未安装，跳过
            print("（VS Code 未找到，使用默认编辑器）")
            from IPython.core.error import TryNext
            raise TryNext()
    
    ip.set_hook('editor', vscode_editor)


def load_ipython_extension(ipython):
    """加载扩展"""
    _extension_state['shell'] = ipython
    
    # 1. 注册魔法
    ipython.register_magics(DevToolsMagics)
    
    # 2. 注册事件回调（自动计时）
    _register_event_callbacks(ipython)
    
    # 3. 设置编辑器钩子
    _setup_editor_hook(ipython)
    
    print("✅ devtools_ext 已加载！")
    print("   可用魔法: %timer_stats, %%profile, %autoimport, %whereami")
    print("   事件: 自动记录每次执行时间")
    print("   钩子: 编辑器设为 VS Code")


def unload_ipython_extension(ipython):
    """卸载扩展"""
    # 清理事件回调
    _unregister_event_callbacks(ipython)
    
    # 注意：注销魔法比较复杂，因为 MagicsManager 没有提供 unregister API
    # 简单方案是接受魔法残留（不影响功能）
    # 完整方案需要手动从 magics_manager.magics 中移除
    
    _extension_state['shell'] = None
    print("👋 devtools_ext 已卸载（事件已清理，魔法可能仍可用直到重启）")
```

**使用示例（在 IPython 中运行）：**

```python
# 加载扩展
%load_ext devtools_ext

# 执行一些代码（会被自动计时）
import math
for i in range(100):
    math.sqrt(i)

total = sum(range(1_000_000))

# 查看统计
%timer_stats

# 使用 %profile
%profile sum(range(10000))

# 使用 %%profile
%%profile 数据处理
data = list(range(100_000))
result = [x**2 for x in data if x % 2 == 0]
print(f"处理了 {len(result)} 个偶数")

# 使用 %autoimport
%autoimport json os
json.dumps({"hello": "world"})
os.getcwd()

# 使用 %whereami
%whereami
%whereami devtools_ext.py

# 重载扩展（开发时很有用）
%reload_ext devtools_ext

# 卸载扩展
%unload_ext devtools_ext
```

### 示例 3：使用内置 autoreload 扩展

`autoreload` 是 IPython 自带的扩展，自动重新加载磁盘上已修改的模块，开发时非常有用：

```python
# ===== autoreload 扩展使用演示 =====

# 1. 加载 autoreload 扩展
%load_ext autoreload

# 2. 设置自动重载模式
%autoreload 2   # 模式 2：每次执行前自动重载所有模块（推荐开发模式）
# %autoreload 1  # 模式 1：只重载用 %aimport 标记的模块
# %autoreload 0  # 关闭自动重载

# 3. 演示（假设你有一个 mymodule.py 文件）
# mymodule.py 内容:
#   def greet():
#       return "Hello v1"

import mymodule
mymodule.greet()
# Out: "Hello v1"

# 现在修改 mymodule.py 将 "Hello v1" 改为 "Hello v2"，保存文件
# 不需要重启 IPython，直接调用：
mymodule.greet()
# Out: "Hello v2"  （自动重载了！）

# 4. 使用 %aimport 精确控制
%aimport mymodule        # 标记 mymodule 为自动重载（模式 1 需要）
%aimport -mymodule       # 排除 mymodule 不重载
%aimport                # 列出所有模块的自动重载状态

# 5. 在配置文件中设置自动加载（推荐）
# 编辑 ~/.ipython/profile_default/ipython_config.py:
# c = get_config()
# c.InteractiveShellApp.extensions = ['autoreload']
# c.InteractiveShellApp.exec_lines = ['%autoreload 2']
```

### 示例 4：可 pip 安装的扩展包结构

创建可分发的 IPython 扩展包，目录结构：

```
my_ipython_ext/
├── pyproject.toml
├── README.md
└── my_ipython_ext/
    ├── __init__.py
    ├── magics.py
    └── _version.py
```

**`my_ipython_ext/magics.py`：**

```python
# my_ipython_ext/magics.py
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic


@magics_class
class MyPackageMagics(Magics):
    """我的扩展包提供的魔法"""
    
    @line_magic
    def myecho(self, line):
        """回显输入
        
        用法: %myecho <text>
        """
        print(f"ECHO: {line}")


def load_ipython_extension(ipython):
    ipython.register_magics(MyPackageMagics)
    print("my_ipython_ext loaded. Use %myecho.")


def unload_ipython_extension(ipython):
    print("my_ipython_ext unloaded.")
```

**`my_ipython_ext/__init__.py`：**

```python
# my_ipython_ext/__init__.py
from ._version import __version__
```

**`pyproject.toml`：**

```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-ipython-ext"
version = "0.1.0"
description = "My custom IPython extension"
requires-python = ">=3.9"
dependencies = [
    "ipython>=8.0",
]

[project.entry-points."ipython_extensions"]
# 通过 entry point 声明扩展，用户无需知道模块路径
my_ext = "my_ipython_ext.magics:load_ipython_extension"
```

安装后即可使用：

```bash
pip install -e .  # 开发模式安装
```

```python
# IPython 中
%load_ext my_ipython_ext.magics
%myecho Hello from installed extension!
```

### 示例 5：扩展 vs Startup 脚本 vs 魔法模块对比

```python
# ===== 三种定制方式对比 =====

# === 方式 A: Startup 脚本 ===
# 位置: ~/.ipython/profile_default/startup/NN-name.py
# 特点: IPython 启动时自动执行，适合简单的变量设置和魔法注册
# 示例内容:
"""
from IPython.core.magic import register_line_magic
import os, sys

@register_line_magic
def cwd(line):
    print(os.getcwd())

sys.path.insert(0, '/my/dev/path')
"""

# === 方式 B: 魔法模块（可 %load_ext 加载的 .py 文件） ===
# 位置: 任何 Python 路径上的 .py 文件
# 特点: 需要手动 %load_ext 加载，有 load/unload 入口，可分发给他人
# 示例: 见示例 1 和 2

# === 方式 C: pip 可安装扩展包 ===
# 位置: site-packages（pip 安装）
# 特点: 可通过 pip 分发，有版本管理，适合团队共享或发布
# 示例: 见示例 4

# === 选择指南 ===
# - 临时/个人使用 → Startup 脚本
# - 项目级别共享 → 魔法模块（放在项目目录）
# - 团队/发布 → pip 可安装扩展包
```

### 示例 6：编程方式管理扩展

```python
# 除了魔法命令，也可以通过 Python API 管理扩展
from IPython import get_ipython

ip = get_ipython()

# 加载扩展
ip.extension_manager.load_extension('autoreload')

# 检查已加载的扩展
print("已加载扩展:", ip.extension_manager.loaded)

# 重新加载扩展
ip.extension_manager.reload_extension('autoreload')

# 卸载扩展
ip.extension_manager.unload_extension('autoreload')

# 在 startup 脚本中编程加载扩展（不使用魔法命令）
# ~/.ipython/profile_default/startup/00-setup.py
# ip = get_ipython()
# if ip is not None:
#     ip.extension_manager.load_extension('autoreload')
#     ip.run_line_magic('autoreload', '2')
```

## 代码解析

### ExtensionManager 扩展管理器

扩展由 `ExtensionManager` 统一管理 [F-430]，在 `InteractiveShell.init_extension_manager()` 中创建为 `shell.extension_manager`。它维护一个 `loaded` 集合记录已加载的扩展模块名 [F-430]。

### 加载流程

`%load_ext module_name` 的执行流程 [F-431][F-434]：

```
%load_ext my_ext
  → ExtensionManager.load_extension("my_ext")
    → 1. import my_ext（如果尚未导入）
    → 2. 检查模块是否有 load_ipython_extension 函数
    → 3. 调用 my_ext.load_ipython_extension(ip)
    → 4. 将 "my_ext" 加入 loaded 集合
```

卸载流程 [F-432][F-435]：
```
%unload_ext my_ext
  → ExtensionManager.unload_extension("my_ext")
    → 1. 检查是否已加载
    → 2. 如果有 unload_ipython_extension，调用之
    → 3. 从 loaded 集合移除
```

`%reload_ext` 先调用 `unload_extension` 再调用 `load_extension` [F-433]。

### 扩展入口协议

扩展是一个普通 Python 模块，必须实现 [F-434]：

```python
def load_ipython_extension(ipython):
    """加载入口，接收 InteractiveShell 实例
    
    在此函数中可以:
    - 注册魔法: ipython.register_magics(MyMagics)
    - 注册事件: ipython.events.register('post_run_cell', callback)
    - 设置钩子: ipython.set_hook('editor', my_editor)
    - 注册 formatter: ipython.display_formatter.formatters['text/html'].for_type(...)
    - 修改配置: ipython.config 相关设置
    - 执行任意 Python 代码
    """
```

可选实现 [F-435]：

```python
def unload_ipython_extension(ipython):
    """卸载入口，清理资源
    
    - 注销事件回调（必须手动 unregister）
    - 恢复被修改的钩子
    - 注意：魔法的注销比较复杂，MagicsManager 没有官方 unregister API
    """
```

### autoreload 工作原理

`autoreload` 扩展通过 `pre_execute` 事件在每次代码执行前检查已导入模块的修改时间 [F-520]。如果 `.py` 文件的修改时间晚于导入时间，自动调用 `importlib.reload()` 重载模块。三种模式：

| 模式 | 行为 |
|------|------|
| 0 | 禁用自动重载 |
| 1 | 只重载 `%aimport` 标记的模块 |
| 2 | 重载所有模块（除了 `%aimport -module` 排除的）|

### 扩展安全注意事项

扩展执行任意 Python 代码 [F-430 相关洞察]：
- `load_ipython_extension(ipython)` 可以读写文件系统、修改 sys.path、执行系统命令
- 只加载来自可信来源的扩展
- `%load_ext` 等价于 `import 模块` + 执行入口函数
- startup 目录中的脚本和配置文件中的 extensions 列表同样有代码执行风险

### 注册多个自定义项

一个扩展可以同时注册多种定制：

| 定制类型 | API | 说明 |
|---------|-----|------|
| 魔法 | `ip.register_magics(MyMagics)` | 添加 `%`/`%%` 命令 |
| 事件 | `ip.events.register(event, cb)` | 监听生命周期回调 |
| 钩子 | `ip.set_hook(name, hook)` | 替换默认行为 |
| Formatter | `ip.display_formatter.formatters[mime].for_type(cls, func)` | 注册自定义类型格式化 |

## 常见问题排查

**问题：`%load_ext my_ext` 报错 "No module named 'my_ext'"**

原因：扩展模块不在 Python 搜索路径中。

解决方案：
- 将 `.py` 文件放在当前工作目录（`%pwd`）
- 或放到 `~/.ipython/extensions/` 目录（IPython 自动将此目录加入 sys.path）
- 或在 startup 脚本中添加 `sys.path.insert(0, '/path/to/dir')`
- 或通过 pip 安装（见示例 4）

**问题：`%unload_ext` 后魔法命令仍然可用**

原因：IPython 的 `MagicsManager` 没有提供官方的 `unregister()` API，卸载扩展时不会自动移除已注册的魔法 [F-305 源码]。

解决方案：
- 对于开发场景，使用 `%reload_ext` 重新加载（旧魔法会被同名覆盖）
- 在 `unload_ipython_extension` 中手动清理：
  ```python
  def unload_ipython_extension(ip):
      mm = ip.magics_manager
      for magic_name in ['my_magic1', 'my_magic2']:
          if magic_name in mm.magics['line']:
              del mm.magics['line'][magic_name]
  ```
- 完全清理需要重启 IPython

**问题：autoreload 无法正确重载某些模块**

原因：`autoreload` 有一些限制，不能正确处理以下情况：
- 替换类定义后，已有实例不会更新为新类
- C 扩展模块（如 numpy 的 .so/.pyd）无法重载
- 修改了 `__init__.py` 中的导入可能不生效
- 函数签名变更可能导致旧引用失效

解决方案：
- 对于类修改，重新创建实例
- 对于 C 扩展，需要重启 IPython
- 遇到问题时使用 `%autoreload 0` 临时关闭，手动重新导入

**问题：扩展加载时报错但没有详细信息**

原因：扩展加载时的异常被 ExtensionManager 捕获，可能只显示简单的错误信息。

解决方案：
- 使用 `%reload_ext` 查看完整 traceback
- 手动 `import my_ext; my_ext.load_ipython_extension(get_ipython())` 可以获得完整错误
- 启动时加 `--debug` 标志查看详细加载日志

**问题：pip 安装的扩展 `%load_ext` 找不到**

原因：entry points 声明方式不正确，或者包名与模块名不匹配。

解决方案：
- 确认 `pyproject.toml` 中 `[project.entry-points."ipython_extensions"]` 格式正确
- 尝试使用完整模块路径加载：`%load_ext my_package.my_module`
- 验证包已正确安装：`pip show my-ipython-ext`

## 相关概念

- [扩展系统](/concepts/09-extension-system.md)
- [事件与钩子](/concepts/10-events-hooks.md)
- [自定义魔法开发](/concepts/11-custom-magics.md)
- [魔法命令系统](/concepts/04-magic-system.md)
- [Shell 生命周期](/concepts/03-shell-lifecycle.md)
- [信源参考 - 扩展系统](/references/extension-source.md)
