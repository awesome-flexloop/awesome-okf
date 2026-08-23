---
type: example
title: "04 - 创建自定义魔法命令"
description: 从零开始编写 IPython 自定义行魔法和单元魔法，包括 Magics 类方式、函数装饰器方式、参数解析、行为装饰器和 startup 文件加载
tags: [example, custom-magic, magics-class, decorators, magic-arguments, line-magic, cell-magic]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-magic
    title: IPython/core/magic.py
  - id: ipython-magics-init
    title: IPython/core/magics/__init__.py
related_concepts: [/concepts/04-magic-system.md, /concepts/11-custom-magics.md, /concepts/09-extension-system.md]
---

## 目标

本示例演示如何编写自己的 IPython 魔法命令（`%` 行魔法和 `%%` 单元魔法），覆盖以下内容：

1. 方法一：创建 `Magics` 子类，使用 `@magics_class` 和 `@line_magic`/`@cell_magic` 装饰器
2. 方法二：使用 `@register_line_magic` 函数装饰器在运行时快速注册
3. 行为装饰器：`@needs_local_scope`、`@no_var_expand`、`@magic_arguments`
4. 通过 `%load_ext` 加载、通过 `ip.register_magics()` 直接注册
5. 在 startup 文件中自动加载自定义魔法

## 完整代码

### 示例 1：最简单的行魔法——%hello（可直接在 IPython 中运行）

```python
# 在 IPython 会话中直接定义和注册
from IPython.core.magic import Magics, magics_class, line_magic
from IPython import get_ipython

@magics_class
class HelloMagics(Magics):
    """简单的问候魔法集合"""
    
    @line_magic
    def hello(self, line):
        """一个简单的问候行魔法
        
        用法:
            %hello          # 输出 "Hello, World!"
            %hello Alice    # 输出 "Hello, Alice!"
        """
        name = line.strip() or "World"
        print(f"Hello, {name}!")

# 注册到当前 IPython 实例
ip = get_ipython()
ip.register_magics(HelloMagics)

# 现在可以使用
# %hello
# %hello IPython
```

### 示例 2：创建可通过 %load_ext 加载的魔法模块

将以下代码保存为 `my_magics.py`（放在 Python 路径或当前目录中）：

