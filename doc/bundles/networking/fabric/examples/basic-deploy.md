---
type: Example
title: 基础部署脚本
description: 使用 fabric Connection 完成远程部署的完整示例——拉取代码、安装依赖、重启服务
tags: [fabric, example, deploy, connection]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 基础部署脚本

## 场景

通过 SSH 连接到远程服务器，执行典型的 Web 应用部署流程：拉取最新代码、安装依赖、收集静态文件、重启服务。

## 方式一：Python 脚本直接使用

```python
from fabric import Connection

def deploy(host, user="deploy", branch="main"):
    with Connection(host, user=user) as c:
        print(f"连接到 {host}...")

        print("拉取最新代码...")
        c.run(f"git fetch origin {branch}")
        c.run(f"git reset --hard origin/{branch}")

        print("安装依赖...")
        c.run("pip install -r requirements.txt")

        print("收集静态文件...")
        c.run("python manage.py collectstatic --noinput")

        print("运行数据库迁移...")
        c.run("python manage.py migrate --noinput")

        print("重启服务...")
        c.sudo("systemctl restart myapp")
        c.sudo("systemctl status myapp --no-pager")

        print(f"部署完成: {host}")

if __name__ == "__main__":
    deploy("web.example.com")
```

## 方式二：fabfile 任务

创建 `fabfile.py`：

```python
from fabric import task

@task
def deploy(c, branch="main"):
    c.run(f"git fetch origin {branch}")
    c.run(f"git reset --hard origin/{branch}")
    c.run("pip install -r requirements.txt")
    c.run("python manage.py collectstatic --noinput")
    c.run("python manage.py migrate --noinput")
    c.sudo("systemctl restart myapp")
    c.run("systemctl is-active myapp")

@task
def status(c):
    c.run("uptime")
    c.run("free -h")
    c.run("df -h /")
    c.sudo("systemctl status myapp --no-pager")

@task
def logs(c, lines=50):
    c.sudo(f"journalctl -u myapp -n {lines} --no-pager")
```

通过 CLI 执行：

```bash
fab -H web.example.com deploy
fab -H web.example.com deploy --branch staging
fab -H web.example.com status
fab -H web.example.com logs --lines 100
```

## 使用密钥认证

```python
from fabric import Connection

c = Connection(
    host="web.example.com",
    user="deploy",
    connect_kwargs={
        "key_filename": "/home/localuser/.ssh/id_ed25519",
    },
    forward_agent=True,
)

with c:
    c.run("git pull")
```

`forward_agent=True` 将本地 SSH agent 转发到远程，使得远程服务器可以使用本地密钥访问 Git 仓库。

## 带错误处理的部署

```python
from fabric import Connection
from invoke.exceptions import UnexpectedExit

def safe_deploy(host):
    with Connection(host) as c:
        try:
            c.run("git fetch origin main")
        except UnexpectedExit:
            print("错误：无法拉取代码，检查网络和仓库状态")
            return False

        result = c.run("python -m pytest", warn=True)
        if result.failed:
            print("测试失败，中止部署")
            return False

        c.sudo("systemctl stop myapp")
        try:
            c.run("pip install -r requirements.txt")
            c.run("python manage.py migrate")
            c.sudo("systemctl start myapp")
        except UnexpectedExit:
            print("部署出错，回滚...")
            c.run("git reset --hard HEAD~1")
            c.sudo("systemctl start myapp")
            return False

        health = c.run("curl -sf http://localhost:8000/health", warn=True)
        if health.ok:
            print("部署成功，健康检查通过")
            return True
        else:
            print("健康检查失败！")
            return False
```

## 带配置的部署

使用 Config 对象设置默认值：

```python
from fabric import Connection, Config

config = Config(overrides={
    "run": {"hide": True, "warn": False},
    "sudo": {"password": "sudo-password"},
    "connect_kwargs": {
        "key_filename": "/home/user/.ssh/deploy_key",
    },
})

c = Connection("web.example.com", user="deploy", config=config)
with c:
    c.run("hostname")
```

## 关键 API 说明

| API | 说明 |
|-----|------|
| `Connection(host, user=...)` | 创建连接对象（不立即连接） |
| `c.run(command)` | 远程执行命令，返回 Result |
| `c.sudo(command)` | 以 sudo 执行命令 |
| `c.local(command)` | 本地执行命令 |
| `c.put(local, remote)` | 上传文件 |
| `c.get(remote, local)` | 下载文件 |
| `c.open()` / `c.close()` | 手动开关连接 |
| `with Connection(...) as c` | 上下文管理器自动关闭 |
| `result.ok` / `result.failed` | 命令是否成功 |
| `warn=True` | 失败时不抛异常 |
| `hide=True` | 隐藏输出 |

## 相关示例

- [多服务器组并行操作](multi-server-group.md)
- [文件上传下载](file-upload-download.md)
- [跳板机隧道](tunnel-bastion.md)
