---
type: bundle
title: podman-py Python SDK
okf_version: "0.2"
description: Podman 官方 Python SDK（podman-py v5.8.x）系统化中文源码教程，基于client.py/api.client.py/domain/*/AGENTS.md逐文件阅读萃取。覆盖Docker SDK兼容快速入门、4级连接优先级UDS/SSH/TCP、9资源Manager架构（含Quadlet/Pod/Secret/Manifest/Volume/Network/Event）、容器run/create/exec/logs生命周期、镜像pull/push/build Rich进度条、异常继承体系8子类、测试体系unit/integration/skipif/pnext；R3新增Pod/Network/Volume契约差异、Secret/Manifest多架构分发、NDJSON/多路复用帧/Upgrade三套流协议、构建上下文x-tar管线、UDS四层栈与containers.conf双格式
tags: [Podman, Python SDK, Docker 兼容, OKF v0.2, Container, Rootless, SSH Remote, Quadlet, pytest, Mixin 模式, streaming, multi-arch]
generated:
  by: method_orchestrator/seven-concepts-cmd
  at: 2026-09-07T00:00:00Z
verified:
  by: process:podman-py-grep-20260914
  at: 2026-09-14T00:00:00Z
status: stable
stale_after: 2027-09-14
sources:
  - id: pp-readme
    resource: ../external/dao/action/Containers/podman-py/README.md
    title: podman-py v5.8 README 安装与快速使用
  - id: pp-agents
    resource: ../external/dao/action/Containers/podman-py/AGENTS.md
    title: podman-py AI Agent Guide 开发规范与7大陷阱
  - id: pp-client
    resource: ../external/dao/action/Containers/podman-py/podman/client.py
    title: PodmanClient 薄门面类110行源码
  - id: pp-apiclient
    resource: ../external/dao/action/Containers/podman-py/podman/api/client.py
    title: APIClient requests.Session 子类传输层
  - id: pp-domain-cm
    resource: ../external/dao/action/Containers/podman-py/podman/domain/containers_manager.py
    title: ContainersManager RunMixin+CreateMixin+Manager 组合
  - id: pp-domain-im
    resource: ../external/dao/action/Containers/podman-py/podman/domain/images_manager.py
    title: ImagesManager BuildMixin Rich 进度条
  - id: pp-quadlets
    resource: ../external/dao/action/Containers/podman-py/podman/domain/quadlets.py
    title: Quadlet/Podlet 资源模型与Manager v5.8 新增
  - id: pp-errors
    resource: ../external/dao/action/Containers/podman-py/podman/errors/exceptions.py
    title: 8类异常继承体系 APIError/NotFound/ImageNotFound/ContainerError/BuildError
  - id: pp-ssh
    resource: ../external/dao/action/Containers/podman-py/podman/api/ssh.py
    title: SSHAdapter shell-out ssh -N -L 隧道机制
  - id: pp-vendor-r3
    resource: references/source-code-map.md
    title: R3 vendor 稳定信源（submodule commit 5dd81b4，39 文件 6078 行结构地图）
---

# podman-py Python SDK 知识库

> 🔗 **相关束对比**：[podman-compose 与 podman-py 对比：编排器与 SDK 的选型](../podman-compose/concepts/10-compose-vs-podman-py.md)——声明式 CLI 编排器 vs 命令式 REST SDK 的十维对比与选型决策表。

本知识包是 Podman 官方 Python SDK（[containers/podman-py](https://github.com/containers/podman-py)，Apache-2.0 许可证）的系统化中文源码教程，基于 podman-py v5.8.0 源码深度阅读生成。**特别**萃取了本仓库携带的 `AGENTS.md`（Podman-py AI Agent Guide）中的7大AI陷阱、80% vs 85%覆盖率双轨治理、SSH集成测试前置要求等独有工程治理信息，填补官方ReadTheDocs文档未覆盖的「开发流程合规」盲区。覆盖范围：Docker SDK 兼容入门→4级连接优先级（命名connection / base_url / active_service / 本地socket 回退）→ Mixin+Manager 三层资源架构→容器完整生命周期→Rich进度条镜像构建→Quadlet/Pod/Secrets v5新增资源→8类异常体系→测试双态治理（unit/integration + skipif 版本门控 + pnext 未来特性标记）。

## 概念层（concepts/ 11 篇，按学习路径递进）

* **[00 - Docker SDK 兼容性与三层代码架构](concepts/00-introduction.md)** — Python≥3.9 要求、PyPI 包名 `podman`、`DockerClient = PodmanClient` 别名导入、CONTAINER_HOST / DOCKER_HOST 双前缀6环境变量兼容、9资源管理器+7直接方法、Swarm 三大端点 NotImplementedError、三层代码图（薄门面 PodmanClient → domain Manager+Mixin → api/ APIClient+3Adapter）、核心依赖（requests / urllib3 / rich.progress 可选）。
* **[01 - 连接配置与远程传输适配器](concepts/01-connection.md)** — 四级连接优先级（`connection=` 参数 → `base_url=` 参数 → `containers.conf active_service` is_machine → 本地 `XDG_RUNTIME_DIR/podman/podman.sock` 回退）、`from_env()` 6环境变量双前缀解析、rootless vs rootful socket 路径差异、SSH `http+ssh://user@host[:port]/remote/sock?secure=True` + identity 密钥、TCP 端口暴露注意事项、`supported_schemes` 6方案路由、SSHSocket ssh -N -L 隧道100ms×N轮询机制、`with PodmanClient() as c` 上下文管理器自动close、`max_pool_size` 连接池配置。
* **[02 - 资源管理器架构：Mixin + Manager](concepts/02-managers.md)** — Manager 基类 prepare_model() / @property resource / list()get()exists()骨架、`@cached_property` 懒加载9管理器（containers/images/manifests/networks/volumes/pods/secrets/system **+ v5新增 quadlets**）、ContainersManager「RunMixin + CreateMixin + Manager」三继承模式、ImagesManager「BuildMixin + Manager」二继承模式、PodmanResource 基类 attrs / reload() / id / short_id / name、资源对象实例方法（container.start/stop/kill/pause/unpause/remove/exec_run/logs/reload 等）。
* **[03 - 容器生命周期与状态机](concepts/03-containers.md)** — 容器状态机（created/running/paused/exited/dead/restarting）、`list(all/sparse/filters/ignore_removed)` sparse=not compatible 默认差异（Libpod True vs Docker False）、`get(key, compatible)` 404→NotFound vs APIError、`create(**)` 30+关键字透传 /libpod/containers/create、**`run(image, command, detach/stream/remove/auto_remove/pull policy/missing→always→never→newer)`** 四语义（detach=True→Container对象；detach+stream→日志生成器；detach+remove→thread后台清理；ContainerError非零退出抛异常）、start/stop(timeout)/kill(signal)/pause/unpause/restart/remove(force/v)/prune(filters)、logs(stream/timestamps/tail/since/until/stdout/stderr)、`exec_run(cmd, stdout/stderr/stream/detach/workdir/user/environment)` 三返回模式。
* **[04 - 镜像管理与 Rich 进度条构建](concepts/04-images.md)** — list/get/exists(name→reference 过滤映射)、`pull(repository, tag/platform/auth_config/policy, stream→迭代器/False→Image对象, progress_bar→rich[Progress] 默认尝试import失败降级纯文本)` 4种策略（missing/always/never/newer）、`push(repository, tag/auth_config, stream→字典流/False→str)`、**`build(path/containerfile, buildargs/tags/nocache/pull/rm/squash/platform, stream→build_log 迭代器/False→(Image, build_log), gzip/extra_hosts/network, BuildError 抛异常含msg+build_log)`**、remove/prune、search(term/limit)、load(tarball)/save(image, tgt)、tag(xxx, repo, tag)、login/logout、`scp(source, dest, container/pod/quiet)` 跨主机文件复制。
* **[05 - 高级资源、异常体系与工程治理](concepts/05-advanced.md)** — QuadletsManager v5.8 新增（show/list/get/delete/create/get_contents/print_contents/reload_systemd/report + 4关键字 force/ignore/reload_systemd/stdout）、PodsManager（list/get/create/start/stop/pause/unpause/remove/exec_run/prune/kill）、SecretsManager/ManifestsManager/VolumesManager/NetworksManager 四件套70%接口对齐Docker、SystemManager（df/ping/version/info/events 直接挂 PodmanClient 门面）、异常继承链（PodmanError > BuildError/ContainerError/InvalidArgument；HTTPError > APIError > NotFound/ImageNotFound；DockerException 兼容基类；StreamParseError RuntimeError）、**AGENTS.md7大AI陷阱**（错Go仓库podman/pkg/bindings/make or tox教条/80-85覆盖矛盾/API drift/ssh hang/rootful vs rootless/冗余.gitignore）、测试双态（unit unittest vs integration pytest + pnext @pytest.mark.pnext + skipif OS_RELEASE/PODMAN_VERSION 三元组 + PODMAN_BINARY/PODMAN_LOG_LEVEL/SSH localhost前置）。
* **[06 - Pod / Network / Volume：组编排原语与资源契约差异](concepts/06-pods-networks-volumes.md)** — Pod 身份键 `ID` 优先/stop 参数名 `t`/stats 非流式默认返回原始字节/all-name 互斥；Network id 缺失时 sha256(name) 推导、get 端点无 `/json` 后缀、prune 错误键是 `Error`（非 Err）；IPAMConfig/IPAMPool（host-local、单 pool、IPRange→lease_range 的 net[1]/net[-2] 换算）、connect 嵌套 PascalCase EndpointConfig；Volume.id==name、list 404 返回 `[]`、prune 累加真实 Size、export/import 归档互斥；三资源身份-端点-语义差异矩阵（禁止跨资源类推）。
* **[07 - Secret / Manifest / Registry：密钥与多架构镜像分发](concepts/07-secrets-manifests-registry.md)** — Secret 裸字节上送（name/driver 在 query、data 在 body）、名称在 `Spec.Name`、exists 借用 /json；Manifest 多架构清单（id 取 manifests[0].digest 去前缀、PUT operation=update/remove、push 到 /registry/{dest}、**list() 抛 NotImplementedError**）；RegistryData.has_platform 只判 Os/Architecture（variant 不承载）；**push 进度消息为客户端本地合成两条 dict（不消费服务端流）**、load 返回生成器需迭代、prune 防 JSON null、prune_builds 不发请求。
* **[08 - 事件系统与三套流协议](concepts/08-events-and-streams.md)** — ①NDJSON 行流（events/pull/build：iter_lines、json_stream raw_decode 容错分割、chunked 错误内联）②Docker 8 字节多路复用帧（1B类型+3Bpad+4B大端长度；frames 缓冲/stream_frames 实时/demux_output 分流，logs 不暴露 demux）③HTTP Upgrade 裸 socket（exec_run(socket=True) 劫持、http+ssh 显式拒绝、sock._hijacked_response 防回池）；stream 默认值跨方法差异（Container.stats True vs Pods.stats False）；attach/attach_socket 无条件 NotImplementedError；wait 阻塞返回退出码。
* **[09 - 镜像构建上下文管线](concepts/09-build-context-pipeline.md)** — BuildMixin.build 三入口（custom_context 必须 fileobj+dockerfile / fileobj 走临时目录 / path 走代理拷贝）归约为 application/x-tar；.containerignore 优先于 .dockerignore（仅 fnmatch，不支持 ! 与 **）；create_tar 脱敏（uid=0/root、mtime 钳制、仅 file/dir/symlink、win32 mode 修正）；_render_params 参数映射（OCI 默认清单格式、layers 默认 True、未知 kwargs 静默丢弃）；响应 itertools.tee 分叉 + `(^[0-9a-f]+)$` 正则提取 image id；BuildError 诊断三部曲。
* **[10 - 传输与配置深化](concepts/10-transport-deep-dive.md)** — URL 一生轨迹（scheme 白名单 ValueError、unix/ssh/tcp 改写、netloc quote_plus、lstrip("/")+urljoin）；UDS 四件套（UDSSocket/UDSConnection/Pool/Adapter）与 key_uds 池键、http+ssh 复用 UDS 池、trust_env=False；TLSConfig 兼容空壳（currently ignored）与 verify 一词两义；libpod `/v5.8.0/` 与兼容 `/v1.4/` 双前缀（login /auth 是唯一显式兼容端点）；PodmanConfig 新旧 JSON/TOML 双格式（同名 JSON 覆盖、uri/URI 双写、四级 TOML 回退）；XDG 回退目录 lstat+0700 防 symlink；SystemManager 五端点；APIResponse 代理与 404 异常类参数化。

## 实战示例（examples/ 4 篇，覆盖真实迁移+生产代码+测试治理+组编排）

* **[01 - 从 docker-py 迁移到 podman-py 脚本级灰度](examples/01-migration.md)** — pip 替换（pip uninstall docker && pip install podman）、三行别名（`import podman as docker; from podman import DockerClient`）、from_env() 无改迁移 vs base_url 路径差异（/var/run/docker.sock → /run/user/$UID/podman/podman.sock）、10项API兼容对比表（containers.*/images.*/networks.create 等）、5个高频差异点（Swarm/sparse=True默认/socket路径/Containerfile命名/docker.types*类缺失）、迁移前后完整脚本对比（Nginx部署+健康检查40行→40行，修改<8行）、迁移验证脚本（assert client.ping()==OK, sparse=True→reload()补齐, 兼容模式compatible=True对齐docker行为）。
* **[02 - 完整生命周期：Quadlet + Postgres + Redis 三服务编排](examples/02-container-ops.md)** — 前置检查（socket可达、podman --version ≥5.8、/etc/containers/nsswitch.conf DNS 映射）、15步流水线（版本→清理旧资源→拉取postgres:16+redis:7→quadlets.create postgres.container→quadlets.get_contents校验→quadlets.report健康→containers.create redis+卷挂载→containers.start→containers.exec_run pg_isready→containers.exec_run redis-cli ping→logs(timestamps=True,tail=10)流→stop sequence postgres→redis remove(v=True)→prune filters label=env=demo）、Nginx 反向代理 80→8080 PublishPort + 实时日志follow流、批量启动/停止/删除label=env=prod容器（for c in list(filters): c.remove(force=True)）、异常捕获（ContainerError exit_code / ImageNotFound 404 / APIError cause+explanation）。
* **[03 - 集成测试治理：skipif + pnext + coverage 双阈值](examples/03-testing-governance.md)** — tox.ini 环境对齐（coverage,py39-py313; CONTAINER_HOST=unix://... 前置）、unit测试结构（test_podmanclient.py / test_containersmanager.py，requests-mock mock HTTP响应）、integration测试base.py（PODMAN_BINARY 可执行验证、SSH localhost exit 0 预断言）、**@pytest.mark.skipif 三元组**（PODMAN_VERSION<(5,8,0) / OS_RELEASE ID=fedora VERSION_ID<42 / Rootful vs Rootless socket不一致）、**@pytest.mark.pnext**（--pnext flag控制未来特性用例）、覆盖率双轨（tox -e coverage --fail-under=80自动化；人工review 85%红线核心模块client.py/domain/*/api/*）、pylint按需调用（非pre-commit，非make lint默认项，reviewer要求时执行）、DCO签名（make validate需git-validation二进制）。
* **[04 - 多容器 Pod 网络拓扑（自定义子网 + Secret + Volume + 事件流）](examples/04-pod-network-topology.md)** — IPAMConfig/IPAMPool 自定义 10.89.0.0/24 bridge（IPRange→lease_range）、Secret 裸字节上送与 dict target/mode、命名卷 bind/mode 挂载、Pod 内容器组（app+sidecar localhost 互通）+ networks 空字典端点配置、后台线程消费 events NDJSON（since/filters/decode）、pods.stats 流式 decode、finally 逆序幂等清理。

