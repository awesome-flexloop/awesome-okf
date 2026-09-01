---
type: Concept
title: 高级模式
description: FSM 有限状态机、run() 函数、超时处理、非阻塞读取、异步 expect、调试技巧、异常处理最佳实践
tags: [pexpect, advanced, fsm, run, async, debugging]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# 高级模式

## run() 函数

`run()` 是一个高层便捷函数，适合不需要复杂交互的场景。它内部创建 `spawn` 实例，执行命令并返回输出。

### 签名

```python
run(command, timeout=30, withexitstatus=False, events=None,
    extra_args=None, logfile=None, cwd=None, env=None, **kwargs)
```

### 基本用法

```python
import pexpect

output = pexpect.run('ls -la')
print(output.decode())

# 带退出状态
output, exitstatus = pexpect.run('ls -la', withexitstatus=True)
print(f'Exit: {exitstatus}')
```

### events——模式-响应对

`events` 参数允许在命令输出中匹配模式并自动发送响应，类似精简版的 expect/send 循环：

```python
# 自动响应密码提示
output = pexpect.run(
    'scp file.txt user@host:/tmp/',
    events={'(?i)password:': 'mypassword\n'},
    withexitstatus=True
)
```

events 支持字典或元组列表：

```python
# 字典形式（顺序不保证）
events={'pattern1': 'response1', 'pattern2': 'response2'}

# 元组列表（顺序保持，推荐用于需要优先级的场景）
events=[
    ('(?i)password:', 'mypassword\n'),
    ('(?i)continue connecting', 'yes\n'),
]
```

### 回调函数

events 的值可以是回调函数，接收 `locals()` 字典作为参数（包含 child、event_count、extra_args 等），返回 True 终止执行，返回字符串则发送给子进程：

```python
def print_ticks(d):
    print(f"Tick #{d['event_count']}")

pexpect.run(
    'long_running_command',
    events={pexpect.TIMEOUT: print_ticks},
    timeout=5
)
```

### 超时行为

- `timeout=30`（默认）：30 秒无匹配则中断
- `timeout=-1`：无超时（无限等待 EOF）
- events 中可包含 `pexpect.TIMEOUT` 作为周期性触发的模式

### run() vs spawn

| 特性 | run() | spawn |
|------|-------|-------|
| 复杂度 | 低（一次性执行） | 高（持续交互） |
| 交互能力 | 仅 events 自动响应 | 完整 expect/send |
| 返回值 | 输出字符串或 (输出, 退出码) | spawn 对象 |
| 适合 | 简单命令+密码 | 多步交互、REPL |
| 上下文管理 | 不支持 | 支持 with 语句 |

## FSM 有限状态机

`pexpect.FSM` 模块提供了一个通用有限状态机实现，可用于解析协议输出或构建复杂的交互状态机。

### 基本概念

FSM 维护三张转换表：

1. **state_transitions**：`(input_symbol, current_state) → (action, next_state)`（精确匹配）
2. **state_transitions_any**：`(current_state) → (action, next_state)`（任意输入符号）
3. **default_transition**：兜底转换（catch-all）

查找顺序：精确匹配 → 任意匹配 → 默认 → 抛出 ExceptionFSM。

### 示例：RPN 计算器

```python
from pexpect.FSM import FSM
import string

def begin_build_number(fsm):
    fsm.memory.append(fsm.input_symbol)

def build_number(fsm):
    s = fsm.memory.pop()
    fsm.memory.append(s + fsm.input_symbol)

def end_build_number(fsm):
    fsm.memory.append(int(fsm.memory.pop()))

def do_operator(fsm):
    ar = fsm.memory.pop()
    al = fsm.memory.pop()
    op = fsm.input_symbol
    fsm.memory.append({'+': al+ar, '-': al-ar,
                       '*': al*ar, '/': al/ar}[op])

def do_equal(fsm):
    print(fsm.memory.pop())

f = FSM('INIT', [])  # 初始状态 INIT，memory 为空列表（用作栈）
f.set_default_transition(None, 'INIT')
f.add_transition('=', 'INIT', do_equal, 'INIT')
f.add_transition_list(string.digits, 'INIT', begin_build_number, 'BUILDING_NUMBER')
f.add_transition_list(string.digits, 'BUILDING_NUMBER', build_number, 'BUILDING_NUMBER')
f.add_transition_list(string.whitespace, 'BUILDING_NUMBER', end_build_number, 'INIT')
f.add_transition_list('+-*/', 'INIT', do_operator, 'INIT')

f.process_list('167 3 2 2 * * * 1 - =')
# 输出: 2003
```

### FSM API

| 方法 | 说明 |
|------|------|
| `FSM(initial_state, memory=None)` | 构造 FSM，memory 为任意对象（解析时通常用 list 作栈） |
| `reset()` | 重置到 initial_state |
| `add_transition(symbol, state, action, next_state)` | 添加精确转换 |
| `add_transition_list(symbols, state, action, next_state)` | 为多个符号添加相同转换 |
| `add_transition_any(state, action, next_state)` | 添加任意符号转换 |
| `set_default_transition(action, next_state)` | 设置兜底转换 |
| `process(symbol)` | 处理一个输入符号，可能改变状态和调用 action |
| `process_list(symbols)` | 批量处理符号序列 |

action 函数接收 FSM 实例，可访问 `input_symbol`、`current_state`、`memory` 等属性。

## 超时处理

### 超时层级

