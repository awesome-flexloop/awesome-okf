---
type: Concept
title: 02 - 资源管理器架构：Mixin + Manager
description: Manager 基类骨架 + @property resource + prepare_model()、@cached_property 9个管理器懒加载（containers/images/manifests/networks/volumes/pods/secrets/system/+quadlets）、Mixin 横切扩展 RunMixin/CreateMixin/BuildMixin、PodmanResource 基类属性与实例方法、资源对象-管理器关系图
tags: [Manager Pattern, Mixin, cached_property, PodmanResource, CRUD Skeleton, 三继承模式]
generated:
  by: method_orchestrator/seven-concepts-cmd
  at: 2026-09-07T00:00:00Z
verified:
  by: process:podman-py-grep-20260907
  at: 2026-09-07T00:00:00Z
status: stable
stale_after: 2027-09-07
sources:
  - id: src-manager-base
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/manager.py
    title: Manager 基类 list/get/exists + prepare_model + self.api + self.client 属性
  - id: src-podmanresource
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/manager.py
    title: PodmanResource attrs / id / short_id / name / reload() / remove() 基类
  - id: src-9managers
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/client.py
    title: PodmanClient 9 个 @cached_property 管理器注册
  - id: src-runmixin
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/containers_run.py
    title: RunMixin.run() image+command+detach/stream/remove 4语义
  - id: src-createmixin
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/containers_create.py
    title: CreateMixin.create(** 30+ kwargs → /libpod/containers/create)
  - id: src-buildmixin
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/images_build.py
    title: BuildMixin.build(path, containerfile, buildargs, stream, nocache, squahs, gzip → BuildError)
---

# 02 - 资源管理器架构：Mixin + Manager

podman-py 领域层（domain/）采用 **「Manager 基类（纵向 CRUD） + Mixin 扩展（横向语义）」** 双模式组合：所有 9 个资源类型共享同一套 Manager 骨架（list/get/exists/create/prepare_model），但 Containers 需要 `run()` 语义、Images 需要 `build()` 语义——通过 Mixin 在不变更基类的情况下追加扩展。

## 1. PodmanClient：9 个管理器懒加载（@cached_property）

PodmanClient（薄门面）不 new 具体 Manager，首次访问时才实例化。源码中 9 个管理器的定义顺序（`podman/client.py` L146-L188）如下，实际使用时通过属性名访问，顺序不影响语义：

| # | @cached_property 名称 | 对应 Python 文件 | 继承组合 | 资源对象类 |
|---|---|---|---|---|
| 1 | **`containers`** | `domain/containers_manager.py` | **RunMixin + CreateMixin + Manager**（三继承，最多） | Container |
| 2 | **`images`** | `domain/images_manager.py` | **BuildMixin + Manager**（二继承） | Image |
| 3 | **`manifests`** | `domain/manifests.py` | Manager（纯） | Manifest |
| 4 | **`networks`** | `domain/networks_manager.py` | Manager（纯） | Network |
| 5 | **`volumes`** | `domain/volumes.py` | Manager（纯） | Volume |
| 6 | **`quadlets`** | `domain/quadlets.py`（v5.8 **新增**） | Manager（纯） | Quadlet（6 个属性 + delete/get_contents/print_contents） |
| 7 | **`pods`** | `domain/pods_manager.py` | Manager（纯） | Pod |
| 8 | **`secrets`** | `domain/secrets.py` | Manager（纯） | Secret |
| 9 | **`system`** | `domain/system.py` | Manager（纯，同时 7 个方法被挂 PodmanClient 门面：df/ping/version/info/events/login/close） | — |

**懒加载模式源码示例**（client.py 任意一条 @cached_property）：

```python
@cached_property
def containers(self) -> ContainersManager:
    return ContainersManager(client=self)  # Manager 构造时拿到 PodmanClient 引用
```

