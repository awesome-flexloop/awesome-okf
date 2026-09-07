---
type: concept
title: 04 - 镜像管理与 Rich 进度条构建
description: ImagesManager 查询/拉取/推送/构建/删除镜像；pull policy 四策略；Rich progress 降级与 BuildError 处理；Containerfile 命名与 build 20+ 参数；tag/login/scp 跨主机
tags: [podman-py, images-manager, rich-progress, builderror, pull-policy, containerfile]
generated:
  by: process:seven-concepts/sc-20260907-podman-py/e-phase
  at: 2026-09-07
verified:
  by: human:xinzo
  at: 2026-09-07
status: stable
stale_after: 2027-09-07
sources:
  - id: src-images-manager
    resource: external/dao/action/Containers/podman-py/podman/domain/images_manager.py
    title: ImagesManager 源码 — list/get/exists/pull/push/build/remove/prune/load/save/scp
  - id: src-images-build
    resource: external/dao/action/Containers/podman-py/podman/domain/images_build.py
    title: BuildMixin.build 源码 — Containerfile 20+ kwargs + BuildError 抛出
  - id: src-api-client
    resource: external/dao/action/Containers/podman-py/podman/api/client.py
    title: APIClient 源码 — requests.Session 继承 + stream/iter_lines 语义
---

# 04 - 镜像管理与 Rich 进度条构建

## 4.1 ImagesManager 继承链与职责

```
BuildMixin    Manager
   └──┬────────┬──┘
      └────────┘
    ImagesManager
      ├── exists(name) → bool    (HEAD /images/{name}/exists)
      ├── list(name,all,filters) → list[Image]  (GET /images/json)
      ├── get(name) → Image      (404→ImageNotFound)
      ├── get_registry_data(name, auth_config) → RegistryData
      ├── pull(repo,tag,all_tags,**) → Image|list|Generator
      ├── push(repo,tag,**) → str|Iterator     (X-Registry-Auth)
      ├── search(term,**) → list[dict]         (stars/is-official/limit)
      ├── build(**kwargs) → (Image, Iterator[bytes])  (BuildMixin)
      ├── remove(image,force,noprune) → list[dict]    (Deleted/Untagged/Errors/ExitCode)
      ├── prune(all,external,filters) → {ImagesDeleted, SpaceReclaimed}
      ├── prune_builds() → {CachesDeleted:[], SpaceReclaimed:0}  (空壳兼容)
      ├── load(data|file_path) → Generator[Image]  (二选一参数校验)
      └── scp(source,dest,quiet) → str         (跨主机镜像复制)
```

## 4.2 查询三件套：list/get/exists + reference 过滤

| 方法 | 核心参数 | 返回 | 异常语义 | 与 docker-py 差异 |
|---|---|---|---|---|
| `exists(name)` | 镜像名或 ID | `bool` | `APIError` 服务端错误 | Podman 新增 |
| `get(name)` | name (已 URL quote_plus) | `Image` | **`ImageNotFound`** (404)、`APIError` | 签名一致，异常子类多 ImageNotFound |
| `list(**kwargs)` | name / all / filters={dangling,label} | `list[Image]`，404→`[]` 空列表 | `APIError` | **`name→reference` 映射**(L67)：name 参数自动转成 filters["reference"] |

