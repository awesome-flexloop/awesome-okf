---
type: Reference
title: 魔法命令系统 API 参考
description: MagicsManager、Magics 基类、魔法装饰器及内置魔法命令注册系统的完整 API 参考
tags: [api, magic, magics, decorator, reference, ipython]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ipython-core-magic
    resource: /references/magic-source.md
    title: IPython/core/magic.py MagicsManager & Magics base class
  - id: ipython-core-magics-init
    resource: /references/magic-source.md
    title: IPython/core/magics/__init__.py Builtin magics classes
  - id: ipython-core-magics-table
    resource: /references/magic-source.md
    title: IPython/core/magics/_table.py BUILTIN_LAZY_MAGICS & MAGICS_CLASSES
---

# 魔法命令系统 API 参考

IPython 魔法系统提供了 `%` 前缀的行魔法和 `%%` 前缀的单元格魔法，定义在 `core/magic.py`。内置魔法通过延迟加载机制注册，定义在 `core/magics/_table.py`。

## 全局常量

```python
# 转义字符
ESC_MAGIC = "%"    # 行魔法前缀
ESC_MAGIC2 = "%%"  # 单元格魔法前缀

magic_kinds = ("line", "cell")
magic_spec = ("line", "cell", "line_cell")
magic_escapes = {"line": ESC_MAGIC, "cell": ESC_MAGIC2}

# 属性标记
MAGIC_NO_VAR_EXPAND_ATTR = "_ipython_magic_no_var_expand"
MAGIC_OUTPUT_CAN_BE_SILENCED = "_ipython_magic_output_can_be_silenced"
```

## MagicsManager

文件：`IPython/core/magic.py`

```python
class MagicsManager(Configurable):
    """Object that handles all magic-related functionality for IPython."""
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `magics` | Dict | 两级字典：`{'line': {name: callable}, 'cell': {name: callable}}`，存储实际可调用对象 |
| `lazy_magics` | Dict | 延迟加载魔法映射：`{name: "module:Class" 或 "module"}`，首次调用时才导入 |
| `registry` | Dict | 已注册的 Magics 实例字典：`{ClassName: instance}`（实际类型 `_MagicsRegistry`） |
| `shell` | Instance | 关联的 InteractiveShell 实例 |
| `auto_magic` | Bool | 是否自动调用行魔法（无需 `%` 前缀），默认 True |
| `user_magics` | Instance(UserMagics) | 用户自定义魔法占位类实例 |

### 核心方法

```python
def register(self, *magic_objects: type[Magics] | Magics) -> None:
    """注册一个或多个 Magics 类或实例。
    类会被自动实例化（传入 shell=self.shell）。
    """

def register_function(
    self,
    func: Callable,
    magic_kind: str = "line",      # 'line' | 'cell' | 'line_cell'
    magic_name: str | None = None,  # 默认使用函数名
) -> None:
    """将独立函数注册为魔法命令。
    函数签名：行魔法 def f(line)；单元格魔法 def f(line, cell)；
    双重魔法 def f(line, cell=None)
    """

def register_alias(
    self,
    alias_name: str,
    magic_name: str,
    magic_kind: str = "line",      # 'line' | 'cell'
    magic_params: str | None = None,
) -> None:
    """注册魔法别名。调用时转发到目标魔法，magic_params 作为前缀参数。"""

def register_lazy(
    self,
    name: str,
    fully_qualified_name: str,     # "package.module" 或 "package.module:MagicsClass"
    magic_kind: str = "line_cell",
) -> None:
    """延迟注册魔法，首次调用时才导入模块或类。
    - "package.module"：作为扩展加载（%load_ext 等价）
    - "package.module:MagicsClass"：直接导入类并注册
    """

def find(self, magic_kind: str, magic_name: str) -> Callable | None:
    """查找已注册魔法，如为 LazyMagic 则自动加载。返回 None 表示未找到。"""

def lsmagic(self) -> dict[str, dict[str, Any]]:
    """返回当前可用魔法字典：{'line': {...}, 'cell': {...}}"""

