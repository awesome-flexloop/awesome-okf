---
type: Changelog
title: podman-py 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2027-09-07
---

# Bundle Update Log

## 2026-09-14 podman-py 知识包 v3.0 第 3 轮增量（vendor 全量源码深化）

* **Update Scope**：概念 **6 篇 → 11 篇**（新增 [06 Pod/Network/Volume 组编排原语](concepts/06-pods-networks-volumes.md)、[07 Secret/Manifest/Registry 分发面](concepts/07-secrets-manifests-registry.md)、[08 事件与三套流协议](concepts/08-events-and-streams.md)、[09 构建上下文管线](concepts/09-build-context-pipeline.md)、[10 传输与配置深化](concepts/10-transport-deep-dive.md)）；示例 **3 篇 → 4 篇**（新增 [04 多容器 Pod 网络拓扑](examples/04-pod-network-topology.md)）；信源 **3 篇 → 4 篇**（新增 [source-code-map](references/source-code-map.md)）。新增 **7 个内容文档**，编号续接不重排；既有 12 篇结论未重写，仅各级 index/log 追加。
* **信源固定（G0）**：首次锚定 SpecWeave vendor 稳定信源 `vendor/podman-py`（third_party git submodule，只读）：Git `v5.8.0-9-g5dd81b4`、commit `5dd81b49f35733a27b8051c47e23d3b4c85ea716`、2026-08-19、remote containers/podman-py；包内 `__version__="5.8.0"`/`__compatible_version__="1.40"`。前两轮基于 `external/dao/...` 路径快照的信源登记保留作历史基线，新文档一律引用 vendor 路径对应的 source-code-map。
* **R 阶段事实来源（25 个文件逐行/分段精读，另含 3 个辅助文件）**：api 层 8 个新覆盖 `uds.py`/`tar_utils.py`/`http_utils.py`/`output_utils.py`/`parse_utils.py`/`path_utils.py`/`adapter_utils.py`/`api_versions.py`（`client.py` 全量复核）；domain 层 14 个全文 `config.py`/`events.py`/`json_stream.py`/`ipam.py`/`registry_data.py`/`system.py`/`pods.py`/`pods_manager.py`/`networks.py`/`networks_manager.py`/`volumes.py`/`secrets.py`/`manifests.py`/`images_build.py`，加 `images_manager.py`/`containers.py` 流式段复核；顶层 `tlsconfig.py`；辅助 `contrib/examples/demo.py`、`tests/integration/base.py`、`tests/utils.py`。facts.md 落盘 `.trae/specs/podman-py-wiki-r3/`（A-P 组编号事实，G1 零推断通过）。
* **核心新事实（防虚构锚点）**：39 库文件 6078 行（api 11/1209 + domain 22/4455 + errors 2/197 + 顶层 4/217，独立计数复核）+ 测试 unit 26/integration 11；资源契约差异矩阵（Pod id 取 `ID`/Network get 无 `/json`/Secret exists 借 `/json`/prune 错误键 Err vs Error/Volume list 404→[]/Manifest.list 抛 NotImplementedError）；三套流协议（NDJSON 行流、8 字节多路复用帧 `>BxxxL`、HTTP Upgrade 裸 socket 且禁 SSH）；push 进度为客户端本地合成两条 dict 不消费响应体；构建三入口归约 x-tar 与 uid=0 脱敏；TLSConfig 为 currently ignored 空壳；containers.conf 新 JSON 覆盖旧 TOML；login `/auth` 唯一显式 compatible 前缀端点。
* **洞察与模式（G2/G3）**：5 组四元组洞察（契约差异无类推/stream 一词三义/合成进度/客户端构建标准化/兼容优先折中）；各新概念文末累计 20+ 条可迁移模式（契约差异矩阵法、协议先判定再消费、传输四分层、双格式配置优先级、临时目录最小权限、404 异常参数化等）。
* **质量门**：G0 信源 stable 无临时克隆；G3 信源先行（source-code-map 先于概念生成）、分批 ≤7（1+3+3）、index 最后写；G4 见同日 V 阶段报告（Grep 类名/方法/端点/常量存在性 + 计数断言 39 文件/6078 行/26/11 + toctree 4 级闭环）。

## 2026-09-07 podman-py 知识包 v2.0 全面升级

