---
type: Concept
title: Context 对象
description: Context（上下文对象）：c.run()、c.sudo()、c.cd()、c.prefix() 方法与配置访问
tags: [pyinvoke, context, c.run, c.sudo, c.cd, c.prefix, MockContext]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# Context 对象

**Context**（上下文对象）是 Invoke 任务执行时传递状态和配置的核心对象。每个任务函数的第一个参数必须是 Context 实例（约定命名为 `c`），它提供了执行 shell 命令、管理工作目录、维护命令前缀、访问配置等核心能力。

## 为什么需要 Context

Context 解决了以下问题：

1. **状态共享**：在任务间共享 CLI 解析结果、配置值、运行时状态
2. **命令封装**：提供 `run()`/`sudo()` 等方法，自动考虑配置选项（如 echo、warn 等）
3. **目录/前缀管理**：通过 `cd()` 和 `prefix()` 上下文管理器维护 shell 状态
4. **配置代理**：Context 作为 `c.config` 的代理，可以直接用 `c.KEY` 访问配置

## c.run() —— 执行 Shell 命令

`c.run(command, **kwargs)` 是最常用的方法，用于在本地子进程中执行 shell 命令。

### 基本用法

```python
from invoke import task

@task
def build(c):
    c.run("mkdir -p dist")
    c.run("echo 'Building project...'")
    result = c.run("ls -la dist")
```

### 常用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `command` | `str` | 必填 | 要执行的 shell 命令字符串 |
| `echo` | `bool` | `False` | 执行前是否先打印命令字符串到 stdout |
| `warn` | `bool` | `False` | 命令非零退出时是否仅警告继续（而非抛出 `UnexpectedExit` 异常） |
| `hide` | `bool/str` | `None` | 隐藏输出：`True`/`'both'` 隐藏 stdout+stderr，`'out'`/`'stdout'` 只隐藏 stdout，`'err'`/`'stderr'` 只隐藏 stderr |
| `pty` | `bool` | `False` | 是否使用伪终端（pty）执行命令（某些程序在 pty 下行为不同） |
| `env` | `dict` | `{}` | 更新子进程的环境变量（合并到当前环境） |
| `replace_env` | `bool` | `False` | 为 `True` 时用 `env` 完全替换而非更新当前环境 |
| `shell` | `str` | `/bin/bash`（Unix）/`cmd.exe`（Windows） | 指定使用的 shell 程序 |
| `encoding` | `str` | 自动检测 | 覆盖 stdout/stderr 的编码 |
| `timeout` | `float` | `None` | 超时秒数，超时后中断进程并抛出 `CommandTimedOut` |
| `dry` | `bool` | `False` | 试运行模式，不实际执行命令 |
| `asynchronous` | `bool` | `False` | 异步执行，返回 `Promise` 对象而非 `Result` |
| `disown` | `bool` | `False` | 完全分离子进程，使其在 Python 退出后继续运行 |
| `watchers` | `list` | `[]` | `StreamWatcher` 实例列表，用于模式匹配和自动应答 |
| `in_stream` | file-like | `sys.stdin` | 子进程 stdin 的来源 |
| `out_stream` | file-like | `sys.stdout` | 子进程 stdout 的目标 |
| `err_stream` | file-like | `sys.stderr` | 子进程 stderr 的目标 |
| `echo_stdin` | `bool` | 自动判断 | 是否将输入回显到终端 |
| `fallback` | `bool` | `True` | pty 不可用时是否自动回退到非 pty 模式 |

### echo —— 打印正在执行的命令

```python
@task
def build(c):
    c.run("echo building...", echo=True)
```

输出时会先以粗体打印命令本身，再打印命令输出。

### warn —— 容忍命令失败

默认情况下，命令返回非零退出码会抛出 `UnexpectedExit` 异常。设置 `warn=True` 可以仅打印警告而不中断执行：

```python
@task
def clean(c):
    # 如果 dist 目录不存在，rm 会失败，但我们不想因此中断
    c.run("rm -rf dist", warn=True)
```

### hide —— 隐藏命令输出

```python
@task
def check(c):
    # 隐藏输出，只通过 Result 对象获取结果
    result = c.run("git status --porcelain", hide=True)
    if result.stdout:
        print("存在未提交的更改")
    else:
        print("工作区干净")
```

### env —— 设置环境变量

```python
@task
def serve(c):
    c.run("python app.py", env={"FLASK_ENV": "development", "PORT": "5000"})
```

### pty —— 使用伪终端

某些程序（如需要交互输入的程序、彩色输出的程序）在 pty 下行为不同：

```python
@task
def interactive(c):
    c.run("vim", pty=True)  # 需要 pty 才能正常工作
```

