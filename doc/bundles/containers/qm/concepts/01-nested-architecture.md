---
type: Concept
title: 嵌套隔离架构
description: 深入理解 QM 的多层嵌套隔离：主机→QM容器→systemd→Podman→嵌套容器的完整架构
tags: [architecture, nested, container, systemd, podman, isolation]
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

# 嵌套隔离架构

QM 采用深度嵌套的隔离架构，不仅在容器级别隔离应用，还在容器内运行独立的 systemd init 系统和 Podman 容器引擎，实现工具链层面的彻底隔离。这种"容器中的容器中的 systemd 中的容器"架构是 QM 区别于普通容器的核心特征。

## 架构层级详解

QM 环境包含四个主要的隔离层级：

### 第一层：主机 OS（Host OS）

最底层是主机操作系统（如 CentOS Automotive Stream Distribution），直接运行在硬件上：

- 主机的 systemd（PID 1）管理所有主机服务
- 主机的 Podman 负责启动 QM 容器
- ASIL 安全关键应用直接运行在主机上（或独立容器中）
- 主机 SELinux 策略控制全局访问权限

### 第二层：QM 容器（qm.container）

QM 本身是一个通过 Podman Quadlet 管理的特权容器：

- **Quadlet 配置**：`/usr/share/containers/systemd/qm.container`
- **Rootfs 位置**：`/usr/lib/qm/rootfs/`（独立的根文件系统）
- **SELinux 域**：`qm_t`
- **默认 OOM 分数**：`oom_score_adj=500`
- **默认丢弃能力**：`DropCapability=sys_boot`（不含 `SYS_RESOURCE`）
- **服务管理**：通过 systemd 管理，服务名 `qm.service`

```ini
# qm.container 关键配置（节选）
[Container]
ContainerName=qm
Rootfs=/usr/lib/qm/rootfs
# DropCapability=sys_boot  # 默认丢弃 sys_boot 能力
# OOMScoreAdjust=500       # 默认 OOM 分数调整
```

### 第三层：QM 内的独立用户空间

QM 容器内运行完整的独立用户空间，不共享主机的 systemd 和 Podman：

- **独立的 systemd**：QM 内 PID 1 是 QM 自己的 systemd（`/sbin/init`）
- **独立的 Podman**：QM 内安装并运行独立版本的 Podman
- **独立的包管理**：使用 `dnf --installroot=/usr/lib/qm/rootfs` 安装包
- **独立的配置**：`/etc/` 目录下的配置与主机隔离
- **bluechi-agent**：运行独立的 BlueChi agent，节点名带 `qm.` 前缀

进入 QM 环境验证独立用户空间：

```bash
# 从主机进入 QM
podman exec -ti qm sh

# 在 QM 内验证
sh-5.2# id -Z
system_u:system_r:qm_t:s0:c35,c404  # SELinux 域是 qm_t

sh-5.2# ps -p 1
PID  TTY          TIME CMD
  1 ?        00:00:01 systemd         # QM 内 PID 1 是独立的 systemd

sh-5.2# which podman
/usr/bin/podman                     # QM 内有自己的 podman
```

### 第四层：QM 内的嵌套容器

在 QM 内可以使用 Podman 运行嵌套容器，实现应用级隔离：

- **默认 OOM 分数**：`oom_score_adj=750`（比 QM 容器更容易被 OOM 终止）
- **容器配置**：`/usr/lib/qm/rootfs/usr/share/qm/containers.conf`
- **推荐方式**：使用 Quadlet 在 QM 内管理嵌套容器
- **网络**：默认可以配置为独立网络或共享主机网络

在 QM 内运行嵌套容器：

```bash
# 在 QM 内运行嵌套容器
sh-5.2# podman run --rm ubi9-minimal echo hi
Resolved "ubi9-minimal" as an alias
Trying to pull registry.access.redhat.com/ubi9-minimal:latest...
...
hi
```

