---
type: example
title: "02 - 魔法命令实战"
description: 掌握 IPython 常用行魔法和单元魔法，包括性能测试、文件操作、命名空间管理、脚本执行等实战示例
tags: [example, magic, magics, line-magic, cell-magic, timeit, automagic]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-magic
    title: IPython/core/magic.py
  - id: ipython-magics-init
    title: IPython/core/magics/__init__.py
  - id: ipython-magics-table
    title: IPython/core/magics/_table.py
related_concepts: [/concepts/04-magic-system.md, /concepts/11-custom-magics.md]
---

## 目标

本示例演示 IPython 魔法命令（Magic Commands）的实战用法，覆盖以下内容：

1. 行魔法（`%` 前缀）：性能测试、目录导航、命名空间管理、历史查看、文件操作等
2. 单元魔法（`%%` 前缀）：计时、脚本执行、文件写入、HTML/JS 渲染等
3. automagic 模式：不带 `%` 前缀使用行魔法
4. 使用 `%lsmagic` 列出所有魔法、`%magic_name?` 查看帮助

## 完整代码

以下所有代码可直接在 IPython 终端中逐行运行：

```python
# ============================================================
# 一、查看所有可用魔法命令
# ============================================================

# 列出所有行魔法和单元魔法
In [1]: %lsmagic
# 输出类似:
# Available line magics:
# %alias  %alias_magic  %autoawait  %autocall  %automagic  %autoreload ...
# Available cell magics:
# %%!  %%HTML  %%SVG  %%bash  %%capture  %%debug  %%file  %%html ...

# 查看魔法系统帮助
In [2]: %magic?

# 查看具体魔法的帮助
In [3]: %timeit?
# 显示 %timeit 的详细文档和参数说明

# ============================================================
# 二、automagic 模式
# ============================================================

# automagic 默认开启，行魔法可以省略 % 前缀
In [4]: pwd          # automagic 自动转换为 %pwd
Out[4]: '/home/user/projects'

In [5]: %pwd         # 显式使用 % 前缀也可以
Out[5]: '/home/user/projects'

# 关闭 automagic
In [6]: %automagic off
Automagic is OFF, % prefix IS needed for line magics.

# 此时 pwd 会被当作 Python 变量
In [7]: pwd
# NameError: name 'pwd' is not defined

# 重新开启 automagic
In [8]: %automagic on
Automagic is ON, % prefix IS NOT needed for line magics.

# ============================================================
# 三、性能测试魔法：%timeit / %%timeit / %time / %%time
# ============================================================

# %timeit：自动多次运行取平均值，精确测量小段代码
In [9]: %timeit sum(range(1000))
# 12.3 µs ± 152 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

# 指定运行次数和循环次数
In [10]: %timeit -n 1000 -r 5 sum(range(100))
# 1.02 µs ± 48.3 ns per loop (mean ± std. dev. of 5 runs, 1000 loops each)

# %time：运行一次，显示 CPU 时间和墙钟时间
In [11]: %time sum(range(1000000))
# CPU times: user 20.1 ms, sys: 0 ns, total: 20.1 ms
# Wall time: 19.8 ms

# %%timeit：单元魔法，测量整个代码块
In [12]: %%timeit
    ...: s = 0
    ...: for i in range(1000):
    ...:     s += i
    ...:
# 38.5 µs ± 410 ns per loop ...

# %%time：单元级单次计时
In [13]: %%time
    ...: import time
    ...: time.sleep(0.1)
    ...:
# CPU times: user 0 ns, sys: 500 µs, total: 500 µs
# Wall time: 100 ms

# ============================================================
# 四、目录与文件操作魔法
# ============================================================

# %pwd：显示当前工作目录
In [14]: pwd
Out[14]: '/home/user/projects'

# %cd：切换目录（也会维护目录栈）
In [15]: cd /tmp
In [16]: pwd
Out[16]: '/tmp'

# %pushd / %popd：目录栈操作
In [17]: pushd /home/user
In [18]: pwd
Out[18]: '/home/user'
In [19]: popd
In [20]: pwd
Out[20]: '/tmp'

# %dirs：显示目录栈
In [21]: dirs

# %dhist：显示目录访问历史
In [22]: dhist

# %ls：列出目录内容（部分平台可用，类 Unix 系统的别名）
In [23]: ls
# file1.txt  file2.py  subdir/

# %env：查看和设置环境变量
In [24]: env
# 显示所有环境变量

In [25]: env MY_VAR=hello
In [26]: env MY_VAR
Out[26]: 'hello'

# ============================================================
# 五、运行脚本和代码加载
# ============================================================

# %run：运行外部 Python 脚本（在当前命名空间执行）
# 假设有一个 script.py 文件：
#   def greet(name):
#       return f"Hello, {name}!"
#   x = 42
In [27]: run script.py
In [28]: greet("World")  # 脚本中定义的函数可以直接使用
Out[28]: 'Hello, World!'
In [29]: x
Out[29]: 42

# %run -i：在当前交互命名空间中运行（可访问已定义变量）
# %run -t：打印执行时间
# %run -d：在 pdb 调试器下运行

# %load：加载文件内容到当前 cell
In [30]: load script.py
# 会将 script.py 的内容填充到下一个输入提示中

# %save：保存输入历史到文件
In [31]: save my_session.py 1-5  # 保存第 1-5 行输入到 my_session.py

# %edit：在编辑器中打开代码
In [32]: edit my_function.py
# 会打开 $EDITOR 环境变量指定的编辑器

# ============================================================
# 六、命名空间管理魔法
# ============================================================

# %who：列出当前命名空间中的变量（简短格式）
In [33]: who
# greeting   i   math   s   time   x

# %who_ls：以列表形式返回变量名
In [34]: who_ls
Out[34]: ['greeting', 'i', 'math', 's', 'time', 'x']

# %whos：详细显示变量信息（类型、大小、内容摘要）
In [35]: whos
# Variable   Type        Data/Info
# ------------------------------
# greeting   str         Hello, IPython!
# i          int         999
# math       module      <module 'math' from '...'>
# x          int         42

# %reset：清空命名空间（需要确认）
In [36]: reset
Once deleted, variables cannot be recovered. Proceed (y/[n])? y

# %reset -f：强制清空，不提示
In [37]: reset -f

# %reset_selective：选择性重置（按正则匹配）
In [38]: reset_selective temp.*
# 删除所有以 temp 开头的变量

# %xdel：删除变量并尝试清理所有引用
In [39]: xdel large_object

# ============================================================
# 七、历史记录魔法
# ============================================================

# %history：显示输入历史
In [40]: history
# 显示当前会话的所有输入

# %history -n：带行号显示
In [41]: history -n 1-10

# %history -g pattern：跨会话搜索
In [42]: history -g import
# 在所有历史中搜索包含 "import" 的行

# %recall：将历史行调到当前输入
In [43]: recall 5  # 将第 5 行历史填入当前输入

# %rerun：重新执行历史行
In [44]: rerun 3  # 重新执行第 3 行

# ============================================================
# 八、别名魔法
# ============================================================

# %alias：定义系统命令别名
In [45]: alias ll ls -la
In [46]: ll
# 执行 ls -la

# %alias_magic：为现有魔法创建别名
In [47]: alias_magic t timeit
In [48]: %t sum(range(100))  # 等价于 %timeit sum(range(100))

# %unalias：删除别名
In [49]: unalias ll

# ============================================================
# 九、单元魔法实战
# ============================================================

# %%bash：在 bash 中执行整个单元（类 Unix 系统）
In [50]: %%bash
    ...: echo "Hello from bash"
    ...: for i in 1 2 3; do
    ...:     echo "Number: $i"
    ...: done
    ...:
# Hello from bash
# Number: 1
# Number: 2
# Number: 3

# %%writefile：将单元内容写入文件
In [51]: %%writefile hello.py
    ...: def hello(name="World"):
    ...:     """A simple greeting function."""
    ...:     return f"Hello, {name}!"
    ...:
    ...: if __name__ == "__main__":
    ...:     print(hello())
    ...:
# Writing hello.py

In [52]: run hello.py
# Hello, World!

# %%html：渲染 HTML（在 Jupyter 中效果最佳，终端显示源码）
In [53]: %%html
    ...: <div style="color: blue; font-size: 20px;">
    ...:     <b>Hello HTML!</b>
    ...:     <ul>
    ...:         <li>Item 1</li>
    ...:         <li>Item 2</li>
    ...:     </ul>
    ...: </div>
    ...:

# %%javascript / %%js：执行 JavaScript（Jupyter 环境）
In [54]: %%javascript
    ...: console.log("Hello from JavaScript!");
    ...: alert("This runs in the browser");
    ...:

# %%markdown：渲染 Markdown（Jupyter 环境）
In [55]: %%markdown
    ...: # 标题
    ...:
    ...: 这是 **Markdown** 内容，支持*斜体*、`代码`和[链接](https://ipython.org)。
    ...:

# %%capture：捕获单元输出
In [56]: %%capture captured_output
    ...: print("This goes to stdout")
    ...: import sys
    ...: print("This goes to stderr", file=sys.stderr)
    ...: x = 42
    ...: print(f"x = {x}")
    ...:

In [57]: captured_output.stdout
Out[57]: 'This goes to stdout\nx = 42\n'

In [58]: captured_output.stderr
Out[58]: 'This goes to stderr\n'

In [59]: captured_output.show()  # 重新显示捕获的输出

# ============================================================
# 十、系统命令集成
# ============================================================

# 使用 ! 执行系统命令
In [60]: !echo "Hello from shell"
Hello from shell

# 捕获系统命令输出到 Python 变量
In [61]: files = !ls *.py
In [62]: files
Out[62]: ['hello.py', 'script.py']

# !! 等价于 !，返回 SList 对象
In [63]: !!ls
Out[63]: SList(. .. file.txt hello.py script.py)

# 在系统命令中使用 Python 变量（用 $ 或 {} 包裹）
In [64]: filename = "hello.py"
In [65]: !wc -l $filename
# 6 hello.py

# ============================================================
# 十一、实用魔法组合
# ============================================================

# %pdef：显示函数签名
In [66]: def greet(name, greeting="Hello"):
    ...:     return f"{greeting}, {name}!"
    ...:
In [67]: %pdef greet
# greet(name, greeting='Hello')

# %pdoc：显示文档字符串
In [68]: %pdoc greet

# %psource：显示源代码
In [69]: %psource greet

# %precision：设置浮点数显示精度
In [70]: import math
In [71]: %precision 4
In [72]: math.pi
Out[72]: 3.1416
In [73]: %precision %  # 恢复默认

# %pprint：开关 pretty printing
In [74]: %pprint
# Pretty printing has been turned OFF
In [75]: %pprint
# Pretty printing has been turned ON

# %xmode：设置异常显示模式
In [76]: %xmode Verbose
# Exception reporting mode: Verbose
In [77]: %xmode Context
# Exception reporting mode: Context

# %debug：在异常后进入调试器
In [78]: def divide(a, b):
    ...:     return a / b
    ...:
In [79]: divide(1, 0)
# ZeroDivisionError ...
In [80]: %debug
# 进入 pdb 调试器，可以检查变量和堆栈

# %pdb：开关异常后自动进入调试器
In [81]: %pdb on
# Automatic pdb calling has been turned ON
```

