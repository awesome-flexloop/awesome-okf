---
type: concept
title: "04 - 魔法命令系统"
description: IPython 魔法命令三级机制——装饰器注册、LazyMagic 延迟加载、自动魔法前缀，MagicsManager 管理与内置魔法分类
tags: [magic, magics-manager, decorators, lazy-loading, automagic, line-magic, cell-magic]
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
---

## 魔法命令概述

魔法命令（Magic Commands）是 IPython 最具特色的功能，提供了超出 Python 语法的便捷交互命令。魔法命令分为两类 [F-330][F-331]：

- **行魔法（Line Magic）**：以 `%` 为前缀，作用于单行输入。如 `%timeit`、`%run`、`%pwd`、`%cd`
- **单元魔法（Cell Magic）**：以 `%%` 为前缀，必须写在单元首行，作用于整个代码块。如 `%%timeit`、`%%html`、`%%javascript`

转义字符常量定义为 `ESC_MAGIC = '%'` 和 `ESC_MAGIC2 = '%%'` [F-330]。在 automagic 模式下（默认开启 [F-304]），行魔法可以省略 `%` 前缀直接输入命令名。

魔法系统采用**三级机制**实现：装饰器注册 → 延迟加载 → 自动魔法转换。

## MagicsManager 魔法管理器

`MagicsManager` 是魔法命令的核心管理器，继承 `Configurable` [F-300]，在 `init_magics()` 中被实例化为 `shell.magics_manager`。

### 核心数据结构

```python
class MagicsManager(Configurable):
    # 二级 dict：magics['line'][name] → 可调用对象
    #          magics['cell'][name] → 可调用对象
    magics = Dict()  # [F-301]
    
    # 延迟魔法映射：name → "module:Class" 或 "module"（扩展路径）
    lazy_magics = Dict()  # [F-302]
    
    # Magics 类实例注册表：按类名存储 Magics 对象
    registry = Instance(_MagicsRegistry)  # [F-303]
    
    # 自动魔法模式：行魔法不需要 % 前缀
    auto_magic = Bool(True)  # [F-304]
```

### 核心方法

| 方法 | 说明 | 事实 |
|------|------|------|
| `register(*magic_objects)` | 注册一个或多个 Magics 类/实例 | [F-305] |
| `register_function(func, magic_kind, magic_name=None)` | 注册独立函数为魔法 | [F-306] |
| `register_alias(alias_name, magic_name)` | 注册魔法别名 | [F-307] |
| `register_lazy(name, fully_qualified_name, magic_kind='line_cell')` | 延迟注册魔法 | [F-308] |
| `load_lazy(magic_name)` | 导入并注册延迟魔法 | [F-309] |
| `load_all_lazy_magics()` | 加载所有 "module:Class" 形式的延迟魔法 | [F-310] |
| `find(magic_kind, magic_name)` | 查找魔法，必要时自动加载延迟魔法 | [F-311] |
| `lsmagic()` | 返回 `{'line': {...}, 'cell': {...}}` 字典 | [F-312] |
| `lsmagic_docs(brief=False)` | 返回魔法文档字符串字典 | [F-313] |
| `auto_status()` | 返回 automagic 状态描述字符串 | [F-314] |

### 注册流程

注册一个 Magics 类时，MagicsManager 遍历类上的 `magics` dict（由 `@magics_class` 装饰器构建），将每个魔法方法绑定到 Magics 实例后存入 `self.magics`：

```python
# 注册一个 Magics 类实例
mm.register(MyMagics(shell))

# 注册后，mm.magics['line']['my_magic'] → 绑定的方法
#       mm.magics['cell']['my_cell_magic'] → 绑定的方法
#       mm.registry['MyMagics'] → MyMagics 实例
```

### LazyMagic 延迟加载

`LazyMagic` 类是未导入魔法的占位代理 [F-316]。它在 `magics` dict 中占位，但不触发实际模块导入：

