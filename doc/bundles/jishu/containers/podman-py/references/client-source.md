---
type: reference
title: PodmanClient + APIClient 信源锚点（20 条）
description: PodmanClient __init__ 四级优先级；from_env 6变量双前缀代码表；9 @cached_property 管理器+7直接方法；DockerClient别名+4 NotImplementedError端点；APIClient requests.Session继承图 + supported_schemes 6项 + APIResponse 404→NotFound映射
tags: [podman-py, podmanclient, apiclient, requests-session, dockerclient-alias, notimplementederror, supported-schemes]
generated:
  by: process:seven-concepts/sc-20260907-podman-py/e-phase
  at: 2026-09-07
verified:
  by: human:xinzo
  at: 2026-09-07
status: stable
stale_after: 2027-09-07
sources:
  - id: src-client-py
    resource: external/dao/action/Containers/podman-py/podman/client.py
    title: PodmanClient 源码 — __init__ 优先级 + from_env + cached_property managers + DockerClient 别名
  - id: src-api-client-py
    resource: external/dao/action/Containers/podman-py/podman/api/client.py
    title: APIClient 源码 — requests.Session 继承 + 6 scheme + APIResponse 404→NotFound 映射
---

# PodmanClient + APIClient 信源锚点（20 条）

## 第一部分：PodmanClient（薄门面层）13 条锚点

### CL-1 类签名与继承链
```python
class PodmanClient(AbstractContextManager):
    """Client for connecting to Podman service."""
    # __enter__ → return self
    # __exit__  → self.close()
```
**不是** APIClient 子类；PodmanClient 持有 `.api: APIClient` 成员（组合优于继承）。

### CL-2 DockerClient 别名（迁移兼容）
```python
# podman/__init__.py 末尾（兼容层）
DockerClient = PodmanClient
DockerException = PodmanError   # 异常别名
```
docker-py 迁移用户 `from docker import DockerClient` → `from podman import DockerClient` 零改。

### CL-3 __init__ 四级连接优先级（L62-L82 精确伪代码）
```python
def __init__(self, *,
             connection: Optional[str] = None,    # 第 1 优先级（最高）
             base_url:   Optional[str] = None,    # 第 2 优先级
             compatible: bool = False,            # sparse 默认值翻转开关
             **kwargs):
    # 第 1 优先级：containers.conf [engine] service_dest= 的命名连接
    if connection is not None:
        uri = resolve_from_containers_conf(connection)
    # 第 2 优先级：显式 base_url= 参数
    elif base_url is not None:
        uri = base_url
    # 第 3 优先级：active_service ∈ containers.conf 且 PodmanConfig.is_machine==True
    elif (active := PodmanConfig().active_service) is not None and active.is_machine:
        uri = f"unix://{active.identity.path}"   # Podman Machine (macOS/Windows)
    # 第 4 优先级（回退，最低）：本地 Rootless socket → 否则 Rootful socket
    else:
        uri = default_local_socket()
    self.api = APIClient(base_url=uri, compatible=compatible, **kwargs)
```
⚠️ 四级优先级与参数名必须一致；不要同时传 `connection=` + `base_url=`（前者被忽略，后者生效，浪费调试时间）。

### CL-4 from_env 6 变量双前缀表（L90-L140）

| 变量名（docker 前缀，仅当 CONTAINER 同名变量不存在时生效） | 变量名（container 前缀，优先） | 对应 client 参数 |
|---|---|---|
| `DOCKER_HOST` | `CONTAINER_HOST` | base_url / socket 地址 |
| `DOCKER_TLS_VERIFY` | `CONTAINER_TLS_VERIFY` | tls=True/False |
| `DOCKER_CERT_PATH` | `CONTAINER_CERT_PATH` | cert/key 目录 |
| `DOCKER_USERNAME` | `CONTAINER_USERNAME` | registry auth（配合 DOCKER_PASSWORD） |
| `DOCKER_PASSWORD` | `CONTAINER_PASSWORD` | registry auth |
| `DOCKER_TIMEOUT` | `CONTAINER_TIMEOUT` | socket timeout 秒 |

规则：**CONTAINER_* > DOCKER_*（优先级高）**；两边都设 → 取 CONTAINER。

### CL-5 9 个 @cached_property 管理器字母序表
```
containers  →  ContainersManager (RunMixin + CreateMixin + Manager)
images      →  ImagesManager     (BuildMixin + Manager)
manifests   →  ManifestsManager
networks    →  NetworksManager
volumes     →  VolumesManager
pods        →  PodsManager       (pod 组容器，Swarm services 的 Podman 替代)
secrets     →  SecretsManager
system      →  SystemManager     (df/info/version/ping/events/login/close 7直方法)
quadlets    →  QuadletsManager   (v5.8 新增，systemd .container/.volume ... 管理)
```

### CL-6 7 个直接方法（从 PodmanClient 暴露，不经过管理器）
| 方法 | 实际转发对象 | 参数签名 |
|---|---|---|
| `df()` | `self.system.df()` | 无参数 |
| `ping()` | `self.system.ping()` | 无参数，返回 bool（非 docker-py 的 200 文本 "OK"） |
| `version()` | `self.system.version()` | 无参数，返回 Version / APIVersion / GoVersion / BuiltTime |
| `info()` | `self.system.info()` | 无参数 |
| `events(*, since, until, filters)` | `self.system.events()` | Generator |
| `login(*, username, password, registry, ...)` | `self.system.login()` | 返回 dict |
| `close()` | `self.api.close()` | 清理 requests.Session + SSH 隧道 |

