---
type: Concept
title: 5分钟快速上手
description: 从安装到第一个 fab 任务、Connection 基本用法、远程命令执行和文件传输的快速入门
tags: [fabric, getting-started, tutorial]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 5分钟快速上手

## 安装

```bash
pip install fabric
```

## 方式一：Python 脚本中直接使用

最简单的用法是创建 `Connection` 对象并执行命令：

```python
from fabric import Connection

c = Connection("web.example.com", user="deploy")
result = c.run("uname -a")
print(f"Exit code: {result.exited}")
print(f"STDOUT: {result.stdout.strip()}")
```

### 使用上下文管理器

推荐使用 `with` 语句确保连接被正确关闭：

```python
from fabric import Connection

with Connection("web.example.com", user="deploy") as c:
    c.run("uptime")
    c.run("df -h /")
    c.put("app.tar.gz", "/tmp/app.tar.gz")
    c.run("tar xzf /tmp/app.tar.gz -C /opt/app/")
```

### 主机简写

`Connection` 的第一个参数支持 `user@host:port` 简写格式：

```python
Connection("deploy@web.example.com")
Connection("web.example.com:2222")
Connection("deploy@web.example.com:2222")
```

> **注意**：IPv6 地址包含多个 `:`，无法使用 `host:port` 简写，请使用显式的 `port=` 参数。

### 使用密钥认证

通过 `connect_kwargs` 传递 paramiko 连接参数：

```python
c = Connection(
    host="web.example.com",
    user="deploy",
    connect_kwargs={
        "key_filename": "/home/user/.ssh/id_ed25519",
    },
)
```

### sudo 命令

```python
c.sudo("systemctl restart nginx")
c.sudo("apt-get update", password="my-sudo-password")
```

## 方式二：fabfile 任务

fabric 基于 invoke，因此可以使用 `fab` 命令运行定义在 `fabfile.py` 中的任务。

### 创建 fabfile.py

```python
from fabric import task

@task
def deploy(c):
    c.run("git pull")
    c.run("pip install -r requirements.txt")
    c.sudo("systemctl restart myapp")

@task
def uptime(c):
    c.run("uptime")
```

### 运行任务

```bash
# 在单台主机上运行
fab -H web.example.com deploy

# 在多台主机上运行
fab -H web1.example.com,web2.example.com deploy

# 运行多个任务
fab -H web.example.com uptime deploy
```

> **注意**：`-H` 参数的主机字符串也支持 `user@host:port` 简写。

### 任务中指定主机

通过 `@task(hosts=[...])` 装饰器指定默认主机列表：

```python
from fabric import task

@task(hosts=["web1.example.com", "web2.example.com"])
def deploy(c):
    c.run("git pull")
    c.sudo("systemctl restart myapp")
```

然后直接运行 `fab deploy` 即可。CLI 的 `-H` 参数优先级高于装饰器中的 hosts。

### 直接运行远程命令（无需 fabfile）

```bash
fab -H web.example.com -- uname -a
fab -H web1,web2 -- "df -h /"
```

`--` 之后的内容作为 remainder 直接通过 `c.run()` 执行。

## Result 对象

`run()` 和 `sudo()` 返回 `Result` 对象（继承自 `invoke.runners.Result`），包含：

| 属性 | 说明 |
|------|------|
| `command` | 执行的命令字符串 |
| `stdout` | 标准输出 |
| `stderr` | 标准错误 |
| `exited` | 退出码（int） |
| `ok` | 是否成功退出（exited == 0） |
| `failed` | 是否失败（exited != 0） |
| `pty` | 是否使用了 PTY |
| `connection` | 关联的 Connection 对象（fabric 扩展） |

默认情况下，命令失败（退出码非零）会抛出 `UnexpectedExit` 异常。使用 `warn=True` 可以改为警告而不抛异常：

```python
result = c.run("false", warn=True)
print(result.failed)
```

## 隐藏输出

使用 `hide` 参数控制输出：

```python
c.run("ls", hide=True)
c.run("ls", hide="stdout")
c.run("ls", hide="stderr")
c.run("ls", hide="both")
```

## 下一步

- 学习 [Connection 详解](02-connection.md) 了解全部参数和方法
- 了解 [配置体系](03-configuration.md) 管理连接默认值
- 探索 [命令执行](04-command-execution.md) 的高级选项
- 尝试 [多主机并行](05-group-parallel.md) 批量操作

## 相关概念

- [Connection 详解](02-connection.md)
- [配置体系](03-configuration.md)
- [命令执行](04-command-execution.md)
- [pyinvoke 任务基础](../../tooling/pyinvoke/concepts/02-task-basics.md)
