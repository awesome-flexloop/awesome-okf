---
type: Example
title: 多主机并行连接
description: 使用 asyncio.gather 同时连接多台主机执行命令、信号量限流、异常收集
tags: [asyncssh, example, parallel, asyncio, gather]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 多主机并行连接

## 基本并行

使用 `asyncio.gather()` 同时连接多台主机：

```python
import asyncio
import asyncssh

async def run_on_host(host, command, **kwargs):
    async with asyncssh.connect(host, **kwargs) as conn:
        result = await conn.run(command)
        return host, result.returncode, result.stdout, result.stderr

async def main():
    hosts = ['web1.example.com', 'web2.example.com', 'db1.example.com']

    tasks = [
        run_on_host(h, 'uname -r', username='admin',
                    client_keys=['~/.ssh/id_ed25519'])
        for h in hosts
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for host, result in zip(hosts, results):
        if isinstance(result, Exception):
            print(f'[{host}] 错误: {result}')
        else:
            hostname, rc, stdout, stderr = result
            print(f'[{hostname}] (exit {rc}) {stdout.strip()}')

asyncio.run(main())
```

## 信号量限流

连接大量主机时，使用 `asyncio.Semaphore` 限制并发数：

```python
import asyncio
import asyncssh

MAX_CONCURRENT = 10

async def run_command(sem, host, command):
    async with sem:
        try:
            async with asyncssh.connect(host, known_hosts=None) as conn:
                result = await conn.run(command, check=True)
                return host, result.stdout.strip(), None
        except Exception as e:
            return host, None, str(e)

async def main():
    hosts = [f'host{i}.example.com' for i in range(100)]
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    tasks = [run_command(sem, h, 'hostname') for h in hosts]
    results = await asyncio.gather(*tasks)

    succeeded = 0
    failed = 0
    for host, output, error in results:
        if error:
            print(f'FAIL {host}: {error}')
            failed += 1
        else:
            print(f'OK   {host}: {output}')
            succeeded += 1

    print(f'\n成功: {succeeded}, 失败: {failed}')

asyncio.run(main())
```

## 批量文件传输

并行从多台主机下载文件：

```python
import asyncio
import asyncssh

async def fetch_log(sem, host, remote_path, local_path):
    async with sem:
        try:
            async with asyncssh.connect(host, known_hosts=None) as conn:
                async with await conn.start_sftp_client() as sftp:
                    await sftp.get(remote_path, local_path)
                    return host, True, None
        except Exception as e:
            return host, False, str(e)

async def main():
    hosts = ['web1', 'web2', 'web3']
    sem = asyncio.Semaphore(5)

    tasks = [
        fetch_log(sem, h, '/var/log/syslog', f'./logs/{h}-syslog')
        for h in hosts
    ]

    results = await asyncio.gather(*tasks)
    for host, ok, error in results:
        status = 'OK' if ok else 'FAIL'
        print(f'{status} {host}: {error or "已下载"}')

asyncio.run(main())
```

## 带超时的并行

```python
import asyncio
import asyncssh

async def run_with_timeout(host, command, timeout=30):
    try:
        async with asyncssh.connect(host, known_hosts=None) as conn:
            result = await conn.run(command, timeout=timeout)
            return host, result.stdout, None
    except asyncio.TimeoutError:
        return host, None, '超时'
    except Exception as e:
        return host, None, str(e)

async def main():
    hosts = ['slow1', 'slow2', 'fast1']
    tasks = [run_with_timeout(h, 'sleep 5 && echo done', timeout=3)
             for h in hosts]
    results = await asyncio.gather(*tasks)

    for host, output, error in results:
        print(f'{host}: {error or output.strip()}')

asyncio.run(main())
```

## 长连接复用

对同一主机执行多个命令时，复用连接比每次新建连接更高效：

```python
import asyncio
import asyncssh

async def run_multiple_commands(host, commands):
    async with asyncssh.connect(host, known_hosts=None) as conn:
        results = await asyncio.gather(
            *[conn.run(cmd) for cmd in commands]
        )
        return [(r.returncode, r.stdout) for r in results]

async def main():
    commands = ['uname -a', 'df -h', 'free -m', 'uptime']
    results = await run_multiple_commands('localhost', commands)

    for cmd, (rc, output) in zip(commands, results):
        print(f'$ {cmd} (exit {rc})')
        print(output)

asyncio.run(main())
```

## 并行 SFTP 操作

```python
import asyncio
import asyncssh

async def sftp_operations(host):
    async with asyncssh.connect(host, known_hosts=None) as conn:
        async with await conn.start_sftp_client() as sftp:
            files = await sftp.listdir('.')
            stat = await sftp.stat('.')
            return host, files, stat.size

async def main():
    hosts = ['host1', 'host2']
    results = await asyncio.gather(*[sftp_operations(h) for h in hosts])

    for host, files, _ in results:
        print(f'{host}: {len(files)} 个文件')

asyncio.run(main())
```

## 完整运维示例

```python
import asyncio
import asyncssh
import json
from datetime import datetime

async def check_host(sem, host):
    async with sem:
        result = {'host': host, 'timestamp': datetime.utcnow().isoformat()}
        try:
            async with asyncssh.connect(
                host,
                username='monitor',
                client_keys=['~/.ssh/monitor_key'],
                known_hosts='~/.ssh/known_hosts',
                connect_timeout=10
            ) as conn:
                checks = await asyncio.gather(
                    conn.run('hostname'),
                    conn.run('uptime'),
                    conn.run('df -h /'),
                    conn.run('free -m'),
                    return_exceptions=True
                )

                result['status'] = 'online'
                result['hostname'] = checks[0].stdout.strip()
                result['uptime'] = checks[1].stdout.strip()
                result['disk'] = checks[2].stdout.strip()
                result['memory'] = checks[3].stdout.strip()

        except asyncssh.PermissionDenied:
            result['status'] = 'auth_failed'
        except asyncio.TimeoutError:
            result['status'] = 'timeout'
        except (OSError, asyncssh.ConnectionLost) as e:
            result['status'] = 'unreachable'
            result['error'] = str(e)

        return result

async def main():
    hosts = [f'10.0.0.{i}' for i in range(1, 51)]
    sem = asyncio.Semaphore(20)

    tasks = [check_host(sem, h) for h in hosts]
    results = await asyncio.gather(*tasks)

    online = sum(1 for r in results if r['status'] == 'online')
    print(f'在线: {online}/{len(results)}')

    with open('report.json', 'w') as f:
        json.dump(results, f, indent=2)

asyncio.run(main())
```

## 相关概念

- [异步连接详解](../concepts/02-async-connection.md)
- [高级模式](../concepts/11-advanced-patterns.md)
- [异步执行命令](async-command.md)

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](../references/asyncssh-source.md)。
