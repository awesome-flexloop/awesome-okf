---
type: Example
title: SFTP 文件传输
description: 使用 SFTPClient 上传下载文件、目录操作、进度回调、并行传输、文件属性
tags: [asyncssh, example, sftp, file-transfer, upload, download]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# SFTP 文件传输

## 基本上传下载

```python
import asyncio
import asyncssh

async def main():
    async with asyncssh.connect('localhost',
                                username='user',
                                known_hosts=None) as conn:
        async with await conn.start_sftp_client() as sftp:
            await sftp.put('local.txt', 'remote.txt')
            print('上传完成')

            await sftp.get('remote.txt', 'downloaded.txt')
            print('下载完成')

asyncio.run(main())
```

## 进度回调

```python
import asyncio
import asyncssh

def progress(src, dst, copied, total):
    pct = copied * 100 // total if total else 0
    bar = '#' * (pct // 5) + '-' * (20 - pct // 5)
    print(f'\r[{bar}] {pct}% ({copied}/{total})', end='')
    if copied == total:
        print()

async def main():
    async with asyncssh.connect('localhost', known_hosts=None) as conn:
        async with await conn.start_sftp_client() as sftp:
            await sftp.put('large_file.iso', '/remote/large_file.iso',
                           progress_handler=progress)

asyncio.run(main())
```

## 目录操作

```python
async def directory_ops(sftp):
    entries = await sftp.readdir('.')
    for entry in entries:
        t = 'd' if entry.attrs.is_dir() else '-'
        print(f'{t} {entry.filename} ({entry.attrs.size} bytes)')

    await sftp.mkdir('new_directory')
    await sftp.makedirs('path/to/nested/dir')

    files = await sftp.listdir('.')
    print(f'文件列表: {files}')

    await sftp.rmdir('new_directory')
    await sftp.rmtree('path/to')
```

## 文件属性操作

```python
async def file_attrs(sftp):
    attrs = await sftp.stat('remote.txt')
    print(f'大小: {attrs.size} 字节')
    print(f'权限: {oct(attrs.permissions)}')
    print(f'UID/GID: {attrs.uid}/{attrs.gid}')
    print(f'修改时间: {attrs.mtime}')

    await sftp.chmod('remote.txt', 0o644)
    await sftp.chown('remote.txt', uid=1000, gid=1000)

    import os
    os.utime('local.txt', (attrs.atime, attrs.mtime))

    if await sftp.exists('remote.txt'):
        print('文件存在')

    if await sftp.isfile('remote.txt'):
        print('是普通文件')

    if await sftp.isdir('.'):
        print('是目录')

    size = await sftp.getsize('remote.txt')
```

## 远程文件读写

使用 `sftp.open()` 返回 `SFTPClientFile`：

```python
async def remote_file_io(sftp):
    async with sftp.open('remote.txt', 'w') as f:
        await f.write('Hello, SFTP!\n')
        await f.write('Second line\n')

    async with sftp.open('remote.txt', 'r') as f:
        content = await f.read()
        print(content)

    async with sftp.open('remote.txt', 'r') as f:
        async for line in f:
            print(repr(line))
```

### 随机访问

```python
async def random_access(sftp):
    async with sftp.open('data.bin', 'rb') as f:
        await f.seek(1024)
        data = await f.read(256)
        pos = await f.tell()
        print(f'位置 {pos}, 读取 {len(data)} 字节')

    async with sftp.open('data.bin', 'r+b') as f:
        await f.seek(0)
        await f.write(b'HEADER')
        await f.fsync()
```

## 批量传输

### mget / mput

```python
async def batch_transfer(sftp):
    await sftp.mput('logs/*.log', '/remote/logs/')
    await sftp.mget('/remote/data/*.csv', './local_data/')
```

### 递归目录传输

