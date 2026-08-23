---
type: Concept
title: 多主机并行
description: Group/SerialGroup/ThreadingGroup 批量操作、GroupResult 结果聚合、异常处理与多主机编排
tags: [fabric, group, parallel, threading, multi-host]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 多主机并行

## Group 概览

`Group` 是一组 `Connection` 对象的集合，继承自 Python `list`。它提供了对组内所有连接批量执行操作的 API。

Group 本身是部分抽象类——`_do()` 方法抛出 `NotImplementedError`，必须使用具体子类：

- `SerialGroup`：串行逐个执行
- `ThreadingGroup`：多线程并发执行

```python
from fabric import SerialGroup, ThreadingGroup

# 从主机字符串创建
group = SerialGroup("web1", "web2", "web3", user="deploy")

# 从已有 Connection 创建
from fabric import Connection
group = Group.from_connections([
    Connection("web1"),
    Connection("web2"),
])
```

## 创建 Group

### 从主机字符串创建

```python
group = SerialGroup("web1.example.com", "web2.example.com", user="deploy")
```

每个位置参数作为 Connection 的第一个位置参数（host），支持 `user@host:port` 简写。所有关键字参数转发给每个 Connection 构造函数。

### from_connections()

```python
connections = [
    Connection("web1", user="admin"),
    Connection("web2", user="deploy", port=2222),
]
group = ThreadingGroup.from_connections(connections)
```

### 上下文管理器

Group 支持上下文管理器，退出时自动关闭所有连接：

```python
with SerialGroup("web1", "web2") as group:
    group.run("uptime")
```

## 可用操作

Group 提供以下批量方法，签名与 Connection 对应方法一致：

| 方法 | 说明 | 返回值类型 |
|------|------|-----------|
| `run(*args, **kwargs)` | 批量执行远程命令 | `GroupResult`（值为 `runners.Result`） |
| `sudo(*args, **kwargs)` | 批量执行 sudo 命令 | `GroupResult` |
| `put(*args, **kwargs)` | 批量上传文件 | `GroupResult`（值为 `transfer.Result`） |
| `get(*args, **kwargs)` | 批量下载文件 | `GroupResult`（值为 `transfer.Result`） |
| `close()` | 关闭所有连接 | None |

### get() 的特殊行为

Group 的 `get()` 方法默认将 `local` 参数设为 `"{host}/"`，即下载到以主机名命名的子目录中：

```python
group = SerialGroup("web1", "web2")
group.get("/var/log/syslog")
# 下载到:
# ./web1/syslog
# ./web2/syslog
```

要覆盖此行为，显式指定 `local` 参数：

```python
group.get("/var/log/syslog", "/tmp/{host}-syslog")
```

> **注意**：Group.get() 不支持 file-like 对象作为 local 参数。

## SerialGroup — 串行执行

`SerialGroup._do()` 简单遍历连接列表，逐个调用方法：

```python
from fabric import SerialGroup

group = SerialGroup("web1", "web2", "web3", user="deploy")
results = group.run("uptime")

for cxn, result in results.items():
    print(f"{cxn.host}: {result.stdout.strip()}")
```

执行顺序与主机列表顺序一致。某台主机的异常被捕获并存入结果，但不会中断后续主机的执行。

## ThreadingGroup — 并行执行

`ThreadingGroup._do()` 为每个 Connection 创建一个 `ExceptionHandlingThread`，通过 `Queue` 收集结果：

```python
from fabric import ThreadingGroup

group = ThreadingGroup("web1", "web2", "web3", user="deploy")
results = group.run("uptime")
```

执行完成后（所有线程 join），从队列收集成功结果，从线程的 `exception()` 方法收集异常。

## GroupResult — 结果聚合

`GroupResult` 继承 `dict`，键是 `Connection` 对象，值是方法返回值或异常对象。

### 基本访问