## 完整嵌套架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│  HARDWARE (物理硬件)                                                 │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│  HOST OS (主机操作系统)                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Host systemd (PID 1)                                        │   │
│  │ ├─ ASIL 进程 (oom_score_adj=-1000, SELinux=asil_t)         │   │
│  │ ├─ podman (主机 Podman)                                     │   │
│  │ └─ qm.service (Podman Quadlet 生成的服务)                   │   │
│  │    └─ conmon → 启动 QM 容器                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         ▲ SELinux: 容器运行在 container_t，转换到 qm_t              │
│         │ oom_score_adj=500                                        │
└─────────┼───────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────────────┐
│  QM CONTAINER (qm.container)                                        │
│  Rootfs: /usr/lib/qm/rootfs/                                        │
│  SELinux: qm_t                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ QM systemd (PID 1 in container) - 独立版本!                  │   │
│  │ ├─ dbus-broker.service                                      │   │
│  │ ├─ systemd-journald.service                                 │   │
│  │ ├─ bluechi-agent.service (node name: qm.<hostname>)         │   │
│  │ ├─ podman.socket (QM 内独立的 Podman socket)                │   │
│  │ └─ 用户 Quadlet 服务（嵌套容器）                             │   │
│  │    ├─ kvm.container (KVM 子系统)                             │   │
│  │    ├─ wayland-compositor.container (Wayland)               │   │
│  │    └─ 自定义 .container 文件                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         ▲ 注意：这是 QM 内独立安装的 Podman，不是主机的！           │
│         │ oom_score_adj=750（默认）                                 │
└─────────┼───────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────────────┐
│  NESTED CONTAINERS (QM 内的嵌套容器)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Nested 1     │  │ Nested 2     │  │ Nested 3     │              │
│  │ oom=750      │  │ oom=自定义    │  │ oom=750      │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

## Rootfs 软件安装

QM 的独立根文件系统位于 `/usr/lib/qm/rootfs/`，安装软件有两种方式：

### 方式一：从主机使用 dnf --installroot

```bash
# 主机上执行，安装到 QM rootfs
dnf install --installroot=/usr/lib/qm/rootfs <package-name>

# 例如：在 QM 内安装 dnf
dnf install --installroot=/usr/lib/qm/rootfs dnf
```

### 方式二：进入 QM 后使用 dnf（如果已安装）

```bash
podman exec -ti qm sh
# 在 QM 内
dnf install <package-name>
```

## Quadlet 配置层级

Quadlet 配置文件可以放在多个位置，优先级不同：

| 位置 | 作用域 | 用途 |
|------|--------|------|
| `/usr/share/containers/systemd/` | 系统（包安装） | QM 主容器默认配置 |
| `/etc/containers/systemd/qm.container.d/` | 主机系统 | 修改 QM 主容器配置的 drop-in |
| `/usr/lib/containers/systemd/qm.container.d/` | 主机系统 | 包安装的 QM drop-in |
| `/usr/lib/qm/rootfs/etc/containers/systemd/` | QM 内部 | QM 内的嵌套容器 Quadlet |
| `/etc/qm/containers/systemd/` | QM 内部 | 管理员自定义的嵌套容器 |

创建 QM drop-in 配置示例：

```bash
# 修改 QM 内存限制
mkdir -p /etc/containers/systemd/qm.container.d/

cat > /etc/containers/systemd/qm.container.d/100-MemoryMax.conf << EOF
[Service]
MemoryHigh=2G
EOF

systemctl daemon-reload
systemctl restart qm.service
```

## 为什么需要嵌套 systemd 和 Podman

普通容器通常只隔离应用，共享主机的 systemd 和容器运行时。但在功能安全场景下：

1. **工具链隔离**：防止 QM 内的 systemctl/podman 命令误操作主机服务
2. **配置隔离**：QM 内的容器配置（registries.conf、storage.conf）与主机独立
3. **版本独立**：QM 内可以运行不同版本的 Podman/systemd，不影响主机
4. **故障隔离**：QM 内 Podman 崩溃不会影响主机容器运行时
5. **安全纵深防御**：即使 QM 内容器逃逸，仍在 qm_t SELinux 域内

## 相关概念

- [QM 定位与 ASIL 汽车功能安全场景](00-introduction.md)：了解 QM 解决的核心问题
- [三级 OOM 策略与 SELinux 隔离](02-oom-selinux.md)：了解内存和访问控制隔离
- [子系统扩展](03-subsystems.md)：了解预构建的子系统容器
- [BlueChi 多节点管理](04-bluechi.md)：了解 QM 内的 BlueChi agent
