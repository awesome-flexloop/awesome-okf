---
type: Concept
title: StreamWatcher 自动响应
description: StreamWatcher、Responder 密码自动输入、FailingResponder 失败检测、自定义 watcher
tags: [pyinvoke, watcher, StreamWatcher, Responder, FailingResponder, sudo, auto-response, pattern-matching]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# StreamWatcher 自动响应

StreamWatcher（流监控器）是 Invoke 提供的输出监控与自动响应机制。它可以在子进程执行过程中实时扫描 stdout/stderr 输出，匹配特定模式（如密码提示、确认对话框），并自动向子进程 stdin 写入响应内容。这一机制使得 `c.sudo()` 的密码自动输入、交互式程序的自动应答等场景成为可能。

## 为什么需要 StreamWatcher

在自动化任务执行中，经常遇到需要交互的命令：

- `sudo` 要求输入密码
- `ssh` 首次连接要求确认主机密钥
- `apt-get install` 要求确认 `[Y/n]`
- 数据库客户端可能要求输入密码

如果没有自动应答机制，这些命令会阻塞等待用户输入，导致自动化脚本无法继续。StreamWatcher 正是解决这一问题的抽象机制。

## StreamWatcher 基类

`StreamWatcher` 是所有监控器的基类，它继承自 `threading.local`，使其实例可以安全地在多线程环境中使用（stdout 和 stderr 在不同线程中处理）。

### 核心 API

子类必须实现 `submit(stream)` 方法：

```python
class StreamWatcher(threading.local):
    def submit(self, stream):
        """
        处理流数据，可选返回响应字符串。
        
        :param stream: 该 IO 流自会话开始以来的全部内容（字符串）
        :returns: 可迭代的字符串（可为空），每个字符串写入子进程 stdin
        """
        raise NotImplementedError
```

**关键设计要点**：

1. **累积式扫描**：`submit()` 接收的是该流自开始以来的**全部**累积内容，而非增量数据。watcher 自身负责追踪已处理的位置（通过索引）。
2. **生成器模式**：`submit()` 可以返回一个可迭代对象（如生成器），yield 多个响应字符串。
3. **线程隔离**：继承 `threading.local` 确保每个 IO 线程中的 watcher 状态独立。stdout 线程和 stderr 线程各自拥有 watcher 的独立副本，避免竞态条件。
4. **状态追踪**：watcher 可以在实例中维护状态（如"是否已提交过响应"），实现复杂的应答逻辑。

### submit() 的调用时机

在 IO 线程中，每次从子进程读取到新数据并追加到缓冲区后，Runner 会调用 `respond(buffer_)` 方法：

```python
def respond(self, buffer_):
    stream = "".join(buffer_)
    for watcher in self.watchers:
        for response in watcher.submit(stream):
            self.write_proc_stdin(response)
```

这意味着每次 stdout 或 stderr 有新输出时，所有注册的 watcher 都会被调用，其返回的每个响应字符串都会被写入子进程 stdin。

## Responder：模式响应器

`Responder` 是 StreamWatcher 最常用的实现，它通过正则表达式匹配输出中的特定模式，并在匹配时返回预设的响应字符串。

### 构造与使用

```python
class Responder(StreamWatcher):
    def __init__(self, pattern, response):
        self.pattern = pattern      # 正则表达式模式（原始字符串）
        self.response = response    # 匹配时返回的响应字符串
        self.index = 0              # 已处理位置的索引
```

基本用法：

```python
from invoke import Responder, task

@task
def deploy(c):
    # 自动响应 sudo 密码提示
    sudo_responder = Responder(
        pattern=r"\[sudo\] password for .*:",
        response="mypassword\n"
    )
    c.run("sudo apt-get update", watchers=[sudo_responder])
```

### pattern_matches()：增量扫描机制

Responder 内部使用 `pattern_matches()` 方法实现增量扫描，避免对已处理内容重复匹配：

```python
def pattern_matches(self, stream, pattern, index_attr):
    index = getattr(self, index_attr)
    new = stream[index:]                    # 只扫描新增内容
    matches = re.findall(pattern, new, re.S)  # DOTALL 模式，跨行匹配
    if matches:
        setattr(self, index_attr, index + len(new))  # 更新索引
    return matches
```

**工作原理**：

1. 维护一个 `index` 属性，记录已处理到流的哪个位置
2. 每次 `submit()` 被调用时，只扫描 `stream[index:]` 的新增部分
3. 使用 `re.findall()` 查找所有匹配项
4. 如果找到匹配，将 index 推进到当前流末尾
5. `submit()` 方法对每个匹配项 yield 一次 response

这确保了每个匹配只触发一次响应，不会重复应答。

### 注意事项

- 响应字符串通常需要以换行符 `\n` 结尾，模拟用户按下 Enter
- pattern 使用原始字符串（`r"..."`）避免反斜杠转义问题
- `re.S`（DOTALL）标志使得 `.` 可以匹配换行符，支持跨行模式
- 如果输出中多次出现相同模式，每次出现都会触发一次响应

## FailingResponder：带失败检测的响应器

`FailingResponder` 扩展了 Responder，增加了**失败检测**能力。典型场景是 sudo 密码输入：如果密码正确，命令继续执行；如果密码错误，sudo 会再次提示或显示错误信息。FailingResponder 可以检测到这种失败并抛出异常。

### 构造参数

```python
class FailingResponder(Responder):
    def __init__(self, pattern, response, sentinel):
        super().__init__(pattern, response)
        self.sentinel = sentinel        # 失败模式（正则表达式）
        self.failure_index = 0          # 失败扫描的索引
        self.tried = False             # 是否已尝试过响应
```

### 工作流程

