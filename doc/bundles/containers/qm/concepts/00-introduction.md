---
type: Concept
title: QM 定位与 ASIL 汽车功能安全场景
description: 了解 QM（Quality Management）是什么、解决什么问题，以及在汽车 ASIL 功能安全场景中的应用
tags: [introduction, asil, automotive, safety, overview]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T16:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T16:00:00+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /bundles/containers/qm/references/readme-source.md
    title: "QM 项目 README 与 man 手册信源"
---

# QM 定位与 ASIL 汽车功能安全场景

QM（Quality Management，质量管理）是一个容器化运行环境，专门用于在汽车功能安全场景中运行质量管理软件，防止非安全关键进程干扰 ASIL（Automotive Safety Integrity Level，汽车安全完整性等级）安全关键进程。

> **注意**：AutoSD 不是经过认证的安全产品。在 AutoSD 环境中，QM 仅用于研究和学习目的，不适用于生产环境。

## ASIL 安全等级简介

ASIL 是 ISO 26262 标准定义的汽车安全完整性等级，分为 A（最低）到 D（最高）四个等级，外加 QM（质量管理）等级：

| 等级 | 说明 | 进程要求 |
|------|------|---------|
| ASIL D | 最高安全等级（如制动、转向） | 绝对不能被干扰，OOM 免疫 |
| ASIL B/C | 中等安全等级 | 严格隔离，低 OOM 分数 |
| ASIL A | 最低安全等级 | 基本隔离 |
| QM | 质量管理（非安全关键） | 可被优先终止，不影响安全 |

QM 环境的核心目标就是在同一硬件平台上运行 QM 等级的非安全关键软件，同时通过强隔离机制确保其不会干扰 ASIL 等级的安全关键进程。

## QM 解决什么问题

在汽车电子电气架构中，域控制器需要同时运行多个不同安全等级的软件：

1. **混合关键性系统**：同一硬件上运行安全关键（ASIL）和非安全关键（QM）软件
2. **干扰防护**：防止 QM 软件的 bug、内存泄漏、资源耗尽影响 ASIL 进程
3. **容器工具隔离**：不仅隔离应用，还要隔离 systemd、Podman 等容器工具本身
4. **独立软件生态**：QM 内可以有独立的软件包、独立的 init 系统

传统容器只隔离应用，但 QM 的隔离更彻底——它连 systemd 和 Podman 都有自己独立的版本。

## QM 核心隔离技术

QM 使用多层隔离技术实现"免于干扰"（Freedom from Interference, FFI）：

| 隔离层 | 技术 | 作用 |
|--------|------|------|
| 资源隔离 | cgroups v2 | 限制 CPU、内存、IO 资源使用 |
| 视图隔离 | Linux namespaces | 独立的 PID、mount、network、UTS 命名空间 |
| 强制访问控制 | SELinux | QM 进程运行在独立的 `qm_t` 域 |
| OOM 优先级 | oom_score_adj | 内存不足时 QM 进程优先被终止 |
| 嵌套容器 | Podman in Podman | QM 内可进一步运行嵌套容器隔离应用 |

## 典型使用场景

- **汽车座舱域**：运行信息娱乐、导航等 QM 等级应用，与仪表、ADAS 等 ASIL 应用隔离
- **功能安全研究**：在 AutoSD 上研究混合关键性系统的隔离技术
- **容器化工作负载**：在嵌入式汽车环境中使用 Podman 和 systemd 管理容器
- **多节点编排**：通过 BlueChi 管理分布式汽车 ECU 节点上的服务

## QM 环境架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        主机 (Host)                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    QM 容器 (qm.container)              │  │
│  │  oom_score_adj=500, SELinux=qm_t                       │  │
│  │                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │ QM systemd   │  │ QM Podman    │  │ bluechi-agent│ │  │
│  │  │ (独立版本)    │  │ (独立版本)    │  │ (节点名 qm.*)│ │  │
│  │  └──────────────┘  └──────┬───────┘  └──────────────┘ │  │
│  │                            │                           │  │
│  │              ┌─────────────┴─────────────┐             │  │
│  │              v                           v             │  │
│  │  ┌──────────────────┐        ┌──────────────────┐      │  │
│  │  │ 嵌套容器 1       │        │ 嵌套容器 2       │      │  │
│  │  │ oom_score_adj=750│        │ oom_score_adj=750│      │  │
│  │  └──────────────────┘        └──────────────────┘      │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              ASIL 应用 (主机直接运行)                  │  │
│  │  oom_score_adj=-1 ~ -1000, SELinux=asil_t            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 相关概念

- [嵌套隔离架构](/bundles/containers/qm/concepts/01-nested-architecture.md)：了解容器→systemd→Podman→嵌套容器的多层隔离架构
- [三级 OOM 策略与 SELinux 隔离](/bundles/containers/qm/concepts/02-oom-selinux.md)：了解内存不足时的进程优先级和强制访问控制
- [子系统扩展](/bundles/containers/qm/concepts/03-subsystems.md)：了解 KVM、Wayland、ROS2 等可选子系统
- [BlueChi 多节点管理](/bundles/containers/qm/concepts/04-bluechi.md)：了解多节点环境下的服务管理