## 信源登记簿（references/ 4 篇，R1/R2 70 条编号锚点 + R3 vendor 结构地图）

* **[README.md + AGENTS.md 项目总览与工程治理](references/readme-source.md)** — README.md：PyPI包名`pip install podman`；依赖四组（default requests/urllib3、progress_bar[rich]、docs[Sphinx+apidoc]、test[pytest+coverage+tox+requests-mock]）；基础示例代码7行。AGENTS.md：7大AI陷阱（R1-R7）完整列举；质量标准双轨（CONTRIBUTING 85% vs tox/Makefile 80%覆盖冲突）；Persona/Quick start/Common local issues 三段共18项开发流程锚点；DCO Signed-off-by / make validate git-validation要求。
* **[PodmanClient 薄门面 + APIClient 传输层](references/client-source.md)** — PodmanClient：__init__ 四级连接优先级分支（L62-L82）；from_env()6环境变量DOCKER_HOST/CONTAINER_HOST双前缀（L105-L110）；9个@cached_property管理器列表按字母序；7个直接方法（df/ping/version/info/events/login/close）；DockerClient=PodmanClient别名+swarm/services/configs/nodes NotImplementedError四端点。APIClient：requests.Session继承；supported_schemes 6方案（L94-L101）；APIResponse.__getattr__ 转发+raise_for_status 404→NotFound映射；DEFAULT_CHUNK_SIZE 2MB；兼容端点 vs libpod端点双前缀。
* **[Domain Manager 体系 + 异常 + SSH + Quadlets](references/api-source.md)** — Manager基类+Mixin组合：ContainersManager(RunMixin+CreateMixin+Manager)/ImagesManager(BuildMixin+Manager)/QuadletsManager(纯Manager)；RunMixin.run()四分支return语义（L19-L80 containers_run.py）；ImagesManager.pull progress_bar Rich 进度条import try/except（L23-L32 images_manager.py）；Quadlet模型6个@property（name/unit_name/path/status/application）+delete/get_contents/print_contents；异常8类完整继承链；SSHAdapter SHSocket connect() ssh -N -L命令+100ms轮询等待forward sock；PodmanConfig active_service is_machine字段判定。
* **[vendor 全量源码信源登记 R3](references/source-code-map.md)** — 固定 vendor 子模块 `v5.8.0-9-g5dd81b4`（commit 5dd81b4）；39 个库文件 6078 行（api 11/1209 + domain 22/4455 + errors 2/197 + 顶层 4/217）与测试 26 unit + 11 integration 的分层结构地图；R3 新覆盖模块核心符号索引；8 资源端点/身份/prune 差异速查表；9 条版本行为门槛。

