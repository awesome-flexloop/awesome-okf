---
type: Example
title: "从 docker-py 迁移到 podman-py"
description: "将现有使用 Docker SDK for Python 的代码迁移到 podman-py 的分步指南、常见差异与注意事项。"
tags: [podman-py, docker-py, migration, compatibility, porting]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:45:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README.md 项目概览与快速入门
  - id: client
    resource: /references/client-source.md
    title: client.py PodmanClient 核心客户端
---

# 从 docker-py 迁移到 podman-py

podman-py 设计为与 Docker SDK for Python（docker-py）高度 API 兼容，大多数场景下只需修改导入语句即可完成迁移。本示例覆盖常见迁移场景与注意事项。

## 第一步：安装与导入替换

### 卸载 docker-py，安装 podman-py

```bash
pip uninstall docker
pip install podman
```

### 导入语句修改

**迁移前（docker-py）：**

```python
import docker
from docker import DockerClient
from docker.types import Mount, LogConfig
```

**迁移后（podman-py）：**

最简单的方式是直接别名导入，保持代码其他部分不变：

```python
import podman as docker
from podman import DockerClient  # 别名 DockerClient = PodmanClient
```

或者使用 PodmanClient 原名（推荐用于新代码）：

```python
from podman import PodmanClient
```

## 第二步：客户端初始化

### 自动从环境变量连接（最常见）

**迁移前：**

```python
# docker-py
client = docker.from_env()
```

**迁移后：**

```python
# podman-py — API 完全一致
import podman as docker
client = docker.from_env()

# 或使用原名
from podman import from_env
client = from_env()
```

环境变量自动兼容：
- `DOCKER_HOST` → `CONTAINER_HOST`（两个都识别，CONTAINER_HOST 优先）
- `DOCKER_TLS_VERIFY` → `CONTAINER_TLS_VERIFY`
- `DOCKER_CERT_PATH` → `CONTAINER_CERT_PATH`

### 指定 base_url 连接

**迁移前：**

```python
# docker-py
client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
```

**迁移后：**

```python
# podman-py — 注意 rootless Podman 路径不同
import podman as docker

# rootful Podman（类似 Docker 路径）
client = docker.DockerClient(base_url="unix:///run/podman/podman.sock")

# rootless Podman（推荐，普通用户）
client = docker.DockerClient(base_url="unix:///run/user/$UID/podman/podman.sock")

# 使用 http+unix scheme（推荐显式写法）
client = docker.DockerClient(
    base_url="http+unix:///run/user/1000/podman/podman.sock"
)
```

**关键差异**：Docker 默认使用 `unix:///var/run/docker.sock`，Podman 区分：
- rootful：`/run/podman/podman.sock`
- rootless：`/run/user/<UID>/podman/podman.sock`

如果不显式指定 base_url，podman-py 会自动：
1. 检查 `PodmanMachine` 活跃连接（macOS/Windows 上的 Podman Machine）
2. 回退到本地 rootless socket 路径

### SSH 远程连接

**迁移前：**

```python
# docker-py
client = docker.DockerClient(base_url="ssh://user@host")
```

**迁移后：**

```python
# podman-py — SSH 支持更完善，默认使用系统 SSH 客户端
client = docker.DockerClient(
    base_url="ssh://core@192.168.1.100/run/user/1000/podman/podman.sock",
    identity="~/.ssh/id_ed25519",
    use_ssh_client=True  # 默认值，使用系统 ssh（支持 ~/.ssh/config）
)
```

## 第三步：容器操作（API 高度兼容）

以下操作 API 签名完全兼容，可以直接使用：

```python
import podman as docker

client = docker.from_env()

# 运行容器
container = client.containers.run(
    "nginx:alpine",
    name="my-nginx",
    ports={"80/tcp": 8080},
    detach=True,
    environment={"NGINX_HOST": "example.com"},
)

# 列出容器
containers = client.containers.list(all=True)
for c in containers:
    print(f"{c.short_id}  {c.name}  {c.status}")

# 获取容器
c = client.containers.get("my-nginx")

# 停止/启动/重启
c.stop()
c.start()
c.restart()

# 查看日志
print(c.logs(tail=20).decode("utf-8"))

# 在容器内执行命令
exit_code, output = c.exec_run("nginx -v")
print(output.decode("utf-8"))

# 删除容器
c.remove(force=True)
```

## 第四步：镜像操作（API 高度兼容）

