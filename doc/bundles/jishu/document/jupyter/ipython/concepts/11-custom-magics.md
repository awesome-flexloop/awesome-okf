---
type: concept
title: "11 - 自定义魔法开发"
description: 自定义魔法开发分步指南——创建 Magics 子类、使用装饰器、参数解析、加载方式，以及方法装饰器 vs 函数装饰器的区别
tags: [custom-magic, magics-class, decorators, magic-arguments, development-guide]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-magic
    title: IPython/core/magic.py
---

## 自定义魔法开发指南

IPython 提供了完善的 API 来创建自定义魔法命令。本指南从基础到进阶，逐步讲解如何开发行魔法和单元魔法。

## 开发步骤概览

创建自定义魔法需要以下步骤：

1. 创建继承 `Magics` 的子类，使用 `@magics_class` 装饰器
2. 使用 `@line_magic`/`@cell_magic`/`@line_cell_magic` 装饰方法
3. 添加行为装饰器（`@needs_local_scope`、`@no_var_expand`、`@output_can_be_silenced`）
4. 通过 `%load_ext` 扩展或 `ip.register_magics()` 加载

## 第一步：创建 Magics 子类

所有魔法类必须继承 `Magics` 基类并使用 `@magics_class` 装饰器 [F-320][F-322]：

```python
from IPython.core.magic import Magics, magics_class

@magics_class
class MyMagics(Magics):
    """我的自定义魔法集合"""
    pass
```

`@magics_class` 装饰器的作用是：
1. 标记类为已注册的 Magics 类（设置 `cls.registered = True`）
2. 将方法装饰器（`@line_magic`/`@cell_magic`）临时存储在模块全局 dict 中的魔法映射复制到类上
3. 清空模块级全局 dict，为下一个 Magics 类做准备 [F-322]

## 第二步：添加魔法方法

### 行魔法（@line_magic）

行魔法方法接收两个参数：`self` 和 `line`（魔法命令后的参数字符串）[F-323]：

```python
from IPython.core.magic import line_magic

@magics_class
class MyMagics(Magics):
    
    @line_magic
    def hello(self, line):
        """一个简单的问候行魔法
        
        用法: %hello [name]
        """
        name = line.strip() or "World"
        print(f"Hello, {name}!")
    
    @line_magic("greet")  # 自定义魔法名
    def greet_function(self, line):
        """自定义名称的行魔法
        
        用法: %greet [message]
        """
        message = line.strip()
        if message:
            print(f"Greetings: {message}")
        else:
            print("Greetings!")
```

### 单元魔法（@cell_magic）

单元魔法方法接收三个参数：`self`、`line`（首行参数）、`cell`（单元体内容）[F-324]：

```python
from IPython.core.magic import cell_magic

@magics_class
class MyMagics(Magics):
    
    @cell_magic
    def writelog(self, line, cell):
        """将单元内容写入日志文件
        
        用法:
        %%writelog filename.log
        content to write
        """
        filename = line.strip() or "default.log"
        with open(filename, 'w') as f:
            f.write(cell)
        print(f"Written to {filename}")
```

### 行+单元魔法（@line_cell_magic）

同时作为行魔法和单元魔法使用，方法需通过 `cell is None` 判断调用方式 [F-325]：

```python
from IPython.core.magic import line_cell_magic

@magics_class
class MyMagics(Magics):
    
    @line_cell_magic
    def timer(self, line, cell=None):
        """计时魔法
        
        行模式: %timer <expression>
        单元模式:
        %%timer [name]
        <code to time>
        """
        import time
        
        if cell is None:
            # 行模式：计时单行表达式
            start = time.time()
            self.shell.ex(line)  # 在用户命名空间执行代码
            elapsed = time.time() - start
            print(f"Line executed in {elapsed:.4f}s")
        else:
            # 单元模式：计时整个单元
            name = line.strip() or "Cell"
            start = time.time()
            self.shell.run_cell(cell)
            elapsed = time.time() - start
            print(f"{name} executed in {elapsed:.4f}s")
```

