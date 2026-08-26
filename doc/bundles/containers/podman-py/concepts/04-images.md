---
type: Concept
title: "镜像管理与构建"
description: "镜像拉取、推送、列表查询、删除、构建（build）、加载保存、标签管理与 registry 认证。"
tags: [podman-py, images, pull, push, build, Containerfile, registry, tag]
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

# 镜像管理与构建

镜像是容器运行的基础，podman-py 通过 `ImagesManager` 提供镜像的完整生命周期管理：拉取、推送、列表、构建、删除、加载、保存、标签管理和 registry 认证。

## 列出镜像（list）

```python
from podman import PodmanClient

with PodmanClient.from_env() as client:
    # 列出所有本地镜像
    images = client.images.list()
    for img in images:
        print(f"{img.id[:12]}  {', '.join(img.tags)}")

    # 列出所有镜像（包括中间层）
    all_images = client.images.list(all=True)

    # 按仓库名称过滤
    python_images = client.images.list(name="python")

    # 按标签过滤（dangling = 悬空镜像）
    dangling = client.images.list(
        filters={"dangling": True}
    )

    # 按标签键值对过滤
    labeled = client.images.list(
        filters={"label": {"maintainer": "team"}}
    )
```

## 获取单个镜像（get）

按名称、ID 或 digest 获取镜像：

```python
image = client.images.get("alpine:latest")
print("镜像 ID:", image.id)
print("标签:", image.tags)
print("大小:", image.attrs["Size"])
print("创建时间:", image.attrs["Created"])
```

## 检查镜像存在（exists）

```python
if client.images.exists("alpine:latest"):
    print("镜像已存在")
else:
    print("需要拉取")
```

## 拉取镜像（pull）

从 registry 拉取镜像到本地：

```python
# 基本拉取（默认 latest 标签）
image = client.images.pull("alpine")

# 指定标签
image = client.images.pull("python", tag="3.12-slim")

# 拉取所有标签
all_tags = client.images.pull("ubuntu", all_tags=True)

# 带进度条（需要安装 rich：pip install podman[progress_bar]）
image = client.images.pull(
    "nginx:alpine",
    progress_bar=True
)

# 流式获取拉取进度
for line in client.images.pull("alpine", stream=True, decode=True):
    print(line)

# 指定平台（多架构镜像）
image = client.images.pull(
    "alpine:latest",
    platform="linux/arm64"
)

# 自定义拉取策略：always/missing/never/newer
image = client.images.pull(
    "my-registry.local/myimage:v1",
    policy="newer"  # 只在本地镜像更旧时拉取
)
```

### pull 策略选项

| 策略 | 说明 |
|------|------|
| `always` | 总是拉取（默认） |
| `missing` | 本地不存在时才拉取 |
| `never` | 从不拉取，仅使用本地 |
| `newer` | 仅当远程版本更新时拉取 |

## 推送镜像（push）

推送本地镜像到 registry：

```python
# 基本推送
client.images.push("myimage:latest")

# 推送到指定 registry
client.images.push(
    "myimage:latest",
    destination="registry.example.com/myimage:latest"
)

# 带认证
auth_config = {
    "username": "myuser",
    "password": "mypassword"
}
client.images.push(
    "myimage:latest",
    auth_config=auth_config
)

# 流式推送
for line in client.images.push("myimage:latest", stream=True, decode=True):
    print(line)
```

**认证头编码**：`auth_config` 通过 `X-Registry-Auth` HTTP 头传递，内部使用 base64url 编码。

## 构建镜像（build）

从 Containerfile（Dockerfile）构建镜像：

```python
# 从当前目录构建（使用 ./Containerfile）
image, logs = client.images.build(
    path=".",
    tag="myapp:latest",
)

# 从指定 Containerfile 构建
image, logs = client.images.build(
    path="./myproject",
    dockerfile="./docker/Containerfile",
    tag="myapp:v1",
)

# 构建参数
image, logs = client.images.build(
    path=".",
    tag="myapp:latest",
    buildargs={
        "APP_VERSION": "1.0.0",
        "ENV": "production"
    },
)

# 不使用缓存构建
image, logs = client.images.build(
    path=".",
    tag="myapp:latest",
    nocache=True,
)

# 平台指定
image, logs = client.images.build(
    path=".",
    tag="myapp:latest",
    platform="linux/amd64",
)
```