def lsmagic_docs(
    self, brief: bool = False, missing: str = ""
) -> dict[str, dict[str, str]]:
    """返回魔法文档字典，brief=True 仅返回首行文档。会强制加载所有非扩展类魔法。"""

def load_lazy(self, magic_name: str) -> None:
    """导入并注册指定延迟魔法。"""

def load_all_lazy_magics(self) -> None:
    """导入并注册所有 module:Class 形式的延迟魔法（不触发扩展加载）。"""

def auto_status(self) -> str:
    """返回 automagic 状态描述字符串。"""
```

### _MagicsRegistry 内部类

```python
class _MagicsRegistry(dict[str, Any]):
    """MagicsManager.registry 的类型，缺失键时自动加载对应的 lazy magics 类。"""
    def __missing__(self, key: str) -> Any:
        # 查找 lazy_magics 中以 :key 结尾的 spec，加载后重试
        ...
```

### LazyMagic 类

```python
class LazyMagic:
    """延迟魔法占位符，调用或访问属性时自动解析为真实魔法。"""
    def __init__(self, manager, spec, magic_kind, magic_name): ...
    def _resolve(self) -> Callable: ...
    def __call__(self, *args, **kwargs): return self._resolve()(*args, **kwargs)
    def __getattr__(self, name): return getattr(self._resolve(), name)
    def __repr__(self): return f"<unloaded magic {self._name} from {self.spec}>"
```

## Magics 基类

文件：`IPython/core/magic.py`

```python
class Magics(Configurable):
    """Base class for implementing magic functions."""
```

### 类属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `magics` | dict | 类级别：`{'line': {name: method_name}, 'cell': {name: method_name}}` |
| `registered` | bool | 类装饰器 `@magics_class` 是否正确应用的标志 |
| `options_table` | dict | 每个魔法的命令行选项缓存 |
| `shell` | InteractiveShell | 关联的 Shell 实例 |

### 核心方法

```python
def __init__(self, shell=None, **kwargs):
    """初始化 Magics 实例。必须先应用 @magics_class 装饰器。"""
    # 将类级别 magics 中的方法名替换为绑定方法
    ...

def parse_options(
    self, arg_str: str, opt_str: str, *long_opts: str,
    mode: str = "string",    # 'string' | 'list'
    list_all: bool = False,
    posix: bool = True,
    strict: bool = True,
    preserve_non_opts: bool = False,
) -> tuple[Struct, str | list]:
    """解析魔法参数，类 getopt 接口。返回 (opts_struct, args)。"""

def arg_err(self, func: Callable) -> None:
    """参数错误时打印函数文档。"""

def format_latex(self, strng: str) -> str:
    """将魔法命令格式化为 LaTeX。"""
```

### 自定义 Magics 类模板

```python
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic

@magics_class
class MyMagics(Magics):
    @line_magic
    def mymagic(self, line):
        """行魔法：%mymagic args"""
        return f"Got: {line}"

    @line_magic("myalias")
    def my_magic_with_alias(self, line):
        """行魔法，名称为 myalias：%myalias args"""
        ...

    @cell_magic
    def mycell(self, line, cell):
        """单元格魔法：%%mycell opts\ncell body"""
        return f"Line: {line}\nCell: {cell}"

    @line_cell_magic
    def mydual(self, line, cell=None):
        """既可作行魔法也可作单元格魔法。
        - %mydual args 时 cell=None
        - %%mydual args\\nbody 时 cell 为单元格内容
        """
        if cell is None:
            return f"Line mode: {line}"
        return f"Cell mode: {line} / {cell}"

# 注册
ip = get_ipython()
ip.magics_manager.register(MyMagics)
```

## 装饰器

### 类装饰器

```python
def magics_class(cls: type[Magics]) -> type[Magics]:
    """类装饰器，所有 Magics 子类必须使用。
    将方法装饰器记录的魔法信息从全局 dict 复制到类，并清空全局。
    """