## 第三步：添加行为装饰器

三个行为装饰器控制魔法的特殊行为 [F-327][F-328][F-329]：

### @needs_local_scope

标记魔法需要访问本地命名空间。框架会额外传入 `local_ns` 关键字参数：

```python
from IPython.core.magic import needs_local_scope

@magics_class
class DataMagics(Magics):
    
    @needs_local_scope
    @line_magic
    def inspect_var(self, line, local_ns=None):
        """检查局部变量
        
        用法: %inspect_var <varname>
        """
        varname = line.strip()
        if varname in local_ns:
            value = local_ns[varname]
            print(f"{varname} = {value!r} (type: {type(value).__name__})")
        elif varname in self.shell.user_ns:
            value = self.shell.user_ns[varname]
            print(f"{varname} = {value!r} (in user_ns, type: {type(value).__name__})")
        else:
            print(f"Variable '{varname}' not found")
```

### @no_var_expand

标记魔法不需要变量展开。默认情况下，IPython 会将魔法行参数中的 `{var}` 和 `$var` 替换为 Python 变量的值 [F-328]：

```python
from IPython.core.magic import no_var_expand

@magics_class
class CodeMagics(Magics):
    
    @no_var_expand  # 重要！防止 {x} 和 $y 被误展开
    @line_magic
    def mytimeit(self, line):
        """计时魔法，不展开变量
        
        与 %timeit 类似，{x} 应该保持字面意义
        """
        # line 中的 {var} 保持原样，不会被 Python 变量替换
        import timeit
        # 直接使用 line 作为代码字符串
        result = timeit.timeit(line, number=1000, globals=self.shell.user_ns)
        print(f"{result*1000:.2f} ms per loop")
```

> **重要**：执行代码的魔法（如 `%timeit`、`%time`、`%run`）必须加 `@no_var_expand`，否则 `{x}` 会被错误地展开为变量值，破坏代码语义。

### @output_can_be_silenced

标记魔法的输出可以被行末分号 `;` 静默 [F-329]：

```python
from IPython.core.magic import output_can_be_silenced

@magics_class
class OutputMagics(Magics):
    
    @output_can_be_silenced
    @line_magic
    def verbose(self, line):
        """输出详细信息，可被分号静默
        
        用法:
        %verbose data  → 显示输出
        %verbose data; → 静默输出
        """
        data = self.shell.user_ns.get(line.strip(), "N/A")
        print(f"[VERBOSE] {line} = {data}")
```

## 参数解析：@magic_arguments

对于需要复杂参数解析的魔法，使用 `@magic_arguments` 装饰器（基于 argparse）：

```python
from IPython.core.magic import magics_class, line_magic, cell_magic
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring
)

@magics_class
class DataProcessMagics(Magics):
    
    @magic_arguments()
    @argument('varname', help='要处理的变量名')
    @argument('-o', '--output', default=None, help='输出变量名')
    @argument('-n', '--normalize', action='store_true', help='归一化数据')
    @argument('-v', '--verbose', action='count', default=0, help='详细级别')
    @line_magic
    def process(self, line):
        """处理数据变量
        
        用法:
        %process data -o result -n -v
        """
        args = parse_argstring(self.process, line)
        
        data = self.shell.user_ns.get(args.varname)
        if data is None:
            print(f"Variable '{args.varname}' not found")
            return
        
        if args.verbose >= 1:
            print(f"Processing {args.varname}, shape: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        
        result = data
        if args.normalize and hasattr(data, '__iter__'):
            total = sum(data)
            if total != 0:
                result = [x / total for x in data]
        
        output_name = args.output or f"{args.varname}_processed"
        self.shell.user_ns[output_name] = result
        print(f"Result stored in '{output_name}'")
    
    @magic_arguments()
    @argument('-f', '--format', default='text', choices=['text', 'html', 'markdown'],
              help='输出格式')
    @argument('-t', '--title', default='Output', help='标题')
    @cell_magic
    def render(self, line, cell):
        """渲染单元内容为指定格式
        
        用法:
        %%render -f html -t My Title
        <h1>Content</h1>
        """
        args = parse_argstring(self.render, line)
        
        from IPython.display import HTML, Markdown, display
        
        title = f"<h2>{args.title}</h2>" if args.title else ""
        
        if args.format == 'html':
            display(HTML(f"{title}{cell}"))
        elif args.format == 'markdown':
            display(Markdown(f"## {args.title}\n\n{cell}" if args.title else cell))
        else:
            print(f"=== {args.title} ===")
            print(cell)
```

