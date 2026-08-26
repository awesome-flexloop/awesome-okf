# 概念文档

## 入门篇

* [Podman 简介](00-introduction.md) — 什么是Podman、无守护进程特性、rootless安全模式、与Docker的区别、容器工具生态定位。
* [5分钟快速上手](01-getting-started.md) — 各平台安装方式、验证安装、运行第一个容器、基础命令速览。
* [架构概览](02-architecture-overview.md) — 无守护进程架构、Runtime/Container/Pod三层抽象、ABI/Tunnel双引擎模式、REST API、Buildah/Skopeo分工。

## 核心篇

* [Runtime 运行时](03-runtime.md) — Runtime结构体解析、函数式选项模式、NewRuntime创建流程、crun/conmon组件、XDG环境设置、异步worker。
* [容器基础](04-container-basics.md) — Container结构体、syncContainer()并发安全机制、ContainerState状态、7种Linux命名空间隔离、容器生命周期。
* [Pod 一等公民](05-pod-first-class.md) — Pod作为独立资源、PodConfig配置详解、infra容器设计原理、命名空间共享策略、与Kubernetes Pod对应。

## CLI与命令篇

* [CLI 命令结构](06-cli-structure.md) — Cobra框架、main.go启动流程、rootCmd钩子链、registry命令注册、EngineMode命令过滤机制。
* [容器操作命令](07-container-commands.md) — 36个容器命令分类详解：生命周期管理、状态查询、交互执行、检查点、提交、导入导出、清理。
* [镜像操作命令](08-image-commands.md) — 27个镜像命令分类详解：镜像获取/查询/构建/标记/删除/信任/传输，与Buildah的关系。
* [网络与存储卷](09-network-volume.md) — 网络命令与CNI/netavark栈、rootless网络、卷命令与Volume结构、命名卷vs绑定挂载。

## 高级主题篇

* [无 Root 容器](10-rootless.md) — rootless用户命名空间原理、UID/GID映射、与rootful对比、安全优势、网络栈差异、常见问题。
* [远程连接与 REST API](11-remote-api.md) — ABI/Tunnel双引擎、ContainerEngine/ImageEngine接口抽象、system service、system connection管理、Docker兼容vs原生API、Go bindings。
* [systemd 集成与 Quadlet](12-systemd-quadlet.md) — systemd集成必要性、Quadlet容器→systemd单元生成器、支持的单元类型、单元文件示例、notifyproxy。
* [Kubernetes 集成](13-kubernetes-integration.md) — kube play/generate/apply/down命令、支持的K8s资源类型、本地Podman作为轻量K8s开发环境。

## 生态与工具篇

* [容器工具生态全景](14-ecosystem.md) — Containers组织项目全景、三剑客(Podman+Buildah+Skopeo)协作流程、5个子项目职责分工、社区治理。
* [官方镜像构建](15-image-build.md) — image_build monorepo结构、AIO/Buildah/Podman/Skopeo官方镜像、多架构构建(amd64/arm64/ppc64le/s390x)、quay.io发布、标签策略。
* [自动化与 Machine OS](16-automation-ci.md) — CI自动化脚本、Mac测试池、renovate配置、podman-machine-os虚拟机镜像构建系统、COREOS/WSL镜像、验证测试。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-runtime
04-container-basics
05-pod-first-class
06-cli-structure
07-container-commands
08-image-commands
09-network-volume
10-rootless
11-remote-api
12-systemd-quadlet
13-kubernetes-integration
14-ecosystem
15-image-build
16-automation-ci
```
