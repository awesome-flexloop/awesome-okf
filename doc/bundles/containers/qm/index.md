---
okf_version: "0.2"
type: Index
title: QM - Quality Management 容器化环境
description: QM 是用于汽车 ASIL 功能安全场景的容器化隔离环境，通过多层嵌套容器、SELinux、OOM 策略实现免于干扰，支持 KVM/Wayland/ROS2 等子系统和 BlueChi 多节点管理
tags: [qm, containers, podman, systemd, asil, automotive, safety, selinux, bluechi, kvm, wayland]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T16:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T16:00:00+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: facts
    resource: "file:///d:/spaces/SpecWeave/.trae/specs/containers-okf-wiki/facts-qm.md"
    title: "QM 项目事实清单"
  - id: readme
    resource: /bundles/containers/qm/references/readme-source.md
    title: "QM 项目 README 与 man 手册信源"
  - id: qmctl
    resource: /bundles/containers/qm/references/qmctl-source.md
    title: "qmctl 管理工具信源"
  - id: subsystem
    resource: /bundles/containers/qm/references/subsystem-source.md
    title: "QM 子系统扩展信源"
---

# QM - Quality Management 容器化环境

**QM**（Quality Management，质量管理）是一个专门为汽车功能安全场景设计的容器化隔离环境。它在同一硬件平台上运行非安全关键（QM 等级）软件的同时，通过多层容器隔离、SELinux 强制访问控制、三级 OOM 优先级策略等机制，确保 QM 进程不会干扰 ASIL（Automotive Safety Integrity Level）安全关键进程，实现"免于干扰"（Freedom from Interference, FFI）。

## 核心特性

- ✅ **深度嵌套隔离**：主机→QM容器→独立systemd→独立Podman→嵌套容器，四层隔离架构
- ✅ **SELinux 强访问控制**：QM 进程运行在独立的 `qm_t` 域，容器与 QM 进程互相隔离
- ✅ **三级 OOM 策略**：QM容器(500)→嵌套容器(750)→ASIL应用(-1000)，内存不足时安全进程最后终止
- ✅ **独立用户空间**：QM 内运行独立版本的 systemd 和 Podman，工具链彻底隔离
- ✅ **BlueChi 多节点支持**：内置 bluechi-agent，节点名自动加 `qm.` 前缀，支持汽车 ECU 多节点编排
- ✅ **模块化子系统**：可选 KVM 虚拟化、Wayland 图形、ROS2 机器人、音频视频等扩展
- ✅ **qmctl 管理工具**：提供 Python 编写的 CLI 工具，用于检查、执行命令、文件复制

## 快速开始

### 安装 QM

```bash
# CentOS Stream 9 / AutoSD
dnf install -y python3-dnf-plugins-core
dnf config-manager --set-enabled crb
dnf install -y qm

# 初始化 QM 环境（安装 rootfs 包、启动服务）
/usr/share/qm/setup
```

### 验证安装

```bash
# 检查 QM 服务状态
systemctl status qm.service

# 进入 QM 环境
podman exec -ti qm sh

# 在 QM 内验证隔离环境
sh-5.2# id -Z
system_u:system_r:qm_t:s0:...  # SELinux 域是 qm_t
sh-5.2# podman run --rm ubi9-minimal echo "Hello from nested container!"
```

### 基本操作

```bash
# 在 QM 内安装额外软件包
dnf --installroot=/usr/lib/qm/rootfs install <package>

# 使用 qmctl 工具
qmctl show all              # 显示所有 QM 信息
qmctl exec uname -a         # 在 QM 内执行命令
qmctl cp file qm:/tmp/      # 复制文件到 QM
```

## 文档导航

### [概念文档 Concepts](/bundles/containers/qm/concepts/index.md)

按学习路径排列的核心概念：

| 主题 | 说明 |
|------|------|
| [QM 定位与 ASIL 汽车功能安全场景](/bundles/containers/qm/concepts/00-introduction.md) | 项目介绍、ASIL 安全等级、解决的问题、核心隔离技术概览 |
| [嵌套隔离架构](/bundles/containers/qm/concepts/01-nested-architecture.md) | 主机→QM容器→systemd→Podman→嵌套容器四层架构详解、Rootfs 管理、Quadlet 配置层级 |
| [三级 OOM 策略与 SELinux 隔离](/bundles/containers/qm/concepts/02-oom-selinux.md) | 三级 oom_score_adj 策略、SELinux qm_t 域、Capabilities 权限边界、自定义 OOM 配置 |
| [子系统扩展（kvm/wayland/ros2）](/bundles/containers/qm/concepts/03-subsystems.md) | KVM 虚拟化、Wayland 图形、ROS2 机器人、音频视频、OCI Hooks 架构详解 |
| [BlueChi 多节点管理](/bundles/containers/qm/concepts/04-bluechi.md) | BlueChi 确定性服务控制器、多节点架构、QM 节点命名规则、汽车 ECU 场景 |

### [示例文档 Examples](/bundles/containers/qm/examples/index.md)

