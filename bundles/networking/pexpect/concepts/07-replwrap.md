---
type: Concept
title: REPLWrapper REPL 交互封装
description: REPLWrapper 封装 Python/Bash/Zsh 等 REPL 交互、run_command、continuation prompt、工厂函数
tags: [pexpect, repl, replwrap, python, bash]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# REPLWrapper REPL 交互封装

## REPLWrapper 的定位

`REPLWrapper`（`pexpect/replwrap.py`）是对 Read-Eval-Print Loop（REPL）交互式 shell 的高层封装。它自动处理提示符同步、多行命令、续行提示等问题，让控制 Python/Bash/Zsh/数据库 CLI 等 REPL 程序变得简单。

REPLWrapper 不直接继承 spawn，而是**组合**一个 spawn 实例（或自己创建），通过提示符匹配来同步命令执行。

## 快速开始

### Python REPL

```python
from pexpect.replwrap import python

p = python()
output = p.run_command('1 + 1')
print(output)  # '2\r\n'

output = p.run_command('import os; os.getcwd()')
print(output)
```

### Bash

```python
from pexpect.replwrap import bash

b = bash()
print(b.run_command('ls -la'))
print(b.run_command('echo $HOME'))
```

### Zsh

```python
from pexpect.replwrap import zsh

z = zsh()
print(z.run_command('pwd'))
```

## 构造函数

```python
REPLWrapper(cmd_or_spawn, orig_prompt, prompt_change,
            new_prompt=PEXPECT_PROMPT,
            continuation_prompt=PEXPECT_CONTINUATION_PROMPT,
            extra_init_cmd=None)
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `cmd_or_spawn` | （必填） | 命令字符串（自动 spawn）或已存在的 spawn 实例 |
| `orig_prompt` | （必填） | 初始提示符的正则表达式 |
| `prompt_change` | （必填） | 修改提示符的命令；用 `{0}`/`{1}` 引用 new_prompt/continuation_prompt |
| `new_prompt` | `PEXPECT_PROMPT` | 新提示符字符串，默认为 `'[PEXPECT_PROMPT>'` |
| `continuation_prompt` | `PEXPECT_CONTINUATION_PROMPT` | 续行提示符，默认为 `'[PEXPECT_PROMPT+'` |
| `extra_init_cmd` | `None` | 初始化完成后执行的额外命令（如禁用分页器） |

### 常量

```python
PEXPECT_PROMPT = u'[PEXPECT_PROMPT>'
PEXPECT_CONTINUATION_PROMPT = u'[PEXPECT_PROMPT+'
```

这两个提示符被设计为不会在正常程序输出中出现。

### 自定义 REPL

```python
import pexpect
from pexpect.replwrap import REPLWrapper

child = pexpect.spawn('sqlite3 test.db', echo=False, encoding='utf-8')
repl = REPLWrapper(
    child,
    r'sqlite> ',                          # 原始提示符
    "PROMPT '{0}'\nPROMPT_CONTINUE '{1}'",  # 修改提示符命令
    extra_init_cmd='.mode list',          # 额外初始化
)

result = repl.run_command('SELECT * FROM users;')
print(result)
```

当 `prompt_change` 为 `None` 时，不修改提示符，直接使用 `orig_prompt`。

## run_command()

```python
run_command(command, timeout=-1, async_=False)
```

发送命令到 REPL，等待提示符返回，返回命令输出（不含提示符本身）。

```python
output = repl.run_command('print("hello")')
# output: 'hello\r\n'
```

### 多行命令

`run_command` 自动处理多行命令：按行分割，逐行发送，每行之间等待主提示符或续行提示符：

```python
code = """
for i in range(3):
    print(i)
""".strip()

output = repl.run_command(code)
print(output)
```

### 续行检测

如果命令发送后收到续行提示符（continuation prompt），说明命令不完整。REPLWrapper 会发送 SIGINT 中断并抛出 `ValueError`：

```python
try:
    repl.run_command('for i in range(3):')  # 不完整的 for 循环
except ValueError as e:
    print(e)  # "Continuation prompt found - input was incomplete"
```

### 超时

```python
# 等待最多 60 秒
output = repl.run_command('long_running_function()', timeout=60)

