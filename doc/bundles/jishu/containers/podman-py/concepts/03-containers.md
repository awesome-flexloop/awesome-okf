---
type: Concept
title: "容器生命周期操作"
description: "容器的创建、启动、停止、删除、列表查询、日志获取与状态管理完整生命周期操作。"
tags: [podman-py, containers, lifecycle, create, start, stop, remove, run, logs]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:45:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: client
    resource: /references/client-source.md
    title: client.py PodmanClient 核心客户端
  - id: api
    resource: /references/api-source.md
    title: api/ HTTP 传输层实现
---

# 容器生命周期操作

容器是 Podman 的核心资源，podman-py 通过 `ContainersManager` 和 `Container` 模型类提供容器完整生命周期的管理能力，包括创建、启动、停止、查询、日志、执行命令和删除。

## 容器生命周期状态机

```
         create()              start()
 不存在 ────────► 已创建 ────────────► 运行中
   ▲               │                    │
   │               │ stop()/kill()      │ stop()/kill()
   │               ▼                    ▼
   │            已停止 ◄────────────── 运行中
   │               │
   │ remove()      │ start()
   └───────────────┘
                   │
                   ▼
                 删除
```

## 列出容器（list）

使用 `client.containers.list()` 列出容器，支持多种过滤条件：

```python
from podman import PodmanClient

with PodmanClient.from_env() as client:
    # 默认只列出运行中的容器
    running = client.containers.list()

    # 列出所有容器（包括已停止）
    all_containers = client.containers.list(all=True)

    # 按状态过滤：restarting/running/paused/exited
    exited = client.containers.list(
        all=True,
        filters={"status": "exited"}
    )

    # 按镜像过滤
    alpine_containers = client.containers.list(
        filters={"ancestor": "alpine:latest"}
    )

    # 按标签过滤
    labeled = client.containers.list(
        filters={"label": ["env=production", "app=web"]}
    )

    # 按名称/ID 过滤
    named = client.containers.list(
        filters={"name": "my-container"}
    )

    # 限制返回数量
    latest_5 = client.containers.list(limit=5)
```

**sparse 参数说明**：
- `sparse=True`（libpod 默认）：列表只返回基本信息，需要 `container.reload()` 获取完整属性，性能更好
- `sparse=False`（Docker 兼容模式默认）：每个容器自动 reload，返回完整属性

```python
# 高性能列表（大量容器场景）
containers = client.containers.list(sparse=True)
for c in containers:
    c.reload()  # 需要时再加载完整信息
    print(c.status)
```

## 获取单个容器（get）

按容器名称或 ID 获取 Container 对象：

```python
container = client.containers.get("my-container")
# 或使用短 ID
container = client.containers.get("a1b2c3d4")
```

获取后可以访问容器属性：

```python
print("容器 ID:", container.id)
print("容器名称:", container.name)
print("容器状态:", container.status)
print("镜像:", container.image)
print("创建时间:", container.attrs["Created"])
print("端口映射:", container.ports)
```

## 检查容器存在（exists）

快速检查容器是否存在，不抛出异常：

```python
if client.containers.exists("my-container"):
    print("容器存在")
else:
    print("容器不存在")
```

## 创建容器（create）

`create()` 创建容器但不启动，需要后续调用 `start()`：

```python
container = client.containers.create(
    image="alpine:latest",
    command=["echo", "hello world"],
    name="my-echo",
    detach=True,
)
print("容器已创建:", container.id)
```

### 常用创建参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `image` | `str` | 镜像名称（必填） |
| `command` | `list[str]` / `str` | 启动命令 |
| `name` | `str` | 容器名称 |
| `detach` | `bool` | 后台运行，默认 `True` |
| `ports` | `dict` | 端口映射，如 `{"8080/tcp": 8080}` |
| `volumes` | `dict` / `list` | 卷挂载 |
| `environment` | `dict` / `list` | 环境变量 |
| `working_dir` | `str` | 工作目录 |
| `user` | `str` / `int` | 运行用户 |
| `restart_policy` | `dict` | 重启策略，如 `{"Name": "always"}` |
| `network` | `str` | 网络名称 |
| `labels` | `dict` | 标签 |
| `mem_limit` | `str` / `int` | 内存限制 |
| `cpu_shares` | `int` | CPU 权重 |

