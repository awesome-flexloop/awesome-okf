---
type: Concept
title: 文件传输
description: Transfer 类详解、get/put 文件上传下载、SFTP 封装、路径插值、file-like 对象支持与权限保留
tags: [fabric, transfer, sftp, file, upload, download]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 文件传输

## Transfer 类

`Transfer` 类封装了基于 SFTP 的文件上传下载功能。通常不直接实例化，而是通过 `Connection.get()` 和 `Connection.put()` 方法间接使用：

```python
# 这两种方式等价
c.get("/remote/file", "/local/file")
Transfer(c).get("/remote/file", "/local/file")
```

Transfer 内部通过 `connection.sftp()` 获取 `paramiko.SFTPClient` 实例。

## get() — 下载文件

```python
get(remote, local=None, preserve_mode=True)
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `remote` | str | 必填 | 远程文件路径（绝对或相对远程工作目录） |
| `local` | str/file-like | None | 本地保存路径或文件对象；None 则使用远程文件名保存到当前目录 |
| `preserve_mode` | bool | True | 是否将本地文件权限设置为与远程文件一致 |

### 基本用法

```python
# 下载到当前目录，使用远程文件名
c.get("/var/log/syslog")

# 指定本地路径
c.get("/var/log/syslog", "/tmp/syslog")

# 本地路径是目录时，自动附加远程文件名
c.get("/var/log/syslog", "/tmp/logs/")
# 保存为 /tmp/logs/syslog
```

### 路径插值

`local` 参数支持 `str.format()` 插值，可用变量：

| 变量 | 来源 |
|------|------|
| `{host}` | `connection.host` |
| `{user}` | `connection.user` |
| `{port}` | `connection.port` |
| `{basename}` | 远程路径的文件名（posixpath.basename） |
| `{dirname}` | 远程路径的目录名（posixpath.dirname） |

```python
c.get(
    "/var/log/nginx/access.log",
    "/tmp/{host}/{basename}",
)
# 例如: /tmp/web1/access.log
```

不存在的目录会通过 `Path.mkdir(parents=True, exist_ok=True)` 自动创建。

### file-like 对象

传入具有 `.write()` 方法的对象时，调用 `sftp.getfo()` 将内容写入该对象：

```python
from io import BytesIO

buf = BytesIO()
c.get("/etc/hostname", buf)
print(buf.getvalue().decode().strip())
```

### 权限保留

当 `preserve_mode=True` 时：
1. 通过 `sftp.stat(remote)` 获取远程文件的 `st_mode`
2. 使用 `stat.S_IMODE()` 提取权限位
3. 调用 `os.chmod(local, mode)` 设置本地文件权限

### 远程路径说明

SFTP 服务器的工作目录通常是连接用户的家目录。与 shell 不同，SFTP **不展开波浪号 `~`**：

```python
# 错误
c.get("~/tmp/file.txt")

# 正确（相对于家目录）
c.get("tmp/file.txt")
```

远程路径会被拼接为绝对路径：`posixpath.join(sftp.getcwd() or sftp.normalize("."), remote)`。

### 返回值

返回 `transfer.Result` 对象：

```python
result = c.get("/etc/hostname", "/tmp/hostname")
print(result.remote)      # 远程绝对路径
print(result.orig_remote) # 原始 remote 参数
print(result.local)       # 本地绝对路径
print(result.orig_local)  # 原始 local 参数
print(result.connection)  # Connection 对象
```

## put() — 上传文件

```python
put(local, remote=None, preserve_mode=True)
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `local` | str/file-like | 必填 | 本地文件路径或文件对象 |
| `remote` | str | None | 远程保存路径；None 则使用本地文件名保存到远程工作目录 |
| `preserve_mode` | bool | True | 是否将远程文件权限设置为与本地文件一致 |

### 基本用法

```python
# 上传到远程家目录，使用本地文件名
c.put("app.tar.gz")

# 指定远程路径
c.put("app.tar.gz", "/tmp/app.tar.gz")

# 远程路径是目录时，自动附加本地文件名
c.put("app.tar.gz", "/tmp/releases/")
```

