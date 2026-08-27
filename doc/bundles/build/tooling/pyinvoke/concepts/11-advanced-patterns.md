---
type: Concept
title: 高级模式
description: 自定义 Program/Executor/Runner、MockContext 测试、任务间调用、命名空间组织、嵌入使用、tab 补全
tags: [pyinvoke, advanced, custom-program, custom-runner, MockContext, testing, namespace, embedding, tab-completion]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# 高级模式

掌握了 Invoke 的基础概念（Task、Context、Runner、配置、CLI）之后，本章介绍进阶用法：自定义组件扩展、测试策略、命名空间组织、嵌入使用等高级模式，帮助你将 Invoke 从简单的任务运行器提升为可定制的自动化框架。

## 自定义 Program：构建捆绑式 CLI

Program 默认运行在"任务运行器模式"（`inv` 命令），从 tasks.py 中发现任务。通过创建 Program 子类或实例，可以构建"捆绑式命名空间"CLI——将 Invoke 的任务调度能力打包成独立的命令行工具。

### 捆绑式 Program 示例

```python
# mytool.py
from invoke import Program, Collection, task

@task
def build(c, clean=False):
    """构建项目"""
    if clean:
        c.run("rm -rf dist/")
    c.run("python -m build")

@task
def deploy(c, env="staging"):
    """部署到指定环境"""
    c.run(f"./deploy.sh {env}")

ns = Collection(build, deploy)

program = Program(
    name="mytool",
    namespace=ns,
    version="1.0.0",
    binary_names=["mytool", "mt"],
)

if __name__ == "__main__":
    program.run()
```

运行效果：

```bash
$ python mytool.py --list
Available tasks:

  build    构建项目
  deploy   部署到指定环境

$ python mytool.py build --clean
$ python mytool.py deploy --env=production
```

### Program 自定义要点

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `name` | 程序名称（用于 --help 输出） | `"invoke"` |
| `namespace` | 预设的任务集合（捆绑模式） | `None`（从文件发现） |
| `version` | 版本号 | 未设置时 `--version` 报错 |
| `binary_names` | 可执行文件名列表（影响 --help 显示） | `["invoke", "inv"]` |
| `config_class` | 自定义 Config 类 | `Config` |
| `executor_class` | 自定义 Executor 类 | `Executor`（也可通过配置指定） |
| `loader_class` | 自定义 Loader 类 | `FilesystemLoader` |

### 自定义核心参数

通过子类化 Program 并覆盖 `core_args()` 方法，可以添加全局命令行选项：

```python
from invoke import Program, Argument

class MyProgram(Program):
    def core_args(self):
        args = super().core_args()
        args.append(Argument(
            names=("verbose", "v"),
            kind=bool,
            default=False,
            help="启用详细输出",
        ))
        return args

# 访问自定义参数：在任务中通过 c.config.core.verbose 获取
@task
def build(c):
    if c.config.core.verbose:
        print("Building with verbose output...")
    c.run("python -m build", echo=c.config.core.verbose)
```

### 任务发现配置

FilesystemLoader 支持自定义任务文件名和搜索路径：

```python
program = Program(
    name="mytool",
    namespace=ns,
)
# 或通过配置：
# config = {"tasks": {"collection_name": "mytool_tasks", "search_root": "./scripts"}}
```

## 自定义 Executor

通过继承 Executor 并重写关键方法，可以改变任务执行行为：

```python
from invoke import Executor
import time
import logging

class TimingExecutor(Executor):
    """记录每个任务执行时间的 Executor。"""
    
    def execute(self, *tasks):
        self.timings = {}
        results = super().execute(*tasks)
        for task, elapsed in self.timings.items():
            print(f"[timing] {task.name}: {elapsed:.2f}s")
        return results
    
    def _execute(self, call):
        start = time.time()
        result = super()._execute(call)
        self.timings[call.task] = time.time() - start
        return result

# 使用方式
program = Program(executor_class=TimingExecutor, namespace=ns)
```

### Executor 可重写方法

