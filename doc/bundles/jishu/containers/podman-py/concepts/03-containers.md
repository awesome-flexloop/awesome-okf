---
type: Concept
title: 03 - 容器生命周期与状态机
description: created/running/paused/exited/dead/restarting 六状态机流转、list sparse/compat 默认差异、get/exists 行为差异、create(** kwargs → /libpod/containers/create)、run(image, command) 四语义（detach/stream/remove/auto_remove/ContainerError）、start/stop/kill/pause/unpause/restart、logs(stream/timestamps/tail/since/until)、exec_run(cmd, stream/detach, stdout/stderr)、remove(force, v, link)、prune(filters) 批量清理、8类异常捕获清单
tags: [Container Life-cycle, State Machine, run(), exec_run, ContainerError, sparse Mode, 异常捕获]
generated:
  by: method_orchestrator/seven-concepts-cmd
  at: 2026-09-07T00:00:00Z
verified:
  by: process:podman-py-grep-20260907
  at: 2026-09-07T00:00:00Z
status: stable
stale_after: 2027-09-07
sources:
  - id: src-cm
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/containers_manager.py
    title: ContainersManager list/get/exists/list filters/sparse 参数
  - id: src-run
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/containers_run.py
    title: RunMixin.run 四分支 + detach+remove 线程清理逻辑
  - id: src-create
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/containers_create.py
    title: CreateMixin.create 30+ kwargs → /libpod/containers/create
  - id: src-container
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/containers.py
    title: Container 资源类 start/stop/kill/pause/unpause/restart/exec_run/logs/wait/remove/reload
  - id: src-containererr
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/errors/exceptions.py
    title: ContainerError 构造（容器对象+exit_status+command+image+stderr）
---

# 03 - 容器生命周期与状态机

容器资源是 podman-py 最常用的管理器（70%+ 的脚本都会 `from podman import PodmanClient; client.containers.xxx`），本章按「六状态机 → 查询 → 创建 → 运行高阶方法 → 状态变更 → 命令执行 + 日志流 → 删除清理 → 异常捕获清单」闭环讲解。

## 1. 六状态机与流转条件

Podman 容器 6 种状态（REST API 返回 `State.Status`），与 libpod 状态定义一一对应：

```
            ┌────────────── create(image, command) / containers.create()
            │
            ▼
     ┌──────────────┐     start()                stop(timeout=10)/kill(SIGTERM)
     │   created    │ ─────────────────────▶  ┌─────────────────┐
     └──────────────┘                          │     running     │
               │                               └─────────────────┘
               │                                          │  pause()
               │                                          ▼
               │ rm() if dead                       ┌──────────┐
               │                                     │  paused  │
               │                                     └──────────┘
               │                                          │  unpause()
               │                                          ▼
               │ restart(timeout)                     running
               ▼                                          │
     ┌──────────────┐◀──────────────────────────────────────┘
     │    exited    │
     └──────────────┘
            │
            │ kill(signal), OOMKilled, daemon restart
            ▼
     ┌──────────────┐
     │     dead     │  ──▶ remove(force=True) 清理残留
     └──────────────┘

     ┌──────────────┐
     │ restarting   │ restart() 过程中瞬态
     └──────────────┘
```

在代码里读状态：`container.status` → 小写字符串（running/exited/paused/created/dead/restarting）；`container.attrs["State"]["OOMKilled", "ExitCode", "StartedAt", "FinishedAt"]` 获取细节。

## 2. 查询三件套：list() / get() / exists()

三查询看似相似，但返回值与异常语义差异极大，是 docker-py 迁移 bug 高频点：

| 方法 | 返回值 | 抛异常场景 | 关键参数 | 典型用例 |
|---|---|---|---|---|
| **`cm.list(**kwargs) → list[Container]`** | 空 list 也不抛 | APIError 仅服务端 5xx | `all=True/False`（默认 False → 只 running）、`filters={status/exited/label/id/name/ancestor/before/since}`、`limit=N`、`sparse`、`ignore_removed=True`、`compatible=True/False` | 页面渲染列表、批量筛选清理 |
| **`cm.get(key, **kwargs) → Container`** | 单个 Container 对象 | **404 → NotFound 子类**、非 4xx/5xx → APIError | `compatible=True/False`（False→libpod/json，True→/v1.40/containers/json Docker 兼容返回） | 已知 name/id 取单对象做后续 start/stop/exec |
| **`cm.exists(key) → bool`** | True/False | **永不抛 404**（exists 端点语义就是 204 exists / 404 not-exists，response.ok 直接转 bool） | 无 | 幂等 "if not exists then create" 业务判断 |