```python
results = group.run("hostname")

for cxn, result in results.items():
    print(f"{cxn.host}: {result.stdout.strip()}")
```

### succeeded 和 failed

```python
results = group.run("false", warn=True)

print("成功:", results.succeeded)
# {<Connection host='web1'>: <Result ...>}

print("失败:", results.failed)
# {<Connection host='web2'>: <UnexpectedExit ...>}
```

`succeeded` 和 `failed` 是 property，内部通过 `_bifurcate()` 方法惰性分类：值为 `BaseException` 实例的归入 failed，其余归入 succeeded。

### 成功场景

当所有主机都成功时，方法直接返回 `GroupResult`：

```python
results = group.run("true")
assert len(results.succeeded) == 3
assert len(results.failed) == 0
```

## GroupException — 部分失败处理

当任意一台主机抛出异常时，Group 方法抛出 `GroupException`，其 `.result` 属性包含完整的 `GroupResult`（包括成功和失败的条目）：

```python
from fabric import GroupException
from invoke.exceptions import UnexpectedExit

group = SerialGroup("web1", "web2", "notahost")

try:
    group.run("hostname")
except GroupException as e:
    results = e.result

    # 检查成功的主机
    for cxn, result in results.succeeded.items():
        print(f"OK: {cxn.host} -> {result.stdout.strip()}")

    # 检查失败的主机
    for cxn, error in results.failed.items():
        print(f"FAIL: {cxn.host} -> {type(error).__name__}: {error}")
```

异常类型可能包括：
- `UnexpectedExit`：命令退出码非零
- `socket.gaierror`：DNS 解析失败
- `paramiko.ssh_exception.SSHException`：SSH 协议错误
- `OSError`：网络连接问题
- `ValueError`：参数错误

## 典型模式

### 模式一：全部成功或全部失败

```python
try:
    group.run("systemctl restart myapp")
    print("所有主机重启成功")
except GroupException as e:
    print(f"部分主机失败: {list(e.result.failed.keys())}")
```

### 模式二：容忍部分失败

```python
try:
    results = group.run("apt-get upgrade -y", warn=True)
except GroupException as e:
    results = e.result

for cxn, result in results.succeeded.items():
    print(f"{cxn.host}: 升级成功")
```

### 模式三：条件执行

```python
results = group.run("cat /etc/os-release", hide=True)
for cxn, result in results.succeeded.items():
    if "Ubuntu" in result.stdout:
        cxn.sudo("apt-get update")
```

### 模式四：文件分发

```python
group = ThreadingGroup("web1", "web2", "web3")
group.put("app.tar.gz", "/tmp/app.tar.gz")
group.run("tar xzf /tmp/app.tar.gz -C /opt/app/")
group.sudo("systemctl restart myapp")
```

## 与 Executor 的关系

Group 是编程式 API，直接在 Python 中使用。而 `Executor` 配合 `@task(hosts=[...])` 用于 CLI 场景（`fab -H host1,host2 taskname`）。Executor 内部通过 `expand_calls()` 为每个主机创建独立的 `ConnectionCall`，等价于在循环中执行任务。

详见 [高级模式](08-advanced-patterns.md)。

## 注意事项

1. **无去重**：如果传入相同主机的多个 Connection，会创建重复连接并执行多次
2. **ThreadingGroup 无超时配置**：`thread.join()` 没有超时参数，慢主机会阻塞整体
3. **结果字典的键是 Connection 对象**：不是主机名字符串，需要通过 `cxn.host` 访问
4. **异常不中断执行**：单台主机失败不影响其他主机（无论 Serial 还是 Threading）
5. **线程安全**：ThreadingGroup 中每个线程使用独立的 Connection，不存在共享状态问题

## 相关概念

- [Connection 详解](02-connection.md)
- [命令执行](04-command-execution.md)
- [高级模式](08-advanced-patterns.md)
- [文件传输](06-file-transfer.md)