* **Update Scope**: 概念 **5 篇 → 6 篇**（新增 [05 - 高级资源、异常体系与工程治理](concepts/05-advanced.md) 覆盖 Quadlet v5.8 / 8 类异常 / AGENTS 7 陷阱 / 测试双态治理）；示例 **2 篇 → 3 篇**（新增 [03 - 集成测试治理：skipif/pnext/覆盖率双轨/DCO/pylint不默认](examples/03-testing-governance.md)）；信源 3 篇全面重写为 20+20+30 = **70 条编号锚点 + 1 调用链图**；根 index + 3 子目录 index toctree 同步更新。
* **AGENTS.md 显式要求覆盖**：严格对应用户指令学习 `external/.../podman-py/AGENTS.md` 全文，将其 Persona/Mental Model/Build-Test-Quality 表/Quick Start SSH 前置/7 大 AI 陷阱 R1~R7/80% vs 85% 覆盖率矛盾/pylint 不默认/DCO git-validation 依赖/冗余 ignore 同步等核心内容分别写入 05-advanced（概念）、03-testing-governance（示例）、readme-source（信源登记）三处。
* **Quadlet v5.8 新增资源覆盖**：完成了 podman 5.8 起新引入的 QuadletsManager.install 三形态（tuple/路径/tarball）、6 @property、3 方法、force/ignore/reload_systemd 关键字、enable-linger 前置检查等内容，写入 05-advanced 概念 + 02-container-ops 示例 Step 4~6。
* **源文件集合**：新增/重写过程中实际阅读的源文件（R 阶段 13 份）：`README.md`、`AGENTS.md`、`tox.ini`、`pyproject.toml`、`podman/client.py`、`podman/api/client.py`、`podman/api/ssh.py`、`podman/domain/manager.py`、`podman/domain/containers_manager.py`、`podman/domain/containers_run.py`、`podman/domain/containers_create.py`、`podman/domain/images_manager.py`、`podman/domain/images_build.py`、`podman/domain/quadlets.py`、`podman/errors/exceptions.py`。
* **洞察与模式**：G2 四元组 4 组（薄门面兼容三坑/SSH隧道挂起/Mixin组合复用/工程治理双轨覆盖率）；G3 可迁移模式 10+ 项（分布在 02-managers/04-images/05-advanced 文末的模式表）。
* **质量门**：所有非保留文件 frontmatter 字段（type/title/description/tags/generated/verified/status/stale_after/sources）齐全 OKF v0.2；toctree（根→概念/示例/信源→子条目）4 级闭环无孤立；概念 6 / 示例 3 / 信源 3 计数与根 index 完全对账；对抗审查 Grep 对齐见下一步 V 阶段报告。

## 2026-08-26

* **Creation**: 建立 podman-py（v5.8.0，Apache-2.0）源码 OKF 知识包脚手架（references/concepts/examples 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——基于 `.trae/specs/containers-okf-wiki/facts-podman-py.md` 中的 19 条源码事实，补充阅读 `external/dao/action/Containers/podman-py/` 核心文件：`README.md`（安装/依赖/示例）、`podman/__init__.py`（模块导出）、`podman/version.py`（__version__=5.8.0、__compatible_version__=1.40）、`podman/client.py`（PodmanClient 类、__init__ 参数、from_env、9个@cached_property管理器、DockerClient别名、Swarm NotImplementedError）、`podman/api/__init__.py`（工具函数导出、DEFAULT_CHUNK_SIZE=2MB）、`podman/api/client.py`（APIClient/APIResponse、supported_schemes）、`podman/domain/containers_manager.py`（list/get/exists/create/run/remove/prune、sparse模式）、`podman/domain/images_manager.py`（list/get/pull/push/build/remove/prune/search/load/scp、progress_bar）。
* **Add**: E阶段完成——references/ 下 3 个信源登记（readme-source/client-source/api-source），concepts/ 下 5 个概念文档（00-introduction/01-connection/02-managers/03-containers/04-images），examples/ 下 2 个实战示例（01-migration/02-container-ops），加上 references/concepts/examples 三个子目录 index.md（无 frontmatter）和根 index.md（含 okf_version:"0.2"）、log.md。
* **Verify**: V阶段完成——Grep 验证 PodmanClient/DockerClient/from_env/ContainersManager/ImagesManager/APIClient/APIResponse/UDSAdapter/SSHAdapter 等关键类名在 podman/ 源码中存在；__version__="5.8.0" 与 version.py 一致；supported_schemes 列表与 api/client.py 一致；list()/get()/create()/run()/start()/stop()/pull()/push()/build()/remove()/prune()/exec_run()/logs()/reload()/login()/ping()/version()/df()/close() 等方法签名与源码一致；DockerClient = PodmanClient 别名存在；swarm/services/configs/nodes 抛出 NotImplementedError；9 个管理器 cached_property 完整。
