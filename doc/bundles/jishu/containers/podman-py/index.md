---
type: bundle
title: podman-py Python SDK
okf_version: "0.2"
description: Podman 官方 Python SDK（podman-py v5.8.x）系统化中文源码教程，基于client.py/api.client.py/domain/*/AGENTS.md逐文件阅读萃取。覆盖Docker SDK兼容快速入门、4级连接优先级UDS/SSH/TCP、9资源Manager架构（含Quadlet/Pod/Secret/Manifest/Volume/Network/Event）、容器run/create/exec/logs生命周期、镜像pull/push/build Rich进度条、异常继承体系8子类、测试体系unit/integration/skipif/pnext、AGENTS.md7大AI陷阱+80%vs85%覆盖率双轨治理
tags: [Podman, Python SDK, Docker 兼容, OKF v0.2, Container, Rootless, SSH Remote, Quadlet, pytest, Mixin 模式]
generated:
  by: method_orchestrator/seven-concepts-cmd
  at: 2026-09-07T00:00:00Z
verified:
  by: process:podman-py-grep-20260907
  at: 2026-09-07T00:00:00Z
status: stable
stale_after: 2027-09-07
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
---

# podman-py Python SDK 知识库

本知识包是 Podman 官方 Python SDK（[containers/podman-py](https://github.com/containers/podman-py)，Apache-2.0 许可证）的系统化中文源码教程，基于 podman-py v5.8.0 源码深度阅读生成。**特别**萃取了本仓库携带的 `AGENTS.md`（Podman-py AI Agent Guide）中的7大AI陷阱、80% vs 85%覆盖率双轨治理、SSH集成测试前置要求等独有工程治理信息，填补官方ReadTheDocs文档未覆盖的「开发流程合规」盲区。覆盖范围：Docker SDK 兼容入门→4级连接优先级（命名connection / base_url / active_service / 本地socket 回退）→ Mixin+Manager 三层资源架构→容器完整生命周期→Rich进度条镜像构建→Quadlet/Pod/Secrets v5新增资源→8类异常体系→测试双态治理（unit/integration + skipif 版本门控 + pnext 未来特性标记）。

## 概念层（concepts/ 6 篇，按学习路径递进）

* **[00 - Docker SDK 兼容性与三层代码架构](concepts/00-introduction.md)** — Python≥3.9 要求、PyPI 包名 `podman`、`DockerClient = PodmanClient` 别名导入、CONTAINER_HOST / DOCKER_HOST 双前缀6环境变量兼容、9资源管理器+7直接方法、Swarm 三大端点 NotImplementedError、三层代码图（薄门面 PodmanClient → domain Manager+Mixin → api/ APIClient+3Adapter）、核心依赖（requests / urllib3 / rich.progress 可选）。
* **[01 - 连接配置与远程传输适配器](concepts/01-connection.md)** — 四级连接优先级（`connection=` 参数 → `base_url=` 参数 → `containers.conf active_service` is_machine → 本地 `XDG_RUNTIME_DIR/podman/podman.sock` 回退）、`from_env()` 6环境变量双前缀解析、rootless vs rootful socket 路径差异、SSH `http+ssh://user@host[:port]/remote/sock?secure=True` + identity 密钥、TCP 端口暴露注意事项、`supported_schemes` 6方案路由、SSHSocket ssh -N -L 隧道100ms×N轮询机制、`with PodmanClient() as c` 上下文管理器自动close、`max_pool_size` 连接池配置。
* **[02 - 资源管理器架构：Mixin + Manager](concepts/02-managers.md)** — Manager 基类 prepare_model() / @property resource / list()get()exists()骨架、`@cached_property` 懒加载9管理器（containers/images/manifests/networks/volumes/pods/secrets/system **+ v5新增 quadlets**）、ContainersManager「RunMixin + CreateMixin + Manager」三继承模式、ImagesManager「BuildMixin + Manager」二继承模式、PodmanResource 基类 attrs / reload() / id / short_id / name、资源对象实例方法（container.start/stop/kill/pause/unpause/remove/exec_run/logs/reload 等）。
* **[03 - 容器生命周期与状态机](concepts/03-containers.md)** — 容器状态机（created/running/paused/exited/dead/restarting）、`list(all/sparse/filters/ignore_removed)` sparse=not compatible 默认差异（Libpod True vs Docker False）、`get(key, compatible)` 404→NotFound vs APIError、`create(**)` 30+关键字透传 /libpod/containers/create、**`run(image, command, detach/stream/remove/auto_remove/pull policy/missing→always→never→newer)`** 四语义（detach=True→Container对象；detach+stream→日志生成器；detach+remove→thread后台清理；ContainerError非零退出抛异常）、start/stop(timeout)/kill(signal)/pause/unpause/restart/remove(force/v)/prune(filters)、logs(stream/timestamps/tail/since/until/stdout/stderr)、`exec_run(cmd, stdout/stderr/stream/detach/workdir/user/environment)` 三返回模式。
* **[04 - 镜像管理与 Rich 进度条构建](concepts/04-images.md)** — list/get/exists(name→reference 过滤映射)、`pull(repository, tag/platform/auth_config/policy, stream→迭代器/False→Image对象, progress_bar→rich[Progress] 默认尝试import失败降级纯文本)` 4种策略（missing/always/never/newer）、`push(repository, tag/auth_config, stream→字典流/False→str)`、**`build(path/containerfile, buildargs/tags/nocache/pull/rm/squash/platform, stream→build_log 迭代器/False→(Image, build_log), gzip/extra_hosts/network, BuildError 抛异常含msg+build_log)`**、remove/prune、search(term/limit)、load(tarball)/save(image, tgt)、tag(xxx, repo, tag)、login/logout、`scp(source, dest, container/pod/quiet)` 跨主机文件复制。
* **[05 - 高级资源、异常体系与工程治理](concepts/05-advanced.md)** — QuadletsManager v5.8 新增（show/list/get/delete/create/get_contents/print_contents/reload_systemd/report + 4关键字 force/ignore/reload_systemd/stdout）、PodsManager（list/get/create/start/stop/pause/unpause/remove/exec_run/prune/kill）、SecretsManager/ManifestsManager/VolumesManager/NetworksManager 四件套70%接口对齐Docker、SystemManager（df/ping/version/info/events 直接挂 PodmanClient 门面）、异常继承链（PodmanError > BuildError/ContainerError/InvalidArgument；HTTPError > APIError > NotFound/ImageNotFound；DockerException 兼容基类；StreamParseError RuntimeError）、**AGENTS.md7大AI陷阱**（错Go仓库podman/pkg/bindings/make or tox教条/80-85覆盖矛盾/API drift/ssh hang/rootful vs rootless/冗余.gitignore）、测试双态（unit unittest vs integration pytest + pnext @pytest.mark.pnext + skipif OS_RELEASE/PODMAN_VERSION 三元组 + PODMAN_BINARY/PODMAN_LOG_LEVEL/SSH localhost前置）。

## 实战示例（examples/ 3 篇，覆盖真实迁移+生产代码+测试治理）

* **[01 - 从 docker-py 迁移到 podman-py 脚本级灰度](examples/01-migration.md)** — pip 替换（pip uninstall docker && pip install podman）、三行别名（`import podman as docker; from podman import DockerClient`）、from_env() 无改迁移 vs base_url 路径差异（/var/run/docker.sock → /run/user/$UID/podman/podman.sock）、10项API兼容对比表（containers.*/images.*/networks.create 等）、5个高频差异点（Swarm/sparse=True默认/socket路径/Containerfile命名/docker.types*类缺失）、迁移前后完整脚本对比（Nginx部署+健康检查40行→40行，修改<8行）、迁移验证脚本（assert client.ping()==OK, sparse=True→reload()补齐, 兼容模式compatible=True对齐docker行为）。
* **[02 - 完整生命周期：Quadlet + Postgres + Redis 三服务编排](examples/02-container-ops.md)** — 前置检查（socket可达、podman --version ≥5.8、/etc/containers/nsswitch.conf DNS 映射）、15步流水线（版本→清理旧资源→拉取postgres:16+redis:7→quadlets.create postgres.container→quadlets.get_contents校验→quadlets.report健康→containers.create redis+卷挂载→containers.start→containers.exec_run pg_isready→containers.exec_run redis-cli ping→logs(timestamps=True,tail=10)流→stop sequence postgres→redis remove(v=True)→prune filters label=env=demo）、Nginx 反向代理 80→8080 PublishPort + 实时日志follow流、批量启动/停止/删除label=env=prod容器（for c in list(filters): c.remove(force=True)）、异常捕获（ContainerError exit_code / ImageNotFound 404 / APIError cause+explanation）。
* **[03 - 集成测试治理：skipif + pnext + coverage 双阈值](examples/03-testing-governance.md)** — tox.ini 环境对齐（coverage,py39-py313; CONTAINER_HOST=unix://... 前置）、unit测试结构（test_podmanclient.py / test_containersmanager.py，requests-mock mock HTTP响应）、integration测试base.py（PODMAN_BINARY 可执行验证、SSH localhost exit 0 预断言）、**@pytest.mark.skipif 三元组**（PODMAN_VERSION<(5,8,0) / OS_RELEASE ID=fedora VERSION_ID<42 / Rootful vs Rootless socket不一致）、**@pytest.mark.pnext**（--pnext flag控制未来特性用例）、覆盖率双轨（tox -e coverage --fail-under=80自动化；人工review 85%红线核心模块client.py/domain/*/api/*）、pylint按需调用（非pre-commit，非make lint默认项，reviewer要求时执行）、DCO签名（make validate需git-validation二进制）。

