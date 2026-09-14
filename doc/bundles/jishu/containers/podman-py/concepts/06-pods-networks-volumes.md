---
type: concept
title: 06 - Pod / Network / Volume：组编排原语与资源契约差异
description: Pod 共享命名空间容器组（ID 键/stop 的 t 参数/stats 默认非流）、Network 端点连接与 IPAM lease_range 转换、Volume 身份即名与归档导入；三类资源在身份键、端点后缀、prune 语义上的系统差异矩阵
tags: [podman-py, pods, networks, volumes, ipam, resource-contract, libpod-api]
generated:
  by: source-code-to-okf-wiki/sc-20260914-podman-py-wiki
  at: 2026-09-14
verified:
  by: process:seven-concepts-v
  at: 2026-09-14
status: stable
stale_after: 2027-09-14
sources:
  - id: src-code-map
    resource: /references/source-code-map.md
    title: podman-py vendor 全量源码信源登记（commit 5dd81b4）
  - id: src-api-r2
    resource: /references/api-source.md
    title: Manager + Mixin 基类信源（R2）
---

# 06 - Pod / Network / Volume：组编排原语与资源契约差异

容器与镜像之外，Podman 的"组编排"能力由三类一等资源承载：**Pod**（共享命名空间的容器组）、**Network**（网络与端点连接）、**Volume**（独立生命周期的持久卷）。它们与容器/镜像共用同一套 `Manager` + `PodmanResource` 骨架（见 [02 资源管理器架构](02-managers.md)），但各自映射的 libpod 端点形成于不同时期，**身份键、URL 后缀、错误键名存在系统性差异——严禁用一个资源的写法类推另一个**。

## 6.1 Pod：共享命名空间的容器组