注意：`pty=True` 时 stdout 和 stderr 会合并为一个流，无法区分。

### Result 返回值

`c.run()` 返回一个 `Result` 对象，包含以下属性：

- `result.stdout`：标准输出字符串
- `result.stderr`：标准错误字符串（pty=True 时为空）
- `result.exited`：退出码（整数）
- `result.ok`：布尔值，退出码为 0 时为 `True`
- `result.failed`：布尔值，退出码非 0 时为 `True`
- `result.command`：执行的命令字符串
- `result.return_code`：同 `exited`

```python
@task
def version(c):
    result = c.run("python --version", hide=True)
    print(f"Python 版本: {result.stdout.strip()}")
    print(f"退出码: {result.exited}")
```

## c.sudo() —— 以特权执行命令

`c.sudo(command, **kwargs)` 与 `c.run()` 类似，但通过 `sudo` 执行命令，并自动处理密码提示应答。

```python
@task
def install(c):
    c.sudo("apt-get update")
    c.sudo("apt-get install -y nginx")
```

### sudo 特有参数

| 参数 | 说明 |
|------|------|
| `password` | sudo 密码（运行时覆盖配置中的 `sudo.password`） |
| `user` | 以指定用户身份执行（默认 root），对应 `sudo -u user` |

### sudo 自动应答机制

`c.sudo()` 内部会自动添加一个 `FailingResponder` 监控器：

1. 搜索 sudo 密码提示（默认匹配 `[sudo] password:` 样式的提示符）
2. 自动输入配置中设定的密码（`sudo.password` 配置项）
3. 如果密码错误导致认证失败，自动抛出 `AuthFailure` 异常

如果想手动输入密码，直接使用 `c.run("sudo command")` 即可。

### 指定用户执行

```python
@task
def setup(c):
    c.sudo("mkdir -p /opt/myapp", user="www-data")
    c.sudo("chown www-data:www-data /opt/myapp", user="root")
```

sudo 命令构造：使用 `-S`（从 stdin 读密码）、`-p <prompt>`（自定义提示符）、`-u <user>`（指定用户）、`-H`（设置 HOME 环境变量）等标志。

## c.cd() —— 切换工作目录（上下文管理器）

`c.cd(path)` 是一个上下文管理器（context manager），在 `with` 块内的所有 `run`/`sudo` 调用都会自动添加 `cd <path> &&` 前缀。

### 为什么需要 c.cd()

直接 `c.run("cd /some/path")` 是无效的，因为每次 `c.run()` 都在独立的子进程中执行，`cd` 不会影响后续命令。`c.cd()` 通过命令前缀机制维护目录状态。

```python
# ❌ 错误做法：不会生效
@task
def wrong(c):
    c.run("cd /var/www")
    c.run("ls")  # 仍然在原目录，不会列出 /var/www

# ✅ 正确做法：使用 c.cd()
@task
def right(c):
    with c.cd("/var/www"):
        c.run("ls")  # 实际执行: cd /var/www && ls
```

### 嵌套使用

`c.cd()` 支持嵌套：

```python
@task
def nested(c):
    with c.cd("/var/www"):
        c.run("ls")  # cd /var/www && ls
        with c.cd("website1"):
            c.run("ls")  # cd /var/www/website1 && ls
        c.run("pwd")  # 回到 /var/www
```

相对路径和绝对路径都支持，路径中的空格会自动转义。`c.cd()` 也支持 `Path` 对象（任何定义了 `__str__` 的对象）。

### c.cwd 属性

`c.cwd` 属性返回当前工作目录（考虑所有 `c.cd()` 嵌套后的实际目录）：

```python
@task
def whereami(c):
    print(f"当前目录: {c.cwd}")  # 空字符串或当前目录
    with c.cd("/tmp"):
        print(f"当前目录: {c.cwd}")  # "/tmp"
```

## c.prefix() —— 命令前缀（上下文管理器）

`c.prefix(command)` 也是上下文管理器，在 `with` 块内的所有 `run`/`sudo` 调用前都会添加指定命令加 `&&`。

典型用途是激活虚拟环境、设置环境变量等需要改变 shell 状态的操作：

```python
@task
def migrate(c):
    with c.prefix("workon myvenv"):
        c.run("./manage.py migrate")
        c.run("./manage.py loaddata fixtures.json")
```

实际执行的命令：

```bash
workon myvenv && ./manage.py migrate
workon myvenv && ./manage.py loaddata fixtures.json
```

### 与 c.cd() 组合使用

`c.cd()` 和 `c.prefix()` 可以嵌套组合，顺序会正确保留：