```

### 方法装饰器（用于 Magics 子类中）

```python
# 在 @magics_class 装饰的类中使用
line_magic = _method_magic_marker("line")
cell_magic = _method_magic_marker("cell")
line_cell_magic = _method_magic_marker("line_cell")
```

### 函数装饰器（用于独立函数，需要 IPython 已运行）

```python
# 在 startup 文件或 IPython 会话中使用，立即注册
register_line_magic = _function_magic_marker("line")
register_cell_magic = _function_magic_marker("cell")
register_line_cell_magic = _function_magic_marker("line_cell")
```

使用示例：

```python
# 方法装饰器（在 Magics 子类中）
@line_magic
def mymagic(self, line): ...

@line_magic("custom_name")
def mymagic(self, line): ...

# 函数装饰器（在 IPython 运行时）
@register_line_magic
def mymagic(line):
    print(f"You called %mymagic with: {line}")

@register_line_cell_magic("dothings")
def dothings(line, cell=None): ...
```

### 辅助装饰器

```python
def needs_local_scope(func: F) -> F:
    """标记魔法需要访问局部作用域。
    被标记的魔法调用时会额外传入 local_ns 参数。
    """
    func.needs_local_scope = True
    return func

def no_var_expand(magic_func: F) -> F:
    """标记魔法不需要变量展开（{var} / $var 插值）。
    适用于执行 Python 代码的魔法，如 %timeit、%time。
    """
    setattr(magic_func, MAGIC_NO_VAR_EXPAND_ATTR, True)
    return magic_func

def output_can_be_silenced(magic_func: F) -> F:
    """标记魔法输出可被末尾分号静默。"""
    setattr(magic_func, MAGIC_OUTPUT_CAN_BE_SILENCED, True)
    return magic_func
```

使用示例：

```python
@line_magic
@needs_local_scope
def my_eval(self, line, local_ns=None):
    """需要局部作用域的魔法"""
    return eval(line, self.shell.user_ns, local_ns)
```

## MagicAlias 类

```python
class MagicAlias:
    """魔法别名，调用时转发到目标魔法。"""
    def __init__(self, shell, magic_name, magic_kind, magic_params=None): ...
    def __call__(self, *args, **kwargs):
        # 查找目标魔法并调用，防止无限递归
        ...