## 代码解析

### 魔法命令分类

IPython 内置了 80+ 魔法命令，由 15 个 Magics 类分别管理 [F-340][F-341]：

| Magics 类 | 模块 | 提供的核心魔法 |
|-----------|------|---------------|
| `BasicMagics` | `basic` | `%pwd`、`%cd`、`%dirs`、`%pushd`、`%popd`、`%env`、`%lsmagic`、`%xmode` 等 |
| `ExecutionMagics` | `execution` | `%timeit`、`%time`、`%run`、`%prun`、`%debug`、`%load`、`%save`、`%edit` 等 |
| `NamespaceMagics` | `namespace` | `%who`、`%whos`、`%who_ls`、`%pdef`、`%pdoc`、`%psource`、`%reset`、`%xdel` |
| `HistoryMagics` | `history` | `%history`、`%recall`、`%rerun` |
| `OSMagics` | `osm` | `!cmd`、`%alias`、`%sx`、`%set_env`、`%pip`、`%conda` |
| `DisplayMagics` | `display` | `%%html`、`%%javascript`、`%%markdown`、`%%latex`、`%%capture`、`%%svg` |
| `ScriptMagics` | `script` | `%%bash`、`%%sh`、`%%python`、`%%writefile`、`%%script` |
| `ExtensionMagics` | `extension` | `%load_ext`、`%unload_ext`、`%reload_ext` |