```python
class LazyMagic:
    """延迟魔法占位符"""
    def __init__(self, manager, spec, magic_kind, magic_name):
        self.spec = spec          # "IPython.core.magics.execution:ExecutionMagics"
        self._manager = manager   # MagicsManager 引用
        self._kind = magic_kind   # "line" 或 "cell"
        self._name = magic_name   # 魔法名称
    
    def _resolve(self):
        """调用 manager.find() 触发实际导入"""
        return self._manager.find(self._kind, self._name)
    
    def __call__(self, *args, **kwargs):
        return self._resolve()(*args, **kwargs)  # 首次调用时解析
    
    def __getattr__(self, name):
        return getattr(self._resolve(), name)     # 属性访问也触发解析
```

关键设计：`%lsmagic` 列出所有魔法名称时不需要导入实际模块——它只需要遍历 `magics` dict 的键，而 LazyMagic 对象一直占位到首次调用或属性访问。`_MagicsRegistry.__missing__` 在访问未加载的 Magics 类时自动触发加载 [F-315]。

### register_lazy 的两种模式

`register_lazy()` 支持两种延迟注册模式 [F-308][F-309]：

1. **"module:Class" 模式**（内置魔法使用）：直接导入模块并实例化指定类，注册其魔法。不经过扩展机制。
2. **"module" 模式**（扩展使用）：将模块作为 IPython 扩展加载，调用 `load_ipython_extension(ip)`。

```python
# 模式1：直接导入类（内置魔法）
mm.register_lazy('timeit', 'IPython.core.magics.execution:ExecutionMagics')

# 模式2：作为扩展加载
mm.register_lazy('my_magic', 'my_package.my_magics')
```

## 装饰器体系

IPython 的魔法系统通过一套精心设计的装饰器实现魔法方法的声明和注册。

### 类装饰器：@magics_class

`@magics_class` 是 Magics 子类的必备装饰器 [F-322]。它解决了一个 Python 元编程难题：方法装饰器（`@line_magic`）在类定义时运行，此时类还不存在，无法直接将方法注册到类上。

解决方案：使用一个模块级全局 dict `magics` 作为临时存储 [F-50]：

```python
# 模块级全局临时存储
magics = dict(line={}, cell={})

def magics_class(cls):
    """类装饰器：将临时存储的魔法映射复制到类上，清空全局"""
    cls.registered = True
    cls.magics = dict(line=magics["line"], cell=magics["cell"])
    magics["line"] = {}   # 清空全局，准备下一个类
    magics["cell"] = {}
    return cls
```

> **注意**：这个机制不是线程安全的，但 Magics 类只在 IPython 启动时单线程定义，实践中无问题 [F-322 源码注释]。

### 方法装饰器（类中使用）

三个方法装饰器用于标记 Magics 子类中的魔法方法 [F-323][F-324][F-325]：

| 装饰器 | 魔法类型 | 说明 |
|--------|---------|------|
| `@line_magic` | 行魔法 | 标记方法为行魔法，接收 `(self, line: str)` 参数 |
| `@cell_magic` | 单元魔法 | 标记方法为单元魔法，接收 `(self, line: str, cell: str)` 参数 |
| `@line_cell_magic` | 行+单元魔法 | 同时注册为行和单元魔法，方法需判断调用方式 |

装饰器支持带参数（自定义魔法名）和不带参数（使用函数名）两种用法：

```python
from IPython.core.magic import (Magics, magics_class, line_magic, 
                                cell_magic, line_cell_magic)

@magics_class
class MyMagics(Magics):
    
    @line_magic  # 无参数：魔法名为方法名 "hello"
    def hello(self, line):
        """一个简单的行魔法"""
        print(f"Hello, {line}!")
    
    @line_magic("greet")  # 带参数：魔法名为 "greet"
    def greet_func(self, line):
        """自定义名称的行魔法"""
        print(f"Greetings, {line}!")
    
    @cell_magic
    def sql(self, line, cell):
        """一个单元魔法：执行 SQL"""
        print(f"Running SQL on: {line}")
        print(cell)
    
    @line_cell_magic
    def timer(self, line, cell=None):
        """既是行魔法也是单元魔法"""
        if cell is None:
            print(f"Line mode: {line}")
        else:
            print(f"Cell mode: line={line}, cell={cell}")
```