```python
# 1. 构造时设置默认超时
child = pexpect.spawn('command', timeout=60)

# 2. 全局修改
child.timeout = 30

# 3. 单次 expect 覆盖
child.expect('pattern', timeout=10)

# 4. 无限等待
child.expect('pattern', timeout=None)
```

### 优雅处理超时

```python
import pexpect

child = pexpect.spawn('ssh user@host', encoding='utf-8')

i = child.expect([
    r'[$#] ',          # 0: 提示符
    pexpect.TIMEOUT,   # 1: 超时
    pexpect.EOF,       # 2: 连接断开
], timeout=30)

if i == 0:
    print("Logged in")
elif i == 1:
    print("Timeout - output so far:", child.before)
    child.close()
elif i == 2:
    print("Connection closed")
```

### read_nonblocking 超时语义

`read_nonblocking(size=1, timeout=-1)` 的 timeout 语义：

- `-1`：使用 `self.timeout`
- `None`：无限等待
- `0`：轮询，无数据立即抛 TIMEOUT
- 正数：等待最多 N 秒读取**至少一个字符**（不保证读满 size 个）

## 非阻塞读取

### read_nonblocking

```python
try:
    data = child.read_nonblocking(size=1024, timeout=5)
    print(data)
except pexpect.TIMEOUT:
    print("No data available within 5 seconds")
except pexpect.EOF:
    print("Child exited")
```

### 结合 select 自定义轮询

```python
import select

while True:
    r, _, _ = select.select([child.child_fd], [], [], 1.0)
    if child.child_fd in r:
        try:
            data = child.read_nonblocking(size=4096, timeout=0)
            print(data, end='')
        except pexpect.EOF:
            break
    # 可在此执行其他任务
```

### use_poll 选项

当文件描述符数量可能超过 1024（`select.select()` 的限制）时，启用 `use_poll=True` 使用 `select.poll()`：

```python
child = pexpect.spawn('command', use_poll=True)
```

## 异步 expect

pexpect 支持 asyncio 协程模式：

```python
import asyncio
import pexpect

async def remote_command():
    child = pexpect.spawn('ssh user@host', encoding='utf-8')
    await child.expect('password:', async_=True)
    child.sendline('mypassword')
    await child.expect(r'[$#] ', async_=True)
    child.sendline('uptime')
    await child.expect(r'[$#] ', async_=True)
    result = child.before
    child.close()
    return result

output = asyncio.run(remote_command())
print(output)
```

`expect_list` 和 `expect_exact` 同样支持 `async_=True`。

## 调试技巧

### 1. 开启全量日志

```python
import sys
child = pexpect.spawn('command', encoding='utf-8', logfile=sys.stdout)
```

### 2. 检查对象状态

`spawn.__str__()` 输出详细的调试状态：

```python
child = pexpect.spawn('ssh user@host')
child.expect('password:')
print(child)
# 输出包括: command, args, buffer, before, after, match, match_index,
# exitstatus, pid, child_fd, closed, timeout, delimiter, maxread, 等
```

### 3. 查看异常栈

`ExceptionPexpect.get_trace()` 返回排除 pexpect 内部帧的调用栈：

```python
try:
    child.expect('pattern')
except pexpect.ExceptionPexpect as e:
    print(e.get_trace())
```

### 4. 分别记录读写

```python
child.logfile_read = sys.stdout     # 只看子进程输出
child.logfile_send = open('sent.log', 'w')  # 记录发送内容（含密码！）
```

### 5. 增大 searchwindowsize 排查匹配问题

```python
child.expect('pattern', searchwindowsize=None)  # 搜索全缓冲区
```

## 异常处理最佳实践

### 完整的异常处理模板

```python
import pexpect
import sys

def ssh_execute(host, user, password, command):
    try:
        child = pexpect.spawn(f'ssh {user}@{host}', encoding='utf-8',
                              timeout=30)
        i = child.expect([
            r'(?i)password:',
            r'(?i)are you sure you want to continue connecting',
            r'[$#] ',
            pexpect.EOF,
            pexpect.TIMEOUT,
        ])

        if i == 0:
            child.sendline(password)
            child.expect(r'[$#] ')
        elif i == 1:
            child.sendline('yes')
            child.expect(r'(?i)password:')
            child.sendline(password)
            child.expect(r'[$#] ')
        elif i == 2:
            pass  # 密钥认证，直接到提示符
        elif i == 3:
            raise RuntimeError(f'Connection closed: {child.before}')
        elif i == 4:
            raise TimeoutError(f'Login timed out: {child.before}')

        child.sendline(command)
        child.expect(r'[$#] ')
        output = child.before
        child.sendline('exit')
        child.close()
        return output

    except pexpect.EOF:
        raise RuntimeError(f'Unexpected EOF. Output: {child.before}')
    except pexpect.TIMEOUT:
        raise TimeoutError(f'Command timed out. Output: {child.before}')
    except pexpect.ExceptionPxssh as e:
        raise RuntimeError(f'SSH error: {e}')
```

## 相关概念

- [run() 函数](#run-函数)
- [FSM 有限状态机](#fsm-有限状态机)
- [spawn 类详解](02-spawn-class.md)
- [expect 模式匹配](03-expect-patterns.md)
- [pxssh SSH 自动化](05-pxssh.md)
- [REPLWrapper](07-replwrap.md)
- [pexpect 源码信源登记](../references/pexpect-source.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](../references/pexpect-source.md)。