### automagic 机制

`MagicsManager.auto_magic` 默认为 `True` [F-304]，由 `PrefilterManager` 在输入预处理阶段检测无前缀的行魔法名并自动添加 `%` 前缀 [F-460]。单元魔法始终需要 `%%` 前缀，因为其跨越多行，无法通过简单的行首检测判断。

### 延迟加载（LazyMagic）

所有内置魔法都以延迟方式注册 [F-302][F-316]。`%lsmagic` 只列出魔法名称而不导入实际模块，首次调用时 `LazyMagic._resolve()` 才会触发 `load_lazy()` 导入对应的 Magics 类 [F-309]。这使得 IPython 启动速度很快——80+ 魔法的模块只在首次使用时才加载。

### %timeit vs %time

- `%timeit`：多次运行代码（默认 7 轮，每轮自动选择循环次数），计算平均值和标准差，适合测量短代码的性能。使用 `timeit` 模块实现，会暂时关闭垃圾回收以获得更准确结果。
- `%time`：只运行一次，报告 CPU 时间和墙钟时间，适合测量 I/O 操作或较长时间运行的代码。
- 两者都标记了 `@no_var_expand` [F-328]，防止代码中的 `{var}` 被误展开为 Python 变量。

### %%capture 的工作原理

`%%capture` 使用 `CapturingDisplayPublisher` 和 `CapturingDisplayHook` 捕获 stdout、stderr 和 display 输出 [F-392][F-402]，返回一个 `CapturedIO` 对象，可以通过 `.stdout`、`.stderr`、`.outputs` 属性访问捕获的内容。

