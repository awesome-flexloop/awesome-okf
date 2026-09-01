---
type: Concept
title: 三级 OOM 策略与 SELinux 隔离
description: 深入理解 QM 的内存安全机制：三级 OOM 分数调整策略和 SELinux 强制访问控制隔离
tags: [oom, selinux, memory, security, isolation, cgroups]
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

# 三级 OOM 策略与 SELinux 隔离

QM 通过两种核心机制实现内存安全和访问控制隔离：**三级 OOM 分数调整策略**确保内存不足时安全关键进程最后被终止，**SELinux 强制访问控制**从内核层面限制 QM 进程的权限边界。

## OOM Killer 基础

Linux 内核的 Out-of-Memory (OOM) Killer 是内存管理子系统的一部分，当系统内存严重不足时，它会选择终止一些进程来释放内存。每个进程有一个 `oom_score_adj` 参数（范围 -1000 到 1000）：

- **值越高**：进程越容易被 OOM Killer 选中终止
- **值越低**：进程越不容易被终止
- **-1000**：进程对 OOM Killer 免疫，永远不会被终止
- **0**：默认值，普通优先级

查看进程的 OOM 分数：

```bash
# 查看指定进程的 oom_score_adj
cat /proc/<PID>/oom_score_adj
```

## QM 三级 OOM 策略

QM 为不同层级的进程设置了不同的 `oom_score_adj`，形成三级保护策略：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        内核空间 (Kernel Space)                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    OOM Killer 机制                          │   │
│  └─────────────────────────────┬───────────────────────────────┘   │
│                                │                                   │
│  ┌─────────────────────────────▼───────────────────────────────┐   │
│  │                    内核调度器 (Kernel Scheduler)             │   │
│  └─────────────────────────────┬───────────────────────────────┘   │
└────────────────────────────────┼────────────────────────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────────┐
│                        用户空间 (User Space)                        │
│  ┌─────────────────────────────▼───────────────────────────────┐   │
│  │              oom_score_adj (OOM 分数调整)                    │   │
│  └───────┬──────────────────┬──────────────────┬────────────────┘  │
│          │                  │                  │                    │
│          ▼                  ▼                  ▼                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐│
│  │ QM 容器      │  │ QM 嵌套容器   │  │ ASIL 应用    │  │其他进程 ││
│  │ oom=500      │  │ oom=750      │  │ oom=-1~-1000 │  │ oom=0  ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────┬────┘│
│         │                 │                  │               │      │
│         ▼                 ▼                  ▼               ▼      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐│
│  │ 较低终止优先级│  │ 较高终止优先级│  │ 极低终止优先级│  │默认优先级││
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 第一级：QM 容器（oom_score_adj=500）

QM 主容器本身的 OOM 分数设置为 500：

- **配置位置**：`/usr/share/containers/systemd/qm.container`
- **配置项**：`OOMScoreAdjust=500`
- **含义**：比普通进程（oom=0）更容易被终止，但比嵌套容器安全

```bash
# 查看 QM 容器的 OOM 配置
cat /usr/share/containers/systemd/qm.container | grep OOMScoreAdjust
# 输出: OOMScoreAdjust=500
```

### 第二级：QM 内嵌套容器（oom_score_adj=750）

在 QM 内运行的所有嵌套容器默认 OOM 分数为 750：

- **配置位置**：`/usr/share/qm/containers.conf`
- **配置项**：`oom_score_adj = 750`
- **含义**：嵌套容器是内存压力下最先被终止的对象，优先保护 QM 主环境和 ASIL 进程

```bash
# 在 QM 内查看嵌套容器默认 OOM 配置
cat /usr/share/qm/containers.conf | grep oom_score_adj
# 输出: oom_score_adj = 750
```

### 第三级：ASIL 应用（oom_score_adj=-1 ~ -1000）

ASIL 安全关键应用可以设置负的 OOM 分数：

- **推荐值**：-1000（完全免疫 OOM Killer）
- **含义**：ASIL 应用是最后被终止的，-1000 表示永远不会被 OOM Killer 终止
- **设置位置**：ASIL 应用的 systemd 服务文件或容器配置

### 终止优先级顺序

当系统内存不足时，OOM Killer 按以下顺序选择终止进程（从先到后）：

1. **QM 内嵌套容器**（oom=750）- 最先终止
2. **QM 容器本身**（oom=500）- 其次终止
3. **主机普通进程**（oom=0）- 然后终止
4. **ASIL 应用**（oom=-1~-1000）- 最后终止（-1000 永不终止）

## 自定义嵌套容器 OOM 分数

自定义嵌套容器的 OOM 分数需要两步：**创建嵌套容器配置**和**添加 SYS_RESOURCE 能力**。

> **注意**：QM 默认丢弃了 `SYS_RESOURCE` 能力，自定义 OOM 分数需要添加此能力，请评估安全风险后操作。