懒加载的好处：
- 你只用 `client.version()`、`client.ping()` 时，不会 import 任何 domain/*.py，启动快；
- 任何管理器构造异常（比如缺依赖）只在首次访问时抛，不阻塞其他功能；
- 新增资源类型（如 v5.8 quadlets）**只加一个 cached_property + 一个 Manager 文件**，零回归。

## 2. Manager 基类骨架（podman/domain/manager.py Manager）

Manager 是所有资源管理器的纵向基类，定义统一 CRUD 骨架 + 资源对象装配：

```
Manager（抽象基类，不可直接 new）
 ├── 构造：__init__(client, /) → self._client = client; self.collection = <HTTP path 前缀如 "/containers">
 │
 ├── self.client → PodmanClient 引用（用于跨 Manager 调用，如 container.exec_run 内部再拉 images.pull）
 ├── self.api    → APIClient 引用（self.client.api，直接发 HTTP，不写 requests 代码）
 │
 ├── @property @abstractmethod resource → 返回"资源对象类"（如 Container/Image/Quadlet）
 │     子类必须实现：
 │       ContainersManager: return Container
 │       ImagesManager:     return Image
 │       QuadletsManager:   return Quadlet
 │
 ├── list(**kwargs) → 默认发 GET /{collection}/json，响应每个 dict 走 prepare_model 组装资源对象
 ├── get(key, **kwargs) → GET /{collection}/{key}/json，404 → NotFound，prepare_model → 单个资源对象
 ├── exists(key) → GET /{collection}/{key}/exists，返回 response.ok（True/False，永不抛 404）
 │
 └── prepare_model(attrs=resp.json, /) → 核心装配函数：
        attrs["manager"] = self  # 资源对象能反向找到 manager，从而调 reload/remove/exec_run
        attrs["client"]  = self._client
        return self.resource(attrs)  # 调资源类构造函数
```

关键示例（ContainersManager 真实 3 行模式）：

```python
class ContainersManager(RunMixin, CreateMixin, Manager):  # ← 三继承：RunMixin/CreateMixin 横切 Manager
    @property
    def resource(self):  # 满足 abstractmethod，返回类对象（不是实例）
        return Container

    def get(self, key, **kwargs):  # ← 可以覆盖基类，追加 compatible 参数、sparse 逻辑
        compatible = kwargs.get("compatible", False)
        cid = urllib.parse.quote_plus(key)
        resp = self.api.get(f"/containers/{cid}/json", compatible=compatible)
        resp.raise_for_status()
        return self.prepare_model(attrs=resp.json())
```

## 3. Mixin 横切扩展：RunMixin / CreateMixin / BuildMixin

**Mixin 是不带构造、只带一个方法的纯逻辑类**（Go 语言 interface 默认方法等价物），插到继承链左端即被 Python 方法解析顺序（MRO）匹配为第一候选方法：

| Mixin 名称 | 插入的 Manager | 提供方法 | 复杂度（行数） | 代码位置 |
|---|---|---|---|---|
| **RunMixin** | ContainersManager 左端 | `run(image, command, *, detach/stream/remove/auto_remove, **kwargs → Container or Generator[bytes] or Iterator[bytes] or raise ContainerError)` | ~90 行 | `containers_run.py` |
| **CreateMixin** | ContainersManager 中间 | `create(image, command=None, **~30 kwargs → Container)` 调 `/libpod/containers/create` + 如果镜像不存在按 policy pull | ~50 行 | `containers_create.py` |
| **BuildMixin** | ImagesManager 左端 | `build(path, containerfile="Containerfile", buildargs, tags, nocache, pull, rm, squash, platform, network, gzip, extra_hosts, stream → (Image, build_log) or stream=True→ Iterator[dict])` BuildError 抛错 | ~120 行 | `images_build.py` |

> 为什么 **Mixin 左端继承顺序很重要**？Python MRO 从左到右匹配同名方法：
> `class ContainersManager(RunMixin, CreateMixin, Manager):` → 当外部调 `cm.run()`，先查 RunMixin（命中，正确）；若顺序写反 `Manager, RunMixin` → 先查 Manager（无 run，AttributeError，失败）。

### 3.1 Mixin 与 Manager 基类的协作（以 RunMixin.run 为例）

RunMixin.run 的四返回语义完全依赖 Manager 基类的 prepare_model + 资源对象方法：

```
RunMixin.run(
    image="docker.io/library/postgres:16",
    command=["postgres"],
    detach=True, remove=False,
    ports={"5432/tcp": 5432}, environment={"POSTGRES_PASSWORD":"xxx"}
)
│
├── ① isinstance(Image) 处理 → 归一化 image_id = str
├── ② self.create(image=image_id, command=command, ports=ports, environment=...)
│        │  这个 self.create 来自 CreateMixin（因为 MRO 左端第二），不是 Manager 基类
│        └─→ return Container 对象（通过 Manager.prepare_model 装配）
│
├── ③ container.start()      ← Container 资源对象自身的实例方法（来自 PodmanResource 子类）
├── ④ container.reload()     ← Container 资源对象方法，调 manager.get(key) 刷新 attrs
│
├── ⑤ if detach:
│       if remove=True: 起 daemon thread 监控 container.wait() 退出后调 container.remove(v=True)
│       return container  ← Case 1：返回 Container 对象（最常用）
│   else:
│       等待 container.wait()
│       if exit_status != 0: raise ContainerError(container, exit_status, command, image, stderr)
│       return logs(stream=True → Generator; stream=False → Iterator)
│                    ← Case 2/3/4：日志流 or 错误
```

这解释了一个常见困惑：**"containers.run() 代码在哪？"** — 不在 containers_manager.py，在左邻的 containers_run.py。查文档先看 MRO 继承链！

## 4. PodmanResource 基类：所有资源对象的骨架（manager.py 内定义）

资源对象（Container/Image/Volume 等）构造时带 `attrs` dict + `manager` + `client` 反向引用，因此能自己发 API：

```
PodmanResource（抽象基类）
 ├── __init__(attrs, /) → self.attrs = attrs; self.id = attrs["Id"]; self.short_id = id[:12]; self.name = attrs.get("Name", "")
 ├── self.manager 反向引用 → 能调 manager.get(self.id) 做 reload
 ├── self.client  反向引用 → 能调 client.* 或 client.images.* 等跨管理器
 │
 ├── reload(**kwargs) → 模板方法：GET /{collection}/{self.id}/json → 更新 self.attrs（子类覆盖 URL 路径）
 ├── remove(**kwargs) → 模板方法：DELETE /{collection}/{self.id}（force/v 等 kwargs 透传）
 │
 └── 资源子类追加方法（举例）
     Container: start / stop(timeout=10) / kill(signal="SIGKILL") / pause / unpause / restart
                exec_run(cmd, stdout=True, stderr=True, stdin=False, tty=False,
                         stream=False, detach=False, workdir, user, environment)
                logs(stream, timestamps, tail, since, until, stdout, stderr)
                wait(condition="exited" / "removed" / "stopped" / "running")
                top(ps_args) / stats(stream, decode) / commit(repository, tag, ...) → Image
                diff / rename(name) / resize(h, w) / attach / export(chunk_size) → tar stream
     Image:     tag(repo, tag, force) / history / inspect_distribution
                save(chunk_size) → tar stream  (配对：images_manager.load(tar))
     Quadlet:   delete(force, ignore, reload_systemd) / get_contents → str / print_contents → None
```

**管理器-资源对象-API 三层关系（UML 风格文字图）**

```
PodmanClient (client.py)
    │ @cached_property containers  ──── new ──▶  ContainersManager (domain/containers_manager.py)
    │                                                       │ extends Manager (domain/manager.py)
    │                                                       │   Manager.list/get/exists/prepare_model
    │                                                       │ extends RunMixin (domain/containers_run.py)  → run(...)
    │                                                       │ extends CreateMixin(domain/containers_create.py)→ create(...)
    │                                                       │
    │ .get(id) / .list() → prepare_model(attrs) ────── new ▼
    │                                            Container (domain/containers.py extends PodmanResource)
    │                                                         │ .start/stop/pause/exec_run/logs/reload/remove
    │                                                         └──→ .manager = ContainersManager（反向回指）
    │ .containers.get("abc").exec_run("ls -la")
    └──────────────────────────────────────────────────────────────▶ exec_run 内部 .manager.api.post(f".../exec")
```

## 5. 模式可迁移（G3 触发条件/核心步骤/反模式）

| 维度 | 内容（直接可复用到 docker SDK 编写、自建 API SDK、云 SDK 等场景） |
|---|---|
| **触发场景** | ①面向 RESTful/UDS 资源的 Python SDK；②需要对多个资源（container/image/network…）提供一致 CRUD；③需要追加高阶语义（run/build）又不想修改基类；④ 已有另一个 SDK（docker-py）要做兼容 API |
| **核心步骤** | ① 定义 Thin Facade（PodmanClient），管理器通过 @cached_property 懒加载；② 建 Manager 基类：list/get/exists（默认） + 抽象 @property resource + prepare_model；③ 每个资源新建 XxxManager(extend Manager) + 对应 XxxResource(extend PodmanResource)；④ 高阶语义独立 Mixin 文件，按 MRO 左端顺序插入；⑤ 资源对象 attrs/manager/client 三属性，保证 reload/remove 等模板方法可复用 |
| **反模式（切勿踩）** | ❌ 厚门面：管理器实现全写在 client.py，回归慢；❌ Mixin 顺序写反导致 AttributeError；❌ 资源对象不反向回指 manager，每次 reload 都让用户调 manager.get(id)（体验差）；❌ 所有管理器硬编码一个继承类，用 if-elif 分发 run/build（违反开闭，新增资源必须改基类）；❌ 不用 lazy property，启动时 9 个管理器全 import 全构造（冷启动慢 3-5 倍） |
