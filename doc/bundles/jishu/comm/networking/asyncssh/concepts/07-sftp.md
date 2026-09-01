---
type: Concept
title: SFTP 文件传输
description: SFTPClient/SFTPServer、get/put/mget/mput、stat/listdir/chmod/chown、SFTPAttrs、SFTPClientFile、VFS、协议版本 v3-v6
tags: [asyncssh, sftp, file-transfer, sftpclient]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# SFTP 文件传输

## 启动 SFTP 客户端

通过 `SSHClientConnection.start_sftp_client()` 协程创建 `SFTPClient`（sftp.py:3829）：

```python
async with await conn.start_sftp_client() as sftp:
    files = await sftp.listdir('.')
```

`start_sftp_client()` 参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `env` | `()` | SFTP 会话环境变量 |
| `send_env` | `()` | 从本地环境发送的变量名模式 |
| `path_encoding` | `'utf-8'` | 路径编码，None 表示 bytes |
| `path_errors` | `'strict'` | 编码错误处理策略 |
| `sftp_version` | 3 | 最大支持 SFTP 版本（3-6） |

`SFTPClient` 支持异步上下文管理器，退出时自动调用 `exit()` 和 `wait_closed()`。

## 文件传输

### get —— 下载

```python
await sftp.get('remote_file.txt', 'local_file.txt')
```

`get()` 支持进度回调和错误处理：

```python
def progress(src_path, dst_path, copied, total):
    print(f'{copied}/{total} bytes')

await sftp.get('remote.tar.gz', 'local.tar.gz',
               progress_handler=progress)
```

递归下载目录：

```python
await sftp.get('remote_dir/', 'local_dir/', recurse=True)
```

### put —— 上传

```python
await sftp.put('local_file.txt', 'remote_file.txt')
await sftp.put('local_dir/', 'remote_dir/', recurse=True,
               progress_handler=progress)
```

### 批量传输

```python
await sftp.mget('/remote/logs/*.log', 'local_logs/')
await sftp.mput('local_data/*.csv', '/remote/data/')
```

支持通配符 `*` 和 `?`。

### 远程复制

```python
await sftp.copy('/remote/source.txt', '/remote/dest.txt')
await sftp.remote_copy(src_sftp, 'source.txt', dst_sftp, 'dest.txt')
```

`remote_copy()` 使用 SFTP `copy-data` 扩展（服务端支持时），数据不经客户端中转。

## 目录操作

```python
files = await sftp.listdir('.')              # 文件名列表
entries = await sftp.readdir('.')            # SFTPName 列表
async for entry in sftp.scandir('.'):        # 异步迭代器
    print(entry.filename, entry.attrs.size)

await sftp.mkdir('new_dir')
await sftp.makedirs('path/to/deep/dir')      # 递归创建
await sftp.rmdir('empty_dir')
await sftp.rmtree('dir_tree')                # 递归删除
```

`listdir()` 返回 `Sequence[BytesOrStr]`（文件名），`readdir()` 和 `scandir()` 返回 `SFTPName` 对象（含属性）。

## 文件属性

### stat / lstat

```python
attrs = await sftp.stat('file.txt')
print(attrs.size, oct(attrs.permissions), attrs.uid, attrs.gid)

link_attrs = await sftp.lstat('symlink')     # 不跟随符号链接
```

`SFTPAttrs`（sftp.py:1658）包含的字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `size` | int | 文件大小（字节） |
| `uid` | int | 所有者 UID |
| `gid` | int | 所有者 GID |
| `permissions` | int | 权限位 |
| `atime` | int | 访问时间（秒） |
| `mtime` | int | 修改时间（秒） |
| `atime_ns` | int | 访问时间（纳秒） |
| `mtime_ns` | int | 修改时间（纳秒） |
| `createtime` | int | 创建时间 |
| `type` | int | 文件类型 |
| `nlink` | int | 硬链接数 |
| `acl` | list | ACL |
| `extended` | dict | 扩展属性 |

### chmod / chown / utime / truncate

```python
await sftp.chmod('file.txt', 0o755)
await sftp.chown('file.txt', uid=1000, gid=1000)
await sftp.chown('file.txt', owner='user', group='group')  # SFTP v4+
await sftp.utime('file.txt', (atime, mtime))
await sftp.truncate('file.txt', 1024)
```

### setstat —— 批量设置属性

```python
attrs = SFTPAttrs(permissions=0o644, uid=1000, gid=1000)
await sftp.setstat('file.txt', attrs)
```

### 文件系统信息

```python
vfs_attrs = await sftp.statvfs('/')
print(vfs_attrs.f_bytes, vfs_attrs.f_bavail)
```

### 便捷查询

```python
await sftp.exists('file.txt')       # bool
await sftp.lexists('symlink')       # 不跟随链接
await sftp.isdir('path')            # bool
await sftp.isfile('path')           # bool
await sftp.islink('path')           # bool
await sftp.getsize('file.txt')      # int
await sftp.getmtime('file.txt')     # float
await sftp.getatime('file.txt')     # float
```