## 第四步：加载魔法

有三种方式加载自定义魔法：

### 方式 1：通过扩展加载（推荐）

将魔法类放在 Python 模块中，通过 `%load_ext` 加载：

```python
# my_magics.py
from IPython.core.magic import Magics, magics_class, line_magic

@magics_class
class MyMagics(Magics):
    @line_magic
    def hello(self, line):
        print(f"Hello, {line.strip() or 'World'}!")

def load_ipython_extension(ipython):
    """扩展加载入口"""
    ipython.register_magics(MyMagics)

def unload_ipython_extension(ipython):
    """扩展卸载入口（可选）"""
    pass
```

然后在 IPython 中：
```python
%load_ext my_magics
%hello IPython  # → "Hello, IPython!"
```

### 方式 2：运行时直接注册

在 IPython 会话或 startup 文件中直接注册：

```python
# 在 IPython 会话中直接定义和注册
from IPython.core.magic import Magics, magics_class, line_magic
from IPython import get_ipython

@magics_class
class QuickMagics(Magics):
    @line_magic
    def mem(self, line):
        """显示内存使用"""
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        print(f"Memory: {usage.ru_maxrss / 1024:.1f} MB")

get_ipython().register_magics(QuickMagics)
# 之后可以直接使用 %mem
```

### 方式 3：使用函数装饰器（简单场景）

对于简单的独立魔法函数，使用 `@register_line_magic`/`@register_cell_magic` 在运行时立即注册 [F-326]：

```python
from IPython.core.magic import register_line_magic

# 注意：这种方式只能在 IPython 已运行的环境中使用
# （如 startup 文件或 IPython 会话中）
@register_line_magic
def quickecho(line):
    """快速回显魔法"""
    print(f"ECHO: {line}")

# 之后可以直接使用 %quickecho
```

> **注意**：函数装饰器（`@register_line_magic`）和方法装饰器（`@line_magic`）的区别：
> - 方法装饰器延迟到类实例化时注册（配合 `@magics_class`），可用于扩展模块
> - 函数装饰器立即注册，需要 `get_ipython()` 在当前上下文中可用
> - 方法装饰器接收 `self` 参数（Magics 实例），函数装饰器不接收

## 实用示例：SQL 执行魔法

以下是一个完整的自定义魔法示例——执行 SQL 查询的单元魔法：