### 系统命令集成

`!command` 语法由 `OSMagics` 处理，在子进程中执行系统命令。输出以 `SList`（字符串列表）形式返回，支持列表操作和 grep/fields 等方法。`$var` 和 `{var}` 语法将 Python 变量插入到系统命令中。

## 常见问题排查

**问题：`%%writefile` 或 `%%bash` 报错 "UsageError: Line magic function `%%xxx` not found"**

原因：单元魔法必须写在单元的第一行，前面不能有任何代码或注释。

解决方案：确保 `%%magic` 是 cell 的第一个输入，前面不能有空行、注释或其他代码。

**问题：`%cd` 切换目录后，后续代码中 `os.getcwd()` 没有更新**

原因：这通常不会发生——IPython 的 `%cd` 魔法会同时调用 `os.chdir()` 更新进程工作目录。如果遇到此问题，可能是在子进程中执行了目录切换。

解决方案：使用 `%cd`（而非 `!cd`）切换目录，`!cd` 在子 shell 中执行，不影响 IPython 进程。

**问题：`%run script.py` 后，脚本中的变量覆盖了当前命名空间的变量**

原因：`%run` 默认在独立命名空间运行脚本，但使用 `-i` 参数时会在当前交互命名空间运行。不带 `-i` 时，脚本顶层定义的变量仍会注入到用户命名空间。

解决方案：如果需要隔离，请将脚本逻辑封装在函数中；或使用 `%run -d` 在调试器中运行以更好控制。

**问题：automagic 模式下，某些魔法名与 Python 变量冲突**

原因：当存在同名 Python 变量时，automagic 可能将输入解析为变量引用而非魔法调用。

解决方案：显式使用 `%` 前缀（如 `%pwd`），或使用 `%automagic off` 关闭自动模式以避免歧义。

**问题：`%%bash` 在 Windows 上不可用**

原因：`%%bash` 需要系统安装 bash（如 Git Bash、WSL）。Windows 默认的脚本魔法是 `%%cmd` [F-343]。

解决方案：使用 `%%cmd` 在 Windows 上执行命令，或安装 WSL/Git Bash 后使用 bash。

## 相关概念

- [魔法命令系统](/concepts/04-magic-system.md)
- [自定义魔法开发](/concepts/11-custom-magics.md)
- [输入转换与特殊语法](/concepts/07-input-transform.md)
- [代码执行管线](/concepts/05-execution-pipeline.md)
- [信源参考 - 魔法系统](/references/magic-source.md)
