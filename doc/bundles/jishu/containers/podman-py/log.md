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
