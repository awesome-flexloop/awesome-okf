---
type: Concept
title: 5分钟快速上手
description: 从安装到第一个异步 SSH 连接、执行命令、传输文件的快速入门
tags: [asyncssh, getting-started, ssh, asyncio]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 5分钟快速上手

## 前置条件

- Python 3.10+
- `pip install asyncssh`

## 第一个异步连接

asyncssh 的所有操作都是协程，必须在 `asyncio` 事件循环中运行：

```python
import asyncio
import asyncssh

async def main():
    async with asyncssh.connect('hostname', username='user',
                                password='secret') as conn:
        result = await conn.run('uname -a', check=True)
        print(result.stdout, end='')

asyncio.run(main())
```

`asyncssh.connect()` 是模块级协程，返回 `SSHClientConnection` 实例。`async with` 确保连接在退出时自动关闭。

## 执行命令

### 简单执行（收集全部输出）

`conn.run()` 是最高层的命令执行方法，等待命令结束并返回 `SSHCompletedProcess`：

```python
result = await conn.run('ls -la')
print('退出码:', result.returncode)
print('标准输出:', result.stdout)
print('标准错误:', result.stderr)
```

`check=True` 时，非零退出码会抛出 `ProcessError`：

```python
try:
    result = await conn.run('false', check=True)
except asyncssh.ProcessError as e:
    print(f'命令失败: exit_status={e.exit_status}, stderr={e.stderr}')
```

设置 `timeout` 参数可在超时后抛出 `TimeoutError`：

```python
result = await conn.run('sleep 10', timeout=5)
```

### 交互式进程

`conn.create_process()` 返回 `SSHClientProcess` 对象，可通过 `stdin`/`stdout`/`stderr` 流式交互：

```python
async with conn.create_process(term_type='xterm') as proc:
    proc.stdin.write('ls\n')
    await proc.stdin.drain()
    output = await proc.stdout.readline()
    print(output)
```

### 发送输入数据

```python
result = await conn.run('cat', input='Hello, asyncssh!\n')
print(result.stdout)
```

## SFTP 文件传输

```python
async with await conn.start_sftp_client() as sftp:
    await sftp.put('local_file.txt', 'remote_file.txt')
    await sftp.get('remote_file.txt', 'downloaded.txt')

    files = await sftp.listdir('.')
    print(files)

    stat = await sftp.stat('remote_file.txt')
    print(f'大小: {stat.size}, 权限: {oct(stat.permissions)}')
```

`start_sftp_client()` 是协程，返回 `SFTPClient`。支持 `async with` 自动关闭。

## SCP 文件复制

`asyncssh.scp()` 支持本地到远程、远程到本地、远程到远程复制：

```python
await asyncssh.scp('local.txt', ('hostname', '/remote/path/'),
                  username='user', password='secret')
```

## 多主机并行连接

利用 `asyncio.gather()` 同时连接多台主机：

```python
async def run_on_host(host):
    async with asyncssh.connect(host, username='user',
                                known_hosts=None) as conn:
        result = await conn.run('hostname')
        return result.stdout.strip()

results = await asyncio.gather(*[run_on_host(h) for h in hosts])
```

## 公钥认证

```python
async with asyncssh.connect('hostname', username='user',
                            client_keys=['~/.ssh/id_ed25519']) as conn:
    result = await conn.run('whoami')
```

`client_keys` 参数接受私钥文件路径列表，也可传入 `SSHKey` 对象（通过 `asyncssh.read_private_key()` 加载）。

## 已知主机密钥验证

默认情况下，asyncssh 会加载 `~/.ssh/known_hosts`。要禁用验证（不推荐生产环境）：

```python
async with asyncssh.connect('hostname', known_hosts=None) as conn:
    ...
```

## 端口转发

```python
listener = await conn.forward_local_port('localhost', 8080,
                                        'remote-db.internal', 5432)
print(f'本地转发监听在 {listener.get_port()}')
await listener.wait_closed()
```

## 下一步

- [异步连接详解](/concepts/02-async-connection.md) —— connect() 参数全解析、认证方式、连接生命周期
- [通道与流](/concepts/03-channels.md) —— SSHChannel、PTY、窗口调整
- [流与进程](/concepts/04-streams-processes.md) —— SSHReader/SSHWriter、create_process、SSHCompletedProcess
- [认证体系](/concepts/05-authentication.md) —— 密码/公钥/键盘交互/GSSAPI

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