1. 初始行为与 Responder 相同：匹配 `pattern` 时返回 `response`
2. 一旦提交过响应（`tried = True`），开始扫描 `sentinel` 模式
3. 如果在提交响应后检测到 `sentinel` 匹配，抛出 `ResponseNotAccepted` 异常

这意味着：
- 第一次看到密码提示 → 自动输入密码
- 如果密码正确 → 不会出现 sentinel，继续正常执行
- 如果密码错误 → 会看到 "Sorry, try again" 之类的错误信息（sentinel），抛出异常

### c.sudo() 中的自动注入

`Context.sudo()` 方法内部自动创建并注入一个 FailingResponder：

```python
# c.sudo("apt-get update") 内部大致逻辑：
sudopass = self.config.sudo.password
prompt = self.config.sudo.prompt  # 默认 "[sudo] password: "
watcher = FailingResponder(
    pattern=re.escape(prompt),
    response=sudopass + "\n",
    sentinel="Sorry, try again.\r?\n",  # sudo 密码错误时的输出
)
self.run(command, watchers=[watcher], ...)
```

当 sudo 密码被拒绝时，会抛出 `AuthFailure` 异常（在 Runner 将 ResponseNotAccepted 包装为 Failure 后，由 sudo 逻辑进一步转换）。

## 自定义 Watcher

通过继承 StreamWatcher 可以实现复杂的自动应答逻辑。以下是一些常见场景的示例。

### 示例 1：是/否确认自动应答

```python
from invoke import task, Responder

@task
def install(c):
    # 自动回答所有 yes/no 确认为 yes
    confirm = Responder(
        pattern=r"Do you want to continue\? \[Y/n\]",
        response="y\n"
    )
    c.run("apt-get install -y nginx", watchers=[confirm])
```

### 示例 2：多模式应答器

一个 watcher 可以处理多种模式。以下是一个模拟简单 SSH 主机密钥确认 + 密码输入的示例：

```python
import re
from invoke import StreamWatcher, task

class SSHWatcher(StreamWatcher):
    def __init__(self, password):
        self.password = password
        self.host_key_index = 0
        self.password_index = 0
    
    def submit(self, stream):
        responses = []
        
        # 检测主机密钥确认提示
        host_key_prompt = r"Are you sure you want to continue connecting \(yes/no/\[fingerprint\]\)\?"
        new = stream[self.host_key_index:]
        if re.search(host_key_prompt, new):
            responses.append("yes\n")
            self.host_key_index += len(new)
        
        # 检测密码提示
        password_prompt = r"password:"
        new = stream[self.password_index:]
        if re.search(password_prompt, new):
            responses.append(self.password + "\n")
            self.password_index += len(new)
        
        return responses

@task
def ssh_copy(c):
    watcher = SSHWatcher(password="mysecret")
    c.run("ssh user@host 'echo connected'", watchers=[watcher], pty=True)
```

注意：SSH 交互通常需要 `pty=True` 才能正确工作，因为 SSH 在非 TTY 环境下可能不会发出密码提示。

### 示例 3：带状态的条件应答

```python
class ConditionalResponder(StreamWatcher):
    """根据输出来决定响应内容的 watcher。"""
    
    def __init__(self):
        self.index = 0
        self.attempts = 0
    
    def submit(self, stream):
        new = stream[self.index:]
        if "Enter choice:" in new:
            self.index += len(new)
            self.attempts += 1
            if self.attempts == 1:
                return ["1\n"]  # 第一次选 1
            else:
                return ["2\n"]  # 后续选 2
        return []
```

## Watcher 的执行上下文

### 线程模型

Watcher 在 IO 线程中执行，需要注意：

1. **每个流独立**：stdout 和 stderr 各自有独立的 watcher 副本（由于 threading.local）
2. **PTY 模式下无 stderr 线程**：`pty=True` 时 stderr 合并到 stdout，因此不会创建 stderr 线程，watcher 只会在 stdout 线程中运行
3. **阻塞 IO**：watcher 的 `submit()` 方法在 IO 线程中同步执行，不应执行耗时操作
4. **响应编码**：返回的响应字符串由 Runner 编码为字节后写入子进程 stdin

### 使用建议

1. **PTY 优先**：对于交互式程序（如 sudo、ssh），通常需要 `pty=True`，因为许多程序在非 TTY 环境下不会输出提示符或缓冲输出
2. **模式精确**：正则表达式应尽量精确匹配，避免误触发
3. **换行符**：响应字符串末尾加 `\n`，否则程序不会收到"回车"
4. **错误处理**：对于可能失败的应答，使用 FailingResponder 或自定义带失败检测的 watcher
5. **密码安全**：避免在代码中硬编码密码，应通过配置系统或环境变量传递

## 内置 Watcher 类一览

| 类 | 用途 | 关键参数 |
|----|------|----------|
| `StreamWatcher` | 基类，定义 submit 接口 | 无 |
| `Responder` | 简单模式匹配应答 | `pattern`（正则）、`response`（响应字符串） |
| `FailingResponder` | 带失败检测的应答 | `pattern`、`response`、`sentinel`（失败模式） |

这些类通过 `from invoke import Responder, FailingResponder, StreamWatcher` 导入。

## 相关概念

- [Runner 系统](/concepts/06-runners.md)
- [Context 对象](/concepts/03-context-object.md)
- [执行模型](/concepts/08-execution-model.md)
- [终端与 IO](/concepts/10-terminals-io.md)
- [PyInvoke 源码信源登记](/references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](/references/pyinvoke-source.md)；StreamWatcher/Responder/FailingResponder 定义于 `invoke/watchers.py`，Runner.respond() 方法定义于 `invoke/runners.py`。
