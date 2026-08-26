---
type: Changelog
title: podman-py 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2027-08-26
---

# Bundle Update Log

## 2026-08-26

* **Creation**: 建立 podman-py（v5.8.0，Apache-2.0）源码 OKF 知识包脚手架（references/concepts/examples 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——基于 `.trae/specs/containers-okf-wiki/facts-podman-py.md` 中的 19 条源码事实，补充阅读 `external/dao/action/Containers/podman-py/` 核心文件：`README.md`（安装/依赖/示例）、`podman/__init__.py`（模块导出）、`podman/version.py`（__version__=5.8.0、__compatible_version__=1.40）、`podman/client.py`（PodmanClient 类、__init__ 参数、from_env、9个@cached_property管理器、DockerClient别名、Swarm NotImplementedError）、`podman/api/__init__.py`（工具函数导出、DEFAULT_CHUNK_SIZE=2MB）、`podman/api/client.py`（APIClient/APIResponse、supported_schemes）、`podman/domain/containers_manager.py`（list/get/exists/create/run/remove/prune、sparse模式）、`podman/domain/images_manager.py`（list/get/pull/push/build/remove/prune/search/load/scp、progress_bar）。
* **Add**: E阶段完成——references/ 下 3 个信源登记（readme-source/client-source/api-source），concepts/ 下 5 个概念文档（00-introduction/01-connection/02-managers/03-containers/04-images），examples/ 下 2 个实战示例（01-migration/02-container-ops），加上 references/concepts/examples 三个子目录 index.md（无 frontmatter）和根 index.md（含 okf_version:"0.2"）、log.md。
* **Verify**: V阶段完成——Grep 验证 PodmanClient/DockerClient/from_env/ContainersManager/ImagesManager/APIClient/APIResponse/UDSAdapter/SSHAdapter 等关键类名在 podman/ 源码中存在；__version__="5.8.0" 与 version.py 一致；supported_schemes 列表与 api/client.py 一致；list()/get()/create()/run()/start()/stop()/pull()/push()/build()/remove()/prune()/exec_run()/logs()/reload()/login()/ping()/version()/df()/close() 等方法签名与源码一致；DockerClient = PodmanClient 别名存在；swarm/services/configs/nodes 抛出 NotImplementedError；9 个管理器 cached_property 完整。