> **G2 洞察四元组 #3：隐式字段名映射陷阱**
> docker-py 的 `images.list(name="postgres:16")` 直接走 name 参数；而 podman-py [images_manager.py#L67-68](https://github.com/containers/podman-py/blob/main/podman/domain/images_manager.py#L67-L68) 实际把 `name` 重写为 `filters["reference"]`。当你已经写了 `filters={"reference":"..."}` 又同时传 `name` 时，后者**覆盖**前者，导致过滤失效。
> **修复决策**：要么传 `name`，要么传 `filters={"reference":...}`，绝不同时传两个。

## 4.3 pull 四策略 + Rich Progress 优雅降级

`images.pull()` 有三条控制流分支，核心参数：
- **policy** (L361)：`always`(默认) / `missing` / `never` / `newer` — 对应 OCI 分发规范四种拉取策略
- **all_tags=True**：拉全部 tag，`params["allTags"]=True`
- **platform="linux/amd64/v3"**：拆成 `OS/Arch/Variant` 三段，tokens 长度 1~3

### 4.3.1 Rich Progress Bar 生命周期

```python
try:
    from rich.progress import Progress, TextColumn, BarColumn, \
        TaskProgressColumn, TimeRemainingColumn
except ImportError:
    Progress = None              # 降级：不启用 progress_bar

# pull(progress_bar=True) 时的硬约束
if progress_bar:
    if Progress is None:
        raise ModuleNotFoundError("progress_bar requires 'rich.progress' module")
    params["compatMode"] = True   # 必须走 docker-compat 端点
    stream = True                 # 必须流式输出
```

进度渲染逻辑 [images_manager.py#L401-L461](https://github.com/containers/podman-py/blob/main/podman/domain/images_manager.py#L401-L461)：
1. `Progress(TextColumn + BarColumn + TaskProgressColumn + TimeRemainingColumn)` 构建
2. `response.iter_lines()` 迭代拉取事件流
3. `status=="Downloading"` → `add_task(description, total=progressDetail.total)`
4. `status=="Download complete"` → 强制 `update(..., total=100, completed=100)`（处理"小块直接下载完"乱序事件）
5. 小图层（<几 KB）可能跳过 Downloading 直接到 complete → `add_task(..., total=100, completed=100)` 兜底

> **反模式：安装 `pip install podman` 却期望 progress_bar=True 能用**
> 默认 extras 不含 `rich`。正确命令：
> ```bash
> pip install 'podman[progress]'  # 或 pip install podman rich
> ```

## 4.4 BuildMixin.build：Containerfile 20+ 参数速查

**命名**：参数名仍叫 `dockerfile=`，但实际值**可以是 `Containerfile` 路径**（这是 podman-py 对 Docker SDK 兼容的刻意保留）。

高频参数清单 [images_build.py#L29-L73](https://github.com/containers/podman-py/blob/main/podman/domain/images_build.py#L29-L73)：

| 参数 | 类型 | 作用 | Podman-only 标注 |
|---|---|---|---|
| `path` | str | 构建上下文目录 | |
| `fileobj` | IO | tarball 上下文（与 path 二选一） | |
| `dockerfile` | str | Containerfile/Dockerfile 相对或绝对路径 | |
| `tag` | str | 最终镜像 tag `name:tag` | |
| `buildargs` | `dict[str,str]` | `--build-arg` 字典 | |
| `labels` | `dict[str,str]` | 镜像标签 | |
| `target` | str | 多阶段构建目标 stage 名 | |
| `pull` | bool | 拉取 FROM 镜像更新 | |
| `nocache` | bool | 禁用构建缓存 | |
| `squash` | bool | 所有层 squash 为单层 | |
| `platform` | str | `os/arch/variant` | |
| `secrets` | `list[str]` | build 时暴露的 secret 文件/环境变量 | ✅ Podman only |
| `http_proxy` | bool | 注入 HTTP_PROXY 等变量进构建容器 | ✅ Podman only |
| `layers` | bool | 缓存中间层，默认 `True` | ✅ Podman only |
| `manifest` | str | 构建后加入指定 manifest list | ✅ Podman only |
| `outputformat` | str | 默认 `application/vnd.oci.image.manifest.v1+json` (OCI) | ✅ Podman only |
| `container_limits.memory` / `memswap` / `cpushares` / `cpusetcpus` / `cpuperiod` / `cpuquota` | int/str | CFS 调度限制 | 最后两个 ✅ Podman only |

### 4.4.1 BuildError 捕获与 build_log 留存

```python
from podman.errors import BuildError, APIError

try:
    image, build_logs = client.images.build(
        path="./myapp",
        dockerfile="Containerfile",   # 可以不是 Dockerfile
        tag="myapp:v1",
        buildargs={"PY_VER": "3.14"},
        secrets=["/run/secrets/token"],
    )
except BuildError as e:
    print(f"Build 失败原因: {e.msg}")
    print("--- build log 最后 20 行 ---")
    logs = list(e.build_log)          # Iterable[str] 需转 list 消费
    for line in logs[-20:]:
        print(line)
except APIError as e:
    # HTTP 层错误（e.g. 无权限 / daemon 挂掉）
    print(f"HTTP {e.status_code}: {e.explanation}")
```

> **G3 可迁移模式：构建失败诊断三部曲**
> - **触发场景**：`images.build()` 抛异常 CI 日志只有一行 "Build failed"
> - **核心步骤**：① 捕获 BuildError → ② 消费 `e.build_log` 持久化到 artifact → ③ 若不是 BuildError 而是 APIError 则看 `e.status_code` + `e.explanation`
> - **反模式**：只 `except Exception` 吞掉 build_log 细节，导致"相同代码本地过 CI 挂"无法定位。

## 4.5 push/remove/prune/search/scp 关键语义

### 4.5.1 push：X-Registry-Auth header
`push(auth_config={"username":"u","password":"p"})` 时，SDK 会把字典 base64url 编码后塞入 `X-Registry-Auth` header（不是 Basic Auth）。私有仓库认证失败时需检查：
- auth_config 键名是 `username` + `password`（不是 `user`/`pass`）
- `tlsVerify=False` 仅对自签证书仓库设置（⚠️ 生产禁用）

### 4.5.2 remove 返回结构
返回 `list[dict]`，每个元素只有一个 key：`{"Deleted":id}` / `{"Untagged":ref}` / `{"Errors":msg}` / `{"ExitCode":0}`。
不是 docker-py 里合并后的单 dict。统计被删 ID 时需遍历提取。

### 4.5.3 prune 空响应修复
`images.prune()` 返回 `ImagesDeleted` 列表。libpod API 在没删除任何东西时返回 **`null`**（不是空数组），SDK 在 [images_manager.py#L203-L216](https://github.com/containers/podman-py/blob/main/podman/domain/images_manager.py#L203-L216) 用 `if response.json() is not None` 修复这个行为差异——这是对 libpod 的隐式兼容，用户无感知。

### 4.5.4 scp 跨主机
`images.scp(source, dest, quiet)` 对应 `podman image scp` CLI。
- source/dest 格式：`[connection@]image`，如 `prod-user@10.0.0.5::myapp:v1`
- 需要两端 Podman ≥5.0 且连接配置（`containers.conf connection`）已就绪

## 4.6 load/save：tarball 往返

`load()` 严格校验：**只能二选一**传 `data:bytes` 或 `file_path:os.PathLike`，两个都传或都不传都抛 `PodmanError`。
Content-Type 固定 `application/x-tar`。

```python
# 保存 → 加载（跨主机迁移镜像时替代 scp 的备选）
with open("myapp_v1.tar", "rb") as f:
    images = list(client.images.load(file_path=f))
print(f"加载完成 {len(images)} 个镜像: {[i.tags for i in images]}")
```

## 4.7 本节陷阱清单（R3 + R6 工程治理延伸）

| 陷阱编号 | 现象 | 根因 | 修复 |
|---|---|---|---|
| IMG-1 | `pip install podman` 后 pull(progress_bar=True) 抛 `ModuleNotFoundError` | 默认 extras 不含 `rich` | `pip install 'podman[progress]'` |
| IMG-2 | `list(name=X, filters={"reference":Y})` Y 被忽略 | name→reference 覆盖 | 二选一，不要同时传 |
| IMG-3 | `build(dockerfile="Containerfile")` 报找不到文件 | path + dockerfile 相对路径拼接错 | dockerfile 传相对 path 的路径，或传绝对路径 |
| IMG-4 | BuildError 被吞，日志里看不到构建详情 | 裸 `except Exception` | 先 `except BuildError` 消费 `e.build_log` |
| IMG-5 | `remove(force=True)` 后仍返回 `ExitCode!=0` | 镜像被多个 tag 引用，只 untag 没 delete | 先查 `len(image.tags)>1`，每个 tag 单独 untag 再 remove |
| IMG-6 | `load(data=tar_bytes, file_path=...)` 二传二 | 从迁移脚本抄漏参数 | 严格只传一个，tar 内容小用 data，大文件用 file_path |
| IMG-7 | `push(tlsVerify=False)` 到生产 | 自签证书调试代码漏删 | 生产必须走 CA 签名证书或 auth_config |