### 函数装饰器（运行时立即注册）

三个函数装饰器用于在运行时立即注册独立函数为魔法 [F-326]：

| 装饰器 | 说明 |
|--------|------|
| `@register_line_magic` | 立即注册行魔法函数 |
| `@register_cell_magic` | 立即注册单元魔法函数 |
| `@register_line_cell_magic` | 立即注册行+单元魔法函数 |

这些装饰器**立即执行注册**，需要 `get_ipython()` 在当前上下文中可用 [F-326 源码]：

```python
# 只能在 IPython 已运行时使用（如 startup 文件或 IPython 会话中）
from IPython.core.magic import register_line_magic

@register_line_magic
def mymagic(line):
    """直接在 IPython 会话中注册行魔法"""
    print(f"Got: {line}")

# 之后可以直接使用 %mymagic
```

> **重要区别**：方法装饰器（`@line_magic`）延迟到类实例化时注册；函数装饰器（`@register_line_magic`）立即注册，需要 IPython 已运行。函数装饰器不能在配置文件中使用（配置文件执行时 IPython 尚未完全初始化）。

### 行为装饰器

三个行为装饰器控制魔法函数的特殊行为 [F-327][F-328][F-329]：

| 装饰器 | 属性标记 | 说明 |
|--------|---------|------|
| `@needs_local_scope` | `func.needs_local_scope = True` | 标记魔法需要本地命名空间，框架会传入 `local_ns` 参数 |
| `@no_var_expand` | `func._ipython_magic_no_var_expand = True` | 不进行 `{var}`/`$var` 变量展开。`%timeit`、`%time` 等必须加此装饰器，防止 `{x}` 被误展开 |
| `@output_can_be_silenced` | `func._ipython_magic_output_can_be_silenced = True` | 标记魔法输出可被行末分号 `;` 静默 |

```python
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.magic import no_var_expand, needs_local_scope

@magics_class
class MyMagics(Magics):
    
    @needs_local_scope
    @line_magic
    def inspect_local(self, line, local_ns=None):
        """需要访问本地命名空间的魔法"""
        var_name = line.strip()
        print(f"Local variable {var_name}: {local_ns.get(var_name, 'NOT FOUND')}")
    
    @no_var_expand
    @line_magic
    def mytimeit(self, line):
        """不展开变量的计时魔法，防止 {n} 被展开"""
        # line 中的 {x} 或 $x 保持原样，不会被 Python 变量替换
        import timeit
        print(timeit.timeit(line, number=1000))
```

## Magics 基类

所有自定义魔法类继承 `Magics` 基类 [F-320]：

```python
class Magics(Configurable):
    """Magics 基类，提供 shell 和 options 属性"""
    
    def __init__(self, shell=None, **kwargs):
        super().__init__(**kwargs)
        self.shell = shell  # 指向 InteractiveShell 实例
    
    # 工具方法
    def named_params(self, defaults):
        """解析命令行参数"""
        ...
```

通过 `self.shell` 可以访问 IPython 的所有功能：命名空间、显示系统、历史管理、事件等。

## 内置魔法分类

IPython 内置了 15 个 Magics 类 [F-340]，通过 MAGICS_CLASSES 映射表管理：

