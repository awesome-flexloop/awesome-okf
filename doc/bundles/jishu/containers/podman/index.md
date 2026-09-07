---
type: bundle
title: Podman 容器引擎
okf_version: "0.2"
---

# Podman 知识库

本知识包是 [Podman](https://github.com/containers/podman)（Libpod，Apache-2.0 许可证）——无守护进程的 OCI 兼容容器引擎的系统化中文源码教程，基于 Podman v6.x 源码（`external/dao/action/podman-container-tools/podman/` 目录）与官方文档深度阅读生成。覆盖从 daemonless 架构设计、核心命令分层，到 Rootless 安全模型、Docker CLI/API 双向兼容、Quadlet/Kubernetes YAML 系统集成，以及跨平台远程连接与 podman machine 虚拟机的完整知识体系。所有内容均溯源至 Podman Go 源码、Sphinx 文档中心与 man page 源文件，遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 架构总览篇（concepts/）

* [daemonless 架构与分层代码结构](concepts/00-introduction.md) —— 无守护进程设计哲学、Go 代码库四层架构（cmd/podman CLI 层 → pkg/domain 业务层 → libpod 核心层 → containers/* 依赖层）、SQLite/BoltDB 持久化、Cobra 命令框架、9 大命令域总览。
* [核心命令分层与资源模型](concepts/01-commands.md) —— 容器/镜像/Pod/网络/卷/秘钥/系统/清单/构件 9 大命令域、资源状态机、create → start → exec → stop → rm 生命周期、list/get/exists/inspect 查询四件套、prune 批量清理模式。
* [Rootless 容器安全模型](concepts/02-rootless.md) —— user namespace 映射（subuid/subgid）、/dev/fuse + fuse-overlayfs 存储、slirp4netns 网络、cgroup v2 分层、limits.conf 资源、--privileged 禁用原则、常见问题排查。
* [Docker CLI/API 兼容性设计](concepts/03-docker-compat.md) —— CLI 命令对齐（docker run → podman run）、环境变量兼容（DOCKER_HOST → CONTAINER_HOST）、REST API Docker 端点（/v1.x/libpod 双端点）、podman-compose 替代方案、已知差异清单（Swarm/links/--link）。
* [Quadlet 与 Kubernetes YAML 系统集成](concepts/04-quadlet-kube.md) —— Quadlet .container/.volume/.network/.kube 单元文件、systemd socket 激活、podman kube play/apply/down YAML 循环、podman generate kube 导出、与 systemd 自动更新（auto-update）协同。
* [跨平台远程连接与 podman machine](concepts/05-remote-machine.md) —— podman-remote 客户端、system-connection 命名连接（UDS/SSH/TCP）、podman machine init/start/ssh QEMU 虚拟机、macOS/Windows 平台差异、WSL2 后端配置。

## 实战示例（examples/）

* [CentOS/RHEL 系 Rootless Podman 生产部署](examples/01-rootless-production.md) —— 内核 5.14+ cgroup v2 前置检查、subuid/subgid 配置、fuse-overlayfs 存储驱动验证、普通用户拉取运行 Nginx 容器、systemd --user 自启动、防火墙与端口转发、资源限制验证（CPU/内存）。
* [Quadlet 部署多服务系统级容器栈](examples/02-quadlet-stack.md) —— Postgres .container 卷持久化 + Redis .container 内存缓存 + Web 应用 .container 网络互联 + 整个栈的 .kube YAML 替代方案、systemctl enable --now 开机自启、auto-update 镜像滚动更新策略、健康检查与重启策略。

## 信源登记簿（references/）

* [README.md 与 docs/README.md 文档工程](references/readme-source.md) —— `README.md` 项目定位与快速安装、`docs/README.md` Sphinx 文档目录结构（source/markdown/ 为 man page 源）、docs/requirements.txt 依赖、docs/CODE_STRUCTURE.md 代码库分层说明、docs/MANPAGE_SYNTAX.md 手册页语法。
* [CLI 层与 Domain 层架构源码](references/cli-domain-source.md) —— `cmd/podman/` Cobra 命令定义、`pkg/domain/entities/` ContainerEngine/ImageEngine 双接口、`pkg/domain/infra/abi/` 本地 libpod 直接调用、`pkg/domain/infra/tunnel/` 远程 bindings 转发、`pkg/specgen/` 容器/Pod 规格生成器。
* [libpod 核心与外部协同库](references/libpod-source.md) —— `libpod/` 容器/Pod/Volume 管理核心、SQLite/BoltDB 磁盘数据库、与 containers/storage（镜像层存储）、containers/buildah（镜像构建）、containers/common/libnetwork（网络管理）、containers/image（镜像传输）四大核心依赖的协同调用链。

## 信任与生命周期说明

* **status 判定依据**：全部 11 个内容文档（6 个概念 + 2 个示例 + 3 个信源登记）均 `status: stable`。内容基于对 Podman 源码（cmd/podman/、pkg/domain/、libpod/、pkg/api/、pkg/bindings/、pkg/specgen/、README.md、docs/CODE_STRUCTURE.md、docs/README.md）的逐目录阅读与事实提取（37 条架构与命令事实），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-09-07`。Podman 核心架构（daemonless 四层结构、9 大命令域、Rootless 模型、Docker 兼容端点、Quadlet 单元格式）自 v4.x 确立以来保持稳定；该日期作为针对未来大版本（如 v7.x 引入破坏性架构变更或 API 不兼容升级）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（ContainerEngine/ImageEngine 接口、abi/tunnel 双实现、libpod 核心函数、Quadlet 单元类型、kube play/generate 命令、podman machine 子命令 等关键类名与方法签名逐一比对源码与 man page），两者分离、可追溯。

本知识包共收录 11 个内容文档（6 个概念 + 2 个示例 + 3 个信源登记），另含 3 个子目录 index.md、根 index.md 与 log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
