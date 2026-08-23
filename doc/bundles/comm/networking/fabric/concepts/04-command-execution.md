---
type: Concept
title: 命令执行
description: run/sudo/local/shell 方法详解、Result 对象、PTY、warn/hide/echo、环境变量与 inline_ssh_env
tags: [fabric, command, run, sudo, pty, result]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 命令执行

## 三个命令执行入口

Connection 提供三个命令执行方法，它们的底层路径不同：

| 方法 | 执行位置 | Runner | 自动连接 |
|------|---------|--------|---------|
| `run()` | 远程 SSH | `Remote`（exec_command） | ✅ @opens |
| `sudo()` | 远程 SSH（sudo 前缀） | `Remote`（exec_command） | ✅ @opens |
| `local()` | 本地系统 | invoke 的 Local runner | ❌ |
| `shell()` | 远程交互式 Shell | `RemoteShell`（invoke_shell） | ✅ @opens |

### run() — 远程命令

```python
result = c.run("uname -a")
```

`run()` 被 `@opens` 装饰器修饰，执行前自动调用 `open()` 确保 SSH 连接已建立。内部流程：

1. 调用 `_remote_runner()` 创建 `Remote(context=self, inline_env=self.inline_ssh_env)` 实例
2. 调用继承自 `invoke.Context` 的 `_run(runner, command, **kwargs)`
3. invoke 的 `_run()` 调用 `runner.run()`，后者执行模板方法循环：
   - `start()`：创建 SSH channel、可选分配 PTY、处理 env、发送命令
   - 主循环：`read_proc_stdout/stderr()` 读取输出
   - `returncode()`：获取退出状态
   - `generate_result()`：构造 Result 对象

### sudo() — 提权命令

```python
c.sudo("systemctl restart nginx")
```

`sudo()` 同样被 `@opens` 修饰，使用 Remote runner，但通过 invoke 的 sudo 机制在命令前加 `sudo -S -p <prompt>` 前缀，并通过 stdin 传递密码。

支持的 kwargs（来自 invoke）：

| 参数 | 说明 |
|------|------|
| `password` | sudo 密码（默认从配置/sudo 密码缓存获取） |
| `prompt` | sudo 密码提示字符串（默认 `[sudo] password: `） |
| `hide` | 隐藏输出 |
| `warn` | 失败时警告而非抛异常 |
| `pty` | 是否分配 PTY（sudo 默认 True） |

### local() — 本地命令

```python
c.local("ls -la")
```

`local()` 直接调用 `super().run()`（`invoke.Context.run()`），在本地子进程执行。不经过 SSH，不需要连接。

### shell() — 交互式 Shell

```python
result = c.shell()
```

使用 `RemoteShell` runner，调用 channel 的 `invoke_shell()` 而非 `exec_command()`。强制分配 PTY，行为类似直接运行 `ssh host`。

仅支持五个 kwargs：`encoding`、`env`、`in_stream`、`replace_env`、`watchers`。传入其他参数会抛出 `TypeError`。

## Result 对象

`run()` 和 `sudo()` 返回 `fabric.runners.Result`，它继承 `invoke.runners.Result` 并增加 `connection` 属性：

```python
result = c.run("hostname")
print(result.command)      # "hostname"
print(result.stdout)       # "web01\n"
print(result.stderr)       # ""
print(result.exited)       # 0
print(result.ok)           # True
print(result.failed)       # False
print(result.pty)          # False
print(result.connection)   # <Connection host='...'>
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `command` | str | 执行的命令 |
| `stdout` | str | 标准输出 |
| `stderr` | str | 标准错误 |
| `exited` | int | 退出码 |
| `ok` | bool | exited == 0 |
| `failed` | bool | exited != 0 |
| `pty` | bool | 是否使用了 PTY |
| `connection` | Connection | fabric 扩展：关联的 Connection |
| `encoding` | str | 输出编码 |
| `shell` | str | 使用的 shell |

## 常用选项

### warn — 失败不抛异常

默认情况下，命令退出码非零时抛出 `invoke.exceptions.UnexpectedExit`：

```python
c.run("false")
# UnexpectedExit: Command 'false' failed with exit code 1!
```

设置 `warn=True` 则返回 Result 对象而不抛异常：

```python
result = c.run("false", warn=True)
print(result.failed)  # True
```

也可通过配置设置默认值：

```python
config = Config(overrides={"run": {"warn": True}})
```

### hide — 隐藏输出

```python
c.run("ls", hide=True)       # 隐藏 stdout 和 stderr
c.run("ls", hide="stdout")   # 只隐藏 stdout
c.run("stderr", hide="stderr")
c.run("ls", hide="both")     # 同 True
```

即使隐藏了输出，Result 对象仍包含完整的 stdout/stderr。

### echo — 回显命令

```python
c.run("ls", echo=True)
# 输出: ls
# 文件列表...
```

在执行前将命令字符串打印到 stderr，类似 shell 的 `set -x`。

### pty — 伪终端

```python
c.run("top -bn1", pty=True)
```

分配 PTY 后：
- stdout 和 stderr 合并为一个流（stderr 始终为空）
- 某些程序（如 sudo、top、vim）需要 PTY 才能正常工作
- `sudo()` 默认使用 PTY

Remote runner 在 PTY 模式下：
1. 调用 `channel.get_pty(width=cols, height=rows)` 设置初始终端大小
2. 在主线程上注册 `SIGWINCH` 信号处理器（仅 Unix），终端大小变化时调用 `channel.resize_pty()`

### env — 环境变量

```python
c.run("echo $MY_VAR", env={"MY_VAR": "hello"})
```

环境变量的传递方式受 `inline_ssh_env` 控制。

### watchers — 输出监控

```python
from invoke import Responder