| 方法 | 用途 | 重写场景 |
|------|------|----------|
| `normalize(tasks)` | 输入标准化 | 支持新的任务输入格式 |
| `expand_calls(calls)` | 展开 pre/post | 改变依赖解析逻辑 |
| `dedupe(calls)` | 去重 | 自定义去重策略 |
| `execute(*tasks)` | 执行入口 | 添加全局前后置逻辑、计时、日志 |
| `_execute(call)` | 单 Call 执行 | 单任务包装（重试、超时、日志） |
| `parameters_for_call(call)` | 参数解析 | 自定义参数注入 |

## 自定义 Runner

通过继承 Runner 或 Local，可以改变命令执行方式。最常见的场景是实现远程执行（如 Fabric 的 Remote runner）、Docker 执行或 Mock 执行。

```python
from invoke.runners import Runner, Result
from invoke.exceptions import CommandTimedOut

class DryRunRunner(Runner):
    """干跑模式：不真正执行命令，只记录并返回模拟结果。"""
    
    def _start(self, command, shell, env):
        # 不启动实际进程
        self._command = command
        print(f"[dry-run] Would run: {command}")
    
    def _read_proc_output(self, reader):
        return ""  # 无输出
    
    def _write_proc_stdin(self, data):
        pass  # 不写入
    
    def _close_proc_stdin(self):
        pass
    
    def _send_interrupt(self):
        pass
    
    def _wait(self):
        # 返回退出码 0
        self._returncode = 0
    
    def _returncode(self):
        return 0
    
    def _kill(self):
        pass
    
    def is_finished(self):
        return True
```

### Runner 抽象接口

自定义 Runner 必须实现以下方法：

| 方法 | 职责 |
|------|------|
| `_start(command, shell, env)` | 启动命令执行 |
| `_read_proc_output(reader)` | 读取进程输出（stdout/stderr） |
| `_write_proc_stdin(data)` | 向进程写入 stdin 数据 |
| `_close_proc_stdin()` | 关闭进程 stdin |
| `_send_interrupt()` | 发送中断信号（Ctrl+C） |
| `_wait()` | 等待进程结束，设置 `returncode` |
| `_kill(self)` | 强制终止进程（timeout 时调用） |
| `is_finished()` | 返回进程是否已结束（非阻塞查询） |

### 注册自定义 Runner

通过配置注册自定义 Runner，使其在 `c.run()` 中可用：

```python
# 全局配置
config = {
    "runners": {
        "local": DryRunRunner,  # 替换默认 local runner
    }
}

# 或通过 collection.configure()
ns = Collection(my_task)
ns.configure({"runners": {"local": DryRunRunner}})
```

Context.run() 通过 `config.runners[runner]` 查找 Runner 类，支持点分路径动态导入。

## MockContext 测试

Invoke 提供 `MockContext` 类，方便在测试中模拟命令执行而不真正运行外部命令。

```python
from invoke import MockContext, Result, task
import pytest

@task
def check_status(c):
    result = c.run("systemctl is-active nginx", hide=True)
    return result.ok

def test_check_status_running():
    c = MockContext(run={
        "systemctl is-active nginx": Result(
            stdout="active\n",
            exited=0,
            ok=True,
        )
    })
    assert check_status(c) is True

def test_check_status_stopped():
    c = MockContext(run={
        "systemctl is-active nginx": Result(
            stdout="inactive\n",
            exited=3,
            ok=False,
        )
    })
    assert check_status(c) is False
```

### MockContext 的 run 参数

`MockContext(run=...)` 接受多种格式来预设 `run()` 的返回值：

1. **单个 Result 对象**：每次调用都返回该 Result
2. **布尔值**：`True` 返回退出码 0 的 Result，`False` 返回退出码 1 的 Result
3. **可迭代对象**：按顺序依次返回每个值（配合 `repeat=False` 使用）
4. **字典形式**：键为命令字符串或编译后的正则表达式（`re.compile()`），值为上述任一类型，按命令匹配返回

```python
import re
from invoke import MockContext, Result

# 简单字典匹配（精确字符串）
c = MockContext(run={"ls": Result(stdout="file1\nfile2\n")})

# 正则表达式匹配（字典键为 re.compile 对象）
c = MockContext(run={
    re.compile(r"git log.*"): Result(stdout="abc1234 Fix bug\ndef5678 Add feature\n")
})

# 单个 Result：所有命令都返回同一结果
c = MockContext(run=Result(stdout="ok\n"))

# 布尔快捷方式：所有命令成功/失败
c = MockContext(run=True)
```

### Mock 配置