```python
# my_magics.py —— 可通过 %load_ext my_magics 加载
"""自定义 IPython 魔法集合

使用方法:
    %load_ext my_magics
    %hello [name]
    %%greet [title]
    <body content>
    %timer_stats
"""

from IPython.core.magic import (
    Magics, magics_class, line_magic, cell_magic,
    line_cell_magic, needs_local_scope, no_var_expand,
)
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring,
)
import time
import sys


@magics_class
class MyUtilityMagics(Magics):
    """实用工具魔法集合"""
    
    # ---- 行魔法 1: 问候 ----
    
    @line_magic
    def hello(self, line):
        """问候魔法
        
        用法:
            %hello          # Hello, World!
            %hello Alice    # Hello, Alice!
        """
        name = line.strip() or "World"
        print(f"Hello, {name}! 👋")
    
    # ---- 行魔法 2: 计时统计（需要本地命名空间） ----
    
    @needs_local_scope
    @line_magic
    def inspect(self, line, local_ns=None):
        """检查变量信息
        
        用法:
            %inspect <varname>
        
        显示变量的值和类型信息。使用 @needs_local_scope 访问局部变量。
        """
        varname = line.strip()
        if not varname:
            print("用法: %inspect <变量名>")
            return
        
        # 先在本地命名空间查找，再到用户命名空间查找
        ns = local_ns if local_ns else {}
        if varname in ns:
            value = ns[varname]
            scope = "local"
        elif varname in self.shell.user_ns:
            value = self.shell.user_ns[varname]
            scope = "global"
        else:
            print(f"变量 '{varname}' 未找到")
            return
        
        print(f"[{scope}] {varname} = {value!r}")
        print(f"  类型: {type(value).__name__}")
        if hasattr(value, '__len__'):
            try:
                print(f"  长度: {len(value)}")
            except Exception:
                pass
    
    # ---- 单元魔法 1: 带参数解析的 %%sql 占位实现 ----
    
    @magic_arguments()
    @argument('-o', '--output', default=None, help='将结果保存到指定变量')
    @argument('-c', '--connection', default=':memory:', help='数据库连接路径')
    @no_var_expand  # SQL 中可能有 {x} 等，不应被展开
    @cell_magic
    def sql(self, line, cell):
        """执行 SQL 查询（演示实现，使用 sqlite3）
        
        用法:
            %%sql [-o output_var] [-c db_path]
            SELECT * FROM users WHERE age > 18
        
        这是一个演示实现，使用内存 SQLite 数据库。
        """
        import sqlite3
        
        args = parse_argstring(self.sql, line)
        
        # 获取或创建数据库连接
        conn_key = f"_sql_conn_{args.connection}"
        if not hasattr(self, '_connections'):
            self._connections = {}
        
        if conn_key not in self._connections:
            self._connections[conn_key] = sqlite3.connect(args.connection)
        
        conn = self._connections[conn_key]
        cursor = conn.cursor()
        
        try:
            cursor.executescript(cell) if ';' in cell.strip()[:-1] else cursor.execute(cell)
            conn.commit()
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                # 打印结果表格
                widths = [len(col) for col in columns]
                for row in rows:
                    for i, val in enumerate(row):
                        widths[i] = max(widths[i], len(str(val)))
                
                header = " | ".join(col.ljust(widths[i]) for i, col in enumerate(columns))
                separator = "-+-".join("-" * w for w in widths)
                print(header)
                print(separator)
                for row in rows:
                    print(" | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row)))
                print(f"\n({len(rows)} 行)")
                
                # 保存到变量
                if args.output:
                    self.shell.user_ns[args.output] = rows
                    print(f"结果已保存到变量 '{args.output}'")
            else:
                print(f"SQL 执行成功，影响 {cursor.rowcount} 行")
        except Exception as e:
            print(f"SQL 错误: {e}")
    
    # ---- 行+单元魔法: %%%%timer ----
    
    @line_cell_magic
    def timer(self, line, cell=None):
        """计时魔法：行模式计时表达式，单元模式计时代码块
        
        用法:
            %timer <expression>      # 行模式：执行并计时单行表达式
            %%timer [label]          # 单元模式：执行并计时整个代码块
            <code to time>
        """
        if cell is None:
            # 行模式
            start = time.time()
            result = self.shell.ex(line)
            elapsed = time.time() - start
            print(f"⏱  行执行时间: {elapsed:.4f}s")
        else:
            # 单元模式
            label = line.strip() or "Cell"
            start = time.time()
            self.shell.run_cell(cell)
            elapsed = time.time() - start
            print(f"⏱  {label} 执行时间: {elapsed:.4f}s")
    
    # ---- 行魔法: 带参数解析的数据处理 ----
    
    @magic_arguments()
    @argument('varname', help='要处理的变量名')
    @argument('-o', '--output', default=None, help='输出变量名')
    @argument('-n', '--normalize', action='store_true', help='归一化数据')
    @argument('-v', '--verbose', action='count', default=0, help='详细级别')
    @needs_local_scope
    @line_magic
    def process(self, line, local_ns=None):
        """处理数据变量
        
        用法:
            %process data -o result -n -v
        
        示例:
            data = [1, 2, 3, 4, 5]
            %process data -o normalized -n
            print(normalized)
        """
        args = parse_argstring(self.process, line)
        
        ns = local_ns if local_ns else self.shell.user_ns
        data = ns.get(args.varname)
        if data is None:
            data = self.shell.user_ns.get(args.varname)
        
        if data is None:
            print(f"变量 '{args.varname}' 未找到")
            return
        
        if args.verbose >= 1:
            print(f"处理 {args.varname}, 长度: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        
        result = list(data)  # 复制
        
        if args.normalize and hasattr(data, '__iter__'):
            total = sum(result)
            if total != 0:
                result = [x / total for x in result]
            if args.verbose >= 2:
                print(f"归一化总和: {total}")
        
        output_name = args.output or f"{args.varname}_processed"
        self.shell.user_ns[output_name] = result
        print(f"结果已保存到 '{output_name}': {result}")


# ---- 扩展加载入口 ----

def load_ipython_extension(ipython):
    """%load_ext my_magics 时调用"""
    ipython.register_magics(MyUtilityMagics)
    print("✅ my_magics 已加载！可用魔法: %hello, %inspect, %%sql, %%timer, %process")


def unload_ipython_extension(ipython):
    """%unload_ext my_magics 时调用（清理）"""
    print("👋 my_magics 已卸载")
```