# 无限等待
output = repl.run_command('blocking_call()', timeout=None)
```

### 异步支持

```python
import asyncio

async def main():
    output = await repl.run_command('1+1', async_=True)
    print(output)

asyncio.run(main())
```

## 工厂函数

### python()

```python
python(command=sys.executable)
```

启动 Python shell 并返回 REPLWrapper：

```python
from pexpect.replwrap import python

p = python()
p.run_command('x = 42')
p.run_command('x * 2')  # '84\r\n'
```

内部执行的提示符修改命令为：

```python
"import sys; sys.ps1={new_prompt!r}; sys.ps2={continuation_prompt!r}"
```

### bash()

```python
bash(command="bash")
```

启动 bash shell（使用自定义 bashrc 禁用颜色和干扰输出）：

```python
from pexpect.replwrap import bash

b = bash()
b.run_command('cd /tmp')
b.run_command('pwd')  # '/tmp\r\n'
```

bash 工厂函数：
- 使用 `--rcfile` 指定 pexpect 自带的 `bashrc.sh`
- 设置 `PS1`/`PS2` 为不可见标记字符（`\[\]`）包裹的 PEXPECT_PROMPT，避免 `env` 等命令将提示符误识别为输出
- 执行 `export PAGER=cat` 禁用分页器
- 传入 `NO_COLOR=1` 环境变量

### zsh()

```python
zsh(command="zsh", args=("--no-rcs", "-V", "+Z"))
```

启动 zsh shell，默认使用 `--no-rcs`（不读取配置文件）、`-V`（详细模式）、`+Z`（禁用 zsh 特有功能以模拟 POSIX 模式）。

## 内部机制

### 初始化流程

1. 如果 `cmd_or_spawn` 是字符串，创建 `pexpect.spawn(cmd, echo=False, encoding='utf-8', env={'NO_COLOR': '1'})`
2. 如果 spawn 实例的 echo 为 True，调用 `setecho(False)` 和 `waitnoecho()` 禁用回显
3. 如果 `prompt_change` 非 None，先 expect `orig_prompt`，发送 `prompt_change` 格式化后的命令
4. 设置 `self.prompt = new_prompt`
5. 调用 `_expect_prompt()` 等待新提示符出现
6. 如果 `extra_init_cmd` 非 None，执行 `run_command(extra_init_cmd)`

### _expect_prompt()

```python
_expect_prompt(timeout=-1, async_=False)
```

内部使用 `expect_exact`（纯字符串匹配，非正则）匹配 `[self.prompt, self.continuation_prompt]`，返回 0（主提示符）或 1（续行提示符）。

### set_prompt()

```python
set_prompt(orig_prompt, prompt_change)
```

先等待原始提示符，再发送修改提示符的命令。可在运行时手动调用以更换提示符。

## 典型应用场景

### 数据库交互

```python
from pexpect.replwrap import REPLWrapper
import pexpect

child = pexpect.spawn('psql -U postgres', echo=False, encoding='utf-8')
repl = REPLWrapper(child, r'=# ', "\\set PROMPT1 '{0}'\n\\set PROMPT2 '{1}'")
print(repl.run_command('SELECT version();'))
```

### SSH 远程 REPL

结合 pxssh 使用：

```python
from pexpect import pxssh
from pexpect.replwrap import REPLWrapper

s = pxssh.pxssh(encoding='utf-8')
s.login('host', 'user', 'password')
s.sendline('python3')
s.expect('>>> ')

repl = REPLWrapper(s, '>>> ', 'import sys; sys.ps1="{0}"; sys.ps2="{1}"')
print(repl.run_command('import platform; platform.node()'))
s.logout()
```

### 命令执行器

```python
from pexpect.replwrap import bash

shell = bash()
commands = ['uname -a', 'df -h', 'free -m', 'uptime']
for cmd in commands:
    print(f'$ {cmd}')
    print(shell.run_command(cmd))
```

## 相关概念

- [spawn 类详解](/concepts/02-spawn-class.md)
- [expect 模式匹配](/concepts/03-expect-patterns.md)
- [pxssh SSH 自动化](/concepts/05-pxssh.md)
- [REPL 交互控制示例](/examples/repl-control.md)
- [高级模式](/concepts/08-advanced-patterns.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](/references/pexpect-source.md)。
