---
type: Concept
title: SFTP 文件传输
description: SFTPClient 全解——put/get 文件传输、listdir/stat/chmod/chown 目录操作、SFTPFile、SFTPAttributes
tags: [paramiko, sftp, file-transfer]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# SFTP 文件传输

## SFTPClient 概述

`SFTPClient` 实现了 SSH 文件传输协议（SFTP），在 SSH 通道上提供远程文件操作。它继承 `BaseSFTP` 和 `ClosingContextManager`，支持上下文管理器。

### 创建 SFTP 会话

```python
sftp = client.open_sftp()

sftp = paramiko.SFTPClient.from_transport(transport)
```

`from_transport(cls, t, window_size=None, max_packet_size=None)` 打开新的 session 通道，请求 "sftp" 子系统，然后构造 SFTPClient。

调整窗口和包大小可能影响传输速度：

```python
sftp = SFTPClient.from_transport(
    transport,
    window_size=4194304,
    max_packet_size=65536,
)
```

### 关闭

```python
sftp.close()

with client.open_sftp() as sftp:
    sftp.put("local.txt", "remote.txt")
```

## 目录操作

### 列出目录

```python
files = sftp.listdir(".")
for name in files:
    print(name)

entries = sftp.listdir_attr("/var/log")
for entry in entries:
    print(entry.filename, entry.st_size, entry.st_mtime)

for entry in sftp.listdir_iter("/tmp", read_aheads=50):
    print(entry.filename, entry.st_size)
```

三个方法的区别：

| 方法 | 返回类型 | 特点 |
|------|---------|------|
| `listdir(path)` | `list[str]` | 仅文件名，最轻量 |
| `listdir_attr(path)` | `list[SFTPAttributes]` | 含属性，一次加载 |
| `listdir_iter(path, read_aheads)` | 迭代器 | 异步预取，适合大目录 |

### 创建和删除目录

```python
sftp.mkdir("/path/to/newdir", mode=0o755)
sftp.rmdir("/path/to/emptydir")
```

### 当前工作目录

```python
sftp.chdir("/home/user")
print(sftp.getcwd())
sftp.chdir()
```

`chdir(path=None)` 传入 None 重置为用户主目录（发送 REALPATH 请求 "."）。

### 路径规范化

```python
real_path = sftp.normalize("~/docs")
```

## 文件操作

### 打开远程文件

```python
with sftp.open("/remote/path/file.txt", "r") as f:
    content = f.read()

with sftp.open("/remote/path/output.txt", "w") as f:
    f.write(b"hello world\n")
```

`open(filename, mode="r", bufsize=-1)` 返回 `SFTPFile` 对象，继承 `BufferedFile`，支持标准文件接口。

模式字符：`r`（读）、`w`（写）、`a`（追加）、`+`（读写）、`b`（二进制，SFTP 默认二进制）。

### 删除和重命名

```python
sftp.remove("/path/to/file.txt")
sftp.rename("/old/name.txt", "/new/name.txt")
sftp.posix_rename("/old/name.txt", "/new/name.txt")
```

`rename` 使用 SSH_FXP_RENAME，`posix_rename` 使用 posix-rename@openssh.com 扩展（原子替换目标文件）。

### 符号链接

```python
sftp.symlink("/path/to/target", "/path/to/link")
target = sftp.readlink("/path/to/link")
```

### 截断文件

```python
sftp.truncate("/path/to/file", 1024)
```

## 文件属性

### 获取属性

```python
attr = sftp.stat("/path/to/file")
print(attr.st_size, attr.st_mode, attr.st_uid, attr.st_gid)
print(attr.st_atime, attr.st_mtime)

lstat_attr = sftp.lstat("/path/to/symlink")
```

`stat` 跟随符号链接，`lstat` 不跟随。

返回的 `SFTPAttributes` 对象镜像 `os.stat`：

| 属性 | 说明 |
|------|------|
| `st_size` | 文件大小（字节） |
| `st_uid` | 所有者 UID |
| `st_gid` | 所有者 GID |
| `st_mode` | 权限和文件类型 |
| `st_atime` | 访问时间 |
| `st_mtime` | 修改时间 |
| `attr` | 扩展属性字典 |
| `filename` | 文件名（listdir_attr 时） |

### 修改属性

```python
sftp.chmod("/path/to/file", 0o644)
sftp.chown("/path/to/file", uid=1000, gid=1000)
sftp.utime("/path/to/file", (atime, mtime))
```