### 2.1 list() 的 sparse 默认值陷阱（与 G2 洞察 #1 薄门面兼容层呼应）

`containers_manager.py L87-L93` 有一段非常容易忽略的默认值分支：

```python
if "sparse" in kwargs:
    sparse = kwargs["sparse"]
else:
    sparse = not compatible  # ⚠️ Libpod 模式默认 sparse=True（精简，快）；Docker 兼容 compatible=True 时 sparse=False（全量）
```

这意味着：
- **默认 docker-py 用户最常用的 `client.containers.list()`** → sparse=True → 每个 Container 的 attrs 只包含基本字段（Id/Name/State 简要），如 `NetworkSettings.IPAddress` 为 None → `container.reload()` 补全
- **迁移过来的 docker-py 用户惊讶 `list[0].attrs["NetworkSettings"]["Networks"]` 全空** → 解决：要么传 `compatible=True` 让默认 sparse=False 与 docker SDK 一致；要么对单个容器调 `container.reload()`（推荐，性能+兼容折中）

示例：

```python
running = client.containers.list(filters={"label": "app=web"})
for c in running:
    # c.attrs["NetworkSettings"] 很可能是精简版
    c.reload()  # ← 补全后才能读 IP 地址
    for net, meta in (c.attrs.get("NetworkSettings") or {}).get("Networks", {}).items():
        print(f"{c.name} net={net} ip={meta.get('IPAddress')}")
```

### 2.2 list() 的 filters 结构（推荐写成 dict，原生 JSON 编码后传给 ?filters=）

```python
# 常见过滤组合：
containers = client.containers.list(
    all=True,           # 包含 exited/paused
    filters={
        "status": "exited",           # 或 restarting/running/paused
        "exited": 1,                  # status=exited 且 ExitCode=1
        "label": ["app=web", "env=prod"],  # label=key 或 label=key=value；列表 AND
        "name": "postgres",           # 模糊匹配（contains）
        "ancestor": "docker.io/library/postgres:16",  # 来源镜像
        "before": "container-old-id", "since": "container-new-id",  # 时间范围
    },
    limit=50,
    ignore_removed=True,  # 并发删除时，对中途 404 的单个容器直接跳过不抛 APIError
)
```

## 3. Create：CreateMixin.create(**) → /libpod/containers/create

CreateMixin（containers_create.py）接收 30+ 关键字参数，构造 multipart form 或 JSON body 传给 libpod create 端点。常用参数：

```python
c = client.containers.create(
    image="docker.io/library/nginx:1.27",
    command=["nginx", "-g", "daemon off;"],
    name="web-frontend",
    # 端口：host_port ⇄ container_port；两种写法等价：
    ports={"80/tcp": 8080, "443/tcp": ("127.0.0.1", 8443)},  # ("host_ip", host_port) 绑定特定网卡
    # 卷挂载：host_path:container_path:mode，或 /named_volume:/data:z
    mounts=[
        {"type": "bind",   "source": "/srv/www", "target": "/usr/share/nginx/html", "read_only": True},
        {"type": "volume", "source": "nginx_logs", "target": "/var/log/nginx"},
    ],
    # 环境变量 / secrets：
    environment={"NGINX_HOST": "example.com", "TZ": "Asia/Shanghai"},
    secrets=[{"secret_name": "tls.crt", "path": "/etc/nginx/certs/tls.crt", "uid": "101", "gid": "101", "mode": 0o400}],
    # 安全：
    user="101:101", read_only=True, tmpfs={"/run": "rw,noexec,size=64m"},
    cap_drop=["ALL"], cap_add=["NET_BIND_SERVICE"], security_opt=["no-new-privileges"],
    # 资源限制（cgroup v2）：
    mem_limit="512m", memswap_limit="512m", cpus="1.5", pids_limit=200,
    # 网络：
    network="backend", network_mode="bridge",
    # 健康检查（Containerfile 有 HEALTHCHECK 可省略）：
    healthcheck={"test": ["CMD", "wget", "-qO-", "http://127.0.0.1/healthz"], "interval": 10_000_000_000, "timeout": 2_000_000_000, "retries": 3},
    # 标签：
    labels={"app": "web", "env": "prod", "managed-by": "podman-py"},
)
print("created id:", c.id, "status:", c.status)  # status = "created"（不是 running）
c.start()  # create→running 需要显式 start
```

