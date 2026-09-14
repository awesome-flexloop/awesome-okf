---
type: Reference
title: podman-py vendor 全量源码信源登记（R3）
description: vendor/podman-py 子模块在 v5.8.0-9-g5dd81b4 快照上的版本固定、39 文件结构地图、核心符号索引与资源端点差异表，供第 3 轮概念文档溯源
tags: [podman-py, source-code, reference, vendor, architecture, v5.8.0]
generated: { by: "source-code-to-okf-wiki/sc-20260914-podman-py-wiki", at: "2026-09-14" }
verified: { by: "process:seven-concepts-v", at: "2026-09-14" }
status: stable
stale_after: 2027-09-14
sources:
  - id: source-code-r3
    resource: /references/source-code-map.md
    title: podman-py vendor 全量源码信源登记（commit 5dd81b4）
---

# podman-py vendor 全量源码信源登记（R3）

本文件登记第 3 轮扩展所依据的 **vendor 稳定信源**：SpecWeave 通过 git submodule 固定的 containers/podman-py 源码树。本轮概念文档（06-10）与示例 04 中涉及内部实现（类名、方法签名、端点路径、行号、控制流）的陈述，均以本信源为准。前两轮信源（[readme-source](readme-source.md)、[client-source](client-source.md)、[api-source](api-source.md)）基于 `external/dao/...` 路径快照，本轮起新增内容一律锚定 vendor 稳定路径。

## 版本固定

