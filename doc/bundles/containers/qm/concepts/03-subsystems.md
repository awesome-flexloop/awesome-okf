---
type: Concept
title: 子系统扩展（kvm/wayland/ros2）
description: 了解 QM 的可选子系统模块：KVM 虚拟化、Wayland 图形、ROS2 机器人、音频视频等扩展功能
tags: [subsystems, kvm, wayland, ros2, sound, video, oci-hooks]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T16:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T16:00:00+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: subsystem
    resource: /bundles/containers/qm/references/subsystem-source.md
    title: "QM 子系统扩展信源"
---

# 子系统扩展（kvm/wayland/ros2）

QM 采用模块化子系统设计，核心的 QM 容器只提供基础隔离环境，而 KVM 虚拟化、Wayland 图形、ROS 2 机器人框架等功能通过独立的子系统 RPM 包提供。每个子系统有自己的容器镜像、Quadlet 配置和绑定挂载设置。

## 子系统架构概览

子系统采用统一的架构模式：

1. **主机 drop-in 配置**：`etc/containers/systemd/qm.container.d/` 目录下的 `.conf` 文件添加设备绑定挂载
2. **QM 内 Quadlet 服务**：`etc/containers/systemd/` 目录下的 `.container` 文件定义子系统容器
3. **容器镜像构建**：`usr/share/qm/<subsystem>/` 目录下的 ContainerFile 和构建脚本
4. **独立 RPM 打包**：每个子系统有独立的 `.spec` 文件，可单独安装卸载

```
┌─────────────────────────────────────────────────────────────────┐
│ 主机 (Host)                                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ QM 容器 (qm.container)                                    │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 子系统 Quadlet 服务 (在 QM 内运行的嵌套容器)         │  │  │
│  │  │  ├─ kvm.container          → KVM 虚拟化容器          │  │  │
│  │  │  ├─ wayland-compositor.container → Weston 合成器    │  │  │
│  │  │  ├─ qm-dbus-broker.container → D-Bus broker          │  │  │
│  │  │  ├─ ros2.container         → ROS 2 环境              │  │  │
│  │  │  ├─ audio.container        → 音频服务                │  │  │
│  │  │  └─ rear-camera.container  → 后视摄像头              │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  OCI Hooks: qm-device-manager, qm-seat-manager, etc.     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  主机设备绑定: /dev/kvm, /dev/snd, /dev/dri, /dev/video*        │
└─────────────────────────────────────────────────────────────────┘
```

## KVM 子系统

KVM 子系统允许在 QM 内运行硬件加速的虚拟机，用于在隔离环境中运行其他操作系统或实时工作负载。

### 安装

```bash
# 安装 KVM 子系统包（根据发行版）
dnf install qm-kvm
```

### 文件结构

```
subsystems/kvm/
├── etc/containers/systemd/
│   └── kvm.container              # KVM 嵌套容器 Quadlet
├── usr/share/qm/kvm/
│   ├── ContainerFile              # 容器镜像构建文件
│   └── build_kvm_container.sh     # 镜像构建脚本
└── Makefile
```

### 主机配置

安装 KVM 子系统后，会自动在主机添加 drop-in 配置，将 `/dev/kvm` 设备绑定挂载到 QM 内：

- 配置文件：`/etc/containers/systemd/qm.container.d/qm_dropin_mount_bind_kvm.conf`
- 绑定设备：`/dev/kvm`（KVM 硬件虚拟化设备）、`/dev/vhost-net` 等

### 使用方式

在 QM 内启动 KVM 容器：

```bash
# 进入 QM
podman exec -ti qm sh

# 启动 KVM 服务（通过 systemd）
systemctl start kvm

# 或者直接运行 podman 启动 KVM 容器
podman run --rm --device /dev/kvm <kvm-image>
```

## Wayland 子系统

Wayland 子系统提供 Wayland 显示服务器支持，在 QM 隔离环境中运行图形应用，支持 Weston 合成器、GPU 加速等。

### 安装

```bash
dnf install qm-wayland
```

### 文件结构

Wayland 子系统比其他子系统更复杂，包含多个服务：

```
subsystems/wayland/
├── containers/
│   ├── qm-dbus-broker/
│   │   └── Containerfile          # D-Bus broker 容器
│   └── wayland-compositor/
│       └── Containerfile          # Weston 合成器容器
├── etc/
│   ├── containers/systemd/
│   │   ├── qm-dbus-broker.container    # D-Bus Quadlet
│   │   └── wayland-compositor.container # Weston Quadlet
│   ├── pam.d/
│   │   ├── systemd-user
│   │   └── wayland-autologin
│   ├── systemd/system/
│   │   ├── qm-dbus.socket        # D-Bus socket
│   │   ├── wayland-session.service  # Wayland 会话服务
│   │   └── wayland.socket        # Wayland socket
│   └── weston/
│       └── weston.ini            # Weston 合成器配置
├── usr/bin/
│   └── wayland-session           # Wayland 会话启动脚本
├── 50-qm-wayland.preset          # systemd preset 配置
├── Makefile
└── README.md
```

### 核心组件