### 步骤 1：创建嵌套容器 Quadlet 配置

在主机上创建 QM 内的嵌套容器配置（通过绑定挂载自动同步到 QM 内）：

```bash
# 创建第一个嵌套容器配置
mkdir -p /etc/qm/containers/systemd/

cat > /etc/qm/containers/systemd/nested.container << EOF
[Container]
ContainerName=nested
Image=alpine:latest
Exec=sleep 1d
Network=none

[Service]
OOMScoreAdjust=1000
EOF

# 创建第二个嵌套容器配置（不同 OOM 分数）
cat > /etc/qm/containers/systemd/nested2.container << EOF
[Container]
ContainerName=nested2
Image=alpine:latest
Exec=sleep 1d
Network=none

[Service]
OOMScoreAdjust=100
EOF
```

### 步骤 2：为 QM 添加 SYS_RESOURCE 能力

创建 QM 主容器的 drop-in 配置：

```bash
mkdir -p /etc/containers/systemd/qm.container.d/

cat > /etc/containers/systemd/qm.container.d/100-AddCAPA.conf << EOF
[Container]
DropCapability=
DropCapability=sys_boot
AddCapability=sys_resource
EOF
```

### 步骤 3：验证并应用配置

```bash
# 预览生成的 systemd 配置
/usr/lib/systemd/system-generators/podman-system-generator --dryrun
# 检查输出中是否包含: --cap-drop sys_boot --cap-add all --cap-add sys_resource

# 重载并重启 QM
systemctl daemon-reload
systemctl restart qm
```

### 步骤 4：测试验证

```bash
# 进入 QM
podman exec -it qm /bin/bash

# 启动第一个嵌套容器并检查 OOM 分数
systemctl start nested
PID=$(podman inspect -f '{{.State.Pid}}' nested)
cat /proc/$PID/oom_score_adj
# 预期输出: 1000

# 启动第二个嵌套容器并检查 OOM 分数
systemctl start nested2
PID=$(podman inspect -f '{{.State.Pid}}' nested2)
cat /proc/$PID/oom_score_adj
# 预期输出: 100
```

## SELinux 强制访问控制

SELinux（Security-Enhanced Linux）提供内核级强制访问控制（MAC），QM 有独立的 SELinux 策略模块。

### QM SELinux 策略文件

QM 项目包含以下 SELinux 策略源文件：

| 文件 | 作用 |
|------|------|
| `qm.te` | 类型强制（Type Enforcement）规则，定义 `qm_t` 域的访问权限 |
| `qm.if` | 接口定义文件，供其他策略模块调用 |
| `qm.fc` | 文件上下文（File Contexts），定义文件路径的安全标签 |
| `qm_file_context` | 文件上下文配置 |
| `qm_contexts` | 上下文配置 |

### QM SELinux 域：qm_t

QM 内的所有控制进程（容器除外）都运行在 `qm_t` SELinux 类型：

```bash
# 进入 QM 后查看 SELinux 上下文
podman exec -ti qm sh
sh-5.2# id -Z
system_u:system_r:qm_t:s0:c35,c404
#           ^^^^^ qm_t 域
```

### SELinux 隔离目标

QM SELinux 策略实现三层隔离：

1. **QM 与主机隔离**：`qm_t` 域进程无法访问 ASIL 域或其他主机域的资源
2. **QM 与容器隔离**：QM 内容器运行在 `container_t` 域，与 `qm_t` 进程隔离
3. **容器之间隔离**：不同嵌套容器之间也通过 SELinux 互相隔离

### SELinux 问题排障

遇到 SELinux 拒绝访问时，使用以下命令诊断：

```bash
# 查看最近的 AVC 拒绝消息并分析原因
ausearch -m avc -ts recent | audit2why

# 查看 setroubleshoot 日志
journalctl -t setroubleshoot

# 生成详细的 SELinux 警报报告
sealert -a /var/log/audit/audit.log
```

如遇到 SELinux 相关问题，可在 [QM GitHub Issues](https://github.com/containers/qm/issues) 提交问题并附上上述命令的输出。

## 能力边界（Capabilities）

除了 SELinux 和 OOM，QM 还通过 Linux capabilities 限制进程权限：

- **默认丢弃**：`sys_boot`（防止重启系统）
- **默认不包含**：`SYS_RESOURCE`（防止修改资源限制，包括 OOM 分数）
- **添加能力**：通过 drop-in 配置的 `AddCapability=` 添加

## 相关概念

- [嵌套隔离架构](01-nested-architecture.md)：了解 QM 的整体嵌套架构
- [QM 定位与 ASIL 汽车功能安全场景](00-introduction.md)：了解安全隔离的背景
- [创建 QM 虚拟机环境](../examples/01-vm-setup.md)：在虚拟机中测试 QM 的 OOM 和 SELinux 配置