**使用方法：**

```python
# 在 IPython 中加载扩展
%load_ext my_magics

# 使用 %hello
%hello
%hello IPython

# 使用 %inspect
data = [1, 2, 3, 4, 5]
%inspect data

# 使用 %%sql
%%sql
CREATE TABLE users (id INTEGER, name TEXT, age INTEGER)
;;;
%%sql
INSERT INTO users VALUES (1, 'Alice', 25), (2, 'Bob', 30), (3, 'Charlie', 17)
;;;
%%sql -o results
SELECT name, age FROM users WHERE age >= 18
;;;
results  # 查看查询结果

# 使用 %%timer
%%timer 数据处理
total = sum(range(1_000_000))
print(f"Sum: {total}")
;;;
%timer sum(range(100000))

# 使用 %process
values = [10, 20, 30, 40]
%process values -o normalized_values -n -v
normalized_values
```

### 示例 3：使用函数装饰器快速注册魔法（IPython 会话中直接运行）

```python
# 这种方式最简单，适合在 IPython 会话或 startup 文件中快速添加魔法
from IPython.core.magic import register_line_magic, register_cell_magic

# 行魔法
@register_line_magic
def dice(line):
    """掷骰子魔法
    
    用法:
        %dice       # 默认掷 1 个 6 面骰
        %dice 3d6   # 掷 3 个 6 面骰
        %dice 2d20  # 掷 2 个 20 面骰
    """
    import random
    parts = line.strip().split('d')
    if len(parts) == 1 and parts[0] == '':
        count, sides = 1, 6
    elif len(parts) == 2:
        count = int(parts[0]) if parts[0] else 1
        sides = int(parts[1])
    else:
        count, sides = 1, 6
    
    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)
    if count == 1:
        print(f"🎲 {rolls[0]}")
    else:
        print(f"🎲 {rolls} = {total}")
    return total

# 单元魔法
@register_cell_magic
def writelog(line, cell):
    """将单元内容写入日志文件
    
    用法:
        %%writelog [filename]
        log content...
    """
    filename = line.strip() or "ipython.log"
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"\n--- {timestamp} ---\n")
        f.write(cell)
        if not cell.endswith('\n'):
            f.write('\n')
    print(f"✅ 已追加到 {filename} ({len(cell)} 字符)")

# 现在可以直接使用
# %dice
# %dice 4d6
# %%writelog notes.txt
# 这是日志内容
```

### 示例 4：Startup 文件自动加载

创建文件 `~/.ipython/profile_default/startup/00-my-magics.py`（或 Windows 上的 `%USERPROFILE%\.ipython\profile_default\startup\00-my-magics.py`）：

```python
# ~/.ipython/profile_default/startup/00-my-magics.py
# IPython 启动时自动执行此文件

from IPython.core.magic import register_line_magic, Magics, magics_class, line_magic
from IPython import get_ipython

# 方式 1：快速函数魔法
@register_line_magic
def timer_now(line):
    """显示当前时间"""
    import datetime
    now = datetime.datetime.now()
    print(f"🕐 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")

@register_line_magic
def meminfo(line):
    """显示内存使用（跨平台兼容的简单版本）"""
    import sys
    # 简单显示 Python 进程内存信息
    print(f"Python 版本: {sys.version}")
    print(f"递归限制: {sys.getrecursionlimit()}")
    
    # 尝试使用 psutil（如果安装了）
    try:
        import psutil
        proc = psutil.Process()
        mem = proc.memory_info()
        print(f"内存使用: {mem.rss / 1024 / 1024:.1f} MB")
        print(f"CPU 使用率: {proc.cpu_percent()}%")
    except ImportError:
        print("（安装 psutil 可查看详细内存信息: pip install psutil）")

# 方式 2：使用 Magics 类
@magics_class
class QuickToolsMagics(Magics):
    """快速工具魔法"""
    
    @line_magic
    def reload_modules(self, line):
        """重新加载指定的模块
        
        用法:
            %reload_modules mymodule
            %reload_modules module1 module2
        """
        import importlib
        modules = line.strip().split()
        for mod_name in modules:
            if mod_name in sys.modules:
                importlib.reload(sys.modules[mod_name])
                print(f"🔄 已重新加载 {mod_name}")
            else:
                print(f"⚠️  模块 {mod_name} 未导入")

ip = get_ipython()
if ip is not None:
    ip.register_magics(QuickToolsMagics)
    print("🚀 自定义魔法已加载: %timer_now, %meminfo, %reload_modules")
```

