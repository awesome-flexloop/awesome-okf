---
type: Concept
title: 00 - Docker SDK 兼容性与三层代码架构
description: Docker SDK 对齐设计、DockerClient 别名、DOCKER_HOST/CONTAINER_HOST 双前缀6环境变量、薄门面 PodmanClient、三层架构（门面→domain Manager+Mixin→api 传输）、核心依赖图谱、Swarm 不支持边界
tags: [Docker Compat, PodmanClient, Thin Facade, 三层架构, requests, Python 3.9+]
generated:
  by: method_orchestrator/seven-concepts-cmd
  at: 2026-09-07T00:00:00Z
verified:
  by: process:podman-py-grep-20260907
  at: 2026-09-07T00:00:00Z
status: stable
stale_after: 2027-09-07
sources:
  - id: src-pp-client
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/client.py
    title: PodmanClient.__init__ / from_env / 9 cached_property Manager
  - id: src-pp-init
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/__init__.py
    title: __version__ / __compatible_version__ / DockerClient 别名
  - id: src-pp-pyproject
    resource: ../../../../../external/dao/action/Containers/podman-py/pyproject.toml
    title: requires-python >=3.9 / dependencies / extras
  - id: src-pp-readme
    resource: ../../../../../external/dao/action/Containers/podman-py/README.md
    title: PyPI 包名 podman / 基础示例代码
---

# 00 - Docker SDK 兼容性与三层代码架构

## 1. 定位与安装

podman-py（PyPI 包名 **`podman`**）是 Podman 项目官方维护的 Python 绑定库，目标是**对齐 docker-py（现 docker SDK for Python）API 签名**，让已有 Docker 自动化脚本以**最小改动**迁移到 Podman daemonless 引擎上。最低要求：**Python ≥ 3.9**（见 `pyproject.toml` requires-python）。

```bash
pip install podman                      # 最小安装（requests + urllib3 + tomli）
pip install "podman[progress_bar]"      # + rich 进度条（images.pull/build 默认用 Rich 渲染）
pip install "podman[test]"              # + pytest/coverage/tox/requests-mock（开发）
pip install "podman[docs]"              # + Sphinx + sphinx-apidoc（生成 API 文档）
```

## 2. Docker SDK 兼容三要素

开发者将 `docker` → `podman` 迁移时，三层兼容机制依次生效：

| 兼容层级 | 源码位置 | 作用 | 限制 |
|---|---|---|---|
| **① 别名导入** | `podman/__init__.py`: `DockerClient = PodmanClient` + 可选 `import podman as docker` | 脚本第一行即可零改动 `from docker import DockerClient` → 替换为 `from podman import DockerClient`；现有 `docker.from_env()` 直接变 `podman.from_env()` | **`docker.types.*` 子模块不存在**（podman-py 不提供独立类型对象，用 Mapping/kwargs 传参） |
| **② 环境变量双前缀** | `PodmanClient.from_env()`（L90-L119 `client.py`）：同时读取 DOCKER_* 与 CONTAINER_* 6个变量，后者优先 | `DOCKER_HOST / DOCKER_TLS_VERIFY / DOCKER_CERT_PATH` 无需改名即可识别；Podman 原生 `CONTAINER_HOST / CONTAINER_TLS_VERIFY / CONTAINER_CERT_PATH` 优先级更高覆盖前者 | TLS 仅对 tcp://https:// 生效，UDS/SSH 不走 TLS |
| **③ Manager 方法签名对齐** | `podman/domain/*_manager.py`（ContainersManager/ImagesManager/NetworksManager 等） | `client.containers.run(image, detach=True, remove=True, ports={'80/tcp': 8080})` 与 docker-py **完全相同**；`get/list/create/prune` 返回 Container/Image/PodmanResource 对象，属性 `id/name/status/attrs` 一致 | `containers.list()` sparse 默认值差异（Libpod True → Docker False）；Swarm 相关 services/configs/nodes 返回 NotImplementedError |

最小迁移示例（实际修改 ≤ 3行）：

```python
# 迁移前：docker-py
from docker import DockerClient
client = DockerClient(base_url="unix:///var/run/docker.sock")

# 迁移后：podman-py
from podman import DockerClient  # ①别名导入：DockerClient=PodmanClient
client = DockerClient(
    base_url="unix:///run/user/1000/podman/podman.sock"  # ②socket路径：rootless改UID；或 from_env() 走环境变量双前缀
)

with client:  # ③上下文管理器：podman-py 原生支持 AbstractContextManager
    print(client.version()["Version"])
    client.containers.run("docker.io/library/alpine:3.20", ["echo", "hello"], remove=True)
```

## 3. 三层代码架构（薄门面 → Manager + Mixin → 传输层）

podman-py 约 12k 行代码按「分层调用」组织，每层单一职责，与 Podman Go 引擎的 cmd→domain→libpod 分层形成**镜像对应**：