## 信任与生命周期说明

* **status 判定依据（R1/R2）**：首批 12 个内容文档（6 概念 + 3 示例 + 3 信源登记）均 `status: stable`，基于对 podman-py v5.8 源码 9 个核心文件 + README.md + AGENTS.md 的逐文件 Grep 事实提取（合计 38 条源码级锚点 + 7 项 AI 陷阱）。
* **status 判定依据（R3，2026-09-14）**：新增 7 个内容文档（5 概念 06-10 + 1 示例 04 + 1 信源 source-code-map）均 `status: stable`，基于 vendor 子模块 commit 5dd81b4（v5.8.0-9-g5dd81b4）25 个文件的逐行/分段精读（api 工具层 8 个、domain 14 个全文 + containers/images_manager 流式段复核、tlsconfig 1 个，另核官方 demo 与测试基建 3 文件），经 R→I→E→V 五阶段流程生成，V 阶段对全部新增类名/方法签名/端点/常量做 Grep 复核与计数断言（含修正 api `__all__` 14→17、SecretsManager `__init__` 非唯一两处事实偏差）。
* **stale_after 解释**：统一 `2027-09-14`。podman-py 核心 API（PodmanClient、9 Manager、run/pull/build 签名）自 v4.x 确立 Docker 兼容设计以来保持高度稳定；R3 新增的内部实现细节（端点路径、帧协议、tar 打包规则）与 libpod HTTP 契约绑定，1 年内预计无破坏性变更；该日期作为针对 podman-py v6.x 潜在破坏性 API / Python ≤3.8 EOL 后的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（R2：from_env/sparse/progress_bar/QuadletsManager/SSHSocket/异常继承链；R3：PodsManager 端点、Network `/json` 缺失、Secret 裸字节、Manifest NotImplementedError、stream_frames 帧格式、exec socket 劫持、create_tar uid=0、双前缀拼接、JSON/TOML 配置优先级），两者分离、可追溯。

本知识包共收录 **19 个内容文档**（11 概念 + 4 示例 + 4 信源登记），另含 3 个子目录 index.md、根 index.md 与 log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
