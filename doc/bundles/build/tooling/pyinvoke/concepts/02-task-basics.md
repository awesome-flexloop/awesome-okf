---
type: Concept
title: Task 基础
description: Task 类详解：@task 参数、任务名与别名、默认任务、帮助文本、pre/post 钩子、autoprint、iterable/incrementable 参数
tags: [pyinvoke, task, decorator, "@task", call]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# Task 基础

Task（任务）是 Invoke 的核心概念。每个任务对应一个被 `@task` 装饰器标记的 Python 函数。本文档详解 `@task` 装饰器的所有参数、Task 类的关键方法，以及相关的 Call/call 机制。

## @task 装饰器详解

`@task` 装饰器用于将普通 Python 函数转换为 Invoke 任务。它既可以不带括号使用（无额外配置），也可以带括号并传入关键字参数进行精细配置。

### 无参数形式

最简单的用法，不需要额外配置时可以省略括号：

```python
from invoke import task

@task
def build(c):
    """构建项目。"""
    c.run("echo building")
```

### 带参数形式

当需要配置任务行为时，使用带括号的形式：

```python
@task(
    name="my-build",
    aliases=["b"],
    default=True,
    help={"target": "构建目标目录"},
    pre=[clean],
    post=[notify],
    autoprint=True,
)
def build(c, target="dist"):
    """构建项目到指定目录。"""
    c.run(f"echo building to {target}")
```

### @task 参数完整列表

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | 函数名 | CLI 中使用的任务名，覆盖 Python 函数名 |
| `aliases` | `Iterable[str]` | `()` | 一个或多个任务别名 |
| `default` | `bool` | `False` | 是否为所在集合的默认任务 |
| `positional` | `Iterable[str]` | `None`（自动推断） | 指定哪些参数作为位置参数 |
| `optional` | `Iterable[str]` | `()` | 指定哪些参数是"可选值"参数（即可作为布尔标志也可接受值） |
| `iterable` | `Iterable[str]` | `None` | 指定哪些参数是可迭代的（可多次指定，累积为列表） |
| `incrementable` | `Iterable[str]` | `None` | 指定哪些参数是可递增的（如 `-vvv` 增加详细程度） |
| `auto_shortflags` | `bool` | `True` | 是否自动生成短标志（如 `--verbose` → `-v`） |
| `help` | `Dict[str, str]` | `None` | 参数名到帮助文本的映射 |
| `pre` | `List[Task/Call]` | `[]` | 前置任务列表，当前任务执行前自动执行 |
| `post` | `List[Task/Call]` | `[]` | 后置任务列表，当前任务执行后自动执行 |
| `autoprint` | `bool` | `False` | 是否自动打印任务的返回值 |
| `klass` | `Type[Task]` | `Task` | 自定义 Task 子类（高级用法） |

## 任务名与别名

### 自定义任务名（name）

默认情况下，任务名取自 Python 函数名。使用 `name` 参数可以覆盖：

```python
@task(name="compile")
def build_project(c):
    """编译项目。"""
    pass
```

此时命令行调用为 `inv compile` 而非 `inv build-project`。

### 别名（aliases）

为任务设置一个或多个别名，允许用户用不同名称调用同一任务：

```python
@task(aliases=["b", "build-all"])
def build(c):
    """构建项目。"""
    pass
```

以下命令都可以执行该任务：

```bash
inv build
inv b
inv build-all
```

### 下划线自动转短横线

Invoke 默认将函数名中的下划线（`_`）转换为命令行中的短横线（`-`）：

```python
@task
def run_tests(c):  # CLI 名称为 run-tests
    pass
```

命令行调用：

```bash
inv run-tests
```

Python 代码中仍然使用 `run_tests` 引用。

## 默认任务（default）

将任务标记为集合的默认任务后，直接调用集合名（不带任务名）时自动执行该任务：

```python
@task(default=True)
def build(c):
    """默认构建任务。"""
    print("building...")

@task
def test(c):
    print("testing...")
```

```bash
inv        # 执行 build（因为它是默认任务）
inv build  # 也可以显式执行
inv test   # 执行 test
```

一个集合只能有一个默认任务，设置多个会抛出 `ValueError`。

## 帮助文本（help）

通过 `help` 参数为命令行选项提供帮助文本，显示在 `--help` 输出中：

```python
@task(help={
    "target": "构建输出目录，默认为 dist",
    "clean": "构建前是否清理旧的构建产物",
})
def build(c, target="dist", clean=False):
    """构建项目。"""
    if clean:
        c.run(f"rm -rf {target}")
    c.run(f"echo building to {target}")
```

对于包含下划线的参数名，`help` 字典中既可以用下划线版本也可以用短横线版本。

函数的 docstring 会自动成为任务的整体帮助描述。

## 前置与后置钩子（pre / post）

### 前置任务（pre）

`pre` 参数指定在当前任务执行前自动运行的任务：

```python
@task
def clean(c):
    c.run("rm -rf dist")

@task(pre=[clean])
def build(c):
    c.run("echo building")
```

执行 `inv build` 时，先执行 `clean` 再执行 `build`。

### 后置任务（post）

`post` 参数指定在当前任务执行后自动运行的任务：

```python
@task
def notify(c):
    print("构建完成！")

@task(post=[notify])
def build(c):
    c.run("echo building")
```

### 为前置任务传递参数（call 函数）

当需要为前置/后置任务传递特定参数时，使用 `call()` 函数：

```python
from invoke import task, call

@task
def setup(c, clean=False):
    if clean:
        c.run("rm -rf target")
    c.run("echo setting up")

@task(pre=[call(setup, clean=True)])
def release(c):
    """发布构建，以干净状态开始。"""
    c.run("echo releasing")
```

