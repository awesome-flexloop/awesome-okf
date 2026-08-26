---
type: Reference
title: QM 子系统扩展信源
description: QM subsystems/ 目录下的子系统模块，包括 kvm、wayland、ros2、sound、video、text2speech、qm-oci-hooks 等
tags: [subsystems, kvm, wayland, ros2, oci-hooks, sound, video]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T16:00:00+08:00"
verified:
  by: "process:source-verification"
  at: "2026-08-26T16:00:00+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: subsystems
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/subsystems/"
    title: "subsystems/ 子系统目录"
  - id: kvm-subsystem
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/subsystems/kvm/"
    title: "kvm 子系统"
  - id: wayland-subsystem
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/subsystems/wayland/"
    title: "wayland 子系统"
  - id: oci-hooks
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/qm/oci-hooks/"
    title: "OCI hooks 目录"
---

# QM 子系统扩展信源

## 信源内容摘要

本信源来自 QM 项目 `subsystems/` 目录和 `oci-hooks/` 目录下的子系统模块实现。

### 子系统列表

`subsystems/` 目录包含以下子系统模块，每个子系统有独立的 Makefile：

| 子系统 | 功能 | 关键文件 |
|--------|------|---------|
| kvm | KVM 虚拟化支持 | kvm.container Quadlet、ContainerFile、build_kvm_container.sh |
| wayland | Wayland 图形合成器支持 | weston.ini、wayland-session、多个 Quadlet 文件、Containerfile |
| ros2 | ROS 2 机器人操作系统支持 | ros2.container Quadlet、ContainerFile |
| sound | 音频支持 | audio.container Quadlet、ContainerFile |
| video | 视频支持（后视摄像头等） | rear-camera.container Quadlet、ContainerFile.rear-camera |
| text2speech | 文本转语音支持 | Makefile |
| qm-oci-hooks | QM OCI hooks 集成 | Makefile |

### KVM 子系统

KVM 子系统文件结构：

```
subsystems/kvm/
├── etc/containers/systemd/kvm.container    # Quadlet 服务文件
├── usr/share/qm/kvm/
│   ├── ContainerFile                       # 容器构建文件
│   └── build_kvm_container.sh              # 构建脚本
└── Makefile
```

主机 drop-in 配置（`etc/containers/systemd/qm.container.d/`）：
- `qm_dropin_mount_bind_kvm.conf` - KVM 设备绑定挂载

### Wayland 子系统

Wayland 子系统提供 Weston 合成器支持，文件结构：

```
subsystems/wayland/
├── containers/
│   ├── qm-dbus-broker/Containerfile        # D-Bus broker 容器
│   └── wayland-compositor/Containerfile    # Wayland 合成器容器
├── etc/
│   ├── containers/systemd/
│   │   ├── qm-dbus-broker.container        # D-Bus broker Quadlet
│   │   └── wayland-compositor.container    # 合成器 Quadlet
│   ├── pam.d/                              # PAM 配置
│   │   ├── systemd-user
│   │   └── wayland-autologin
│   ├── systemd/system/                     # systemd 单元
│   │   ├── qm-dbus.socket
│   │   ├── wayland-session.service
│   │   └── wayland.socket
│   └── weston/weston.ini                   # Weston 配置
├── usr/bin/wayland-session                 # Wayland 会话二进制
├── 50-qm-wayland.preset                    # systemd preset
├── Makefile
└── README.md
```

主机 drop-in 配置：
- `qm_dropin_mount_bind_window_manager.conf` - 窗口管理器绑定挂载

### 其他子系统

- **sound**：`audio.container` Quadlet，主机 drop-in `qm_dropin_mount_bind_snd.conf`
- **video**：`rear-camera.container` Quadlet，主机 drop-in `qm_dropin_mount_bind_video.conf`
- **ros2**：`ros2.container` Quadlet，用于 ROS 2 机器人开发

### OCI Hooks

`oci-hooks/` 目录包含 OCI runtime hooks：

| Hook | 功能 |
|------|------|
| qm-device-manager | 设备管理 hook，配置设备访问权限 |
| qm-seat-manager | Seat 管理 hook |
| wayland-client-devices | Wayland 客户端设备 hook |

hooks 目录还包含：
- `lib/common.sh`、`lib/device-support.sh` - 共享 Shell 库
- 完整的 pytest 测试套件（tests/ 目录）

### RPM 打包

每个子系统在 `rpm/` 目录下有独立的 spec 文件：
- `rpm/kvm/qm-kvm.spec`
- `rpm/wayland/qm-wayland.spec`
- `rpm/ros2/ros2_rolling.spec`
- `rpm/sound/sound.spec`
- `rpm/video/video.spec`
- `rpm/text2speech/text2speech.spec`
- `rpm/oci-hooks/qm-oci-hooks.spec`
