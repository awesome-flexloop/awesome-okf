---
type: Concept
title: 执行模型
description: Executor 执行流程、Call 对象、预处理/后处理、dedupe 去重、异常处理体系
tags: [pyinvoke, executor, Call, pre, post, dedupe, exception, Failure, execute, normalize]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# 执行模型

Executor（执行器）是 Invoke 任务调度的核心引擎。当 Program 完成 CLI 解析后，会创建 Executor 实例并将任务列表交给它执行。Executor 负责将命令行输入转化为具体的 Task 调用序列，处理前置/后置任务链、任务去重、逐任务配置加载和异常传播。

## Executor 构造

`Executor(collection, config=None, core=None)` 接收三个核心依赖：

| 参数 | 类型 | 说明 |
|------|------|------|
| `collection` | `Collection` | 任务集合树，用于按名称查找 Task 对象 |
| `config` | `Config` | 配置对象；为 None 时创建空 Config |
| `core` | `ParseResult` | 核心 CLI 参数解析结果；为 None 时创建空 ParseResult |

Executor 类被设计为可子类化扩展。Program 在 `execute()` 方法中确定使用哪个 Executor 类：优先使用构造参数 `executor_class`，其次使用配置项 `tasks.executor_class`（支持点分路径如 `"myapp.MyExecutor"`），最后回退到默认 `Executor`。

## execute() 执行流水线

`Executor.execute(*tasks)` 是执行入口，接受零个或多个任务规格，返回 `Dict[Task, Result]` 映射。核心执行流水线如下：

```
normalize() → expand_calls() → dedupe() → 逐 Call 执行
```

### 完整流程

1. **normalize(tasks)**：将各种形式的任务输入统一转换为 `Call` 对象列表
2. **expand_calls(calls)**：递归展开每个 Call 的前置（pre）和后置（post）任务
3. **dedupe(expanded)**：根据配置决定是否去重相同的 Call
4. **逐 Call 执行**：
   a. 加载该 Call 对应 Collection 的配置（`config.load_collection()`）
   b. 加载 shell 环境变量配置（`config.load_shell_env()`）
   c. 通过 `call.make_context()` 创建 Context
   d. 调用 Task 函数：`call.task(context, *call.args, **call.kwargs)`
   e. 如果是直接任务且 `autoprint=True`，打印返回值
   f. 记录结果到 `results` 字典

如果 `execute()` 没有传入任何任务参数，且 Collection 设置了默认任务，则执行默认任务。

## normalize()：输入标准化

`Executor.normalize(tasks)` 将多种任务输入格式统一为 `List[Call]`：

支持的输入格式：

| 输入类型 | 示例 | 说明 |
|----------|------|------|
| 字符串 | `"build"` | 按名称查找任务，无参数调用 |
| 二元组 | `("build", {"clean": True})` | 名称 + kwargs 字典 |
| ParserContext | CLI 解析结果 | 从 `.name` 获取任务名，`.as_kwargs` 获取参数 |

```python
# 字符串形式
executor.execute("build", "test")

# (name, kwargs) 元组形式
executor.execute(
    ("build", {"clean": True}),
    ("deploy", {"env": "production"})
)

# 混合形式
executor.execute("clean", ("build", {"prod": True}))
```

对于字符串和元组形式，`normalize()` 通过 `self.collection[name]` 查找对应的 Task 对象，然后构造 `Call(task, kwargs=kwargs, called_as=name)`。

## Call：带参数的任务调用

`Call` 对象表示一个任务的具体调用，包含 Task 引用和调用参数：

```python
class Call:
    def __init__(self, task, called_as=None, args=None, kwargs=None):
        self.task = task       # Task 对象
        self.called_as = called_as  # 调用时使用的名称（可能是别名）
        self.args = args or tuple()  # 位置参数
        self.kwargs = kwargs or dict()  # 关键字参数
```

### Call 与 Task 的关系

- **Task** 是任务定义（函数 + 元数据），不包含调用参数
- **Call** 是 Task 的一次具体调用，绑定了参数值
- 同一个 Task 可以对应多个不同参数的 Call

### Call 的属性代理

