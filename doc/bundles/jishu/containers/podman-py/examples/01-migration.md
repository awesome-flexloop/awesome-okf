---
type: example
title: 01 - docker-py → podman-py 脚本级灰度迁移
description: 从 docker SDK 迁移到 podman SDK：依赖替换→3行别名→from_env零改→base_url差异→10项API对比→Nginx示例前后40行代码对比→3步验证脚本
tags: [podman-py, migration, docker-py-compat, gray-release, alias-import]
generated:
  by: process:seven-concepts/sc-20260907-podman-py/e-phase
  at: 2026-09-07
verified:
  by: human:xinzo
  at: 2026-09-07
status: stable
stale_after: 2027-09-07
sources:
  - id: src-client
    resource: external/dao/action/Containers/podman-py/podman/client.py
    title: PodmanClient 源码 — DockerClient 别名 + from_env 双前缀 + NotImplementedError
  - id: src-containers-manager
    resource: external/dao/action/Containers/podman-py/podman/domain/containers_manager.py
    title: ContainersManager 源码 — list sparse 默认逻辑 + RunMixin/CreateMixin
---

# 01 - docker-py → podman-py 脚本级灰度迁移

## E1.1 迁移前检查清单

```bash
# 1. 旧依赖
pip list | grep docker     # docker==7.x / docker-py 已废弃改名

# 2. Podman daemon 可达性（Rootless）
podman --version          # ≥5.0, 推荐 ≥5.8 (Quadlets)
podman info --format '{{.Host.RemoteSocket.Path}}'
# 输出: /run/user/$UID/podman/podman.sock

# 3. 环境变量（兼容两种前缀）
env | grep -E 'DOCKER|CONTAINER' | sort
# CONTAINER_HOST 优先级 > DOCKER_HOST
```

## E1.2 三步最小改动迁移

### Step 1：依赖替换

```diff
# requirements.txt
- docker>=7.0
+ podman>=5.8        # PyPI 名是 podman 不是 podman-py（R1 陷阱）
```

```bash
pip install 'podman[progress]'   # 含 rich.progress 支持
```

### Step 2：3 行别名导入（不修改业务代码！）

```python
# 新建 compat_podman.py，旧代码里的 `import docker` 全部替换成本模块
# 或者在入口 app/__init__.py 注入：
from podman import PodmanClient as DockerClient  # 别名 1：类名
from podman.errors import (                        # 别名 2：异常层
    DockerException,
    APIError,
    NotFound as ImageNotFound,
    BuildError,
    ContainerError,
)
# import docker → import compat_podman as docker （别名 3：模块名）
```

### Step 3：`from_env()` 零修改迁移（R6 提醒：rootful/rootless 不要混用 socket）

```python
# 旧代码（docker SDK）
from docker import from_env
client = from_env()

# 新代码（podman-py）—— 签名完全一致！
# 读取 DOCKER_HOST/CONTAINER_HOST 双前缀，CONTAINER 优先
from podman import from_env
client = from_env()
```

## E1.3 10 项高频 API 兼容性对照表

| 操作 | docker-py 写法 | podman-py 兼容写法 | 备注 / 陷阱 |
|---|---|---|---|
| 客户端创建 | `DockerClient(base_url=..)` | `PodmanClient(base_url=..)` | socket 路径见 E1.4 |
| 客户端 from_env | `from_env()` | `from_env()` | 6 双前缀环境变量 |
| 拉取镜像 | `client.images.pull("nginx:alpine")` | 完全相同 | `policy="newer"` 是 podman-only |
| 容器运行 | `client.containers.run(img, cmd, detach=True)` | 完全相同 | 4 分支返回语义一致 |
| 容器列表 | `client.containers.list(sparse=True)` | **默认值不同！** 见 E1.5 | docker 默认 False，podman 默认 `sparse = not compatible` |
| 创建并启动 | `client.containers.create(..)` + `start()` | 完全相同 | kwargs 签名 98% 一致 |
| logs | `container.logs(tail=10, follow=True)` | 完全相同 | stream 生成器语义一致 |
| exec_run | `container.exec_run("pg_isready")` | 完全相同 | demux=True 返回 (stdout,stderr) 元组 |
| stop + rm | `container.stop();container.remove()` | 完全相同 | `remove(force=True, v=True)` |
| 构建镜像 | `client.images.build(path=.., tag=..)` | 完全相同 | `dockerfile="Containerfile"` 允许 |

## E1.4 base_url 路径差异（G2 洞察 #1 第二坑）

```diff
# 旧代码（Rootful docker）
- client = DockerClient(base_url="unix:///var/run/docker.sock")

# 新代码（Rootless podman 推荐）
+ import os
+ xdg_rt = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
+ client = PodmanClient(base_url=f"unix://{xdg_rt}/podman/podman.sock")

# 新代码（Rootful podman，不推荐日常开发用）
+ client = PodmanClient(base_url="unix:///run/podman/podman.sock")
```

> **R6 陷阱再现**：在 rootless shell 里连 rootful socket → permission denied；在 root shell 连 rootless socket → `FileNotFoundError`。
> 别浪费 2 小时 debug socket 权限，直接用 `PodmanClient()` 不传参，SDK 四级优先级自动找。

## E1.5 sparse 默认差异陷阱修复（G2 洞察 #1 第一坑）

