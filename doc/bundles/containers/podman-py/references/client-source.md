---
type: Reference
title: "client.py PodmanClient 核心客户端"
description: "PodmanClient 类定义、构造参数、from_env 类方法、资源管理器属性、上下文管理器协议与 Docker 兼容性别名。"
tags: [podman-py, PodmanClient, client, from_env, context-manager, docker-compat]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:45:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: client-py
    resource: podman/client.py
    title: podman/client.py
  - id: init-py
    resource: podman/__init__.py
    title: podman/__init__.py
  - id: version-py
    resource: podman/version.py
    title: podman/version.py
---

# PodmanClient 核心客户端

## 模块导出（podman/__init__.py）

```python
from podman.client import PodmanClient, from_env
from podman.version import __version__

__all__ = ['PodmanClient', '__version__', 'from_env']
```

**Docker 兼容性别名**：
```python
DockerClient = PodmanClient
```

## 版本信息（podman/version.py）

- `__version__ = "5.8.0"`
- `__compatible_version__ = "1.40"`（兼容 Docker API 版本）

## PodmanClient 类定义

```python
class PodmanClient(AbstractContextManager):
    """Client to connect to a Podman service."""
```

继承自 `contextlib.AbstractContextManager`，支持 `with` 语句上下文管理。

### __init__ 关键字参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `base_url` | `str` | Podman 服务完整 URL，支持 unix/http+unix/ssh/http+ssh/tcp/http scheme |
| `version` | `str` | API 版本，默认 `"auto"` 使用服务端版本 |
| `timeout` | `int` | API 调用超时秒数，默认使用 socket 全局默认超时 |
| `tls` | - | 已忽略，SSH 连接配置委托给 SSH 主机配置 |
| `user_agent` | `str` | 服务连接 User-Agent，默认 `PodmanPy/<Code Version>` |
| `credstore_env` | `Mapping[str, str]` | 凭证存储环境变量字典 |
| `use_ssh_client` | `bool` | SSH 连接始终使用系统 SSH 客户端，默认 `True` |
| `max_pool_size` | `int` | 连接池保存的连接数 |
| `connection` | `str` | 从 `containers.conf` 读取的连接配置标识符 |
| `identity` | `str` | SSH 认证私钥路径 |

### base_url 支持的格式示例

```
http+ssh://<user>@<host>[:port]</run/podman/podman.sock>[?secure=True]
http+unix://</run/podman/podman.sock>
tcp://<localhost>[:<port>]
```

### 默认连接逻辑

当未指定 `base_url` 或 `connection` 时：
1. 检查 `PodmanConfig().active_service`，如果是 machine 则使用其 URL
2. 否则回退到本地 Unix socket：`http+unix://<runtime_dir>/podman/podman.sock`
   - `runtime_dir` 通过 `podman.api.path_utils.get_runtime_dir()` 获取

### from_env 类方法

```python
@classmethod
def from_env(
    cls,
    *,
    version: str = "auto",
    timeout: Optional[int] = None,
    max_pool_size: Optional[int] = None,
    ssl_version: Optional[int] = None,
    assert_hostname: bool = False,
    environment: Optional[dict[str, str]] = None,
    credstore_env: Optional[dict[str, str]] = None,
    use_ssh_client: bool = True,
) -> "PodmanClient"
```

从环境变量读取连接配置：
- `CONTAINER_HOST` / `DOCKER_HOST`：Podman 服务 URL
- `CONTAINER_TLS_VERIFY` / `DOCKER_TLS_VERIFY`：是否验证主机 CA 证书
- `CONTAINER_CERT_PATH` / `DOCKER_CERT_PATH`：TLS 证书路径

### 资源管理器属性（@cached_property）

| 属性 | 类型 | 说明 |
|------|------|------|
| `containers` | `ContainersManager` | 容器操作管理器 |
| `images` | `ImagesManager` | 镜像操作管理器 |
| `manifests` | `ManifestsManager` | 清单操作管理器 |
| `networks` | `NetworksManager` | 网络操作管理器 |
| `volumes` | `VolumesManager` | 卷操作管理器 |
| `quadlets` | `QuadletsManager` | Quadlet 操作管理器 |
| `pods` | `PodsManager` | Pod 操作管理器 |
| `secrets` | `SecretsManager` | 密钥操作管理器 |
| `system` | `SystemManager` | 系统操作管理器 |

### 直接方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `df()` | `dict[str, Any]` | 磁盘使用统计 |
| `events(*args, **kwargs)` | - | 事件监听 |
| `info(*args, **kwargs)` | - | 系统信息 |
| `login(*args, **kwargs)` | - |  registry 登录 |
| `ping()` | `bool` | 服务连通性检测 |
| `version(*args, **kwargs)` | - | 版本信息 |
| `close()` | - | 释放客户端资源 |

### 不支持的操作

访问以下属性会抛出 `NotImplementedError`：
- `swarm`
- `services`（= swarm）
- `configs`（= swarm）
- `nodes`（= swarm）