```
[调用者 your_script.py]
        │
        ▼
┌─────────────────────────────────────────── 1) 薄门面 PodmanClient（client.py ~110行）──┐
│  @cached_property containers/images/networks/volumes/pods/secrets/manifests/system/    │
│                    quadlets  ← 懒加载9个 Manager                                        │
│  直接方法：df()  ping()  version()  info()  events()    login()  close()  __enter__/exit│
│  兼容别名：DockerClient = PodmanClient ; swarm/services/configs/nodes → NotImplementedErr│
└─────────────────────────────────┬───────────────────────────────────────────────────────┘
                                  │ 参数、返回对象包装
                                  ▼
┌───────────────────────────────── 2) 领域层 domain/（~60% 代码量）─────────────────────┐
│  Manager 基类（manager.py）：                                                           │
│    list()/get()/exists() → 调 self.api.get/post；prepare_model(attrs=resp.json())      │
│    → 组装具体 PodmanResource（Container/Image/Volume 等）对象                          │
│                                                                                        │
│  Mixin 语义扩展（横切复用）：                                                          │
│    RunMixin  → run(image, detach/stream/remove/auto_remove)   [仅 ContainersManager]   │
│    CreateMixin→ create(** ~30参数→/libpod/containers/create) [仅 ContainersManager]   │
│    BuildMixin → build(path,containerfile,buildargs,stream)   [仅 ImagesManager]       │
│                                                                                        │
│  具体 Manager（10 个）：                                                                │
│    containers_run.py containers_create.py containers_manager.py                        │
│    images_build.py images_manager.py   quadlets.py  pods_manager.py  networks_manager  │
│    volumes.py  secrets.py  manifests.py  events.py  system.py  config.py(PodmanConfig)│
└─────────────────────────────────┬───────────────────────────────────────────────────────┘
                                  │ HTTP 请求构造、错误码映射
                                  ▼
┌───────────────────────────────── 3) 传输适配层 api/（~30% 代码量）────────────────────┐
│  APIClient（api/client.py ~240行）：继承 requests.Session，加 Podman API 版本前缀       │
│    supported_schemes = ["unix","http+unix","ssh","http+ssh","tcp","http"]  (6方案)     │
│    delete/get/head/post/put → 加 /v{version}/libpod 或 /v{version}/（兼容）URL前缀    │
│    调 self.send() → 按 scheme 选择 Adapter → 发实际请求                                │
│                                                                                        │
│  传输 Adapter：                                                                         │
│    UDSAdapter   → podman/api/uds.py  ─────────┐                                        │
│    SSHAdapter   → podman/api/ssh.py  shell ssh│ requests.Session HTTP 语义统一        │
│    HTTPAdapter  → requests.adapters.HTTPAdapter (tcp/http)┘                           │
│                                                                                        │
│  工具函数导出（podman/api/__init__.py re-export）：                                     │
│    create_tar() → 本地目录→上传tar  prepare_filters() → 类型encode                     │
│    encode_auth_header()  parse_utils  path_utils(get_runtime_dir)  output_utils        │
└─────────────────────────────────┬───────────────────────────────────────────────────────┘
                                  │
                                  ▼
[Podman (libpod) REST API / UDS / SSH Tunnel → libpod service 响应 JSON]
```

**架构洞察（反模式标注，与 I 阶段 G2 洞察呼应）**：

* ✅ **薄门面模式（推荐）**：PodmanClient 仅 110 行，不直接调用 HTTP，所有业务逻辑下推到 domain/ → 修改 Manager 不会影响门面接口，Docker 兼容签名稳定；新资源类型只需加 `@cached_property xxx_manager` + Manager 类，保持 100% 向后兼容。
* ❌ **厚门面反模式**（历史上 podman-py v3 踩过坑）：若把 containers.run() 实现放 client.py，后续每次 API drift 都要改门面文件，容易引入回归；v4 重写后完全消除此模式。
* ⚠️ **Manager + Mixin 组合注意点**：`containers.run()` 实际代码在 `domain/containers_run.py` RunMixin，不在 `containers_manager.py` —— 查源码前先确认继承树，不要盲 grep 文件名。

## 4. 不支持边界（迁移前必查清单）

| 能力 | docker-py | podman-py | 建议替代 |
|---|---|---|---|
| Swarm orchestration（services/tasks/configs/nodes/secrets external） | ✅ | ❌（返回 NotImplementedError / 抛异常） | Podman 用 Pod（pods_manager）替代单容器 Service，或 K8s YAML |
| BuildKit buildx 多平台构建 | ✅ buildx 子模块 | ❌（build() 走 buildah 后端，不支持 BuildKit --sbom/--provenance） | buildah 多平台 manifest+push，或 quadlets 混合构建 |
| `docker.types.*` 对象（HostConfig/EndpointSpec/ContainerSpec） | ✅ 类对象 | ❌（仅接受 dict/Mapping，不做 Python 类型封装） | 直接传 **kwargs dict，按 libpod API 字段名 |
| Windows 命名管道 `npipe:////./pipe/docker_engine` | ✅ | ❌（仅 unix/tcp/ssh；Windows 用 WSL2 + unix:///mnt/wsl/.../podman.sock 或 tcp://） | 见 01-connection「Windows 推荐路径」 |
| `client.plugins.*` / `client.secrets.*`（Docker Swarm secrets） | ✅ | ✅（podman secrets_manager 有 CRUD，但语义是 Podman 本地 secret，非 Swarm 全局） | 迁移前评估使用场景 |
| `.docker/config.json` 完全一致性 | ✅ | 🟡（login() 读写 `~/.config/containers/auth.json`，兼容格式但路径不同；from_env() 可识别两者） | 用 `podman login` 一次性同步即可 |

## 5. 版本号双轨（与 Docker SDK 协议版本兼容）

`podman/version.py` 定义两个独立版本（不要混淆）：

* `podman.__version__` → **podman-py 自身版本**，如 `5.8.0`（对应 Podman 引擎 v5.8.x 功能范围）
* `podman.__compatible_version__` → **Docker API 兼容版本号**，如 `1.40` → 即兼容到 Docker Engine 19.03 时代的 API 契约；发请求时 `/v1.40/libpod/...` 和 `/v1.40/containers/json`（兼容端点）双 URL 都可访问

本知识包所有接口说明均基于 **podman-py ≥ v5.8.0（Podman libpod API ≥ 5.8） / compatible_version ≥ 1.40**。