## 信源登记簿（references/ 3 篇，按源码切片组织，共 38 条可追溯事实锚点）

* **[README.md + AGENTS.md 项目总览与工程治理](references/readme-source.md)** — README.md：PyPI包名`pip install podman`；依赖四组（default requests/urllib3、progress_bar[rich]、docs[Sphinx+apidoc]、test[pytest+coverage+tox+requests-mock]）；基础示例代码7行。AGENTS.md：7大AI陷阱（R1-R7）完整列举；质量标准双轨（CONTRIBUTING 85% vs tox/Makefile 80%覆盖冲突）；Persona/Quick start/Common local issues 三段共18项开发流程锚点；DCO Signed-off-by / make validate git-validation要求。
* **[PodmanClient 薄门面 + APIClient 传输层](references/client-source.md)** — PodmanClient：__init__ 四级连接优先级分支（L62-L82）；from_env()6环境变量DOCKER_HOST/CONTAINER_HOST双前缀（L105-L110）；9个@cached_property管理器列表按字母序；7个直接方法（df/ping/version/info/events/login/close）；DockerClient=PodmanClient别名+swarm/services/configs/nodes NotImplementedError四端点。APIClient：requests.Session继承；supported_schemes 6方案（L94-L101）；APIResponse.__getattr__ 转发+raise_for_status 404→NotFound映射；DEFAULT_CHUNK_SIZE 2MB；兼容端点 vs libpod端点双前缀。
* **[Domain Manager 体系 + 异常 + SSH + Quadlets](references/api-source.md)** — Manager基类+Mixin组合：ContainersManager(RunMixin+CreateMixin+Manager)/ImagesManager(BuildMixin+Manager)/QuadletsManager(纯Manager)；RunMixin.run()四分支return语义（L19-L80 containers_run.py）；ImagesManager.pull progress_bar Rich 进度条import try/except（L23-L32 images_manager.py）；Quadlet模型6个@property（name/unit_name/path/status/application）+delete/get_contents/print_contents；异常8类完整继承链；SSHAdapter SHSocket connect() ssh -N -L命令+100ms轮询等待forward sock；PodmanConfig active_service is_machine字段判定。