构建返回元组 `(image, build_logs)`：
- `image`：构建成功的 Image 对象
- `build_logs`：构建过程日志列表

**注意**：Podman 使用 `Containerfile` 作为默认构建文件名，但与 Dockerfile 语法完全兼容，可以使用 `dockerfile=` 参数指定 Dockerfile 路径。

## 删除镜像（remove）

```python
# 按名称删除
client.images.remove("alpine:latest")

# 强制删除（即使被容器使用）
client.images.remove("myimage:latest", force=True)

# 通过 Image 对象删除
image = client.images.get("myimage:latest")
result = image.remove(force=True)
for r in result:
    print(r)
```

删除结果返回一个列表，包含 `Deleted`、`Untagged`、`ExitCode` 等条目。

## 清理镜像（prune）

批量清理未使用的镜像：

```python
# 清理悬空镜像（默认）
result = client.images.prune()
print("删除数量:", len(result["ImagesDeleted"]))
print("回收空间:", result["SpaceReclaimed"], "bytes")

# 清理所有未使用的镜像（不只是 dangling）
result = client.images.prune(all=True)

# 按标签过滤清理
result = client.images.prune(
    filters={
        "until": "168h",  # 清理 7 天前的镜像
        "label!": {"protected": "true"}  # 保留标记为 protected 的镜像
    }
)
```

## 搜索镜像（search）

在 registry 中搜索镜像：

```python
# 基础搜索
results = client.images.search("python")
for r in results:
    print(f"{r['name']}: {r['description']} (⭐{r.get('star_count', 0)})")

# 限制结果数量
results = client.images.search("nginx", limit=5)

# 只显示官方镜像
results = client.images.search(
    "ubuntu",
    filters={"is-official": True}
)

# 列出镜像所有标签
results = client.images.search(
    "python",
    listTags=True
)
```

## 加载与保存镜像

### 从 tar 文件加载（load）

```python
# 从文件路径加载
images = list(client.images.load(file_path="./myimage.tar"))
for img in images:
    print("已加载:", img.tags)

# 从 bytes 数据加载
with open("./myimage.tar", "rb") as f:
    data = f.read()
images = list(client.images.load(data=data))
```

### 保存镜像到 tar（save）

```python
# 通过 Image 实例保存
image = client.images.get("alpine:latest")
with open("./alpine.tar", "wb") as f:
    for chunk in image.save():
        f.write(chunk)
```

## 镜像标签（tag）

给本地镜像添加新标签：

```python
image = client.images.get("alpine:latest")

# 添加新标签
image.tag("my-alpine:v1")
image.tag("registry.example.com/my-alpine:latest")

# 重新列出可见新标签
for img in client.images.list(name="my-alpine"):
    print(img.tags)
```

## Registry 登录（login）

登录到容器 registry：

```python
client.login(
    username="myuser",
    password="mypassword",
    registry="registry.example.com",
)

# 登录 Docker Hub
client.login(
    username="dockerhub-user",
    password="dockerhub-pass",
)
```

凭证保存在 Podman 的认证存储中，后续 push/pull 自动使用。

## SCP 跨主机镜像复制

`scp()` 方法在 Podman 主机间安全复制镜像：

```python
# 本地到远程
client.images.scp(
    source="myimage:latest",
    dest="ssh://user@remotehost/run/user/1000/podman/podman.sock"
)
```

## Image 对象常用属性

| 属性/方法 | 说明 |
|----------|------|
| `.id` | 镜像完整 ID（SHA256） |
| `.short_id` | 镜像短 ID |
| `.tags` | 标签列表 |
| `.attrs` | API 返回的完整属性字典 |
| `.tag(repository, tag=None)` | 添加标签 |
| `.save(chunk_size=2MB)` | 保存为 tar 生成器 |
| `.remove(force=False)` | 删除镜像 |

## 相关概念

- [/concepts/02-managers.md](/concepts/02-managers.md)
- [/concepts/03-containers.md](/concepts/03-containers.md)
- [/examples/01-migration.md](/examples/01-migration.md)