### SFTPAttributes.from_stat

从本地 os.stat 结果创建属性对象（主要用于服务端）：

```python
import os
local_stat = os.stat("/local/file")
attr = paramiko.SFTPAttributes.from_stat(local_stat, filename="file.txt")
```

## 文件传输

### 上传

```python
sftp.put("local.tar.gz", "/remote/backup.tar.gz")

sftp.put(
    "local.tar.gz",
    "/remote/backup.tar.gz",
    callback=lambda transferred, total: print(f"{transferred}/{total}"),
    confirm=True,
)
```

`put(localpath, remotepath, callback=None, confirm=True)`：
- 读取本地文件，写入远程
- `callback(bytes_transferred, total_bytes)` 进度回调
- `confirm=True` 时上传后 stat 验证大小

### 上传文件对象

```python
with open("local.dat", "rb") as f:
    sftp.putfo(f, "/remote/file.dat", file_size=1024, callback=None, confirm=True)
```

### 下载

```python
sftp.get("/remote/data.csv", "local_data.csv")

sftp.get(
    "/remote/data.csv",
    "local_data.csv",
    callback=lambda transferred, total: print(f"{transferred}/{total}"),
)
```

### 下载到文件对象

```python
with open("output.dat", "wb") as f:
    sftp.getfo("/remote/input.dat", f, callback=None)
```

### 传输机制

`put`/`get` 内部通过 `_transfer_with_callback` 分块读写，默认使用 SFTPFile 的流水线（pipeline）和预取（prefetch）优化传输性能。

## SFTPFile

`SFTPFile` 继承 `BufferedFile`，是远程文件的代理对象。

```python
f = sftp.open("/remote/file", "r")

data = f.read(1024)
line = f.readline()
lines = f.readlines()

f.seek(0, 0)
pos = f.tell()

f.prefetch(file_size)

f.close()
```

### 预取优化

`SFTPFile.MAX_REQUEST_SIZE = 32768` 限制单个读请求大小。prefetch 机制发送多个未完成的读请求，利用网络往返延迟重叠：

```python
with sftp.open("/remote/large.file", "rb") as f:
    f.prefetch(f.stat().st_size)
    data = f.read()
```

### 流水线写入

`pipelined` 属性启用写流水线，多个写请求批量发送：

```python
with sftp.open("/remote/output", "wb") as f:
    f.set_pipelined(True)
    for chunk in data_chunks:
        f.write(chunk)
```

## 状态码

SFTP 协议定义的状态码：

| 常量 | 值 | 说明 |
|------|---|------|
| `SFTP_OK` | 0 | 成功 |
| `SFTP_EOF` | 1 | 文件结束 |
| `SFTP_NO_SUCH_FILE` | 2 | 文件不存在 |
| `SFTP_PERMISSION_DENIED` | 3 | 权限拒绝 |
| `SFTP_FAILURE` | 4 | 一般失败 |
| `SFTP_BAD_MESSAGE` | 5 | 错误消息 |
| `SFTP_NO_CONNECTION` | 6 | 无连接 |
| `SFTP_CONNECTION_LOST` | 7 | 连接丢失 |
| `SFTP_OP_UNSUPPORTED` | 8 | 操作不支持 |

## 获取底层通道

```python
channel = sftp.get_channel()
channel.settimeout(30)
```

## 常见模式

### 上传整个目录

```python
import os

def upload_dir(sftp, local_dir, remote_dir):
    sftp.mkdir(remote_dir)
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"
        if os.path.isfile(local_path):
            sftp.put(local_path, remote_path)
        elif os.path.isdir(local_path):
            upload_dir(sftp, local_path, remote_path)
```

### 带进度条的下载

```python
def progress(transferred, total):
    pct = transferred * 100 // total
    print(f"\r[{'=' * (pct // 2)}{' ' * (50 - pct // 2)}] {pct}%", end="")

sftp.get("/remote/bigfile.iso", "bigfile.iso", callback=progress)
print()
```

## 相关概念

- [SSHClient 详解](/concepts/02-ssh-client.md)
- [Channel 通道](/concepts/04-channel.md)
- [服务端开发](/concepts/09-server.md)
- [高级模式](/concepts/10-advanced-patterns.md)
- [文件传输示例](/examples/file-transfer.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](/references/paramiko-source.md)。
