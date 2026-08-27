---
type: concept
title: "01 - 快速开始"
description: IPython 安装、启动、第一个会话、命令行选项、嵌入式 API 快速上手指南
tags: [getting-started, installation, startup, embed, cli]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-init
    title: IPython/__init__.py
  - id: ipython-main
    title: IPython/__main__.py
  - id: ipython-terminal-app
    title: IPython/terminal/ipapp.py
---

## 安装 IPython

IPython 可以通过 pip 从 PyPI 安装：

```bash
pip install ipython
```

安装后即可使用 `ipython` 命令启动交互式 Shell。IPython 依赖 traitlets（配置框架）、prompt_toolkit（终端交互）、pygments（语法高亮）、jedi（智能补全）等包。

如需使用 Jupyter Notebook/Lab 的 Python 内核，还需安装 ipykernel：

```bash
pip install ipykernel
```

## 启动 IPython

### 命令行启动

直接在终端输入 `ipython` 即可启动 [F-101][F-111]：

```bash
$ ipython
Python 3.x.x (default, ...)
Type 'copyright', 'credits' or 'license' for more information
IPython 9.17.0.dev -- An enhanced Interactive Python. Type '?' for help.

In [1]:
```

`ipython` 命令等价于 `python -m IPython`，因为 `__main__.py` 从 `IPython` 导入 `start_ipython` 并调用 [F-005]。

### 命令行选项

TerminalIPythonApp 定义了多个命令行 flags 和 aliases [F-108]：

| Flag | 说明 |
|------|------|
| `--classic` | 经典 Python 提示符模式（禁用 pretty printing、使用 ClassicPrompts、无颜色、Plain xmode） |
| `--quick` | 快速启动，跳过配置文件加载 |
| `--no-banner` | 不显示启动横幅 |
| `--simple-prompt` | 使用简单提示符（禁用 prompt_toolkit，适合基础终端） |
| `--no-confirm-exit` | Ctrl-D 退出时不确认 |
| `--no-term-title` | 不自动设置终端标题 |
| `--no-autoedit-syntax` | 语法错误时不自动打开编辑器 |
| `--no-tip` | 不显示启动提示 |
| `-i` | 运行命令行代码后进入交互模式 |

使用 `ipython --help` 查看完整选项列表。常用启动方式：

```bash
# 经典模式（类似标准 Python REPL）
ipython --classic

# 快速启动（不加载配置文件）
ipython --quick

# 无横幅启动
ipython --no-banner

# 运行脚本后进入交互模式
ipython -i script.py

# 使用指定 profile
ipython --profile=myprofile

# 启用 matplotlib 集成
ipython --matplotlib
ipython --matplotlib=qt
```

### 子命令

TerminalIPythonApp 提供以下子命令 [F-107]：

| 子命令 | 说明 |
|--------|------|
| `ipython profile create <name>` | 创建新的 profile 配置 |
| `ipython kernel` | 启动 Jupyter 内核（委托给 ipykernel） |
| `ipython locate` | 打印 IPython 目录路径 [F-110] |
| `ipython history` | 历史记录管理 |

## 第一个 IPython 会话

启动 IPython 后，你会看到 `In [1]:` 提示符。以下是基本操作：

### 基本表达式

```python
In [1]: 1 + 1
Out[1]: 2

In [2]: print("Hello, IPython!")
Hello, IPython!

In [3]: import math

In [4]: math.sqrt(16)
Out[4]: 4.0
```

### In/Out 历史变量

IPython 自动维护输入输出历史 [F-232]：

- `In` 或 `_ih`：输入历史列表，`In[1]` 是第 1 个输入
- `Out` 或 `_oh`：输出历史字典，`Out[1]` 是第 1 个输出
- `_`：上一个输出结果
- `__`：倒数第二个输出结果
- `___`：倒数第三个输出结果

```python
In [5]: x = 42

In [6]: x * 2
Out[6]: 84

In [7]: print(_)  # 上一个输出
84

In [8]: In[1]     # 查看第 1 个输入
Out[8]: '1 + 1'
```

### 对象内省

使用 `?` 和 `??` 快速查看对象信息：

```python
In [9]: math.sqrt?
Signature: math.sqrt(x, /)
Docstring: Return the square root of x.
Type:      builtin_function_or_method

In [10]: import os

In [11]: os.path.join??  # 查看源代码
```

### 魔法命令入门

