---
type: Concept
title: "资源管理器架构"
description: "PodmanClient 的 9 个资源管理器（Managers）设计模式、cached_property 懒加载、Manager 基类与资源模型关系。"
tags: [podman-py, managers, architecture, ContainersManager, ImagesManager, cached_property, domain]
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

# 资源管理器架构

podman-py 采用**管理器模式（Manager Pattern）**组织各类容器资源的操作，通过 `@cached_property` 实现懒加载，将不同资源域的 API 隔离在独立的 Manager 类中。所有 Manager 继承自 `podman.domain.manager.Manager` 基类，负责与 APIClient HTTP 层交互并返回领域模型对象。

## 管理器总览

`PodmanClient` 通过 `@cached_property` 暴露 9 个资源管理器，首次访问时初始化并缓存：

```
PodmanClient
├── .containers    → ContainersManager   # 容器生命周期
├── .images        → ImagesManager       # 镜像管理与构建
├── .manifests     → ManifestsManager    # 镜像清单
├── .networks      → NetworksManager     # 网络配置
├── .volumes       → VolumesManager      # 数据卷
├── .pods          → PodsManager         # Pod 容器组
├── .secrets       → SecretsManager      # 密钥管理
├── .quadlets      → QuadletsManager     # Quadlet 单元文件
└── .system        → SystemManager       # 系统级操作
```

## Manager 基类设计

所有管理器位于 `podman/domain/` 目录，继承自 `Manager` 基类：

```python
class Manager:
    @property
    def resource(self):
        """返回此 Manager 管理的资源模型类，prepare_model() 使用"""
        raise NotImplementedError

    def prepare_model(self, attrs):
        """将 API 返回的 JSON 字典转换为资源模型对象"""
        return self.resource(attrs=attrs, client=self.api)
```

核心机制：
- `resource` 属性：子类必须返回对应的模型类（如 `Container`、`Image`）
- `prepare_model()`：将 API 响应的 JSON dict 实例化为领域模型对象
- `self.api`：持有 `APIClient` 实例，用于发送 HTTP 请求

## @cached_property 懒加载

管理器使用 Python 3.8+ 内置的 `functools.cached_property` 装饰器：

```python
@cached_property
def containers(self) -> ContainersManager:
    return ContainersManager(client=self.api, podman_client=self)
```

特点：
- **首次访问时初始化**：不访问的管理器不会实例化，减少启动开销
- **实例级别缓存**：同一 PodmanClient 实例多次访问返回同一 Manager 对象
- **持有 APIClient 引用**：所有 Manager 共享底层 HTTP 连接池

## ContainersManager（容器管理器）

文件：`podman/domain/containers_manager.py`，继承自 `RunMixin, CreateMixin, Manager`

| 方法 | 说明 |
|------|------|
| `list(**kwargs)` | 列出容器，支持 `all`/`filters`/`sparse`/`compatible` 等参数 |
| `get(key, **kwargs)` | 按名称或 ID 获取单个容器 |
| `exists(key)` | 检查容器是否存在 |
| `create(image, **kwargs)` | 创建容器（来自 CreateMixin） |
| `run(image, **kwargs)` | 创建并启动容器（来自 RunMixin） |
| `remove(container_id, **kwargs)` | 删除容器，支持 `force`/`v` 参数 |
| `prune(filters=None)` | 清理已停止的容器 |

**sparse 模式**：`list(sparse=True)`（libpod 默认）只返回基本信息，需要调用 `container.reload()` 获取完整属性，提高列表性能；`compatible=True`（Docker 兼容模式）默认 `sparse=False`。

## ImagesManager（镜像管理器）

文件：`podman/domain/images_manager.py`，继承自 `BuildMixin, Manager`