## 信任与生命周期说明

* **status 判定依据**：全部 12 个内容文档（6 概念 + 3 示例 + 3 信源登记）均 `status: stable`。内容基于对 podman-py v5.8 源码 9 个核心文件（client.py/api/client.py/domain/{containers_manager,containers_run,images_manager,quadlets}.py/errors/exceptions.py/api/ssh.py）+ README.md + AGENTS.md 的逐文件Grep事实提取（合计 38 条源码级锚点 + 7 项AI陷阱），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一 `2027-09-07`。podman-py 核心 API（PodmanClient、9 Manager、run/pull/build签名）自 v4.x 确立 Docker 兼容设计以来保持高度稳定；AGENTS.md 工程治理条款（80% vs 85%、7大陷阱）预计1年内不会修订；该日期作为针对 podman-py v6.x 潜在破坏性 API / Python ≤3.8 EOL 后的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（PodmanClient.from_env / ContainersManager.list sparse / ImagesManager.pull progress_bar / QuadletsManager / SSHSocket connect / 异常继承链 等关键类名与方法签名逐一比对源码与 AGENTS.md），两者分离、可追溯。

本知识包共收录 **12 个内容文档**（6 概念 + 3 示例 + 3 信源登记），另含 3 个子目录 index.md、根 index.md 与 log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