> 与 Docker 差异：Podman create 支持 `secrets=`（Podman 本地 Secret 资源）、quadlets 单元字段等扩展；但 Swarm 相关 `endpoint_spec, configs, credentialspec` 无效。

## 4. Run：RunMixin.run(**) → 四返回分支 + 自动清理线程

run() 是 create+start+（等退出+读日志）的**组合糖**，也是 90% 自动化脚本的首选。按 `detach / stream / remove` 组合共有 4 种**完全不同**的返回类型（写注释标明类型，别让 IDE 或 mypy 困惑）：

```python
# ── Case 1：detach=True（长驻容器，最常用）→ Container 对象 ──────────
c: Container = client.containers.run(
    "docker.io/library/redis:7-alpine",
    detach=True,
    name="redis-cache",
    ports={"6379/tcp": ("127.0.0.1", 6379)},
    mem_limit="256m",
    remove=True,  # ← detach=True 时，RunMixin 启动 daemon thread：wait() 退出后 container.remove(v=True)
)
# Redis 正常停止或被 SIGTERM 杀死，容器资源自动清理（等价于 CLI --rm）

# ── Case 2：detach=False / stream=False（一次性命令，等退出返回完整日志）→ Iterator[bytes] ─
log_bytes: Iterator[bytes] = client.containers.run(
    "docker.io/library/alpine:3.20",
    ["sh", "-c", "echo line1; sleep 0.1; echo line2 >&2; exit 0"],
    stdout=True, stderr=True, stream=False,
)
print(b"".join(log_bytes).decode())
# 若 exit != 0 → 抛 ContainerError（见 §8 异常体系）

# ── Case 3：detach=False / stream=True（流式日志，边跑边输出）→ Generator[bytes] ──
for chunk in client.containers.run(
    "docker.io/library/buildpack-deps:curl",
    ["curl", "-sSL", "https://example.com/report.csv"],
    stdout=True, stderr=False, stream=True, remove=True,
):
    f.write(chunk)

# ── Case 4：policy + auto_remove 扩展 ──
# pull policy（RunMixin 透传给 CreateMixin）：missing(default) / always / never / newer
c = client.containers.run(
    "registry.example.com/my/app:v1.2.3",
    policy="always",  # 每次强制重新拉取（CI 场景避免缓存镜像）
    auto_remove=True,  # 由 Podman 服务端在容器退出时删除（不等同于 remove=True 客户端线程）
    platform="linux/amd64",  # 多平台清单镜像：显式指定 os/arch/variant
    auth_config={"username": "ci", "password": "$CI_REG_PWD"},
)
```

### 4.1 remove=True（客户端） vs auto_remove=True（服务端）

| 参数 | 谁执行删除 | 时机 | 适用场景 |
|---|---|---|---|
| `remove=True` | RunMixin 启动的 Python `threading.Thread`（**客户端进程内**） | 容器 exit / removed condition 触发后 | Python 脚本一直活，退出也要负责的短任务 |
| `auto_remove=True` | **Podman daemon / libpod**（服务端） | 容器进程真正退出后立刻做 cleanup | 短 CLI 工具、无人值守、客户端可能崩溃的情况（避免残留容器） |

⚠️ **陷阱**：`remove=True` 时若 Python 进程被杀（SIGKILL、机器断电），线程根本没机会执行 remove → 容器残留；生产脚本用 `auto_remove=True` 双保险。

## 5. 状态变更：start / stop(timeout) / kill(signal) / pause / unpause / restart

都是 Container 类上的方法（Create 后必须先 start 才能用其他）：

```python
c = client.containers.get("redis-cache")

c.start()                                # 转到 running；等价于 CLI podman start
c.stop(timeout=30)                       # SIGTERM → 等 30s → SIGKILL；默认 10s
c.kill(signal="SIGHUP")                  # 直接发信号；默认 SIGKILL；字符串或 int 均可
c.pause()                                # cgroups freezer 冻结 → status=paused
c.unpause()                              # 解冻
c.restart(timeout=30)                    # stop + start；瞬态 restarting 期间 status=restarting
c.wait(condition="exited", timeout=300)  # 阻塞直到 condition；返回 {"Error":None, "StatusCode":0}
```