```python
# 行魔法（% 前缀，automagic 开启时可省略）
In [12]: %pwd
Out[12]: '/home/user'

In [13]: %timeit sum(range(1000))
1.23 µs ± 45 ns per loop ...

In [14]: %run myscript.py  # 运行外部脚本

# 单元魔法（%% 前缀，必须写在单元首行）
In [15]: %%timeit
    ...: s = 0
    ...: for i in range(1000):
    ...:     s += i
    ...:
```

### 系统命令

使用 `!` 执行系统 Shell 命令：

```python
In [16]: !ls
file1.py  file2.py  myscript.py

In [17]: files = !ls  # 捕获输出到 Python 变量
```

### 退出 IPython

有几种方式退出 IPython：

- 输入 `exit` 或 `quit`（通过 ExitAutocall 自动调用 [F-233]）
- 按 Ctrl-D（Unix）或 Ctrl-Z+Enter（Windows），根据 `confirm_exit` 设置决定是否确认 [F-244]
- 使用 `%exit` 魔法命令

## start_ipython() API

`start_ipython()` 是启动 IPython 的编程接口 [F-011]，调用 `TerminalIPythonApp.launch_new_instance()`：

```python
from IPython import start_ipython

# 启动 IPython（等价于命令行 ipython 命令）
start_ipython()

# 传递命令行参数
start_ipython(argv=['--classic', '--no-banner'])

# 指定用户命名空间
start_ipython(user_ns={'x': 42, 'data': [1, 2, 3]})

# 传递 Config 对象进行配置
from traitlets.config import Config
c = Config()
c.InteractiveShell.ast_node_interactivity = 'all'
c.TerminalInteractiveShell.confirm_exit = False
start_ipython(config=c)
```

`start_ipython()` 执行完整初始化流程：加载配置文件、profile、startup 文件等 [F-104]。这与 `embed()` 不同，后者跳过大部分初始化步骤。

## embed() 嵌入式 API

`embed()` 用于在任意 Python 代码中嵌入一个 IPython 交互式会话，非常适合调试 [F-007][F-008]：

```python
from IPython import embed

def my_function():
    x = 42
    data = [1, 2, 3]
    # 在这里嵌入 IPython，可以检查局部变量
    embed()  # 你将看到 IPython 提示符，可以访问 x 和 data
    return x + sum(data)

my_function()
```

`embed()` 通过 `__getattr__` 延迟导入 `IPython.terminal.embed` 模块 [F-008]，避免拖慢 `import IPython` 的速度。与 `start_ipython()` 不同：

- `embed()` 嵌入当前调用栈的作用域，可以访问局部变量
- `embed()` 跳过配置文件加载和完整 startup 文件执行
- `start_ipython()` 启动全新的独立 IPython 实例，执行完整初始化

### 使用示例：调试嵌入

```python
import IPython

def process_data(items):
    result = []
    for i, item in enumerate(items):
        processed = item * 2
        if processed > 100:
            # 在此处嵌入调试会话
            IPython.embed(
                header=f"Debugging at item {i}",
                colors="neutral"
            )
        result.append(processed)
    return result

process_data([10, 50, 60, 200])
```

## 应用层初始化流程

当通过命令行启动 `ipython` 时，TerminalIPythonApp 的初始化流程如下 [F-104][F-105][F-106]：

```
ipython 命令
  │
  ▼
TerminalIPythonApp.initialize(argv)
  ├── super().initialize()    ← 配置加载、命令行解析
  ├── init_path()             ← 初始化 IPython 目录路径
  ├── init_shell()            ← 创建 InteractiveShell 实例 [F-105]
  │     └── self.interactive_shell_class.instance(parent=self, ...)
  │           └── TerminalInteractiveShell.__init__()
  │                 └── 31 个 init_* 方法依次执行（见 [03-shell-lifecycle]）
  ├── init_banner()           ← 准备启动横幅
  ├── init_gui_pylab()        ← GUI/pylab 集成
  ├── init_extensions()       ← 加载配置的扩展
  └── init_code()             ← 执行启动代码
  │
  ▼
TerminalIPythonApp.start()
  ├── 若 self.interact: shell.mainloop()  ← 进入 REPL 主循环 [F-106]
  └── 否则：非交互模式执行指定代码
```

`launch_new_instance` 是 `TerminalIPythonApp.launch_instance` 的别名 [F-111]，它是 traitlets Application 框架提供的类方法，负责创建应用实例、调用 `initialize()` 和 `start()`。

## 相关概念

- [IPython 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [Shell 生命周期](03-shell-lifecycle.md)
- [终端前端与 GUI 集成](13-terminal-frontend.md)
- [信源参考 - 应用层](../references/app-source.md)