```python
async def recursive_transfer(sftp):
    await sftp.put('local_dir/', '/remote/backup/',
                   recurse=True, preserve=True)
    await sftp.get('/remote/backup/', './restore/',
                   recurse=True, preserve=True)
```

## 通配符匹配

```python
async def glob_example(sftp):
    matches = await sftp.glob('/var/log/*.log')
    for path in matches:
        print(path)

    entries = await sftp.glob_sftpname('/home/*/.bashrc')
    for entry in entries:
        print(f'{entry.filename}: {entry.attrs.size} bytes')
```

## 符号链接

```python
async def symlinks(sftp):
    await sftp.symlink('/original/path', 'link_name')
    target = await sftp.readlink('link_name')
    print(f'链接目标: {target}')

    if await sftp.islink('link_name'):
        print('是符号链接')

    await sftp.link('original', 'hard_link')
```

## 路径操作

```python
async def path_ops(sftp):
    cwd = await sftp.getcwd()
    print(f'当前目录: {cwd}')

    await sftp.chdir('/tmp')
    real = await sftp.realpath('../var/log')
    print(f'真实路径: {real}')

    await sftp.rename('old.txt', 'new.txt')
    await sftp.posix_rename('old2.txt', 'new2.txt')

    await sftp.remove('file.txt')
    await sftp.unlink('another.txt')
```

## 并行传输

并行下载多个文件：

```python
import asyncio
import asyncssh

async def download_file(sftp, remote, local, sem):
    async with sem:
        await sftp.get(remote, local)
        print(f'下载: {remote}')

async def main():
    async with asyncssh.connect('localhost', known_hosts=None) as conn:
        async with await conn.start_sftp_client() as sftp:
            files = [f'log_{i}.txt' for i in range(20)]
            sem = asyncio.Semaphore(5)

            tasks = [
                download_file(sftp, f'/remote/{f}', f'./{f}', sem)
                for f in files
            ]
            await asyncio.gather(*tasks)

asyncio.run(main())
```

## Bytes 路径模式

设置 `path_encoding=None` 以 bytes 处理路径（适用于非 UTF-8 文件名）：

```python
async with await conn.start_sftp_client(path_encoding=None) as sftp:
    files = await sftp.listdir(b'/remote/path')
    for name in files:
        print(name)
```

## 完整备份脚本

```python
import asyncio
import asyncssh
from datetime import datetime

async def backup_host(host, remote_paths, local_dir):
    try:
        async with asyncssh.connect(
            host,
            username='backup',
            client_keys=['~/.ssh/backup_key'],
            known_hosts='~/.ssh/known_hosts'
        ) as conn:
            async with await conn.start_sftp_client() as sftp:
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

                for remote_path in remote_paths:
                    name = remote_path.rstrip('/').split('/')[-1]
                    local_path = f'{local_dir}/{host}/{timestamp}/{name}'

                    def progress(src, dst, copied, total):
                        pct = copied * 100 // total if total else 0
                        print(f'\r  {name}: {pct}%', end='')

                    await sftp.get(remote_path, local_path,
                                   recurse=True, preserve=True,
                                   progress_handler=progress)
                    print()

                return host, True, None
    except Exception as e:
        return host, False, str(e)

async def main():
    hosts = {
        'web1': ['/var/log/nginx', '/etc/nginx'],
        'db1': ['/var/lib/postgresql/backup'],
    }

    tasks = [
        backup_host(host, paths, './backups')
        for host, paths in hosts.items()
    ]

    results = await asyncio.gather(*tasks)
    for host, ok, error in results:
        status = 'OK' if ok else f'FAIL: {error}'
        print(f'{host}: {status}')

asyncio.run(main())
```

## 相关概念

- [SFTP 文件传输](/concepts/07-sftp.md)
- [SCP 文件复制](/concepts/08-scp.md)
- [多主机并行连接](/examples/parallel-connections.md)
- [paramiko SFTP 文件传输](../../paramiko/examples/file-transfer.md)（同步 SFTP 对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
