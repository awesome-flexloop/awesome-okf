---
type: Example
title: SFTP 文件上传下载
description: 使用 SFTPClient 进行文件传输、目录操作、进度回调、批量上传下载的完整示例
tags: [paramiko, example, sftp, file-transfer]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# SFTP 文件上传下载

## 基本上传下载

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    with client.open_sftp() as sftp:
        sftp.put("local_file.txt", "/remote/path/file.txt")
        sftp.get("/remote/path/data.csv", "local_data.csv")
```

## 带进度回调的传输

```python
import paramiko
import sys

def progress(transferred, total):
    pct = transferred * 100 // total if total > 0 else 0
    bar_len = 40
    filled = bar_len * transferred // total if total > 0 else 0
    bar = "=" * filled + " " * (bar_len - filled)
    sys.stdout.write(f"\r[{bar}] {pct:3d}% ({transferred}/{total})")
    sys.stdout.flush()
    if transferred == total:
        print()

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    with client.open_sftp() as sftp:
        print("Uploading...")
        sftp.put(
            "large_file.tar.gz",
            "/remote/large_file.tar.gz",
            callback=progress,
        )

        print("Downloading...")
        sftp.get(
            "/remote/large_file.tar.gz",
            "downloaded.tar.gz",
            callback=progress,
        )
```

## 使用文件对象传输

```python
import paramiko
from io import BytesIO

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    with client.open_sftp() as sftp:
        content = b"Hello, remote file!\nThis is written from memory."
        sftp.putfo(BytesIO(content), "/remote/memory_file.txt")

        buf = BytesIO()
        sftp.getfo("/remote/memory_file.txt", buf)
        print(buf.getvalue().decode())
```

## 目录操作

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    with client.open_sftp() as sftp:
        sftp.mkdir("/home/user/newdir", mode=0o755)

        sftp.chdir("/home/user/newdir")
        print("CWD:", sftp.getcwd())

        with sftp.open("test.txt", "w") as f:
            f.write(b"test content\n")

        for entry in sftp.listdir_attr("."):
            print(f"  {entry.filename:20s} {entry.st_size:8d} bytes")

        print("stat:", sftp.stat("test.txt"))

        sftp.remove("test.txt")
        sftp.rmdir("/home/user/newdir")
```

## 递归上传目录

```python
import os
import paramiko

def upload_dir(sftp, local_dir, remote_dir):
    try:
        sftp.mkdir(remote_dir)
    except IOError:
        pass

    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir.rstrip("/") + "/" + item

        if os.path.isfile(local_path):
            print(f"Uploading: {remote_path}")
            sftp.put(local_path, remote_path)
        elif os.path.isdir(local_path):
            upload_dir(sftp, local_path, remote_path)

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    with client.open_sftp() as sftp:
        upload_dir(sftp, "./myproject", "/home/user/myproject")
```

## 递归下载目录

```python
import os
import paramiko

def download_dir(sftp, remote_dir, local_dir):
    os.makedirs(local_dir, exist_ok=True)

    for entry in sftp.listdir_attr(remote_dir):
        remote_path = remote_dir.rstrip("/") + "/" + entry.filename
        local_path = os.path.join(local_dir, entry.filename)

        import stat
        if stat.S_ISDIR(entry.st_mode):
            download_dir(sftp, remote_path, local_path)
        else:
            print(f"Downloading: {remote_path}")
            sftp.get(remote_path, local_path)

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    with client.open_sftp() as sftp:
        download_dir(sftp, "/home/user/docs", "./downloaded_docs")
```

## 文件属性操作

```python
import paramiko
import stat

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    with client.open_sftp() as sftp:
        attr = sftp.stat("/home/user/file.txt")
        print(f"Size: {attr.st_size}")
        print(f"Mode: {oct(attr.st_mode)}")
        print(f"UID:GID = {attr.st_uid}:{attr.st_gid}")

        sftp.chmod("/home/user/file.txt", 0o644)
        sftp.chown("/home/user/file.txt", 1000, 1000)

        import time
        now = time.time()
        sftp.utime("/home/user/file.txt", (now, now))

        sftp.truncate("/home/user/file.txt", 100)
```

## 符号链接操作

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    with client.open_sftp() as sftp:
        sftp.symlink("/home/user/original.txt", "/home/user/link.txt")

        target = sftp.readlink("/home/user/link.txt")
        print(f"Link target: {target}")

        lstat = sftp.lstat("/home/user/link.txt")
        import stat
        print(f"Is symlink: {stat.S_ISLNK(lstat.st_mode)}")
```

## 使用 SFTPFile 预取优化

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    sftp = client.open_sftp()

    with sftp.open("/remote/large_file.bin", "rb") as f:
        f.prefetch(f.stat().st_size)
        data = f.read()

    sftp.close()
    print(f"Read {len(data)} bytes")
```

## 列出目录（迭代器模式）

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    with client.open_sftp() as sftp:
        count = 0
        total_size = 0
        for entry in sftp.listdir_iter("/var/log", read_aheads=100):
            count += 1
            total_size += entry.st_size or 0
            print(f"  {entry.filename:30s} {entry.st_size or 0:>10d}")

        print(f"\nTotal: {count} files, {total_size} bytes")
```

## 相关概念

- [SFTP 文件传输](/concepts/07-sftp.md)
- [SSHClient 详解](/concepts/02-ssh-client.md)
- [Channel 通道](/concepts/04-channel.md)
- [基础连接示例](/examples/basic-connection.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](/references/paramiko-source.md)。
