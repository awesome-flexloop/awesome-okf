---
okf_version: "0.2"
type: domain-index
title: "容器生态"
description: "容器技术生态——OCI 运行时、存储驱动、Podman 工具链、容器开发环境与 AI 容器配方"
---

# 容器生态

本域存放容器技术相关的开源项目知识包，覆盖容器运行时监控、OCI 规范、存储驱动、Podman Python/Compose 绑定、容器化开发环境、AI 实验室容器配方等核心组件，构成从底层 OCI 规范到上层开发体验的完整容器生态。

## 域内项目列表

| 项目 | 一句话简介 |
|------|-----------|
| [conmon](conmon/index.md) | 容器运行时监控进程——OCI 容器生命周期管理、日志、TTY 附加等核心功能 |
| [conmon-rs](conmon-rs/index.md) | conmon 的 Rust 重写版本——内存安全、性能优化、现代化实现 |
| [fuse-overlayfs](fuse-overlayfs/index.md) | FUSE 用户态 overlay 文件系统——无根容器（rootless）存储驱动实现 |
| [libocispec](libocispec/index.md) | OCI 运行时规范 C 语言库——解析与生成 OCI 规范配置文件 |
| [olot](olot/index.md) | 容器镜像层操作工具——OCI 镜像层管理与转换 |
| [omlmd](omlmd/index.md) | OCI 模型元数据规范——容器化 AI 模型的元数据标准 |
| [podman-py](podman-py/index.md) | Podman Python 绑定——Python 调用 Podman RESTful API |
| [podman-compose](podman-compose/index.md) | Podman Compose 兼容层——Docker Compose 规范的 Podman 实现 |
| [qm](qm/index.md) | QEMU 虚拟机管理工具——容器中运行虚拟机的管理接口 |
| [toolbox](toolbox/index.md) | 容器化开发环境工具——在容器中搭建隔离的开发与调试环境 |
| [ai-lab-recipes](ai-lab-recipes/index.md) | AI 实验室容器配方——预构建的 AI/ML 工作负载容器镜像与最佳实践 |

```{toctree}
:maxdepth: 2

conmon/index
conmon-rs/index
fuse-overlayfs/index
libocispec/index
olot/index
omlmd/index
podman-py/index
podman-compose/index
qm/index
toolbox/index
ai-lab-recipes/index
```
