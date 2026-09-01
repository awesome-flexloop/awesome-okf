---
okf_version: "0.2"
---

# Podman Container Tools 知识库

本知识包是 [Podman 容器工具集](https://podman.io/)（POD MANager）的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到高级主题的完整知识体系。Podman 是一个无守护进程（daemonless）的 OCI 容器与 Pod 管理工具，支持 rootless 安全运行、Docker 兼容 CLI、Kubernetes YAML 原生支持，是 Docker 的主流替代方案之一。

所有内容均溯源至 Podman v6 源码（`external/dao/action/podman-container-tools/` 目录）及周边子项目（automation/community/image_build/podman-machine-os），遵循 OKF v0.2 规范。

## 入门与基础（concepts/）

* [Podman 简介](concepts/00-introduction.md) — 无守护进程容器引擎、rootless安全模式、与Docker对比、容器工具生态定位。
* [5分钟快速上手](concepts/01-getting-started.md) — Linux/Mac/Windows安装、验证安装、运行第一个容器、基础命令速览。
* [架构概览](concepts/02-architecture-overview.md) — 无守护进程vs client-server、三层核心抽象、双引擎模式(ABI/Tunnel)、REST API设计。

## 核心概念（concepts/）

* [Runtime 运行时](concepts/03-runtime.md) — Runtime结构、函数式选项模式、NewRuntime创建流程、crun/conmon组件。
* [容器基础](concepts/04-container-basics.md) — Container结构体、syncContainer并发安全、ContainerState状态、7种Linux命名空间。
* [Pod 一等公民](concepts/05-pod-first-class.md) — Pod独立资源模型、infra容器、命名空间共享策略、与Kubernetes Pod对应。
* [CLI 命令结构](concepts/06-cli-structure.md) — Cobra框架、启动流程、命令注册表机制、EngineMode本地/远程过滤。

## 命令操作（concepts/）

* [容器操作命令](concepts/07-container-commands.md) — 36个容器命令分类：生命周期、状态查询、交互、检查点、提交、清理。
* [镜像操作命令](concepts/08-image-commands.md) — 27个镜像命令分类：获取、查询、构建、标记、删除、信任、传输。
* [网络与存储卷](concepts/09-network-volume.md) — CNI/netavark网络栈、rootless网络、Volume管理、命名卷vs绑定挂载。

## 高级主题（concepts/）

* [无 Root 容器](concepts/10-rootless.md) — 用户命名空间原理、UID/GID映射、安全优势、网络差异。
* [远程连接与 REST API](concepts/11-remote-api.md) — 双引擎架构、system connection管理、Docker兼容API、Go bindings。
* [systemd 集成与 Quadlet](concepts/12-systemd-quadlet.md) — Quadlet自动生成systemd单元、容器服务化部署。
* [Kubernetes 集成](concepts/13-kubernetes-integration.md) — kube play/generate、本地轻量K8s开发环境。

## 生态与工具（concepts/）

* [容器工具生态全景](concepts/14-ecosystem.md) — Podman+Buildah+Skopeo三剑客协作、containers共享库。
* [官方镜像构建](concepts/15-image-build.md) — 多架构官方镜像构建流程、quay.io发布、标签策略。
* [自动化与 Machine OS](concepts/16-automation-ci.md) — CI自动化、Mac测试池、podman-machine-os虚拟机镜像。

## 实战示例（examples/）

* [基础容器操作](examples/basic-container.md) — 镜像拉取→运行容器→查看日志→进入容器→停止删除完整流程。
* [Pod 与 Kubernetes YAML 实战](examples/pod-deployment.md) — Pod管理多容器、kube generate/play、nginx+redis sidecar。
* [无 Root 部署 Nginx](examples/rootless-nginx.md) — rootless容器+systemd用户服务+linger开机自启。
* [远程连接与 API 使用](examples/remote-client.md) — 远程服务配置、REST API调用、Go bindings示例。

## 信源登记簿（references/）

* [Podman Container Tools 源码信源登记](references/podman-source.md) — 源码路径、核心模块清单、数据结构公开API、依赖列表。

## 信任与生命周期说明

* **status 判定依据**：全部 22 个内容文档（17 个概念 + 4 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 Podman v6 源码及 5 个子项目目录的逐模块阅读与事实提取（131 条源码事实），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-26`。Podman v6 核心架构（无守护进程、Runtime/Container/Pod 三层抽象、双引擎模式）自 v3.x 以来保持稳定；该日期作为针对未来大版本升级的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-26）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-26），两者分离、可追溯。

本知识包共收录 22 个内容文档（17 个概念 + 4 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 2

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