responder = Responder(
    pattern=r"Password:",
    response="mypassword\n",
)
c.run("sudo whoami", watchers=[responder], pty=True)
```

Watcher 在输出流中匹配模式并自动响应。详见 [pyinvoke Watcher](../../../../build/tooling/pyinvoke/index.md)。

### in_stream — 标准输入

```python
from io import StringIO

c.run("cat", in_stream=StringIO("hello\n"))
```

### replace_env — 替换环境

`Remote.run()` 默认设置 `replace_env=True`（与 invoke.Local 的默认值不同）。当 `replace_env=False` 时，env 字典中的变量合并到远程 shell 的已有环境中；为 `True` 时仅传递指定的变量。

## inline_ssh_env

### 两种模式

`inline_ssh_env` 控制环境变量如何传递到远程命令：

**True（默认，fabric 3.0+）**：在命令前拼接 export 前缀：

```python
c.run("mycommand", env={"FOO": "bar", "BAZ": "qux"})
# 实际发送: export BAZ=qux FOO=bar && mycommand
```

- 环境变量按键名排序后拼接
- 不执行 shell 转义（文档明确警告）
- 适用于大多数 sshd 的 `AcceptEnv` 受限场景

**False**：通过 SSH 协议的 `channel.update_environment(env)` 传递：

```python
c.run("mycommand", env={"FOO": "bar"}, inline_ssh_env=False)
# 调用 channel.update_environment({"FOO": "bar"})
# 然后执行 mycommand
```

- 要求 sshd 的 `AcceptEnv` 配置允许对应变量
- 更安全但经常不可用

### 设置方式

```python
# 构造函数参数
c = Connection("host", inline_ssh_env=True)

# 配置文件
config = Config(overrides={"inline_ssh_env": False})
```

> **安全警告**：inline 模式不做 shell 转义，不要将不可信值放入 env 字典。

## Remote Runner 架构

`Remote` 继承 `invoke.Runner`，实现以下模板方法：

| 方法 | 实现 |
|------|------|
| `start(command, shell, env, timeout)` | `context.create_session()` → `channel.get_pty()`（如需）→ 处理 env → `send_start_message(command)` |
| `send_start_message(command)` | `channel.exec_command(command)` |
| `read_proc_stdout(num_bytes)` | `channel.recv(num_bytes)` |
| `read_proc_stderr(num_bytes)` | `channel.recv_stderr(num_bytes)` |
| `_write_proc_stdin(data)` | `channel.sendall(data)` |
| `close_proc_stdin()` | `channel.shutdown_write()` |
| `process_is_finished` (property) | `channel.exit_status_ready()` |
| `returncode()` | `channel.recv_exit_status()` |
| `generate_result(**kwargs)` | 添加 connection 后构造 Result |
| `stop()` | 关闭 channel，恢复 SIGWINCH |
| `kill()` | 直接关闭 channel |
| `send_interrupt(interrupt)` | PTY 模式发送 `\x03`（ETX），否则抛出 KeyboardInterrupt |

### RemoteShell

`RemoteShell` 继承 `Remote`，仅覆盖 `send_start_message()`：

```python
def send_start_message(self, command):
    self.channel.invoke_shell()
```

用于 `shell()` 方法，不接受 command 参数。

## 命令执行配置默认值

通过 `run.*` 配置树设置默认值：

```yaml
run:
  warn: false
  hide: null
  echo: false
  pty: false
  encoding: utf-8
  replace_env: true
  in_stream: true
```

sudo 相关配置在 `sudo.*` 下：

```yaml
sudo:
  password: null
  prompt: "[sudo] password: "
  pty: true
```

## 相关概念

- [Connection 详解](02-connection.md)
- [配置体系](03-configuration.md)
- [多主机并行](05-group-parallel.md)
- [pyinvoke Runner](../../../../build/tooling/pyinvoke/index.md)
- [paramiko Channel](../../paramiko/concepts/04-channel.md)