### 示例 5：完整可运行的测试脚本（保存为 test_magics.py 运行）

```python
#!/usr/bin/env python
"""测试自定义魔法的完整脚本

运行方式:
    python test_magics.py
这将启动一个加载了自定义魔法的 IPython 会话。
"""
from IPython import start_ipython
from traitlets.config import Config

# 创建配置
c = Config()

# 启动 IPython，预加载自定义魔法
if __name__ == '__main__':
    # 可以通过 exec_lines 在启动时注册魔法
    start_ipython(
        argv=['--no-banner'],
        config=c,
        user_ns={
            # 预定义一些变量方便测试
            'test_data': [10, 20, 30, 40, 50],
            'test_dict': {'name': 'IPython', 'version': 9},
        },
        exec_lines=[
            # 启动时直接注册一个简单魔法
            """
from IPython.core.magic import register_line_magic
@register_line_magic
def welcome(line):
    print(f'欢迎使用 IPython! 你好, {line.strip() or \"朋友\"}!')
            """.strip(),
        ],
    )
```

## 代码解析

### 装饰器体系

IPython 的魔法系统使用多层装饰器来声明和注册魔法 [F-322-F-326]：

**类装饰器**：
- `@magics_class`：标记 `Magics` 子类。它将方法装饰器临时存储的魔法映射从模块级全局 dict 复制到类上，然后清空全局 dict [F-322]。这是必须的，因为方法装饰器在类定义时执行，类还不存在。

**方法装饰器**（在 Magics 类中使用）：
| 装饰器 | 签名 | 说明 |
|--------|------|------|
| `@line_magic` | `(self, line: str)` | 行魔法方法 |
| `@cell_magic` | `(self, line: str, cell: str)` | 单元魔法方法 |
| `@line_cell_magic` | `(self, line: str, cell=None)` | 行+单元魔法，通过 `cell is None` 判断模式 |

方法装饰器支持带参数自定义魔法名：`@line_magic("custom_name")`。

**函数装饰器**（模块级独立函数）：
| 装饰器 | 说明 |
|--------|------|
| `@register_line_magic` | 立即注册行魔法，需要 `get_ipython()` 可用 |
| `@register_cell_magic` | 立即注册单元魔法 |
| `@register_line_cell_magic` | 立即注册行+单元魔法 |

函数装饰器**立即执行注册**，不能在模块导入时使用（IPython 未初始化），适合在 IPython 会话或 startup 文件中使用。

### 行为装饰器

| 装饰器 | 作用 | 源码事实 |
|--------|------|---------|
| `@needs_local_scope` | 标记魔法需要访问局部命名空间，框架额外传入 `local_ns` 参数 | [F-327] |
| `@no_var_expand` | 不展开 `{var}`/`$var` 变量。执行代码的魔法（如 `%timeit`、`%%sql`）必须加此装饰器 | [F-328] |
| `@output_can_be_silenced` | 输出可被行末分号 `;` 静默 | [F-329] |

### @magic_arguments 参数解析

`@magic_arguments` 基于 argparse 提供声明式参数解析 [F-4-magic_arguments]：

```python
@magic_arguments()
@argument('varname', help='位置参数')
@argument('-o', '--output', default=None, help='可选参数')
@argument('-v', '--verbose', action='count', default=0)
@line_magic
def my_magic(self, line):
    args = parse_argstring(self.my_magic, line)
    # args.varname, args.output, args.verbose
```