| 方法 | 说明 |
|------|------|
| `list(**kwargs)` | 列出镜像，支持 `name`/`all`/`filters` |
| `get(name)` | 按名称或 ID 获取镜像 |
| `exists(key)` | 检查镜像是否存在 |
| `pull(repository, tag=None, **kwargs)` | 拉取镜像，支持 `progress_bar`/`stream`/`platform` |
| `push(repository, tag=None, **kwargs)` | 推送镜像到 registry |
| `build(**kwargs)` | 从 Containerfile 构建镜像（来自 BuildMixin） |
| `remove(image, force=None, noprune=False)` | 删除镜像 |
| `load(data=None, file_path=None)` | 从 tar 包加载镜像 |
| `prune(**kwargs)` | 清理未使用的镜像 |
| `search(term, **kwargs)` | 搜索 registry 镜像 |
| `scp(source, dest=None, quiet=False)` | 在主机间安全复制镜像 |
| `get_registry_data(name, auth_config=None)` | 获取镜像 registry 元数据 |

**pull 进度条**：安装 `rich` 后可使用 `pull(..., progress_bar=True)` 显示下载进度。

## 其他管理器速查

| 管理器 | 文件 | 核心操作 |
|--------|------|---------|
| `ManifestsManager` | `podman/domain/manifests.py` | 多架构清单创建/推送/查看 |
| `NetworksManager` | `podman/domain/networks_manager.py` | 网络创建/列表/删除/连接/断开 |
| `VolumesManager` | `podman/domain/volumes.py` | 数据卷创建/列表/删除/清理 |
| `PodsManager` | `podman/domain/pods_manager.py` | Pod 组创建/启动/停止/删除 |
| `SecretsManager` | `podman/domain/secrets.py` | Secret 创建/列表/删除 |
| `QuadletsManager` | `podman/domain/quadlets.py` | Quadlet 单元文件管理（Podman 特有） |
| `SystemManager` | `podman/domain/system.py` | `df()`/`info()`/`ping()`/`version()`/`login()` |

## Mixin 组合模式

部分管理器通过 Mixin 类扩展能力：

```
ContainersManager
├── Manager          # 基类：get/list/remove/prune/exists/prepare_model
├── CreateMixin      # create() 方法
└── RunMixin         # run() 方法（create + start）

ImagesManager
├── Manager          # 基类
└── BuildMixin       # build() 方法
```

这种组合模式将不同维度的操作分离到独立的 Mixin 类中，避免 Manager 类过于庞大。

## 直接方法代理

PodmanClient 上的系统级方法实际代理到对应管理器：

```python
def df(self) -> dict[str, Any]:
    return self.system.df()

def ping(self) -> bool:
    return self.system.ping()

def events(self, *args, **kwargs):
    return EventsManager(client=self.api).list(*args, **kwargs)
```

## 领域目录结构（podman/domain/）

| 文件 | 说明 |
|------|------|
| `manager.py` | Manager 基类 |
| `config.py` | PodmanConfig 配置解析（containers.conf） |
| `containers.py` / `containers_create.py` / `containers_manager.py` / `containers_run.py` | 容器域模型与管理器 |
| `images.py` / `images_build.py` / `images_manager.py` | 镜像域模型与管理器 |
| `networks.py` / `networks_manager.py` | 网络模型与管理器 |
| `volumes.py` / `pods.py` / `secrets.py` / `manifests.py` / `quadlets.py` | 其他资源模型 |
| `system.py` | 系统管理器 |
| `events.py` | 事件管理器 |
| `json_stream.py` | JSON 流解析器 |
| `ipam.py` | IP 地址管理配置 |
| `registry_data.py` | Registry 元数据模型 |

## 资源模型对象

每个 Manager 返回对应的资源模型实例（如 `Container`、`Image`、`Network`、`Volume`），模型对象持有 `client.api` 引用，可以执行实例级操作：

```python
container = client.containers.get("my-container")
container.start()      # 实例方法：启动
container.stop()       # 实例方法：停止
container.reload()     # 重新加载属性
container.logs()       # 获取日志
```

## 相关概念

- [/concepts/01-connection.md](/concepts/01-connection.md)
- [/concepts/03-containers.md](/concepts/03-containers.md)
- [/concepts/04-images.md](/concepts/04-images.md)