| 项目 | 值 |
|------|-----|
| 子模块路径（SpecWeave 内） | `vendor/podman-py/`（third_party，gitlink pin，只读引用） |
| 上游仓库 | `git@github.com:containers/podman-py.git`（[containers/podman-py](https://github.com/containers/podman-py)，Apache-2.0） |
| Git 描述 | `v5.8.0-9-g5dd81b4`（v5.8.0 标签之后 9 个提交） |
| 固定 commit | `5dd81b49f35733a27b8051c47e23d3b4c85ea716` |
| 提交日期 | 2026-08-19（合并 PR #651） |
| 包内版本号 | `__version__ = "5.8.0"`、`__compatible_version__ = "1.40"`（`podman/version.py`） |
| API 版本常量 | `VERSION="5.8.0"`（libpod 前缀 `/v5.8.0/libpod/`）、`COMPATIBLE_VERSION="1.4"`（兼容前缀 `/v1.4/`） |
| 代码规模（不含测试） | **39 个 Python 文件 / 6078 行**：api 层 11 文件 1209 行、domain 层 22 文件 4455 行、errors 2 文件 197 行、包顶层 4 文件 217 行 |
| 测试规模 | `podman/tests/`：unit 26 个 test_*.py、integration 11 个 test_*.py（另含 conftest.py、errors.py、utils.py 及两个包 __init__） |

> 版本固定纪律：文档中的签名、端点与行号均对应 commit `5dd81b4` 快照；上游重构后需重新核验。计数经文件系统独立统计（非目测）：分层行数与文件数经 `Get-ChildItem + Measure-Object` 复核，测试文件数经 Glob 复核（unit 26 / integration 11）。

## 源码结构地图（39 文件，行数为该快照实测）

### 包顶层（4 文件 / 217 行）

| 文件 | 行数 | 职责 |
|------|------|------|
| `podman/__init__.py` | 5 | 仅导出 `PodmanClient`、`from_env`、`__version__` |
| `podman/client.py` | 189 | `PodmanClient` 薄门面（AbstractContextManager）：四级连接解析、9 个 cached_property 管理器、7 个 system 直方法、Swarm 拒绝、`DockerClient` 别名 |
| `podman/tlsconfig.py` | 20 | `TLSConfig` 兼容空壳（当前被忽略，configure_client 为 no-op） |
| `podman/version.py` | 3 | `__version__` / `__compatible_version__` 双版本 |

### api 传输层（11 文件 / 1209 行）

| 文件 | 行数 | 职责 |
|------|------|------|
| `api/client.py` | 394 | `APIClient(requests.Session)` + `APIResponse` 代理：scheme 规范化、三适配器挂载、libpod/兼容双前缀、五 HTTP 方法、404 异常类可参数化 |
| `api/ssh.py` | 233 | `SSHAdapter` / `SSHSocket`：shell-out `ssh -N -L` 本地隧道（前轮 S-1~S-8 已登记） |
| `api/uds.py` | 138 | UDS 四件套：`UDSSocket`→`UDSConnection`→`UDSConnectionPool`→`UDSAdapter`；http 与 http+ssh 两 scheme 共用池 |
| `api/tar_utils.py` | 100 | 构建上下文打包：ignore 解析、Containerfile 代理拷贝、去身份化 tar |
| `api/parse_utils.py` | 89 | 镜像名/时间戳/CIDR 解析 + 帧协议：`frames` / `stream_frames` / `stream_helper` |
| `api/http_utils.py` | 84 | `prepare_filters`（三态入参）、`prepare_body`（递归剔空保 False）、`encode_auth_header` |
| `api/output_utils.py` | 40 | `demux_output`：8 字节帧头多路复用 stdout/stderr 拆分 |
| `api/path_utils.py` | 45 | XDG 运行时/配置目录解析，含 0700 防 symlink 回退目录 |
| `api/adapter_utils.py` | 39 | `_key_normalizer`（复制自 urllib3，连接池键规范化） |
| `api/__init__.py` | 35 | 17 符号导出（`__all__`）+ `DEFAULT_CHUNK_SIZE = 2 MiB` |
| `api/api_versions.py` | 12 | release 字符串 → API 版本常量 |

### domain 领域层（22 文件 / 4455 行）

| 文件 | 行数 | 模型 / 管理器 |
|------|------|---------------|
| `domain/containers_create.py` | 804 | CreateMixin：容器创建 kwargs 模型（前轮已覆盖） |
| `domain/containers.py` | 693 | `Container` 资源：状态机操作、exec/logs/stats/top/wait/archive/commit，attach 未实现 |
| `domain/images_manager.py` | 503 | `ImagesManager(BuildMixin, Manager)`：pull/push/build/load/scp/prune 与 Rich 进度 |
| `domain/quadlets.py` | 326 | Quadlet/QuadletsManager（v5.8，前轮 Q-1~Q-11 已覆盖） |
| `domain/manifests.py` | 205 | `Manifest` / `ManifestsManager`：多架构清单 add/push/remove，list 不支持 |
| `domain/images_build.py` | 188 | `BuildMixin.build` + `_render_params` |
| `domain/volumes.py` | 175 | `Volume` / `VolumesManager`（同文件）：CRUD、prune、export/import archive |
| `domain/networks_manager.py` | 165 | `NetworksManager`：create 的 snake/Pascal 键映射、IPAM→subnets 转换 |
| `domain/config.py` | 147 | `PodmanConfig` / `ServiceConnection`：新旧双格式连接配置 |
| `domain/containers_manager.py` | 141 | `ContainersManager(RunMixin, CreateMixin, Manager)`（前轮已覆盖） |
| `domain/manager.py` | 137 | `PodmanResource` / `Manager` 双抽象基类、`prepare_model` 工厂 |
| `domain/pods_manager.py` | 134 | `PodsManager`：Pod CRUD/prune/stats |
| `domain/networks.py` | 116 | `Network` 资源：connect/disconnect、id 推导、containers 惰性查询 |
| `domain/images.py` | 110 | `Image` 资源：tags/labels/history/save/tag |
| `domain/secrets.py` | 111 | `Secret` / `SecretsManager`：data 原始字节上送 |
| `domain/pods.py` | 95 | `Pod` 资源：kill/start/stop/pause/top 等动作 |
| `domain/system.py` | 89 | `SystemManager`：df/info/login/ping/version |
| `domain/containers_run.py` | 90 | RunMixin.run 四返回分支（前轮 R-1~R-4 已覆盖） |
| `domain/registry_data.py` | 67 | `RegistryData`：平台匹配与按 digest 拉取 |
| `domain/json_stream.py` | 60 | NDJSON/裸 JSON 混合缓冲分割（pull 进度流用） |
| `domain/events.py` | 47 | `EventsManager.list`：`/events?stream=true` 行流 |
| `domain/ipam.py` | 52 | `IPAMPool` / `IPAMConfig`（dict 子类，PascalCase 键） |

### errors（2 文件 / 197 行）

| 文件 | 行数 | 职责 |
|------|------|------|
| `errors/exceptions.py` | 109 | 8 类异常继承链（前轮 E-1~E-8 已覆盖） |
| `errors/__init__.py` | 88 | 异常导出 |

## 核心符号索引（R3 新覆盖模块）

| 符号 | 文件 | 职责要点 |
|------|------|---------|
| `APIClient._normalize_url` | api/client.py L185-207 | scheme 白名单校验 + unix/ssh/tcp 改写 + netloc quote_plus |
| `APIClient._request` | api/client.py L395-462 | compatible 切前缀、lstrip("/")、verify 切 https、OSError→APIError |
| `APIResponse.raise_for_status` | api/client.py L71-85 | 404 异常类可由 `not_found=` 参数替换（ImageNotFound 等） |
| `UDSSocket` / `UDSAdapter` | api/uds.py | AF_UNIX 连接四件套；连接失败包 APIError |
| `prepare_filters` / `prepare_body` | api/http_utils.py | filters 三态→JSON；body 递归剔空保留 False/0，networks 键特判 |
| `frames` / `stream_frames` / `stream_helper` | api/parse_utils.py | 缓冲帧 / 实时帧 / NDJSON 行三种消费器 |
| `demux_output` | api/output_utils.py | 1B 类型+3B pad+4B 大端长度帧拆分 stdout/stderr |
| `create_tar` / `prepare_containerfile` / `prepare_containerignore` | api/tar_utils.py | 上下文打包三函数；uid=0 脱敏；.containerignore 优先 |
| `get_runtime_dir` | api/path_utils.py | XDG→/run/user→/tmp 回退（lstat 防 symlink，0700） |
| `TLSConfig` | tlsconfig.py | 兼容空壳，当前 ignored |
| `PodmanConfig.services/active_service` | domain/config.py L128-177 | TOML 先装、JSON 后装（同名 JSON 赢） |
| `PodmanResource` / `Manager` / `prepare_model` | domain/manager.py | 资源/管理器双基类；collection 与 manager 双名别名 |
| `Pod` / `PodsManager` | domain/pods*.py | id 取 `ID`；stop 参数名 `t`；prune 键 `Err`；stats 默认非流 |
| `Network` / `NetworksManager` | domain/networks*.py | get 无 /json 后缀；prune 键 `Error`；id 可由 name 哈希推导 |
| `IPAMPool` / `IPAMConfig` | domain/ipam.py | dict 子类 PascalCase；driver 默认 host-local；仅支持一个 pool |
| `Volume` / `VolumesManager` | domain/volumes.py | id==name；list 404→[]；prune 真实 Size；export/import 互斥 |
| `Secret` / `SecretsManager` | domain/secrets.py | 名在 `Spec.Name`；exists 借 /json；create data 为裸字节 |
| `Manifest` / `ManifestsManager` | domain/manifests.py | list 抛 NotImplementedError；name 经 quote_plus；digest 去 sha256: |
| `RegistryData.has_platform` | domain/registry_data.py | os/arch 匹配，variant 不被 libpod 承载 |
| `BuildMixin.build/_render_params` | domain/images_build.py | 三上下文入口归约 x-tar；image id 正则从流文本提取 |
| `EventsManager.list` | domain/events.py | `/events` NDJSON 流；门面每次现建管理器 |
| `json_stream/split_buffer` | domain/json_stream.py | raw_decode 容错切分混合缓冲；残块失败抛 StreamParseError |
| `SystemManager` | domain/system.py | login 走 compatible 前缀；ping 为 HEAD 不抛异常 |

## 资源端点与身份差异速查

| 资源 | id 键 | get 端点 | exists 端点 | prune 错误键 | SpaceReclaimed | list |
|------|-------|----------|-------------|--------------|----------------|------|
| Container | `Id` | `/containers/{id}/json` | — | — | — | 有 |
| Image | `Id`（short_id 17/10 截断） | `/images/{name}/json` | `/images/{key}/exists` | `Err`（聚合抛） | 真实累加 | 有 |
| Pod | `ID` 优先回退 `Id` | `/pods/{id}/json` | `/pods/{key}/exists` | `Err` | 恒 0 | 有 |
| Network | `Id`，缺则 sha256(name) | `/networks/{key}`（**无 /json**） | `/networks/{key}/exists` | `Error`（注意拼写） | 恒 0 | 有 |
| Volume | == name | `/volumes/{id}/json` | `/volumes/{key}/exists` | `Err` | 真实累加；list 404→[] | 有 |
| Secret | `ID`；名在 `Spec.Name` | `/secrets/{id}/json` | 借用 `/json` 判 ok | — | — | 有（filters 忽略） |
| Manifest | `manifests[0].digest` 去前缀 | `/manifests/{name}/json` | `/manifests/{name}/exists` | — | — | **NotImplementedError** |
| Quadlet | `Name` | — | HEAD `/quadlets/{key}/exists`（前轮已登记） | — | — | 有 |

## 关键版本/行为门槛

| 条件 | 行为 | 位置 |
|------|------|------|
| Python ≥ 3.11 | TOML 用标准库 tomllib；3.9/3.10 依次回退 tomli/toml/pytomlpp | domain/config.py L12-21 |
| scheme 非 6 种之一 | `ValueError` | api/client.py L188-191 |
| scheme 未匹配挂载分支 | `PodmanError` | api/client.py L168-169 |
| `exec_run(socket=True)` + http+ssh | `NotImplementedError`（裸连接劫持不支持 SSH） | domain/containers.py L223-224 |
| rich 未安装且 progress_bar=True | `ModuleNotFoundError` | domain/images_manager.py L389-391 |
| build 无 path 且无 fileobj | `TypeError` | domain/images_build.py L169-170 |
| build 同时给 gzip 与 encoding | `PodmanError` | domain/images_build.py L172-173 |
| volume import data/path 同给或都不给 | `RuntimeError` | domain/volumes.py L212-215 |
| pods.stats all 与 name 同传 | `ValueError` | domain/pods_manager.py L149-150 |

## 相关信源

- [README + AGENTS 信源](readme-source.md)：安装、extras、7 大 AI 陷阱与工程治理（用户/协作者视角）
- [PodmanClient + APIClient 信源](client-source.md)：门面与传输层 20 锚点（CL/API 编号）
- [Manager + Mixin + 异常 + SSH + Quadlet 信源](api-source.md)：30+ 锚点与 pull 调用链图