当 `remote` 为 None 且 `local` 是文件路径时，自动取 `os.path.basename(local)` 作为远程文件名。当 `local` 是 file-like 对象且无 `.name` 属性时，remote 必须显式指定。

### file-like 对象

```python
from io import BytesIO

data = b"Hello, World!"
c.put(BytesIO(data), "/tmp/hello.txt")
```

文件对象上传时：
1. 记录当前指针位置 `local.tell()`
2. `seek(0)` 回到开头
3. 调用 `sftp.putfo(fl=local, remotepath=remote)`
4. 在 finally 中恢复指针位置

### 权限保留

当 `preserve_mode=True` 时：
1. 通过 `os.stat(local)` 获取本地文件的 `st_mode`
2. 使用 `stat.S_IMODE()` 提取权限位
3. 调用 `sftp.chmod(remote, mode)` 设置远程文件权限

### 远程目录自动检测

`put()` 通过 `is_remote_dir(remote)` 检测远程路径是否为目录（调用 `sftp.stat()` 并检查 `stat.S_ISDIR`）。如果是目录且 local 路径有文件名，自动拼接：`remote = posixpath.join(remote, local_base)`。

## transfer.Result

`Transfer` 的 `get()` 和 `put()` 都返回同一个 `Result` 类：

```python
class Result:
    def __init__(self, local, orig_local, remote, orig_remote, connection):
        self.local = local           # 处理后的（绝对）路径
        self.orig_local = orig_local # 原始参数值
        self.remote = remote         # 处理后的（绝对）路径
        self.orig_remote = orig_remote
        self.connection = connection
```

与 `runners.Result` 不同，`transfer.Result` 没有布尔真值行为——传输失败直接抛出异常（`OSError` 或 paramiko 异常）。

## 直接使用 SFTP 客户端

对于更复杂的 SFTP 操作，可通过 `Connection.sftp()` 获取底层 `paramiko.SFTPClient`：

```python
sftp = c.sftp()

# 列目录
files = sftp.listdir("/tmp")

# 创建目录
sftp.mkdir("/tmp/newdir")

# 删除文件
sftp.remove("/tmp/old")

# 检查文件属性
attr = sftp.stat("/etc/passwd")
print(attr.st_size, attr.st_mode)

# 修改权限
sftp.chmod("/tmp/script.sh", 0o755)
```

`sftp()` 方法使用 memoize 模式——同一 Connection 只创建一个 SFTPClient 实例，状态（如 `chdir`）会被保留。`close()` 时自动关闭 SFTP 会话。

## Group 批量传输

Group 的 `get()` 和 `put()` 可以在多台主机上批量传输：

```python
from fabric import ThreadingGroup

group = ThreadingGroup("web1", "web2", "web3")

# 批量上传同一文件
group.put("app.tar.gz", "/tmp/app.tar.gz")

# 批量下载（自动按主机名分子目录）
group.get("/var/log/nginx/access.log")
# 保存到:
# ./web1/access.log
# ./web2/access.log
# ./web3/access.log

# 使用路径插值自定义
group.get("/var/log/syslog", "/tmp/{host}-syslog")
```

Group.get() 默认 local 参数为 `"{host}/"`。Group 的文件操作返回 `GroupResult`，值为 `transfer.Result` 对象。

## 不支持的功能

- **递归目录传输**：fabric 不内置递归上传/下载目录的功能，需自行遍历或使用 rsync
- **进度回调**：Transfer 层不暴露 progress callback，但可直接使用 paramiko SFTPClient 的回调参数
- **SCP 协议**：仅支持 SFTP，不支持 SCP
- **远程到远程传输**：不支持两台远程主机之间直接传输

## 相关概念

- [Connection 详解](02-connection.md)
- [多主机并行](05-group-parallel.md)
- [paramiko SFTP](../../paramiko/concepts/07-sftp.md) — 底层 SFTPClient 的完整 API