## 文件读写

### open —— 返回 SFTPClientFile

```python
async with sftp.open('remote.txt', 'r') as f:
    content = await f.read()

async with sftp.open('remote.bin', 'wb') as f:
    await f.write(b'binary data')
```

`SFTPClientFile`（sftp.py:3310）支持：

| 方法 | 说明 |
|------|------|
| `async read(size=-1)` | 读取数据 |
| `async read_parallel(size=-1, block_size=..., max_requests=...)` | 并行读取优化 |
| `async write(data, offset=None)` | 写入数据 |
| `async seek(offset, from_what=SEEK_SET)` | 移动文件指针 |
| `async tell()` | 返回当前偏移 |
| `async stat(flags=...)` | 获取文件属性 |
| `async setstat(attrs)` | 设置文件属性 |
| `async chmod(mode)` | 修改权限 |
| `async chown(uid, gid)` | 修改所有者 |
| `async utime(times=None)` | 修改时间 |
| `async truncate(size=None)` | 截断文件 |
| `async fsync()` | 同步到磁盘 |
| `async lock(offset, length, flags)` | 字节范围锁 |
| `async unlock(offset, length)` | 解锁 |
| `async close()` | 关闭文件 |

### open56 —— SFTP v5/v6 风格打开

```python
f = await sftp.open56('file.txt',
                      desired_access=READ_DATA | WRITE_DATA,
                      create_attributes=SFTPAttrs(permissions=0o644))
```

## 路径操作

```python
await sftp.chdir('/path/to/dir')
cwd = await sftp.getcwd()

real = await sftp.realpath('relative/path')
target = await sftp.readlink('link')
await sftp.symlink('target', 'link_path')
await sftp.link('old', 'new')          # 硬链接

await sftp.rename('old', 'new')
await sftp.posix_rename('old', 'new')  # POSIX 语义（原子替换）
await sftp.remove('file.txt')
await sftp.unlink('file.txt')
```

路径编码由 `path_encoding` 参数控制：
- 默认 `'utf-8'`：路径以 `str` 传入返回
- `None`：路径以 `bytes` 处理

## 通配符匹配

```python
matches = await sftp.glob('/var/log/*.log')
entries = await sftp.glob_sftpname('/var/log/*.log')
```

## SFTPClient 属性

```python
sftp.version              # SFTP 协议版本（3-6）
sftp.limits               # SFTPLimits 对象
sftp.supports_remote_copy # 是否支持 copy-data 扩展
sftp.logger               # 关联的 logger
```

## SFTPLimits

`SFTPLimits`（sftp.py:2159）描述服务器能力限制：

| 字段 | 说明 |
|------|------|
| `max_read_size` | 最大读取块大小 |
| `max_write_size` | 最大写入块大小 |
| `max_open_handles` | 最大打开句柄数 |
| `max_vendor_id` | 供应商 ID 长度 |

## SFTP 服务端

`SFTPServer`（sftp.py:6991）在 SSH 服务端提供 SFTP 子系统：

```python
class MySSHServer(asyncssh.SSHServer):
    def session_requested(self):
        return True

async def handle_client(process):
    process.exit(0)

await asyncssh.create_server(
    MySSHServer, '', 22,
    server_host_keys=['host_key'],
    sftp_factory=SFTPServer
)
```

### VFS 抽象

`SFTPServerFS`（sftp.py:8153）是虚拟文件系统基类，可子类化将 SFTP 操作映射到任意后端：

```python
class MyFS(SFTPServerFS):
    async def stat(self, path):
        ...
    async def open(self, path, mode, attrs):
        ...
```

## SFTP 异常层次

`SFTPError`（sftp.py:944）是所有 SFTP 异常的基类，30+ 子类映射 SFTP 协议状态码：

- `SFTPEOFError`：文件结束
- `SFTPNoSuchFile`：文件不存在
- `SFTPPermissionDenied`：权限不足
- `SFTPFailure`：通用失败
- `SFTPNoConnection`：无连接
- `SFTPConnectionLost`：连接丢失
- `SFTPOpUnsupported`：操作不支持
- `SFTPFileAlreadyExists`：文件已存在
- `SFTPDirNotEmpty`：目录非空
- `SFTPNoSpaceOnFilesystem`：磁盘空间不足
- `SFTPQuotaExceeded`：配额超限
- `SFTPInvalidFilename`：无效文件名
- `SFTPLinkLoop`：符号链接循环

## 相关概念

- [SCP 文件复制](08-scp.md) —— SCP 协议与 SFTP 的区别
- [流与进程](04-streams-processes.md) —— 通道基础
- [服务端开发](10-server.md) —— SFTPServer 配置
- [paramiko SFTP 文件传输](../../paramiko/concepts/07-sftp.md)（同步 SFTP 对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](../references/asyncssh-source.md)。