1. **qm-dbus-broker**：D-Bus 消息总线，用于 Wayland 合成器和应用之间的通信
2. **wayland-compositor**：Weston Wayland 合成器
3. **wayland-session**：PAM 会话管理，处理自动登录
4. **weston.ini**：Weston 配置文件，配置输出、输入设备等

### 主机配置

- 配置文件：`/etc/containers/systemd/qm.container.d/qm_dropin_mount_bind_window_manager.conf`
- 绑定内容：GPU 设备（`/dev/dri/`）、输入设备、Wayland socket 目录等

### 启动 Wayland 图形环境

```bash
# 进入 QM
podman exec -ti qm sh

# 启用并启动 Wayland 相关服务
systemctl enable qm-dbus.socket wayland.socket
systemctl start wayland-session
```

## ROS 2 子系统

ROS 2（Robot Operating System 2）子系统为机器人开发提供隔离的 ROS 2 环境。

### 文件结构

```
subsystems/ros2/
├── etc/containers/systemd/
│   └── ros2.container             # ROS 2 Quadlet 服务
├── usr/share/qm/
│   └── ContainerFile              # ROS 2 容器镜像
└── Makefile
```

### 安装

```bash
dnf install qm-ros2  # 或对应版本的 ROS 2 包（如 ros2-rolling）
```

## Sound（音频）子系统

音频子系统提供声音设备访问支持。

### 文件结构

```
subsystems/sound/
├── etc/containers/systemd/
│   └── audio.container            # 音频服务 Quadlet
├── usr/share/qm/
│   └── ContainerFile
└── Makefile
```

### 主机配置

- 配置文件：`/etc/containers/systemd/qm.container.d/qm_dropin_mount_bind_snd.conf`
- 绑定设备：`/dev/snd/`（ALSA 音频设备）

## Video（视频）子系统

视频子系统提供视频设备访问，支持后视摄像头等汽车场景。

### 文件结构

```
subsystems/video/
├── etc/containers/systemd/
│   └── rear-camera.container      # 后视摄像头 Quadlet
├── usr/share/qm/
│   └── ContainerFile.rear-camera  # 摄像头容器镜像
└── Makefile
```

### 主机配置

- 配置文件：`/etc/containers/systemd/qm.container.d/qm_dropin_mount_bind_video.conf`
- 绑定设备：`/dev/video*`（V4L2 视频设备）

## Text-to-Speech（文本转语音）子系统

```
subsystems/text2speech/
└── Makefile
```

## OCI Hooks

除了子系统模块，QM 还包含 OCI runtime hooks，在容器启动/停止时执行自定义逻辑。

### Hook 列表

| Hook | 功能 |
|------|------|
| qm-device-manager | 设备管理 hook，配置容器的设备访问权限 |
| qm-seat-manager | Seat 管理 hook，处理图形会话 seat 分配 |
| wayland-client-devices | Wayland 客户端设备 hook，配置 Wayland 应用的设备访问 |

### Hook 文件位置

```
oci-hooks/
├── lib/
│   ├── common.sh                  # 共享 Shell 函数库
│   ├── device-support.sh          # 设备支持库
│   └── mock-device-support.sh     # 测试用 mock 设备库
├── qm-device-manager/
│   ├── README.md
│   ├── oci-qm-device-manager      # Hook 执行脚本
│   └── oci-qm-device-manager.json # Hook 配置（匹配条件等）
├── qm-seat-manager/
│   ├── oci-qm-seat-manager.json
│   └── ...
├── wayland-client-devices/
│   ├── README.md
│   ├── oci-qm-wayland-client-devices
│   └── oci-qm-wayland-client-devices.json
└── tests/                         # pytest 测试套件
```

### Hook 配置示例

oci-hooks JSON 配置定义何时执行 hook：

```json
{
  "version": "1.0.0",
  "hook": {
    "path": "/usr/libexec/oci/hooks.d/oci-qm-device-manager",
    "args": ["oci-qm-device-manager"],
    "env": []
  },
  "when": {
    "annotations": {
      "org.containers.qm.device": "*"
    }
  },
  "stages": ["createRuntime"]
}
```

## 子系统安装与管理

### 查看可用子系统包

```bash
# 列出所有 qm 相关包
dnf list qm-*
```

### 安装/卸载子系统

```bash
# 安装 KVM 子系统
dnf install qm-kvm

# 安装 Wayland 子系统
dnf install qm-wayland

# 卸载子系统
dnf remove qm-kvm
```

### 重启 QM 应用子系统配置

安装/卸载子系统后需要重启 QM：

```bash
systemctl daemon-reload
systemctl restart qm.service
```

## 相关概念

- [嵌套隔离架构](/bundles/containers/qm/concepts/01-nested-architecture.md)：了解子系统如何作为嵌套容器运行在 QM 内
- [KVM 子系统使用](/bundles/containers/qm/examples/02-kvm-subsystem.md)：KVM 子系统的实战使用示例
- [创建 QM 虚拟机环境](/bundles/containers/qm/examples/01-vm-setup.md)：在虚拟机中测试包含子系统的 QM 环境