可直接复制使用的实战示例：

| 示例 | 说明 |
|------|------|
| [创建 QM 虚拟机环境](/bundles/containers/qm/examples/01-vm-setup.md) | QEMU/KVM 虚拟机中安装 AutoSD、部署 QM、验证环境、使用 qmctl 的完整步骤 |
| [KVM 子系统使用](/bundles/containers/qm/examples/02-kvm-subsystem.md) | KVM 子系统安装、嵌套虚拟化配置、运行 QEMU 虚拟机、libvirt 管理、性能对比 |

### [信源 References](/bundles/containers/qm/references/index.md)

所有文档内容的可验证信源：

| 信源 | 内容 |
|------|------|
| [readme-source.md](/bundles/containers/qm/references/readme-source.md) | 官方 README.md 和 qm.8.md man 手册：安装、SELinux、BlueChi、OOM 策略 |
| [qmctl-source.md](/bundles/containers/qm/references/qmctl-source.md) | qmctl CLI 工具：show/exec/execin/cp 命令、Python 实现、辅助 Shell 脚本 |
| [subsystem-source.md](/bundles/containers/qm/references/subsystem-source.md) | 子系统模块：kvm/wayland/ros2/sound/video 结构、OCI Hooks、RPM 打包 |

## 项目结构

```
qm/
├── qm.container                  # QM Quadlet 主配置
├── qm.te, qm.if, qm.fc          # SELinux 策略模块
├── setup                         # QM 初始化设置脚本
├── containers.conf               # 容器默认配置（嵌套容器 OOM 等）
├── etc/                          # 默认配置 drop-in
│   └── containers/systemd/qm.container.d/
│       ├── qm_dropin_mount_bind_kvm.conf
│       ├── qm_dropin_mount_bind_snd.conf
│       ├── qm_dropin_mount_bind_video.conf
│       └── qm_dropin_mount_bind_window_manager.conf
├── subsystems/                   # 可选子系统模块
│   ├── kvm/                      # KVM 虚拟化子系统
│   ├── wayland/                  # Wayland 图形子系统
│   ├── ros2/                     # ROS 2 机器人子系统
│   ├── sound/                    # 音频子系统
│   ├── video/                    # 视频子系统
│   ├── text2speech/              # 文本转语音子系统
│   └── qm-oci-hooks/             # OCI hooks 集成
├── oci-hooks/                    # OCI runtime hooks
│   ├── qm-device-manager/        # 设备管理 hook
│   ├── qm-seat-manager/          # Seat 管理 hook
│   └── wayland-client-devices/   # Wayland 设备 hook
├── tools/                        # 工具
│   ├── qmctl/                    # qmctl Python CLI 工具
│   │   ├── qmctl.py              # Python 实现
│   │   ├── qmctl                 # Shell 包装脚本
│   │   ├── qmctl.1               # man 手册
│   │   └── README.md
│   ├── qm-rootfs                 # 输出 rootfs 位置
│   ├── qm-storage-settings       # 存储配置
│   ├── qm-is-ostree              # OSTree 检测
│   └── ...
├── rpm/                          # RPM spec 文件
│   ├── qm.spec                   # 主包 spec
│   ├── kvm/qm-kvm.spec
│   ├── wayland/qm-wayland.spec
│   └── ...
├── tests/                        # 测试套件（FFI、e2e、sanity）
└── docs/                         # 项目文档
```

## 三级 OOM 保护架构

QM 通过 `oom_score_adj` 实现内存压力下的进程优先级保护：

```
内存不足时终止顺序（从先到后）：
1. QM 内嵌套容器    (oom_score_adj=750)  ← 最先被终止
2. QM 容器本身      (oom_score_adj=500)
3. 主机普通进程     (oom_score_adj=0)
4. ASIL 安全应用    (oom_score_adj=-1000) ← 永不被 OOM 终止
```

## 适用场景

- 汽车座舱域控制器：信息娱乐/导航等 QM 应用与仪表/ADAS 等 ASIL 应用混合运行
- 功能安全研究：在 AutoSD 上研究混合关键性系统的隔离技术
- 嵌入式容器工作负载：在资源受限的嵌入式环境使用 Podman + systemd
- 多节点 ECU 编排：通过 BlueChi 管理分布式汽车节点上的服务
- 嵌套虚拟化：在隔离容器中运行 KVM 虚拟机

## 相关项目

| 项目 | 关系 |
|------|------|
| [Podman](https://podman.io/) | QM 使用 Podman 作为容器运行时 |
| [systemd](https://systemd.io/) | QM 内运行独立的 systemd 作为 init |
| [Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) | QM 通过 Quadlet 管理容器服务 |
| [BlueChi](https://github.com/eclipse-bluechi/bluechi) | QM 内置 BlueChi agent 用于多节点管理 |
| [CentOS Automotive SIG](https://wiki.centos.org/SpecialInterestGroup/Automotive) | AutoSD（Automotive Stream Distribution）发行版 |

## 更新日志

完整变更记录见 [log.md](/bundles/containers/qm/log.md)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