```python
from IPython.core.magic import (
    Magics, magics_class, line_magic, cell_magic,
    needs_local_scope, no_var_expand
)
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring
)
from IPython.display import display, HTML
import sqlite3

@magics_class
class SQLMagics(Magics):
    """SQL 查询魔法"""
    
    def __init__(self, shell=None, **kwargs):
        super().__init__(shell=shell, **kwargs)
        self._connections = {}
    
    @line_magic
    def sql_connect(self, line):
        """连接到 SQLite 数据库
        
        用法: %sql_connect <database_path> [--name conn_name]
        """
        parts = line.strip().split()
        if not parts:
            print("Usage: %sql_connect <database_path> [--name <name>]")
            return
        
        db_path = parts[0]
        conn_name = 'default'
        if '--name' in parts:
            idx = parts.index('--name')
            if idx + 1 < len(parts):
                conn_name = parts[idx + 1]
        
        conn = sqlite3.connect(db_path)
        self._connections[conn_name] = conn
        print(f"Connected to '{db_path}' as '{conn_name}'")
    
    @needs_local_scope
    @no_var_expand
    @magic_arguments()
    @argument('-c', '--connection', default='default', help='连接名')
    @argument('-o', '--output', default=None, help='输出变量名')
    @cell_magic
    def sql(self, line, cell, local_ns=None):
        """执行 SQL 查询
        
        用法:
        %%sql -c default -o results
        SELECT * FROM users WHERE age > %s
        """
        args = parse_argstring(self.sql, line)
        
        conn = self._connections.get(args.connection)
        if conn is None:
            print(f"No connection named '{args.connection}'. Use %sql_connect first.")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute(cell)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                # 输出为 HTML 表格（在 Jupyter 中更好看）
                if rows:
                    html = "<table><tr>" + "".join(f"<th>{c}</th>" for c in columns) + "</tr>"
                    for row in rows:
                        html += "<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>"
                    html += "</table>"
                    display(HTML(html))
                
                print(f"({len(rows)} rows)")
                
                if args.output:
                    self.shell.user_ns[args.output] = rows
            else:
                conn.commit()
                print(f"Query executed, {cursor.rowcount} rows affected")
        except Exception as e:
            print(f"SQL Error: {e}")

def load_ipython_extension(ipython):
    ipython.register_magics(SQLMagics)
    print("SQL magics loaded. Use %sql_connect and %%sql.")
```

## 魔法开发最佳实践

1. **始终为魔法添加 docstring**：`%mymagic?` 和 `%quickref` 依赖 docstring 显示帮助
2. **执行代码的魔法加 `@no_var_expand`**：防止 `{var}` 和 `$var` 被错误展开
3. **需要访问局部变量时加 `@needs_local_scope`**：通过 `local_ns` 参数访问
4. **使用 `self.shell` 访问 Shell 功能**：
   - `self.shell.user_ns`：用户命名空间
   - `self.shell.ex(code)`：执行 Python 代码
   - `self.shell.run_cell(code)`：执行完整代码单元
   - `self.shell.display_formatter`：显示格式化器
   - `self.shell.events`：事件管理器
5. **使用 `@magic_arguments` 处理复杂参数**：比手动解析字符串更可靠
6. **输出使用 `display()` 而非 `print()`**：在 Jupyter 中支持富显示
7. **通过 `load_ipython_extension` 入口点注册**：这是标准的扩展分发方式
8. **提供 `unload_ipython_extension` 进行清理**：良好的扩展应该可卸载
9. **处理异常**：魔法中的异常应该给出清晰的错误信息，而不是抛出原始 traceback

## 方法装饰器 vs 函数装饰器对比

| 特性 | 方法装饰器（@line_magic 等） | 函数装饰器（@register_line_magic 等） |
|------|---------------------------|-------------------------------------|
| **使用位置** | Magics 子类内的方法 | 模块级独立函数 |
| **注册时机** | `register_magics()` 类实例化时 | 装饰器执行时立即注册 |
| **需要 `get_ipython()`** | 否（类实例化时传入 shell） | 是（装饰器执行时查找） |
| **self 参数** | 有（Magics 实例，通过 self.shell 访问 shell） | 无 |
| **适合场景** | 扩展模块、可分发的功能包 | 快速原型、startup 文件、临时使用 |
| **可卸载性** | 通过 ExtensionManager 可管理 | 需要手动移除 |
| **延迟加载** | 支持（配合 register_lazy） | 不支持（立即注册） |

## 相关概念

- [魔法命令系统](04-magic-system.md)
- [扩展系统](09-extension-system.md)
- [事件与钩子](10-events-hooks.md)
- [代码执行管线](05-execution-pipeline.md)
- [信源参考 - 魔法系统](../references/magic-source.md)