```python
@task
def deploy(c):
    with c.cd("/opt/myapp"):
        with c.prefix("source venv/bin/activate"):
            c.run("pip install -r requirements.txt")
            c.run("gunicorn app:app")
```

实际执行：

```bash
cd /opt/myapp && source venv/bin/activate && pip install -r requirements.txt
cd /opt/myapp && source venv/bin/activate && gunicorn app:app
```

### 嵌套 prefix

多个 `c.prefix()` 也可以嵌套：

```python
@task
def test(c):
    with c.prefix("export FLASK_ENV=testing"):
        with c.prefix("source .env"):
            c.run("pytest")
```

实际执行：`export FLASK_ENV=testing && source .env && pytest`

## c.config —— 配置访问

`c.config` 是 `Config` 对象，存储所有层级合并后的配置值。Context 本身代理了 `c.config`，因此可以通过两种方式访问配置：

```python
@task
def show_config(c):
    # 方式 1：通过 c.config 访问
    print(c.config.run.echo)
    print(c.config["run"]["echo"])
    
    # 方式 2：直接通过 c 访问（代理）
    print(c.run.echo)
    print(c["run"]["echo"])
```

支持字典风格（`c['key']`）和属性风格（`c.key`）两种访问方式。

配置来自多个层级的合并：系统级→用户级→项目级（invoke.yaml/json/py）→环境变量→CLI 参数。

## MockContext —— 测试用模拟上下文

`MockContext` 是 `Context` 的子类，用于单元测试中。它允许预设 `run()`/`sudo()` 的返回值，而不实际执行命令。

```python
from invoke import task
from invoke.context import MockContext
from invoke.runners import Result

@task
def build(c):
    c.run("mkdir -p dist")
    result = c.run("echo done")
    return result.stdout

# 测试
def test_build():
    mc = MockContext(run={
        "mkdir -p dist": Result(""),
        "echo done": Result("done\n"),
    })
    result = build(mc)
    assert result == "done\n"
    # 验证 c.run 确实被调用了
    assert mc.run.call_count == 2
```

### MockContext 构造参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `config` | `Config` | 配置对象，与普通 Context 相同 |
| `run` | `Result/bool/str/dict/iterable` | 预设 `run()` 调用的返回值 |
| `sudo` | 同上 | 预设 `sudo()` 调用的返回值 |
| `repeat` | `bool` | 是否循环重复结果（默认 `True`），`False` 时结果用完后抛出 `NotImplementedError` |

`run` 参数支持多种形式：

- **单个 Result**：每次调用都返回该 Result
- **布尔值**：`True` 返回退出码 0 的 Result，`False` 返回退出码 1 的 Result
- **字符串**：返回 stdout 为该字符串的 Result
- **字典**：键为命令字符串或正则表达式，值为上述任一类型，按命令匹配返回
- **可迭代对象**：按顺序依次返回每个值

```python
# 布尔值快捷方式
mc = MockContext(run=True)  # 所有命令都成功
mc.run("anything")  # 返回 exited=0 的 Result

# 按顺序返回
mc = MockContext(run=[Result("first"), Result("second")], repeat=False)
mc.run("cmd1")  # Result("first")
mc.run("cmd2")  # Result("second")
mc.run("cmd3")  # 抛出 NotImplementedError

# 正则匹配
import re
mc = MockContext(run={re.compile(r"git .*"): Result("on branch main")})
mc.run("git status")  # 匹配成功
```

### set_result_for 方法

`mc.set_result_for(method_name, command, result)` 可以在 MockContext 创建后动态添加预设结果：

```python
mc = MockContext()
mc.set_result_for("run", "mycommand", Result("mystdout"))
assert mc.run("mycommand").stdout == "mystdout"
```

## 模块级便捷函数

除了 Context 方法外，`invoke` 包还提供了两个模块级便捷函数，用于不需要自定义 Context 的简单场景：

- `invoke.run(command, **kwargs)`：创建匿名 Context 并调用其 `run()` 方法
- `invoke.sudo(command, **kwargs)`：创建匿名 Context 并调用其 `sudo()` 方法

```python
from invoke import run

# 简单的一次性命令执行
result = run("echo hello", hide=True)
print(result.stdout)
```

## 相关概念

- [Task 基础](/concepts/02-task-basics.md)
- [Collection 与命名空间](/concepts/04-collection-namespace.md)
- [5分钟快速上手](/concepts/01-getting-started.md)
- [PyInvoke 简介](/concepts/00-introduction.md)
- [PyInvoke 源码信源登记](/references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](/references/pyinvoke-source.md)；Context 类定义于 `invoke/context.py`，Runner 类定义于 `invoke/runners.py`。
