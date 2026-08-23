---
type: Example
title: 文件上传下载
description: 使用 fabric 的 get/put 方法进行 SFTP 文件传输、目录操作、file-like 对象与批量传输
tags: [fabric, example, sftp, file-transfer, upload, download]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 文件上传下载

## 场景

通过 SFTP 在本地和远程服务器之间传输文件，包括单文件上传下载、file-like 对象操作、权限保留和批量传输。

## 上传文件

### 基本上传

```python
from fabric import Connection

c = Connection("web.example.com", user="deploy")

# 上传到远程家目录，使用本地文件名
c.put("app.tar.gz")
# 远程路径: ~/app.tar.gz

# 指定远程路径
c.put("app.tar.gz", "/tmp/app.tar.gz")

# 远程路径是目录时，自动使用本地文件名
c.put("app.tar.gz", "/tmp/releases/")
# 远程路径: /tmp/releases/app.tar.gz
```

### 带权限保留

```python
# 本地文件权限 0o755，上传后远程文件也设置为 0o755
c.put("deploy.sh", "/opt/app/deploy.sh")

# 不保留权限
c.put("deploy.sh", "/opt/app/deploy.sh", preserve_mode=False)
```

### 使用 file-like 对象上传

```python
from io import BytesIO, StringIO

# 从内存上传二进制数据
data = b"Hello, World!"
c.put(BytesIO(data), "/tmp/hello.txt")

# 从内存上传文本
text = "key=value\n"
c.put(StringIO(text), "/tmp/config.ini")
```

file-like 对象必须有 `.write()` 方法且可调用。fabric 会在上传前 `seek(0)`，上传后恢复文件指针位置。file-like 对象上传时 remote 参数是必需的。

## 下载文件

### 基本下载

```python
# 下载到当前目录，使用远程文件名
c.get("/var/log/syslog")
# 本地路径: ./syslog

# 指定本地路径
c.get("/var/log/syslog", "/tmp/syslog")

# 本地路径是目录时，自动附加远程文件名
c.get("/var/log/syslog", "/tmp/logs/")
# 本地路径: /tmp/logs/syslog
```

### 路径插值

本地路径支持 `{host}`、`{user}`、`{port}`、`{basename}`、`{dirname}` 变量：

```python
c.get(
    "/var/log/nginx/access.log",
    "logs/{host}/{basename}",
)
# 例如: logs/web.example.com/access.log
```

不存在的目录会自动创建（`Path.mkdir(parents=True, exist_ok=True)`）。

### 使用 file-like 对象下载

```python
from io import BytesIO

buf = BytesIO()
c.get("/etc/hostname", buf)
hostname = buf.getvalue().decode().strip()
print(f"远程主机名: {hostname}")
```

## 传输结果对象

`get()` 和 `put()` 都返回 `transfer.Result`：

```python
result = c.put("local.txt", "/tmp/remote.txt")

print(f"本地: {result.orig_local} -> {result.local}")
print(f"远程: {result.orig_remote} -> {result.remote}")
print(f"连接: {result.connection.host}")
```

## 实际场景

### 场景一：部署应用包

```python
from fabric import Connection

def deploy_app(host, archive_path):
    with Connection(host, user="deploy") as c:
        print("上传应用包...")
        c.put(archive_path, "/tmp/app.tar.gz")

        print("解压...")
        c.run("mkdir -p /opt/app")
        c.run("tar xzf /tmp/app.tar.gz -C /opt/app/")

        print("安装依赖...")
        c.run("pip install -r /opt/app/requirements.txt")

        print("重启服务...")
        c.sudo("systemctl restart myapp")

        print("清理...")
        c.run("rm /tmp/app.tar.gz")

        print("完成")
```

### 场景二：下载日志并按主机分类

```python
from fabric import ThreadingGroup
from datetime import datetime

group = ThreadingGroup("web1", "web2", "web3", user="deploy")

date_str = datetime.now().strftime("%Y%m%d")
remote_log = f"/var/log/myapp/app-{date_str}.log"
local_path = f"logs/{date_str}/{{host}}.log"

group.get(remote_log, local_path)
```

### 场景三：上传配置文件

```python
from fabric import Connection
from io import StringIO

config = """
[server]
host = 0.0.0.0
port = 8000
debug = false
"""

c = Connection("web.example.com")
c.put(StringIO(config.strip()), "/etc/myapp/config.ini")
c.sudo("chown myapp:myapp /etc/myapp/config.ini")
c.sudo("systemctl restart myapp")
```

### 场景四：从远程读取数据处理

```python
from fabric import Connection
import json
from io import BytesIO

c = Connection("db.example.com", user="deploy")

buf = BytesIO()
c.get("/var/lib/myapp/export.json", buf)
data = json.loads(buf.getvalue())

for record in data["records"]:
    print(f"  {record['id']}: {record['name']}")
```

### 场景五：上传后校验

```python
from fabric import Connection
import hashlib

def put_with_checksum(c, local_path, remote_path):
    c.put(local_path, remote_path)

    local_hash = hashlib.sha256(open(local_path, "rb").read()).hexdigest()
    result = c.run(f"sha256sum {remote_path}", hide=True)
    remote_hash = result.stdout.split()[0]

    if local_hash == remote_hash:
        print(f"校验通过: {local_hash[:16]}...")
        return True
    else:
        print(f"校验失败! 本地={local_hash[:16]} 远程={remote_hash[:16]}")
        return False

c = Connection("web.example.com")
put_with_checksum(c, "app.tar.gz", "/tmp/app.tar.gz")
```

## 使用底层 SFTPClient

对于更复杂的 SFTP 操作，直接获取 paramiko 的 SFTPClient：

```python
c = Connection("web.example.com")
sftp = c.sftp()

# 列目录
entries = sftp.listdir_attr("/var/log")
for entry in entries:
    print(f"{entry.filename} ({entry.st_size} bytes)")

# 创建目录
sftp.mkdir("/tmp/newdir")

# 删除文件
sftp.remove("/tmp/old-file")

# 重命名
sftp.posix_rename("/tmp/old", "/tmp/new")

# 修改权限
sftp.chmod("/tmp/script.sh", 0o755)

# 获取文件属性
attr = sftp.stat("/etc/passwd")
print(f"大小: {attr.st_size}, 权限: {oct(attr.st_mode)}")
```

`c.sftp()` 使用 memoize，同一 Connection 只创建一个 SFTPClient 实例。

## 注意事项

1. **SFTP 不展开 `~`**：路径 `~/tmp/file` 不会被展开，使用相对路径（相对于家目录）或绝对路径
2. **递归目录不支持**：fabric 的 get/put 只处理单文件，递归需自行遍历或使用 rsync
3. **Group.get() 默认分子目录**：Group 批量下载时 local 默认为 `"{host}/"`
4. **file-like 对象上传时必须指定 remote**：fabric 无法从无名称的流对象推断远程文件名
5. **权限保留依赖 SFTP stat**：远程文件权限通过 SFTP 协议获取，不是通过 shell `ls`

## 相关示例

- [基础部署脚本](basic-deploy.md)
- [多服务器组并行操作](multi-server-group.md)
- [paramiko SFTP 文档](../../paramiko/concepts/07-sftp.md) — 底层 SFTPClient 完整 API