| Magics 类 | 模块 | 主要魔法 |
|-----------|------|---------|
| **AsyncMagics** | basic | `%autoawait` 异步控制 |
| **AutoMagics** | auto | `%automagic` 自动魔法开关 |
| **BasicMagics** | basic | `%pwd`、`%cd`、`%dirs`、`%pushd`、`%popd`、`%dhist`、`%env`、`%colors`、`%xmode`、`%doctest_mode`、`%gui`、`%lsmagic`、`%magic`、`%page`、`%pprint`、`%precision`、`%quickref` 等 |
| **CodeMagics** | code | `%paste`、`%cpaste`、`%run`（部分）、代码编辑相关 |
| **ConfigMagics** | config | `%config` 配置管理 |
| **DisplayMagics** | display | `%%html`、`%%javascript`、`%%js`、`%%latex`、`%%markdown`、`%%svg`、`%display`、`%%capture` |
| **ExecutionMagics** | execution | `%run`、`%time`、`%timeit`、`%prun`、`%debug`、`%tb`、`%load`、`%save`、`%pastebin`、`%macro`、`%edit` 等 |
| **ExtensionMagics** | extension | `%load_ext`、`%unload_ext`、`%reload_ext` |
| **HistoryMagics** | history | `%history`、`%recall`、`%rerun` |
| **LoggingMagics** | logging | `%logstart`、`%logstop`、`%logon`、`%logoff`、`%logstate` |
| **NamespaceMagics** | namespace | `%who`、`%who_ls`、`%whos`、`%pdef`、`%pdoc`、`%pfile`、`%pinfo`（?）、`%pinfo2`（??）、`%psource`、`%psearch`、`%reset`、`%reset_selective`、`%xdel` |
| **OSMagics** | osm | `!cmd`、`!!cmd`、`%alias`、`%unalias`、`%rehashx`、`%sx`、`%system`、`%sc`、`%bookmark`、`%pycat`、`%set_env`、`%conda`、`%pip`、`%mamba`、`%micromamba`、`%uv`、`%matplotlib`、`%pylab`、`%killbgscripts` |
| **PackagingMagics** | packaging | 包管理辅助 |
| **PylabMagics** | pylab | `%pylab`、`%matplotlib` 集成 |
| **ScriptMagics** | script | `%%script`、`%%bash`、`%%sh`、`%%perl`、`%%ruby`、`%%python`、`%%writefile` |

### 内置行魔法清单

BUILTIN_LAZY_MAGICS 声明了 80+ 内置行魔法 [F-341]，全部以延迟方式注册。常用行魔法按功能分类：

**执行与性能**：`%run`、`%time`、`%timeit`、`%prun`、`%debug`、`%tb`、`%macro`
**环境导航**：`%pwd`、`%cd`、`%pushd`、`%popd`、`%dirs`、`%dhist`、`%env`、`%bookmark`
**系统命令**：`%alias`、`%unalias`、`%sx`、`%system`、`%sc`、`%rehashx`
**对象内省**：`%pdef`、`%pdoc`、`%pfile`、`%pinfo`（?）、`%pinfo2`（??）、`%psource`、`%psearch`
**命名空间管理**：`%who`、`%who_ls`、`%whos`、`%reset`、`%reset_selective`、`%xdel`
**历史操作**：`%history`、`%recall`、`%rerun`
**扩展管理**：`%load_ext`、`%unload_ext`、`%reload_ext`、`%autoreload`（需加载扩展）
**显示控制**：`%colors`、`%xmode`、`%pprint`、`%precision`、`%page`、`%display`
**代码加载/保存**：`%load`、`%loadpy`、`%save`、`%pastebin`、`%edit`、`%pycat`
**日志**：`%logstart`、`%logstop`、`%logon`、`%logoff`、`%logstate`
**配置**：`%config`、`%lsmagic`、`%magic`、`%quickref`、`%automagic`、`%gui`、`%doctest_mode`、`%notebook`
**包管理**：`%pip`、`%conda`、`%mamba`、`%micromamba`、`%uv`
**集成**：`%matplotlib`、`%pylab`、`%killbgscripts`、`%autoawait`
**代码包装**：`%code_wrap`

### 内置单元魔法清单

BUILTIN_LAZY_MAGICS 声明的内置单元魔法 [F-342]：

| 单元魔法 | 功能 |
|---------|------|
| `%%html` | 渲染 HTML |
| `%%javascript`/`%%js` | 执行 JavaScript |
| `%%latex` | 渲染 LaTeX |
| `%%markdown` | 渲染 Markdown |
| `%%svg` | 渲染 SVG |
| `%%capture` | 捕获输出 |
| `%%code_wrap` | 代码包装 |
| `%%debug` | 单元级调试 |
| `%%prun` | 性能分析 |
| `%%time` | 计时 |
| `%%timeit` | 基准测试 |
| `%%writefile` | 写入文件 |
| `%%script`/`%%!`/`%%sx`/`%%system` | 执行脚本命令 |

