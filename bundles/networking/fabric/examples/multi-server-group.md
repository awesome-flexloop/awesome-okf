---
type: Example
title: 多服务器组并行操作
description: 使用 SerialGroup 和 ThreadingGroup 在多台服务器上批量执行命令、处理部分失败、聚合结果
tags: [fabric, example, group, parallel, threading]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 多服务器组并行操作

## 场景

管理一组 Web 服务器，需要批量执行命令、上传文件，并优雅处理部分主机失败的情况。

## 基础批量执行

```python
from fabric import SerialGroup

group = SerialGroup(
    "web1.example.com",
    "web2.example.com",
    "web3.example.com",
    user="deploy",
    connect_kwargs={"key_filename": "/home/user/.ssh/id_ed25519"},
)

results = group.run("uptime", hide=True)

for cxn, result in results.items():
    print(f"{cxn.host}: {result.stdout.strip()}")
```

输出：

```
web1.example.com: 10:30:01 up 30 days,  3:14,  1 user,  load average: 0.10, 0.15, 0.20
web2.example.com: 10:30:01 up 15 days,  5:22,  2 users, load average: 0.30, 0.25, 0.18
web3.example.com: 10:30:01 up 45 days,  8:01,  1 user,  load average: 0.05, 0.08, 0.12
```

## 并行执行

```python
from fabric import ThreadingGroup

group = ThreadingGroup("web1", "web2", "web3", user="deploy")

results = group.run("apt-get update && apt-get upgrade -y", hide=True)
```

`ThreadingGroup` 为每个连接创建独立线程，命令在所有主机上并发执行。总耗时取决于最慢的主机。

## 处理部分失败

```python
from fabric import ThreadingGroup, GroupException

group = ThreadingGroup("web1", "web2", "notahost", user="deploy")

try:
    results = group.run("systemctl restart myapp")
except GroupException as e:
    results = e.result

    print("=== 成功 ===")
    for cxn, result in results.succeeded.items():
        print(f"  {cxn.host}")

    print("=== 失败 ===")
    for cxn, error in results.failed.items():
        print(f"  {cxn.host}: {type(error).__name__}")
        if hasattr(error, "result"):
            print(f"    退出码: {error.result.exited}")
            print(f"    stderr: {error.result.stderr.strip()}")
```

输出示例：

```
=== 成功 ===
  web1
  web2
=== 失败 ===
  notahost: gaierror
```

## 带 warn 的容错执行

```python
from fabric import ThreadingGroup, GroupException

group = ThreadingGroup("web1", "web2", "web3", user="deploy")

try:
    results = group.run("test -f /etc/myapp/config.yml", warn=True, hide=True)
except GroupException as e:
    results = e.result

for cxn, result in results.items():
    if result.ok:
        print(f"{cxn.host}: 配置文件存在")
    else:
        print(f"{cxn.host}: 配置文件缺失，正在创建...")
        cxn.sudo("mkdir -p /etc/myapp")
        cxn.put("default-config.yml", "/etc/myapp/config.yml")
```

## 批量文件上传

```python
from fabric import ThreadingGroup

group = ThreadingGroup("web1", "web2", "web3", user="deploy")

group.put("dist/app.tar.gz", "/tmp/app.tar.gz")

group.run("tar xzf /tmp/app.tar.gz -C /opt/app/", hide=True)
group.sudo("systemctl restart myapp")
```

## 批量文件下载

Group 的 `get()` 默认将文件保存到 `{host}/` 子目录：

```python
from fabric import SerialGroup

group = SerialGroup("web1", "web2", "web3", user="deploy")

group.get("/var/log/myapp/error.log")
```

目录结构：

```
./web1/error.log
./web2/error.log
./web3/error.log
```

自定义路径：

```python
group.get(
    "/var/log/myapp/error.log",
    "/tmp/logs/{host}-error.log",
)
```

## 混合主机参数

```python
from fabric import ThreadingGroup, Connection

connections = [
    Connection("web1.example.com", user="deploy"),
    Connection("web2.example.com", user="admin", port=2222),
    Connection(
        "db.example.com",
        user="dbadmin",
        connect_kwargs={"key_filename": "/home/user/.ssh/db_key"},
    ),
]

group = ThreadingGroup.from_connections(connections)
group.run("hostname", hide=True)
```

## 完整运维示例

```python
from fabric import ThreadingGroup, GroupException
import argparse

def rolling_restart(hosts, user="deploy"):
    group = ThreadingGroup(*hosts, user=user)

    print("1. 检查所有主机健康状态...")
    try:
        results = group.run("systemctl is-active myapp", hide=True)
    except GroupException as e:
        results = e.result
        for cxn, error in results.failed.items():
            print(f"  警告: {cxn.host} 服务未运行: {error}")

    print("2. 上传新版本...")
    group.put("dist/app.tar.gz", "/tmp/app.tar.gz")

    print("3. 逐台部署（并行但每台内部串行）...")
    for cxn in group:
        print(f"  部署到 {cxn.host}...")
        try:
            cxn.sudo("systemctl stop myapp")
            cxn.run("tar xzf /tmp/app.tar.gz -C /opt/app/")
            cxn.sudo("systemctl start myapp")
            result = cxn.run(
                "curl -sf http://localhost:8000/health",
                warn=True, hide=True,
            )
            if result.ok:
                print(f"  {cxn.host}: 部署成功")
            else:
                print(f"  {cxn.host}: 健康检查失败，回滚")
                cxn.run("git checkout -f HEAD~1")
                cxn.sudo("systemctl start myapp")
        except Exception as e:
            print(f"  {cxn.host}: 部署异常: {e}")

    print("4. 清理临时文件...")
    group.run("rm -f /tmp/app.tar.gz", hide=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hosts", required=True, help="逗号分隔的主机列表")
    args = parser.parse_args()
    hosts = args.hosts.split(",")
    rolling_restart(hosts)
```

## 使用上下文管理器

```python
from fabric import ThreadingGroup

with ThreadingGroup("web1", "web2", user="deploy") as group:
    group.run("uptime")
    group.run("df -h /")
```

退出 with 块时自动调用 `group.close()` 关闭所有连接。

## 关键 API 说明

| API | 说明 |
|-----|------|
| `SerialGroup(*hosts, **kwargs)` | 串行执行组 |
| `ThreadingGroup(*hosts, **kwargs)` | 并行执行组 |
| `Group.from_connections(connections)` | 从 Connection 列表创建组 |
| `group.run/sudo/put/get(...)` | 批量操作 |
| `GroupResult` | dict 子类，键为 Connection |
| `result.succeeded` | 成功条目的子字典 |
| `result.failed` | 失败条目的子字典 |
| `GroupException.result` | 异常中包装的 GroupResult |
| `group.close()` | 关闭所有连接 |

## 相关示例

- [基础部署脚本](basic-deploy.md)
- [文件上传下载](file-upload-download.md)
