# 核心概念

本目录按学习路径组织 Podman 容器引擎的核心概念文档，从 daemonless 架构与代码分层切入，经核心命令分层与资源状态机，再深入 Rootless 安全模型、Docker 兼容性设计，最后到 Quadlet/Kubernetes YAML 系统集成和跨平台远程连接，形成完整的知识递进链路。

* [00 - daemonless 架构与分层代码结构](00-introduction.md) — 无守护进程设计哲学、Go 代码库四层架构（cmd/podman CLI 层 → pkg/domain 业务层 → libpod 核心层 → containers/* 依赖层）、SQLite/BoltDB 持久化、Cobra 命令框架、9 大命令域总览。
* [01 - 核心命令分层与资源模型](01-commands.md) — 容器/镜像/Pod/网络/卷/秘钥/系统/清单/构件 9 大命令域、容器状态机、create→start→exec→stop→rm 生命周期、查询四件套（list/get/exists/inspect）、prune 批量清理、镜像传输协议、Pod infra 容器。
* [02 - Rootless 容器安全模型](02-rootless.md) — user namespace 映射（subuid/subgid）、/dev/fuse + fuse-overlayfs 存储驱动、slirp4netns/pasta 网络、cgroup v2 delegation 资源限制、禁用 --privileged 原则、9 项常见问题排查清单。
* [03 - Docker CLI/API 兼容性设计](03-docker-compat.md) — CLI 命令一字不差对齐、DOCKER_HOST/CONTAINER_HOST 双环境变量、/v1.x 与 /libpod 双 REST API 端点、podman-compose 6.x 内置、Swarm/links 不支持清单、生产迁移五步灰度法。
* [04 - Quadlet 与 Kubernetes YAML 系统集成](04-quadlet-kube.md) — .container/.volume/.network/.kube 四种 Quadlet 单元文件、[Container] 常用字段 → podman run 对照表、podman kube play/apply/down 幂等语义、systemd socket 激活、auto-update + healthcheck 自愈闭环。
* [05 - 跨平台远程连接与 podman machine](05-remote-machine.md) — UDS/SSH/TCP 三种连接协议、system-connection 命名管理、Apple Silicon / Intel mac Hypervisor/QEMU 后端、Windows WSL2 原生 Podman 推荐路径、多 machine + 命名连接组合用法、8 项高频跨平台故障排查清单。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-commands
02-rootless
03-docker-compat
04-quadlet-kube
05-remote-machine
```