## 创建并启动（run）

`run()` 是 `create()` + `start()` 的便捷方法：

```python
# 后台运行容器
container = client.containers.run(
    image="nginx:alpine",
    name="my-nginx",
    ports={"80/tcp": 8080},
    detach=True,
)
print("Nginx 运行在 http://localhost:8080")

# 前台运行并获取输出（类似 docker run --rm）
result = client.containers.run(
    image="alpine:latest",
    command=["echo", "hello"],
    remove=True,  # 退出后自动删除
)
print(result.decode("utf-8"))
```

**注意**：`detach=False`（默认）时，`run()` 等待容器退出并返回输出日志（bytes）。

## 启动容器（start）

启动已创建或已停止的容器：

```python
container = client.containers.get("my-container")
container.start()
```

## 停止容器（stop）

优雅停止运行中的容器：

```python
container.stop()  # 默认 10 秒超时后 SIGKILL
container.stop(timeout=30)  # 自定义超时
```

## 强制终止（kill）

发送 SIGKILL 信号立即终止容器：

```python
container.kill()
container.kill(signal="SIGTERM")  # 发送指定信号
```

## 重启容器（restart）

```python
container.restart()
container.restart(timeout=30)
```

## 暂停与恢复

```python
container.pause()   # 暂停容器（冻结进程）
container.unpause() # 恢复暂停的容器
```

## 删除容器（remove）

```python
# 删除已停止的容器
client.containers.remove("my-container")

# 强制删除运行中的容器（先 kill 再删）
client.containers.remove("my-container", force=True)

# 同时删除关联的卷
client.containers.remove("my-container", v=True)

# 或通过实例方法删除
container = client.containers.get("my-container")
container.remove(force=True)
```

## 清理已停止容器（prune）

批量删除所有已停止的容器：

```python
result = client.containers.prune()
print("删除的容器:", result["ContainersDeleted"])
print("回收空间:", result["SpaceReclaimed"], "bytes")

# 按条件过滤清理
result = client.containers.prune(
    filters={"until": "24h"}  # 只清理 24 小时前停止的容器
)
```

## 获取容器日志（logs）

```python
container = client.containers.get("my-nginx")

# 获取所有日志
logs = container.logs()
print(logs.decode("utf-8"))

# 实时流式日志
for line in container.logs(stream=True, follow=True):
    print(line.decode("utf-8"), end="")

# 只获取最后 N 行
logs = container.logs(tail=100)

# 带时间戳
logs = container.logs(timestamps=True)
```

## 容器内执行命令（exec）

在运行中的容器内执行命令：

```python
container = client.containers.get("my-container")

# 执行命令并获取输出
exit_code, output = container.exec_run("ls -la /")
print("Exit code:", exit_code)
print(output.decode("utf-8"))

# 指定工作目录和用户
exit_code, output = container.exec_run(
    "whoami",
    workdir="/tmp",
    user="nginx"
)
```

## 刷新容器属性（reload）

list() 稀疏模式下获取的容器信息不完整，或容器状态变化后需要刷新：

```python
container = client.containers.get("my-container")
container.start()
container.reload()  # 刷新 attrs，获取最新状态
print(container.status)  # "running"
```

## 容器属性访问

Container 对象的常用属性：

| 属性 | 说明 |
|------|------|
| `.id` | 容器完整 ID（64 字符） |
| `.short_id` | 容器短 ID（12 字符） |
| `.name` | 容器名称 |
| `.status` | 当前状态（running/exited/paused/created） |
| `.image` | 镜像对象 |
| `.labels` | 标签字典 |
| `.ports` | 端口映射 |
| `.attrs` | API 返回的完整属性字典 |
| `.logs()` | 获取日志 |
| `.exec_run(cmd)` | 执行命令 |

## 相关概念

- [/concepts/02-managers.md](02-managers.md)
- [/concepts/04-images.md](04-images.md)
- [/examples/02-container-ops.md](../examples/02-container-ops.md)