`Call.__getattr__` 将未定义的属性代理到内部的 Task 对象，因此可以直接通过 Call 访问 Task 的属性：

```python
call = Call(build_task, kwargs={"clean": True})
print(call.name)      # "build"（代理到 Task.name）
print(call.pre)       # [...]（代理到 Task.pre，前置任务列表）
print(call.post)      # [...]（代理到 Task.post，后置任务列表）
print(call.body)      # 原始函数对象
```

### Call.__eq__：去重依据

两个 Call 相等当且仅当它们的 `task`、`args`、`kwargs` 都相同。`called_as` 不参与相等性比较，因为通过别名调用同一任务且参数相同时应被视为同一调用。这是 `dedupe()` 方法的基础。

### make_context()

`call.make_context(config, core_parse_result)` 为本次调用创建 Context 对象：

```python
def make_context(self, config, core_parse_result):
    return Context(config=config, remainder=core_parse_result.remainder)
```

子类（如 Fabric 的 Connection 子类）可以覆盖此方法以提供自定义 Context。

### call() 便捷函数

`call(task, *args, **kwargs)` 是创建 Call 对象的便捷函数，主要用于 pre/post 参数化：

```python
from invoke import task, call

@task
def setup(c, clean=False):
    if clean:
        c.run("rm -rf dist/")
    c.run("mkdir -p dist")

@task(pre=[call(setup, clean=True)])
def build(c):
    c.run("python -m build")
```

直接在 `pre` 中传入 Task 对象（如 `pre=[setup]`）会无参数调用前置任务；使用 `call()` 可以为前置任务传递参数。

## expand_calls()：前置/后置任务展开

`Executor.expand_calls(calls)` 递归展开每个 Call 的前置和后置任务链，生成最终的执行顺序：

```python
def expand_calls(self, calls):
    ret = []
    for call in calls:
        if isinstance(call, Task):
            call = Call(call)
        ret.extend(self.expand_calls(call.pre))   # 前置任务（递归展开）
        ret.append(call)                          # 任务本身
        ret.extend(self.expand_calls(call.post))  # 后置任务（递归展开）
    return ret
```

### pre/post 定义方式

通过 `@task` 装饰器的 `pre` 和 `post` 参数定义前置/后置任务：

```python
@task
def clean(c):
    c.run("rm -rf dist/ build/")

@task
def lint(c):
    c.run("flake8 src/")

@task(pre=[clean, lint])
def build(c):
    c.run("python -m build")

@task(pre=[build])
def test(c):
    c.run("pytest")

@task(post=[clean])
def package(c):
    c.run("twine upload dist/*")
```

执行 `inv package` 时，展开顺序为：`clean` → `build`（其前置 `clean` 和 `lint`）→ `test`（如果 build 的 post 有）→ `package` → `clean`（后置）。

递归展开意味着 pre 任务自己的 pre 任务也会被包含进来，形成完整的依赖链。

## dedupe()：任务去重

`Executor.dedupe(calls)` 移除执行列表中重复的 Call：

```python
def dedupe(self, calls):
    deduped = []
    for call in calls:
        if call not in deduped:
            deduped.append(call)
    return dedup
```

去重基于 `Call.__eq__`：相同 Task + 相同 args + 相同 kwargs 视为同一调用。例如在上面的例子中，`clean` 既是 `build` 的前置任务又是 `package` 的后置任务，但去重后只会执行一次（第一次出现的位置）。

去重行为受配置项 `tasks.dedupe` 控制（默认为 `True`），CLI 标志 `--no-dedupe` 可以禁用去重。禁用后，同一个 Call 会按其在展开链中的位置多次执行。

## 逐 Call 配置加载

对于每个待执行的 Call，Executor 在调用前执行两步配置加载：

```python
collection_config = self.collection.configuration(call.called_as)
config.load_collection(collection_config)
config.load_shell_env()
context = call.make_context(config, core_parse_result=self.core)
result = call.task(*args, **call.kwargs)
```

### load_collection

根据任务的调用路径（`called_as`，如 `"db.migrate"`），从 Collection 树中获取该路径上所有层级的 `configure()` 设置，合并后加载到 Config 的 `_collection` 层。这使得子集合的配置只在执行该子集合中的任务时生效。