```

## 内置魔法注册

文件：`IPython/core/magics/_table.py`

### MAGICS_CLASSES 映射

| 类名 | 模块 | 说明 |
|------|------|------|
| `BasicMagics` | `IPython.core.magics.basic` | 基础魔法（colors, xmode, lsmagic 等） |
| `AsyncMagics` | `IPython.core.magics.basic` | 异步魔法（autoawait） |
| `AutoMagics` | `IPython.core.magics.auto` | 自动魔法（autocall, automagic） |
| `CodeMagics` | `IPython.core.magics.code` | 代码魔法（edit, load, save, pastebin） |
| `ConfigMagics` | `IPython.core.magics.config` | 配置魔法（config） |
| `DisplayMagics` | `IPython.core.magics.display` | 显示魔法（%%html, %%javascript 等） |
| `ExecutionMagics` | `IPython.core.magics.execution` | 执行魔法（%timeit, %run, %debug, %prun 等） |
| `ExtensionMagics` | `IPython.core.magics.extension` | 扩展魔法（%load_ext, %unload_ext, %reload_ext） |
| `HistoryMagics` | `IPython.core.magics.history` | 历史魔法（%history, %recall, %rerun） |
| `LoggingMagics` | `IPython.core.magics.logging` | 日志魔法（%logstart, %logon, %logoff 等） |
| `NamespaceMagics` | `IPython.core.magics.namespace` | 命名空间魔法（%who, %whos, %reset, %pdef 等） |
| `OSMagics` | `IPython.core.magics.osm` | 系统魔法（%cd, %pwd, %alias, !cmd, %%writefile 等） |
| `PackagingMagics` | `IPython.core.magics.packaging` | 包管理魔法（%pip, %conda, %uv 等） |
| `PylabMagics` | `IPython.core.magics.pylab` | Pylab 魔法（%matplotlib, %pylab） |
| `ScriptMagics` | `IPython.core.magics.script` | 脚本魔法（%%script, %%bash, %%python 等） |

### BUILTIN_LAZY_MAGICS 内置延迟魔法列表

#### 行魔法（line）

| 分类 | 魔法名 |
|------|--------|
| AutoMagics | `autocall`, `automagic` |
| BasicMagics | `alias_magic`, `colors`, `doctest_mode`, `gui`, `lsmagic`, `magic`, `notebook`, `page`, `pprint`, `precision`, `quickref`, `xmode` |
| AsyncMagics | `autoawait` |
| CodeMagics | `edit`, `load`, `loadpy`, `pastebin`, `save` |
| ConfigMagics | `config` |
| ExecutionMagics | `code_wrap`, `debug`, `macro`, `pdb`, `prun`, `run`, `tb`, `time`, `timeit` |
| ExtensionMagics | `load_ext`, `reload_ext`, `unload_ext` |
| HistoryMagics | `history`, `recall`, `rerun` |
| LoggingMagics | `logoff`, `logon`, `logstart`, `logstate`, `logstop` |
| NamespaceMagics | `pdef`, `pdoc`, `pfile`, `pinfo`, `pinfo2`, `psearch`, `psource`, `reset`, `reset_selective`, `who`, `who_ls`, `whos`, `xdel` |
| OSMagics | `alias`, `bookmark`, `cd`, `dhist`, `dirs`, `env`, `popd`, `pushd`, `pwd`, `pycat`, `rehashx`, `sc`, `set_env`, `sx`, `system`, `unalias` |
| PackagingMagics | `conda`, `mamba`, `micromamba`, `pip`, `uv` |
| PylabMagics | `matplotlib`, `pylab` |
| ScriptMagics | `killbgscripts` |

#### 单元格魔法（cell）

| 分类 | 魔法名 |
|------|--------|
| DisplayMagics | `html`, `javascript`, `js`, `latex`, `markdown`, `svg` |
| ExecutionMagics | `capture`, `code_wrap`, `debug`, `prun`, `time`, `timeit` |
| OSMagics | `!`, `sx`, `system`, `writefile` |
| ScriptMagics | `script`（以及动态生成的 `%%bash`, `%%python`, `%%ruby` 等） |

#### 脚本魔法（ScriptMagics 动态生成）

默认脚本魔法（`default_script_magics()`）：
- 跨平台：`sh`, `bash`, `perl`, `ruby`, `python`, `python2`, `python3`, `pypy`
- Windows 额外：`cmd`

可通过 `c.ScriptMagics.script_magics` 配置自定义解释器。

### UserMagics

```python
@magics_class
class UserMagics(Magics):
    """用户自定义魔法占位类，register_function 将方法添加到此实例。"""
```

## 使用示例

```python
from IPython import get_ipython
ip = get_ipython()

# 查看所有魔法
ip.magics_manager.lsmagic()

# 注册函数魔法
@register_line_magic
def hello(line):
    print(f"Hello, {line}!")

# 使用魔法
ip.run_line_magic('hello', 'World')  # 或直接 %hello World

# 通过 MagicsManager 注册
ip.magics_manager.register_function(
    lambda line: print(f"Square: {int(line)**2}"),
    magic_kind='line',
    magic_name='square'
)

# 注册 Magics 类
ip.magics_manager.register(MyMagics)

# 注册别名
ip.magics_manager.register_alias('lm', 'lsmagic')

# 查找魔法
fn = ip.magics_manager.find('line', 'timeit')

# 禁用 automagic
ip.magics_manager.auto_magic = False

# 延迟注册自定义魔法
ip.magics_manager.register_lazy(
    'my_magic',
    'my_package.my_module:MyMagics',
    magic_kind='line'
)
```

## 相关概念

- [魔法系统](../concepts/04-magic-system.md)
- [代码执行管线](../concepts/05-execution-pipeline.md)
- [InteractiveShell API 参考](interactiveshell-source.md)
- [扩展系统 API 参考](extension-source.md)