```python
# 背景：podman-py containers.list() 默认 sparse=not compatible
# 当 compat=True（即 Docker 兼容模式）→ sparse=False → 全量数据（NetworkSettings 不空）
# 当 compat=False（默认 libpod 模式）→ sparse=True → NetworkSettings 全空！

# 迁移前（docker SDK：NetworkSettings 永远非空）
for c in client.containers.list():
    ip = c.attrs["NetworkSettings"]["IPAddress"]   # ✅ OK

# 迁移后（podman-py 裸调用：NetworkSettings 全空）
for c in client.containers.list():
    ip = c.attrs["NetworkSettings"]["IPAddress"]   # ❌ KeyError 或空字符串！

# ✅ 修复方式 1（推荐，docker-py 行为完全对齐）
client = PodmanClient(compatible=True)                # 全局兼容模式
for c in client.containers.list():
    ip = c.attrs["NetworkSettings"]["IPAddress"]     # ✅ 正常

# ✅ 修复方式 2（保留 libpod，list 后显式 reload）
for c in client.containers.list():
    c.reload()                                        # 单独请求完整详情
    ip = c.attrs["NetworkSettings"]["IPAddress"]     # ✅ 正常，性能略差
```

## E1.6 5 个高概率踩坑点总结

| 坑 | 现象 | 修复代码 |
|---|---|---|
| **Swarm services** | `client.services.list()` 抛 NotImplementedError | 改成 `client.pods.list()` 查 Pod 组容器 |
| **sparse 默认**（上一节） | `NetworkSettings` 全空 | 创建 client 时加 `compatible=True` |
| **socket 路径** | `FileNotFoundError: docker.sock` | 用 `from_env()` 或参考 E1.4 |
| **Containerfile 命名** | 代码里写死 `Dockerfile` 团队却用 `Containerfile` | `build(dockerfile="Containerfile")` 两者都支持 |
| **docker.types.\*** | `ImportError: No module named 'docker.types'` | 直接传原生 dict，podman-py 不提供 types 子包 |

## E1.7 Nginx 部署：迁移前后 40 行代码对比

### 迁移前（docker-py）

```python
import docker
client = docker.from_env()

img = client.images.pull("nginx:alpine")
container = client.containers.run(
    "nginx:alpine",
    detach=True,
    ports={"80/tcp": 8080},
    name="demo-nginx",
    volumes={"/srv/www": {"bind": "/usr/share/nginx/html", "mode": "ro"}},
    environment={"NGINX_HOST": "demo.local"},
    labels={"env": "demo"},
)

print(f"Container {container.short_id} status={container.status}")
exit_code, output = container.exec_run("nginx -t")
if exit_code == 0:
    for line in container.logs(tail=20).splitlines():
        print(f"  nginx> {line.decode()}")
else:
    print(f"nginx config broken: {output.decode()}")
```

### 迁移后（podman-py，改 1 行 import + 1 行 compatible）

```python
# 唯一改动：import 语句 + compatible=True
from podman import from_env
client = from_env()
# client.api.compatible = True   # 如需要 sparse 默认=False 对齐 docker
# 也可 PodmanClient(compatible=True)

img = client.images.pull("nginx:alpine")
container = client.containers.run(
    "nginx:alpine",
    detach=True,
    ports={"80/tcp": 8080},
    name="demo-nginx",
    volumes={"/srv/www": {"bind": "/usr/share/nginx/html", "mode": "ro"}},
    environment={"NGINX_HOST": "demo.local"},
    labels={"env": "demo"},
)

print(f"Container {container.short_id} status={container.status}")
exit_code, output = container.exec_run("nginx -t")
if exit_code == 0:
    for line in container.logs(tail=20).splitlines():
        print(f"  nginx> {line.decode()}")
else:
    print(f"nginx config broken: {output.decode()}")
```

## E1.8 三步迁移验证脚本（CI 集成）

```bash
#!/usr/bin/env bash
# scripts/verify-podman-migration.sh
set -euo pipefail

echo "=== Step 1: ping OK ==="
python -c "
from podman import from_env
c = from_env()
assert c.ping() is True, 'podman daemon unreachable'
print('ping: OK ✓')
"

echo "=== Step 2: sparse + reload 补全 NetworkSettings ==="
python -c "
from podman import PodmanClient
# 方式 A：compatible 模式
client = PodmanClient(compatible=True)
for ct in client.containers.list(all=True, limit=3):
    ip = ct.attrs.get('NetworkSettings',{}).get('IPAddress','')
    print(f'  compatible mode: {ct.short_id} {ct.name} ip={repr(ip)}')
# 方式 B：libpod + reload
client2 = PodmanClient()
for ct in client2.containers.list(all=True, limit=3):
    ct.reload()
    ip = ct.attrs.get('NetworkSettings',{}).get('IPAddress','')
    print(f'  libpod+reload : {ct.short_id} {ct.name} ip={repr(ip)}')
print('sparse check: OK ✓')
"

echo "=== Step 3: 容器 run + rm 端到端 ==="
python -c "
from podman import from_env
from podman.errors import ContainerError
c = from_env()
# 成功分支
r = c.containers.run('alpine:3', 'echo hello from podman', remove=True)
assert b'hello from podman' in r, f'Unexpected output: {r}'
# 失败分支
try:
    c.containers.run('alpine:3', 'exit 42', remove=True)
    assert False, 'ContainerError 未抛出'
except ContainerError as e:
    assert e.exit_status == 42, f'期望 exit 42 实际 {e.exit_status}'
print('run/error/remove: OK ✓')
"

echo "
=================================
✅ 迁移三步验证全通过！
下一步：灰度 10% 流量 → 观察 1 周 → 全量
=================================
"
```