## 6. 日志流：logs() + 命令执行：exec_run()

### 6.1 logs()

```python
# 一次性拿最近 50 行 + 时间戳 + 仅 stdout：
lines = b"".join(
    c.logs(timestamps=True, tail=50, stdout=True, stderr=False, stream=False)
).decode().splitlines()

# 流式 follow（等价于 podman logs -f；容器未退出时生成器不结束）：
for chunk in c.logs(stream=True, follow=True, since="2026-09-01T00:00:00Z", until="2026-09-07T00:00:00Z"):
    sys.stdout.buffer.write(chunk)
```

### 6.2 exec_run(cmd, …)

在运行中容器里执行命令（**不等于 containers.run**，容器不会因 exec 的命令 exit 而改变自己的 status）：

```python
exit_code, output = c.exec_run(
    ["psql", "-U", "app", "-d", "appdb", "-c", "SELECT count(*) FROM users;"],
    stdout=True, stderr=True, stdin=False,
    stream=False,                # False → output bytes；True → output Generator[bytes]
    detach=False,                # True → 立即返回 exit_code=None，命令后台执行
    workdir="/app", user="1000", environment={"PGPASSWORD": "s3cr3t"},
    tty=False, demux=False,
)
if exit_code == 0:
    print(output.decode().strip())
else:
    print("exec failed:", exit_code, output.decode()[:200])
```

> 注意：`exec_run` 的 stdout+stderr 混合输出（默认 demux=False）；要分离两者传 `demux=True`，返回 (exit_code, (stdout_bytes, stderr_bytes))。

## 7. 删除清理：remove() / prune()

```python
# 单容器：
c.remove(force=False, v=False, link=False)   # force=True → 先 SIGKILL 再删除（running 也能删）
                                            # v=True → 删除时同步删除与容器关联的匿名卷（危险，默认 False）

# 批量 prune（等价于 podman container prune）：
report = client.containers.prune(filters={"label": "env=dev"})
# report = {"ContainersDeleted": list[str|None], "SpaceReclaimed": int bytes}
print("回收字节数:", report["SpaceReclaimed"])
```

prune filters 支持 `until=<unix_ts>`、`label=/label!=` 等；谨慎 prune 无 filters → 默认删除所有 exited/dead/created 非 running 容器。

## 8. 容器操作的 8 类异常捕获清单（与 05-advanced 异常继承链配合）

```python
from podman.errors import (
    APIError,          # 通用 HTTP 4xx/5xx；含 response.status_code / .explanation 详情
    NotFound,          # 404 子类：容器/镜像不存在（用 exists() 预判可避免）
    ImageNotFound,     # 404 子类（images.pull/get 失败）
    ContainerError,    # run(detach=False) + exit != 0；含 .container/.exit_status/.command/.image/.stderr
    BuildError,        # images.build 时 buildah 返回错误；含 .msg + .build_log
    InvalidArgument,   # 参数非法（如 ports 结构写错）
    PodmanError,       # 所有 Podman 特定异常的基类（DockerException 兼容）
)
import requests.exceptions as req_err  # 底层网络异常：Timeout/ConnectionError

try:
    log_out = client.containers.run(
        "registry.internal/my-job:v${CI_COMMIT_SHORT_SHA}",
        ["python", "-m", "job.batch_sync"],
        mem_limit="2g", cpus="2",
        auto_remove=True, stream=False,
        network="production",
    )
except (ContainerError, BuildError) as e:
    logger.error("业务失败 exit=%s stderr=%s", getattr(e, "exit_status", "?"), getattr(e, "stderr", ""))
except (NotFound, ImageNotFound) as e:
    logger.warning("资源缺失自动修复触发: %s", e); trigger_rebuild_pipeline()
except APIError as e:
    logger.error("Podman API %s %s", e.status_code, e.explanation)
except req_err.Timeout:
    logger.warning("网络超时重试；建议加大 timeout 参数")
except req_err.ConnectionError:
    logger.critical("socket 不可达；切换 base_url 或报警")
```