### CL-7 ~ CL-10 4 个 NotImplementedError（Swarm 不支持，显式抛错）
```python
@property
def swarm(self):       # CL-7
    raise NotImplementedError("Podman 不支持 Swarm orchestration")
@property
def services(self):    # CL-8
    raise NotImplementedError("Podman 不支持 Swarm services")
@property
def configs(self):     # CL-9
    raise NotImplementedError("Podman 不支持 Swarm configs")
@property
def nodes(self):       # CL-10
    raise NotImplementedError("Podman 不支持 Swarm nodes")
```
⚠️ 注意：`client.secrets`（Podman 自有）是可用的；只 `secrets.external`（Swarm 概念）未实现。

### CL-11 version() 返回字段（docker-py 兼容）
```
{
  "Platform": {"Name": "podman/<ver>"},   # Podman 特有 Platform.Name
  "Version": "5.8.0",                     # 与 CLI podman --version 对齐
  "ApiVersion": "5.8.0",                  # libpod API 契约版本
  "MinAPIVersion": "5.0.0",
  "GitCommit": "...",
  "GoVersion": "go1.22.x",
  "Os": "linux", "Arch": "amd64",
  "KernelVersion": "6.10...",
  "BuildTime": "2025-..."
}
```

### CL-12 PodmanConfig().active_service 读取路径
读取顺序：`$XDG_CONFIG_HOME/containers/containers.conf` → `/etc/containers/containers.conf` → `/usr/share/containers/containers.conf`；[engine] 段 `service_dest=`, `active_service=` 决定连接名。

### CL-13 close() 语义
- with 语句退出时自动调用
- 关闭底层 requests.Session（HTTP keep-alive 断开）
- SSH 适配器：杀掉 `ssh -N -L` shell-out 子进程，删除本地转发 socket

## 第二部分：APIClient（传输层）7 条锚点

### API-1 类继承
```python
class APIClient(requests.Session):
    """低阶传输层：封装 requests.Session + scheme 路由 + 404→NotFound 映射"""
```
⚠️ 业务代码**不要直接用 APIClient**；除非你在写新 Manager，否则通过 PodmanClient.xxx_manager 间接调用。

### API-2 6 种 supported_schemes（L94-L101）

| scheme 前缀 | 适配器 | 典型 base_url 示例 | 适用场景 |
|---|---|---|---|
| `unix://` | UDSAdapter（unix domain socket） | `unix:///run/user/1000/podman/podman.sock` | 本地 Linux Rootless（最常用） |
| `http+unix://` | UDSAdapter（同上，HTTP 语义写 socket） | `http+unix:///run/podman/podman.sock` | 本地 Linux Rootful |
| `ssh://` | SSHAdapter（`ssh -N -L` shell-out） | `ssh://user@host:22/run/podman/podman.sock` | 远程 Linux SSH 免密 + key |
| `http+ssh://` | SSHAdapter（同上，HTTP 语义写转发 socket） | `http+ssh://user@host` | 远程（与 ssh:// 等价别名） |
| `tcp://` | HTTPAdapter（requests 原生） | `tcp://10.0.0.5:8888` | 远程 Podman API 暴露 TCP |
| `http://` / `https://` | HTTPAdapter（requests 原生） | `https://podman.example.com:8443` | 带 TLS 鉴权的远程守护进程 |

### API-3 APIResponse.__getattr__ 转发 + raise_for_status 增强
requests.Response 的子类/包装类（非直接继承），`raise_for_status()` 被重写：
```python
# 404 → 映射到精确异常
if response.status_code == 404:
    if "image" in request.path.lower() and "json" in request.path:
        raise ImageNotFound(...)
    else:
        raise NotFound(...)
# 其他 4xx/5xx → APIError（HTTPError 子类）
response.raise_for_status(not_found=ImageNotFound)
```

### API-4 DEFAULT_CHUNK_SIZE = 2 MB
- `images.build()` tarball upload chunk size
- `logs(stream=True)` 行读取 block size
- 性能调优：大量小镜像构建场景可调大 8~16 MB

### API-5 兼容端点 vs libpod 端点双前缀路由
```python
if self.compatible:
    # /v{version}/containers/json  ← docker-py 兼容路径
    url = f"{self.base_url}/v{APIVERSION}/{resource}"
else:
    # /v{version}/libpod/containers/json  ← Podman 原生路径（字段更多，含 NetworkSettings=false）
    url = f"{self.base_url}/v{version}/libpod/{resource}"
```
⚠️ 这是 `containers.list(sparse=not compatible)` 的根因（见 containers 概念 G2 洞察 #1）。

### API-6 max_pool_size / pool_connections
requests.Session 默认 pool_connections=10、max_pool_size=10。
批量并发 10+ 容器场景建议 `PodmanClient(max_pool_size=50)` 避免连接等待。

### API-7 timeout 两级语义
```python
# connect timeout (TCP 三次握手) = 10s
# read timeout (首字节响应)      = 180s
PodmanClient(timeout=(10, 180))  # 元组
# 也可 PodmanClient(timeout=60) 单值 → 两者相同
```
拉取大镜像 `policy=always` 超时常见 → 调 `timeout=(10, 600)`。
