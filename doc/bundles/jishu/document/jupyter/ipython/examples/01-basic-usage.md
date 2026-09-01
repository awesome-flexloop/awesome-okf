---
type: example
title: "01 - IPython 基本使用"
description: 从零开始安装、启动 IPython 终端，掌握基础表达式、In/Out 变量、快捷键、帮助查询和启动参数的完整入门示例
tags: [example, basic, getting-started, installation, repl, shortcuts, help]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-terminal-app
    title: IPython/terminal/ipapp.py
  - id: ipython-interactiveshell
    title: IPython/core/interactiveshell.py
  - id: ipython-oinspect
    title: IPython/core/oinspect.py
related_concepts: [/concepts/00-introduction.md, /concepts/01-getting-started.md, /concepts/08-completer-history.md]
---

## 目标

本示例演示如何从零开始使用 IPython 终端，完成以下核心任务：

1. 安装 IPython 并从命令行启动
2. 熟悉 `In [N]:` / `Out[N]:` 提示符和历史变量（`_`、`__`、`___`）
3. 使用 Tab 补全、历史回溯等常用键盘快捷键
4. 通过 `?` 和 `??` 获取对象帮助和源码
5. 使用 `--classic`、`--no-banner`、`--quick` 等启动参数
6. 正确退出 IPython 会话

## 完整代码

### 1. 安装 IPython

```bash
# 使用 pip 安装 IPython
pip install ipython

# 验证安装
ipython --version
# 输出示例: 9.17.0
```

### 2. 启动 IPython

```bash
# 基本启动
ipython

# 查看所有命令行选项
ipython --help

# 常用启动方式
ipython --classic       # 经典模式：类似标准 Python REPL，无颜色、无 pretty 打印
ipython --no-banner     # 不显示启动横幅
ipython --quick         # 快速启动，跳过配置文件加载
ipython --simple-prompt # 使用简单提示符（禁用 prompt_toolkit）
```

### 3. 第一个 IPython 会话（可直接在 IPython 中逐行运行）

```python
# === 基本表达式 ===
In [1]: 1 + 1
Out[1]: 2

In [2]: print("Hello, IPython!")
Hello, IPython!

In [3]: import math

In [4]: math.sqrt(16)
Out[4]: 4.0

In [5]: x = 42

In [6]: x * 2
Out[6]: 84

# === In/Out 历史变量 ===
# _  是上一个输出结果
In [7]: _
Out[7]: 84

# __ 是倒数第二个输出
In [8]: __
Out[8]: 4.0

# ___ 是倒数第三个输出
In [9]: ___
Out[9]: 2

# In 列表保存所有输入
In [10]: In[1]
Out[10]: '1 + 1'

# Out 字典保存所有有返回值的输出
In [11]: Out[4]
Out[11]: 4.0

# _ih 和 _oh 是 In 和 Out 的别名
In [12]: _ih[2]
Out[12]: 'print("Hello, IPython!")'

# === 获取帮助 ===
# 单个 ? 显示文档字符串
In [13]: math.sqrt?
# Signature: math.sqrt(x, /)
# Docstring: Return the square root of x.
# Type:      builtin_function_or_method

# 双个 ?? 显示源代码（如果可用）
In [14]: import os
In [15]: os.path.join??
# 显示 os.path.join 的 Python 源码

# 通配符搜索
In [16]: math.*sqrt*?
# math.sqrt
# math.isqrt

# === 查看所有可用变量 ===
In [17]: who_ls   # automagic 模式下等价于 %who_ls
Out[17]: ['__', '___', '_dh', '_i', '_i1', '_i10', ..., 'math', 'x']

# === 退出 IPython ===
# 方式 1：输入 exit 或 quit
exit

# 方式 2：按 Ctrl-D（Unix/macOS）或 Ctrl-Z+Enter（Windows）
# 方式 3：使用 %exit 魔法命令
```

### 4. 编程方式启动 IPython（可保存为 .py 文件运行）

```python
#!/usr/bin/env python
"""编程方式启动 IPython 的完整示例"""

from IPython import start_ipython

# 方式 1：最简单——等价于命令行 ipython
# start_ipython()

# 方式 2：带命令行参数启动
# start_ipython(argv=['--classic', '--no-banner'])

# 方式 3：带预定义变量启动
if __name__ == '__main__':
    start_ipython(
        argv=['--no-banner'],
        user_ns={
            'greeting': 'Hello from start_ipython!',
            'data': [1, 2, 3, 4, 5],
        }
    )
```

### 5. 使用 embed() 嵌入调试（可保存为 .py 文件运行）

```python
#!/usr/bin/env python
"""使用 IPython.embed() 在代码中嵌入调试会话"""

from IPython import embed

def process_data(items):
    """处理数据列表，在特定条件下嵌入 IPython 调试"""
    result = []
    for i, item in enumerate(items):
        processed = item * 2
        if processed > 100:
            # 在此处嵌入 IPython，可以访问当前所有局部变量
            print(f"--- Debugging at item {i}, value={item} ---")
            embed(header="Debug session: inspect 'i', 'item', 'processed', 'result'")
        result.append(processed)
    return result

if __name__ == '__main__':
    data = [10, 50, 60, 200]
    output = process_data(data)
    print(f"Final result: {output}")
```

