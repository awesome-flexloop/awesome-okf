---
type: bundle
title: podman-py Python SDK
okf_version: "0.2"
---

# podman-py 知识库

本知识包是 Podman 官方 Python SDK（[podman-py](https://github.com/containers/podman-py)，Apache-2.0 许可证）的系统化中文源码教程，基于 podman-py v5.8.0 源码（`external/dao/action/Containers/podman-py/` 目录）深度阅读生成。覆盖从 Docker SDK 兼容快速入门，到 UDS/SSH/TCP 三种连接配置，再到资源管理器架构、容器完整生命周期与镜像管理构建的知识体系。所有内容均溯源至 podman-py Python 源码，遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 快速入门篇（concepts/）

* [快速入门与 Docker SDK 兼容性](concepts/00-introduction.md) — Python ≥ 3.9 版本要求、pip 安装、第一个 Podman 程序、DockerClient 别名、环境变量双兼容（CONTAINER_HOST/DOCKER_HOST）、Manager API 对齐、Swarm 不支持说明、核心依赖（requests/tomli/urllib3）。
* [连接配置（UDS/SSH/TCP）](concepts/01-connection.md) — 四级连接优先级（connection → base_url → active_service → 本地 socket）、Unix Socket rootful/rootless 路径、SSH 远程隧道与 identity 密钥、TCP 服务启用、from_env() 自动检测、containers.conf 命名连接、连接池配置、with 上下文管理器。

## 核心架构篇（concepts/）

* [资源管理器架构](concepts/02-managers.md) — Manager 模式、@cached_property 懒加载、Manager 基类 prepare_model()、9 个资源管理器总览（containers/images/manifests/networks/volumes/pods/secrets/quadlets/system）、RunMixin/CreateMixin/BuildMixin 组合、领域目录结构、资源模型对象实例方法。
* [容器生命周期操作](concepts/03-containers.md) — 容器状态机、list() 过滤与 sparse 模式、get()/exists()、create() 参数详解、run() 便捷方法、start()/stop()/kill()/restart()/pause()/unpause() 状态控制、remove()/prune() 删除清理、logs() 实时流、exec_run() 命令执行、reload() 属性刷新。
* [镜像管理与构建](concepts/04-images.md) — 镜像 list/get/exists、pull() 拉取（进度条/流式/平台/策略）、push() 推送（认证/目的地）、build() Containerfile 构建（buildargs/nocache/platform）、remove()/prune() 删除清理、search() registry 搜索、load()/save() tar 加载保存、tag() 标签管理、login() registry 认证、scp() 跨主机复制。

## 实战示例（examples/）

* [从 docker-py 迁移到 podman-py](examples/01-migration.md) — pip 替换、import podman as docker 别名导入、from_env() 无修改迁移、base_url 路径差异（/var/run/docker.sock vs /run/user/$UID/podman/podman.sock）、容器/镜像/网络 API 兼容对比、5 个常见差异点（Swarm/sparse/socket 路径/Containerfile/docker.types）、完整迁移前后代码对比、迁移验证脚本。
* [容器创建、启动、停止完整操作](examples/02-container-ops.md) — Podman socket 前置准备、12 步完整生命周期脚本（连接检查→拉镜像→清理旧容器→create→start→list→exec_run→logs→stop→delete→prune）、run()+remove=True 便捷模式、Nginx 端口映射与实时日志流、批量启动/停止/删除带标签容器。

## 信源登记簿（references/）

* [README.md 项目概览与快速入门](references/readme-source.md) — `README.md`：安装命令、PyPI 包名 podman、运行时与可选依赖（progress_bar/docs/test 三组）、基础使用示例代码、官方文档与源码仓库链接。
* [PodmanClient 核心客户端](references/client-source.md) — `podman/__init__.py`、`podman/client.py`、`podman/version.py`：模块导出、__version__=5.8.0、__compatible_version__=1.40、DockerClient 别名、__init__ 10 个关键字参数、from_env() 6 个环境变量、默认连接回退逻辑、9 个 @cached_property 管理器、df/ping/version/info/events/login/close 直接方法、swarm/services/configs/nodes NotImplementedError。
* [HTTP 传输层实现](references/api-source.md) — `podman/api/` 目录：APIClient 继承 requests.Session、APIResponse 错误映射（404→NotFound）、6 种 supported_schemes（unix/http+unix/ssh/http+ssh/tcp/http）、UDSAdapter/SSHAdapter/HTTPAdapter 传输适配器选择、DEFAULT_CHUNK_SIZE=2MB、create_tar/prepare_filters/encode_auth_header 等工具函数导出、PodmanError/APIError/NotFound/ImageNotFound 异常体系。

## 信任与生命周期说明

* **status 判定依据**：全部 10 个内容文档（5 个概念 + 2 个示例 + 3 个信源登记）均 `status: stable`。内容基于对 podman-py 源码（`podman/__init__.py`、`podman/client.py`、`podman/api/` 目录、`podman/domain/containers_manager.py`、`podman/domain/images_manager.py`、`README.md`）的逐文件阅读与事实提取（19 条源码事实），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-26`。podman-py 核心 API（PodmanClient、9 个 Manager、容器/镜像生命周期方法）自 Docker SDK 兼容设计确立以来保持高度稳定；该日期作为针对未来大版本（如 6.x 引入破坏性 API 变更）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（PodmanClient/from_env/ContainersManager/ImagesManager/APIClient 等关键类名、create/run/start/stop/pull/push/build 等方法签名逐一比对源码），两者分离、可追溯。

本知识包共收录 10 个内容文档（5 个概念 + 2 个示例 + 3 个信源登记），另含 3 个子目录 index.md、根 index.md 与 log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
