---
type: concept
title: 07 - Secret / Manifest / Registry：密钥与多架构镜像分发
description: Secret 裸字节上送与 Spec.Name 身份、Manifest 多架构清单 add/push/remove 与 list 不支持、RegistryData 平台匹配；push 进度为客户端合成、load 生成器、prune 响应 null 防护等分发面陷阱
tags: [podman-py, secrets, manifests, registry, multi-arch, image-distribution, OCI]
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
  - id: src-images-r2
    resource: /concepts/04-images.md
    title: 镜像管理与 Rich 进度条构建（R2 基线）
---

# 07 - Secret / Manifest / Registry：密钥与多架构镜像分发

本文覆盖镜像从"本地资源"走向"分发制品"链路上的三个小契约：**Secret**（交给守护进程托管的敏感字节）、**Manifest**（多架构清单列表）、**RegistryData**（镜像的仓库平台元数据），并补齐 R2 镜像文档未覆盖的 push/load/prune 三个分发面语义陷阱。

## 7.1 Secret：裸字节上送的密钥资源

模型与管理器同居 [secrets.py](https://github.com/containers/podman-py/blob/v5.8.0/podman/domain/secrets.py)（111 行）。

```python
with open("db_password.txt", "rb") as f:
    secret = client.secrets.create("db_pwd", f.read(), driver=None)
# POST /secrets/create?name=db_pwd&driver=None
# 请求体 = 原始字节（不是 JSON！）；响应 {"ID": ...} 后立即 get 回完整 Secret
```

身份与端点契约（与其他资源全不同）：

| 要点 | 实际行为 |
|------|---------|
| `Secret.id` | `attrs["ID"]`（大写） |
| `Secret.name` | **`attrs["Spec"]["Name"]`**（嵌在 Spec 里，缺失时 suppress KeyError 返回 `""`） |
| `__repr__` | 用 name 而非 short_id 展示 |
| `exists(key)` | 没有独立 exists 端点，**借用 `GET /secrets/{key}/json` 的 `response.ok`** 判定 |
| `get/list` | `GET /secrets/{id}/json`、`GET /secrets/json`；list 的 filters 参数被忽略 |
| `create` 参数 | `name`、`data: bytes`、`labels`（**接收但忽略**）、`driver`；name/driver 走 query string，data 裸字节作 body |
| `remove(secret_id, all=None)` | `DELETE /secrets/{id}?all=`；实例方法 `Secret.remove(all=None)` 委托管理器 |

> 注意 `SecretsManager` 与 `SystemManager` 都显式定义了单参 `__init__(self, client)`（不经基类的 podman_client 形参）；区别是 SecretsManager 内调 `super().__init__(client)`，SystemManager 直接 `self.client = client`。此外 `secrets` 是门面上唯一**无返回类型注解**的 `@cached_property`。

## 7.2 Manifest：多架构清单列表

[manifests.py](https://github.com/containers/podman-py/blob/v5.8.0/podman/domain/manifests.py)（205 行）封装 OCI/Docker manifest list：一个"逻辑镜像名"指向多张按 os/arch/variant 区分的实体镜像。

### 7.2.1 身份模型

- `Manifest.id`：`attrs["manifests"][0]["digest"]`，并剥除 `sha256:` 前缀；解析失败（KeyError/TypeError/IndexError）回退到 `name`。
- `Manifest.name`：读 `attrs.get("names")`——注意这是一个**列表字段**而非字符串；`names` 属性是其别名。
- 所有出现在 URL 中的 name 都经 `urllib.parse.quote_plus`（`quoted_name` 属性），因为镜像名含 `/` 与 `:`。
- `media_type` ↔ `attrs["mediaType"]`；`version` ↔ `attrs["schemaVersion"]`。

### 7.2.2 管理器操作

```python
# 创建：images 可传 Image 实例（取 attrs["RepoTags"][0]）或字符串
m = client.manifests.create("quay.io/me/app:multi",
                            images=["quay.io/me/app:amd64", "quay.io/me/app:arm64"])
# POST /manifests/{quote(name)}?images=...&all=...
# get 回对象后手动补 attrs["names"]=name；attrs["manifests"] 为 None 时置 []

# 增删条目：PUT 同一端点，用 body 的 operation 字段区分
m.add(["quay.io/me/app:ppc64le"], arch="ppc64le", os="linux")
# body {"operation": "update", "images": [...], "all","annotation","arch","features","os","os_version","variant"}
m.remove("quay.io/me/app:amd64@sha256:abcd...")   # 含 @ 时自动切出 digest 段
# body {"operation": "remove", "images": [digest]}；两者执行后都 self.reload()

# 推送到仓库
m.push("quay.io/me/app:multi", all=True,
       auth_config={"username": u, "password": p})
# POST /manifests/{name}/registry/{quote(destination)}?all=&destination=
# X-Registry-Auth 头 = base64url(json(auth_config))，无 auth_config 时给空串
```

错误映射上，add/remove/create/push 的 `raise_for_status(not_found=ImageNotFound)` 把 404 映射为镜像未找到异常。

### 7.2.3 两个硬边界

1. **`ManifestsManager.list()` 直接 `raise NotImplementedError`**——libpod 服务端不支持清单列举，没有"列出所有 manifest"的 API。枚举只能靠外部自行登记名称。
2. 管理器级 `remove(name)` 是 `DELETE /manifests/{name}`（name 列表直接拼路径），返回服务端 body 并追加 `ExitCode=<HTTP 状态码>`；`exists(key)` 内部也先 quote_plus。

## 7.3 RegistryData：镜像的平台元数据

[registry_data.py](https://github.com/containers/podman-py/blob/v5.8.0/podman/domain/registry_data.py) 的 `RegistryData(PodmanResource)` 由 `client.images.get_registry_data(name)` 构造（兼容性方法；`auth_config` 参数当前**不参与请求**，源码留 FIXME）。构造时若未显式给 attrs，则以 `manager.get(image_name).attrs` 填充。

两个方法：

- `pull(platform=None)`：按镜像名解析 repository，调用 `manager.pull(repository, tag=self.id, platform=platform)`。
- `has_platform(platform)`：判定镜像 attrs 是否覆盖目标平台。
  - 字符串形式 `os[/arch[/variant]]`：按 `/` 切分，段数非法（`1 < len > 3` 的边界条件）抛 `InvalidArgument`；
  - 字典形式须含 `os` 与 `architecture`，缺失时用 `client.version()` 返回的 `Os`/`Arch` 补当前平台默认值；
  - 最终只比较 `attrs["Os"]` 与 `attrs["Architecture"]`——**variant 虽然能传入，但 libpod attrs 不承载该字段，不参与判定**。

## 7.4 分发面的三个语义陷阱（ImagesManager）

### 7.4.1 push 的进度消息是客户端合成的

`push(repository, tag=None, stream=False, decode=False, auth_config=None, destination=None, ...)` 完成 HTTP POST（`/images/{quote(name)}/push`，404 映射 ImageNotFound）后，**并不迭代服务端响应体**：返回的进度内容是客户端本地构造的固定两条 dict：

```python
[{"status": "Pushing repository {repository} ({0 或 1} tags)"},
 {"status": "Pushing", "progressDetail": {}, "id": repository}]
```

`stream=True` 只是把这两条合成消息变成生成器（`decode=True` 出 dict，否则出 JSON 字符串）；非流式则拼成一个字符串返回。**结论：推送是否成功只能靠是否抛异常判断，不要把返回内容当作真实仓库进度或 digest 回执。**

### 7.4.2 load 返回的是生成器，且 data/file_path 互斥

`load(data=None, file_path=None)` → POST `/images/load`（application/x-tar）：两者皆无或皆有都抛 `PodmanError`。方法内部定义嵌套生成器 `_generator`（遍历响应 `body["Names"]` 逐个 `self.get()`）并显式 `return` 它——因此**调用得到的是生成器对象，不迭代就不会产出 Image**：

```python
images = list(client.images.load(file_path="batch.tar"))   # 必须消费
```

对应反方向 `Image.save(named=False)`：GET `/images/{img}/get?format=docker-archive`，返回 iter_content（默认 2 MiB 分块）；`named="sometag"` 时该标签必须在 `image.tags` 中，否则 `InvalidArgument`。

### 7.4.3 prune 要防服务端 JSON null

`prune(all=False, external=False, filters=None)` 的服务端响应在没有可删镜像时可能是 JSON `null`，直接迭代会触发 `TypeError: 'NoneType' object is not iterable`——源码以 `if response.json() is not None` 显式防护，多个元素的 `Err` 被聚合成一个分号分隔字符串后**一次性**抛 APIError。`prune_builds()` 更彻底：**完全不发请求**，本地返回 `{"CachesDeleted": [], "SpaceReclaimed": 0}`。

## 7.5 分发面 API 速查

| 操作 | 入口 | HTTP / 形态 | 注意 |
|------|------|-------------|------|
| 创建密钥 | `secrets.create(name, data:bytes, driver=None)` | POST `/secrets/create`，裸字节 body | labels 忽略 |
| 多架构清单 | `manifests.create(name, images)` | POST `/manifests/{name}` | 无 list |
| 清单增删 | `Manifest.add/remove` | PUT，operation=update/remove | 自动 reload |
| 清单推送 | `Manifest.push(dest, auth_config=...)` | POST `.../registry/{dest}` | X-Registry-Auth |
| 平台判定 | `RegistryData.has_platform` | 本地比较 Os/Architecture | variant 不生效 |
| 镜像推送 | `images.push` | POST `/images/{name}/push` | 进度为本地合成 |
| 镜像载入 | `images.load(data|file_path)` | POST `/images/load` | 返回生成器，需消费 |
| 镜像导出 | `Image.save(named=...)` | GET `/images/{img}/get?format=docker-archive` | named 标签须存在 |
| 缓存清理 | `images.prune_builds()` | **不发请求** | 固定空结果 |

## 相关概念

- [04 - 镜像管理与 Rich 进度条构建](04-images.md)：pull 四策略、build 与 Rich 进度条（本文的推送侧对照）
- [06 - Pod / Network / Volume](06-pods-networks-volumes.md)：另两类 libpod 小契约资源
- [08 - 事件与三套流协议](08-events-and-streams.md)：pull 进度流的 chunked 解析机制
- [09 - 构建上下文管线](09-build-context-pipeline.md)：多架构清单参数 `manifest=` 如何进入 /build
- [信源登记：vendor 全量源码地图](/references/source-code-map.md)