## 代码解析

### 安装与启动

IPython 通过 `pip install ipython` 安装。安装后，`ipython` 命令等价于 `python -m IPython`，因为 `IPython/__main__.py` 从 `IPython` 包导入 `start_ipython` 并调用 [F-005]。`start_ipython()` 进一步调用 `TerminalIPythonApp.launch_new_instance()` 启动完整的终端应用 [F-011]。

### 启动参数

`TerminalIPythonApp` 定义了多个命令行 flags [F-108]：

| 参数 | 作用 | 源码位置 |
|------|------|---------|
| `--classic` | 经典模式，使用 `ClassicPrompts`、禁用颜色、Plain xmode | [F-246] |
| `--no-banner` | 跳过 `init_banner()`，不显示版本横幅 | [F-104] |
| `--quick` | 跳过配置文件加载，加速启动 | [F-108] |
| `--simple-prompt` | 禁用 prompt_toolkit，使用基础 readline 提示符 | [F-242] |

### In/Out 历史变量

IPython 在 `InteractiveShell` 中维护完整的输入输出历史 [F-232]：

- `In` / `_ih`：输入历史列表，`In[N]` 返回第 N 次输入的源代码字符串
- `Out` / `_oh`：输出历史字典，`Out[N]` 返回第 N 次有返回值的输出
- `_`、`__`、`___`：分别是倒数第一、第二、第三个输出结果的快捷引用
- `_iN`：动态变量，`_i1`、`_i2` 等也指向对应输入

这些变量由 `DisplayHook` 在每次表达式求值后自动更新 [F-400][F-401]。

### 帮助系统（? 和 ??）

- `obj?` 调用 `Inspector.pinfo()` 显示对象签名、文档字符串、类型信息 [F-500][F-502]
- `obj??` 调用 `Inspector.pinfo2()`，如果对象是 Python 定义的（非 C 扩展），额外显示源代码
- 通配符 `*pattern*?` 搜索匹配的名称
- 帮助信息由 `OInspect` 模块提供 [F-500]

### exit/quit 的实现

`exit` 和 `quit` 不是内置函数，而是 `ExitAutocall` 实例 [F-233]。在 IPython 中输入 `exit` 时，自动调用实例触发退出，不需要加括号。

### 常用键盘快捷键

在终端 IPython（prompt_toolkit 模式）中：

| 快捷键 | 功能 |
|--------|------|
| `Tab` | 自动补全（变量名、模块属性、文件路径、魔法命令） |
| `↑` / `↓` | 浏览历史命令 |
| `Ctrl-R` | 反向搜索历史 |
| `Ctrl-L` | 清屏 |
| `Ctrl-D` | 退出（若 confirm_exit 开启则需确认）[F-244] |
| `Ctrl-C` | 中断当前执行 |
| `Ctrl-A` / `Ctrl-E` | 移动到行首/行尾 |

补全由 `IPCompleter` 提供 [F-440]，支持 Jedi 语义补全和字典键补全 [F-446]。

## 常见问题排查

**问题：输入 `exit` 后没有退出，而是显示 `<IPython.core.autocall.ExitAutocall object at ...>`**

原因：`exit` 被当作 Python 变量引用而非自动调用。这通常发生在将 `exit` 赋值给了变量或在某些特殊上下文中。

解决方案：使用 `exit()`（加括号）、`quit()`、按 Ctrl-D 或 `%exit` 魔法命令退出。

**问题：Tab 补全不工作或行为异常**

原因：可能是 `--simple-prompt` 模式下禁用了 prompt_toolkit，或 Jedi 补全失败。

解决方案：
- 确认未使用 `--simple-prompt` 参数
- 尝试 `%config IPCompleter.use_jedi = False` 切换到基础补全模式
- 检查 prompt_toolkit 是否已正确安装：`pip install prompt_toolkit`

**问题：`--classic` 模式下 automagic 不可用**

原因：`--classic` 模式会调整多个配置项，包括禁用 automagic 的部分行为。

解决方案：经典模式下显式使用 `%` 前缀调用魔法命令，或使用 `%automagic on` 重新开启。

**问题：embed() 嵌入后无法访问局部变量**

原因：`embed()` 需要从调用帧提取局部变量，如果在某些优化环境（如 Cython 编译的函数）中调用可能失效。

解决方案：确保在纯 Python 函数中调用 `embed()`；可以显式传递 `user_ns` 参数指定命名空间：
```python
embed(user_ns={'x': x, 'data': data})
```

## 相关概念

- [IPython 简介](../concepts/00-introduction.md)
- [快速开始](../concepts/01-getting-started.md)
- [补全与历史管理](../concepts/08-completer-history.md)
- [Shell 生命周期](../concepts/03-shell-lifecycle.md)
