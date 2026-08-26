# QM 概念文档索引

按学习路径排列的核心概念文档：

| 序号 | 主题 | 说明 |
|------|------|------|
| 00 | [QM 定位与 ASIL 汽车功能安全场景](/bundles/containers/qm/concepts/00-introduction.md) | QM 项目介绍、解决的问题、ASIL 功能安全场景、核心隔离技术概览 |
| 01 | [嵌套隔离架构](/bundles/containers/qm/concepts/01-nested-architecture.md) | 主机→QM容器→systemd→Podman→嵌套容器的四层嵌套架构详解，Rootfs管理，Quadlet配置层级 |
| 02 | [三级 OOM 策略与 SELinux 隔离](/bundles/containers/qm/concepts/02-oom-selinux.md) | 内存安全机制：三级oom_score_adj策略、SELinux qm_t域、Capabilities权限边界、排障方法 |
| 03 | [子系统扩展（kvm/wayland/ros2）](/bundles/containers/qm/concepts/03-subsystems.md) | 可选子系统模块：KVM虚拟化、Wayland图形、ROS2机器人、音频视频、OCI Hooks架构 |
| 04 | [BlueChi 多节点管理](/bundles/containers/qm/concepts/04-bluechi.md) | BlueChi确定性服务控制器、多节点架构、QM节点命名规则、配置同步、汽车ECU场景 |

## 概念依赖关系

```
00-introduction（入门必读）
    ├── 01-nested-architecture（架构基础）
    │       ├── 02-oom-selinux（安全机制）
    │       └── 03-subsystems（扩展功能）
    └── 04-bluechi（多节点管理）
```

**推荐学习顺序**：00 → 01 → 02 → 03/04（03 和 04 可并行阅读）。