MockContext 的构造参数还支持 `config` 字典来模拟配置：

```python
c = MockContext(
    config={"run": {"echo": True, "warn": False}},
    run={"ls": Result(stdout="")}
)
assert c.config.run.echo is True
```

## 任务间调用

一个任务可以通过 `c.run("inv other-task")` 的方式调用另一个任务，但更优雅的方式是直接导入并调用任务函数：

```python
from invoke import task

@task
def clean(c):
    c.run("rm -rf dist/ build/")

@task
def build(c, clean_first=False):
    if clean_first:
        clean(c)  # 直接调用，传递 context
    c.run("python -m build")

@task
def package(c):
    clean(c)       # 复用 clean 任务
    build(c)       # 复用 build 任务
    c.run("twine upload dist/*")
```

**注意**：直接调用任务函数不会经过 Executor 的 pre/post 展开和 dedupe 逻辑。如果需要完整的执行链（包含依赖任务），应通过 pre/post 声明依赖，或者使用 `c.run("inv task-name")` 方式。

## 命名空间组织

大型项目应将任务分模块组织，使用 Collection 树结构：

```
tasks/
├── __init__.py       # 根命名空间
├── db.py             # 数据库任务
├── docker.py         # Docker 任务
└── deploy.py         # 部署任务
```

```python
# tasks/__init__.py
from invoke import Collection
from . import db, docker, deploy

ns = Collection()
ns.add_collection(db)       # 通过模块名 "db" 访问
ns.add_collection(docker, name="d")  # 自定义别名 "d"
ns.add_collection(deploy)
```

```python
# tasks/db.py
from invoke import task

@task
def migrate(c):
    c.run("alembic upgrade head")

@task
def seed(c):
    c.run("python seed.py")
```

命令行访问：

```bash
$ inv db.migrate
$ inv db.seed
$ inv d.build    # 通过别名访问
$ inv deploy.prod
```

### 子集合配置

每个子集合可以独立配置，配置只对该子集合中的任务生效：

```python
# tasks/docker.py
from invoke import Collection, task

@task
def build(c):
    c.run("docker build -t myapp .")

@task
def push(c):
    c.run("docker push myapp")

ns = Collection(build, push)
ns.configure({
    "run": {
        "echo": True,
        "pty": True,
    }
})
```

## 嵌入使用

除了 CLI 入口，Invoke 还可以作为库嵌入到 Python 应用中：

```python
from invoke import Config, Executor, Collection, task

@task
def greet(c, name="world"):
    print(f"Hello, {name}!")
    c.run("echo 'running in embedded mode'")

ns = Collection(greet)
config = Config(overrides={"run": {"echo": True}})
executor = Executor(collection=ns, config=config)

# 编程式执行任务
results = executor.execute(("greet", {"name": "Invoke"}))
```

### Program.run() 编程式调用

```python
from invoke import Program, Collection, task

@task
def hello(c):
    c.run("echo hello")

ns = Collection(hello)
program = Program(namespace=ns, exit=False)  # exit=False 不调用 sys.exit

# 模拟命令行调用
program.run("invoke hello")
```

`exit=False` 参数在测试和嵌入场景中非常重要，它阻止 Program 在执行完毕或出错时调用 `sys.exit()`。

## Tab 补全

Invoke 内置支持 bash/zsh/fish 的 tab 补全：

```bash
# bash
source <(inv --print-completion-script bash)

# zsh
source <(inv --print-completion-script zsh)

# fish
inv --print-completion-script fish | source
```

添加到 shell 配置文件（如 `~/.bashrc`）以持久化。补全功能支持：

- 任务名补全
- 任务参数补全（`--` 开头的 flag）
- 子命名空间任务补全

## 相关概念

- [Task 基础](02-task-basics.md)
- [Context 对象](03-context-object.md)
- [Collection 与命名空间](04-collection-namespace.md)
- [配置系统](05-configuration.md)
- [Runner 系统](06-runners.md)
- [CLI 与 Program 类](07-cli-program.md)
- [执行模型](08-execution-model.md)
- [PyInvoke 源码信源登记](../references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](../references/pyinvoke-source.md)；Program/Executor/Runner/MockContext 分别定义于 `invoke/program.py`、`invoke/executor.py`、`invoke/runners.py`、`invoke/context.py`。
