---
type: Example
title: 异步执行命令
description: 使用 asyncssh 异步执行远程命令、收集输出、交互式进程、错误处理
tags: [asyncssh, example, command, run, process]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 异步执行命令

## 基本命令执行

使用 `conn.run()` 执行命令并收集全部输出：

```python
import asyncio
import asyncssh

async def main():
    async with asyncssh.connect('localhost',
                                username='user',
                                password='secret',
                                known_hosts=None) as conn:
        result = await conn.run('uname -a')
        print(f'退出码: {result.returncode}')
        print(f'标准输出: {result.stdout}')
        print(f'标准错误: {result.stderr}')

asyncio.run(main())
```

## 检查退出码

设置 `check=True`，非零退出码抛出 `ProcessError`：

```python
async def main():
    async with asyncssh.connect('localhost', known_hosts=None) as conn:
        try:
            result = await conn.run('false', check=True)
        except asyncssh.ProcessError as e:
            print(f'命令失败: returncode={e.returncode}')
            print(f'stderr: {e.stderr}')
```

## 超时控制

```python
try:
    result = await conn.run('sleep 100', timeout=5)
except asyncssh.TimeoutError as e:
    print(f'超时! 已有输出: {e.stdout}')
```

## 发送输入数据

```python
result = await conn.run('cat', input='Hello from asyncssh!\n')
assert result.stdout == 'Hello from asyncssh!\n'
```

## 交互式进程

使用 `create_process()` 创建交互式进程：

```python
async def main():
    async with asyncssh.connect('localhost', known_hosts=None) as conn:
        async with conn.create_process(term_type='xterm',
                                       term_size=(80, 24)) as proc:
            proc.stdin.write('ls -la\n')
            await proc.stdin.drain()

            output = await proc.stdout.readline()
            print(output)

            proc.stdin.write('exit\n')
            await proc.stdin.drain()
```

### 逐行读取

```python
async with conn.create_process() as proc:
    proc.stdin.write('for i in 1 2 3; do echo "line $i"; done\n')
    proc.stdin.write_eof()

    async for line in proc.stdout:
        print(repr(line))
```

### readuntil 读取

```python
async with conn.create_process() as proc:
    proc.stdin.write('echo "START"; sleep 1; echo "END"\n')
    await proc.stdin.drain()

    data = await proc.stdout.readuntil('START')
    print('收到 START 标记')

    proc.stdin.write_eof()
```

## 多命令并行

单个连接上并行执行多个命令：

```python
async with asyncssh.connect('localhost', known_hosts=None) as conn:
    r1, r2, r3 = await asyncio.gather(
        conn.run('hostname'),
        conn.run('whoami'),
        conn.run('uptime')
    )
    print(r1.stdout.strip())
    print(r2.stdout.strip())
    print(r3.stdout.strip())
```

## Bytes 模式

设置 `encoding=None` 以字节模式处理数据：

```python
result = await conn.run('cat /etc/hostname', encoding=None)
assert isinstance(result.stdout, bytes)
print(result.stdout.decode().strip())
```

## 环境变量

```python
result = await conn.run('echo $MY_VAR',
                        env={'MY_VAR': 'hello'},
                        send_env=['LANG'])
```

## 完整示例

```python
import asyncio
import asyncssh
import sys

async def run_command(host, command):
    try:
        async with asyncssh.connect(
            host,
            username='user',
            client_keys=['~/.ssh/id_ed25519'],
            known_hosts='~/.ssh/known_hosts'
        ) as conn:
            result = await conn.run(command, check=True, timeout=30)
            return result.stdout, None
    except asyncssh.ProcessError as e:
        return e.stdout, e.stderr
    except asyncssh.TimeoutError:
        return None, f'{host}: 命令超时'
    except asyncssh.HostKeyNotVerifiable:
        return None, f'{host}: 主机密钥验证失败'
    except asyncssh.PermissionDenied:
        return None, f'{host}: 认证失败'
    except (OSError, asyncssh.ConnectionLost) as e:
        return None, f'{host}: 连接失败 - {e}'

async def main():
    hosts = sys.argv[1:]
    if not hosts:
        print('用法: python async-command.py host1 host2 ...')
        return

    tasks = [run_command(h, 'uname -r') for h in hosts]
    results = await asyncio.gather(*tasks)

    for host, (stdout, stderr) in zip(hosts, results):
        if stderr:
            print(f'[{host}] 错误: {stderr}')
        else:
            print(f'[{host}] {stdout.strip()}')

asyncio.run(main())
```

## 相关概念

- [流与进程](/concepts/04-streams-processes.md)
- [异步连接详解](/concepts/02-async-connection.md)
- [高级模式](/concepts/11-advanced-patterns.md)

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