Pod 把多个容器编进同一个 infra 组，共享 network/UTS/IPC 等命名空间。模型在 [pods.py](https://github.com/containers/podman-py/blob/v5.8.0/podman/domain/pods.py)，管理器在 [pods_manager.py](https://github.com/containers/podman-py/blob/v5.8.0/podman/domain/pods_manager.py)。

### 6.1.1 身份与查询

- `Pod.id` 读取顺序是 `attrs["ID"]` 优先、回退 `attrs["Id"]`（大写 `ID` 在前，与容器的 `Id` 恰好相反）；`Pod.name` 读 `attrs["Name"]`。
- `PodsManager.get(pod_id)` → `GET /pods/{id}/json`；`exists(key)` → `GET /pods/{key}/exists`，直接返回 `response.ok` 布尔（404 不抛异常）。
- `list(filters=...)` → `GET /pods/json`。可用 9 类过滤器：`ctr-ids`、`ctr-names`、`ctr-number`、`ctr-status`、`id`、`name`、`status`、`label`、`network`（值为网络 **ID** 而非名称）。

### 6.1.2 创建与删除

```python
# create：name 为位置参数，其余 libpod CreatePod 字段经 **kwargs 透传
pod = client.pods.create("demo_pod")          # POST /pods/create，body 强制含 "name"
# 创建响应只给 Id，管理器立即 get 一次返回完整 Pod 对象

# 容器入组：创建容器时传 pod=<Pod 实例>（官方 demo 的用法）
container = client.containers.create(image, pod=pod)

pod.remove(force=True)                         # DELETE /pods/{id}?force=true
```

`prune(filters=None)` → `POST /pods/prune`：逐项检查响应数组中的 `Err` 键，非空即抛 `APIError`；成功返回 `{"PodsDeleted": [id...], "SpaceReclaimed": 0}`——**Pod 清理不汇报回收空间，该值恒为 0**。

### 6.1.3 Pod 级动作（Pod 实例方法）

| 方法 | HTTP | 备注 |
|------|------|------|
| `start()` / `restart()` / `pause()` / `unpause()` / `kill(signal=None)` | POST `/pods/{id}/<action>` | 组内容器统一动作 |
| `stop(timeout=None)` | POST `/pods/{id}/stop` | query 参数名是 **`t`**（不是 timeout） |
| `top(ps_args=None)` | GET `/pods/{id}/top?stream=False` | 响应体为空串时返回 `{"Processes": [], "Titles": []}` |
| `remove(force=None)` | 委托管理器 | 等价于 `client.pods.remove(pod.id, force=...)` |

`PodsManager.stats(all=..., name=..., stream=False, decode=False)` → `GET /pods/stats`，有两个反直觉点：

1. `all` 与 `name` 同时给出直接 `ValueError("...mutually exclusive")`；入参 `name` 映射为 query 参数 `namesOrIDs`。
2. **`stream` 默认 False**（源码注释：为不破坏旧用户刻意保留，计划在新 major 版本对齐 container.stats）。非流式且 `decode=False` 时返回的是**原始字节 `response.content`**，不是字典；要字典需显式 `decode=True`。

## 6.2 Network：网络、端点与 IPAM

模型 [networks.py](https://github.com/containers/podman-py/blob/v5.8.0/podman/domain/networks.py)，管理器 [networks_manager.py](https://github.com/containers/podman-py/blob/v5.8.0/podman/domain/networks_manager.py)，IPAM 数据类 [ipam.py](https://github.com/containers/podman-py/blob/v5.8.0/podman/domain/ipam.py)。

### 6.2.1 身份模型的两个特殊点

- `Network.id` 先取 `attrs["Id"]`；**缺失时不退化为 None，而是用 `sha256(attrs["name"].encode("ascii")).hexdigest()` 现场推导**。
- `get(key)` 的端点是 `GET /networks/{key}`——**常规 CRUD 资源管理器中唯一不带 `/json` 后缀的 get**（Quadlet 走独立的 quadlets 路径族，另当别论）；`exists` 仍是 `/networks/{key}/exists`，`remove` 是 `DELETE /networks/{name}?force=`（按名删除）。
- `reload()` 按 **name**（而非 id）重新查询。

### 6.2.2 create：snake_case 入参到混合键名 body 的映射

`NetworksManager.create(name, driver=None, dns_enabled=None, network_dns_servers=None, enable_ipv6=None, internal=None, ipam=None, labels=None, options=None, subnets=None, ...)` 组装的 body 键名并非常规的 snake_case：

```python
data = {
    "name": name,
    "driver": ...,
    "dns_enabled": ...,              # 注意：不是 dnsEnabled
    "network_dns_servers": ...,
    "subnets": ...,
    "ipv6_enabled": ...,             # 入参叫 enable_ipv6，body 键叫 ipv6_enabled
    "internal": ..., "labels": ..., "options": ...,
}
```

`attachable` / `check_duplicate` / `ingress` / `scope` 四个 docker 风格参数被接收但**忽略**（docstring 标注 Ignored）。

`ipam=IPAMConfig(...)`（dict 子类）经 `_prepare_ipam` 转换：

- `IPAMConfig(driver="host-local", pool_configs=[IPAMPool(...)], options={})`：driver 默认 `host-local`，docstring 明示 **Podman 仅支持一个 pool**；键为 PascalCase（`Config/Driver/Options`）。
- `IPAMPool(subnet, iprange, gateway, aux_addresses=None)`：键 `Subnet/IPRange/Gateway/AuxiliaryAddresses`（aux_addresses 被接收但忽略）。
- 转换结果：`ipam_options={"driver": ...}`，`subnets=[{"gateway", "subnet", "lease_range": {"start_ip", "end_ip"}}]`；当给了 `IPRange`，用 `ipaddress.ip_network` 计算租约范围——**起始地址取 `net[1]`、结束取 `net[-2]`**（跳过网络地址与广播地址）。

### 6.2.3 connect / disconnect：运行期端点管理

```python
net.connect(
    container,                          # Container 实例会被换成 .id
    aliases=["db"],                     # → EndpointConfig.Aliases
    ipv4_address="10.89.0.22",          # 同时进 IPAMConfig.IPv4Address 与外层 IPAddress
    ipv6_address=None,
    link_local_ips=None,                # → IPAMConfig.Links / 外层 Links
    driver_opt=None,                    # → EndpointConfig.DriverOpts
)                                       # POST /networks/{name}/connect
net.disconnect(container, force=False)  # POST /networks/{name}/disconnect
```

请求体是嵌套的 PascalCase 结构（`{"Container": ..., "EndpointConfig": {"NetworkID", "Aliases", "IPAddress", "IPAMConfig", ...}}`），组装时逐层剔除 None 与空值。`Network.containers` 属性每次新建 `ContainersManager`，按 `attrs["containers"]` 的键逐个查询，属性缺失时返回 `[]`。

`list(names=None, ids=None, filters=None, ...)` → `GET /networks/json`：`names`/`ids` 不作为独立 query 参数，而是被**并入 filters 字典**（`filters["name"]`、`filters["id"]`）。`prune` 的逐项错误键是 **`Error`**——与 Pod/Volume 的 `Err` 拼写不同，捕获处理时勿照搬。

## 6.3 Volume：身份即名称的持久卷

模型与管理器同居 [volumes.py](https://github.com/containers/podman-py/blob/v5.8.0/podman/domain/volumes.py)。

### 6.3.1 身份与 CRUD

- `Volume.id` 直接返回 `self.name`（`attrs["Name"]`）——卷没有独立于名称的 ID 语义，这是全资源族最简单的身份模型。
- `create(name=None, driver=None, driver_opts=None, labels=None)`：body 为 PascalCase `{"Driver", "Labels", "Name", "Options"}`（注意 driver_opts→Options），POST `/volumes/create`。
- `get(volume_id)` → `/volumes/{id}/json`；`inspect(tls_verify=True)` → `/volumes/{id}/json?tlsVerify=`。
- **`list()` 对 404 的处理是返回 `[]` 而非抛异常**（`status_code == requests.codes.not_found` 特判）；其他资源族无此宽容。

### 6.3.2 prune 与归档

```python
# prune：POST /volumes/prune，错误键 "Err"，explanation 用 item.get("Id")
# 与 pods/networks 不同：SpaceReclaimed 逐项累加 item["Size"]，是真实回收字节数
result = client.volumes.prune()
# {"VolumesDeleted": [...], "SpaceReclaimed": 123456}

# 导出/导入（POST 主体为未压缩 tar 字节）
blob = client.volumes.export_archive("pgdata")          # GET  /volumes/{name}/export
client.volumes.import_archive("pgdata", data=blob)     # POST /volumes/{name}/import
client.volumes.import_archive("pgdata", path="v.tar")  # 或读文件字节
```

`import_archive` 的参数纪律：`data` 与 `path` **必须恰好给一个**——都不给或都给均抛 `RuntimeError`，path 指向的文件不存在同样抛错。

## 6.4 资源契约差异矩阵（跨资源操作必读）

| 维度 | Pod | Network | Volume |
|------|-----|---------|--------|
| 模型 id 键 | `ID` 优先，回退 `Id` | `Id`，缺失则 sha256(name) 推导 | 等同 name |
| get URL | `/pods/{id}/json` | `/networks/{key}`（无 /json） | `/volumes/{id}/json` |
| list URL | `/pods/json` | `/networks/json` | `/volumes/json` |
| remove 标识 | id（实例或字符串） | **name** | name |
| prune 错误键 | `Err` | **`Error`** | `Err` |
| SpaceReclaimed | 恒 0 | 恒 0 | **逐项累加 Size** |
| list 404 行为 | raise_for_status | raise_for_status | **返回 `[]`** |
| stats 流式默认 | `stream=False`（decode=False 返回原始字节） | — | — |
| create body 风格 | 透传 libpod + name | 混合键名（dns_enabled/ipv6_enabled/subnets） | PascalCase（Driver/Labels/Name/Options） |

> **G2 洞察**：这些差异不是 SDK 的疏忽，而是对 libpod 各历史端点的忠实映射。实践含义：写跨资源清理/巡检代码时，**每个资源都要回源码核对端点与键名**，抽象一个"统一 CRUD 辅助函数"反而会埋下 Network 的 `/json` 缺失、prune 键名分叉、404 语义不同这三颗雷。

## 6.5 可迁移模式

| 模式 | 要点 |
|------|------|
| 契约差异矩阵法 | 学习一个"同族多资源"SDK 时，先建身份键/端点/错误语义/默认值差异矩阵，再写抽象；矩阵优先于 DRY |
| 布尔端点探测 | `exists()` 一律以 `response.ok` 为据，不消费错误体；适合幂等脚本的资源存在性判断 |
| prune 结果消费 | 只有 Volume/Image 的 SpaceReclaimed 可信；Pod/Network 的清理审计应以删除 ID 列表为准 |
| 流式默认值显式化 | 调用 stats 类接口时显式传 `stream=`/`decode=`，不依赖跨资源默认值一致性 |

## 相关概念

- [02 - 资源管理器架构：Mixin + Manager](02-managers.md)：本卷三资源共用的 Manager/PodmanResource 骨架
- [03 - 容器生命周期与状态机](03-containers.md)：容器入组（`pod=` 参数）与容器自身的状态流转
- [07 - Secret / Manifest / Registry：密钥与多架构分发](07-secrets-manifests-registry.md)：另外两个"小契约"资源
- [10 - 传输与配置深化](10-transport-deep-dive.md)：上述端点如何拼上 libpod/兼容双前缀
- [信源登记：vendor 全量源码地图](/references/source-code-map.md)：端点差异速查表与文件行号