### 加载方式对比

| 方式 | 适用场景 | 可卸载 | 延迟加载 |
|------|---------|--------|---------|
| `ip.register_magics(MyMagics())` | 会话中临时使用、startup 文件 | 需手动清理 | 否 |
| `%load_ext my_module` | 分发给他人使用的扩展 | `%unload_ext` | 支持（register_lazy） |
| `@register_line_magic` | 快速原型、startup 文件 | 需手动移除 | 否 |

### self.shell 访问 Shell 功能

通过 `self.shell`（Magics 基类提供 [F-320]）可以访问 IPython 的所有核心功能：

- `self.shell.user_ns`：用户命名空间字典
- `self.shell.ex(code)`：执行 Python 代码（返回 None）
- `self.shell.ev(expr)`：求值表达式（返回结果）
- `self.shell.run_cell(code)`：执行完整代码单元
- `self.shell.display_formatter`：显示格式化器
- `self.shell.events`：事件管理器
- `self.shell.magics_manager`：魔法管理器

### 扩展入口点

通过 `%load_ext` 加载的模块必须实现 [F-434][F-435]：
- `load_ipython_extension(ipython)`：加载入口，注册魔法/事件/钩子
- `unload_ipython_extension(ipython)`：卸载入口（可选但推荐），清理注册的资源

## 常见问题排查

**问题：在普通 Python 脚本中使用 `@register_line_magic` 报错 "Instance of 'Magics' has no 'user_ns' member" 或 "NoneType has no..."**

原因：`@register_line_magic` 需要 `get_ipython()` 返回有效的 IPython 实例。在普通 Python 脚本中直接运行时 IPython 尚未启动。

解决方案：
- 将魔法定义放在 `load_ipython_extension()` 函数中，通过 `%load_ext` 加载
- 或在 IPython 会话中直接定义
- 或使用 `if ip is not None:` 进行保护（如示例 4 的 startup 文件）

**问题：`%load_ext my_magics` 报错 "No module named 'my_magics'"**

原因：`my_magics.py` 文件不在 Python 搜索路径中。

解决方案：
- 将文件放在当前工作目录（`%pwd` 显示的目录）
- 或将文件所在目录添加到 `sys.path`
- 或将文件放到 `~/.ipython/extensions/` 目录（IPython 扩展专用目录）

**问题：魔法中的 `{var}` 被替换成了 Python 变量的值，导致 SQL 等代码出错**

原因：默认情况下，IPython 会将魔法行/单元中的 `{var}` 和 `$var` 展开为 Python 变量值。

解决方案：在执行代码或包含字面量花括号的魔法上添加 `@no_var_expand` 装饰器 [F-328]。

**问题：`@needs_local_scope` 方法没有收到 `local_ns` 参数**

原因：`@needs_local_scope` 必须放在方法装饰器栈中离方法最近的位置（最内层），否则参数注入可能不正确。

解决方案：确保装饰器顺序正确——`@needs_local_scope` 应直接在 `@line_magic`/`@cell_magic` 上方：
```python
@needs_local_scope  # 最靠近方法
@line_magic         # 然后是方法装饰器
def my_magic(self, line, local_ns=None):
    ...
```

**问题：startup 文件中的魔法没有加载**

原因：startup 文件按文件名顺序执行，文件名必须以 `.py` 结尾，且位于正确的 profile startup 目录中。

解决方案：
- 确认文件位于 `~/.ipython/profile_default/startup/` 目录
- 使用 `ipython locate profile` 查看 profile 目录路径
- 文件名建议以数字开头（如 `00-first.py`）控制加载顺序
- 检查文件中是否有语法错误导致启动时静默失败（使用 `ipython --debug` 查看详细日志）

## 相关概念

- [魔法命令系统](/concepts/04-magic-system.md)
- [自定义魔法开发](/concepts/11-custom-magics.md)
- [扩展系统](/concepts/09-extension-system.md)
- [输入转换与特殊语法](/concepts/07-input-transform.md)
- [信源参考 - 魔法系统](/references/magic-source.md)