`call(task, *args, **kwargs)` 创建一个 `Call` 对象，封装了任务及其预绑定的参数。

### 便捷形式：位置参数作为 pre

`@task` 的非关键字位置参数会自动作为 `pre` 的值：

```python
@task(clean)  # 等价于 @task(pre=[clean])
def build(c):
    pass
```

但不能同时给位置参数和 `pre` 关键字参数，否则会抛出 `TypeError`。

## 自动打印返回值（autoprint）

设置 `autoprint=True` 后，任务的返回值会自动打印到标准输出：

```python
@task(autoprint=True)
def version(c):
    """显示版本号。"""
    return "1.0.0"
```

```bash
$ inv version
1.0.0
```

## 参数类型

### 可迭代参数（iterable）

标记为 `iterable` 的参数可以在命令行中多次指定，值累积为列表：

```python
@task(iterable=["tag"])
def build(c, tag=None):
    """构建并打标签。"""
    for t in tag:
        print(f"标签: {t}")
```

```bash
inv build --tag v1.0 --tag latest --tag stable
# tag 的值为 ["v1.0", "latest", "stable"]
```

默认为空列表 `[]`。

### 可递增参数（incrementable）

标记为 `incrementable` 的参数可通过重复短标志递增值，常用于控制详细程度：

```python
@task(incrementable=["verbose"])
def test(c, verbose=0):
    """运行测试。"""
    if verbose >= 3:
        print("DEBUG 级别输出")
    elif verbose >= 2:
        print("INFO 级别输出")
    elif verbose >= 1:
        print("WARNING 级别输出")
```

```bash
inv test            # verbose = 0
inv test -v         # verbose = 1
inv test -vv        # verbose = 2
inv test -vvv       # verbose = 3
```

### 可选值参数（optional）

标记为 `optional` 的参数既可以作为布尔标志（不给值时为 `True`），也可以接受显式值：

```python
@task(optional=["log"])
def serve(c, log=None):
    """启动服务器。"""
    if log is True:
        print("使用默认日志路径")
    elif log:
        print(f"日志路径: {log}")
    else:
        print("不记录日志")
```

```bash
inv serve           # log = None
inv serve --log     # log = True（布尔标志）
inv serve --log=/var/log/app.log  # log = "/var/log/app.log"
```

### 位置参数（positional）

默认情况下，没有默认值的参数自动被视为位置参数。使用 `positional` 参数可以显式控制哪些参数按位置传递：

```python
@task(positional=["target"])
def build(c, target, clean=False, optimize=True):
    pass
```

```bash
inv build dist          # target = "dist"
inv build dist --clean  # target = "dist", clean = True
```

设置 `positional=[]`（空列表）会强制所有参数必须以显式标志形式给出。

### 自动短标志（auto_shortflags）

`auto_shortflags=True`（默认）时，Invoke 自动为每个参数生成单字符短标志。它选择参数名中第一个尚未被其他参数占用的字符：

```python
@task
def build(c, target="dist", clean=False):
    pass
```

自动短标志可能为：`-t` 对应 `--target`，`-c` 对应 `--clean`。

设置 `auto_shortflags=False` 可禁用此行为。

## Task 类关键方法与属性

`@task` 装饰器创建的对象是 `Task` 类的实例。以下是其关键 API：

### 核心属性

- `task.name`：任务的 CLI 名称
- `task.aliases`：别名元组
- `task.is_default`：是否为默认任务
- `task.body`：原始的 Python 函数对象
- `task.pre` / `task.post`：前置/后置任务列表
- `task.help`：帮助文本字典
- `task.autoprint`：是否自动打印返回值
- `task.called`：布尔值，任务是否已被调用过
- `task.times_called`：任务被调用的次数

### 关键方法

- `task.__call__(c, *args, **kwargs)`：执行任务。第一个参数必须是 Context 实例，否则抛出 `TypeError`
- `task.argspec(body)`：返回去掉 Context 参数后的函数签名（`inspect.Signature` 对象）
- `task.get_arguments(ignore_unknown_help=None)`：返回该任务的 `Argument` 对象列表，用于构建 CLI 解析器

示例：

```python
@task
def build(c, target="dist"):
    pass

print(build.name)        # "build"
print(build.aliases)     # ()
print(build.is_default)  # False
```

## Call 对象与 call() 函数

`Call` 类表示一个任务的带参数调用，类似于 `functools.partial`，但带有任务执行所需的额外元数据。

```python
from invoke import task, call, Call

@task
def greet(c, name="World", exclaim=False):
    msg = f"Hello, {name}"
    if exclaim:
        msg += "!"
    print(msg)

# 使用 call() 创建预绑定参数的调用
excited_greet = call(greet, name="Alice", exclaim=True)
# 等价于 Call(greet, kwargs={"name": "Alice", "exclaim": True})
```

`Call` 对象主要用于 pre/post 列表中为前置/后置任务传递参数。它也支持：

- `call.clone(into=None, with_=None)`：创建 Call 的副本，可转换为子类或追加参数
- `call.make_context(config, core_parse_result)`：为该调用生成合适的 Context 对象
- 属性代理：`Call` 通过 `__getattr__` 代理到底层 Task 对象，可以直接访问 `call.name` 等属性

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [Context 对象](/concepts/03-context-object.md)
- [Collection 与命名空间](/concepts/04-collection-namespace.md)
- [PyInvoke 简介](/concepts/00-introduction.md)
- [PyInvoke 源码信源登记](/references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](/references/pyinvoke-source.md)；Task 类与 `@task` 装饰器定义于 `invoke/tasks.py`。