```python
import podman as docker

client = docker.from_env()

# 拉取镜像
image = client.images.pull("python:3.12-slim")

# 列出镜像
for img in client.images.list():
    print(img.tags)

# 构建镜像
image, logs = client.images.build(
    path=".",
    tag="myapp:latest",
    buildargs={"VERSION": "1.0.0"},
)

# 推送镜像
client.images.push(
    "myapp:latest",
    auth_config={"username": "user", "password": "pass"}
)

# 删除镜像
client.images.remove("myapp:latest", force=True)
```

**pull 进度条**：podman-py 额外支持 `progress_bar=True`（需安装 rich）：

```python
# podman-py 特有：带进度条拉取
client.images.pull("alpine:latest", progress_bar=True)
```

## 第五步：网络与卷操作

```python
# 创建网络
network = client.networks.create("my-network", driver="bridge")

# 列出网络
for net in client.networks.list():
    print(net.name)

# 创建卷
volume = client.volumes.create("my-volume")

# 列出卷
for vol in client.volumes.list():
    print(vol.name)
```

## 常见差异与注意事项

### 1. Swarm 不支持

Docker Swarm 模式相关 API 在 Podman 中不存在，会抛出 `NotImplementedError`：

```python
# ❌ 这些在 podman-py 中不可用
client.swarm.init()
client.services.list()
client.configs.list()
client.nodes.list()
```

**替代方案**：Podman 使用 Pod 概念管理多容器组，使用 `client.pods` 替代：

```python
# ✅ Podman 原生方式：使用 Pod
pod = client.pods.create("my-pod")
```

### 2. list() 的 sparse 默认行为

docker-py 的 `containers.list()` 默认返回完整属性；podman-py 的 libpod 模式默认 `sparse=True`（性能优化），需要 `reload()` 获取完整属性：

```python
# 如果依赖 attrs 中的详细字段，显式 reload
containers = client.containers.list()
for c in containers:
    c.reload()  # 获取完整 attrs
    print(c.status)

# 或使用 Docker 兼容模式
containers = client.containers.list(compatible=True)
```

### 3. 默认 Socket 路径差异

| 环境 | Docker 默认 | Podman rootful | Podman rootless |
|------|------------|---------------|----------------|
| Linux | `/var/run/docker.sock` | `/run/podman/podman.sock` | `/run/user/$UID/podman/podman.sock` |

使用 `from_env()` 自动检测可避免此问题。

### 4. Containerfile vs Dockerfile

构建时 Podman 默认查找 `Containerfile`，但也兼容 `Dockerfile`：

```python
# 如果使用 Dockerfile 文件名，显式指定
client.images.build(
    path=".",
    dockerfile="Dockerfile",  # 显式指定，兼容两种命名
    tag="myapp:latest",
)
```

### 5. 不支持的 docker.types 中的某些类型

Podman 不使用 Docker 专有类型，可以使用普通字典替代：

```python
# docker-py
from docker.types import Mount, LogConfig

# podman-py — 使用字典或直接参数
client.containers.run(
    "alpine",
    volumes={"/host/path": {"bind": "/container/path", "mode": "rw"}},
    # 或者直接使用列表格式
    # volumes=["/host/path:/container/path:rw"],
)
```

## 完整迁移示例对比

**迁移前（docker-py 代码）：**

```python
import docker

client = docker.from_env()

client.images.pull("python:3.12-slim")

container = client.containers.run(
    "python:3.12-slim",
    command=["python", "-c", "print('Hello Docker')"],
    name="hello-docker",
    remove=True,
)
print(container.decode("utf-8"))
```

**迁移后（podman-py 代码）：**

只需修改第一行导入，其余代码不变：

```python
import podman as docker  # 唯一修改：别名导入

client = docker.from_env()

client.images.pull("python:3.12-slim")

container = client.containers.run(
    "python:3.12-slim",
    command=["python", "-c", "print('Hello Podman')"],
    name="hello-podman",
    remove=True,
)
print(container.decode("utf-8"))
```

## 验证迁移结果

运行以下代码验证连接和基本功能：

```python
import podman as docker

client = docker.from_env()

# 测试连接
print("Podman 版本:", client.version()["Version"])

# 测试容器列表
print("运行中容器:", len(client.containers.list()))

# 测试镜像列表
print("本地镜像:", len(client.images.list()))

# 测试 ping
print("服务可达:", client.ping())

client.close()
print("迁移验证通过！")
```

## 相关概念

- [/concepts/00-introduction.md](/concepts/00-introduction.md)
- [/concepts/01-connection.md](/concepts/01-connection.md)
- [/examples/02-container-ops.md](/examples/02-container-ops.md)