### load_shell_env

加载环境变量配置（`INVOKE_*`）。这一步必须在 collection 配置加载之后执行，因为环境变量的类型转换依赖于已合并配置中的默认值类型。

### 配置的跨任务共享

Config 对象在所有 Call 之间共享，因此一个任务对配置的运行时修改（通过 `c.config.key = value`）会影响后续任务。collection 和 shell env 层在每次 Call 前会被重置（通过 `load_collection` 和 `load_shell_env`），但 modifications 层（运行时修改）会持续保留。

## 异常处理体系

Invoke 定义了清晰的异常层次结构：

```
Exception
├── Failure（命令执行失败基类）
│   ├── UnexpectedExit（非零退出码，warn=False 时抛出）
│   ├── CommandTimedOut（命令超时）
│   └── AuthFailure（认证失败，如 sudo 密码错误）
├── Exit（干净退出，替代 sys.exit）
├── ParseError（命令行解析错误）
├── CollectionNotFound（找不到任务集合）
├── ThreadException（IO 线程异常聚合）
├── WatcherError（StreamWatcher 错误）
│   └── ResponseNotAccepted（自动应答失败，如密码错误）
├── PlatformError（平台不支持）
├── AmbiguousEnvVar（环境变量键歧义）
├── UncastableEnvVar（环境变量类型转换失败）
├── UnknownFileType（不支持的配置文件格式）
├── UnpicklableConfigMember（配置文件含不可序列化对象）
└── SubprocessPipeError（子进程管道操作失败）
```

### Failure 异常

`Failure` 及其子类都携带一个 `result` 属性（Result 对象），包含命令执行的上下文信息（命令字符串、stdout、stderr、退出码等）。`Failure` 还可能携带 `reason` 属性（包装的 WatcherError）。

### Exit 异常

`Exit` 是 Invoke 内部用来替代 `sys.exit()` 的异常，便于测试时捕获退出请求而不真正终止进程。它支持 `message`（打印到 stderr 的消息）和 `code`（退出码）两个参数。`Program.run(exit=False)` 会捕获 Exit 异常而不调用 `sys.exit()`。

### ThreadException

当 IO 工作线程（stdout/stderr/stdin 处理线程）中发生非 WatcherError 异常时，这些异常被收集到 `ThreadException` 中，在主线程 wait 结束后统一抛出。`ThreadException.exceptions` 是一个 ExceptionWrapper 元组，每个包含线程的 kwargs 和异常信息（type、value、traceback）。

### 异常传播流程

```
Runner._finish()
├── IO 线程 join → 收集异常
│   ├── WatcherError → watcher_errors 列表 → 包装为 Failure 抛出
│   └── 其他异常 → thread_exceptions 列表 → ThreadException
├── 检查 timeout → CommandTimedOut
└── 检查退出码 → UnexpectedExit（warn=False 时）
```

在 Executor 层面，这些异常不会被捕获，会向上传播到 Program.run()，由 Program 决定打印错误信息和退出。

## 返回值

`execute()` 返回 `Dict[Task, Any]`，键是 Task 对象，值是任务函数的返回值。前置和后置任务的返回值也会被包含在字典中。注意去重后同一个 Task 只执行一次，因此即使它出现在多个位置，结果字典中也只有一个条目。

如果任务设置了 `autoprint=True`，其返回值会在执行后自动打印到 stdout（这主要用于 CLI 直接调用场景）。

## 相关概念

- [Task 基础](/concepts/02-task-basics.md)
- [Collection 与命名空间](/concepts/04-collection-namespace.md)
- [Runner 系统](/concepts/06-runners.md)
- [CLI 与 Program 类](/concepts/07-cli-program.md)
- [高级模式](/concepts/11-advanced-patterns.md)
- [PyInvoke 源码信源登记](/references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](/references/pyinvoke-source.md)；Executor 定义于 `invoke/executor.py`，Call 类和 call() 函数定义于 `invoke/tasks.py`，异常类定义于 `invoke/exceptions.py`。