### 默认脚本魔法解释器

`default_script_magics()` 提供默认脚本解释器 [F-343]：`sh`、`bash`、`perl`、`ruby`、`python`、`python2`、`python3`、`pypy`。Windows 系统额外添加 `cmd`。

## Automagic 自动魔法模式

当 `auto_magic` 为 True（默认值 [F-304]），行魔法不需要 `%` 前缀即可调用。PrefilterManager 在输入预处理阶段检测无前缀的行魔法名并自动转换 [F-460][F-461]。

```python
# automagic 开启时，以下两种写法等价：
In [1]: pwd          # automagic 自动转换为 %pwd
Out[1]: '/home/user'

In [2]: %pwd
Out[2]: '/home/user'

# 关闭 automagic
In [3]: %automagic off
Automagic is OFF, % prefix IS needed for line magics.

In [4]: pwd          # 现在 pwd 被当作 Python 变量
NameError: name 'pwd' is not defined
```

单元魔法（`%%`）始终需要前缀，不能省略——因为单元魔法的参数跨越多个行，无法通过简单的行首检测判断。

## 魔法查找与调用流程

```
用户输入: "%timeit sum(range(1000))"
  │
  ▼
InputTransformer2 识别 ESC_MAGIC 前缀
  │ 转换为: get_ipython().run_line_magic("timeit", "sum(range(1000))")
  ▼
InteractiveShell.run_line_magic("timeit", "sum(range(1000))")  [F-222]
  │
  ▼
MagicsManager.find("line", "timeit")  [F-311]
  ├── 检查 magics["line"]["timeit"]
  ├── 如果是 LazyMagic → _resolve() → load_lazy("timeit")  [F-309]
  │     ├── 解析 spec: "IPython.core.magics.execution:ExecutionMagics"
  │     ├── import IPython.core.magics.execution
  │     ├── 实例化 ExecutionMagics(shell)
  │     └── register() 注册所有 @line_magic/@cell_magic 方法
  └── 返回实际可调用对象
  │
  ▼
变量展开（如果没有 @no_var_expand）
  │  {var} 和 $var 从 user_ns 中插值替换
  ▼
调用魔法函数（处理 @needs_local_scope 注入 local_ns）
  │
  ▼
返回结果（@output_can_be_silenced 检查分号静默）
```

## 自定义魔法示例

```python
from IPython.core.magic import (Magics, magics_class, line_magic, 
                                cell_magic, needs_local_scope, no_var_expand)
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring

@magics_class
class SQLMagics(Magics):
    """执行 SQL 查询的自定义魔法"""
    
    @needs_local_scope
    @line_magic
    def sql(self, line, local_ns=None):
        """执行 SQL 查询，结果可在本地命名空间中使用"""
        import sqlite3
        conn = local_ns.get('conn', sqlite3.connect(':memory:'))
        cursor = conn.execute(line)
        results = cursor.fetchall()
        for row in results:
            print(row)
        return results
    
    @no_var_expand
    @cell_magic
    def sql_script(self, line, cell):
        """执行多行 SQL 脚本，不展开变量"""
        conn_name = line.strip() or 'conn'
        conn = self.shell.user_ns.get(conn_name)
        if conn is None:
            print(f"Connection '{conn_name}' not found")
            return
        conn.executescript(cell)
        print("SQL script executed successfully")

# 在扩展中加载
def load_ipython_extension(ip):
    ip.register_magics(SQLMagics)
```

## 相关概念

- [自定义魔法开发](11-custom-magics.md)
- [代码执行管线](05-execution-pipeline.md)
- [输入转换与特殊语法](07-input-transform.md)
- [扩展系统](09-extension-system.md)
- [信源参考 - 魔法系统](../references/magic-source.md)
